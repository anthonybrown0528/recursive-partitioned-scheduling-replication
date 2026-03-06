import numpy as np

from task import Task
from partition_forest import PartitionForest

from util import is_schedulable

def recursive_gang_schedule(taskset: list[Task], m: int) -> tuple[bool, np.array]:
    forest = PartitionForest(m)
    budget = m

    # Attempt to schedule
    # each task sequentially
    sorted_taskset = sorted(taskset, key=lambda x: (-x.m, x.period))

    for task in sorted_taskset:
        schedulable = False
        mi = task.m

        # Attempt to fit a task in an 
        # existing leaf partition
        for leaf, tree, part_idx in forest.leaves():
            tree.add_task(task, [leaf], [mi], task.m)
            if leaf.m >= mi and is_schedulable(leaf.tasks):
                schedulable = True

                break
            tree.remove_task(task, [leaf])
        if not schedulable and budget >= mi:
            added_tree = forest.create_tree(mi)
            added_tree.add_task(task, added_tree.parts, [mi], task.m)

            budget = budget - mi
            schedulable = True

            # Terminate the algorithm prematurely
            # if any task cannot be scheduled
            if not schedulable:
                return schedulable, forest
    return schedulable, forest