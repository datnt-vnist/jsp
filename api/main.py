import numpy as np
import math
import sys

from api.input import Input
from api.encode import Encode
from api.decode import Decode
from api.particle import Particle

class DPSO:
    def __init__(self):
        self.pro_time_matrix = None
        self.cost_matrix = None
        self.num_operations_per_job = None
        self.prev_operation_matrix = None
        self.machine_avail_time = None
        self.employee_avail_time = None

        self.decoder = None
        self.encoder = None

        self.gbest_position = None
        self.gbest_fitness = None

        self.pop_size = 15
        self.pop = []

        self.max_iter = 10
        self.c1 = 0.75
        self.c2 = 0.75
        self.w_start = 0.9 
        self.w_end = 0.4

        self.init_population()

    def init_population(self):
        input = Input()
        self.cost_matrix, self.pro_time_matrix = input.calculate_cost_time_matrix() 
        self.num_operations_per_job = input.calculate_num_operations_per_command()  
        self.prev_operation_matrix = input.get_prev_operation_matrix()
        self.machine_avail_time, self.employee_avail_time = input.get_avail_time()

        self.encoder = Encode(
                            self.cost_matrix,
                            self.pro_time_matrix, 
                            self.num_operations_per_job
                        )
        self.decoder = Decode(self.cost_matrix,
                              self.pro_time_matrix, 
                              self.num_operations_per_job, 
                              self.prev_operation_matrix,
                              self.machine_avail_time,
                              self.employee_avail_time
                            )

        for _ in range(self.pop_size):
            particle = Particle(self.cost_matrix, 
                                self.pro_time_matrix, 
                                self.num_operations_per_job, 
                                self.encoder, 
                                self.decoder
                            )
            self.pop.append(particle)

            if (self.gbest_fitness == None or particle.pbest_fitness < self.gbest_fitness):
                self.gbest_position = np.copy(particle.pbest_position)
                self.gbest_fitness = particle.pbest_fitness
    
    def execute(self):
        for iter in range(self.max_iter):
            w = self.w_start - (self.w_start - self.w_end) * math.tan((iter * math.pi) / (4 * self.max_iter))
            
            for particle in self.pop:
                particle.update_position(self.gbest_position, w, self.c1, self.c2)
                if particle.pbest_fitness < self.gbest_fitness:
                    self.gbest_position = np.copy(particle.pbest_position)
                    self.gbest_fitness = particle.pbest_fitness

            print("Iteration", iter, "Best fitness", self.decoder.decode(self.gbest_position))
        print("Best position", self.gbest_position)

if __name__ == "__main__":
    dpso = DPSO()
    dpso.execute()
