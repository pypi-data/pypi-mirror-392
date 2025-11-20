from .BaseMetaSummarizerWeights import BaseMetaSummarizerWeights
import random as rd
import numpy as np
import math


class ArchimedesOptimizationAlgorithm(BaseMetaSummarizerWeights):
    def __init__(self,
                 N_OBJECTS=30,
                 MAX_ITERATIONS=100,
                 MAX_KONVERGEN=10,
                 C1=2,
                 C2=6,
                 C3=2,
                 C4=0.57,
                 EXPLORATION_RATE=0.67,
                 OPTIMIZER_NAME='Archimedes Optimization Algorithm',
                 FUNCTIONS={
                     'n_features': 2,
                     'compression_rate': 0.67,  # must be 0.5 <= comp_rate <= 1
                     'objective': 'max',
                     # metrics for evaluating each agent fitness {accuracy, fleiss, krippendorff}
                     'metric': 'accuracy'
                 },
                 BREAK_IF_CONVERGENCE=True
                 ):
        super().__init__(
            N_AGENTS=N_OBJECTS,
            MAX_ITERATIONS=MAX_ITERATIONS,
            MAX_KONVERGEN=MAX_KONVERGEN,
            FUNCTIONS=FUNCTIONS,
            BREAK_IF_CONVERGENCE=BREAK_IF_CONVERGENCE,
        )
        self.optimizer['name'] = OPTIMIZER_NAME
        self.optimizer['params'].update({
            "C1": C1,
            "C2": C2,
            "C3": C3,
            "C4": C4,
            "EXPLORATION_RATE": EXPLORATION_RATE,
        })

    def solve(self):
        """
        Menjalankan proses optimasi AOA.
        """
        if not self.IS_FIT:
            raise ValueError(
                'Please fit your data first through fit() method!')
        MAX_ITERATIONS = self.optimizer['params']['MAX_ITERATIONS']

        # 1. initialize agents
        agents = self._initialize_agents()
        agents = self.__initialize_objects_properties(agents)

        # 2. evaluate fitness and select the best object
        agents = self._evaluate_fitness(agents)
        best_object = self._retrieve_best_agent(agents)
        best_fitness_previous = best_object['fitness']
        self.LIST_BEST_FITNESS.append(best_object['fitness'])

        # 3. Optimization Process
        convergence = 0
        for idx_iteration in range(MAX_ITERATIONS):
            # 4. update object position
            agents = self.__update_object_position(
                agents, best_object, idx_iteration)

            # 5. adjust boundaries
            # agents = self._adjust_boundaries(agents)

            # 5. Evaluate object fitness
            agents = self._evaluate_fitness(agents)

            # 6. select object with best fitness
            current_best_object = self._retrieve_best_agent(agents)
            current_best_fitness = current_best_object['fitness']

            # 7. terapkan elitism: perbarui best_agent hanya jika fitness saat ini lebih baik
            # karena objektifnya adalah 'max', kita cari nilai yang lebih besar
            objective = self.optimizer['params']['FUNCTIONS']['objective']
            if (current_best_fitness > best_object['fitness']) and (objective == 'max'):
                best_object = current_best_object.copy()

            # 7. check konvergensi
            self.LIST_BEST_FITNESS.append(best_object['fitness'])
            is_break, best_fitness_previous, convergence = self._check_convergence(
                best_object['fitness'], best_fitness_previous, convergence, idx_iteration)

            if is_break and self.BREAK_IF_CONVERGENCE:
                break

        self._IS_SOLVE = True
        return best_object

    def __initialize_objects_properties(self, agents):
        """
        Fungsi untuk menginisialisasi densitas, volume, dan akselerasi objek.
        """
        N_DIMENSION = self.optimizer['params']['FUNCTIONS']['n_features']
        LOWER_BOUND = self.optimizer['params']['FUNCTIONS']['lowerbound']
        UPPER_BOUND = self.optimizer['params']['FUNCTIONS']['upperbound']
        for idx_agent, agent in enumerate(agents):
            agents[idx_agent].update({
                # Densitas dan volume diinisialisasi dengan vektor acak di [0, 1]
                'densities': np.random.random(N_DIMENSION),
                'volume': np.random.random(N_DIMENSION),
                # Akselerasi diinisialisasi dalam batas masalah
                'acceleration': np.array([
                    np.random.random() * (UPPER_BOUND - LOWER_BOUND) + LOWER_BOUND
                    for d in range(N_DIMENSION)
                ]),
            })
        return agents

    def __update_object_position(self, agents, best_object, iteration):
        """
        Memperbarui posisi setiap objek berdasarkan mekanisme AOA.

        PERBAIKAN UTAMA:
        - Penggunaan np.random.random(N_DIMENSION) untuk menghasilkan vektor acak.
          Ini memastikan pembaruan posisi dilakukan secara element-wise,
          seperti yang didefinisikan dalam artikel ilmiah AOA.
        - Ini memperbaiki masalah stagnansi dan tren yang salah.
        """
        def normalize_acceleration(vector_acceleration):
            U = 0.9
            L = 0.1
            normalize_vector = U * ((vector_acceleration - np.min(vector_acceleration)) / (
                np.max(vector_acceleration) - np.min(vector_acceleration))) + L
            return normalize_vector

        MAX_ITERATIONS = self.optimizer['params']['MAX_ITERATIONS']
        EXPLORATION_RATE = self.optimizer['params']['EXPLORATION_RATE']
        C1 = self.optimizer['params']['C1']
        C2 = self.optimizer['params']['C2']
        C3 = self.optimizer['params']['C3']
        C4 = self.optimizer['params']['C4']
        N_DIMENSION = self.optimizer['params']['FUNCTIONS']['n_features']

        for idx_agent, agent in enumerate(agents):
            # update density and volume of each object
            agents[idx_agent]['densities'] = agent['densities'] + np.random.random() * \
                (best_object['densities'] - agent['densities'])
            agents[idx_agent]['volume'] = agent['volume'] + \
                np.random.random() * \
                (best_object['volume'] - agent['volume'])

            # update transfer and density decreasing factors TF and d
            TF = math.exp((iteration - MAX_ITERATIONS) / MAX_ITERATIONS)
            d = math.exp((MAX_ITERATIONS - iteration) / MAX_ITERATIONS) - \
                (iteration / MAX_ITERATIONS)

            # check exploration or exploitation based on TF
            if TF <= EXPLORATION_RATE:
                # exploration
                random_agent = self.__generate_random_agent(agents, agent)

                # update acceleration (Eq. 12)
                agents[idx_agent]['acceleration'] = (random_agent['densities'] + random_agent['volume'] *
                                                     random_agent['acceleration']) / (agents[idx_agent]['densities'] * agents[idx_agent]['volume'])

                # normalize acceleration (Eq. 13)
                agents[idx_agent]['acceleration'] = normalize_acceleration(
                    agents[idx_agent]['acceleration'])

                # update position (Eq. 14)
                agents[idx_agent]['position'] = random_agent['position'] + C1 * np.random.random() * \
                    agents[idx_agent]['acceleration'] * d * \
                    (random_agent['position'] - agents[idx_agent]['position'])

            else:
                # exploitation
                # update acceleration (Eq. 10)
                agents[idx_agent]['acceleration'] = (best_object['densities'] + best_object['volume'] * best_object['acceleration']) / (
                    agents[idx_agent]['densities'] * agents[idx_agent]['volume'])

                # normalize acceleration (Eq. 11)
                agents[idx_agent]['acceleration'] = normalize_acceleration(
                    agents[idx_agent]['acceleration'])

                # update direction flag F (Eq. 16)
                P = 2 * np.random.random() - C4
                F = 1
                if P <= 0.5:
                    F = -1

                # update position (Eq. 15)
                T = C3 * TF
                agents[idx_agent]['position'] = best_object['position'] + F * C2 * np.random.random() * \
                    agents[idx_agent]['acceleration'] * d * \
                    (T * best_object['position'] -
                     agents[idx_agent]['position'])

        return agents

    def __generate_random_agent(self, agents, agent):
        """
        Secara acak memilih agen yang bukan agen saat ini.
        """
        N_AGENTS = self.optimizer['params']['N_AGENTS']
        random_agent = agents[rd.randint(0, N_AGENTS - 1)].copy()
        # Pastikan agen acak yang dipilih bukan agen yang sedang diperbarui
        while random_agent['name'] == agent['name']:
            random_agent = agents[rd.randint(0, N_AGENTS - 1)].copy()
        return random_agent
