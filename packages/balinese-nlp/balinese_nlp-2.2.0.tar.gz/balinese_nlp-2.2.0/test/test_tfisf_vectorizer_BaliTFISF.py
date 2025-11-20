
from balinese_nlp.embeddings.TFISF import BaliTFISF
from balinese_nlp.feature_extractor.summarization import FeatureExtractor
import pickle

tfisf_vectorizer_unigram = BaliTFISF(
    huggingface_repo_ID='satriabimantara/balinese-pretrained-vectorizer',
    pretrained_model_name='tfisf_unigram_vectorizer.pkl'
).load_pretrained_model()


filename = "./test_data/BaliSumData.pkl"
BALISUMDATA = pickle.load(open(filename, 'rb'))


# test pretrained TF-ISF untuk digunakan melakukan ekstraksi fitur
df = BALISUMDATA['satuabaliweb']['pre']['lutung dadi pecalang']
title = 'lutung dadi pecalang'
sentences = df['sentences'].values
labels = df['extractive_summary'].values

feature_extractor = FeatureExtractor()
feature_extractor.fit(sentences, title)
print(tfisf_vectorizer_unigram)
f8 = feature_extractor._extract_TFISF(tfisf_vectorizer_unigram)

print(f8)
