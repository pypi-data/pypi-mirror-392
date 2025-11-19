import warnings
from datetime import timedelta
import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import Union, List
from .RLS import FilterRLS
from DSM.structures.dsm_timeseries import dsm_timeseries
from .BaseModel import BaseModel


class STA(BaseModel):
    """
    STA LR forecasting method Class

    :param rls_num_par: number of alfa for RLS model
    :param circles_count: number of circles of the data calculations
    :param *args: rls filter parameters
    :param *kwargs: rls filter parameters
    """

    def __init__(self, rls_num_par: int = 4, circles_count: int = 3, *args, **kwargs):
        self.rls_num_par = rls_num_par
        self.circles_count = circles_count
        self.day = 0
        self.df = None
        self.day_list = None
        self.day_points = 0
        self._features_number = 8
        self.w = None
        self.args = args
        self.kwargs = kwargs
        self.datetime_column_name = None
        self.value_column_name = None
        self.common_features_names = None
        self.y_estimate = None

    def _validate_dataframe(self, df: pd.DataFrame, datetime_column_name: str, value_column_name: str) -> None:
        """
        Validate input DataFrame

        :param df: pandas DataFrame
        :param datetime_column_name: datetime column name
        :param value_column_name: target value column name
        :return: None
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input data must be a pandas DataFrame")
        if datetime_column_name not in df.columns:
            raise ValueError(f"{datetime_column_name} not in DataFrame.")
        if value_column_name not in df.columns:
            raise ValueError(f"{value_column_name} not in DataFrame.")
        if not pd.api.types.is_datetime64_any_dtype(df[datetime_column_name]):
            raise ValueError("Incorrect type of datetime column. Must be datetime.")
        if not np.issubdtype(df[value_column_name].dtype, np.floating):
            raise ValueError("Incorrect type of value column. Must be float.")
        self.df = df.copy()

    def _make_day_list(self, datetime_column_name: str, add_next_day: bool = False):
        """
        Generate day list from DataFrame; optionally add next day
    
        :param datetime_column_name: datetime column name or index
        :param add_next_day: add day after last day if True
        """
        if self.df.index.name == datetime_column_name or (self.df.index.names and datetime_column_name in self.df.index.names):
            datetime_series = self.df.index.to_series()
        else:
            datetime_series = self.df[datetime_column_name]
    
        self.df['date'] = datetime_series.dt.date
        self.df['time'] = datetime_series.dt.time
    
        if not self.df.index.name == datetime_column_name:
            self.df = self.df.set_index(datetime_column_name)
    
        unique_days = sorted(self.df['date'].unique())
        if add_next_day:
            next_day = unique_days[-1] + timedelta(days=1)
            self.day_list = unique_days + [next_day]
        else:
            self.day_list = unique_days

    def _make_base_features(self, common_features_names):
        """
        Extract main and common features for modeling

        :param common_features_names: list of common feature columns
        :return: main_data, common_data numpy arrays
        """
        main_data = np.zeros((self.day_points, self.circles_count * len(self.day_list)))
        common_data = np.zeros((len(common_features_names), self.day_points, len(self.day_list)))

        days_count = len(self.day_list)
        for i in tqdm(range(self.circles_count * days_count), desc='Extracting main data'):
            current_day = self.day_list[i % days_count]
            day_slice = self.df[self.df['date'] == current_day][[self.value_column_name]]
            day_slice = day_slice.dropna(subset=[self.value_column_name])
            limit = min(len(day_slice), self.day_points)
            for j in range(limit):
                main_data[j, i] = day_slice.iloc[j][self.value_column_name]

        for feat_idx, feat_name in enumerate(common_features_names):
            for day_idx, current_day in enumerate(self.day_list):
                values = self.df[self.df['date'] == current_day][[feat_name]]
                values = values.dropna(subset=[feat_name])
                if len(values) == self.day_points:
                    common_data[feat_idx, :, day_idx] = values[feat_name].values
                else:
                    padded = np.pad(values[feat_name].values, (0, self.day_points - len(values)), 'constant')
                    common_data[feat_idx, :, day_idx] = padded

        return main_data, common_data

    def _make_fit(self, main_data, common_data, common_features_names, method_features_count, rls_model):
        """
        Fit RLS model to generate predictions

        :param main_data: np.array, shape (day_points, total_days*cicles)
        :param common_data: np.array, shape (n_common_feats, day_points, n_days)
        :param common_features_names: list of feature names
        :param method_features_count: typically rls_num_par count
        :param rls_model: instance of RLS filter
        """
        days_count = len(self.day_list)
        y_estimate = np.zeros((self.day_points, self.circles_count * days_count))
        average = np.zeros_like(y_estimate)
        y_before = np.zeros((self.day_points, self.rls_num_par + len(common_features_names)))

        day = 0
        for _ in tqdm(range(self.circles_count), desc='Model fitting passes'):
            for s in range(days_count):
                for t in range(self.day_points):
                    diff_n = t - self.rls_num_par
                    if day >= 28:
                        average[t, day] = np.mean([main_data[t, day - 7 * i] for i in range(1, 5)])
                    elif 0 < day < 28:
                        average[t, day] = main_data[t, day - 1]
                    else:
                        average[t, day] = 0

                    # Form feature vector y_before for each t
                    if diff_n == -3:
                        features = [main_data[self.day_points - 1, day - 1],
                                    main_data[self.day_points - 2, day - 1],
                                    main_data[self.day_points - 3, day - 1],
                                    average[t, day]]
                    elif diff_n == -2:
                        features = [y_estimate[0, day],
                                    main_data[self.day_points - 1, day - 1],
                                    main_data[self.day_points - 2, day - 1],
                                    average[t, day]]
                    elif diff_n == -1:
                        features = [y_estimate[1, day], y_estimate[0, day],
                                    main_data[self.day_points - 1, day - 1],
                                    average[t, day]]
                    else:
                        features = [y_estimate[t - 1, day], y_estimate[t - 2, day],
                                    y_estimate[t - 3, day], average[t, day]]

                    # Extend with zeros for common features (will be filled next)
                    features.extend([0] * len(common_features_names))
                    y_before[t, :] = features

                # Fill common features into y_before
                for i in range(len(common_features_names)):
                    y_before[:, method_features_count + i] = common_data[i, :, s]

                # Compute estimate for whole series for this day
                # self.w shape: (day_points, feature_count)
                # y_before shape: (day_points, feature_count)
                y_estimate[:, day] = np.einsum('ij,ij->i', self.w, y_before)

                # Clip predictions within reasonable bounds
                y_estimate[:, day] = np.clip(
                    y_estimate[:, day], 0, self.df[self.value_column_name].max() * 1.2)

                # Update weights using RLS
                y, e, w = rls_model.run(main_data[:, day], y_before)
                self.w = w

                day += 1

        self.y_estimate = y_estimate

    def fit(self, df: Union[pd.DataFrame, dsm_timeseries], day_points: int,
            datetime_column_name: str = None, value_column_name: str = None,
            common_features_names: List[str] = None) -> None:
        """
        Fit the STA model on data

        :param df: Input DataFrame or dsm_timeseries
        :param day_points: Number of points per day
        :param datetime_column_name: Datetime column name
        :param value_column_name: Target value column name
        :param common_features_names: List of common feature names
        """
        warnings.filterwarnings("ignore")
        if isinstance(df, dsm_timeseries):
            data = df
            df = data.data
            datetime_column_name = data.time_column_name
            value_column_name = data.value_column_name

        if common_features_names is None:
            common_features_names = []

        self._validate_dataframe(df, datetime_column_name, value_column_name)
        self.datetime_column_name = datetime_column_name
        self.value_column_name = value_column_name
        self.common_features_names = common_features_names
        self.day_points = day_points

        self._make_day_list(datetime_column_name)  # base day list

        method_features_count = 4
        feature_count = method_features_count + len(common_features_names)
        self.w = np.zeros((self.day_points, feature_count))

        main_data, common_data = self._make_base_features(common_features_names)

        rls_model = FilterRLS(self.rls_num_par + len(common_features_names), *self.args, **self.kwargs)

        self._make_fit(main_data, common_data, common_features_names, method_features_count, rls_model)

    def predict(self, method: str = "All") -> pd.DataFrame:
        """
        Make prediction using the fitted model.
        
        :param method: 'All' for full prediction, 'Last' for next day after last in training
        :return: DataFrame with forecast column
        """
        if method == "All":
            for i in tqdm(range(len(self.day_list))):
                day = self.day_list[i]
                day_slice = self.df[self.df['date'] == day].copy()
                if day_slice.empty:
                    continue
                for j in range(min(len(day_slice), self.day_points)):
                    idx = day_slice.index[j]
                    forecast_val = self.y_estimate[j, i + (self.circles_count - 1) * len(self.day_list)]
                    self.df.loc[idx, 'forecast'] = float(forecast_val)
            return self.df

        elif method == "Last":
            
            self.day_list.append(self.day_list[-1] + timedelta(days=1))
            main_data, common_data = self._make_base_features(self.common_features_names)
            rls_model = FilterRLS(self.rls_num_par + len(self.common_features_names), *self.args, **self.kwargs)
            self._make_fit(main_data, common_data, self.common_features_names, 4, rls_model)
        
            next_day = self.day_list[-1]
        
            last_day_times = self.df[self.df['date'] == self.day_list[-2]]['time'].values
            new_datetimes = [pd.Timestamp.combine(next_day, t) for t in last_day_times]
        
            forecast_df = pd.DataFrame({
                self.datetime_column_name: new_datetimes,
                'forecast': [float(self.y_estimate[j, (self.circles_count - 1) * (len(self.day_list) - 1) + len(self.day_list) - 1])
                             for j in range(min(len(new_datetimes), self.day_points))]
            })
            forecast_df = forecast_df.rename(columns={self.datetime_column_name: 'datetime'})
            return forecast_df

        else:
            raise ValueError("Invalid method argument. Use 'All' or 'Last'.")
