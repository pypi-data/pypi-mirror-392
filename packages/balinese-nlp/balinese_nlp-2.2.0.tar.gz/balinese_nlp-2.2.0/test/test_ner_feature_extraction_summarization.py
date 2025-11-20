import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from balinese_nlp.ner.rule_based import NERPerson, NERLocation, NERTimeExpression

from balinese_nlp.summarization.extractive.metaheuristics.weights import GreyWolfOptimizer
from balinese_nlp.feature_extractor.summarization import FeatureExtractor, TFISFVectorizer
from balinese_nlp.embeddings.gensims import BaliFastText

# 1. Load example splitted dataset
filename = "./test_data/BaliSumData.pkl"
BALISUMDATA = pickle.load(open(filename, 'rb'))


# # 2. Load and download pretrained Word Embedding models (FastText)
# pretrained_FastText_model = BaliFastText(
#     huggingface_repo_ID='satriabimantara/balinese_pretrained_wordembedding',
#     pretrained_model_bin_filename="100_fasttext_model.bin"
# ).load_pretrained_model()
title = 'lutung dadi pecalang'
test_doc = BALISUMDATA['satuabaliweb']['pre'][title]
sentences = test_doc['sentences']

feature_extractor = FeatureExtractor(
    pretrained_character_ner_model='satuaner'
)
feature_extractor.fit(sentences, title)

f1 = feature_extractor._extract_named_entity_density()
print(f1)

# sentence = "I Budi lan Anak Agung Ksatria munggah ring Jalan Ratna ring Rahina Redite"
# print(NERPerson().predict(sentence))
# print(NERLocation().predict(sentence))
# print(NERTimeExpression().predict(sentence))
