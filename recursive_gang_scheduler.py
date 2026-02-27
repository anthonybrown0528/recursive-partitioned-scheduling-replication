import numpy as np
import queue

import heapq

class Task:
    def __init__(self, m: int):
        self.partitions = []

        # Task parallelism
        self.m = m

class Partition:
    def __init__(self, m: int, root: PartitionTree):
        self.m = m
        self.tasks = []

        self.root = root

    def add_task(self, task: Task):
        heapq.heappush(self.tasks, task)

    def greater_priority(self, task):
        left = 0
        right = len(task) - 1

        while left <= right:
            mid = left + (right - left) // 2
            compared = self.tasks[mid]
            if task == compared:
                return self.tasks[:mid]
            elif task > compared:
                left = mid + 1
            else:
                right = mid - 1
        return []

class PartitionTree:
    def __init__(self, m: int):
        # Number of available processors
        self.m = m

        # Partition tree starts with
        # one partition with all available processors
        self.parts = [Partition(m, self)]

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

        pl = Partition(mk, self)
        pr = Partition(part.m - mk, self)

        for task in shared:
            proc_alloc = self.task_partition_map[(task, part)]
            self.add_task(task, [pl, pr], [mk, proc_alloc - mk])
        for task in nonshared:
            proc_alloc = self.task_partition_map[(task, part)]
            schedulable = False
            for leaf in [pl, pr]:
                if leaf.m >= proc_alloc and is_schedulable(task, leaf):
                    schedulable = True
                    self.add_task(task, [leaf], [proc_alloc])
                    break
            if not schedulable:
                return schedulable


    def add_task(self, task: Task, partitions: list[Partition], m_per_part: list[int] ):
        if np.sum(m_per_part) != task.m:
            raise ValueError("Mismatch in task parallelism and processors to allocated")

        # Associate a task to multiple partitions
        task.set_partitions(partitions)
        [partition.add_task(task) for partition in partitions]

        # Specify how many processors in each partition
        # is allocated for a task
        for i, partition in enumerate(partition):
            self.task_partition_map[(task, partition)] = m_per_part[i]



class PartitionForest:
    def __init__(self, m: int):
        self.trees = []
        self.m  = m

    def create_tree(self, mi: int) -> PartitionTree:
        if mi >= self.m:
            raise ValueError("Unable to allocate sufficient processors")
        
        self.m = self.m - mi
        added_tree = Partition(mi)
        self.trees.append(added_tree)

        return added_tree

    def leaves(self) -> list[Partition]:
        forest_partitions = []
        for tree in self.trees:
            forest_partitions = forest_partitions + tree.parts
        return forest_partitions

def compute_dhp(task: Task) -> set:
    partitions = task.partitions
    dhp_task_set = set()
    for part in partitions:
        tasklist = part.greater_priority(task)
        dhp_task_set = dhp_task_set.union(tasklist)
    return dhp_task_set

def compute_ihp(task: Task, dhp: set) -> set:
    q = queue.Queue()
    found = set()

    ihp = set()
    for t in dhp:
        q.put(t)
        found.add(q)
    while not q.empty():
        e = q.get()
        found.remove(e)

        dhp_e = compute_dhp(e)

        for te in dhp_e:
            if te not in found:
                q.put(te)
                found.add(te)
        if e not in dhp:
            ihp.add(e)
    return ihp

def compute_dhp_nocii(task, dhp: set) -> set:
    dhp_noci = set()

    for t in dhp:
        dhp_t = compute_dhp(t)
        ihp_t = compute_ihp(t)

        if dhp_t.issubset(dhp) and len(ihp_t) == 0:
            dhp_noci.union(dhp_t)
    return dhp_noci

def is_schedulable(task, partition) -> bool:
    dhp = compute_dhp(task)
    ihp = compute_ihp(task, dhp)
    dhp_noci = compute_dhp_noci(task)


def generate_sub_partition(assigned_tasks: list, leaf, forest: PartitionForest) -> tuple:
    sorted_tasks = sorted(assigned_tasks)
    m_min = None
    shared_tasks = []
    m_k = 0
    for task in sorted_tasks:
        m_i = leaf.processors_allocated(task)
        if m_min + m_i > len(leaf.procesors()):
            shared_tasks.append(task)
        else:
            m_k = m_i
    if len(assigned_tasks) == len(shared_tasks):
        return None, None, forest, False
    left_leaf, right_leaf = forest.create_subpartitions(leaf, m_k)
    for task in shared_tasks:
        pass
    non_shared_tasks = None
    for task in non_shared_tasks:
        schedulable = False
        for leaf in [left_leaf, right_leaf]:
            if leaf.processors() >= leaf.processors_allocated(task) and is_schedulable(task, leaf):
                schedulable = True
                leaf.tasks().append(task)
                break
        if not schedulable:
            return left_leaf, right_leaf, forest, schedulable
    return left_leaf, right_leaf, forest, True

def recursive_gang_schedule(taskset: list, m: int) -> tuple[bool, np.array]:
    forest = PartitionForest()
    budget = m

    # Attempt to schedule
    # each task sequentially
    for task in taskset:
        schedulable = False
        mi = task.m

        # Attempt to fit a task in an 
        # existing leaf partition
        for leaf in forest.leaves():
            if leaf.m >= mi and is_schedulable(task, leaf):
                leaf.tree.add_task(task, [leaf], [mi])
                schedulable = True

                break
        if not schedulable and budget >= mi:
            added_tree = forest.create_tree(mi)
            added_tree.add_task(task, added_tree.parts, mi)

            schedulable = True
        elif not schedulable:
            for leaf in forest.leaves():
                if len(leaf.processors()) >= mi:
                    leaf.tasks().append(task)
                    left_leaf, right_leaf, forest, success = generate_sub_partition(leaf.tasks(), leaf, forest)
                    
                    # Found a leaf partition which can be subpartitioned
                    # to fit the current task
                    if success:

                        # Add task to the left and right leaf partitions
                        schedulable = True

                        left_leaf.tasks().append(task)
                        right_leaf.tasks().append(task)
                        
                        # Stop searching for leaves to subpartition
                        break

            # Terminate the algorithm prematurely
            # if any task cannot be scheduled
            if not schedulable:
                return schedulable
    return schedulable