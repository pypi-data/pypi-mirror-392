from balinese_nlp.ner.rule_based import NERTimeExpression

sentence = "I Dewa Agung Panji Sakti lunga ka Peken Sanglah sareng Ida Ayu Mas Panji ring Soma 12 Desember 2025"
ner = NERTimeExpression()
print(ner.predict(sentence))

print("="*30)
sentence = "Ida Panji ngengkebang taluh sampun tigang bulan ring Dauh umahne"
print(ner.predict(sentence))


