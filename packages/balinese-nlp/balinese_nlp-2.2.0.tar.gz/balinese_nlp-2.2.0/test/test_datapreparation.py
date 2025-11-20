from balinese_nlp.narratives.characterner.datapreparation import DataPreparation
import pandas as pd

filename = "test_data/I Congeh Kacunduk Ratun Segara.txt"
with open(filename, 'r', encoding='cp1252') as file:
    # Membaca seluruh isi file ke dalam sebuah variabel.
    file_content = file.read()

dataprep = DataPreparation()
raw_df = pd.DataFrame({
    'story_title': ['ExampleStoryTitle1'],
    'story_text': [file_content]
})
# df_ner = dataprep.format_ner_tagset(raw_df)
# print(df_ner.head(20))

df_chars_identification = dataprep.format_character_identification_dataset(
    raw_df)
print(df_chars_identification['examplestorytitle1'].head(20))
