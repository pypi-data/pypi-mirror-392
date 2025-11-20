import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from balinese_nlp.summarization.extractive.metaheuristics.weights import GreyWolfOptimizer
from balinese_nlp.feature_extractor.summarization import FeatureExtractor, TFISFVectorizer
from balinese_nlp.embeddings.gensims import BaliFastText

# 1. Load example splitted dataset
filename = "./test_data/BaliSumData.pkl"
BALISUMDATA = pickle.load(open(filename, 'rb'))

# 2. Load and download pretrained Word Embedding models (FastText)
pretrained_FastText_model = BaliFastText(
    huggingface_repo_ID='satriabimantara/balinese_pretrained_wordembedding',
    pretrained_model_bin_filename="100_fasttext_model.bin"
).load_pretrained_model()


# 3. Feature extraction untuk setiap teks bahasa bali pada BALISUMDATA, assume BALISUMDATA is preprocessed first!
def feature_extraction(BALISUMDATA):
    """Extracting some feature for extractive text summarization from BALISUMDATA

    Args:
        BALISUMDATA (dictionary): dictionary containing key-value, where key is story text and value containing dataframe for the story with extractive label (1: sentence will be included to the final summary, 0: else)
    """
    dfs = dict()  # variables containing extracted features for each df in BALISUMDATA
    for category_name, data_per_category in BALISUMDATA.items():
        for stage_annotation, data_set in data_per_category.items():
            for title, df in data_set.items():
                # remove items with empty sentence
                df.dropna(subset=['sentences'], inplace=True)
                df = df[
                    df['sentences'] != ''
                ]
                df['sentences'] = df['sentences'].apply(lambda x: str(x))

                # retrieve the sentence and extractive label from df
                sentences = df['sentences'].values
                labels = df['extractive_summary'].values

                # create object of feature extractor
                feature_extractor = FeatureExtractor()

                # fit the sentences and story title into object
                feature_extractor.fit(sentences, title)

                # extract some relevant features
                f1 = feature_extractor._extract_sentence_length()
                f2 = feature_extractor._extract_sentence_position()
                f3 = feature_extractor._extract_numerical_data()
                f10 = feature_extractor._extract_sentence_similarity_title_using_cosine(
                    pretrained_FastText_model)

                # concat all extracted features into single dataframe
                df_extracted_features = pd.concat((
                    f1, f2, f3, f10
                ), axis=1)
                df_extracted_features['labels'] = labels
                dfs[title] = df_extracted_features
    return dfs


dfs = feature_extraction(BALISUMDATA)

# 4. Training some of metaheuristics algorithms, e.g GWO
gwo_summarizer = GreyWolfOptimizer(
    FUNCTIONS={'n_features': 4, 'compression_rate': 0.57,
               'objective': 'max', 'metric': 'accuracy'}
)
# fit the extracted data
gwo_summarizer.fit(dfs)

# best agent is optimal feature weight combination from GWO process (will contain 4 in our case because we had retrieved four features in our feature_extraction function)
# optimal feature weight combination is in best_agent['position']
best_agent = gwo_summarizer.solve()
print(best_agent)


# 5. save the best_agent results for later purpose (inferencing)
filename = './pretrained/gwo_best_agent.pkl'
pickle.dump(best_agent, open(filename, 'wb'))
