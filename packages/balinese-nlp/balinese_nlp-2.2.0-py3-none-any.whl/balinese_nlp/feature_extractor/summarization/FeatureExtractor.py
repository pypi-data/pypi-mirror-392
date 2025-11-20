import pandas as pd
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans  # For sentence clustering
# For distance to centroid in clustering
from scipy.spatial.distance import euclidean
from sklearn.metrics import silhouette_score


from balinese_nlp.textpreprocessor import TextPreprocessor
from balinese_nlp.ner.rule_based import NERPerson, NERLocation
from balinese_nlp.postag.HMM import HiddenMarkovModelPOSTag
from balinese_nlp.narratives.utils import load_pretrained_character_ner_model


class FeatureExtractor:
    """Class for extract some relevant features for extractive Balinese text summarization
    """

    def __init__(self,
                 pretrained_character_ner_model='satuaner'
                 ):

        self.preprocessor = TextPreprocessor()
        self.personNER = NERPerson()
        self.locationNER = NERLocation()
        self.hmmModel = HiddenMarkovModelPOSTag()
        self.satuaNER = load_pretrained_character_ner_model(
            modelversion=pretrained_character_ner_model)

        self.sentences = None
        self.title = None
        self.IS_FIT = True

    def fit(self, sentences, title):
        # if not type(sentences) is np.ndarray or  not type(sentences) is list:
        #    raise TypeError("Input 'sentences' must be a list of strings or numpy nd array of strings.")

        # if not all(isinstance(s, str) for s in self.sentences):
        #    raise TypeError("Sentences element must be string")

        # preprocess the sentences first (without casefolding)
        self.sentences = self.__preprocess_sentences(sentences)
        self.title = title
        self.IS_FIT = True
        return self

    def __preprocess_sentences(self, sentences):
        preprocessed_sentences = list()
        for sent in sentences:
            preprocessed_sentence = self.preprocessor.convert_ascii_sentence(
                sent)
            preprocessed_sentence = self.preprocessor.remove_emoji_pattern(
                preprocessed_sentence)
            preprocessed_sentence = self.preprocessor.remove_non_ascii_punctuation(
                preprocessed_sentence)
            preprocessed_sentence = self.preprocessor.remove_special_punctuation(
                preprocessed_sentence)
            preprocessed_sentence = self.preprocessor.remove_urls_and_link(
                preprocessed_sentence)
            preprocessed_sentence = self.preprocessor.remove_whitespace_multiple(
                preprocessed_sentence)
            preprocessed_sentence = self.preprocessor.remove_leading_trailing_whitespace(
                preprocessed_sentence)

            # append results
            preprocessed_sentences.append(preprocessed_sentence)
        return preprocessed_sentences

    def _extract_sentence_length(self):
        """Extract sentence length feature from given list of sentence. This function calculate the percentage length of each sentence (divided by the longest sentence in the same document)

        Args:
            sentences (list): list of string sentence from a document
        """
        if not self.IS_FIT:
            raise ValueError('Please fit your sentences and title first!')

        sentences = self.sentences
        data_tokenized_sentences = list()
        extracted_features = list()
        longest_token_sentence = 0
        for sentence in sentences:
            tokenized_sentence = self.preprocessor.balinese_word_tokenize(
                sentence)
            n_token = len(tokenized_sentence)
            if n_token > longest_token_sentence:
                longest_token_sentence = n_token
            data_tokenized_sentences.append((n_token, tokenized_sentence))

        # apply feature extraction
        for data_tokenized_sentence in data_tokenized_sentences:
            feat = data_tokenized_sentence[0]/longest_token_sentence
            extracted_features.append(feat)

        # convert to dataframe
        df = pd.DataFrame(extracted_features, columns=['sentence_length'])
        return df

    def _extract_sentence_position(self):
        """Extract sentence position index from a document. The first two and last two sentences in the document will have index 1 and the others will have proporsional index

        Args:
            sentences (list): list of string sentence from a document
        """
        if not self.IS_FIT:
            raise ValueError('Please fit your sentences and title first!')

        sentences = self.sentences
        total_sentences = len(sentences)
        extracted_features = list()
        index_awal_akhir_document = [
            0, 1, total_sentences-2, total_sentences-1]

        for idx_sentence, sentence in enumerate(sentences):
            if idx_sentence in index_awal_akhir_document:
                extracted_features.append(1)
            else:
                feat = (total_sentences-(idx_sentence+1))/total_sentences
                extracted_features.append(feat)

        # convert to dataframe
        df = pd.DataFrame(extracted_features, columns=['sentence_position'])
        return df

    def _extract_numerical_data(self):
        """Extract percentage of numerical utterances in each sentence.

        Raises:
            ValueError: Please fit your sentences and title first in fit() method

        Returns:
            df (DataFrame): Extracted features formatted in dataframe
        """
        if not self.IS_FIT:
            raise ValueError('Please fit your sentences and title first!')

        sentences = self.sentences
        extracted_features = list()
        for sentence in sentences:
            # tokenized sentences
            tokenized_words = self.preprocessor.balinese_word_tokenize(
                sentence)

            numerical_count = 0
            total_tokens = len(tokenized_words)

            # calculate the percentage of any numerical data found
            for token in tokenized_words:
                # Regex to identify numerical tokens:
                # \d+ : matches one or more digits (e.g., "12", "2005")
                # |   : OR
                # \d+,\d+ : matches digits, comma, digits (e.g., "1,000", "3,14")
                # |
                # \d+\.\d+ : matches digits, dot, digits (e.g., "3.14", "20.000")
                # This pattern is robust for numbers that might have thousands separators or decimals.
                # It ensures the token is not just a single punctuation mark like '.'
                # Improved regex to handle "20.000" as a single number
                if re.fullmatch(r'\d+([.,]\d+)*', token):
                    numerical_count += 1

            percentage = (numerical_count / total_tokens)

            # append to extracted features
            extracted_features.append(percentage)

        # convert features to df
        df = pd.DataFrame(extracted_features, columns=[
                          'percentage_numerical_data'])
        return df

    def _extract_named_entity_density(self):
        """Extract percentage of Named Entities (Person, location, Character Named Entity) utterances in each sentence.

        Raises:
            ValueError: Please fit your sentences and title first in fit() method

        Returns:
            df (DataFrame): Extracted features formatted in dataframe
        """
        if not self.IS_FIT:
            raise ValueError('Please fit your sentences and title first!')

        sentences = self.sentences
        extracted_personNE_features = list()
        extracted_locationNE_features = list()
        extracted_characterNE_features = list()

        personNER = self.personNER
        locationNER = self.locationNER
        satuaNER = self.satuaNER

        # hitung total tokens dari the longest sentence
        longest_token_sentence = 0

        for sentence in sentences:
            tokenized_sentence = self.preprocessor.balinese_word_tokenize(
                sentence)
            n_token = len(tokenized_sentence)
            if n_token > longest_token_sentence:
                longest_token_sentence = n_token

            # extract person NE in each sentence
            n_personNE = len(personNER.predict(sentence))
            extracted_personNE_features.append(n_personNE)

            # extract location NE in each sentence
            pred_locationNE = [location for location in locationNER.predict(
                sentence).split('Location : ') if location != '']
            n_locationNE = len(pred_locationNE)
            extracted_locationNE_features.append(n_locationNE)

            # extract character NE in each sentence
            y_pred, token_with_predicted_chars = satuaNER.predict_sentence(
                sentence)
            predicted_characters = satuaNER.extract_predicted_characters_from_sentence(
                sentence, y_pred)['predicted_chars']
            n_predicted_characters = 0
            if predicted_characters is not np.nan:
                n_predicted_characters = len(predicted_characters.split('; '))
            extracted_characterNE_features.append(n_predicted_characters)

        # convert results to dataframe
        df = pd.DataFrame({
            'percent_personNE': extracted_personNE_features,
            'percent_locationNE': extracted_locationNE_features,
            'percent_characterNE': extracted_characterNE_features,
        })

        # calculate the percentage
        df['percent_personNE'] = df['percent_personNE']/longest_token_sentence
        df['percent_locationNE'] = df['percent_locationNE']/longest_token_sentence
        df['percent_characterNE'] = df['percent_characterNE'] / \
            longest_token_sentence

        return df

    def _extract_posttag_density_data(self):
        """Extract percentage of POS Tag (VB, MD, NN, NND, NNP, JJ) utterances in each sentence.

        Raises:
            ValueError: Please fit your sentences and title first in fit() method

        Returns:
            df (DataFrame): Extracted features formatted in dataframe
        """
        if not self.IS_FIT:
            raise ValueError('Please fit your sentences and title first!')

        sentences = self.sentences
        extracted_verb_features = list()  # verb, modal and auxiliary verb
        # noun, classifier, partitive, and measurement noun
        extracted_noun_features = list()
        extracted_propernoun_features = list()  # proper noun
        extracted_adjective_features = list()  # adjective

        hmmModel = self.hmmModel

        # hitung total tokens dari the longest sentence
        longest_token_sentence = 0
        for sentence in sentences:
            # calculate the longest sentence
            tokenized_sentence = hmmModel.predict(
                sentence).replace('\n', '').split(' ')
            n_token = len(tokenized_sentence)
            if n_token > longest_token_sentence:
                longest_token_sentence = n_token

            # extract POS Tag features
            verb_count = 0
            noun_count = 0
            propernoun_count = 0
            adjective_count = 0
            for token_with_tag in tokenized_sentence:
                tag = token_with_tag.split('/')[1]
                if tag in ['VB', 'MD']:
                    verb_count += 1
                elif tag in ['NN', 'NND']:
                    noun_count += 1
                elif tag in ['NNP']:
                    propernoun_count += 1
                elif tag in ['JJ']:
                    adjective_count += 1

            extracted_verb_features.append(verb_count)
            extracted_noun_features.append(noun_count)
            extracted_propernoun_features.append(propernoun_count)
            extracted_adjective_features.append(adjective_count)

        # convert results to dataframe
        df = pd.DataFrame({
            'percent_verbTag': extracted_verb_features,
            'percent_nounTag': extracted_noun_features,
            'percent_propernounTag': extracted_propernoun_features,
            'percent_adjectiveTag': extracted_adjective_features,
        })

        # calculate the percentage
        df['percent_verbTag'] = df['percent_verbTag']/longest_token_sentence
        df['percent_nounTag'] = df['percent_nounTag']/longest_token_sentence
        df['percent_propernounTag'] = df['percent_propernounTag'] / \
            longest_token_sentence
        df['percent_adjectiveTag'] = df['percent_adjectiveTag'] / \
            longest_token_sentence

        return df

    def _extract_sentence_similarity_title_using_jaccards(self):
        """
        Feature: Jaccard similarity of sentence words with title words.
        Formula: |Set(SentenceWords) INTERSECT Set(TitleWords)| / |Set(SentenceWords) UNION Set(TitleWords)|
        """
        if not self.IS_FIT:
            raise ValueError('Please fit your sentences and title first!')

        sentences = self.sentences
        title = self.title

        extracted_features = list()

        # tokenized title
        title_tokenized = self.preprocessor.balinese_word_tokenize(title)
        title_set = set(title_tokenized)

        for sentence in sentences:
            sentence = self.preprocessor.case_folding(sentence)

            # sentence tokenization
            sentence_tokenized = self.preprocessor.balinese_word_tokenize(
                sentence)
            sentence_set = set(sentence_tokenized)

            # calculate jaccard similarity
            intersection = len(sentence_set.intersection(title_set))
            union = len(sentence_set.union(title_set))
            jaccard = intersection/union if union > 0 else 0.0

            # append results
            extracted_features.append(jaccard)

        df = pd.DataFrame(extracted_features, columns=[
                          'words_appear_in_title'])
        return df

    def _extract_intrasimilarity_sentences_using_jaccardsim(self):
        """
        calculate average jaccard similarity Si with other sentences (exclude the Si)
        Feature: Average Jaccard similarity of a sentence with all other sentences in the document.
        Formula: Avg(JaccardSimilarity(S_i, S_j) for j != i)
        """
        if not self.IS_FIT:
            raise ValueError('Please fit your sentences and title first!')

        sentences = self.sentences
        extracted_features = list()

        for idx_i_sentence, sentence_i in enumerate(sentences):
            total_Si_jaccard = 0
            sentence_i = self.preprocessor.case_folding(sentence_i)
            sentence_i = set(
                self.preprocessor.balinese_word_tokenize(sentence_i))
            for idx_j_sentence, sentence_j in enumerate(sentences):
                # skip self-comparison
                if idx_i_sentence == idx_j_sentence:
                    continue

                sentence_j = self.preprocessor.case_folding(sentence_j)
                sentence_j = set(
                    self.preprocessor.balinese_word_tokenize(sentence_j))

                # calculate the jaccard from Si with other Sj sentences
                intersection = len(sentence_i.intersection(sentence_j))
                union = len(sentence_i.union(sentence_j))
                Si_jaccard = intersection/union if union > 0 else 0.0
                total_Si_jaccard += Si_jaccard

            # calculate average jaccard similarity from Si and append it to results variable
            avg_Si_jaccard = total_Si_jaccard/(len(sentences)-1)
            extracted_features.append(avg_Si_jaccard)

        # convert to
        df = pd.DataFrame(extracted_features, columns=[
                          'intra_sentence_similarity_words_appear'])

        return df

    def _extract_TFISF(self, pretrained_tfisf_vectorizer):
        """Extract TFISF features from each document using pretrained_tfisf_vectorizer

        Args:
            pretrained_tfisf_vectorizer (TfIsfVectorizer class): pretrained TF-ISF retrieved from using TfIsfVectorizer
        """
        if not self.IS_FIT:
            raise ValueError('Please fit your sentences and title first!')

        sentences = self.sentences
        # transform the sentences
        tf_isf_matrix = pretrained_tfisf_vectorizer.transform(sentences)

        # Create a DataFrame for better readability
        feature_names_unigram = pretrained_tfisf_vectorizer.get_feature_names_out()
        df = pd.DataFrame(tf_isf_matrix, columns=feature_names_unigram)

        return df

    def __sentence_to_embedding_vector(self, sentence, pretrained_wordembedding_model):
        """Convert sentence string to numerical vector using embedding model

        Args:
            sentence (str): string of input sentence
            pretrained_wordembedding_model (Gensim class): pretrained Gensim word embedding model

        Returns:
            numpy array: converted vector from input sentence in d-size 
        """
        VECTOR_SIZE = pretrained_wordembedding_model.vector_size
        PRETRAINED_WORD_EMBEDDING_MODEL = pretrained_wordembedding_model
        tokens = self.preprocessor.balinese_word_tokenize(sentence)
        word_vectors = [PRETRAINED_WORD_EMBEDDING_MODEL.wv[word]
                        for word in tokens if word in PRETRAINED_WORD_EMBEDDING_MODEL.wv]
        if word_vectors:
            return np.mean(word_vectors, axis=0)
        else:
            return np.zeros(VECTOR_SIZE)

    def _extract_avg_wordembedding_vectors(self, pretrained_wordembedding_model):
        """Extract average word embedding vectors for each sentence using pretrained word embedding model

        Args:
            pretrained_wordembedding_model (Gensim class): pretrained word embedding model for balinese retrieved from Gensim class
        """
        if not self.IS_FIT:
            raise ValueError('Please fit your sentences and title first!')
        sentences = self.sentences

        VECTOR_SIZE = pretrained_wordembedding_model.vector_size

        extracted_features = list()
        for sentence in sentences:
            sentence = self.preprocessor.case_folding(sentence)
            sentence_embeddingvector = self.__sentence_to_embedding_vector(
                sentence, pretrained_wordembedding_model)
            extracted_features.append(sentence_embeddingvector)

        # convert results into dataframe
        df = pd.DataFrame(extracted_features, columns=[
                          f'wv-d{i+1}' for i in range(VECTOR_SIZE)])
        return df

    def _extract_intrasimilarity_sentences_using_cosinesim(self, pretrained_wordembedding_model):
        """
        Feature: Average Cosine Similarity of a sentence vector with all other sentence vectors in the document. Sentence vectors was retrieved using word embedding vector
        Formula: Avg(CosineSimilarity(V_i, V_j) for j != i)

        Args:
            pretrained_wordembedding_model (Gensim class): pretrained word embedding model for balinese retrieved from Gensim class
        """
        if not self.IS_FIT:
            raise ValueError('Please fit your sentences and title first!')
        sentences = self.sentences
        document_size = len(sentences)
        PRETRAINED_WORD_EMBEDDING_MODEL = pretrained_wordembedding_model
        VECTOR_SIZE = PRETRAINED_WORD_EMBEDDING_MODEL.vector_size

        extracted_features = list()
        for idx_i_sentence, sentence_i in enumerate(sentences):
            total_Si_cosine_similarity = 0

            # convert Si to vector Vi
            sentence_i = self.preprocessor.case_folding(sentence_i)
            wordvector_Si = self.__sentence_to_embedding_vector(
                sentence_i, pretrained_wordembedding_model)

            # reshape Si vector
            wordvector_Si = wordvector_Si.reshape(1, -1)

            for idx_j_sentence, sentence_j in enumerate(sentences):
                # skip self-comparison
                if idx_i_sentence == idx_j_sentence:
                    continue

                # Convert Sj to vector Vj
                sentence_j = self.preprocessor.case_folding(sentence_j)
                wordvector_Sj = self.__sentence_to_embedding_vector(
                    sentence_j, pretrained_wordembedding_model)

                # reshape Sj vector
                wordvector_Sj = wordvector_Sj.reshape(1, -1)

                # calculate the cosine similarity between Vi and Vj
                sim = cosine_similarity(wordvector_Si, wordvector_Sj)[0][0]
                total_Si_cosine_similarity += sim

            # calculate average jaccard similarity from Si and append it to results variable
            avg_Si_cosine_similarity = total_Si_cosine_similarity / \
                (document_size-1)
            extracted_features.append(avg_Si_cosine_similarity)

        # convert to
        df = pd.DataFrame(extracted_features, columns=[
                          'intra_sentence_vector_similarity_cosine'])

        return df

    def _extract_sentence_similarity_title_using_cosine(self, pretrained_wordembedding_model):
        """
        Feature: Cosine similarity of a sentence vector with the title vector.
        Formula: CosineSimilarity(V_sentence, V_title)

        Args:
            pretrained_wordembedding_model (Gensim class): pretrained word embedding model for balinese retrieved from Gensim class
        """
        if not self.IS_FIT:
            raise ValueError('Please fit your sentences and title first!')
        sentences = self.sentences
        title = self.title

        extracted_features = list()

        # convert title to vector Vtitle
        title = self.preprocessor.case_folding(title)
        wordvector_title = self.__sentence_to_embedding_vector(
            title, pretrained_wordembedding_model)

        # reshape the vector
        wordvector_title = wordvector_title.reshape(1, -1)

        # hitung similarity Vtitle dengan setiap VSi
        for sentence in sentences:
            sentence = self.preprocessor.case_folding(sentence)
            wordvector_Si = self.__sentence_to_embedding_vector(
                sentence, pretrained_wordembedding_model)

            # reshape the vector
            wordvector_Si = wordvector_Si.reshape(1, -1)

            # hitung similarity VTitle dengan VSi
            sim = cosine_similarity(wordvector_Si, wordvector_title)[0][0]

            # append to extracted features
            extracted_features.append(sim)

        # create dataframe
        df = pd.DataFrame(extracted_features, columns=[
                          'sentence_title_vector_similarity'])

        return df

    def _extract_sentence_similarity_title_using_WMD(self, pretrained_wordembedding_model):
        """
        Feature: calculate sentence to title similarity using Word Mover Distance from the pretrained gensim word embedding models
        Formula: WMD(Sentence, Title).
        Karena nilai WMD asli sudah ditransformasi dengan rumus (1/(1+wmd)), maka hasil dataframe di atas diinterpretasikan sebagai 0 - 1 score dengan nilai mendekati 1 menyatakan makin similar antara dua kalimat yang dibandingkan

        Args:
            pretrained_wordembedding_model (Gensim class): pretrained word embedding model for balinese retrieved from Gensim class
        """
        if not self.IS_FIT:
            raise ValueError('Please fit your sentences and title first!')

        sentences = self.sentences
        title = self.title

        extracted_features = list()

        # convert title to tokens
        title = self.preprocessor.case_folding(title)
        tokens_title = self.preprocessor.balinese_word_tokenize(title)
        tokens_title = [
            token for token in tokens_title if token in pretrained_wordembedding_model.wv]

        for sentence in sentences:
            # convert sentence to tokens
            sentence = self.preprocessor.case_folding(sentence)
            tokens_sentence = self.preprocessor.balinese_word_tokenize(
                sentence)
            tokens_sentence = [
                token for token in tokens_sentence if token in pretrained_wordembedding_model.wv]

            # WMD requires words to be in the model's vocabulary
            if not tokens_sentence or not tokens_title:
                # Cannot compute WMD if no common words or empty
                extracted_features.append(0)

            wmdistance = pretrained_wordembedding_model.wv.wmdistance(
                tokens_sentence, tokens_title)
            # transform WMD score
            wmdistance = 1/(1+wmdistance)
            extracted_features.append(wmdistance)

        # create dataframe
        df = pd.DataFrame(extracted_features, columns=[
                          'sentence_title_wmd_similarity'])

        return df

    def __find_optimal_cluster_k(self, sentence_vectors, max_clusters_per_doc, min_sentences_for_clustering):
        """
        Finds the optimal number of clusters for a given set of sentence vectors
        using the Silhouette Score.
        """
        num_sentences = sentence_vectors.shape[0]
        # Handle cases with too few sentences or no valid vectors
        if num_sentences < min_sentences_for_clustering or sentence_vectors.shape[1] == 0:
            return 1  # Not enough sentences or no features for meaningful clustering

        # Check if all vectors are identical (Silhouette score won't work)
        if num_sentences > 1 and np.all([np.array_equal(sentence_vectors[0], v) for v in sentence_vectors[1:]]):
            return 1  # All sentences are identical, only 1 meaningful cluster

        # Define a range for k: from 2 up to min(num_sentences-1, max_clusters_per_doc)
        # Silhouette score requires at least 2 clusters (k >= 2) and k < num_sentences
        k_range = range(2, min(num_sentences, max_clusters_per_doc + 1))

        if not k_range:  # If k_range is empty (e.g., num_sentences is 1 or 2)
            return 1  # Default to 1 cluster

        best_k = 1
        best_score = -1.0  # Silhouette score ranges from -1 to 1

        for k in k_range:
            try:
                # n_init='auto' or explicit number (e.g., 10) for robust centroids
                kmeans = KMeans(n_clusters=k, random_state=42,
                                n_init=15, verbose=1, tol=1e6)
                kmeans.fit(sentence_vectors)

                # Silhouette score requires at least 2 distinct labels
                if len(set(kmeans.labels_)) > 1:
                    score = silhouette_score(sentence_vectors, kmeans.labels_)
                    if score > best_score:
                        best_score = score
                        best_k = k
            except Exception as e:
                # print(f"Warning: KMeans failed for k={k} with error: {e}. Skipping for this k.")
                continue
        return best_k

    def _extract_sentence_cluster_features(self, pretrained_wordembedding_model=None, pretrained_tfisf_vectorizer=None, use_embedding=True, algorithm='K-Means', max_clusters_per_doc=10, min_sentences_for_clustering=3):
        """Extract sentences cluster features such as cluster index and sentence to centroid distance using Euclidean distance

        Args:
            pretrained_wordembedding_model (Gensim class, optional): pretrained balinese word embedding model trained on Gensim class. Defaults to None.
            pretrained_tfisf_vectorizer (TfIsfVectorizer class, optional): pretrained TFISF vectorizer trained on TfIsfVectorizer class. Defaults to None.
            use_embedding (bool, optional): If True, the sentence vector extracted using word embedding, else using TfIsfVectorizer. Defaults to True. You must provide the pretrained_wordembedding_model if True. If False, you must provide the pretrained_tfisf_vectorizer.
            algorithm (str, optional): algorithm to use for clustering the sentences. Defaults to 'K-Means'.
            max_clusters_per_doc (int, optional): maximum cluster formed in the process. Defaults to 10.
            min_sentences_for_clustering (int, optional): minimum number of sentences to be included to run the clustering process. Defaults to 3.

        Raises:
            ValueError: _description_
        """
        if not self.IS_FIT:
            raise ValueError('Please fit your sentences and title first!')

        if pretrained_wordembedding_model is None and use_embedding:
            raise ValueError(
                'Please pass the pretrained word embedding model!')

        if pretrained_tfisf_vectorizer is None and not use_embedding:
            raise ValueError('Please pass the pretrained TF-ISF vectorizer!')

        sentences = self.sentences
        num_sentences_in_doc = len(sentences)

        # step 1: document vectorization

        if use_embedding:
            doc_vectors = self._extract_avg_wordembedding_vectors(
                pretrained_wordembedding_model).to_numpy()
        else:
            doc_vectors = pretrained_tfisf_vectorizer.transform(sentences)

        # step 2: applying clustering algorithm (find the optimal k cluster and run the local cluster algorithms)
        sentence_cluster_labels = [0] * num_sentences_in_doc
        sentence_cluster_distances = [0.0] * num_sentences_in_doc
        # menentukan optimal 'K' dan perform local clustering
        if doc_vectors.shape[0] >= min_sentences_for_clustering and doc_vectors.shape[1] > 0:
            optimal_k = self.__find_optimal_cluster_k(
                doc_vectors, max_clusters_per_doc, min_sentences_for_clustering)
            if optimal_k > 1:
                try:
                    kmeans_local = KMeans(
                        n_clusters=optimal_k, random_state=42, n_init=10)
                    kmeans_local.fit(doc_vectors)
                    sentence_cluster_labels = kmeans_local.labels_.tolist()

                    # Calculate distance to centroid for each sentence
                    for i, vec in enumerate(doc_vectors):
                        centroid = kmeans_local.cluster_centers_[
                            sentence_cluster_labels[i]]
                        # Use .flatten() to ensure 1D array for euclidean distance if vec is 2D
                        distance_to_centroid = euclidean(
                            vec.flatten(), centroid.flatten())
                        sentence_cluster_distances[i] = distance_to_centroid
                except Exception as e:
                    print(
                        f"Error during local KMeans with k={optimal_k}: {e}. Assigning default cluster features.")
            else:
                print(f"Optimal k for this document is 1. No meaningful clusters found.")
                # All sentences default to cluster 0, distance 0
        else:
            print(
                f"Not enough sentences ({num_sentences_in_doc}) or valid features for clustering. Assigning default cluster features.")

        # step 3: extract features for each sentence
        document_sentence_features = []
        for i, sentence_text in enumerate(sentences):
            features_list = []

            # 1. Distance to Cluster Centroid
            features_list.append(sentence_cluster_distances[i])

            # 2. One-Hot Encoded Local Cluster ID (fixed size)
            # Fixed size for the one-hot vector
            cluster_one_hot = np.zeros(max_clusters_per_doc)
            label_idx = sentence_cluster_labels[i]
            if 0 <= label_idx < max_clusters_per_doc:  # Ensure label fits within the one-hot size
                cluster_one_hot[label_idx] = 1
            features_list.extend(cluster_one_hot.tolist())

            document_sentence_features.append(np.array(features_list))

        # convert extracted features to dataframe
        df = pd.DataFrame(
            document_sentence_features,
            columns=['distance_cluster_centroid'] +
            [f"clusterID-{i}" for i in range(max_clusters_per_doc)]
        )
        return df
