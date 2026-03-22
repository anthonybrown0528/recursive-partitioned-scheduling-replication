import numpy as np

from task import Task
from partition_forest import PartitionForest

from util import compute_dhp, compute_ihp, compute_response_time_bound, compute_dhp_noci

def sps(taskset: list[Task], m: int) -> tuple[bool, np.array]:
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