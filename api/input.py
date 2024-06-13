import numpy as np
import math
import json
import math

from datetime import datetime

class Input:
    def __init__(self):    
        self.commands = []
        self.operations = []
        self.employees = []
        self.machines = []

        self.read_file()
    
    def read_json_file(self, file_path):
        with open(file_path, 'r', encoding="utf8") as file:
            data = json.load(file)

        return data

    def read_file(self):
        self.commands = self.read_json_file('request/command.json')
        self.operations = self.read_json_file('request/operation.json')
        self.employees = self.read_json_file('request/employee.json')
        self.machines = self.read_json_file('request/machine.json')

        return self.commands, self.operations, self.employees, self.machines
    
    def init_matrix(self):
        num_operations = len([operation for operation in self.operations if operation['status'] == 1])
        num_machines = len(self.machines)
        num_employees = len(self.employees)
        
        matrix = np.ones((num_operations, num_machines+1, num_employees+1), dtype=float)*(-1)

        return matrix
    
    def round_up_to_nearest_half(self, num):
        return math.ceil(num * 2) / 2

    def calculate_time_difference(self, date_str, hour):
        date = datetime.strptime(date_str, "%Y-%m-%d")

        date = date.replace(hour=hour)

        now = datetime.now()

        difference = date - now

        difference_in_hours = difference.total_seconds() / 3600

        rounded_difference = math.ceil(difference_in_hours * 2) / 2

        return rounded_difference

    def find_operation_list(self, command):
        operation_list = []
        for operation in self.operations:
            if operation['command_id'] == command['id']:
                operation_list.append(operation)
        return operation_list

    def find_employee_list(self, role, min_exp_years):
        employee_list = []
        for employee in self.employees:
            if (employee['role'] == role and
                    employee['years_of_experience'] >= min_exp_years):
                employee_list.append(employee)

        return employee_list

    def find_machine(self, machine_id):
        for machine in self.machines:
            if machine['id'] == machine_id:
                return machine
        return None
        
    
    def calculate_cost_time_matrix(self):
        cost_matrix = self.init_matrix()
        pro_time_matrix = self.init_matrix()

        op_count = 0
        
        for command in self.commands:
            quantity = command['quantity']
            operation_list = self.find_operation_list(command)
            for operation in operation_list:
                if operation['status'] == 1:
                    for machine in operation['machines']:
                        machine_id = 0
                        if (machine['machine'] != None):
                            machine_id = machine['machine']
                        machine_detail = self.find_machine(machine_id)
                        workerRole = machine['workerRole']
                        hour_production = machine['hour_production']
                        min_exp_years = machine['min_exp_years']
                        employee_list = self.find_employee_list(workerRole, min_exp_years)
                        for employee in employee_list:
                            process_time = (quantity / hour_production) * employee['performance_score']
                            if (machine_detail != None):
                                process_time = process_time * machine_detail['efficiency_score']
                            process_time = self.round_up_to_nearest_half(process_time)
                            cost = employee['base_salary'] * process_time
                            if (machine_detail != None):
                                cost = cost + machine_detail['cost_per_hour'] * process_time
                            
                            cost_matrix[op_count, machine_id, employee['id']] = cost
                            pro_time_matrix[op_count, machine_id, employee['id']] = process_time
                    op_count += 1
        
        return cost_matrix, pro_time_matrix 
                    
    def calculate_num_operations_per_command(self):
        num_operations_per_cmd = []
        for command in self.commands:
            num_operations_per_cmd.append(command['number_of_operations'])
            
        return num_operations_per_cmd

    def get_prev_operation_matrix(self):
        prev_operation_matrix = []
        for operation in self.operations:
            prev_operation_matrix.append(operation['prev_operation'])
        
        return prev_operation_matrix

    def get_avail_time(self):
        num_machines = len(self.machines)
        num_employees = len(self.employees)

        machine_avail_time = np.zeros(num_machines+1, dtype=float)
        employee_avail_time = np.zeros(num_employees+1, dtype=float)

        for operation in self.operations:
            if operation['status'] == 2:
                machine_id = operation['assigned_machine']
                employee_id = operation['assigned_worker']
                if machine_id != None:
                    machine_avail_time[machine_id] += self.calculate_time_difference(operation['start_date'], operation['start_hour'])

                if employee_id != None:
                    employee_avail_time[employee_id] += self.calculate_time_difference(operation['start_date'], operation['start_hour'])

        
        return machine_avail_time, employee_avail_time

    def test(self):
        # cost_matrix, pro_time_matrix = self.calculate_cost_time_matrix()
        get_avail_time = self.get_avail_time()
        print(get_avail_time)
        pass

if __name__ == '__main__':
    input = Input()
    input.test()
