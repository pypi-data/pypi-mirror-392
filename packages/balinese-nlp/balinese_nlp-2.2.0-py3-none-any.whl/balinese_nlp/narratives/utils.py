from importlib import resources
import pickle


def load_pretrained_character_ner_model(modelversion='satuaner'):
    with resources.path(f'balinese_nlp.narratives.characterner.pretrained', f"{modelversion}.pkl") as p:
        filepath = str(p)

    pretrained_character_ner_model = pickle.load(open(filepath, 'rb'))
    return pretrained_character_ner_model
