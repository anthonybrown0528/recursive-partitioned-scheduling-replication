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


    def create_subpartitions(self, i: int, tasklist: list[Task]):
        if i < 0 or i >= len(self.parts):
            raise ValueError("Invalid index for subpartition")

        part = self.parts.pop(i)
        task_queue = sorted(tasklist)
        
        # Find task with the least amount of threads
        # mapped to the original partition
        m_min  = part.task_partition_map[tasklist[0]]
        for task in tasklist[1:]:
            proc_alloc = part.task_partition_map[task]
            m_min = min(m_min, proc_alloc)

        shared = []
        nonshared = []

        mk = 0
        for task in task_queue:
            mi = part.task_partition_map[task]
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

        self.parts.append(pl)
        self.parts.append(pr)

        for task in shared:
            proc_alloc = part.task_partition_map[task]
            self.add_task(task, [pl, pr], [mk, proc_alloc - mk])
        for task in nonshared:
            proc_alloc = part.task_partition_map[task]
            schedulable = False
            for leaf in [pl, pr]:
                self.add_task(task, [leaf], [task.m])
                if leaf.m >= proc_alloc and is_schedulable(leaf.tasks):
                    schedulable = True
                    self.add_task(task, [leaf], [proc_alloc])
                    break
                self.remove_task(task, [leaf])
                
            if not schedulable:
                return schedulable


    def add_task(self, task: Task, partitions: list[Partition], m_per_part: list[int] ):
        if np.sum(m_per_part) != task.m:
            raise ValueError("Mismatch in task parallelism and processors to allocated")

        # Associate a task to multiple partitions
        task.partitions = partitions
        [partition.add_task(task, m_per_part[i]) for i, partition in enumerate(partitions)]

    def remove_task(self, task: Task, partitions: list[Partition]):
        task.partitions = []
        [partition.remove_task(task) for partition in partitions]