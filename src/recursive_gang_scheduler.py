from .task import Task
from .partition_forest import PartitionForest


def recursive_gang_schedule(taskset: list[Task], m: int, use_sp=False) -> tuple[bool, PartitionForest]:
    """Perform the Recursive Paritioned Scheduling algorithm with fixed priority.

    :param taskset: list of tasks to schedule
    :type taskset: list[Task]

    :param m: total number of processors
    :type m: int

    :param use_sp: flag that toggles shared priority, defaults to False
    :type use_sp: bool

    :return: a tuple describing the schedulability and response time bounds of tasks
    :rtype: tuple[bool, PartitionForest]
    """

    # Initialize a partition forest with m available processors
    forest = PartitionForest(m)
    budget = m

    # Attempt to schedule
    # each task sequentially
    tasklist = sorted(taskset, key=lambda x: (-x.m, x.priority))

    # Iterate over each task in the provided list
    for task in tasklist:
        schedulable = False
        mi = task.m

        # Attempt to fit a task in an 
        # existing leaf partition
        for leaf, tree in forest.leaves():
            if leaf.m >= mi and tree.check_schedulability(task, leaf, task.m):
                schedulable = True
                break
        # Attempt to create a new partition for the task
        if not schedulable and budget >= mi:
            added_tree = forest.create_tree(mi)
            added_tree.check_schedulability(task, added_tree.parts[0], task.m)

            budget = budget - mi
            schedulable = True
        elif not schedulable:
            # Attempt to split an existing partition into
            # two subpartitions to fit the new task
            for leaf, tree in forest.leaves():
                if leaf.m >= mi:
                    tree.add_task(task, [leaf], [task.m])
                    success = tree.create_subpartitions(leaf, use_sp=use_sp)
                    
                    # Found a leaf partition which can be subpartitioned
                    # to fit the current task
                    if success:

                        # Add task to the left and right leaf partitions
                        schedulable = True

                        # Stop searching for leaves to subpartition
                        break

                    # Remove the task from the leaf if the tasks
                    # in the leaf are not schedulable with the new task
                    tree.remove_task(task, [leaf])

            # Terminate the algorithm prematurely
            # if any task cannot be scheduled
            if not schedulable:
                return schedulable, forest
            
    # Return the schedulability of the taskset and the 
    # response time bounds if schedulable
    return schedulable, forest