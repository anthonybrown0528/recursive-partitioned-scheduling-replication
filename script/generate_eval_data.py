import os
import numpy as np
import pandas as pd

from generate_task_sets import generate_task_sets

# Path where dataset will be stored
DATA_DIR = 'data'

# File extension of data files
DATA_FILE_EXT = '.npy'

# Maximum number of retry attempts to
# generate a task set with utilization
# below the period
MAX_RETRY = 10_000

# Collection of numbers of processors to use
num_processors = np.array([8, 16])

# Number of tasks as a fraction of number of processors
num_tasks_scaled = np.array([1, 1.5, 2, 2.5])

# Total utilization of the task set as a fraction of number of processors
u_gang_scale = np.linspace(start=0.1, stop=1.0, num=10, endpoint=True)

rng = np.random.default_rng()

# Create the dataset directory if it
# does not already exist
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

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

            # Generate utilization values
            u_values = np.zeros((1_000, 2, 2, n))

            # Generate periods uniformly
            periods = rng.integers(low=100, high=1_000, size=u_values.shape, endpoint=True)

            # Generate task parallelism values
            m_i = np.empty_like(periods)

            # Uniformly sample task parallelism in [1, m / 2]
            m_i[:, 0] = rng.integers(low=1, high=m/2, endpoint=True, size=(u_values.shape[0], u_values.shape[2], u_values.shape[3]))
            # Uniformly sample task parallelism in [1, m]
            m_i[:, 1] = rng.integers(low=1, high=m, endpoint=True, size=(u_values.shape[0], u_values.shape[2], u_values.shape[3]))

            c = np.empty_like(periods)

            for i in range(u_values.shape[0]):
                for j in range(u_values.shape[1]):
                    for k in range(u_values.shape[2]):
                        u_values[i, j, k] = generate_task_sets(n, u_taskset)

                        # Compute worst-case execution times
                        c[i, j, k] = u_values[i, j, k] * periods[i, j, k] / m_i[i, j, k]

                        # Regenerate task set if any worst-case execution time
                        # is greater than the task period
                        retry_ctr = 0
                        while np.any(c[i, j, k] > periods[i, j, k]) and retry_ctr < MAX_RETRY:
                            u_values[i, j, k] = generate_task_sets(n, u_taskset)

                            # Compute worst-case execution times
                            c[i, j, k] = u_values[i, j, k] * periods[i, j, k] / m_i[i, j, k]
                            
                            retry_ctr = retry_ctr + 1
                        if np.any(c[i, j, k] > periods[i, j, k]):
                            print("Failed to generate valid task set below period")

            # print(c.shape, n, u_taskset)
            # print(np.min(c), np.min(u_values), np.max(periods), np.min(m_i))

            # Generate deadlines
            deadlines = np.empty_like(periods)
            for i in range(u_values.shape[0]):
                for j in range(u_values.shape[1]):
                    for l in range(u_values.shape[3]):
                        # Uniformly sample constrained deadlines
                        # val1 = 0.8 * periods[i, j, 0, l]
                        # val2 = c[i, j, 0, l]
                        # val3 = periods[i, j, 0, l]

                        deadlines[i, j, 0, l] = rng.integers(low=max(0.8 * periods[i, j, 0, l], c[i, j, 0, l]), high=periods[i, j, 0, l], endpoint=True)

            # Set implicit deadlines
            deadlines[:, :, 1] = periods[:, :, 1]

            # Save data to dataset directory
            data = [
                ('u-values', u_values),
                ('periods', periods),
                ('parallelism', m_i),
                ('wct', c),
                ('deadlines', deadlines)
            ]

            for entry in data:
                np.save(os.path.join(DATA_DIR, f'{m_prefix}{n_prefix}{taskset_util_prefix}{entry[0]}{DATA_FILE_EXT}'), entry[1])
            print("Saved batch of data:", m, n, u_taskset)