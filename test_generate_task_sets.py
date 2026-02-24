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
    assert res.shape == (40, )
    assert np.abs(np.sum(res) - 1.2) < 1e-3

def test_non_zero_utils():
    for _ in range(8_000):
        res = generate_task_sets(8, 0.8)
        assert np.abs(np.sum(res) - 0.8) < 1e-3
        assert np.min(res) > 0