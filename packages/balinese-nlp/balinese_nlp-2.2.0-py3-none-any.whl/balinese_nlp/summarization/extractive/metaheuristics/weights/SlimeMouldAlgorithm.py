from .BaseMetaSummarizerWeights import BaseMetaSummarizerWeights
import random as rd
import numpy as np
import math


class SlimeMouldAlgorithm(BaseMetaSummarizerWeights):
    def __init__(self,
                 N_SLIMES=55,
                 MAX_ITERATIONS=100,
                 MAX_KONVERGEN=10,
                 Z_VALUE=0.67,
                 OPTIMIZER_NAME='Slime Mould Algorithm',
                 FUNCTIONS={
                     'n_features': 2,
                     'compression_rate': 0.57,  # must be 0.5 <= comp_rate <= 1
                     'objective': 'max',
                     # metrics for evaluating each agent fitness {accuracy, fleiss, krippendorff}
                     'metric': 'accuracy'
                 },
                 BREAK_IF_CONVERGENCE=True
                 ):
        super().__init__(
            N_AGENTS=N_SLIMES,
            MAX_ITERATIONS=MAX_ITERATIONS,
            MAX_KONVERGEN=MAX_KONVERGEN,
            FUNCTIONS=FUNCTIONS,
            BREAK_IF_CONVERGENCE=BREAK_IF_CONVERGENCE,
        )
        self.optimizer['name'] = OPTIMIZER_NAME
        self.optimizer['params'].update({
            'Z_VALUE': Z_VALUE
        })

    def solve(self):
        """
        Menjalankan proses optimasi Slime Mould Algorithm (SMA).
        """
        if not self.IS_FIT:
            raise ValueError(
                'Please fit your data first through fit() method!')

        MAX_ITERATIONS = self.optimizer['params']['MAX_ITERATIONS']
        N_SLIMES = self.optimizer['params']['N_AGENTS']
        OBJECTIVE = self.optimizer['params']['FUNCTIONS']['objective']

        # 1. Initialize agents
        agents = self._initialize_agents()

        # 2. Evaluate fitness and select the best and worst agents
        agents = self._evaluate_fitness(agents)
        best_agent = self._retrieve_best_agent(agents)
        worst_agent = self._retrieve_worst_agent(agents)
        best_fitness_previous = best_agent['fitness']
        self.LIST_BEST_FITNESS.append(best_agent['fitness'])

        # 3. Optimization process
        convergence = 0
        for idx_iteration in range(MAX_ITERATIONS):

            # Calculate the weights vector for each agent
            weights_vector = self.__calculate_weights_vector(
                agents, best_agent, worst_agent)

            # Update slime mould positions
            agents = self.__update_slime_position(
                agents, weights_vector, best_agent, idx_iteration)

            # adjust boundaries
            agents = self._adjust_boundaries(agents)

            # Evaluate fitness of the new positions
            agents = self._evaluate_fitness(agents)

            # Retrieve new best and worst agents
            best_agent_current = self._retrieve_best_agent(agents)
            worst_agent_current = self._retrieve_worst_agent(agents)

            # elitism
            if OBJECTIVE == 'max':
                if best_agent_current['fitness'] > best_agent['fitness']:
                    best_agent = best_agent_current.copy()
                if worst_agent_current['fitness'] < worst_agent['fitness']:
                    worst_agent = worst_agent_current.copy()

            # Check for convergence
            self.LIST_BEST_FITNESS.append(best_agent['fitness'])
            is_break, best_fitness_previous, convergence = self._check_convergence(
                best_agent['fitness'], best_fitness_previous, convergence, idx_iteration)

            if is_break and self.BREAK_IF_CONVERGENCE:
                break

        self._IS_SOLVE = True
        return best_agent

    def __calculate_weights_vector(self, agents, best_agent, worst_agent):
        """
        Menghitung vector bobot untuk setiap agen berdasarkan paper asli SMA.
        """
        # Sort slime moulds based on their fitness values
        isDescendingOrder = True
        OBJECTIVE = self.optimizer['params']['FUNCTIONS']['objective']
        if OBJECTIVE == 'min':
            isDescendingOrder = False

        # Create a list of tuples (agent, fitness) for sorting
        slime_moulds_with_fitness = [
            (agent, agent['fitness']) for agent in agents]
        slime_moulds_with_fitness.sort(
            key=lambda x: x[1], reverse=isDescendingOrder)
        sortedFitnessScores = [fitness for _,
                               fitness in slime_moulds_with_fitness]

        weights_vector = []
        best_fitness = best_agent['fitness']
        worst_fitness = worst_agent['fitness']
        N_AGENTS = self.optimizer['params']['N_AGENTS']

        denominator = best_fitness - worst_fitness + np.finfo(float).eps

        # Calculate weights based on formula
        for idx_agent, fitness_score in enumerate(sortedFitnessScores):

            # Handle logarithm input constraint
            inside_log = (best_fitness - fitness_score) / denominator
            w = rd.uniform(0, 1) * math.log2(inside_log+1)

            # Apply W_i formula (Eq. 3)
            # This logic is based on the fitness ranking (i.e., the sorted order)
            if idx_agent < math.ceil(N_AGENTS / 2):
                # if S(i) ranks the first half of the population
                w = 1 + w
            else:
                w = 1 - w

            weights_vector.append(w)

        return np.array(weights_vector)

    def __update_slime_position(self, agents, weights_vector, best_agent, iteration):
        """
        Memperbarui posisi setiap agen berdasarkan formula pergerakan SMA.
        """
        MAX_ITERATIONS = self.optimizer['params']['MAX_ITERATIONS']
        N_AGENTS = self.optimizer['params']['N_AGENTS']
        N_DIMENSION = self.optimizer['params']['FUNCTIONS']['n_features']
        LOWER_BOUND = self.optimizer['params']['FUNCTIONS']['lowerbound']
        UPPER_BOUND = self.optimizer['params']['FUNCTIONS']['upperbound']
        Z_VALUE = self.optimizer['params']['Z_VALUE']
        slime_best_position = best_agent['position']
        slime_best_fitness = best_agent['fitness']

        a = math.atanh(-(iteration/MAX_ITERATIONS)+np.finfo(float).eps)
        for idx_agent, agent in enumerate(agents):
            # update nilai p
            p = math.tanh(abs(
                agent['fitness'] - slime_best_fitness
            ))

            # update position
            r = np.random.random()
            if r < p:
                slime_mould_1 = agents[np.random.randint(
                    0, N_AGENTS)]['position'].copy()
                slime_mould_2 = agents[np.random.randint(
                    0, N_AGENTS)]['position'].copy()
                vb = np.array([rd.uniform(-a, a)
                               for _ in range(N_DIMENSION)])
                agents[idx_agent]['position'] = slime_best_position + (
                    vb * (
                        weights_vector[idx_agent] *
                        slime_mould_1 - slime_mould_2
                    )
                )
            elif r >= p:
                vc = np.array([(1 - (iteration/MAX_ITERATIONS))
                               for _ in range(N_DIMENSION)])
                agents[idx_agent]['position'] = vc * agent['position']
            else:
                r = np.random.random()
                if r < Z_VALUE:
                    agents[idx_agent]['position'] = np.array([
                        r*(UPPER_BOUND - LOWER_BOUND)+LOWER_BOUND for _ in range(N_DIMENSION)
                    ])

            # normalize new position values sum(X[i]) = 1
            agents[idx_agent]['position'] = self._normalize_agent_vector(
                agents[idx_agent]['position'])

        return agents
