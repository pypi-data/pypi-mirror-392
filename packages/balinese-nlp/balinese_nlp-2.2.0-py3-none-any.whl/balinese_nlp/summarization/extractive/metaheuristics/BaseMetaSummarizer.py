import numpy as np
import pandas as pd
import math
import krippendorff
from collections import Counter

from statsmodels.stats.inter_rater import fleiss_kappa
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score, roc_auc_score
from balinese_nlp.textpreprocessor import TextPreprocessor


class BaseMetaSummarizer:
    optimizer = None
    _IS_FIT = False
    _IS_SOLVE = False
    BREAK_IF_CONVERGENCE = None
    LIST_BEST_FITNESS = list()
    FITNESS_FUNCTION = None
    TEXTPREPOCESSOR = None

    def __init__(self,
                 N_AGENTS,
                 MAX_ITERATIONS,
                 MAX_KONVERGEN,
                 BREAK_IF_CONVERGENCE,
                 FUNCTIONS,
                 ):
        self.optimizer = {
            "name": None,
            "params": {
                'N_AGENTS': N_AGENTS,
                'MAX_ITERATIONS': MAX_ITERATIONS,
                "MAX_KONVERGEN": MAX_KONVERGEN,
                "FUNCTIONS": {
                    **FUNCTIONS,
                    'lowerbound': 0,
                    'upperbound': 1
                },
            }
        }
        self.TEXTPREPOCESSOR = TextPreprocessor()
        self._IS_SOLVE = False
        self._IS_FIT = False
        self.BREAK_IF_CONVERGENCE = BREAK_IF_CONVERGENCE
        self.LIST_BEST_FITNESS = list()  # record best fitness each iterations
        self.FITNESS_FUNCTION = self.__fitness_function_score
        # check apakah masing-masing parameter yang dimasukan sudah sesuai ketentuan
        if self.optimizer['params']['FUNCTIONS']['compression_rate'] < 0.5 or self.optimizer['params']['FUNCTIONS']['compression_rate'] > 1:
            raise ValueError(
                'Compression rate must be in this interval: 0.5 <= comp_rate <= 1')

    def fit(self, dfs_train):
        """Fit the input data

        Args:
            dfs_train (dict): dictionary of dataframe from each title. The dictionary key contains title and the value contain the df of extracted features from each title. Provide the same shape(dimension) of df in each title. In the last of title you must provide the 'extractive_summary' label which contains 1/0 label, where 1 is important summary sentence and 0 is not important summary sentence
        """
        if not isinstance(dfs_train, dict):
            raise TypeError(
                'Provide dfs_train as dictionary, where key is title text and value is extracted features from each title')

        if len(dfs_train) <= 0:
            raise ValueError('Please insert your dfs_train!')

        # check apakah dimensi yang diberikan user sudah sesuai dengan dimensi dfs_train
        N_FEATURES = self.optimizer['params']['FUNCTIONS']['n_features']
        for title, df in dfs_train.items():
            X = df.drop(['preprocessed_sentences', 'labels'], axis=1)
            if N_FEATURES != X.shape[1]:
                raise ValueError(
                    f'Please format your df {title} in dfs_train in the same N_FEATURES ({N_FEATURES}) size!')

        self.dfs_train = dfs_train
        self.IS_FIT = True

        return self

    def _initialize_agents(self):
        """
        Function for agents initialization based on size of features
        """
        pass

    def __fitness_function_score(self, df_sentences_score_with_label):
        """Menghitung skor kualitas hasil ringkasan dengan metriks tertentu. Metriks yang bisa digunakan:
        - accuracy: Accuracy Score from scikit-learn metrics
        - fleiss: Fleiss Kappa from package statsmodels.stats.inter_rate
        - krippendorff: Kripendorff Alpha from krippendorff package

        Args:
            df_sentences_score_with_label (_type_): dataframe yang berisi susunan indeks kalimat, total skor per kalimat dari fitur-fitur yang digunakan, label ground truth
        """
        def _calculate_accuracy_score(y_true, y_predicted_labels):
            score = accuracy_score(y_true, y_predicted_labels)
            return score

        def _calculate_f1_score_macro(y_true, y_predicted_labels):
            score = f1_score(y_true, y_predicted_labels, average='macro')
            return score

        def _calculate_f1_score_weighted(y_true, y_predicted_labels):
            score = f1_score(y_true, y_predicted_labels, average='weighted')
            return score

        def _calculate_recall_score_macro(y_true, y_predicted_labels):
            score = recall_score(y_true, y_predicted_labels, average='macro')
            return score

        def _calculate_recall_score_weighted(y_true, y_predicted_labels):
            score = recall_score(
                y_true, y_predicted_labels, average='weighted')
            return score

        def _calculate_precision_score_macro(y_true, y_predicted_labels):
            score = precision_score(
                y_true, y_predicted_labels, average='macro')
            return score

        def _calculate_precision_score_weighted(y_true, y_predicted_labels):
            score = precision_score(
                y_true, y_predicted_labels, average='weighted')
            return score

        def _calculate_roc_auc_score_macro(y_true, y_predicted_labels):
            score = roc_auc_score(
                y_true, y_predicted_labels, average='macro')
            return score

        def _calculate_roc_auc_score_weighted(y_true, y_predicted_labels):
            score = roc_auc_score(
                y_true, y_predicted_labels, average='weighted')
            return score

        def _calculate_fleiss_kappa_score(y_true, y_predicted_labels):
            y_true = y_true.astype(int)
            y_predicted_labels = y_predicted_labels.astype(int)
            annotation_data = np.array([
                y_true,
                y_predicted_labels
            ]).T
            # ada berapa banyak anotator
            num_items = len(annotation_data[:, 0])
            num_categories = 2  # label 0 atau 1
            # transforming data into correct format
            transformed_data = np.zeros((num_items, num_categories))
            for i, item_annotation in enumerate(annotation_data):
                for ann in item_annotation:
                    transformed_data[i, ann] += 1

            # calculate fleiss kappa
            score = fleiss_kappa(transformed_data)
            return score

        def _calculate_krippendorff(y_true, y_predicted_labels):
            y_true = y_true.astype(int)
            y_predicted_labels = y_predicted_labels.astype(int)
            annotation_data = np.array([
                y_true,
                y_predicted_labels
            ])
            score = krippendorff.alpha(reliability_data=annotation_data,
                                       level_of_measurement='nominal')
            return score

        def _calculate_rouge_L(system_summary, ground_truth_summary):
            def _longest_common_subsequence(X, Y):
                """Membantu menghitung Longest Common Subsequence."""
                m = len(X)
                n = len(Y)
                L = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

                for i in range(m + 1):
                    for j in range(n + 1):
                        if i == 0 or j == 0:
                            L[i][j] = 0
                        elif X[i-1] == Y[j-1]:
                            L[i][j] = L[i-1][j-1] + 1
                        else:
                            L[i][j] = max(L[i-1][j], L[i][j-1])
                return L[m][n]

            def _get_n_grams(tokens, n_gram):
                """Membantu mendapatkan n-gram dari list token."""
                return [tuple(tokens[i:i+n_gram]) for i in range(len(tokens) - n_gram + 1)]
            scores = dict()
            # tokenize system and ground truth summary
            tokens_A = self.TEXTPREPOCESSOR.balinese_word_tokenize(
                system_summary)
            tokens_B = self.TEXTPREPOCESSOR.balinese_word_tokenize(
                ground_truth_summary)

            len_A = len(tokens_A)
            len_B = len(tokens_B)

            # --- ROUGE-L (Longest Common Subsequence) ---
            lcs_count = _longest_common_subsequence(tokens_A, tokens_B)

            precision_l = lcs_count / len_A if len_A > 0 else 0
            recall_l = lcs_count / len_B if len_B > 0 else 0
            f1_l = (2 * precision_l * recall_l) / (precision_l +
                                                   recall_l) if (precision_l + recall_l) > 0 else 0

            scores['rouge_L_precision'] = precision_l
            scores['rouge_L_recall'] = recall_l
            scores['rouge_L_f1_score'] = f1_l
            return scores

        def _calculate_rouge(system_summary, ground_truth_summary, n_rouge=1):
            def _get_n_grams(tokens, n_gram):
                """Membantu mendapatkan n-gram dari list token."""
                return [tuple(tokens[i:i+n_gram]) for i in range(len(tokens) - n_gram + 1)]
            scores = dict()

            # tokenize system and ground truth summary
            tokens_A = self.TEXTPREPOCESSOR.balinese_word_tokenize(
                system_summary)
            tokens_B = self.TEXTPREPOCESSOR.balinese_word_tokenize(
                ground_truth_summary)

            # get n-gram
            ngrams_A = _get_n_grams(tokens_A, n_rouge)
            ngrams_B = _get_n_grams(tokens_B, n_rouge)

            # Use Counter to count occurrences for clipping
            count_A = Counter(ngrams_A)
            count_B = Counter(ngrams_B)

            # Calculate intersection_count (clipped count)
            intersection_count = 0
            for ngram, count in count_A.items():
                intersection_count += min(count, count_B[ngram])

            # total_ngrams for denominator must be the actual number of n-grams, including duplicates
            total_ngrams_A = sum(count_A.values())
            total_ngrams_B = sum(count_B.values())

            precision = intersection_count / total_ngrams_A if total_ngrams_A > 0 else 0
            recall = intersection_count / total_ngrams_B if total_ngrams_B > 0 else 0
            f1 = (2 * precision * recall) / (precision +
                                             recall) if (precision + recall) > 0 else 0

            scores[f'rouge_{n_rouge}_precision'] = precision
            scores[f'rouge_{n_rouge}_recall'] = recall
            scores[f'rouge_{n_rouge}_f1_score'] = f1

            return scores

        metric = self.optimizer['params']['FUNCTIONS']['metric']
        compression_rate = self.optimizer['params']['FUNCTIONS']['compression_rate']
        n_sentences = df_sentences_score_with_label.shape[0]

        # sorting sentences berdasarkan total sentence score dikalikan weights dari agent
        df_sentences_score_with_label.sort_values(
            by='total_sentence_score', ascending=False, inplace=True)

        # extract Top-N sentences as system summary
        number_of_compressed_sentences = (compression_rate*n_sentences)
        top_n_extracted_sentences = int(np.ceil(n_sentences -
                                                number_of_compressed_sentences))
        sentence_indexes_summary = df_sentences_score_with_label.head(
            top_n_extracted_sentences)['sentence_idx'].values

        # extract label 1/0 dari top-N sentences
        y_predicted_labels = []
        for idx in range(n_sentences):
            if idx < top_n_extracted_sentences:
                y_predicted_labels.append(1)
            else:
                y_predicted_labels.append(0)
        y_predicted_labels = np.array(y_predicted_labels).astype(int)

        # extract system and ground truth summary untuk perhitungan metriks berbasis ROUGE
        ground_truth_summary = ' '.join(
            df_sentences_score_with_label[
                df_sentences_score_with_label['labels'] == 1
            ].sort_values(by='sentence_idx', ascending=True)['preprocessed_sentences'].values
        )
        system_summary = ' '.join(
            df_sentences_score_with_label[
                df_sentences_score_with_label.index.isin(
                    sentence_indexes_summary)
            ].sort_values(by='sentence_idx', ascending=True)['preprocessed_sentences'].values
        )

        # hitung accuracy score atau ROUGE untuk setiap dokumen
        y_true = df_sentences_score_with_label['labels'].values.astype(int)
        fitness_score = 0
        if metric == 'accuracy':
            fitness_score = _calculate_accuracy_score(
                y_true, y_predicted_labels)
        elif metric == 'fleiss':
            fitness_score = _calculate_fleiss_kappa_score(
                y_true, y_predicted_labels)
        elif metric == 'krippendorff':
            fitness_score = _calculate_krippendorff(
                y_true, y_predicted_labels)
        elif metric == 'f1_macro':
            fitness_score = _calculate_f1_score_macro(
                y_true, y_predicted_labels)
        elif metric == 'f1_weighted':
            fitness_score = _calculate_f1_score_weighted(
                y_true, y_predicted_labels)
        elif metric == 'recall_macro':
            fitness_score = _calculate_recall_score_macro(
                y_true, y_predicted_labels)
        elif metric == 'recall_weighted':
            fitness_score = _calculate_recall_score_weighted(
                y_true, y_predicted_labels)
        elif metric == 'precision_macro':
            fitness_score = _calculate_precision_score_macro(
                y_true, y_predicted_labels)
        elif metric == 'precision_weighted':
            fitness_score = _calculate_precision_score_weighted(
                y_true, y_predicted_labels)
        elif metric == 'roc_auc_macro':
            fitness_score = _calculate_roc_auc_score_macro(
                y_true, y_predicted_labels)
        elif metric == 'roc_auc_weighted':
            fitness_score = _calculate_roc_auc_score_weighted(
                y_true, y_predicted_labels)
        elif (metric == 'rouge_1_f1_score') or (metric == 'rouge_1_recall') or (metric == 'rouge_1_precision'):
            fitness_score = _calculate_rouge(
                system_summary, ground_truth_summary, n_rouge=1)[metric]
        elif (metric == 'rouge_2_f1_score') or (metric == 'rouge_2_recall') or (metric == 'rouge_2_precision'):
            fitness_score = _calculate_rouge(
                system_summary, ground_truth_summary, n_rouge=2)[metric]
        elif (metric == 'rouge_L_f1_score') or (metric == 'rouge_L_recall') or (metric == 'rouge_L_precision'):
            fitness_score = _calculate_rouge_L(
                system_summary, ground_truth_summary)[metric]
        else:
            raise ValueError(
                'Please provide metric within these values:\naccuracy, fleiss, krippendorff, f1_macro, f1_weighted, recall_macro, recall_weighted, precision_macro, precision_weighted, roc_auc_macro, roc_auc_weighted, rouge_1_f1_score, rouge_1_recall, rouge_1_precision, rouge_2_f1_score, rouge_2_recall, rouge_2_precision, rouge_L_f1_score, rouge_L_recall, rouge_L_precision')

        return fitness_score

    def _evaluate_fitness(self, agents):
        """For each agent in agents we calculate the average accuracy/fleiss/krippendorff using all dfs_train

        Args:
            agents (list): list of agents
        """
        pass

    def _adjust_boundaries(self, agents):
        BATAS_BAWAH = self.optimizer['params']['FUNCTIONS']['lowerbound']
        BATAS_ATAS = self.optimizer['params']['FUNCTIONS']['upperbound']
        for idx_agent, agent in enumerate(agents):
            agents[idx_agent]['position'] = np.clip(
                agents[idx_agent]['position'], BATAS_BAWAH, BATAS_ATAS)
        return agents

    def _retrieve_best_agent(self, agents):
        """
        Function untuk retrieve best agent pada iterasi terakhir setelah di solve
        """
        OBJECTIVE = self.optimizer['params']['FUNCTIONS']['objective']

        fitness = np.array([
            agent_data['fitness'] for agent_data in agents
        ])
        best_indices_agents = np.argmin(fitness)
        if OBJECTIVE == 'max':
            best_indices_agents = np.argmax(fitness)

        return agents[best_indices_agents]

    def _retrieve_worst_agent(self, agents):
        """
        Function untuk retrieve worst agent pada iterasi terakhir setelah di solve
        """
        OBJECTIVE = self.optimizer['params']['FUNCTIONS']['objective']

        fitness = np.array([
            agent_data['fitness'] for agent_data in agents
        ])
        worst_indices_agents = np.argmax(fitness)
        if OBJECTIVE == 'max':
            worst_indices_agents = np.argmin(fitness)

        return agents[worst_indices_agents]

    def _check_convergence(self, gbest_fitness, best_fitness_previous, convergence, idx_iteration):
        MAX_KONVERGEN = self.optimizer['params']['MAX_KONVERGEN']
        is_break = False
        if math.isclose(best_fitness_previous, gbest_fitness, rel_tol=1e-9, abs_tol=1e-9):
            convergence += 1
        else:
            convergence = 0
        print(
            f'Generation {idx_iteration + 1}, Best Fitness: {gbest_fitness}, Konvergen: {convergence}')

        if convergence == MAX_KONVERGEN:
            print(f'Convergence is reached = {MAX_KONVERGEN}')
            is_break = True

        best_fitness_previous = gbest_fitness
        return is_break, best_fitness_previous, convergence
