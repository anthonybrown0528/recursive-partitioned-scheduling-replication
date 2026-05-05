import matplotlib.pyplot as plt
import pandas as pd
import os

def load_data(data_path: str):
    df = pd.read_csv(data_path)
    return agg_data(df)

def agg_data(df: pd.DataFrame):
    group = df.groupby(['success', 'taskset_size', 'processor_count'])
    return group.count().rename(columns={"Unnamed: 0": 'count'})

def agg_data_with_util(df: pd.DataFrame):
    group = df.groupby(['success', 'taskset_size', 'processor_count', 'taskset_util'])
    return group.count().rename(columns={"Unnamed: 0": 'count'})

def compute_sched_ratio(df: pd.DataFrame):
    return df.loc[True]['count'] / (df.loc[False]['count'] + df.loc[True]['count'])

def compute_normed_ratio(data: pd.Series, factor: pd.Series):
    return data / factor

# RESULT_DATA_PATH = os.path.join('test_output')
RESULT_DATA_PATH = os.path.join('data', 'output')

datafiles = [
    ('RPS-FP1-DM', 'rps-fp1_schedulability.csv'),
    ('RPS-FP2-DM', 'rps-fp2_schedulability.csv'),
    ('RPS-FP1-RM', 'rps-fp1-rm_schedulability.csv'),
    ('RPS-FP2-RM', 'rps-fp2-rm_schedulability.csv'),
    ('RPS-FP1-RAND', 'rps-fp1-rand_schedulability.csv'),
    ('RPS-FP2-RAND', 'rps-fp2-rand_schedulability.csv'),
    ('SPS-FP', 'sps-fp_schedulability.csv'),
    ('SPS-EDF', 'sps-edf_schedulability.csv'),
    ('Stationary Schedule', 'stationary_schedulability.csv')
]

data_map = {}
normed_data_ratios = {}

data_norm_name = 'RPS-FP1-DM'

for (name, filename) in datafiles:
    data = load_data(os.path.join(RESULT_DATA_PATH, filename))
    data_map[name] = data

for name, dataframe in data_map.items():
    sched_ratio_data = compute_sched_ratio(dataframe)
    normalizer = compute_sched_ratio(data_map[data_norm_name])

    data_norm_series = compute_normed_ratio(sched_ratio_data, normalizer)
    normed_data_ratios[name] = data_norm_series[data_norm_series.notna()]
    


# for name, series in normed_data_ratios.items():
#     print(series)

leg = []
for name, series in normed_data_ratios.items():
    # series.loc[32, 16].plot()
    series.plot()
    leg.append(name)

plt.legend(leg)

plt.grid(visible=True)
# plt.show()

res = None
for name, series, in normed_data_ratios.items():
    if res is None:
        res = series.rename(name)
    else:
        res = pd.concat([res, series.rename(name)], axis=1)

def print_tex_code(res: pd.DataFrame):
    print('\\begin{tabular}{|l', end='')
    print(*(['|c'] * len(res.columns)), '|', sep='', end='}\n')

    print('\\hline')
    header = ['(n, m)'] + list(res.columns)
    for idx, head in enumerate(header):
        if idx == 0:
            print("\\textbf{", head, "}", end=' ')
        else:
            print('&', "\\textbf{", head, "}", end=' ')
    print('\\\\')

    for (index, data) in res.iterrows():

        print(index, end=' ')
        for d in data:
            print('&', '%.3f' % d, end=' ')
        print('\\\\')
        print('\\hline')

    print('\\end{tabular}')

# print_tex_code(res[['RPS-FP1-DM', 'RPS-FP1-RM', 'RPS-FP1-RAND']])
print_tex_code(res[['RPS-FP1-DM', 'RPS-FP2-RM', 'RPS-FP2-RAND']])