from balinese_nlp.postag.HMM import HiddenMarkovModelPOSTag


sentence = "I Dewa ngajeng nasi di paon."
hmm = HiddenMarkovModelPOSTag()

print(hmm.predict(sentence))

sentence = "Sang Lutung ajaka I kakua menek ke punyan biune."
print(hmm.predict(sentence))

