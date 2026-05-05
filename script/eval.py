import os
import pickle
import argparse
import numpy as np
import pandas as pd
import multiprocessing
import random
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.task import Task

from src.recursive_gang_scheduler import recursive_gang_schedule
from src.sps_fp import sps_fp, sps_edf
from src.stationary_scheduler import stationary_schedule


# Path where input dataset will be stored
DATA_DIR = 'data'

# File extension of data files
IN_DATA_FILE_EXT = '.pqt'

# Output data directory
OUT_DATA_DIR = os.path.join(DATA_DIR, 'input', 'parquet')

# Collection of numbers of processors to use
num_processors = np.array([8, 16])

# Number of tasks as a fraction of number of processors
num_tasks_scaled = np.array([1, 1.5, 2, 2.5])

# Total utilization of the task set as a fraction of number of processors
u_gang_scale = np.linspace(start=0.1, stop=1.0, num=10, endpoint=True)

schedulability_results = []
filepaths = []

NUM_THREADS = 8

def get_file_paths(data_dir: str, scheduler_type: str):
    # Iterate over number of processors
    for m in num_processors:
        num_tasks = (num_tasks_scaled * m).astype(np.int8)
        u_gang = u_gang_scale * m

        m_prefix = f'{m}_'

        # Iterate over number of tasks in task set
        for n in num_tasks:
            n_prefix = f'{n}_'

            data = pd.DataFrame()

            # Iterate over target task set utilization
            for ctr, u_taskset in enumerate(u_gang):
                taskset_util_prefix = f'{ctr}_'
                filepaths.append((m, n, ctr, scheduler_type, os.path.join(data_dir, f'{m_prefix}{n_prefix}{taskset_util_prefix}{IN_DATA_FILE_EXT}')))

def load_data(args):
    m, n, ctr, scheduler_type, filepath = args

    df = pd.read_parquet(filepath)
    print("Loaded batch of data:", filepath)

    # Save data to dataset directory
    data = [
        'u-values',
        'periods',
        'parallelism',
        'wct',
        'deadlines'    
    ]

    taskset = []
    taskset_collection = []
    
    for _, row in df.iterrows():
        t = Task(round(row[data[2]]), row[data[3]], round(row[data[4]]), round(row[data[1]]), round(row[data[4]]))
        
        taskset.append(t)

        if len(taskset) == n:
            taskset_collection.append((taskset, m, ctr, scheduler_type))
            taskset = []
    print("Processed data from file:", filepath)
    return taskset_collection

    
def process_data(args):
    scheduler_args = args
    taskset, m, ctr, scheduler_type = scheduler_args

    if scheduler_type == "rps-fp1":
        success, forest, num_scheduled_tasks = recursive_gang_schedule(taskset, m)
    elif scheduler_type == "rps-fp2":
        success, forest, num_scheduled_tasks = recursive_gang_schedule(taskset, m, use_sp=True)
    elif scheduler_type == "sps-fp":
        success, forest, num_scheduled_tasks = sps_fp(taskset, m)
    elif scheduler_type == "sps-edf":
        success, forest, num_scheduled_tasks = sps_edf(taskset, m)
    elif scheduler_type == "stationary":
        success, forest, num_scheduled_tasks = stationary_schedule(taskset, m)
    else:
        raise RuntimeError(f"Invalid scheduler_type: {scheduler_type}")

    n = len(taskset)

    num_partitions = 0
    util_mean = -1
    util_var = -1

    norm_util_mean = -1
    norm_util_var = -1
    
    slack_mean = -1
    slack_var = -1

    # arr = np.zeros((40, ))
    if success and forest is not None:
        partition_util = []
        norm_part_util = []
        slacks = []
        response_bound_map = {}
        for part, _ in forest.leaves():
            util = 0
            norm_util = 0
            for task in part.tasks:
                util = util + task.c / task.period
                norm_util = norm_util + (task.c / task.period) * task.m
            partition_util.append(util)
            norm_part_util.append(norm_util / part.m)

            num_partitions = num_partitions + 1
        if forest.m > 0:
            partition_util.append(0)
            norm_part_util.append(0)
        partition_util = np.array(partition_util)
        util_var = np.var(partition_util)
        util_mean = np.mean(partition_util)

        norm_part_util = np.array(norm_part_util)
        norm_util_var = np.var(norm_part_util)
        norm_util_mean = np.mean(norm_part_util)

        for tree in forest.trees:
            response_bound_map.update(tree.response_bounds.items())
        for jdx, (key, val) in enumerate(response_bound_map.items()):
            slacks.append(key.d - val)
        slacks = np.array(slacks)
        slack_mean = np.mean(slacks)
        slack_var = np.var(slacks)

    return success, n, m, ctr, num_scheduled_tasks, num_partitions, util_mean, util_var, norm_util_mean, norm_util_var, slack_mean, slack_var

def main():
    parser = argparse.ArgumentParser(description="Generate text with trained model")

    parser.add_argument(
        "--input-dir",
        type=str,
        default=OUT_DATA_DIR
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        required=True
    )

    parser.add_argument(
        "--output",
        type=str,
        required=True
    )

    parser.add_argument(
        "--type",
        type=str,
        required=True
    )

    args = parser.parse_args()

    output_schedulability_path = os.path.join(args.output_dir, f"{args.output}_schedulability.csv")

    print('Loading input data...')
    results = []
    with open('packed_data.pkl', 'rb') as f:
        print('Opened input data file...')
        results = pickle.load(f)

    def update_tuple(x):
        y = (x[0], x[1], x[2], args.type)
        return y
    
    def update_collection(x):
        y = list(map(update_tuple, x))
        return y
    
    def rate_monotonic(x):
        x.priority = x.period
        return x

    def augment_tuple(x):
        z = list(map(rate_monotonic, x[0]))

        y = (z, x[1], x[2], x[3])
        return y

    def use_rate_monotonic(x):
        y = list(map(augment_tuple, x))
        return y

    def random_priority(x):
        x.priority = random.randint(0, 1000)
        return x

    def augment_tuple_rand(x):
        z = list(map(random_priority, x[0]))

        y = (z, x[1], x[2], x[3])
        return y

    def use_random(x):
        y = list(map(augment_tuple_rand, x))
        return y

    
    print('Setting scheduling type...')
    results = list(map(update_collection, results))

    # print('Assigning rate-monotonic priority...')
    # results = list(map(use_rate_monotonic, results))

    print('Assigning random priority...')
    results = list(map(use_random, results))

    print("Starting schedulability tests")
    outputs = []
    for i, res in enumerate(results):
        print('processing', i, 'out of', len(results))
        with multiprocessing.Pool(NUM_THREADS) as pool:
            intermediate = pool.map(process_data, res)
            output_term = intermediate

            outputs = outputs + output_term

    cols = [
        'success', 
        'taskset_size', 
        'processor_count', 
        'taskset_util', 
        'schedulable_tasks',
        'num_partitions',
        'part_util_mean',
        'part_util_var',
        'norm_part_util_mean',
        'norm_part_util_var',
        'slack_mean',
        'slack_var'
    ]
    output_df = pd.DataFrame(outputs, columns=cols)
    output_df.to_csv(output_schedulability_path)

if __name__ == '__main__':
    main()