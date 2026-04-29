import math
import numpy as np

from .task import Task

interference_sets = {}
transformed_interference_sets = {}
processor_assignments = {}

suspension_inducer_sets = {}
response_bounds = {}

tasklist = []

def clear():
    """Initialize the state of the stationary scheduling algorithm
    """

    global interference_sets
    global transformed_interference_sets
    global processor_assignments

    global suspension_inducer_sets
    global response_bounds
    
    global tasklist

    interference_sets = {}
    transformed_interference_sets = {}
    processor_assignments = {}

    suspension_inducer_sets = {}
    response_bounds = {}

    tasklist = []

def compute_suspension_inducing_set(i: int, k: int) -> set[int]:
    """Compute the Suspension-Inducing set given a task and a suspension-inducing task

    :param i: identifies a :class:`Task`
    :type i: int

    :param k: identifies suspension-inducing :class:`Task`
    :type k: int

    :return: a set of indices for suspension-induced :class:`Task`
    :rtype: set[int]
    """

    suspension_inducer_set = set()
    for j in range(i):
        if j in interference_sets[i] and len(processor_assignments[j].intersection(processor_assignments[k])) == 0:
            suspension_inducer_set.add(j)
    suspension_inducer_sets[(i, k)] = suspension_inducer_set
    return suspension_inducer_set


def compute_interference_set(k: int) -> set[int]:
    """Compute the interference set of a task

    :param k: identifies a :class:`Task`
    :type k: int

    :return: a set of indices for :class:`Task` that interferes with the specified :class:`Task`
    :rtype: set[int]
    """

    interference_set = set()
    for j in range(k):
        if len(processor_assignments[j].intersection(processor_assignments[k])) != 0:
            interference_set.add(j)
    interference_sets[k] = interference_set
    return interference_set

def transform_interference_set(k: int) -> set[int]:
    """Compute the `s` attribute to each task in the interference set of a task

    :param k: identifies a :class:`Task`
    :type k: int

    :return: a set of indices for :class:`Task` that interferes with the specified :class:`Task`
    :rtype: set[int]
    """

    transformed_interference_set = set()
    for i in interference_sets[k]:
        task = tasklist[i]
        s = response_bounds[i] - task.c

        option = 0
        for j in suspension_inducer_sets[(i, k)]:
            term = 1
            term = term + math.ceil(response_bounds[i] / tasklist[j].period)

            term = term * task.c
            option = option + term
        s = min(s, option)
        transformed_interference_set.add((i, s))
    transformed_interference_sets[k] = transformed_interference_set
    return transformed_interference_set

def eq1(task: Task, transformed_interference_list: list[int]) -> int:
    """Checks the schedulabilty of a task

    This subroutine assumes X is a vector of zeros

    :param task: a :class:`Task` of which to check schedulability
    :type task: Task

    :param transformed_interference_list: a list of indices for :class:`Task` that interfere with the given :class:`Task`
    :type transformed_interference_list: list[int]

    :return: a response time bound for the task if schedulable
    :rtype: int
    """

    response_bound_old = 0
    response_bound_new = task.c

    n = len(transformed_interference_list)
    x = np.zeros(n)

    q_values = [0]
    for idx, (i, s) in reversed(list(enumerate(transformed_interference_list))):
        val = q_values[-1]
        val = val + s * x[idx]
        q_values.append(val)
    q_values.pop(0)
    q_values.reverse()

    while response_bound_new != response_bound_old and response_bound_new <= task.d:
        response_bound_old = response_bound_new
        response_bound_new = task.c
        for idx, (i, _) in enumerate(transformed_interference_list):
            interfering_task = tasklist[i]

            term = response_bound_old + q_values[idx] + (1 - x[idx]) * (response_bounds[i] - interfering_task.c)
            term = math.ceil(term / interfering_task.period) * interfering_task.c

            response_bound_new = response_bound_new + term
    return response_bound_new

def eq2(task: Task, transformed_interference_list: list[int]) -> int:
    """Checks the schedulabilty of a task

    This subroutine assigns X based on the values of S and the WCET of the interfering tasks

    :param task: a :class:`Task` of which to check schedulability
    :type task: Task

    :param transformed_interference_list: a list of indices for :class:`Task` that interfere with the given :class:`Task`
    :type transformed_interference_list: list[int]

    :return: a response time bound for the task if schedulable
    :rtype: int
    """

    response_bound_old = 0
    response_bound_new = task.c

    n = len(transformed_interference_list)
    x = np.zeros(n)
    S = [val[1] for val in transformed_interference_list]

    execution_times = [tasklist[i].c for i in range(n)] 
    mask = np.array(S).flatten() <= np.array(execution_times)
    x[mask] = 1

    q_values = [0]
    for idx, (i, s) in reversed(list(enumerate(transformed_interference_list))):
        val = q_values[-1]
        val = val + s * x[idx]
        q_values.append(val)
    q_values.pop(0)
    q_values.reverse()

    while response_bound_new != response_bound_old and response_bound_new <= task.d:
        response_bound_old = response_bound_new
        response_bound_new = task.c
        for idx, (i, _) in enumerate(transformed_interference_list):
            interfering_task = tasklist[i]

            term = response_bound_old + q_values[idx] + (1 - x[idx]) * (response_bounds[i] - interfering_task.c)
            term = math.ceil(term / interfering_task.period) * interfering_task.c

            response_bound_new = response_bound_new + term
    return response_bound_new

