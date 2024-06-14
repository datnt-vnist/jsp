import numpy as np
import pandas as pd

from api.input import Input

class Decode:
    def __init__(
        self, 
        cost_matrix, 
        pro_time_matrix, 
        num_operations_per_cmd, 
        prev_operation_matrix,
        machine_avail_time,
        employee_avail_time
    ):
        self.cost_matrix = cost_matrix
        self.pro_time_matrix = pro_time_matrix
        self.prev_operation_matrix = prev_operation_matrix
        self.num_operations_per_cmd = num_operations_per_cmd
        self.machine_avail_time = machine_avail_time
        self.employee_avail_time = employee_avail_time
        self.num_commands = len(num_operations_per_cmd)
        self.num_operations = cost_matrix.shape[0]
        self.num_machines = cost_matrix.shape[1]
        self.num_employees = cost_matrix.shape[2]
    
    def get_operation_index(self, job_index, op_num):
        return sum(self.num_operations_per_cmd[:job_index - 1]) + op_num -  1

    def decode(self, position):
        op_count = {}
        os = position[0]
        ma = position[1]
        wa = position[2]

        machine_start_time = np.zeros((self.num_machines, self.num_operations), dtype=int)
        machine_end_time = np.zeros((self.num_machines, self.num_operations), dtype=int)
        employee_start_time = np.zeros((self.num_employees, self.num_operations), dtype=int)
        employee_end_time = np.zeros((self.num_employees, self.num_operations), dtype=int)

        for cmd in os:
            if cmd in op_count:
                op_count[cmd] += 1
            else:
                op_count[cmd] = 1
            
            op_order = op_count[cmd]
            op_index = self.get_operation_index(cmd, op_order)
            machine_index = ma[op_index]
            employee_index = wa[op_index]

            prev_ops = self.prev_operation_matrix[op_index]
            pro_time = self.pro_time_matrix[op_index][machine_index][employee_index]

            free_start = 0

            if (self.machine_avail_time[machine_index] > 0):
                free_start = self.machine_avail_time[machine_index]
            if (self.employee_avail_time[employee_index] > 0):
                free_start = max(free_start, self.employee_avail_time[employee_index])

            if prev_ops != None:
                for prev_op in prev_ops:
                    prev_op_index = self.get_operation_index(cmd, prev_op)
                    prev_machine_index = ma[prev_op_index]
                    prev_end_time = machine_end_time[prev_machine_index][prev_op_index]
                    if prev_end_time > free_start:
                        free_start = prev_end_time
            
            order_machine_start_time = np.sort(machine_start_time[machine_index][machine_end_time[machine_index] > 0])
            order_machine_end_time = np.sort(machine_end_time[machine_index][machine_end_time[machine_index] > 0])
            order_employee_start_time = np.sort(employee_start_time[employee_index][employee_end_time[employee_index] > 0])
            order_employee_end_time = np.sort(employee_end_time[employee_index][employee_end_time[employee_index] > 0])

            flag = 0
            for i in range(len(order_machine_start_time)):
                for j in range(len(order_employee_start_time)):
                    if (free_start + pro_time <= order_machine_start_time[i]
                        and free_start + pro_time <= order_employee_start_time[j]):
                        current_start_time = free_start
                        current_end_time = free_start + pro_time
                        flag = 1
                        break
                    
                    max_end_time = max(order_machine_end_time[i], order_employee_end_time[j])
                    if max_end_time >= free_start:
                        free_start = max_end_time
            
            if flag == 0:
                free_start = max(max(machine_end_time[machine_index]), max(employee_end_time[employee_index]), free_start)
                current_start_time = free_start
                current_end_time = free_start + pro_time
            
            if machine_index != 0:
                machine_start_time[machine_index][op_index] = current_start_time
                machine_end_time[machine_index][op_index] = current_end_time
                
            if employee_index != 0:
                employee_start_time[employee_index][op_index] = current_start_time
                employee_end_time[employee_index][op_index] = current_end_time

        makespan = np.max(machine_end_time)

        self.save_schedule(machine_start_time, machine_end_time, position)

        return makespan
    

    def find_employee_by_id(self, employee_id, employees):
        for employee in employees:
            if employee['id'] == employee_id:
                return employee
        return None

    def find_machine_by_id(self, machine_id, machines):
        for machine in machines:
            if machine['id'] == machine_id:
                return machine
        return None
    
    def save_schedule(self, machine_start_time, machine_end_time, schedule):
        input = Input()
        commands, _, employees, machines = input.read_file()

        ma = schedule[1]
        wa = schedule[2]

        df = pd.DataFrame(columns=['command_id', 'command_code', 'operation', 
                                            'employee', 'machine', 'start time', 'end time', 'duration'])

        op_index = 0
        for command in commands:
            for op in range(command['number_of_operations']):
                employee_id = 0
                machine_id = 0
                if wa[op_index] != 0:
                    employee_id = self.find_employee_by_id(wa[op_index], employees)['id']
                if ma[op_index] != 0:
                    machine_id = self.find_machine_by_id(ma[op_index], machines)['id']

                row = [
                    command['id'],
                    command['code'],
                    op + 1,
                    employee_id,
                    machine_id,
                    machine_start_time[ma[op_index]][op_index],
                    machine_end_time[ma[op_index]][op_index],
                    self.pro_time_matrix[op_index][ma[op_index]][wa[op_index]]
                ]

                df.loc[len(df)] = row
                op_index += 1
        
        df.to_csv('schedule_result.csv', index=False)
