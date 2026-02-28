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


    def create_subpartitions(self, part: Partition):
        tasklist = list(part.tasks)
        self.parts.remove(part)
        task_queue = sorted(tasklist, key=lambda x: (-x.m, x.priority))
        
        task_partition_map = dict(part.task_partition_map)
        [self.remove_task(task, [part]) for task in tasklist]

        # Find task with the least amount of threads
        # mapped to the original partition
        m_min  = task_partition_map[tasklist[0]]
        for task in tasklist[1:]:
            proc_alloc = task_partition_map[task]
            m_min = min(m_min, proc_alloc)

        shared = []
        nonshared = []

        mk = 0
        for task in task_queue:
            mi = task_partition_map[task]
            if m_min + mi > part.m:
                shared.append(task)
            else:
                nonshared.append(task)
                mk = max(mk, mi)

        # Check if all tasks are shared on the partition
        if len(shared) == len(tasklist):
            return False

        pl = Partition(mk)
        pr = Partition(part.m - mk)

        self.parts.append(pl)
        self.parts.append(pr)

        for task in shared:
            proc_alloc = task_partition_map[task]
            self.add_task(task, [pl, pr], [mk, proc_alloc - mk], proc_alloc)
        global_schedulable = True
        for task in nonshared:
            proc_alloc = task_partition_map[task]
            schedulable = False
            for leaf in [pl, pr]:
                self.add_task(task, [leaf], [task.m], proc_alloc)
                if leaf.m >= proc_alloc and is_schedulable(leaf.tasks):
                    schedulable = True
                    break
                self.remove_task(task, [leaf])
                
            if not schedulable:
                global_schedulable = False
                break
        
        if not global_schedulable:
            for task in shared:
                proc_alloc = task_partition_map[task]

                self.remove_task(task, [pl, pr])
                self.add_task(task, [part], [proc_alloc], proc_alloc)
            for task in list(pl.tasks):
                self.remove_task(task, [pl])
            for task in list(pr.tasks):
                self.remove_task(task, [pr])
            for task in nonshared:
                proc_alloc = task_partition_map[task]
                self.add_task(task, [part], [proc_alloc], proc_alloc)
            self.parts.remove(pl)
            self.parts.remove(pr)
            self.parts.append(part) 


        return global_schedulable


    def add_task(self, task: Task, partitions: list[Partition], m_per_part: list[int], part_parallel: int):
        if np.sum(m_per_part) != part_parallel:
            raise ValueError("Mismatch in task parallelism and processors to allocated")

        # Associate a task to multiple partitions
        task.partitions = task.partitions + partitions
        [partition.add_task(task, m_per_part[i]) for i, partition in enumerate(partitions)]

    def remove_task(self, task: Task, partitions: list[Partition]):
        [task.partitions.remove(partition) for partition in partitions]
        [partition.remove_task(task) for partition in partitions]