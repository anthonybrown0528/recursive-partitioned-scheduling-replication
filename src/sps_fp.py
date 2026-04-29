from task import Task
from partition_forest import PartitionForest


def edf_schedulable(taskset: list[Task]) -> bool:
    """Check whether a given list of tasks is schedulable under Earliest-Deadline-First priority

    :param taskset: a collection of :class:`Task`
    :type taskset: list[Task]

    :return: a boolean indicating th schedulability of the task set
    :rtype: bool
    """

    u = 0
    for task in taskset:
        u = u + task.c / task.period
    return u <= 1

def sps_edf(taskset: list[Task], m: int):
    """Perform the Strictly Paritioned Scheduling algorithm with the Earliest-Deadline-First priority policy.

    :param taskset: list of tasks to schedule
    :type taskset: list[Task]

    :param m: total number of processors
    :type m: int

    :return: a tuple describing the schedulability and a NoneType for compatibility reasons
    :rtype: tuple[bool, None]
    """

    # Attempt to schedule
    # each task sequentially
    tasklist = sorted(taskset, key=lambda x: (-x.m, x.priority))

    partitions = []
    budget = m

    for task in tasklist:
        schedulable = False

        for part in partitions:
            if edf_schedulable(part + [task]):
                part.append(task)
                schedulable = True
                break
        if not schedulable and budget >= task.m:
            partitions.append([task])
            budget = budget - task.m
            
            schedulable = True
        elif not schedulable:
            return False, None
    return True, None


def sps_fp(taskset: list[Task], m: int) -> tuple[PartitionForest]:
    """Perform the Strictly Paritioned Scheduling algorithm with fixed priority.

    :param taskset: list of tasks to schedule
    :type taskset: list[Task]

    :param m: total number of processors
    :type m: int

    :return: a tuple describing the schedulability and response time bounds of tasks
    :rtype: tuple[bool, PartitionForest]
    """

    forest = PartitionForest(m)
    budget = m

    # Attempt to schedule
    # each task sequentially
    tasklist = sorted(taskset, key=lambda x: (-x.m, x.priority))

    for task in tasklist:
        schedulable = False
        mi = task.m

        # Attempt to fit a task in an 
        # existing leaf partition
        for leaf, tree in forest.leaves():
            if leaf.m >= mi and tree.check_schedulability(task, leaf, task.m):
                schedulable = True
                break
        if not schedulable and budget >= mi:
            added_tree = forest.create_tree(mi)
            added_tree.check_schedulability(task, added_tree.parts[0], task.m)

            budget = budget - mi
            schedulable = True
        elif not schedulable:
            return False, None

    return schedulable, forest