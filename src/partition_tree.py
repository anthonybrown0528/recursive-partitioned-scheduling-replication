from .task import Task
from .partition import Partition

from .util import is_schedulable

class PartitionTree:
    """Contains information about a partition tree

    :param response_bounds: stores response time bounds for each task
    :type response_bounds: dict[Task, int]

    :param dhp: stores the set of DHP tasks for each task
    :type dhp: dict[Task, set]

    :param ihp: stores the set of IHP tasks for each task
    :type ihp: dict[Task, set]

    :param parts: collection of :class:`Partition` objects within this tree
    :type parts: list[Partition]

    :param partition_assignment: stores the set of partitions in which a task is assigned
    :type partition_assignment: dict[Task, set]
    """

    def __init__(self, m: int):
        """Initialize a :class:`PartitionTree`

        :param m: number of processors to allocate
        :type m: int
        """

        # Maintains response time bounds
        # computed for mapped tasks
        self.response_bounds = dict()

        self.dhp = dict()
        self.ihp = dict()

        # Partition tree starts with
        # one partition with all available processors
        self.parts = [Partition(m)] 

        self.partition_assignment = dict()

    def create_subpartitions(self, part: Partition, use_sp=False) -> bool:
        """Create two disjoint :class:`Partition` objects from a parent :class:`Partition`

        :param part: the parent :class:`Partition` object
        :type part: Partition

        :param use_sp: a flag that toggles the use of shared priority, defaults to False
        :type use_sp: bool

        :return: a boolean that indicates the success or failure to schedule
        :rtype: bool
        """
        
        # Copy partition state
        tasklist = list(part.tasks)
        task_partition_map = dict(part.task_partition_map)

        task_queue = sorted(tasklist, key=lambda x: (-x.m, x.priority))

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

        pl = Partition(mk, depth=part.depth + 1)
        pr = Partition(part.m - mk, depth=part.depth + 1)

        for task in tasklist:
            self.remove_task(task, [part])

        for task in shared:

            if use_sp:
                task.backup_sp = task.sp
                task.sp = part.depth

            proc_alloc = task_partition_map[task]
            self.add_task(task, [pl, pr], [mk, proc_alloc - mk])
            is_schedulable(task, self.partition_assignment[task], pl, self.dhp, self.ihp, self.response_bounds)
        global_schedulable = True
        for task in nonshared:
            proc_alloc = task_partition_map[task]
            schedulable = False
            for leaf in [pl, pr]:
                if leaf.m >= proc_alloc and self.check_schedulability(task, leaf, proc_alloc):
                    schedulable = True
                    break
                
            if not schedulable:
                global_schedulable = False
                break
        
        if not global_schedulable:
            # Restore the original partition
            part.tasks = tasklist

            for task in shared:
                self.remove_task(task, [pl, pr])
                if use_sp:
                    task.sp = task.backup_sp
            for task in list(pl.tasks):
                self.remove_task(task, [pl])
            for task in list(pr.tasks):
                self.remove_task(task, [pr])
            return False

        self.parts.remove(part)

        self.parts.append(pl)
        self.parts.append(pr)

        return global_schedulable


    def add_task(self, task: Task, partitions: list[Partition], m_per_part: list[int]):
        """Add a task to a collection of :class:`Partition` objects

        :param task: the task which shall be added
        :type task: Task

        :param partitions: a collection of :class:`Partition` in which to add a given task
        :type partitions: list[Partition]

        :param m_per_part: a division of task threads to each :class:`Partition`
        :type m_per_part: list[int]
        """

        # Associate a task to multiple partitions
        if task not in self.partition_assignment:
            self.partition_assignment[task] = set(partitions)
        else:
            self.partition_assignment[task] = self.partition_assignment[task].union(set(partitions))

        for i, partition in enumerate(partitions):
            partition.add_task(task, m_per_part[i])

    def remove_task(self, task: Task, partitions: list[Partition]):
        """Remove a task from a collection of :class:`Partition` objects

        :param task: the task which shall be removed
        :type task: Task

        :param partitions: a collection of :class:`Partition` from which to remove a given task
        :type partitions: list[Partition]
        """
        self.partition_assignment[task] = self.partition_assignment[task].difference(set(partitions))
        for partition in partitions:
            partition.remove_task(task)

    def check_schedulability(self, task: Task, part: Partition, m: int) -> bool:
        """Check whether a given :class:`Task` in schedulable within a :class:`Partition`
        
        :param task: a :class:`Task`
        :type task: Task

        :param part: a :class:`Partition`
        :type part: Partition

        :return: a boolean indicating schedulability
        :rtype: bool
        """

        # Copy response bound state
        dhp_copy = dict(self.dhp)
        ihp_copy = dict(self.ihp) 
        rb_copy = dict(self.response_bounds)

        self.add_task(task, [part], [m])

        success = is_schedulable(task, self.partition_assignment[task], part, dhp_copy, ihp_copy, rb_copy)
        if success:
            self.dhp = dhp_copy
            self.ihp = ihp_copy
            self.response_bounds = rb_copy

            return True
        else:
            self.remove_task(task, [part])
        return False
