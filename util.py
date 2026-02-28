import queue
import math

from task import Task

def compute_dhp(task: Task) -> set:
    partitions = task.partitions
    dhp_task_set = set()
    for part in partitions:
        tasklist = part.greater_priority(task)
        dhp_task_set = dhp_task_set.union(tasklist)
    return dhp_task_set

def compute_ihp(dhp: set) -> set:
    q = queue.Queue()
    found = set()

    ihp = set()
    for t in dhp:
        q.put(t)
        found.add(t)
    while not q.empty():
        e = q.get()
        dhp_e = compute_dhp(e)

        for te in dhp_e:
            if te not in found:
                q.put(te)
                found.add(te)
        if e not in dhp:
            ihp.add(e)
    return ihp

def compute_dhp_noci(dhp: set) -> set:
    dhp_noci = set()

    for t in dhp:
        dhp_t = compute_dhp(t)
        ihp_t = compute_ihp(dhp_t)

        if dhp_t.issubset(dhp) and len(ihp_t) == 0:
            dhp_noci.union(dhp_t)
            dhp_noci.add(t)
    return dhp_noci

def compute_response_time_bound(task: Task, dhp: set, dhp_noci: set, response_map: dict):
    rr = task.c
    interference = 0

    for t in dhp:
        term = 0
        if t in dhp_noci:
            term = math.ceil(rr / t.period) * t.c
        else:
            if t not in response_map:
                dhp_t = compute_dhp(t)
                dhp_noci_t = compute_dhp_noci(dhp_t)
                compute_response_time_bound(t, dhp_t, dhp_noci_t, response_map)

            term = math.ceil((rr + response_map[t] - t.c) / t.period) * t.c
        interference = interference + term
    rl = task.c + interference

    while rl != rr and rl <= task.d:
        rr = rl
        interference = 0

        for t in dhp:
            term = 0
            if t in dhp_noci:
                term = math.ceil(rr / t.period) * t.c
            else:
                if t not in response_map:
                    dhp_t = compute_dhp(t)
                    dhp_noci_t = compute_dhp_noci(dhp_t)
                    compute_response_time_bound(t, dhp_t, dhp_noci_t, response_map)

                term = math.ceil((rr + response_map[t] - t.c) / t.period) * t.c
            interference = interference + term
        rl = task.c + interference
    response_map[task] = rl 

def is_schedulable(taskset: list[Task]) -> bool:

    response_map = {}
    for t in taskset:
        dhp = compute_dhp(t)
        dhp_noci = compute_dhp_noci(dhp)

        compute_response_time_bound(t, dhp, dhp_noci, response_map)
        if response_map[t] > t.d:
            return False
    return True