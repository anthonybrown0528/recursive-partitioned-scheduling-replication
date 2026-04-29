import os
import argparse
import numpy as np
import pandas as pd
import multiprocessing
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
        success, forest = recursive_gang_schedule(taskset, m)
    elif scheduler_type == "rps-fp2":
        success, forest = recursive_gang_schedule(taskset, m, use_sp=True)
    elif scheduler_type == "sps-fp":
        success, forest = sps_fp(taskset, m)
    elif scheduler_type == "sps-edf":
        success, forest = sps_edf(taskset, m)
    elif scheduler_type == "stationary":
        success, forest = stationary_schedule(taskset, m)
    else:
        raise RuntimeError(f"Invalid scheduler_type: {scheduler_type}")

    n = len(taskset)
    arr = np.zeros((40, ))
    if success and forest is not None:
        response_bound_map = {}
        for tree in forest.trees:
            response_bound_map.update(tree.response_bounds.items())
        for jdx, val in enumerate(response_bound_map.values()):
            arr[jdx] = val

    return success, n, m, ctr, arr

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

    get_file_paths(args.input_dir, args.type)

    output_schedulability_path = os.path.join(args.output_dir, f"{args.output}_schedulability.csv")
    output_response_time_path = os.path.join(args.output_dir, f"{args.output}_responsetime.csv")

    results = []
    with multiprocessing.Pool(NUM_THREADS) as pool:
        value = pool.map(load_data, filepaths)
        results = value

    print("Starting schedulability tests")
    outputs = []
    response_times = []
    for i, res in enumerate(results):
        print('processing', i, 'out of', len(results))
        with multiprocessing.Pool(NUM_THREADS) as pool:
            intermediate = pool.map(process_data, res)
            output_term = list(map(lambda x: (x[0], x[1], x[2], x[3]), intermediate))
            arr = list(map(lambda x: x[4], intermediate))


            response_times = response_times + arr
            outputs = outputs + output_term
    output_df = pd.DataFrame(outputs, columns=['success', 'taskset size', 'processor count', 'taskset util'])
    response_times_df = pd.DataFrame(np.array(response_times))

    output_df.to_csv(output_schedulability_path)
    response_times_df.to_csv(output_response_time_path)

if __name__ == '__main__':
    main()