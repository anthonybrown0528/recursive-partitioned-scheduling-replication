import heapq

import numpy as np

from task import Task
from partition_forest import PartitionForest

from util import is_schedulable

def recursive_gang_schedule(taskset: list[Task], m: int) -> tuple[bool, np.array]:
    forest = PartitionForest(m)
    budget = m

    # Attempt to schedule
    # each task sequentially
    sorted_taskset = sorted(taskset, key=lambda x: (x.m, x.priority))

    for task in taskset:
        schedulable = False
        mi = task.m

        # Attempt to fit a task in an 
        # existing leaf partition
        for leaf, tree, part_idx in forest.leaves():
            test_list = list(leaf.tasks)
            heapq.heappush(test_list, task)
            if leaf.m >= mi and is_schedulable(test_list):
                tree.add_task(task, [leaf], [mi])
                schedulable = True

                break
        if not schedulable and budget >= mi:
            added_tree = forest.create_tree(mi)
            added_tree.add_task(task, added_tree.parts, [mi])

            schedulable = True
        elif not schedulable:
            for leaf in forest.leaves():
                if len(leaf.processors()) >= mi:
                    success = tree.create_partitions(part_idx, leaf.tasks + task)
                    
                    # Found a leaf partition which can be subpartitioned
                    # to fit the current task
                    if success:

                        # Add task to the left and right leaf partitions
                        schedulable = True

                        # Stop searching for leaves to subpartition
                        break

            # Terminate the algorithm prematurely
            # if any task cannot be scheduled
            if not schedulable:
                return schedulable, forest
    return schedulable, forest