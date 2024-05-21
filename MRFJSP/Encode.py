import numpy as np

from Input import Input

class Encode:
    def __init__(self, cost_matrix, pro_time_matrix, num_operations_per_job):
        self.cost_matrix = cost_matrix
        self.pro_time_matrix = pro_time_matrix
        self.num_operations_per_job = num_operations_per_job
        self.num_jobs = len(num_operations_per_job)
        self.num_operations = cost_matrix.shape[0]
        self.num_machines = cost_matrix.shape[1]
        self.num_workers = cost_matrix.shape[2]

    def init_position(self):
        os = self.random_selection()
        ma, wa = self.gso_selection()
        return np.vstack((os, ma, wa))
    
    def random_selection(self):
        os = []
        for jb, op in enumerate(self.num_operations_per_job):
            for _ in range(op):
                os.append(jb + 1)
        np.random.shuffle(os)
        return os

    def gso_selection(self):
        ma = np.zeros(self.num_operations, dtype=int)
        wa = np.zeros(self.num_operations, dtype=int)

        job_list = [i for i in range(self.num_jobs)]
        
        machine_load = np.zeros(self.num_machines, dtype=int)
        worker_load = np.zeros(self.num_workers, dtype=int)

        for _ in range(self.num_jobs):
            job_num = np.random.choice(job_list)
            start_op = sum(self.num_operations_per_job[:job_num])
            end_op = start_op + self.num_operations_per_job[job_num]
            for op in range(start_op, end_op):
                temp_load = [[999 for _ in range(self.num_workers)] for _ in range(self.num_machines)]
                for m in range(self.num_machines):
                    for w in range(self.num_workers):
                        if self.pro_time_matrix[op][m][w] != -1:
                            if (temp_load[m][w] == 999):
                                temp_load[m][w] = 0
                            temp_load[m][w] = machine_load[m] + worker_load[w] + self.pro_time_matrix[op][m][w] 
                temp_load = np.array(temp_load)
                temp_load_min_index = np.unravel_index(np.argmin(temp_load, axis=None), temp_load.shape)
                machine_index = temp_load_min_index[0]
                worker_index = temp_load_min_index[1]
                ma[op] = machine_index + 1
                wa[op] = worker_index + 1
                machine_load[machine_index] += self.pro_time_matrix[op][machine_index][worker_index]
                worker_load[worker_index] += self.pro_time_matrix[op][machine_index][worker_index]
            job_list.remove(job_num)
        return ma, wa



