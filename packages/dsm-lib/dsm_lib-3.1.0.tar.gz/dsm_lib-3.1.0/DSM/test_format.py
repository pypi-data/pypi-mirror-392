import datetime
from DSM.models.TDaysAVR import TDaysAVR
from DSM.structures.dsm_timeseries import dsm_timeseries
import pandas as pd
import numpy as np

def stabilize_timeseries(df: pd.DataFrame, datetime_col: str, value_col: str, target_day: str = None):
    df_work = df[[datetime_col, value_col]].copy()
    df_work[datetime_col] = pd.to_datetime(df_work[datetime_col], errors='coerce')
    df_work = df_work.dropna(subset=[datetime_col])

    if df_work.empty:
        raise ValueError("Time column is not recognized")

    times = df_work[datetime_col].sort_values().unique()
    if len(times) < 2:
        raise ValueError("Too little data")
    diffs = np.diff(times) / np.timedelta64(1, 'm')
    freq_min = pd.Series(diffs).mode().iloc[0]
    std_freqs = np.array([15, 20, 30, 60, 120])
    freq_round = std_freqs[np.argmin(np.abs(std_freqs - freq_min))]

    def round_dt(dt, freq_min):
        total_minutes = dt.hour * 60 + dt.minute
        rounded_total = int(round(total_minutes / freq_min) * freq_min)
        rounded_total = rounded_total % (24 * 60)
        rounded_hour = rounded_total // 60
        rounded_minute = rounded_total % 60
        return dt.replace(hour=rounded_hour, minute=rounded_minute, second=0, microsecond=0)
    df_work[datetime_col] = df_work[datetime_col].apply(lambda x: round_dt(x, freq_min))

    if target_day is not None:
        target_dt = pd.to_datetime(target_day)
        last_dt = df_work[datetime_col].max()
        if (target_dt - last_dt).days >= 2:
            raise ValueError(f"Target day is too high")
        df_work = df_work[df_work[datetime_col] < target_dt]
        if df_work.empty:
            raise ValueError("Data is empty after filtration")

    start = df_work[datetime_col].min()
    end = df_work[datetime_col].max()
    freq_str = f'{freq_round}m' if freq_round < 60 else f'{int(freq_round//60)}h'
    freq_str_up = f'{freq_round}T' if freq_round < 60 else f'{int(freq_round//60)}h'
    full_range = pd.date_range(
        start=start,
        end=end,
        freq=freq_str_up
    )
    out_df = pd.DataFrame({datetime_col: full_range})
    out_df = out_df.merge(df_work, how='left', on=datetime_col)

    if out_df[value_col].notna().sum() == 0:
        out_df[value_col] = 0.0
    else:
        mean_val = out_df[value_col].mean()
        out_df[value_col] = out_df[value_col].fillna(mean_val)
    n_pts_day = int(24 * 60 // freq_round)
    return out_df, n_pts_day, freq_str


data_path = '/home/inact1ve/hse_lab/eco/digital_ecomonitoring/test_suite/dsm_folder/data/2024_74040101.xlsx'

df = pd.read_excel(data_path)

df = df[['time', 'no2']]

data, points, interval = stabilize_timeseries(df, 'time', 'no2', '2024-11-25')

print(data)
print(points)
print(interval)

dsm_df = dsm_timeseries('test', data, 'no2', interval, 'time')

dsm_df.show()

model = TDaysAVR()

model.predict(dsm_df, datetime_column_name='time', value_column_name='no2', day_points=points, method='Last')


