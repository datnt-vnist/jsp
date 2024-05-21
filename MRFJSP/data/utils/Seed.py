import os
import sys
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import json
from data.utils.Input import Input

class Seed:
    def __init__(self, file_in, file_out):
        self.file_in = file_in
        self.file_out = file_out
        self.input = Input(file_in)

    def get_operation_index(self, num_operations_per_job, job_index, op_num):
        return sum(num_operations_per_job[:job_index - 1]) + op_num -  1
    
    def random_salary(self, worker_num):
        array = [random.randint(15, 30) for _ in range(worker_num)]
        array.sort(reverse=True)

        return array

    def random_cost(self, machine_num):
        array = [random.randint(10, 15) for _ in range(machine_num)]
        array.sort(reverse=True)

        return array
    
    def run(self):
        p_table, num_operations_per_job = self.input.getMatrix()
        num_machines = p_table.shape[1]
        num_workers = num_machines
        num_jobs = len(num_operations_per_job)

        salary_array = self.random_salary(num_workers)
        cost_array = self.random_cost(num_machines)

        job_indexes = []
        for jb, op in enumerate(num_operations_per_job):
            for _ in range(op):
                job_indexes.append(jb + 1)
        
        jobs = []
        for i in range(1, num_jobs + 1):
            operations = []
            for j in range(num_operations_per_job[i - 1]): # each operation of job i
                machines = []
                op_index = self.get_operation_index(num_operations_per_job, i, j + 1)
                base_process_time = 9
                for k in range(p_table.shape[1]): # each machine
                    workers = []
                    process_time = p_table[op_index][k]
                    machine_factor = random.uniform(1, 1.5)
                    if (process_time != -1):
                        for l in range(num_workers):
                            worker = {
                                "id": l + 1,
                                "factor": float((process_time / base_process_time) / machine_factor),
                                "base_salary": int(salary_array[l])
                            }
                            workers.append(worker)
                        machine = {
                            "id": k + 1,
                            "factor": float( machine_factor),
                            "cost_per_hour": int(cost_array[k]),
                            "workers": workers
                        }                
                        machines.append(machine)
                operations.append({
                    "id": j + 1,
                    "base_process_time": int(base_process_time),
                    "prev_operation": None if j == 0 else j,
                    "next_operation": None if j == num_operations_per_job[i - 1] - 1 else j + 2,
                    "machine_set": machines,
                })
            jobs.append({
                "job": i,
                "operations": operations
            })
    
        data = {
            "num_machines": num_machines,
            "num_workers": num_workers,
            "jobs": jobs
        }

        with open(self.file_out, 'w') as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    file_in = "data/raw_data/" + sys.argv[1]
    file_out = "data/output/" + sys.argv[2]
    seed = Seed(file_in, "data/output/data_1.json")
    seed.run()
            
    

    