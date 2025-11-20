from balinese_nlp.narratives.characterner import ConditionalRandomFields, BaseModel
from balinese_nlp.quoteattribution.rule_based import RuleBasedSentenceGrouping
from balinese_nlp.narratives.aliasclustering.rule_based import AliasClusteringRuleBased
from balinese_nlp.textpreprocessor import TextPreprocessor
from pandas import read_excel

# load data
# df = read_excel('./test_data/testCharacterNER.xlsx')
with open("./test_data/Anak Ririh.txt", 'r', encoding='utf-8') as file:
   preprocessed_story_anak_ririh = file.read()
# filter only two titles
# df = df[
#    df['StoryTitle'].isin(['anak_ririh'])
# ]
# df.reset_index(drop=True, inplace=True)
# print(df)


#1.  train CharacterNER model
# crf = ConditionalRandomFields()
# crf.fit(df)
# y_pred = crf.predict(df)
# y_true = crf.Y_TEST
# print(crf.classification_report(y_true, y_pred, y_true,y_pred))

#2. identify characters
# pred_characters_name = ConditionalRandomFields.identify_characters(preprocessed_story_anak_ririh, crf)
pred_characters_name = ['Pan Karsa', 'Pan Karta', 'pianakne', 'pianakne muani', 'Pianakne']
print(pred_characters_name)

#3. alias clustering
model_alias_clustering = AliasClusteringRuleBased()
model_alias_clustering.fit(pred_characters_name)
alias_groups = model_alias_clustering.cluster()
print(alias_groups)

#4. Rule-based SentenceGrouping
sentences = [sent.strip() for sent in preprocessed_story_anak_ririh.split("\\n") if sent!='']
print(sentences)
model_sentence_grouping = RuleBasedSentenceGrouping(add_characterization_column=False)
model_sentence_grouping.fit(sentences, alias_groups)
df_sentence_grouping = model_sentence_grouping.predict()
print(df_sentence_grouping)
for idx, data in df_sentence_grouping.iterrows():
   print(len(data['GroupedSentences']))