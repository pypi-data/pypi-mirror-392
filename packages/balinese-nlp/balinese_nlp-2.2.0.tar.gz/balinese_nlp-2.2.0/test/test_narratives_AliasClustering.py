from balinese_nlp.narratives.aliasclustering.rule_based import AliasClusteringRuleBased


model = AliasClusteringRuleBased()
predicted_characters_name = [
   "I Lutung", 'lutunge', 'Sang Lutung', 'I kakue', 'Sang Kakua', 'Kakuane', 'I Kakua'
]
model.fit(predicted_characters_name)
print(model.cluster())