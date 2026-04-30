from recursive_gang_scheduler import recursive_gang_schedule
from recursive_gang_scheduler import Task

import pickle

def test_valid_schedule():
    t1 = Task(2, 1, 2, 5, 2)
    t2 = Task(5, 1, 5, 5, 5)
    t3 = Task(2, 1, 1, 1, 1)
    t4 = Task(3, 1, 2, 5, 2)
    t5 = Task(1, 1, 1, 1, 1)

    schedulable, forest = recursive_gang_schedule([t2, t4], 5)
    assert schedulable

def test_known_partition():
    t1 = Task(2, 2, 10, 10, 10)
    t2 = Task(5, 8, 20, 20, 20)
    t3 = Task(2, 21, 70, 70, 70)
    t4 = Task(3, 16, 80, 80, 80)
    t5 = Task(1, 20, 55, 55, 55)

    schedulable, forest = recursive_gang_schedule([t1, t2, t3, t4, t5], 5)
    assert schedulable

    assert len(forest.leaves()) == 3

def test_8407():
    obj = None
    with open('dump.pkl', 'rb') as file:
        obj = pickle.load(file)
        obj = pickle.loads(obj)
    recursive_gang_schedule(obj, 8)


def test_12127():
    obj = None
    with open('dump1.pkl', 'rb') as file:
        obj = pickle.load(file)
        obj = pickle.loads(obj)
    recursive_gang_schedule(obj, 8)


def test_9271():
    obj = None
    with open('dump2.pkl', 'rb') as file:
        obj = pickle.load(file)
        obj = pickle.loads(obj)
    recursive_gang_schedule(obj, 8)


def test_9271_rounded():
    obj = None
    with open('dump3.pkl', 'rb') as file:
        obj = pickle.load(file)
        obj = pickle.loads(obj)
    recursive_gang_schedule(obj, 8)


def test_8063():
    obj = None
    with open('dump4.pkl', 'rb') as file:
        obj = pickle.load(file)
        obj = pickle.loads(obj)
    recursive_gang_schedule(obj, 8)


def test_28991():
    obj = None
    with open('dump5.pkl', 'rb') as file:
        obj = pickle.load(file)
        obj = pickle.loads(obj)
    recursive_gang_schedule(obj, 8)

def test_00015():
    obj = None
    with open('dump7.pkl', 'rb') as file:
        obj = pickle.load(file)
        obj = pickle.loads(obj)
    recursive_gang_schedule(obj, 8)

def test_00015():
    obj = None
    with open('dumpsomething.pkl', 'rb') as file:
        obj = pickle.load(file)
        # obj = pickle.loads(obj)
    recursive_gang_schedule(obj[0], obj[1])