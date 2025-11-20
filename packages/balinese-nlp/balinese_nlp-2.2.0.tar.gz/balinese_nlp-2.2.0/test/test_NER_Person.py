from balinese_nlp.ner.rule_based import NERPerson

sentence = "I Dewa Agung Panji Sakti lunga ka dura negara sareng Ida Ayu Mas Panji"
ner = NERPerson()
print(ner.predict(sentence))

print("="*30)
sentence = "Sang Arjuna nangun tapa sawireh mireng pawisik Sang Hyang Indra"
print(ner.predict(sentence))


