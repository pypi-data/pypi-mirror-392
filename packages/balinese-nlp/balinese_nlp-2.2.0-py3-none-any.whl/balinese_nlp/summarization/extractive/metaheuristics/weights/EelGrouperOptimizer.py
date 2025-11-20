from .BaseMetaSummarizerWeights import BaseMetaSummarizerWeights
import random as rd
import numpy as np
import math


class EelGrouperOptimizer(BaseMetaSummarizerWeights):
    def __init__(self,
                 N_EELS=30,
                 MAX_ITERATIONS=100,
                 MAX_KONVERGEN=10,
                 OPTIMIZER_NAME='Eel and Grouper Optimizer',
                 FUNCTIONS={
                     'n_features': 2,
                     'compression_rate': 0.67,  # must be 0.5 <= comp_rate <= 1
                     'objective': 'max',
                     # metrics for evaluating each agent fitness {accuracy, fleiss, krippendorff}
                     'metric': 'accuracy'
                 },
                 BREAK_IF_CONVERGENCE=True
                 ):
        """
        Eel and Grouper Optimizer (EGO)
        - Inspiration: Interaction and Foraging Strategy of Eels and Groupers in Marine Ecosystems
        """
        super().__init__(
            N_AGENTS=N_EELS,
            MAX_ITERATIONS=MAX_ITERATIONS,
            MAX_KONVERGEN=MAX_KONVERGEN,
            FUNCTIONS=FUNCTIONS,
            BREAK_IF_CONVERGENCE=BREAK_IF_CONVERGENCE,
        )
        self.optimizer['name'] = OPTIMIZER_NAME

    def solve(self):
        if not self.IS_FIT:
            raise ValueError(
                'Please fit your data first through fit() method!')

        MAX_ITERATIONS = self.optimizer['params']['MAX_ITERATIONS']

        # initialize agents
        # 1. initialize agents
        agents = self._initialize_agents()
        best_fitness_previous = float("-inf")

        # 2. bagi agents ke dalam tiga kelompok
        XPrey, XGrouper, XEel = self.__divide_eel_grouper(agents)
        best_agent = XGrouper.copy()
        self.LIST_BEST_FITNESS.append(best_agent['fitness'])

        # 2. Optimization process
        convergence = 0
        for idx_iteration in range(MAX_ITERATIONS):
            # 3. update a and starvation rate
            a = 2 - 2 * (idx_iteration/MAX_ITERATIONS)
            starvation_rate = 100 * (idx_iteration/MAX_ITERATIONS)

            # 4. update eel position and simultaneously update the fitness
            agents, XGrouper = self.__update_eel_position(
                agents, XPrey, XGrouper, XEel, a, starvation_rate)

            # 5. Update XPrey
            XPrey = self._retrieve_best_agent(agents)

            # 6. check konvergensi
            best_agent = XGrouper
            self.LIST_BEST_FITNESS.append(best_agent['fitness'])
            is_break, best_fitness_previous, convergence = self._check_convergence(
                best_agent['fitness'], best_fitness_previous, convergence, idx_iteration)
            if is_break and self.BREAK_IF_CONVERGENCE:
                break

        self._IS_SOLVE = True

        return best_agent

    def __divide_eel_grouper(self, agents):
        """
        Bagi agents ke dalam tiga kelompok: XPrey, XGrouper, XEel

        """
        N_AGENTS = self.optimizer['params']['N_AGENTS']
        XPrey = agents[rd.randint(0, N_AGENTS-1)].copy()
        XGrouper = agents[rd.randint(0, N_AGENTS-1)].copy()
        XEel = agents[rd.randint(0, N_AGENTS-1)].copy()
        return XPrey, XGrouper, XEel

    def __update_eel_position(self, agents, XPrey, XGrouper, XEel, a, starvation_rate):
        BATAS_BAWAH = self.optimizer['params']['FUNCTIONS']['lowerbound']
        BATAS_ATAS = self.optimizer['params']['FUNCTIONS']['upperbound']

        # update position based on Grouper and Eel
        for i, agent in enumerate(agents):
            # update r1, r2, r3, r4, C1, C2, and p
            r1 = np.random.rand()
            r2 = np.random.rand()
            r3 = (a - 2) * r1 + 2
            r4 = 100 * np.random.rand()
            b = a * r2
            C1 = 2 * a * r1 - a  # Coefficient for Grouper update
            C2 = 2 * r2  # Coefficient for Eel update

            # update agent position based on grouper
            X_rand = self.__generate_random_agent(agents)['position']
            D_grouper = abs(agents[i]['position'] - C2 * X_rand)
            agents[i]['position'] = X_rand + C1 * D_grouper

            # update XEeel position
            if r4 <= starvation_rate:
                XEel['position'] = C2*XGrouper['position'].copy()
            else:
                X_rand = self.__generate_random_agent(agents)['position']
                XEel['position'] = C2 * X_rand

            # update variable X1 and X2
            Distance2Eel = abs(XEel['position'] - XPrey['position'])
            X_1 = math.exp(b*r3) * math.sin(2*math.pi*r3) * C1 * \
                Distance2Eel + XEel['position']
            Distance2Grouper = abs(XGrouper['position'] - XPrey['position'])
            X_2 = XGrouper['position'] + C1 * Distance2Grouper

            if np.random.rand() < 0.5:
                agents[i]['position'] = (0.8*X_1 + 0.2*X_2)/2
            else:
                agents[i]['position'] = (0.2*X_1 + 0.8*X_2)/2

            # 8. apply boundaries clip: make sure no search agents leave the search space area
            # agents[i]['position'] = np.clip(
            #     agents[i]['position'], BATAS_BAWAH, BATAS_ATAS)

            # update XGrouper (best search agent)
            agents[i]['fitness'] = self._evaluate_fitness([agents[i]])[
                0]['fitness']
            if agents[i]['fitness'] > XGrouper['fitness']:
                XGrouper = agents[i].copy()

        return agents, XGrouper

    def __generate_random_agent(self, agents):
        N_AGENTS = self.optimizer['params']['N_AGENTS']
        random_agent = agents[rd.randint(0, N_AGENTS-1)].copy()
        return random_agent
