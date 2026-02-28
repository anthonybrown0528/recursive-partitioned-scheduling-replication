from recursive_gang_scheduler import recursive_gang_schedule
from recursive_gang_scheduler import Task

def test_valid_schedule():
    t1 = Task(2, 1, 2, 5)
    t2 = Task(5, 1, 1, 1)
    t3 = Task(2, 1, 1, 1)
    t4 = Task(3, 1, 2, 5)
    t5 = Task(1, 1, 1, 1)

    schedulable, forest = recursive_gang_schedule([t2], 5)
    assert schedulable