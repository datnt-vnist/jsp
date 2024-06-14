import numpy as np
from api.input import Input
from api.decode import Decode

MAX_LOAD = 1e6

class Encode:
    def __init__(self, cost_matrix, pro_time_matrix, num_operations_per_cmd):
        self.cost_matrix = cost_matrix
        self.pro_time_matrix = pro_time_matrix
        self.num_operations_per_cmd = num_operations_per_cmd
        self.num_commands = len(num_operations_per_cmd)
        self.num_operations = cost_matrix.shape[0]
        self.num_machines = cost_matrix.shape[1]
        self.num_employees = cost_matrix.shape[2]
    
    def init_position(self):
        os = self.random_selection()
        ma, wa = self.gso_selection()
        return np.vstack((os, ma, wa))

    def random_selection(self):
        os = []
        for cmd, op in enumerate(self.num_operations_per_cmd):
            for _ in range(op):
                os.append(cmd + 1)
        np.random.shuffle(os)
        return os

    def gso_selection(self):
        ma = np.zeros(self.num_operations, dtype=int)
        wa = np.zeros(self.num_operations, dtype=int)

        command_indices = [i for i in range(self.num_commands)]

        machine_load = np.zeros(self.num_machines, dtype=int)
        employee_load = np.zeros(self.num_employees, dtype=int)

        for _ in range(self.num_commands):
            command_index = np.random.choice(command_indices)
            start_op = sum(self.num_operations_per_cmd[:command_index])
            end_op = start_op + self.num_operations_per_cmd[command_index]
            for op in range(start_op, end_op):
                temp_load = [[MAX_LOAD for _ in range(self.num_employees)] for _ in range(self.num_machines)]
                for m in range(self.num_machines):
                    for e in range(self.num_employees):
                        
                        if self.pro_time_matrix[op, m, e] != -1:
                            temp_load[m][e] = machine_load[m] + employee_load[e] + self.pro_time_matrix[op, m, e]
                        
                temp_load = np.array(temp_load)
                temp_load_min_index = np.unravel_index(np.argmin(temp_load, axis=None), temp_load.shape)
                machine_index = temp_load_min_index[0]
                employee_index = temp_load_min_index[1]
                ma[op] = machine_index
                wa[op] = employee_index
                machine_load[machine_index] += self.pro_time_matrix[op, machine_index, employee_index]
                employee_load[employee_index] += self.pro_time_matrix[op, machine_index, employee_index]

            command_indices.remove(command_index)
        return ma, wa

if __name__ == '__main__':
    input = Input()
    cost_matrix, pro_time_matrix = input.calculate_cost_time_matrix()
    num_operations_per_cmd = input.calculate_num_operations_per_command()
    prev_operation_matrix = input.get_prev_operation_matrix()
    machine_avail_time, employee_avail_time = input.get_avail_time()

    encode = Encode(cost_matrix, pro_time_matrix, num_operations_per_cmd)
    position = encode.init_position()
    print(position)

    decode = Decode(
        cost_matrix, 
        pro_time_matrix, 
        num_operations_per_cmd, 
        prev_operation_matrix, 
        machine_avail_time, 
        employee_avail_time
    )

    makespan = decode.decode(position)

    print(makespan)

