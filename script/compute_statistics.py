import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


RESULT_DATA_PATH = os.path.join('data', 'output')

datafiles = [
    ('RPS-FP1', 'rps-fp1_schedulability.csv'),
    ('RPS-FP2', 'rps-fp2_schedulability.csv'),
]

data_map = {}
normed_data_ratios = {}

for (name, filename) in datafiles:
    data = pd.read_csv(os.path.join(RESULT_DATA_PATH, filename))
    data_map[name] = data

"""View Slack Statistics as a Function of Total Gang Taskset Utilization"""

NUM_PROCESSORS = 8
NUM_TASKS = 8

for (name, df) in data_map.items():
    successful = df[df['success'] == True]

    view = successful[['taskset_size', 'processor_count', 'taskset_util', 'slack_mean']]
    aggregate = view.groupby(by=['taskset_size', 'processor_count', 'taskset_util'])
    
    slack_mean = aggregate.mean()
    slack_std = aggregate.std()

    mean_subset = slack_mean.loc[NUM_TASKS, NUM_PROCESSORS, :]
    std_subset = slack_std.loc[NUM_TASKS, NUM_PROCESSORS, :]

    plt.errorbar(x=mean_subset.index, y=mean_subset['slack_mean'], yerr=std_subset['slack_mean'], label=name)

plt.legend()
plt.show()

"""View # scheduled tasks in tasksets where not all are schedulable"""


for (name, df) in data_map.items():
    successful = df[df['success'] == False]

    view = successful[['taskset_size', 'processor_count', 'taskset_util', 'schedulable_tasks']]
    aggregate = view.groupby(by=['taskset_size', 'processor_count', 'taskset_util'])

    slack_mean = aggregate.mean()
    slack_std = aggregate.std()

    mean_subset = slack_mean.loc[NUM_TASKS, NUM_PROCESSORS, :]
    std_subset = slack_std.loc[NUM_TASKS, NUM_PROCESSORS, :]

    plt.errorbar(x=mean_subset.index, y=mean_subset['schedulable_tasks'], yerr=std_subset['schedulable_tasks'], label=name)

plt.legend()
plt.show()

"""View utilization variance across partitions"""


for i, (name, df) in enumerate(data_map.items()):
    successful = df[df['success'] == True]

    view = successful[['taskset_size', 'processor_count', 'taskset_util', 'part_util_var']]
    aggregate = view.groupby(by=['taskset_size', 'processor_count', 'taskset_util'])

    slack_mean = aggregate.mean()
    slack_std = aggregate.std()

    mean_subset = slack_mean.loc[:, :, 6]
    std_subset = slack_std.loc[:, :, 1]
    x = list(map(lambda x: str(x), mean_subset.index.to_numpy().tolist()))

    width = 0.4

    plt.bar(np.arange(len(x)) + (i * 2 - 1) * width/2, mean_subset['part_util_var'], width=width, tick_label=x, label=name)
plt.legend()
plt.show()
