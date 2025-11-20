from .BaseMetaSummarizerWeights import BaseMetaSummarizerWeights
import random as rd
import numpy as np


class GreyWolfOptimizer(BaseMetaSummarizerWeights):
    def __init__(self,
                 N_WOLVES=50,
                 MAX_ITERATIONS=100,
                 MAX_KONVERGEN=10,
                 OPTIMIZER_NAME='Grey Wolf Optimizer',
                 FUNCTIONS={
                     'n_features': 2,
                     'compression_rate': 0.67,  # must be 0.5 <= comp_rate <= 1
                     'objective': 'max',
                     # metrics for evaluating each agent fitness {accuracy, fleiss, krippendorff}
                     'metric': 'accuracy'
                 },
                 BREAK_IF_CONVERGENCE=True
                 ):
        """Grey Wolf Optimizer for optimizing weight features in Balinese Extractive Text Summarization

        Args:
            N_WOLVES (int): number of grey wolf individuals. Defaults to 50.
            MAX_ITERATIONS (int): maximum iterations. Defaults to 100.
            MAX_KONVERGEN (int): optimization will be stoped after MAX_KONVERGEN iterations. Defaults to 4.
            OPTIMIZER_NAME (str): your optimizer name will be. Defaults to 'Grey Wolf Optimizer'.
            FUNCTIONS (dict): objective function criteria. Defaults to { 'n_features': 4, 'compression_rate': 0.57,  # must be 0.5 <= comp_rate <= 1 'objective': 'max', 'metric': 'accuracy' # {accuracy, fleiss, kripendorff_alpha} }.
            BREAK_IF_CONVERGENCE (bool): flag if optimization will be stopped after MAX_KONVERGEN. Defaults to True.
        """
        super().__init__(
            N_AGENTS=N_WOLVES,
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

        # 1. Initialize agents
        agents = self._initialize_agents()
        alpha_wolves, betha_wolves, delta_wolves = self._initialize_best_wolves(
            agents)
        best_agent = alpha_wolves
        best_fitness_previous = best_agent['fitness']
        self.LIST_BEST_FITNESS.append(best_agent['fitness'])

        # 2. Optimization process
        convergence = 0
        for idx_iteration in range(MAX_ITERATIONS):
            # 3. evaluate the leader wolves
            alpha_wolves, betha_wolves, delta_wolves = self._replace_leader_wolves(
                alpha_wolves, betha_wolves, delta_wolves, agents)

            # 4. update wolves position
            agents = self._update_wolves_position(
                alpha_wolves, betha_wolves, delta_wolves, agents, idx_iteration)

            # 5. evaluate wolves fitness
            agents = self._evaluate_fitness(agents)

            # 6. check konvergensi
            self.LIST_BEST_FITNESS.append(best_agent['fitness'])
            is_break, best_fitness_previous, convergence = self._check_convergence(
                best_agent['fitness'], best_fitness_previous, convergence, idx_iteration)
            if is_break and self.BREAK_IF_CONVERGENCE:
                break
            best_agent = alpha_wolves

        self._IS_SOLVE = True

        return best_agent

    def _initialize_best_wolves(self, agents):
        """
        Pilih 3 serigala awal secara acak sebagai Alpha, Beta, dan Delta
        """
        alpha_wolves = agents[rd.randint(0, len(agents)-1)]
        betha_wolves = agents[rd.randint(0, len(agents)-1)]
        delta_wolves = agents[rd.randint(0, len(agents)-1)]
        return alpha_wolves, betha_wolves, delta_wolves

    def _replace_leader_wolves(self, alpha_wolves, betha_wolves, delta_wolves, agents):
        # record only the fitnesses
        for agent_data in agents:
            if agent_data['fitness'] > alpha_wolves['fitness']:
                alpha_wolves = agent_data.copy()
            elif agent_data['fitness'] > betha_wolves['fitness']:
                betha_wolves = agent_data.copy()
            elif agent_data['fitness'] > delta_wolves['fitness']:
                delta_wolves = agent_data.copy()
        return alpha_wolves, betha_wolves, delta_wolves

    def _update_wolves_position(self, alpha_wolves, betha_wolves, delta_wolves, agents, iteration):
        MAX_ITERATIONS = self.optimizer['params']['MAX_ITERATIONS']
        BATAS_BAWAH = self.optimizer['params']['FUNCTIONS']['lowerbound']
        BATAS_ATAS = self.optimizer['params']['FUNCTIONS']['upperbound']

        a = 2*(1-(iteration/MAX_ITERATIONS))
        for idx_agent, agent in enumerate(agents):

            # calculate X1 (how far each agent with alpha wolves)
            r1, r2 = np.random.random(), np.random.random()
            A1, C1 = 2 * a * r1 - a, 2 * r2
            D_alpha = np.abs(C1 * alpha_wolves['position'] - agent['position'])
            X1 = alpha_wolves['position'] - A1*D_alpha

            # calculate X2 (how far each agent with betha wolves)
            r1, r2 = np.random.random(), np.random.random()
            A2, C2 = 2 * a * r1 - a, 2 * r2
            D_betha = np.abs(C2 * betha_wolves['position'] - agent['position'])
            X2 = betha_wolves['position'] - A2*D_betha

            # calculate X3 (how far each agent with delta wolves)
            r1, r2 = np.random.random(), np.random.random()
            A3, C3 = 2 * a * r1 - a, 2 * r2
            D_delta = np.abs(C3 * delta_wolves['position'] - agent['position'])
            X3 = delta_wolves['position'] - A3*D_delta
            agents[idx_agent]['position'] = (X1+X2+X3)/3

            # apply position boundaries
            # agents[idx_agent]['position'] = np.clip(
            #     agents[idx_agent]['position'], BATAS_BAWAH, BATAS_ATAS)

        return agents
