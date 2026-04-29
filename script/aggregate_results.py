import matplotlib
import pandas as pd
import os

def load_data(data_path: str):
    df = pd.read_csv(data_path)

    group = df.groupby(['success', 'taskset size', 'processor count'])
    return group.count().rename(columns={"Unnamed: 0": 'count'})

def compute_sched_ratio(df: pd.DataFrame):
    return df.loc[True]['count'] / (df.loc[False]['count'] + df.loc[True]['count'])

def compute_normed_ratio(data: pd.Series, factor: pd.Series):
    return data / factor

RESULT_DATA_PATH = os.path.join('data', 'output')

rps_fp1 = load_data(os.path.join(RESULT_DATA_PATH, 'rps_fp1_results.csv'))
rps_fp2 = load_data(os.path.join(RESULT_DATA_PATH, 'rps_fp2_results.csv'))

sps_fp_data = load_data(os.path.join(RESULT_DATA_PATH, 'sps_fp_results.csv'))
sps_edf_data = load_data(os.path.join(RESULT_DATA_PATH, 'sps_edf_results.csv'))

stationary_data = load_data(os.path.join(RESULT_DATA_PATH, 'stationary_schedule_results.csv'))

rps_sched_ratio_series = compute_sched_ratio(rps_fp1)
sps_sched_ratio_series = compute_sched_ratio(sps_fp_data)
stationary_sched_ratio_series = compute_sched_ratio(stationary_data)

sps_normed_ratio_series = compute_normed_ratio(sps_sched_ratio_series, sps_sched_ratio_series)
print(sps_normed_ratio_series)

rps_normed_ratio_series = compute_normed_ratio(rps_sched_ratio_series, sps_sched_ratio_series)
print(rps_normed_ratio_series)

stationary_normed_ratio_series = compute_normed_ratio(stationary_sched_ratio_series, sps_sched_ratio_series)
print(stationary_normed_ratio_series)