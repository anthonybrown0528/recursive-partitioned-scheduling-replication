import numpy as np


def generate_task_sets(num_tasks: int, target_utilization: float) -> np.array:    
    
    # Utilization values for tasks
    task_utilizations = np.empty((num_tasks, ))

    # Random values used for the generation
    r = np.random.rand(num_tasks - 1)

    s = np.empty((num_tasks + 1, ))

    s[0] = 0
    s[num_tasks] = target_utilization

    for i in range(num_tasks - 1, 0, -1):
        scaler = r[i - 1] ** (1.0 / i)
        s[i] = s[i + 1] * scaler

    task_utilizations = s[1: num_tasks + 1] - s[0: num_tasks]
    return task_utilizations