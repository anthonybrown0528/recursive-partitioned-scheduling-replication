import os
import numpy as np
import pandas as pd

# Path where input dataset will be stored
DATA_DIR = 'data'

# File extension of data files
IN_DATA_FILE_EXT = '.npy'
OUT_DATA_FILE_EXT = '.pqt'

# Output data directory
# NOTE: Adjust if a different output directory is desired
OUT_DATA_DIR = os.path.join(DATA_DIR, 'input', 'parquet')

# Create output directory if is does not already exist
if not os.path.exists(OUT_DATA_DIR):
    os.makedirs(OUT_DATA_DIR)

# Collection of numbers of processors to use
num_processors = np.array([8, 16])

# Number of tasks as a fraction of number of processors
num_tasks_scaled = np.array([1, 1.5, 2, 2.5])

# Total utilization of the task set as a fraction of number of processors
u_gang_scale = np.linspace(start=0.1, stop=1.0, num=10, endpoint=True)

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

            # Save data to dataset directory
            data = {
                'u-values': np.empty(2)     ,
                'periods': np.empty(2)      ,
                'parallelism': np.empty(2)  ,
                'wct': np.empty(2)          ,
                'deadlines': np.empty(2)    
            }

            for key in data:
                data[key] = np.load(os.path.join(DATA_DIR, f'{m_prefix}{n_prefix}{taskset_util_prefix}{key}{IN_DATA_FILE_EXT}'))
                data[key] = data[key].reshape(-1, 1).flatten()
            print("Loaded batch of data:", m, n, u_taskset)

            df = pd.DataFrame(data)
            df.to_parquet(os.path.join(OUT_DATA_DIR, f'{m_prefix}{n_prefix}{taskset_util_prefix}{OUT_DATA_FILE_EXT}'))