import numpy as np
import pandas as pd
import os

def load_data(data_path: str):
    df = pd.read_csv(data_path)
    return agg_data(df)

def agg_data(df: pd.DataFrame):
    df = df[['success', 'taskset_size', 'processor_count']]
    return df.value_counts(subset=['success', 'taskset_size', 'processor_count'])

RESULT_DATA_PATH = os.path.join('data', 'output')

datafiles = [
    ('RPS-FP1', 'rps-fp1_schedulability.csv'),
    ('RPS-FP2', 'rps-fp2_schedulability.csv'),
    ('SPS-FP', 'sps-fp_schedulability.csv'),
    ('SPS-EDF', 'sps-edf_schedulability.csv'),
    ('SS-FP', 'stationary_schedulability.csv')
]

data_map = {}
normed_data_ratios = {}

data_norm_name = 'SPS-FP'

schedulability_ratios = {
    'RPS-FP1': [1.122, 1.1445, 1.1462, 1.1404, 1.1411, 1.11456, 1.11264, 1.1163],
    'RPS-FP2': [1.193, 1.2692, 1.3153, 1.3463, 1.329, 1.4097, 1.4393, 1.4617],
    'SPS-FP': [1, 1, 1, 1, 1, 1, 1, 1],
    'SPS-EDF': [1.1364, 1.1645, 1.1902, 1.2073, 1.1873, 1.2154, 1.229, 1.2429],
    'SS-FP': [1.0898, 1.0828, 1.0559, 1.0345, 1.0364, 0.9967, 0.9592, 0.9363],
}

ordered_keys = [
    (8, 8),
    (8, 12),
    (8, 16),
    (8, 20),
    (16, 16),
    (16, 24),
    (16, 32),
    (16, 40)
]
ordered_keys = list(map(lambda x: (x[1], x[0]), ordered_keys))

ordered_index = pd.MultiIndex.from_tuples(ordered_keys, names=['taskset_size', 'processor_count'])
norms = pd.DataFrame(schedulability_ratios, index=ordered_index)

for (name, filename) in datafiles:
    data = load_data(os.path.join(RESULT_DATA_PATH, filename))
    data_map[name] = data.loc[True, :, :]


res = None
for name, series, in data_map.items():
    if res is None:
        res = series.rename(name)
    else:
        res = pd.concat([res, series.rename(name)], axis=1)

expected_data_df = res.copy()

for col in expected_data_df.columns:
    expected_data_df[col] = expected_data_df[data_norm_name] * norms[col]


diff = (res - expected_data_df)
val = diff ** 2 / expected_data_df

output = val.to_numpy()
output = np.sum(output)

print(output)