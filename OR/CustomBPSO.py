import pyswarms as ps
import numpy as np
import logging
import multiprocessing as mp
from collections import deque
from pyswarms.backend.operators import compute_objective_function, compute_pbest

class CustomBPSO(ps.discrete.BinaryPSO):
    def __init__(self, n_particles, dimensions, options, init_pos, input_shape):
        super().__init__(n_particles, dimensions, options, init_pos)
        self.input_shape = input_shape

    def optimize(
        self, objective_func, iters, n_processes=None, verbose=True, **kwargs
    ):

        if verbose:
            log_level = logging.INFO
        else:
            log_level = logging.NOTSET

        self.rep.log("Obj. func. args: {}".format(kwargs), lvl=logging.DEBUG)
        self.rep.log(
            "Optimize for {} iters with {}".format(iters, self.options),
            lvl=log_level,
        )
        # Populate memory of the handlers
        self.vh.memory = self.swarm.position

        # Setup Pool of processes for parallel evaluation
        pool = None if n_processes is None else mp.Pool(n_processes)

        self.swarm.pbest_cost = np.full(self.swarm_size[0], np.inf)
        ftol_history = deque(maxlen=self.ftol_iter)
        for i in self.rep.pbar(iters, self.name) if verbose else range(iters):
            # Compute cost for current position and personal best
            self.swarm.current_cost = compute_objective_function(
                self.swarm, objective_func, pool, **kwargs
            )
            self.swarm.pbest_pos, self.swarm.pbest_cost = compute_pbest(
                self.swarm
            )
            best_cost_yet_found = np.min(self.swarm.best_cost)
            # Update gbest from neighborhood
            self.swarm.best_pos, self.swarm.best_cost = self.top.compute_gbest(
                self.swarm, p=self.p, k=self.k
            )
            if verbose:
                # Print to console
                self.rep.hook(best_cost=self.swarm.best_cost)
            # Save to history
            hist = self.ToHistory(
                best_cost=self.swarm.best_cost,
                mean_pbest_cost=np.mean(self.swarm.pbest_cost),
                mean_neighbor_cost=np.mean(self.swarm.best_cost),
                position=self.swarm.position,
                velocity=self.swarm.velocity,
            )
            self._populate_history(hist)
            # Verify stop criteria based on the relative acceptable cost ftol
            relative_measure = self.ftol * (1 + np.abs(best_cost_yet_found))
            delta = (
                np.abs(self.swarm.best_cost - best_cost_yet_found)
                < relative_measure
            )
            if i < self.ftol_iter:
                ftol_history.append(delta)
            else:
                ftol_history.append(delta)
                if all(ftol_history):
                    break
            # Perform position velocity update
            self.swarm.velocity = self.top.compute_velocity(
                self.swarm, self.velocity_clamp, self.vh
            )
            self.swarm.position = self.custom_compute_update(self.swarm)
        # Obtain the final best_cost and the final best_position
        final_best_cost = self.swarm.best_cost.copy()
        final_best_pos = self.swarm.pbest_pos[
            self.swarm.pbest_cost.argmin()
        ].copy()
        self.rep.log(
            "Optimization finished | best cost: {}, best pos: {}".format(
                final_best_cost, final_best_pos
            ),
            lvl=log_level,
        )
        # Close Pool of Processes
        if n_processes is not None:
            pool.close()

        return (final_best_cost, final_best_pos)
    
    def custom_compute_update(self, swarm):
        X = np.zeros((self.n_particles, *self.input_shape), dtype=int)

        for i in range(self.n_particles):
            reshaped_velocity = swarm.velocity[i].reshape(self.input_shape)

            # Apply the sigmoid function to get values between 0 and 1
            S = 1 / (1 + np.exp(-reshaped_velocity))

            # For each column, find the index of the maximum value
            max_indices = np.argmax(S, axis=0)

            # Set the maximum value in each column to 1
            X[i, max_indices, np.arange(S.shape[1])] = 1

        X = X.reshape(swarm.velocity.shape)

        return X
