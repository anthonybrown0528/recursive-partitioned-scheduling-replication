import math

from .task import Task
from .partition import Partition

def compute_dhp(task: Task, partitions: set[Partition], dhp: dict[Task, set]) -> set:
    """Compute the DHP set of a task

    :param task: a :class:`Task`
    :type task: Task

    :param partitions: a set of partitions in which a given task belongs
    :type partitions: set[Partition]

    :param dhp: a global store of DHP set for each task
    :type dhp: dict[Task, set]

    :return: the DHP set of the given task
    :rtype: set[Task]
    """
    
    dhp_taskset = set()
    for part in partitions:
        tasklist = part.greater_priority(task)
        dhp_taskset = dhp_taskset.union(tasklist)
    dhp[task] = dhp_taskset
    return dhp_taskset

def compute_ihp(task: Task, dhp_taskset: set, ihp: dict[Task, set], dhp: dict[Task, set]) -> set:
    """Compute the IHP set of a task

    :param task: a :class:`Task`
    :type task: Task

    :param dhp_taskset: the DHP set of the given task
    :type dhp_taskset: set[Task]

    :param ihp: a global store of IHP set for each task
    :type ihp: dict[Task, set]

    :param dhp: a global store of DHP set for each task
    :type dhp: dict[Task, set]

    :return: the IHP set of the given task
    :rtype: set[Task]
    """

    ihp_taskset = set()
    for t in dhp_taskset:
        ihp_taskset = ihp_taskset.union(ihp[t])
        ihp_taskset = ihp_taskset.union(dhp[t])
    for t in dhp_taskset:
        ihp_taskset = ihp_taskset.difference(dhp_taskset)

    ihp[task] = ihp_taskset
    return ihp_taskset

def compute_dhp_noci(dhp_taskset: set[Task], dhp: dict[Task, set], ihp: dict[Task, set]) -> set:
    """Compute the DHP_noci set of a task

    :param dhp_taskset: the DHP set of the given task
    :type dhp_taskset: set[Task]

    :param dhp: a global store of DHP set for each task
    :type dhp: dict[Task, set]

    :param ihp: a global store of IHP set for each task
    :type ihp: dict[Task, set]

    :return: the DHP_noci set of the given task
    :rtype: set[Task]
    """

    dhp_noci = set()


    for t in dhp_taskset:
        dhp_t = dhp[t]
        ihp_t = ihp[t]

        if dhp_t.issubset(dhp_taskset) and len(ihp_t) == 0:
            dhp_noci.union(dhp_t)
            dhp_noci.add(t)
    return dhp_noci

def compute_response_time_bound(task: Task, dhp: set[Task], dhp_noci: set[Task], response_bounds: dict[Task, float]):
    """Compute the response time bound of a task

    :param task: a :class:`Task`
    :type task: Task

    :param dhp: the DHP set of the given task
    :type dhp: set[Task]

    :param dhp_noci: the DHP_noci set of the given task
    :type dhp_noci: set[Task]

    :param response_bounds: a global store of response time bounds for each task
    :type response_bounds: dict[Task, int]
    """

    rr = task.c
    interference = 0

    for t in dhp:
        term = 0
        if t in dhp_noci:
            term = math.ceil(rr / t.period) * t.c
        else:
            term = math.ceil((rr + response_bounds[t] - t.c) / t.period) * t.c
        interference = interference + term
    rl = task.c + interference

    while rl != rr and rl <= task.d:
        rr = rl
        interference = 0

        for t in dhp:
            term = 0
            if t in dhp_noci:
                term = math.ceil(rr / t.period) * t.c
            else:
                term = math.ceil((rr + response_bounds[t] - t.c) / t.period) * t.c
            interference = interference + term
        rl = task.c + interference
    response_bounds[task] = rl 

def is_schedulable(task: Task, partitions: set[Partition], part: Partition, dhp: dict[Task, set[Task]], ihp: dict[Task, set[Task]], response_bounds: dict[Task, float]) -> bool:
    """Compute the DHP set of a task

    :param task: a :class:`Task` that was inserted into a partition
    :type task: Task

    :param partitions: a set of partitions in which a given task belongs
    :type partitions: set[Partition]

    :param part: a partition of which to check schedulability
    :type part: Partition

    :param dhp: a global store of DHP set for each task
    :type dhp: dict[Task, set]

    :param ihp: a global store of IHP set for each task
    :type ihp: dict[Task, set]

    :param response_bounds: a global store of response time bounds for each task
    :type response_bounds: dict[Task, int]

    :return: a boolean indicating the schedulability of a task
    :rtype: bool
    """


    taskset = part.atmost_priority(task)
    for t in taskset:
        compute_dhp(t, partitions, dhp)
        compute_ihp(t, dhp[t], ihp, dhp)

        dhp_noci = compute_dhp_noci(dhp[t], dhp, ihp)

        compute_response_time_bound(t, dhp[t], dhp_noci, response_bounds)
        if response_bounds[t] > t.d:
            return False
    return True