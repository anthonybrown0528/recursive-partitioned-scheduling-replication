import matplotlib.pyplot as plt
import pandas as pd
import os

def load_data(data_path: str):
    df = pd.read_csv(data_path)
    return agg_data_with_util(df)

def agg_data(df: pd.DataFrame):
    group = df.groupby(['success', 'taskset size', 'processor count'])
    return group.count().rename(columns={"Unnamed: 0": 'count'})

def agg_data_with_util(df: pd.DataFrame):
    group = df.groupby(['success', 'taskset size', 'processor count', 'taskset util'])
    return group.count().rename(columns={"Unnamed: 0": 'count'})

def compute_sched_ratio(df: pd.DataFrame):
    return df.loc[True]['count'] / (df.loc[False]['count'] + df.loc[True]['count'])

def compute_normed_ratio(data: pd.Series, factor: pd.Series):
    return data / factor

# RESULT_DATA_PATH = os.path.join('data', 'output')
RESULT_DATA_PATH = os.path.join('test_output')

datafiles = [
    ('RPS-FP1', 'rps-fp1_schedulability.csv'),
    ('RPS-FP2', 'rps-fp2_schedulability.csv'),
    ('SPS-FP', 'sps-fp_schedulability.csv'),
    ('SPS-EDF', 'sps-edf_schedulability.csv'),
    ('Stationary Schedule', 'stationary_schedulability.csv')
]

data_map = {}
normed_data_ratios = {}

data_norm_name = 'SPS-FP'

for (name, filename) in datafiles:
    data = load_data(os.path.join(RESULT_DATA_PATH, filename))
    data_map[name] = data

for name, dataframe in data_map.items():
    sched_ratio_data = compute_sched_ratio(dataframe)
    normalizer = compute_sched_ratio(data_map[data_norm_name])

    data_norm_series = compute_normed_ratio(sched_ratio_data, normalizer)
    normed_data_ratios[name] = data_norm_series[data_norm_series.notna()]
    


for name, series in normed_data_ratios.items():
    print(series)

leg = []
for name, series in normed_data_ratios.items():
    series.loc[32, 16].plot()
    leg.append(name)

plt.legend(leg)

plt.grid(visible=True)
plt.show()