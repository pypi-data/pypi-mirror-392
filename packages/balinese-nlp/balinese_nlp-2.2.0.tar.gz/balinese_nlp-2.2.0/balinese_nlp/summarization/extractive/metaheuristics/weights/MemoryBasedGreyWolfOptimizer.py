from .BaseMetaSummarizerWeights import BaseMetaSummarizerWeights
from .GreyWolfOptimizer import GreyWolfOptimizer
import random as rd
import numpy as np


class MemoryBasedGreyWolfOptimizer(GreyWolfOptimizer):
    def __init__(self,
                 N_WOLVES=30,
                 MAX_ITERATIONS=100,
                 MAX_KONVERGEN=10,
                 CROSSOVER_RATE=0.67,
                 OPTIMIZER_NAME='Memory-based Grey Wolf Optimizer',
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
            N_WOLVES=N_WOLVES,
            MAX_ITERATIONS=MAX_ITERATIONS,
            MAX_KONVERGEN=MAX_KONVERGEN,
            FUNCTIONS=FUNCTIONS,
            BREAK_IF_CONVERGENCE=BREAK_IF_CONVERGENCE,
        )
        self.optimizer['name'] = OPTIMIZER_NAME
        self.optimizer['params'].update({
            "CROSSOVER_RATE": CROSSOVER_RATE,
        })

    def solve(self):
        if not self.IS_FIT:
            raise ValueError(
                'Please fit your data first through fit() method!')
        MAX_ITERATIONS = self.optimizer['params']['MAX_ITERATIONS']

        # initialize agents
        # 1. initialize agents
        agents = self._initialize_agents()
        alpha_wolves, betha_wolves, delta_wolves = self._initialize_best_wolves(
            agents)
        best_agent = alpha_wolves
        best_fitness_previous = float('-inf')
        self.LIST_BEST_FITNESS.append(best_agent['fitness'])

        # 3. Optimization Process
        convergence = 0
        for idx_iteration in range(MAX_ITERATIONS):
            # evaluate the leader wolves
            alpha_wolves, betha_wolves, delta_wolves = self._replace_leader_wolves(
                alpha_wolves, betha_wolves, delta_wolves, agents)

            # 5. Update wolves position
            agents = self._update_wolves_position(
                alpha_wolves, betha_wolves, delta_wolves, agents, idx_iteration)

            # 6. Evaluate agents
            agents = self._evaluate_fitness(agents)

            # update pBest wolves
            agents = self._update_pbest_wolves(agents)

            # 6. check konvergensi
            self.LIST_BEST_FITNESS.append(best_agent['fitness'])
            is_break, best_fitness_previous, convergence = self._check_convergence(
                best_agent['fitness'], best_fitness_previous, convergence, idx_iteration)
            if is_break and self.BREAK_IF_CONVERGENCE:
                break
            best_agent = alpha_wolves

        self._IS_SOLVE = True

        return best_agent

    def _update_wolves_position(self, alpha_wolves, betha_wolves, delta_wolves, agents, iteration):
        MAX_ITERATIONS = self.optimizer['params']['MAX_ITERATIONS']
        CROSSOVER_RATE = self.optimizer['params']['CROSSOVER_RATE']
        N_AGENTS = self.optimizer['params']['N_AGENTS']
        BATAS_BAWAH = self.optimizer['params']['FUNCTIONS']['lowerbound']
        BATAS_ATAS = self.optimizer['params']['FUNCTIONS']['upperbound']

        a = 2*(1-(iteration/MAX_ITERATIONS))
        k = 1 - (1*iteration/MAX_ITERATIONS)

        for idx_agent, agent in enumerate(agents):
            pbest_agent = agent['PBest']

            # apply memory gwo logic here
            if np.random.random() < CROSSOVER_RATE:
                # calculate X1 (how far each agent with alpha wolves)
                r1, r2 = np.random.random(), np.random.random()
                A1, C1 = 2 * a * r1 - a, 2 * r2
                D_alpha = np.abs(
                    C1 * alpha_wolves['position'] - pbest_agent['position'])
                X1 = alpha_wolves['position'] - A1*D_alpha

                # calculate X2 (how far each agent with betha wolves)
                r1, r2 = np.random.random(), np.random.random()
                A2, C2 = 2 * a * r1 - a, 2 * r2
                D_betha = np.abs(
                    C2 * betha_wolves['position'] - pbest_agent['position'])
                X2 = betha_wolves['position'] - A2*D_betha

                # calculate X3 (how far each agent with delta wolves)
                r1, r2 = np.random.random(), np.random.random()
                A3, C3 = 2 * a * r1 - a, 2 * r2
                D_delta = np.abs(
                    C3 * delta_wolves['position'] - pbest_agent['position'])
                X3 = delta_wolves['position'] - A3*D_delta
                agents[idx_agent]['position'] = (X1+X2+X3)/3

            else:
                # find two wolves randomly
                random_wolf_1 = agents[rd.randint(0, N_AGENTS-1)]
                random_wolf_2 = agents[rd.randint(0, N_AGENTS-1)]
                agents[idx_agent]['position'] = pbest_agent['position'] + k * \
                    np.abs(random_wolf_1['position']-random_wolf_2['position'])

        return agents

    def _update_pbest_wolves(self, agents):
        N_AGENTS = self.optimizer['params']['N_AGENTS']
        OBJECTIVE = self.optimizer['params']['FUNCTIONS']['objective']
        # mekanisme perhitungan PBest
        for idx_agent in range(N_AGENTS):
            if ((agents[idx_agent]['fitness'] < agents[idx_agent]['PBest']['fitness']) and (OBJECTIVE == 'min')) or ((agents[idx_agent]['fitness'] > agents[idx_agent]['PBest']['fitness']) and (OBJECTIVE == 'max')):
                # update nilai PBest setiap agent
                agents[idx_agent]['PBest']['position'] = agents[idx_agent]['position'].copy()
                agents[idx_agent]['PBest']['fitness'] = agents[idx_agent]['fitness']
        return agents
