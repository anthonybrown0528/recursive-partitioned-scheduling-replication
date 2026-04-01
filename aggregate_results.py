import matplotlib
import pandas as pd

def load_data(data_path: str):
    df = pd.read_csv(data_path)

    group = df.groupby(['success', 'taskset size', 'processor count'])
    return group.count().rename(columns={"Unnamed: 0": 'count'})

def compute_sched_ratio(df: pd.DataFrame):
    return df.loc[True]['count'] / (df.loc[False]['count'] + df.loc[True]['count'])

def compute_normed_ratio(data: pd.Series, factor: pd.Series):
    return data / factor

df = load_data('prelim_results.csv')
sps_data = load_data('prelim_results_sps.csv')
stationary_data = load_data('prelim_results_stationary_schedule.csv')

rps_sched_ratio_series = compute_sched_ratio(df)
sps_sched_ratio_series = compute_sched_ratio(sps_data)
stationary_sched_ratio_series = compute_sched_ratio(stationary_data)

sps_normed_ratio_series = compute_normed_ratio(sps_sched_ratio_series, sps_sched_ratio_series)
print(sps_normed_ratio_series)

rps_normed_ratio_series = compute_normed_ratio(rps_sched_ratio_series, sps_sched_ratio_series)
print(rps_normed_ratio_series)

stationary_normed_ratio_series = compute_normed_ratio(stationary_sched_ratio_series, sps_sched_ratio_series)
print(stationary_normed_ratio_series)