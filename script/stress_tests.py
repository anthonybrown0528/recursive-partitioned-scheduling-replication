# Make Python modules in `src` folder accessible
import os
import sys
sys.path.append(os.path.abspath('./'))

from src.task import Task

from src.recursive_gang_scheduler import recursive_gang_schedule

taskset1 = [
    [3, 1, 1, 4],
    [2, 1, 1, 4],
    [2, 1, 2, 4],
    [2, 1, 2, 4],
    [2, 1, 4, 4],
    [2, 1, 4, 4],
    [2, 1, 4, 4],
    [2, 1, 4, 4],
    [1, 1, 2, 4],
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
        taskset.append(Task(m, c, d, p, d))
    return taskset


def process_data(taskset, m, use_sp):
    if not use_sp:
        success, forest, num_scheduled_tasks = recursive_gang_schedule(taskset, m)
    else:
        success, forest, num_scheduled_tasks = recursive_gang_schedule(taskset, m, use_sp=True)

    n = len(taskset)
    return success, n, m, num_scheduled_tasks, forest

def print_forest_details(forest):
    print('=' * 40)
    for leaf, tree in forest.leaves():

        task_id = list(map(lambda x: (x.id, x.m, x.c, x.d), leaf.tasks))
        print(task_id, leaf.m)
        print('=' * 40)

    print('-' * 40)

success, _, _, _, forest = process_data(create_taskset(taskset1), 5, False)
print(success)
print_forest_details(forest)

success, _, _, _, forest = process_data(create_taskset(taskset2), 4, False)
print(success)
print_forest_details(forest)

success, _, _, _, forest = process_data(create_taskset(taskset1), 5, True)
print(success)
print_forest_details(forest)

success, _, _, _, forest = process_data(create_taskset(taskset2), 4, True)
print(success)
print_forest_details(forest)