def eq3(task: Task, transformed_interference_list: list[int]) -> int:
    """Checks the schedulabilty of a task

    This subroutine assigns X based on a linear combination

    :param task: a :class:`Task` of which to check schedulability
    :type task: Task

    :param transformed_interference_list: a list of indices for :class:`Task` that interfere with the given :class:`Task`
    :type transformed_interference_list: list[int]

    :return: a response time bound for the task if schedulable
    :rtype: int
    """

    response_bound_old = 0
    response_bound_new = task.c
    
    n = len(transformed_interference_list)
    x = np.zeros(n)    

    util_sum = 0
    for idx, (i, s) in enumerate(transformed_interference_list):
        t = tasklist[i]
        tu = t.c / t.period
        util_sum = util_sum + tu
        if tu * (response_bounds[i] - t.c) > s * util_sum:
            x[idx] = 1

    q_values = [0]
    for idx, (i, s) in reversed(list(enumerate(transformed_interference_list))):
        val = q_values[-1]
        val = val + s * x[idx]
        q_values.append(val)
    q_values.pop(0)
    q_values.reverse()

    while response_bound_new != response_bound_old and response_bound_new <= task.d:
        response_bound_old = response_bound_new
        response_bound_new = task.c
        for idx, (i, _) in enumerate(transformed_interference_list):
            interfering_task = tasklist[i]

            term = response_bound_old + q_values[idx] + (1 - x[idx]) * (response_bounds[i] - interfering_task.c)
            term = math.ceil(term / interfering_task.period) * interfering_task.c

            response_bound_new = response_bound_new + term
    return response_bound_new

def is_schedulable(k: int, transformed_interference_set: set[int]) -> bool:
    """Checks the schedulabilty of a task

    This subroutine performs three checks and returns an indicator of
    success if any of the checks return a valid response time bound
    
    :param k: identifies a :class:`Task`
    :type k: int

    :param transformed_interference_list: a list of indices for :class:`Task` that interfere with the given :class:`Task`
    :type transformed_interference_list: list[int]

    :return: a boolean indicating the schedulability of the specified task
    :rtype: bool
    """

    task = tasklist[k]
    if len(transformed_interference_set) == 0:
        response_bounds[k] = task.c
        return True

    transformed_interference_list = sorted(list(transformed_interference_set))

    response_bound_new = np.min([eq1(task, transformed_interference_list), eq2(task, transformed_interference_list), eq3(task, transformed_interference_list)])
    if response_bound_new > task.d:
        return False
    response_bounds[k] = response_bound_new
    return True

def assign_processors(k: int, j: int, m: int):
    """Assign a contiguous set of processors to a given task

    The processors are modeled as a circulary array

    :param k: identifies a :class:`Task`
    :type k: int

    :param j: indicates the first processor to assign to the task
    :type j: int

    :param m: number of threads in the task
    :type m: int
    """

    assignment = set()
    task = tasklist[k]
    for i in range(j, j + task.m):
        assignment.add(i % m)
    processor_assignments[k] = assignment

def stationary_schedule(taskset: list[Task], m: int):
    """Perform the Stationary Scheduling algorithm with fixed priority.

    :param taskset: list of tasks to schedule
    :type taskset: list[Task]

    :param m: total number of processors
    :type m: int

    :return: a tuple describing the schedulability and a NoneType for compatibility reasons
    :rtype: tuple[bool, None]
    """

    global tasklist

    clear()

    sorted_tasks = sorted(taskset)
    tasklist = sorted_tasks
    for k, _ in enumerate(sorted_tasks):
        schedulable = False
        for j in range(m):
            assign_processors(k, j, m)
            interference_set = compute_interference_set(k)
            for i in interference_set:
                compute_suspension_inducing_set(i, k)
            interference_set = transform_interference_set(k)

            if is_schedulable(k, interference_set):
                schedulable = True
                break
        if not schedulable:
            return False, None
    return True, None