import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


RESULT_DATA_PATH = os.path.join('data', 'output')
# RESULT_DATA_PATH = os.path.join('test_output')

FIGURE_PATH = 'figure'

datafiles = [
    ('RPS-FP1-DM', 'rps-fp1_schedulability.csv'),
    ('RPS-FP2-DM', 'rps-fp2_schedulability.csv'),
    ('RPS-FP1-RM', 'rps-fp1-rm_schedulability.csv'),
    ('RPS-FP2-RM', 'rps-fp2-rm_schedulability.csv'),
    ('RPS-FP1-RAND', 'rps-fp1-rand_schedulability.csv'),
    ('RPS-FP2-RAND', 'rps-fp2-rand_schedulability.csv'),
]

data_map = {}
normed_data_ratios = {}

for (name, filename) in datafiles:
    data = pd.read_csv(os.path.join(RESULT_DATA_PATH, filename))
    data['part_util_std'] = np.sqrt(data['part_util_var'])
    data['norm_part_util_std'] = np.sqrt(data['norm_part_util_var'])

    data_map[name] = data

def plot_by_taskset_util(data_attribute: str, ylabel: str, success=True):
    for (name, df) in data_map.items():
        successful = df[df['success'] == success]

        view = successful[['taskset_size', 'processor_count', 'taskset_util', data_attribute]]
        aggregate = view.groupby(by=['taskset_size', 'processor_count', 'taskset_util'])
        
        slack_mean = aggregate.mean()
        slack_std = aggregate.std()

        mean_subset = slack_mean.loc[NUM_TASKS, NUM_PROCESSORS, :]
        std_subset = slack_std.loc[NUM_TASKS, NUM_PROCESSORS, :]


        plt.errorbar(x=mean_subset.index, y=mean_subset[data_attribute], yerr=std_subset[data_attribute], label=name, capsize=3, marker='o')

    plt.grid(visible=True)

    plt.xlabel('Gang Task Set Utilization ($i \\times 0.1m + 0.1m$)')
    plt.ylabel(ylabel=ylabel)

    plt.title(data_attribute.replace('_', ' ').capitalize() + ' where $m = ' + str(NUM_PROCESSORS) + ', n = ' + str(NUM_TASKS) + '$')
    plt.legend()

    plt.savefig(os.path.join(FIGURE_PATH, data_attribute + f'_M{NUM_PROCESSORS}_N{NUM_TASKS}.png'))
    plt.show()

def plot_by_taskset_size_processor_count(data_attribute: str, ylabel: str, success=True):
    val1 = 0
    val2 = 0

    for i, (name, df) in enumerate(data_map.items()):
        successful = df[df['success'] == success]

        view = successful[['taskset_size', 'processor_count', 'taskset_util', data_attribute]]
        aggregate = view.groupby(by=['taskset_size', 'processor_count', 'taskset_util'])

        slack_mean = aggregate.mean()

        if data_attribute == 'slack_mean':
            val1 += slack_mean.loc[16, 16, TASKSET_UTIL]
            val2 += slack_mean.loc[16, 8, TASKSET_UTIL]

        mean_subset = slack_mean.loc[:, :, TASKSET_UTIL]
        mean_subset = mean_subset.sort_index(level=1)

        x = list(map(lambda x: str(x), mean_subset.index.to_numpy().tolist()))

        width = 0.1
        gap = 0.01

        plt.bar(np.arange(len(x)) - (i * 2) * (width/2 + gap), mean_subset[data_attribute], width=width, tick_label=x, label=name)

    if data_attribute == 'slack_mean':
        print('(16, 8):', val1 / len(data_map.items()))
        print('(8, 8)', val2 / len(data_map.items()))

    plt.title(data_attribute.replace('_', ' ').capitalize() + ' where $U_{gang} = ' + str(round((TASKSET_UTIL + 1) * 0.1, ndigits=1)) + 'm$')
    plt.ylabel(ylabel=ylabel)
    plt.xlabel(xlabel='(n, m)')

    # NOTE: Uncomment and adjust to see figures better if needed
    # plt.ylim((0, 500))
    plt.legend(loc='best')

    plt.savefig(os.path.join(FIGURE_PATH, data_attribute + f'_u{TASKSET_UTIL}.png'))
    plt.show()

"""View Slack Statistics as a Function of Total Gang Taskset Utilization"""

NUM_PROCESSORS = 16
NUM_TASKS = 40

TASKSET_UTIL = 5

data_attributes = [
    # ('slack_mean', 'Average slack (ms)', True),
    # ('num_partitions', 'Number of Created Partitions', True),
    ('part_util_std', 'Partition Utilization Standard Deviation', True),
    ('norm_part_util_std', 'Normalized Partition Utilization Standard Deviation', True),
    # ('schedulable_tasks', '# Schedulable Tasks', False),
]

for (attrib, ylabel, success) in data_attributes:
    plot_by_taskset_util(attrib, ylabel, success=success)

for (attrib, ylabel, success) in data_attributes:
    plot_by_taskset_size_processor_count(attrib, ylabel, success=success)

"""View # scheduled tasks in tasksets where not all are schedulable"""
"""View utilization variance across partitions"""
"""View # Scheduled Tasks over Taskset size and # Processors"""
"""View Task Slack over Taskset size and # Processors"""
"""View utilization variance across partitions"""
