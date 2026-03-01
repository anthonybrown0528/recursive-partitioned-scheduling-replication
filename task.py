from functools import total_ordering

id = 0

@total_ordering
class Task:
    def __init__(self, m: int, c: float, d: int, period: int, priority: int):
        global id
        self.partitions = []

        self.id = id
        id = id + 1

        # Task parallelism
        self.m = m

        self.c = c
        self.d = d
        self.period = period

        self.priority = priority

    def __lt__(self, other):
        if self.priority == other.priority:
            return self.id < other.id
        return self.priority < other.priority 

    def __eq__(self, other):
        return self.priority == other.priority and self.id == other.id

    def __hash__(self):
        return hash((self.id, self.priority))
        # return hash((self.id, self.m, self.c, self.d, self.period, self.priority))