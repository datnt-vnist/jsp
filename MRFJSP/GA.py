import numpy as np

def os_mutation(os):
    num_operations = len(os)
    random_index = np.random.randint(num_operations)
    op = os[random_index]
    
    op_indices = np.where(os == op)[0]
    prev_op_index = op_indices[op_indices < random_index][-1] if any(op_indices < random_index) else 0
    next_op_index = op_indices[op_indices > random_index][0] if any(op_indices > random_index) else num_operations - 1

    if prev_op_index == next_op_index or prev_op_index + 1 == next_op_index:
        insert_position = next_op_index
    else:
        insert_position = np.random.randint(prev_op_index + 1, next_op_index)

    os = np.roll(os, shift=insert_position - random_index)
    
    return os


def ma_mutation(ma, wa, pro_time_matrix):
    num_operations = pro_time_matrix.shape[0]
    random_index = np.random.randint(num_operations)
    avail_machines = []
    avail_workers = []

    for m in range(pro_time_matrix.shape[1]):
        for w in range(pro_time_matrix.shape[2]):
            if pro_time_matrix[random_index][m][w] != -1:
                avail_machines.append(m + 1)
                break
    
    random_avail_machine = np.random.choice(avail_machines)

    for w in range(pro_time_matrix.shape[2]):
        if pro_time_matrix[random_index][random_avail_machine - 1][w] != -1:
            avail_workers.append(w + 1)
    
    random_avail_worker = np.random.choice(avail_workers)

    ma[random_index] = random_avail_machine
    wa[random_index] = random_avail_worker

    return ma, wa

def wa_mutation(ma, wa, pro_time_matrix):
    num_operations = pro_time_matrix.shape[0]
    random_index = np.random.randint(num_operations)
    machine = ma[random_index]

    avail_workers = []

    for w in range(pro_time_matrix.shape[2]):
        if pro_time_matrix[random_index][machine - 1][w] != -1:
            avail_workers.append(w + 1)

    random_avail_worker = np.random.choice(avail_workers)

    wa[random_index] = random_avail_worker

    return wa


def pox_crossover(p1, p2, num_jobs):
    job_list = [i + 1 for i in range(num_jobs)]

    random_devide_job_index = np.random.randint(1, num_jobs)
    job_set1 = job_list[:random_devide_job_index]
    job_set2 = job_list[random_devide_job_index:]
    c1 = np.ones(len(p1), dtype=int)*(-1)

    for i, op in enumerate(p1):
        if op in job_set1:
            c1[i] = p1[i]

    for op in p2:
        if op in job_set2 and -1 in c1:
            c1[np.where(c1 == -1)[0][0]] = op

    return c1

def lox_crossover(p1, p2):
    p1 = convert_to_job_operation(p1)
    p2 = convert_to_job_operation(p2)

    size = len(p1)
    idx1, idx2 = sorted(np.random.choice(range(size), 2, replace=False))
    
    c1 = [(-1, -1)] * size


    c1[idx1:idx2] = p1[idx1:idx2]

    for op in p2:
        if op not in c1 and (-1, -1) in c1:
            c1[c1.index((-1, -1))] = op

    c1 = [job_id for job_id, _ in c1]

    return c1

def ipx_crossover(p1_ma, p2_ma, p1_wa, p2_wa):
    binary_vector = np.random.choice([0, 1], len(p1_ma))
    
    c1_ma = np.where(binary_vector, p1_ma, p2_ma)
    c1_wa = np.where(binary_vector, p1_wa, p2_wa)

    return c1_ma, c1_wa


# Helper Functions
def convert_to_job_operation(os):
    op_count = {}
    job_operations = []

    for op in os:
        if op in op_count:
            op_count[op] += 1
        else:
            op_count[op] = 1
        job_operations.append((op, op_count[op]))
    
    return job_operations
    
    
