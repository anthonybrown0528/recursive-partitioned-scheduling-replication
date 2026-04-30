from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.task import Task

from src.recursive_gang_scheduler import recursive_gang_schedule

taskset1 = [
    [5, 1, 1, 4],
    [3, 1, 2, 4],
    [2, 1, 3, 4],
    [2, 1, 3, 4],
    [2, 1, 4, 4],
    [2, 1, 4, 4],
    [2, 1, 4, 4]
]

taskset2 = [
    [3, 2, 2, 5],
    [2, 2, 5, 5],
    [2, 1, 5, 5],
    [2, 1, 3, 5],
    [2, 2, 5, 5],
    [1, 2, 2, 5]
]

def create_taskset(tasks: list):
    taskset = []

    for entry in tasks:
        m, c, d, p = entry
        taskset.append(Task(m, c, d, p, p))
    return taskset


def process_data(taskset, m, use_sp):
    if not use_sp:
        success, forest, num_scheduled_tasks = recursive_gang_schedule(taskset, m)
    else:
        success, forest, num_scheduled_tasks = recursive_gang_schedule(taskset, m, use_sp=True)

    n = len(taskset)
    return success, n, m, num_scheduled_tasks

success, _, _, _ = process_data(create_taskset(taskset1), 4, False)
print(success)
success, _, _, _ = process_data(create_taskset(taskset2), 4, False)
print(success)