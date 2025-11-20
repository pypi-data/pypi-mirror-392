
from balinese_nlp.embeddings.gensims import BaliFastText


pretrained_model = BaliFastText(
    huggingface_repo_ID='satriabimantara/balinese_pretrained_wordembedding',
    pretrained_model_bin_filename = '50_fasttext_model.bin'
    ).load_pretrained_model()
print(pretrained_model.wv['Satua'])
print(pretrained_model.wv.most_similar('Lutung'))