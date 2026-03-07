import os
import numpy as np
import pandas as pd
import pickle
import signal

def handler(signum, frame):
    raise RuntimeError("Too long")

signal.signal(signal.SIGALRM, handler)

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

            df = pd.read_parquet(os.path.join(OUT_DATA_DIR, f'{m_prefix}{n_prefix}{taskset_util_prefix}{IN_DATA_FILE_EXT}'))
            print("Loaded batch of data:", m, n, u_taskset)

            # Save data to dataset directory
            data = [
                'u-values',
                'periods',
                'parallelism',
                'wct',
                'deadlines'    
            ]

            taskset = []
            taskset2 = []
            
            another_ctr = 0
            for i, row in df.iterrows():
                t = Task(round(row[data[2]]), row[data[3]], round(row[data[4]]), round(row[data[1]]), round(row[data[4]]))
                t2 = Task(round(row[data[2]]), row[data[3]], round(row[data[4]]), round(row[data[1]]), round(row[data[4]]))
                
                taskset.append(t)
                taskset2.append(t2)

                if len(taskset) == n:
                    # another_ctr = another_ctr + 1
                    # if another_ctr % 100 == 0 and i >= 7999 and ctr == 1:
                    #     print('apply algo: ', i)

                    signal.alarm(30)
                    try:
                        recursive_gang_schedule(taskset, m)
                        taskset.clear()
                        taskset2.clear()
                    except Exception as exc:
                        print(i)
                        print('saving taskset to file...')
                        obj = pickle.dumps(taskset2)
                        with open('dump7.pkl', 'wb') as file:
                            pickle.dump(obj, file)
                        print('saved to file')
                        raise exc

