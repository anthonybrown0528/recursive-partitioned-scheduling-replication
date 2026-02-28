import heapq
from task import Task

class Partition:
    def __init__(self, m: int):
        self.m = m
        self.tasks = []

    def add_task(self, task: Task):
        heapq.heappush(self.tasks, task)

    def greater_priority(self, task):
        left = 0
        right = len(self.tasks) - 1

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