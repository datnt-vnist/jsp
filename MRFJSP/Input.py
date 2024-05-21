import json
import numpy as np

class Input:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = []
        self.num_machines = 0
        self.num_workers = 0
        self.num_operations = 0
        self.num_operations_per_job = []

        self.read_file()

    def read_file(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
        self.data = data['jobs']

        self.num_machines = data['num_machines']
        self.num_workers = data['num_workers']
        self.num_operations = sum(len(job['operations']) for job in self.data)
        self.num_operations_per_job = [len(job['operations']) for job in self.data]
        
    def init_matrix(self):
        matrix = np.ones((self.num_operations, self.num_machines , self.num_workers), dtype=int)*(-1)
        return matrix
    
    def get_matrix(self):
        cost_matrix = self.init_matrix()
        pro_time_matrix = self.init_matrix()
        op_count = 0
        for job in self.data:
            for operation in job['operations']:
                base_process_time = operation['base_process_time']
                for machine in operation['machine_set']:
                    machine_id = machine['id']
                    machine_factor = machine['factor']
                    machine_cost_per_hour = machine['cost_per_hour']
                    for worker in machine['worker_set']:
                        worker_id = worker['id']
                        worker_factor = worker['factor']
                        worker_base_salary = worker['base_salary']
                        process_time = base_process_time * machine_factor * worker_factor
                        cost = process_time * (machine_cost_per_hour + worker_base_salary)
                        cost_matrix[op_count][machine_id-1][worker_id-1] = cost
                        pro_time_matrix[op_count][machine_id-1][worker_id-1] = process_time
                op_count += 1
        
        return cost_matrix, pro_time_matrix, self.num_operations_per_job
