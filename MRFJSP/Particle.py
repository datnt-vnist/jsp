import numpy as np
import GA

class Particle: 
    def __init__(self, cost_matrix, pro_time_matrix, num_operations_per_job, encoder, decoder):
        self.encoder = encoder
        self.decoder = decoder
        self.cost_matrix = cost_matrix
        self.pro_time_matrix = pro_time_matrix

        self.num_jobs = len(num_operations_per_job)
        self.num_operations = cost_matrix.shape[0]
        self.num_machines = cost_matrix.shape[1]
        self.num_workers = cost_matrix.shape[2]

        self.position = None
        self.pbest_position = None
        self.pbest_fitness = None

        self.init_position()

    def init_position(self):
        self.position = self.encoder.init_position()
        self.pbest_position = self.position
        self.pbest_fitness = self.decoder.decode(self.position)

    def update_position(self, gbest_position, w, c1, c2):
        r1 = np.random.random()
        r2 = np.random.uniform(0.6, 0.9)
        r3 = np.random.uniform(0.6, 0.9)

        if (r1 < w):
            self.position[0] = GA.os_mutation(self.position[0])
            self.position[1], self.position[2] = GA.ma_mutation(self.position[1], self.position[2], self.pro_time_matrix)
            self.position[2] = GA.wa_mutation(self.position[1], self.position[2], self.pro_time_matrix)
        
        if (r2 < c1):
            self.position[0] = GA.pox_crossover(self.position[0], self.pbest_position[0], self.num_jobs)
            self.position[1], self.position[2] = GA.ipx_crossover(self.position[1], self.pbest_position[1], self.position[2], self.pbest_position[2])
        
        if (r3 < c2):
            self.position[0] = GA.lox_crossover(self.position[0], gbest_position[0])
            self.position[1], self.position[2] = GA.ipx_crossover(self.position[1], gbest_position[1], self.position[2], gbest_position[2])
        
        fitness = self.decoder.decode(self.position)
    
        if fitness < self.pbest_fitness:
            self.pbest_position = np.copy(self.position)
            self.pbest_fitness = fitness
