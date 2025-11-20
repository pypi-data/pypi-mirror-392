import pickle
import random

from balinese_nlp.summarization.extractive.metaheuristics.weights import (
    GreyWolfOptimizer, ParticleSwarmOptimization,
    MemoryBasedGreyWolfOptimizer, WalrusesOptimizationAlgorithm,
    EelGrouperOptimizer, SlimeMouldAlgorithm, ArchimedesOptimizationAlgorithm
)


# 1. Load  splitted dataset
filename = "./test_data/splitted_BaliSummarizationDataset.pkl"
BALISUMDATA = pickle.load(open(filename, 'rb'))
ROUND = 'round-1'

TRAIN_STATISTICAL_FEATURE_BALISUMDATA = BALISUMDATA['train_test']['STATISTICAL']['train']
TEST_STATISTICAL_FEATURE_BALISUMDATA = BALISUMDATA['train_test']['STATISTICAL']['test']


# total ada total 11 fitur untuk yang statistical-based features
n_features = TRAIN_STATISTICAL_FEATURE_BALISUMDATA[
    random.sample(TRAIN_STATISTICAL_FEATURE_BALISUMDATA.keys(), k=1)[0]
].shape[1]-2
METAHEURISTIC_HYPERPARAMETERS = {
    'N_AGENTS': 50,
    'MAX_ITERATIONS': 15,
    'FUNCTIONS': {
        'n_features': n_features,
        'compression_rate': 0.60,
        'objective': 'max',
        'metric': 'f1_macro'
    },
    'MAX_KONVERGEN': 15
}

# keep the remaining hyperparameters of MGWO using default values
mgwo_summarizer = ParticleSwarmOptimization(
    FUNCTIONS={
        'n_features': METAHEURISTIC_HYPERPARAMETERS['FUNCTIONS']['n_features'],
        'compression_rate': METAHEURISTIC_HYPERPARAMETERS['FUNCTIONS']['compression_rate'],
        'objective': METAHEURISTIC_HYPERPARAMETERS['FUNCTIONS']['objective'],
        'metric': METAHEURISTIC_HYPERPARAMETERS['FUNCTIONS']['metric']
    },
    MAX_KONVERGEN=METAHEURISTIC_HYPERPARAMETERS['MAX_KONVERGEN'],
    MAX_ITERATIONS=METAHEURISTIC_HYPERPARAMETERS['MAX_ITERATIONS']
)
# fit the extracted data
mgwo_summarizer.fit(TEST_STATISTICAL_FEATURE_BALISUMDATA)

# best agent is optimal feature weight combination from metaheuristic process
# optimal feature weight combination is in best_agent['position']
best_agent = mgwo_summarizer.solve()
print(best_agent)
