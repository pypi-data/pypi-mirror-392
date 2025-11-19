"""
Air pollution forecasting class using TDaysAVR
"""
import datetime
from typing import Union, List, Dict, Any
import numpy as np
import pandas as pd
from tqdm import tqdm
from .DayFunctions import get_days, get_NSP_days, get_base_value
from DSM.structures.dsm_timeseries import dsm_timeseries
from .BaseModel import BaseModel


class TDaysAVR(BaseModel):
    """
    Forecasting air pollution by Coping previous day depending on day position in a week
    It not just copy the previous value N weeks ago, it finds average among three previous same days
    For example, average of the 3 previous mondays

    :param n_days:
    """

    def __init__(self, n_days: int = 3):
        self._n_days = n_days
        self.day_list = None

    def _validate_dataframe(self, df: pd.DataFrame, datetime_column_name: str, value_column_name: str) -> None:
        """
        Method for checking data correctness

        :param df: pandas dataframe or dictionary list with datetime and value columns
        :param value_column_name: column name in df with float value of pollution
        :param datetime_column_name: column name in df with datetime value
        :return: None
        """

        if isinstance(df, pd.DataFrame):
            if datetime_column_name not in df.columns:
                raise ValueError(f"{datetime_column_name} not in dataframe.")
            elif value_column_name not in df.columns:
                raise ValueError(f"{value_column_name} not in dataframe.")

            if not pd.api.types.is_datetime64_any_dtype(df[datetime_column_name]):
                raise ValueError("Incorrect type of datetime column. Must be datetime.")
            elif not df[value_column_name].dtype == float:
                raise ValueError("Incorrect type of value column. Must be float.")
        self.df = df

    def _make_day_list(self, datetime_column_name: str):
        """
        Method for calculating day list of df

        :param datetime_column_name: column name in df with datetime value
        :return None
        """
        self.df['date'] = self.df[datetime_column_name].dt.date
        self.df['time'] = self.df[datetime_column_name].dt.time
        self.df = self.df.set_index(datetime_column_name)

        df_tmp = self.df.copy(deep=True)
        df_tmp = df_tmp.drop(columns=['time'])

        avg_day = df_tmp.groupby(['date']).sum()
        self.day_list = list(avg_day.index)

    def predict(self, df: Union[pd.DataFrame, dsm_timeseries], datetime_column_name: str = None, value_column_name: str = None, day_points: int = None, method: str = "All"):
        """
        Predict method for use TDaysAVR

        :param df: pandas dataframe with datetime and value columns or DSM structure (pd.DataFrame, dsm_timeseries)
        :param value_column_name: column name in df with float value of pollution (str)
        :param datetime_column_name: column name in df with datetime value (str)
        :param day_points: count of value points for one day (int)
        :param method: method of forecasting (Only 1 last day = "Last", for full dataframe = "All")
        :return: pandas DataFrame with datetime and forecast columns for both methods
        """
        if isinstance(df, dsm_timeseries):
            data = df
            df = data.data
            datetime_column_name = data.time_column_name
            value_column_name = data.value_column_name 
        
        # Validate dataframe
        df = df.copy(deep=True)
        self._validate_dataframe(df, datetime_column_name, value_column_name)
        self._make_day_list(datetime_column_name)
        df = self.df
        df['forecast'] = float(0)

        # Forecast with method parameter
        if method == "All":
            start_day_index = self._n_days * 7  # 7 is count days of week
            for i in tqdm(range(start_day_index, len(self.day_list))):
                target_day = self.day_list[i]
                condition1 = get_days(target_day, self._n_days * 7)
                condition2 = get_NSP_days(condition1, self._n_days)
                base_data = get_base_value(df, condition2, value_column_name)
                new_data = df[df['date'].isin([list(self.day_list)[i]])].copy()[['date', 'time', value_column_name]]
                for j in range(len(new_data)):  # for each interval of the current day
                    list_ind = base_data.index
                    l = new_data.index[j]  # take the index of the current point
                    point = new_data.loc[l, 'time']  # choose the point
                    if point in list(list_ind):  # if we have previous observations for this point
                        tempData = base_data.loc[list_ind == point]
                        df.loc[l, 'forecast'] = tempData.loc[tempData.index[0], value_column_name]

            # Return DataFrame with original datetime and forecast
            result_df = df[['date', 'time', 'forecast']].copy()
            # Combine date and time into a single datetime column if needed
            result_df['datetime'] = pd.to_datetime(
                result_df['date'].astype(str) + ' ' + result_df['time'].astype(str))
            return result_df[['datetime', 'forecast']]

        elif method == "Last":
            target_day = self.day_list[-1] + datetime.timedelta(days=1)
            result_forecast = []
            result_datetimes = []

            try:
                condition1 = get_days(target_day, self._n_days * 7)
                condition2 = get_NSP_days(condition1, self._n_days)
                base_data = get_base_value(df, condition2, value_column_name)

                # Get the time points from the last available day
                last_day_data = df[df['date'] == self.day_list[-1]].copy()
                time_points = last_day_data['time'].unique()

                # Create future datetimes for the next day
                next_day = self.day_list[-1] + datetime.timedelta(days=1)

                for time_point in time_points:
                    list_ind = base_data.index
                    if time_point in list(list_ind):  # if we have previous observations for this point
                        tempData = base_data.loc[list_ind == time_point]
                        forecast_value = tempData.loc[tempData.index[0], value_column_name]
                        result_forecast.append(forecast_value)

                        # Create datetime for the future point
                        if isinstance(time_point, str):
                            future_datetime = pd.to_datetime(f"{next_day.strftime('%Y-%m-%d')} {time_point}")
                        else:
                            # If time_point is already a time object
                            future_datetime = datetime.datetime.combine(next_day, time_point)

                        result_datetimes.append(future_datetime)

            except Exception as e:
                raise ValueError(f"Incorrect size of input dataframe. Error: {str(e)}")

            # Create result DataFrame
            result_df = pd.DataFrame({
                'datetime': result_datetimes,
                'forecast': result_forecast
            })

            return result_df

        else:
            raise ValueError("Incorrect method parameter. Must be 'All' or 'Last'.")
