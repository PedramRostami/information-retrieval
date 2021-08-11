from engine import ParsingLinguistic,IO, Indexer, Cluster
from dictionaries import Dictionaries
import time
import os
from sort import heapsort
from engine import Scoring
import search


def preparation():
    ts = time.time()
    docs = Indexer.doc_indexing('docs-phase2/')
    dictionaries = Dictionaries('dicts/verbs.csv', 'dicts/plurals.csv',
                                'dicts/farsi_dictionary.txt', 'dicts/arabic_dictionary.txt')
    posting_list = {}
    for doc_id in docs.keys():
        doc_text = IO.read_doc(docs[doc_id]['path'])
        doc_text = ParsingLinguistic.normalization(doc_text)
        doc_tokens = ParsingLinguistic.tokenization(doc_text)
        doc_words = []
        for word in doc_tokens:
            doc_words.append(ParsingLinguistic.stemming(dictionaries, word))
        posting_list = Indexer.append_to_inverted_index(posting_list, doc_words, doc_id)
    inverted_index = Indexer.reformat_inverted_index(posting_list)
    stop_words = ParsingLinguistic.stop_words(inverted_index, 12)
    sorted_inverted_index = heapsort(inverted_index, lambda i, j: i['term'] < j['term'])
    full_inverted_index = Indexer.champion_list(sorted_inverted_index, 15)
    docs = Indexer.tfidf(full_inverted_index, docs)
    # print('hi')
    IO.save_data(sorted_inverted_index, 'preparation-data' + os.sep + 'inverted_index.txt')
    IO.save_data(stop_words, 'preparation-data' + os.sep + 'stop-words.txt')
    IO.save_data(docs, 'preparation-data' + os.sep + 'docs_tfidf.txt')
    return True


def search_engine():
    docs = Indexer.doc_indexing('docs-phase2/')
    dictionaries = Dictionaries('dicts/verbs.csv', 'dicts/plurals.csv',
                                'dicts/farsi_dictionary.txt', 'dicts/arabic_dictionary.txt')
    inverted_index = IO.load_data('preparation-data/inverted_index.txt')
    stop_words = IO.load_data('preparation-data/stop-words.txt')
    docs_tfidf = IO.load_data('preparation-data/docs_tfidf.txt')
    K = 10
    while True:
        query = input('enter query : ')
        start = time.time()
        query = ' ' + query + ' '
        normalized_query = ParsingLinguistic.normalization(query)
        query_tokens = ParsingLinguistic.tokenization(normalized_query)
        query_terms = []
        for word in query_tokens:
            stemmed_word = ParsingLinguistic.stemming(dictionaries, word)
            if stemmed_word not in stop_words:
                query_terms.append(stemmed_word)
        query_terms = Indexer.append_to_inverted_index({}, query_terms, -1)
        results = Scoring.similarity(inverted_index, docs_tfidf, query_terms, K)
        for result in results:
            print(docs_tfidf[str(result)]['path'], end=' -- ')
        print('')
        end = time.time()
        print('time : {}'.format(str(end - start)))
        # print(results)


def clustering_preparation():
    data = {
        'math': {
            'docs': None,
            'inverted_index': None,
            'stop_words': None,
            'centroid': None,
            'docs_path': 'docs/math/'
        },
        'physics': {
            'docs': None,
            'inverted_index': None,
            'stop_words': None,
            'centroid': None,
            'docs_path': 'docs/physics/'
        },
        'health': {
            'docs': None,
            'inverted_index': None,
            'stop_words': None,
            'centroid': None,
            'docs_path': 'docs/health/'
        },
        'history': {
            'docs': None,
            'inverted_index': None,
            'stop_words': None,
            'centroid': None,
            'docs_path': 'docs/history/'
        },
        'technology': {
            'docs': None,
            'inverted_index': None,
            'stop_words': None,
            'centroid': None,
            'docs_path': 'docs/technology/'
        }
    }
    dictionaries = Dictionaries('dicts/verbs.csv', 'dicts/plurals.csv',
                                'dicts/farsi_dictionary.txt', 'dicts/arabic_dictionary.txt')
    for subject in data.keys():
        docs_path = data[subject]['docs_path']
        docs = Indexer.doc_indexing(docs_path)
        posting_list = {}
        for doc_id in docs.keys():
            doc_text = IO.read_doc(docs[doc_id]['path'])
            doc_text = ParsingLinguistic.normalization(doc_text)
            doc_tokens = ParsingLinguistic.tokenization(doc_text)
            doc_words = []
            for word in doc_tokens:
                doc_words.append(ParsingLinguistic.stemming(dictionaries, word))
            posting_list = Indexer.append_to_inverted_index(posting_list, doc_words, doc_id)
        inverted_index = Indexer.reformat_inverted_index(posting_list)
        stop_words = ParsingLinguistic.stop_words(inverted_index, 12)
        sorted_inverted_index = heapsort(inverted_index, lambda i, j: i['term'] < j['term'])
        full_inverted_index = Indexer.champion_list(sorted_inverted_index, 15)
        data[subject]['inverted_index'] = full_inverted_index
        docs = Indexer.tfidf(full_inverted_index, docs)
        data[subject]['docs'] = docs
        centroid = Cluster.calculate_centroid(docs, full_inverted_index)
        data[subject]['centroid'] = centroid
        data[subject]['stop_words'] = stop_words

    IO.save_data(data, 'preparation-data' + os.sep + 'data.txt')
    return True


def cluster_search_engine():
    data = IO.load_data('preparation-data' + os.sep + 'data.txt')
    centroids = {}
    centroids_inverted_index = {}
    dictionaries = Dictionaries('dicts/verbs.csv', 'dicts/plurals.csv',
                                'dicts/farsi_dictionary.txt', 'dicts/arabic_dictionary.txt')
    for subject in data.keys():
        centroids[subject] = data[subject]['centroid']
        Indexer.append_to_inverted_index(centroids_inverted_index, data[subject]['centroid'].keys(), subject)
    centroids_inverted_index = Indexer.reformat_inverted_index(centroids_inverted_index)
    centroids_inverted_index = heapsort(centroids_inverted_index, lambda i, j: i['term'] < j['term'])
    centroids_inverted_index = Indexer.champion_list(centroids_inverted_index, 15)
    while True:
        start = time.time()
        query = input('enter query : ')
        query = ' ' + query + ' '
        normalized_query = ParsingLinguistic.normalization(query)
        query_tokens = ParsingLinguistic.tokenization(normalized_query)
        query_terms = []
        for word in query_tokens:
            stemmed_word = ParsingLinguistic.stemming(dictionaries, word)
            query_terms.append(stemmed_word)
        query_terms = Indexer.append_to_inverted_index({}, query_terms, -1)
        subject_result = Scoring.centroids_similarity(centroids_inverted_index, centroids, query_terms)
        print(subject_result)
        K = 10
        results = Scoring.similarity(data[subject_result]['inverted_index'], data[subject_result]['docs'], query_terms, K)
        for result in results:
            print(data[subject_result]['docs'][str(result)]['path'], end=' - ')
        print()
        end = time.time()
        print('time : {}'.format(str(end - start)))


if __name__ == '__main__':
    # clustering_preparation()
    # cluster_search_engine()
    # start = time.time()
    # preparation()
    # end = time.time()
    # print(end - start)
    search_engine()
    cluster_search_engine()






