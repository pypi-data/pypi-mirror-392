import pickle
from numpy import nan
from balinese_nlp.narratives.utils import load_pretrained_satuaner_model

# satuaner = pickle.load(
#     open('./pretrained/satuaner_for_balinese_nlp.pkl', 'rb'))
satuaner = load_pretrained_satuaner_model()
sentence = "123 849 dabsh"
y_pred, token_with_predicted_chars = satuaner.predict_sentence(sentence)
predicted_characters = satuaner.extract_predicted_characters_from_sentence(
    sentence, y_pred)['predicted_chars']
n_predicted_characters = 0
if predicted_characters is not nan:
    n_predicted_characters = len(predicted_characters.split('; '))
print(n_predicted_characters)
