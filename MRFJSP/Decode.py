import numpy as np
from matplotlib import pyplot as plt

class Decode:
    def __init__(self, cost_matrix, pro_time_matrix, num_operations_per_job):
        self.cost_matrix = cost_matrix
        self.pro_time_matrix = pro_time_matrix
        self.num_operations_per_job = num_operations_per_job
        self.num_jobs = len(num_operations_per_job)
        self.num_operations = cost_matrix.shape[0]
        self.num_machines = cost_matrix.shape[1]
        self.num_workers = cost_matrix.shape[2]

    def get_operation_index(self, job_index, op_num):
        return sum(self.num_operations_per_job[:job_index - 1]) + op_num -  1

    def decode(self, position, plot=False):
        op_count = {}
        os = position[0]
        ma = position[1]
        wa = position[2]

        ma_matrix = np.zeros((self.num_jobs, np.max(self.num_operations_per_job)), dtype=int)
        wa_matrix = np.zeros((self.num_jobs, np.max(self.num_operations_per_job)), dtype=int)
        count = 0
        for i in range(self.num_jobs):
            for j in range(self.num_operations_per_job[i]):
                ma_matrix[i][j] = ma[count]
                wa_matrix[i][j] = wa[count]
                count += 1

        machine_start_time = np.zeros((self.num_machines, self.num_operations), dtype=int)
        machine_end_time = np.zeros((self.num_machines, self.num_operations), dtype=int)
        worker_start_time = np.zeros((self.num_workers, self.num_operations), dtype=int)
        worker_end_time = np.zeros((self.num_workers, self.num_operations), dtype=int)
        machine_op_count = np.zeros(self.num_machines, dtype=int)
        worker_op_count = np.zeros(self.num_workers, dtype=int)
        total_cost = 0

        for op in os:
            if op in op_count:
                op_count[op] += 1
            else:
                op_count[op] = 1
            
            op_num = op_count[op]
            op_index = self.get_operation_index(op, op_num)
            machine_index = ma_matrix[op-1][op_num-1] - 1
            worker_index = wa_matrix[op-1][op_num-1] - 1
            prev_op_index = self.get_operation_index(op, op_num - 1)
            prev_machine_index = ma_matrix[op-1][op_num-2] - 1

            pro_time = self.pro_time_matrix[op_index][machine_index][worker_index]
            total_cost += self.cost_matrix[op_index][machine_index][worker_index]
            
            if machine_op_count[machine_index] == 0 and worker_op_count[worker_index] == 0:
                if op_num == 1:
                    current_start_time = 0
                    current_end_time = pro_time
                else:
                    prev_end_time = machine_end_time[prev_machine_index][prev_op_index]
                    current_start_time = prev_end_time
                    current_end_time = prev_end_time + pro_time
            else:
                flag = 0
                prev_end_time = 0

                if op_num == 1:
                    free_start = 0
                else:
                    prev_end_time = machine_end_time[prev_machine_index][prev_op_index]
                    free_start = prev_end_time

                order_machine_start_time = np.sort(machine_start_time[machine_index][machine_end_time[machine_index] > 0])
                order_machine_end_time = np.sort(machine_end_time[machine_index][machine_end_time[machine_index] > 0])
                order_worker_start_time = np.sort(worker_start_time[worker_index][worker_end_time[worker_index] > 0])
                order_worker_end_time = np.sort(worker_end_time[worker_index][worker_end_time[worker_index] > 0])

                for i in range(len(order_machine_start_time)):
                    for j in range(len(order_worker_start_time)):
                        if free_start + pro_time <= order_machine_start_time[i] and free_start + pro_time <= order_worker_start_time[j]:
                            current_start_time = free_start
                            current_end_time = free_start + pro_time
                            flag = 1
                            break

                        if max(order_machine_end_time[i], order_worker_end_time[j]) >= free_start:
                            free_start = max(order_machine_end_time[i], order_worker_end_time[j])
                
                if flag == 0:
                    free_start = max(max(machine_end_time[machine_index]), max(worker_end_time[worker_index]), prev_end_time)
                    current_start_time = free_start
                    current_end_time = free_start + pro_time

            machine_start_time[machine_index][op_index] = current_start_time
            machine_end_time[machine_index][op_index] = current_end_time
            worker_start_time[worker_index][op_index] = current_start_time
            worker_end_time[worker_index][op_index] = current_end_time

            machine_op_count[machine_index] += 1
            worker_op_count[worker_index] += 1
        
        makespan = np.max(machine_end_time)

        if (plot):
            pass
        
        return makespan
        
    # Result visualization              
    def find_job_operation(self, operation_index):
        job_op_list = [
            (i + 1, j + 1) for i in range( self.num_jobs ) for j in range(self.num_operations_per_job[i])
        ]
        job_op = job_op_list[operation_index]
        return job_op
         
    def draw_gantt(self, start_time, end_time, resource):
        colors = {
            0: 'green', 1:'red', 2:'blue', 3:'yellow', 4:'orange', 5:'palegoldenrod', 6:'purple'
        }

        fig = plt.figure()

        ax = fig.add_subplot(1, 1, 1)

        num_resource = resource == 'machine' and self.num_machines or self.num_workers

        for i in range(num_resource):
            for j in range(self.num_operations):
                current_start_time = start_time[i][j]
                current_end_time = end_time[i][j]
                current_diference_time = current_end_time - current_start_time
                if end_time[i][j] != 0 and end_time[i][j] - start_time[i][j] != 0:
                    operation = self.find_job_operation(j)
                    bar_width = current_diference_time
                    bar_left = current_start_time
                    bar_color = colors[operation[0] - 1]

                    ax.barh(y=i, width=bar_width, height=1, left=bar_left, color=bar_color, edgecolor='black')
                    ax.text(x=bar_left + 0.1, y=i, s=str(operation), fontsize=8)
                else:
                    ax.barh(y=i, width=0, height=1, left=0, color="black", edgecolor='black')

        ax.set_xlabel('Time')
        ax.set_yticks(np.arange(0, num_resource, 1))
        ax.set_ylabel(resource)

        plt.show()

