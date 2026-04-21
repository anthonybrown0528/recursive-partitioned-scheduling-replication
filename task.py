from functools import total_ordering

id = 0

@total_ordering
class Task:
    def __init__(self, m: int, c: float, d: int, period: int, priority: int):
        global id

        self.id = id
        id = id + 1

        # Task parallelism
        self.m = m

        self.c = c
        self.d = d
        self.period = period

        self.priority = priority

        self.sp = None
        self.backup_sp = None

    def __lt__(self, other):

        # Shared Priority takes precedence if defined
        if self.sp is not None and other.sp is not None and self.sp != other.sp:
            return self.sp < other.sp
        if self.sp is not None and other.sp is None:
            return True
        if self.sp is None and other.sp is not None:
            return False        

        if self.priority == other.priority:
            return self.id < other.id
        return self.priority < other.priority 

    def __eq__(self, other):
        return self.priority == other.priority and self.id == other.id

    def __hash__(self):
        return hash((self.id, self.priority))
        # return hash((self.id, self.m, self.c, self.d, self.period, self.priority))