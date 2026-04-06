import os
import numpy as np
import pandas as pd
import multiprocessing

from task import Task

from recursive_gang_scheduler import recursive_gang_schedule


# Path where input dataset will be stored
DATA_DIR = 'data'

# File extension of data files
IN_DATA_FILE_EXT = '.pqt'

# Output data directory
OUT_DATA_DIR = os.path.join(DATA_DIR, 'parquet')

# Collection of numbers of processors to use
num_processors = np.array([8, 16])

# Number of tasks as a fraction of number of processors
num_tasks_scaled = np.array([1, 1.5, 2, 2.5])

# Total utilization of the task set as a fraction of number of processors
u_gang_scale = np.linspace(start=0.1, stop=1.0, num=10, endpoint=True)

schedulability_results = []
filepaths = []

NUM_THREADS = 8

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
            filepaths.append((m, n, os.path.join(OUT_DATA_DIR, f'{m_prefix}{n_prefix}{taskset_util_prefix}{IN_DATA_FILE_EXT}')))

def load_data(args):
    m, n, filepath = args

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
            taskset_collection.append((taskset, m))
            taskset = []
    print("Processed data from file:", filepath)
    return taskset_collection

results = []
with multiprocessing.Pool(NUM_THREADS) as pool:
    value = pool.map(load_data, filepaths)
    results = value
    
def process_data(args):
    taskset, m = args
    success, forest = recursive_gang_schedule(taskset, m)

    n = len(taskset)
    arr = np.zeros((40, ))
    if success:
        response_bound_map = {}
        for tree in forest.trees:
            response_bound_map.update(tree.response_bounds.items())
        for jdx, val in enumerate(response_bound_map.values()):
            arr[jdx] = val

    return success, n, m, arr

print("Starting schedulability tests")
outputs = []
response_times = []
for i, res in enumerate(results):
    print('processing', i, 'out of', len(results))
    with multiprocessing.Pool(NUM_THREADS) as pool:
        intermediate = pool.map(process_data, res)
        output_term = list(map(lambda x: (x[0], x[1], x[2]), intermediate))
        arr = list(map(lambda x: x[3], intermediate))


        response_times = response_times + arr
        outputs = outputs + output_term
output_df = pd.DataFrame(outputs, columns=['success', 'taskset size', 'processor count'])
response_times_df = pd.DataFrame(np.array(response_times))

output_df.to_csv('prelim_results.csv')
response_times_df.to_csv('response_time_data.csv')
# print(output_df[output_df['success'] == True].head())