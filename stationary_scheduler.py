import math
import numpy as np

from task import Task

interference_sets = {}
transformed_interference_sets = {}
processor_assignments = {}

suspension_inducer_sets = {}
response_bounds = {}

taskset = []

def compute_suspension_inducing_set(i: int, k: int) -> set[int]:
    suspension_inducer_set = set()
    for j in range(i):
        if j in interference_sets[i] and len(processor_assignments[j].intersection(processor_assignments[k])) == 0:
            suspension_inducer_set.add(j)
    suspension_inducer_sets[(i, k)] = suspension_inducer_set
    return suspension_inducer_set


def compute_interference_set(k: int, mk: int, m: int) -> set[int]:
    interference_set = set()
    for j in range(k):
        if len(processor_assignments[j].intersection(processor_assignments[k])) != 0:
            interference_set.add(j)
    interference_sets[k] = interference_set
    return interference_set

def transform_interference_set(k: int):
    transformed_interference_set = set()
    for i in interference_sets[k]:
        task = taskset[i]
        s = task.r - task.c

        option = 0
        for j in suspension_inducer_sets[(i, k)]:
            term = 1
            term = term + math.ceil(task.r / taskset[j].r)

            term = term * task.c
            option = option + term
        s = min(s, option)
        transformed_interference_set.add((i, s))
    transformed_interference_sets[k] = transformed_interference_set
    return transformed_interference_set

def is_schedulable(k: int, transformed_interference_set: set[int]):
    task = taskset[k]

    response_bound_old = task.c
    response_bound_new = 0

    transformed_interference_list = sorted(list(transformed_interference_set))

    x = np.zeros(len(transformed_interference_list))

    it = enumerate(transformed_interference_list)
    (idx, (i, s)) = next(it)

    q_values = [s * x[idx]]

    for idx, (i, s) in it:
        val = q_values[-1]
        val = val + s * x[idx]
        q_values.append(val)

    while response_bound_new != response_bound_old and response_bound_new < task.d:
        response_bound_new = 0
        for (i, _) in transformed_interference_list:
            interfering_task = taskset[i]

            term = response_bound_old + q_values[i] + (1 - x[i]) * (response_bounds[i] - interfering_task.c)
            term = math.ceil(term / interfering_task.period)

            response_bound_new = response_bound_new + term
    if response_bound_new > task.d:
        return False
    response_bounds[k] = response_bound_new
    return True

def assign_processors(k: int, j: int, m: int):
    assignment = set()
    task = taskset[k]
    for i in range(j, j + task.m):
        assignment.add(i % m)
    processor_assignments[k] = assignment
def stationary_schedule(taskset: list[Task], m: int):
    sorted_tasks = sorted(taskset)
    for k, task in enumerate(sorted_tasks):
        schedulable = False
        for j in range(m):
            assign_processors(task, j)
            interference_set = compute_interference_set(task.m, j, m)
            for i in interference_set:
                compute_suspension_inducing_set(i, k)
            interference_set = transform_interference_set(k)

            if is_schedulable(task, interference_set):
                schedulable = True
                break
        if not schedulable:
            return False