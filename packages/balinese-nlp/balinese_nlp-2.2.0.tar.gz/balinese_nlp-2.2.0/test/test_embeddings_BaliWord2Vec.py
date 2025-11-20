
from balinese_nlp.embeddings.gensims import BaliWord2Vec


pretrained_model = BaliWord2Vec(
    huggingface_repo_ID='satriabimantara/balinese_pretrained_wordembedding',
    pretrained_model_filename = '50_word2vec_model.bin'
    ).load_pretrained_model()
print(pretrained_model.wv['Satua'])
print(pretrained_model.wv.most_similar('Lutung'))