from task import Task

class Partition:
    """Contains information about processor partitions

    :param m: number of processors assigned to this :class:`Partition`
    :type m: int

    :param depth: the depth within its :class:`PartitionTree`, defaults to 0
    :type depth: int

    :param task_partition_map: stores the number of partition processors assigned to a task
    :type task_partition_map: dict[Task, int]
    """

    def __init__(self, m: int, depth=0):
        """Initialize the :class:`Partition`

        :param m: number of processors to assign
        :type m: int

        :param depth: the depth within its :class:`PartitionTree`, defaults to 0
        :type depth: int
        """

        self.m = m
        self.tasks = []

        self.depth = depth

        # Maintains how many processors in each disjoint partition
        # are assigned to any task
        self.task_partition_map = {}

    def add_task(self, task: Task, m: int):
        """Add a task to the partition

        :param task: a :class:`Task` to add to the partition
        :type task: Task

        :param m: number of processors to assign the :class:`Task` within the :class:`Partition`
        :type m: int
        """

        left = 0
        right = len(self.tasks) - 1

        while left <= right:
            mid = left + (right - left) // 2
            if task > self.tasks[mid]:
                left = mid + 1
            elif task < self.tasks[mid]:
                right = mid - 1
            else:
                self.task_partition_map[task] = m
                return
        self.tasks.insert(left, task) 
        self.task_partition_map[task] = m

    def remove_task(self, task: Task):
        """Remove a :class:`Task` from the partition

        :param task: a :class:`Task` to remove from the partition
        :type task: Task
        """

        self.tasks.remove(task)

    def greater_priority(self, task) -> list[Task]:
        """Get each :class:`Task` which has greater priority than a given :class:`Task`

        :param task: a :class:`Task` with a defined priority
        :type task: Task

        :return: a list of :class:`Task` objects with greater priority than the argument
        :rtype: list[Task]
        """

        left = 0
        right = len(self.tasks) - 1

        while left <= right:
            mid = left + (right - left) // 2
            compared = self.tasks[mid]
            if task == compared:
                return self.tasks[:mid]
            elif task < compared:
                right = mid - 1
            else:
                left = mid + 1
        return []

    def atmost_priority(self, task):
        """Get each :class:`Task` which has priority less than or equal to a given :class:`Task`

        :param task: a :class:`Task` with a defined priority
        :type task: Task

        :return: a list of :class:`Task` objects with greater priority than the argument
        :rtype: list[Task]
        """

        left = 0
        right = len(self.tasks) - 1

        while left <= right:
            mid = left + (right - left) // 2
            compared = self.tasks[mid]
            if task == compared:
                return self.tasks[mid:]
            elif task < compared:
                right = mid - 1
            else:
                left = mid + 1
        return []