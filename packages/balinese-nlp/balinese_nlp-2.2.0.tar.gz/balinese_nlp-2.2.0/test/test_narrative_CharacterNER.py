from balinese_nlp.narratives.characterner import ConditionalRandomFields
from pandas import read_excel
from sklearn.metrics import classification_report

# load data
df = read_excel('./test_data/testCharacterNER.xlsx')
print(df)
crf = ConditionalRandomFields()
crf.fit(df)
y_pred = crf.predict(df)
y_true = crf.Y_TEST
print(crf.classification_report(y_true, y_pred, y_true,y_pred))