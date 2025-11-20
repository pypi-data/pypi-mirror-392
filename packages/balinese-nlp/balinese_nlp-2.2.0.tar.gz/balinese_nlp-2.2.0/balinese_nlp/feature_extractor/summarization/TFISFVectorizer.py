from balinese_nlp.textpreprocessor import TextPreprocessor
from collections import defaultdict
import numpy as np
import math


class TfIsfVectorizer:
    """
    A custom TF-ISF vectorizer similar to scikit-learn's TfidfVectorizer,
    but designed for sentence-level feature extraction (Inverse Sentence Frequency).

    It supports unigrams, bigrams, trigrams, and custom n-grams.
    """

    def __init__(self, ngram_range=(1, 1), lowercase=True):
        """
        Initializes the TfIsfVectorizer.

        Args:
            ngram_range (tuple): The lower and upper boundary of the range of n-values for different
                                 word n-grams to be extracted. All values of n such that
                                 min_n <= n <= max_n will be used. For example, (1, 1) for unigrams,
                                 (1, 2) for unigrams and bigrams, (2, 2) for only bigrams.
            lowercase (bool): Convert all characters to lowercase before tokenizing.
            token_pattern (str): Regular expression to find tokens in a sentence.
                                 Default is r'(?u)\b\w\w+\b' which matches words of 2 or more
                                 alphanumeric characters.
        """
        self.ngram_range = ngram_range
        self.lowercase = lowercase
#         self.token_pattern = token_pattern
        self.vocabulary_ = {}  # Maps terms to their index
        self.idx_to_term = {}  # Maps index to term
        self.isf_scores = {}   # Stores calculated ISF scores for each term
        self.num_sentences_in_corpus = 0
        self.preprocessor = TextPreprocessor()

    def _tokenize(self, text):
        """
        Tokenizes the input text and generates n-grams.
        (This will be replaced by your balinese_word_tokenize for this project,
         but kept here for standalone TfIsfVectorizer functionality)
        """
        if self.lowercase:
            text = text.lower()
        # tokenize text using balinese word tokenizer
        tokens = self.preprocessor.balinese_word_tokenize(text)
        # tokens = re.findall(self.token_pattern, text)

        return tokens

    def _generate_n_grams(self, tokens):
        # Generate n-grams
        ngrams = []
        min_n, max_n = self.ngram_range
        for n in range(min_n, max_n + 1):
            if n == 1:
                ngrams.extend(tokens)
            else:
                for i in range(len(tokens) - n + 1):
                    ngram = ' '.join(tokens[i: i + n])
                    ngrams.append(ngram)
        return ngrams

    def fit(self, sentences, word_tokenizer_func=None):
        """
        Learns the vocabulary and calculates ISF scores from a list of sentences.

        Args:
            sentences (list): A list of strings, where each string is a sentence.
            word_tokenizer_func (callable, optional): A custom word tokenization function.
                                                     If None, uses internal _tokenize.
        """
        if not isinstance(sentences, list) or not all(isinstance(s, str) for s in sentences):
            raise TypeError("Input 'sentences' must be a list of strings.")

        self.num_sentences_in_corpus = len(sentences)

        # Build vocabulary and count sentence frequencies for ISF
        term_sentence_counts = defaultdict(int)

        current_vocab_idx = 0
        for sentence in sentences:
            # Use provided tokenizer if available, otherwise fallback to internal
            if word_tokenizer_func:
                tokens = word_tokenizer_func(sentence)
            else:
                tokens = self._tokenize(sentence)

            # Generate n-grams from the tokens
            ngrams_in_sentence = self._generate_n_grams(tokens)
            # Count only once per sentence for ISF
            unique_ngrams_in_sentence = set(ngrams_in_sentence)

            for term in unique_ngrams_in_sentence:
                term_sentence_counts[term] += 1
                if term not in self.vocabulary_:
                    self.vocabulary_[term] = current_vocab_idx
                    self.idx_to_term[current_vocab_idx] = term
                    current_vocab_idx += 1

        # Calculate ISF scores
        for term, count in term_sentence_counts.items():
            self.isf_scores[term] = math.log(
                (self.num_sentences_in_corpus + 1) / (count + 1)) + 1

        return self

    def transform(self, sentences, word_tokenizer_func=None):
        """
        Transforms a list of sentences into a TF-ISF matrix using the learned vocabulary and ISF scores.

        Args:
            sentences (list): A list of strings, where each string is a sentence.
            word_tokenizer_func (callable, optional): A custom word tokenization function.
                                                     If None, uses internal _tokenize.

        Returns:
            numpy.ndarray: A 2D array representing the TF-ISF matrix, where rows correspond to sentences
                           and columns correspond to terms in the vocabulary.
        """
        if not self.vocabulary_:
            raise RuntimeError("Vectorizer not fitted. Call 'fit' first.")
#         if not isinstance(sentences, list) or not all(isinstance(s, str) for s in sentences) or not isinstance(sentences, np.ndarray):
#             raise TypeError("Input 'sentences' must be a list of strings.")

        num_sentences_to_transform = len(sentences)
        vocab_size = len(self.vocabulary_)
        tf_isf_matrix = np.zeros((num_sentences_to_transform, vocab_size))

        for i, sentence in enumerate(sentences):
            if word_tokenizer_func:
                tokens = word_tokenizer_func(sentence)
            else:
                tokens = self._tokenize(sentence)

            ngrams_in_sentence = self._generate_n_grams(tokens)

            # Calculate TF (Term Frequency) for terms in the current sentence
            term_frequency_in_sentence = defaultdict(int)
            for term in ngrams_in_sentence:
                term_frequency_in_sentence[term] += 1

            # Populate the TF-ISF matrix
            for term, tf in term_frequency_in_sentence.items():
                if term in self.vocabulary_:  # Only consider terms in the learned vocabulary
                    idx = self.vocabulary_[term]
                    tf_isf_matrix[i, idx] = tf * self.isf_scores.get(term, 0)

        return tf_isf_matrix

    def fit_transform(self, sentences, word_tokenizer_func=None):
        """
        Fits the vectorizer to the sentences and then transforms them into a TF-ISF matrix.

        Args:
            sentences (list): A list of strings, where each string is a sentence.
            word_tokenizer_func (callable, optional): A custom word tokenization function.

        Returns:
            numpy.ndarray: A 2D array representing the TF-ISF matrix.
        """
        return self.fit(sentences, word_tokenizer_func).transform(sentences, word_tokenizer_func)

    def get_feature_names_out(self):
        """
        Returns a list of feature names (terms) ordered by their vocabulary index.

        Returns:
            list: A list of strings representing the terms in the vocabulary.
        """
        return [self.idx_to_term[i] for i in range(len(self.vocabulary_))]
