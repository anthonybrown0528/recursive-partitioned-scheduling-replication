import heapq
from task import Task

class Partition:
    def __init__(self, m: int):
        self.m = m
        self.tasks = []

        # Maintains how many processors in each disjoint partition
        # are assigned to any task
        self.task_partition_map = {}

    def add_task(self, task: Task, m: int):
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
        self.tasks.remove(task)
        del self.task_partition_map[task]

    def greater_priority(self, task):
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