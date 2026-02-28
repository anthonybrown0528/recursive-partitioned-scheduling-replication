import heapq

import numpy as np

from task import Task
from partition import Partition

from util import is_schedulable

class PartitionTree:
    def __init__(self, m: int):
        # Number of available processors
        self.m = m

        # Partition tree starts with
        # one partition with all available processors
        self.parts = [Partition(m)] 

        # Maintains how many processors in each disjoint partition
        # are assigned to any task
        self.task_partition_map = {}

    def create_subpartitions(self, i: int, tasklist: list[Task]):
        if i < 0 or i >= len(self.parts):
            raise ValueError("Invalid index for subpartition")

        part = self.parts.pop(i)
        task_queue = sorted(tasklist)
        
        # Find task with the least amount of threads
        # mapped to the original partition
        m_min  = self.task_partition_map[(tasklist[0], part)]
        for task in tasklist[1:]:
            proc_alloc = self.task_partition_map[(task, part)]
            m_min = min(m_min, proc_alloc)

        shared = []
        nonshared = []

        mk = 0
        for task in task_queue:
            mi = self.task_partition_map[(task, part)]
            if m_min + mi > len(part.m):
                shared.append(task)
            else:
                nonshared.append(task)
                mk = mi

        # Check if all tasks are shared on the partition
        if len(shared) == len(tasklist):
            return False

        pl = Partition(mk)
        pr = Partition(part.m - mk)

        for task in shared:
            proc_alloc = self.task_partition_map[(task, part)]
            self.add_task(task, [pl, pr], [mk, proc_alloc - mk])
        for task in nonshared:
            proc_alloc = self.task_partition_map[(task, part)]
            schedulable = False
            for leaf in [pl, pr]:
                test_list = leaf.tasks
                heapq.heappush(test_list, task)
                if leaf.m >= proc_alloc and is_schedulable(test_list):
                    schedulable = True
                    self.add_task(task, [leaf], [proc_alloc])
                    break
            if not schedulable:
                return schedulable


    def add_task(self, task: Task, partitions: list[Partition], m_per_part: list[int] ):
        if np.sum(m_per_part) != task.m:
            raise ValueError("Mismatch in task parallelism and processors to allocated")

        # Associate a task to multiple partitions
        task.partitions = partitions
        [partition.add_task(task) for partition in partitions]

        # Specify how many processors in each partition
        # is allocated for a task
        for i, partition in enumerate(partitions):
            self.task_partition_map[(task, partition)] = m_per_part[i]