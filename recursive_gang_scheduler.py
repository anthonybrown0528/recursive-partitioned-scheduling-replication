import numpy as np

from task import Task
from partition_forest import PartitionForest

def recursive_gang_schedule(taskset: list[Task], m: int) -> tuple[bool, np.array]:
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
            for leaf, tree in forest.leaves():
                if leaf.m >= mi:
                    tree.add_task(task, [leaf], [task.m])
                    success = tree.create_subpartitions(leaf)
                    
                    # Found a leaf partition which can be subpartitioned
                    # to fit the current task
                    if success:

                        # Add task to the left and right leaf partitions
                        schedulable = True

                        # Stop searching for leaves to subpartition
                        break
                    tree.remove_task(task, [leaf])

            # Terminate the algorithm prematurely
            # if any task cannot be scheduled
            if not schedulable:
                return schedulable, forest
    return schedulable, forest