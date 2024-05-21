import numpy as np
import pyswarms as ps
from CustomBPSO import CustomBPSO
from Input import Input

input = Input('data/kc1.fjs')
jobs = input.getMatrix()

num_jobs = len(jobs)
num_machines = 5
num_operations = sum(len(job) for job in jobs)
num_op_per_job = [len(job) for job in jobs]
n_particles = 30

def convert_jobs():
    process_times = np.ones((num_operations, num_machines), dtype=int)*(-1)
    operation_index = 0
    for job in jobs:
        for op in job:
            for pro_time, machine_id in op:
                process_times[operation_index][machine_id - 1] = pro_time
            operation_index += 1
    return process_times

def find_one_operation_in_a_machine(i, j):
    if i == 1:
        op_index = j - 1
    else:
        op_index = sum(num_op_per_job[:i - 1]) + j - 1

    return op_index

def decode(scheduling, process_times):
    machines_matrix = np.zeros((num_jobs, num_operations), dtype=int)
    times_matrix    = np.zeros((num_jobs, num_operations), dtype=int)

    operations_scheduling = scheduling[:num_operations]
    machines_scheduling   = scheduling[num_operations:]

    operation_index = 0
    for i in range( num_jobs ):
        for j in range( num_op_per_job[i] ):
            count = 0
            process_time = process_times[operation_index]

            for index in range( len(process_time) ):
                if process_time[index] != -1:
                    count+=1

                if count == machines_scheduling[operation_index]:
                    machines_matrix[i][j] = index+1
                    times_matrix[i][j]  = process_time[index]
                    break

            operation_index+=1

    start_time = np.zeros(
        (num_machines, num_operations),
        dtype=int
    )

    end_time = np.zeros(
        (num_machines, num_operations),
        dtype=int
    )

    op_count_dict = {}
    machine_operations = np.zeros(num_machines, dtype=int)

    for os in operations_scheduling:
        if os in op_count_dict:
            op_count_dict[os] += 1
        else:
            op_count_dict[os] = 1

        operation_count = op_count_dict[os]
        operation_index = find_one_operation_in_a_machine(os, operation_count)

        machine_number     = machines_matrix[os-1][operation_count-1]
        pro_time           = times_matrix [os-1][operation_count-1]

        machine_operation  = machine_operations[machine_number-1]
        current_start_time = start_time[machine_number-1][operation_index]
        current_end_time   = end_time  [machine_number-1][operation_index]

        previous_operation_index = find_one_operation_in_a_machine(os, operation_count - 1)
        previous_machine_number = machines_matrix[os-1][operation_count-2]

        if machine_operation == 0 and operation_count == 1 :
            current_start_time = 0
            current_end_time   = pro_time

        elif machine_operation == 0 and operation_count > 1 :
            prev_m_num          = machines_matrix[os-1][operation_count-2]
            prev_end_time       = end_time[prev_m_num-1][previous_operation_index]
            current_start_time  = prev_end_time
            current_end_time    = prev_end_time + pro_time

        elif machine_operation > 0:
            flag=0
            prev_end_time = 0

            if operation_count == 1 :
                free_start = 0
            else:
                prev_end_time = end_time[previous_machine_number-1][previous_operation_index]
                free_start = prev_end_time

            order_start_time = np.sort(start_time[machine_number-1][end_time[machine_number-1] > 0])
            order_end_time   = np.sort(end_time  [machine_number-1][end_time[machine_number-1] > 0])

            for index in range(len(order_start_time)):
                if order_start_time[index] - free_start >= pro_time:
                    current_start_time = free_start
                    current_end_time   = free_start + pro_time
                    flag = 1
                    break

                if order_end_time[index] - free_start >= 0:
                    free_start = order_end_time[index]

            if flag == 0:
                free_start = max(np.max(end_time[machine_number-1]), prev_end_time)
                current_start_time = free_start
                current_end_time   = free_start + pro_time

        machine_operation += 1

        machine_operations[machine_number - 1]          = machine_operation
        start_time[machine_number - 1][operation_index] = current_start_time
        end_time  [machine_number - 1][operation_index] = current_end_time

    fitness = np.max(end_time)

    return fitness

    
def makespan_function(schedule):
    schedule_matrix = np.array(schedule).reshape((num_machines, num_operations))
    process_times = convert_jobs()
    os = []
    ma = []

    for jb, op in enumerate(num_op_per_job):
        for _ in range(op):
            os.append(jb+1) 

    for i in range(num_operations):
        for j in range(num_machines):
            if schedule_matrix[j, i] == 1:
                ma.append(j+1)
    makespan = decode(os + ma, process_times)

    return makespan
    
def f(x):
    n_particles = x.shape[0]
    j = [makespan_function(x[i]) for i in range(n_particles)]
    return np.array(j)

def init_pos():
    pos = np.zeros((n_particles, num_machines, num_operations), dtype=int)
    for i in range(n_particles):
        for j in range(num_operations):
            random_index = np.random.randint(num_machines)
            pos[i, random_index, j] = 1
    return pos.reshape(n_particles, num_machines*num_operations)

options = {'c1': 0.5, 'c2': 0.3, 'w': 0.9, 'k': 30, 'p': 2}
dimensions = num_machines * num_operations

init_pos = init_pos()
optimizer = CustomBPSO(n_particles=n_particles, dimensions=dimensions, options=options, init_pos=init_pos, input_shape=(num_machines, num_operations))
cost, pos = optimizer.optimize(f, iters=1000)
