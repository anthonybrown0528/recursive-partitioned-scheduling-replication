import numpy as np

from task import Task
from partition_forest import PartitionForest

from util import compute_dhp, compute_ihp, compute_response_time_bound, compute_dhp_noci

def recursive_gang_schedule(taskset: list[Task], m: int, use_sp=False) -> tuple[bool, np.array]:
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

                    # dhp = compute_dhp(task, [leaf], tree.dhp)
                    # compute_ihp(task, dhp, tree.ihp, tree.dhp)
                    # dhp_noci = compute_dhp_noci(dhp, tree.dhp, tree.ihp)
                    # compute_response_time_bound(task, dhp, dhp_noci, tree.response_bounds)

                    success = tree.create_subpartitions(leaf, use_sp=use_sp)
                    
                    # Found a leaf partition which can be subpartitioned
                    # to fit the current task
                    if success:

                        # Add task to the left and right leaf partitions
                        schedulable = True

                        # Stop searching for leaves to subpartition
                        break
                    
                    # del tree.dhp[task]
                    # del tree.ihp[task]
                    # del tree.response_bounds[task]
                    tree.remove_task(task, [leaf])

            # Terminate the algorithm prematurely
            # if any task cannot be scheduled
            if not schedulable:
                return schedulable, forest
    return schedulable, forest