from balinese_nlp.ner.rule_based import NERLocation

sentence = "I Dewa Agung Panji Sakti lunga ka Peken Sanglah sareng Ida Ayu Mas Panji"
ner = NERLocation()
print(ner.predict(sentence))

print("="*30)
sentence = "Ida Panji ngengkebang taluh ring Dauh Umah"
print(ner.predict(sentence))


