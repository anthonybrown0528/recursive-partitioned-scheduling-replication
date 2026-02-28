from functools import total_ordering

@total_ordering
class Task:
    def __init__(self, m: int, c: float, d: int, period: int, priority: int):
        self.partitions = []

        # Task parallelism
        self.m = m

        self.c = c
        self.d = d
        self.period = period

        self.priority = priority

    def __lt__(self, other):
        self.priority < other.priority

    def __eq__(self, other):
        if not isinstance(other, Task):
            return False
        return (self.m, self.c, self.d, self.period, self.priority) == (other.m, other.c, other.d, other.period, other.priority)

    def __hash__(self):
        return hash((self.m, self.c, self.d, self.period, self.priority))