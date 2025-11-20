# Suppose we have already trained our metaheuristics models for weights optimization and are going to summarize example story using the optimal feature weights combination

import pickle
import pandas as pd
import numpy as np
from balinese_nlp.textpreprocessor import TextPreprocessor
from balinese_nlp.feature_extractor.summarization import FeatureExtractor
from balinese_nlp.embeddings.gensims import BaliFastText

# 1. Load our best_agent
filename = "./pretrained/gwo_best_agent.pkl"
gwo_best_agent = pickle.load(open(filename, 'rb'))['position']

# 2. Load example story input: I Congeh Kacunduk Ratun Segara.txt
# story_title = 'I Congeh Kacunduk Ratun Segara'
story_title = 'Anak Ririh'
filename = f"test_data/{story_title}.txt"
with open(filename, 'r', encoding='cp1252') as file:
    # Membaca seluruh isi file ke dalam sebuah variabel.
    story_example = file.read()


# 3. Preprocess and prepare the data first
preprocessor = TextPreprocessor()
segmented_sentences = preprocessor.balinese_sentences_segmentation(
    story_example
)
print(len(segmented_sentences))

# 4. Extract the features
# NOTES! You must extract the features as same as your pretrained model have learned
# If in the previous training your model use 4 features: f1, f2, f3, f10, then you must extract exactly four features
feature_extractor = FeatureExtractor()

# fit the sentences and story title into object
feature_extractor.fit(segmented_sentences, story_title)

# extract some relevant features
pretrained_FastText_model = BaliFastText(
    huggingface_repo_ID='satriabimantara/balinese_pretrained_wordembedding',
    pretrained_model_bin_filename="100_fasttext_model.bin"
).load_pretrained_model()

f1 = feature_extractor._extract_sentence_length()
f2 = feature_extractor._extract_sentence_position()
f3 = feature_extractor._extract_numerical_data()
f10 = feature_extractor._extract_sentence_similarity_title_using_cosine(
    pretrained_FastText_model)

# concat into single DataFrame
df_extracted_features = pd.concat((
    f1, f2, f3, f10
), axis=1)

# 5. Retrieve the final important sentences as extractive summary
# Dot product each sentence feature with their corresponding weight features from best_agent


def extract_final_summary(segmented_sentences, df_extracted_features, optimal_feature_weights, compression_rate=0.5):
    """Extract the final extractive summary using optimal feature weights from metaheuristics

    Args:
        df_extracted_features (dataframe): DataFrame containing extracted feature from any given story text
        optimal_feature_weights (np.array): optimal feature weights combinations. The shape is the same with your number of extracted features, where each value are fall between 0 to 1.
        compression_rate(float): percentage number of sentences will be deleted from total sentences
    """
    X = df_extracted_features.values
    n_sentences = X.shape[0]

    # hitung dot product dari agent weights dengan matrix df extraksi fitur. (1 x N).(N x number of sentences) where N is number of extracted features
    total_sentences_score = np.dot(optimal_feature_weights, X.T)

    # susun ke dalam format dataframe (dimensi ke-1 adalah posisi indeks kalimat dalam teks, dimensi ke-2 hasil total scores weight)
    df_sentences_score = pd.DataFrame(np.array([
        [idx_sentence for idx_sentence in range(n_sentences)],
        total_sentences_score,
    ]).T, columns=['sentence_idx', 'total_sentence_score'])

    # sorting sentences berdasarkan total sentence score dikalikan weights dari agent (descending)
    df_sentences_score.sort_values(
        by='total_sentence_score', ascending=False, inplace=True)

    # extract Top-N sentences as system summary
    number_of_compressed_sentences = (compression_rate*n_sentences)
    top_n_extracted_sentences = int(np.ceil(n_sentences -
                                            number_of_compressed_sentences))
    sentence_indexes_summary = df_sentences_score.head(
        top_n_extracted_sentences)['sentence_idx'].astype(int)
    sentence_indexes_summary = sentence_indexes_summary.sort_values(
        ascending=True).values

    # extract sentence summary from their indexes
    final_summary = " ".join(
        segmented_sentences[i] for i in sentence_indexes_summary
    )
    return final_summary


# Now you can retrieve the final summary from any given text
final_summary = extract_final_summary(
    segmented_sentences,
    df_extracted_features,
    gwo_best_agent,
    compression_rate=0.5  # please using the values between 0.5 to 0.9
)

print('\t======== TEXT INPUT ===============')
print(story_example)
print('='*30)
print()
print('\t======== HASIL RINGKASAN DENGAN GWO DAN 4 FITUR, COMPRESSION RATE 0.5 ===============')
print(final_summary)
print('='*30)
