import pandas as pd
import re
from dadmatools.normalizer import Normalizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import string
import fasttext

df=pd.read_csv("normalized_data.csv")

normalizer = Normalizer(
    full_cleaning=False,
    unify_chars=True,
    refine_punc_spacing=True,
    remove_extra_space=True,
    remove_puncs=False,
    remove_html=False,
    remove_stop_word=False,
    replace_email_with="<EMAIL>",
    replace_number_with=None,
    replace_url_with="",
    replace_mobile_number_with=None,
    replace_emoji_with=None,
    replace_home_number_with=None
)

def normalize_text(text):
    if pd.isnull(text) or not isinstance(text, str):
        return "" 
    return normalizer.normalize(text)

columns_to_normalize = ['mavad', 'instruction']  
for column in columns_to_normalize:
    df[column] = df[column].apply(normalize_text)



def preprocess_text_function(text):

  # Define the punctuation characters to be removed
  punctuations = string.punctuation

  # Remove the punctuations from the text
  text_without_punctuations = "".join([char for char in text if char not in punctuations])

  return text_without_punctuations



import fasttext

# TFIDF Class: a class to generate TFIDF for your docs and get top k relvant documents
class tfidf:
    
    def __init__(self, docs, ngram_range, bpe_model=None):
        self._min_df = 1
        self._max_df=0.8
        self._max_features=3000
        self._docs = docs
        self._bpe = bpe_model
        self._ngram_range = ngram_range
        if self._bpe:
            print("we are using bpe")
            self._model_tfidf = TfidfVectorizer(analyzer="word", min_df=self._min_df, max_df=self._max_df, max_features=self._max_features, ngram_range=self._ngram_range, tokenizer= lambda x: self.bpe_tokenizer(x))
        else:
            self._model_tfidf = TfidfVectorizer(analyzer="word", min_df=self._min_df, max_df=self._max_df, max_features=self._max_features, ngram_range=self._ngram_range)

        self._matrix = self._model_tfidf.fit_transform(docs)
        self._feature_names = self._model_tfidf.get_feature_names_out()

        model_skipgram = fasttext.load_model('farsi-dedup-skipgram.bin')
        self._tfidf_emb_vecs = np.vstack([model_skipgram.get_word_vector(word) for word in self._feature_names])


        self._docs_emb = np.dot(self._matrix.toarray(), self._tfidf_emb_vecs)


    def bpe_tokenizer(self, text):
        tokens = self._bpe.re.split(r'[و,،]', text)
        return tokens 
        

    def tfidf_top_k(self, query, k=2):
        
        query_tfidf = self._model_tfidf.transform([query])


        doc_scores = []


        for doc in self._matrix:
            doc_scores.append(cosine_similarity(query_tfidf, doc)[0][0])


        sorted_scores = sorted(enumerate(doc_scores), key=lambda ind_score: ind_score[1], reverse=True)
        if k!=-1:
            top_doc_indices = [ind for ind, score in sorted_scores[:k]]
        else:
            top_doc_indices=sorted_scores
        return top_doc_indices



    def tfidf_weighted_top_k(self, query, k=2):

        query_tfidf = self._model_tfidf.transform([query])
        query_emb = np.dot(query_tfidf.toarray(), self._tfidf_emb_vecs)

        doc_scores = []


        for doc in self._docs_emb:
            doc_scores.append(cosine_similarity(query_emb, doc.reshape(1, -1))[0][0])


        sorted_scores = sorted(enumerate(doc_scores), key=lambda ind_score: ind_score[1], reverse=True)
        if k!=-1:
            top_doc_indices = [ind for ind, score in sorted_scores[:k]]
        else:
            top_doc_indices = sorted_scores
        return top_doc_indices

ingredients_text = df["mavad"].apply(preprocess_text_function)

def return_df(df=df):
  return df

def return_list(query,sentence=ingredients_text):
  tf_obj_word_1_1 = tfidf(docs=ingredients_text , ngram_range=(1,1), bpe_model=None)
  result = tf_obj_word_1_1.tfidf_top_k(query, 5)
  return result




