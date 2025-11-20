from balinese_nlp.summarization.extractive.metaheuristics.BaseMetaSummarizer import BaseMetaSummarizer
import numpy as np
import pandas as pd


class BaseMetaSummarizerWeights(BaseMetaSummarizer):

    def __init__(self,
                 N_AGENTS,
                 MAX_ITERATIONS,
                 MAX_KONVERGEN,
                 BREAK_IF_CONVERGENCE,
                 FUNCTIONS,
                 ):
        super().__init__(
            N_AGENTS=N_AGENTS,
            MAX_ITERATIONS=MAX_ITERATIONS,
            MAX_KONVERGEN=MAX_KONVERGEN,
            FUNCTIONS=FUNCTIONS,
            BREAK_IF_CONVERGENCE=BREAK_IF_CONVERGENCE,
        )

    def _initialize_agents(self):
        super()._initialize_agents()
        N_AGENTS = self.optimizer['params']['N_AGENTS']
        N_FEATURES = self.optimizer['params']['FUNCTIONS']['n_features']
        OBJECTIVE = self.optimizer['params']['FUNCTIONS']['objective']

        agents = [None for _ in range(N_AGENTS)]
        for idx_agent in range(N_AGENTS):
            random_position = np.random.uniform(size=N_FEATURES)
            # # normalized agent position vector
            # random_position = self._normalize_agent_vector(random_position)

            agents[idx_agent] = {
                "name": f"Agent-{idx_agent}",
                "position": random_position,
            }
            # update inisialisasi nilai fitness (maksimasi)
            fitness = {
                'fitness': float("-inf")
            }
            if OBJECTIVE == 'min':
                fitness = {
                    'fitness': float("inf")
                }
            agents[idx_agent].update(fitness)

            # update inisialisasi nilai PBest
            agents[idx_agent].update({
                'PBest': {
                    'position': random_position,
                    **fitness
                }
            })

        return agents

    def _normalize_agent_vector(self, agent_vector):
        """Function to normalize each agent vector so its vector's sum is 1

        Args:
            agent (np.ndarray): Numpy array of agent vector
        """
        normalized_agent_vector = agent_vector/np.sum(agent_vector)
        return normalized_agent_vector

    def _evaluate_fitness(self, agents):
        super()._evaluate_fitness(agents)
        dfs_train = self.dfs_train
        n_corpus = len(dfs_train)

        for idx_agent, agent in enumerate(agents):
            agent_weights = agent['position'].copy()  # ndarray

            # normalize bobot acak dalam setiap agent agar sum seluruh bobot setiap fitur = 1
            agent_weights = self._normalize_agent_vector(agent_weights)

            mean_agent_performance_metric = 0
            for title, df in dfs_train.items():
                preprocessed_sentences = df['preprocessed_sentences']
                X = df.drop(['preprocessed_sentences', 'labels'], axis=1)
                y = df['labels'].values
                n_sentences = X.shape[0]

                # hitung dot product dari agents_weight dengan matrix df ekstraksi fitur (1 x N).(N x number of sentences) where N is number of extracted features
                total_sentences_score = np.dot(agent_weights, X.values.T)

                # susun ke dalam format dataframe (dimensi ke-1 adalah posisi indeks kalimat dalam teks, dimensi ke-2 hasil total scores weight dan dimensi ke 3 adalah label extractive)
                df_sentences_score_with_label = pd.DataFrame(np.array([
                    [idx_sentence for idx_sentence in range(n_sentences)],
                    preprocessed_sentences,
                    total_sentences_score,
                    y
                ]).T, columns=['sentence_idx', 'preprocessed_sentences', 'total_sentence_score', 'labels'])

                # calculate metric score based on the inputted metric
                metric_score = self.FITNESS_FUNCTION(
                    df_sentences_score_with_label)
                mean_agent_performance_metric += metric_score

            # hitung fitness agent sebagai rata-rata metrics terhadap corpus latihs
            mean_agent_performance_metric /= n_corpus

            # ganti nilai fitness dari agent dengan mean performance metric
            agents[idx_agent]['fitness'] = mean_agent_performance_metric
        return agents
