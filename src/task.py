from functools import total_ordering

id = 0

@total_ordering
class Task:
    """Stores information about a task
    
    :param id: unique identifier for a task within a process
    :type id: int

    :param m: number of threads of a task
    :type m: int

    :param c: worst-case execution time of a task
    :type c: int

    :param d: relative deadline of a task
    :type d: int

    :param period: minimum inter-arrival time of a task
    :type period: int

    :param priority: a fixed priority assignment of a task
    :type priority: int

    :param sp: an optional shared priority used by RPS-FP2
    :type sp: int

    :param backup_sp: an optional shared priority assignment that lags sp
    :type backup_sp: int
    """

    def __init__(self, m: int, c: float, d: int, period: int, priority: int):
        """Initialize a task
        
        :param m: number of threads of a task
        :type m: int

        :param c: worst-case execution time of a task
        :type c: int

        :param d: relative deadline of a task
        :type d: int

        :param period: minimum inter-arrival time of a task
        :type period: int

        :param priority: a fixed priority assignment of a task
        :type priority: int
        """

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