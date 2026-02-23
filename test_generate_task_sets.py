import numpy as np

from generate_task_sets import generate_task_sets

def test_generate_task_set():
    res = generate_task_sets(10, 0.5)
    assert np.abs(np.sum(res) - 0.5) < 1e-3

def test_generate_task_set_max_tasks():
    res = generate_task_sets(40, 0.5)
    assert np.abs(np.sum(res) - 0.5) < 1e-3

def test_generate_task_set_over_util():
    res = generate_task_sets(40, 1.2)
    assert np.abs(np.sum(res) - 1.2) < 1e-3

