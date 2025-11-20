from balinese_nlp.textpreprocessor import TextPreprocessor

# file for testing TextPreprocessor class
obj = TextPreprocessor()
text = "I Lutung ajake I Kakua ngalih amah-amahan diumah Gubernur N.I.C.A. Ditu lantas ia ajaka dadua mulung nyuh. Pekak-pekak ane nepukin ento lantas ngebug I Lutung ajak I Kakua 35 kali. Adepe buin Rp. 35.0900"
sentence = "I Lutung ajake I Kakua ngalih amah-amahan diumah Gubernur N.I.C.A."

# 1. Test word tokenization function
print('Test function 1: balinese_word_tokenization')
print(obj.balinese_word_tokenize(sentence))

# 1. Test word tokenization function
print('Test function 1: balinese_sentences_segmentation')
print(obj.balinese_sentences_segmentation(text))


# 1. Test convert special characters
print('Test Function: convert_ascii_sentence()')
text = "I mémé ajake ì lutung luas ka cårik!"
print(obj.convert_ascii_sentence(text))

# 1. Test Lemmatization function
print('Test Function: lemmatize_text')
print(obj.lemmatize_text(text))

# 1. Test remove stop words functions
print('Test Function: remove_stopwords')
print(obj.remove_stop_words(text))

# 1. Test Stemmer function
obj = TextPreprocessor()
sentence = "I Lutung ajaka I Kakua nyampat di sisin tukade. Ditu lantas memene ngaukin"
print('Test Function: stem_text')
print(obj.stem_text(sentence))
