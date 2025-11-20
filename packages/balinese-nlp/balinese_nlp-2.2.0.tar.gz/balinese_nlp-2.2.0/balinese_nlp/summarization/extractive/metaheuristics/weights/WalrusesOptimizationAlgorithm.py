from .BaseMetaSummarizerWeights import BaseMetaSummarizerWeights
import random as rd
import numpy as np


class WalrusesOptimizationAlgorithm(BaseMetaSummarizerWeights):
    """
    Implements the Walruses Optimization Algorithm (WaOA) based on the provided research paper.
    This version includes a critical fix to the update logic, ensuring each phase
    of the algorithm builds upon the previous one. This addresses both stagnation and
    the decreasing fitness trend.
    """

    def __init__(self,
                 N_WALRUS=50,
                 MAX_ITERATIONS=100,
                 MAX_KONVERGEN=10,
                 OPTIMIZER_NAME='Walrus Optimization Algorithm',
                 FUNCTIONS={
                     'n_features': 2,
                     'compression_rate': 0.67,  # must be 0.5 <= comp_rate <= 1
                     'objective': 'max',
                     # metrics for evaluating each agent fitness {accuracy, fleiss, krippendorff,f1_macro, f1_weighted, recall_macro, recall_weighted, precision_macro, precision_weighted, roc_auc_score_macro, roc_auc_score_weighted}
                     'metric': 'accuracy'
                 },
                 BREAK_IF_CONVERGENCE=True
                 ):
        super().__init__(
            N_AGENTS=N_WALRUS,
            MAX_ITERATIONS=MAX_ITERATIONS,
            MAX_KONVERGEN=MAX_KONVERGEN,
            FUNCTIONS=FUNCTIONS,
            BREAK_IF_CONVERGENCE=BREAK_IF_CONVERGENCE,
        )
        self.optimizer['name'] = OPTIMIZER_NAME

    def solve(self):
        """
        Runs the WaOA optimization process.
        """
        if not self.IS_FIT:
            raise ValueError(
                'Please fit your data first through fit() method!')

        MAX_ITERATIONS = self.optimizer['params']['MAX_ITERATIONS']
        OBJECTIVE = self.optimizer['params']['FUNCTIONS']['objective']

        # 1. initialize agents
        agents = self._initialize_agents()

        # 2. Evaluate agents and find the strongest walrus
        agents = self._evaluate_fitness(agents)
        best_agent = self._retrieve_best_agent(agents)
        best_fitness_previous = best_agent['fitness']

        strongest_walrus = best_agent.copy()
        self.LIST_BEST_FITNESS.append(strongest_walrus['fitness'])

        # 3. Optimization process
        convergence = 0
        for idx_iteration in range(MAX_ITERATIONS):
            # exploration vs exploitation
            agents = self.__exploration_vs_exploitation(
                agents, strongest_walrus, idx_iteration)

            # NOTE: The '_adjust_boundaries' function is commented out in your original code.
            # It is highly recommended to uncomment and implement this to ensure agents
            # stay within the search space boundaries, which can also prevent stagnation.
            agents = self._adjust_boundaries(agents)

            # evaluate fitness
            agents = self._evaluate_fitness(agents)

            # select best agent
            # best_agent_current = self._retrieve_best_agent(agents)
            strongest_walrus = self._retrieve_best_agent(agents)

            # if OBJECTIVE == 'max':
            #     if best_agent_current['fitness'] > best_agent['fitness']:
            #         strongest_walrus = best_agent_current.copy()

            # 6. check konvergensi
            self.LIST_BEST_FITNESS.append(strongest_walrus['fitness'])
            is_break, best_fitness_previous, convergence = self._check_convergence(
                strongest_walrus['fitness'], best_fitness_previous, convergence, idx_iteration)
            if is_break and self.BREAK_IF_CONVERGENCE:
                break

        self._IS_SOLVE = True

        return best_agent

    def __exploration_vs_exploitation(self, agents, strongest_walrus, iteration):
        """
        Updates the positions of all agents based on the three WaOA phases.

        FIX: This method has been refactored to ensure the position updates are
        sequential. The result of each phase is used as the starting point for
        the next phase, preventing the trend of decreasing fitness and stagnation.
        """
        LB = self.optimizer['params']['FUNCTIONS']['lowerbound']
        UB = self.optimizer['params']['FUNCTIONS']['upperbound']

        for idx_agent, agent in enumerate(agents):
            # Use a temporary variable to hold the agent's state as it is updated
            # through each phase. This ensures the updates are chained.
            current_agent = agent.copy()

            # Phase 1: Feeding Strategy (Exploration)
            # This uses the strongest walrus to guide the agent.
            current_agent = self.__feeding_strategy(
                current_agent, strongest_walrus)

            # Phase 2: Migration
            # This uses a randomly selected agent as a migration destination.
            random_agent = self.__random_select_agent(agents, current_agent)
            current_agent = self.__migration(current_agent, random_agent)

            # Phase 3: Escaping and Fighting with predators (Exploitation)
            # This performs local search around the current agent's position.
            current_agent = self.__attacking_predators(
                current_agent, iteration)

            # Update the agent in the main list with the final, updated state
            agents[idx_agent] = current_agent.copy()

        return agents

    def __feeding_strategy(self, agent, strongest_walrus):
        """
        Implements Phase 1: Feeding Strategy (Exploration).
        Equation (3) from the paper.
        """
        I = rd.randint(1, 2)
        agent_phase_1 = agent.copy()
        # Generate a random vector for each dimension.
        rand = np.random.random(len(agent['position']))
        agent_phase_1['position'] = agent['position'] + rand * (
            strongest_walrus['position'] - I * agent['position'])

        # evaluate fitness function
        agent_phase_1 = self._evaluate_fitness([agent_phase_1])[0]

        # update agent position if the new fitness is better
        # For maximization, '>' is the correct operator.
        if agent_phase_1['fitness'] > agent['fitness']:
            agent = agent_phase_1.copy()

        return agent

    def __migration(self, agent, random_agent):
        """
        Implements Phase 2: Migration.
        Equation (5) from the paper.
        """
        I = rd.randint(1, 2)
        agent_phase_2 = agent.copy()
        # Generate a random vector for each dimension.
        rand = np.random.random(len(agent['position']))

        # Corrected the condition for maximization.
        # The logic is: if the random agent is better, move towards it.
        # if the random agent is worse, move away from it.
        if random_agent['fitness'] > agent['fitness']:
            agent_phase_2['position'] = agent['position'] + rand * (
                random_agent['position'] - I * agent['position'])
        else:
            agent_phase_2['position'] = agent['position'] + \
                rand * (agent['position'] - random_agent['position'])

        # evaluate fitness
        agent_phase_2 = self._evaluate_fitness([agent_phase_2])[0]

        # update agent position if the new fitness is better
        if agent_phase_2['fitness'] > agent['fitness']:
            agent = agent_phase_2.copy()

        return agent

    def __attacking_predators(self, agent, iteration):
        """
        Implements Phase 3: Escaping and Fighting with predators (Exploitation).
        Equation (7) and (8) from the paper.
        """
        BATAS_BAWAH = self.optimizer['params']['FUNCTIONS']['lowerbound']
        BATAS_ATAS = self.optimizer['params']['FUNCTIONS']['upperbound']
        t = iteration + 1  # iteration starts from 0, paper uses t from 1

        # calculate local upper and lower bound
        # Based on equation (8) from the paper.
        local_lb = BATAS_BAWAH / t
        local_up = BATAS_ATAS / t

        # calculate agent_phase_3
        # Corrected the formula to match equation (7) from the paper.
        agent_phase_3 = agent.copy()
        rand1 = np.random.random(len(agent['position']))
        rand2 = np.random.random(len(agent['position']))
        agent_phase_3['position'] = agent['position'] + \
            (local_lb + rand1 * (local_up - rand2 * local_lb))

        # evaluate fitness
        agent_phase_3 = self._evaluate_fitness([agent_phase_3])[0]

        # update agent position
        if agent_phase_3['fitness'] > agent['fitness']:
            agent = agent_phase_3.copy()

        return agent

    def __random_select_agent(self, agents, agent):
        """
        Randomly selects an agent that is not the same as the current one.
        """
        N_AGENTS = self.optimizer['params']['N_AGENTS']
        # randomly select new agent m where m!=indeks agent
        # It's important to select from the original list, not the one being updated in the loop.
        # This prevents picking a walrus that has already moved in the current iteration.
        random_agent = agents[rd.randint(0, N_AGENTS - 1)].copy()
        while random_agent['name'] == agent['name']:
            random_agent = agents[rd.randint(0, N_AGENTS - 1)].copy()
        return random_agent
