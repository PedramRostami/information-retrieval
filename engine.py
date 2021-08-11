import string
from patterns import normalization_patterns, unknown_nouns_stemmer_patterns, \
    verb_stemmer_patterns, plural_noun_stemmer_patterns
from dictionaries import search_in_per_nouns
import re
from os import listdir
from os.path import join, isfile
import json
import os
from sort import heapsort
from search import binary_search
import math
import heapq
from DocScore import DocScore
import io


class ParsingLinguistic:
    @staticmethod
    def normalization(document_text):
        punctuations = string.punctuation + '؛؟،'
        for punctuation in punctuations:
            document_text = document_text.replace(punctuation, ' ')
        for pattern_regex in normalization_patterns.keys():
            document_text = re.sub(pattern_regex, normalization_patterns[pattern_regex], document_text)
        return document_text

    @staticmethod
    def stemming(dictionaries, word):
        for pattern in unknown_nouns_stemmer_patterns:
            noun = re.sub(pattern, unknown_nouns_stemmer_patterns[pattern], word)
            if noun != word:
                if search_in_per_nouns(dictionaries.persian_nouns_dictionary, noun):
                    return noun
                if noun in dictionaries.arabic_nouns_list:
                    return noun
        if word in dictionaries.verbs_list:
            return word
        for pattern in verb_stemmer_patterns.keys():
            verb = re.sub(pattern, verb_stemmer_patterns[pattern], word)
            if verb != word:
                if verb in dictionaries.verbs_list:
                    return verb
        if word in dictionaries.plural_nouns_dictionary.keys():
            return dictionaries.plural_nouns_dictionary[word]
        for pattern in plural_noun_stemmer_patterns:
            singular = re.sub(pattern, plural_noun_stemmer_patterns[pattern], word)
            if singular != word:
                if search_in_per_nouns(dictionaries.persian_nouns_dictionary, singular):
                    return singular
                if singular in dictionaries.arabic_nouns_list:
                    return singular
        return word

    @staticmethod
    def tokenization(document_text):
        return document_text.split()

    @staticmethod
    def stop_words(inverted_index, stop_words_count):
        heapsort(inverted_index, lambda i, j: i['term_frequency'] > j['term_frequency'])
        stop_words = []
        for i in range(stop_words_count):
            stop_words.append(inverted_index[i]['term'])
        return stop_words


class Indexer:
    @staticmethod
    def doc_indexing(path):
        docs = {}
        id = 1
        for f in listdir(path):
            if isfile(join(path, f)):
                docs[id] = {
                    'path': join(path, f),
                    'terms': {}
                }
                id += 1
        return docs

    @staticmethod
    def cluster_doc_indexing(path, subjects, docs_count_in_each_subject):
        docs = {}
        id = 1
        for f in listdir(path):
            if isfile(join(path, f)):
                if subjects[(int) ((id - 1)/docs_count_in_each_subject)] not in docs.keys():
                    docs[subjects[(int) ((id - 1)/docs_count_in_each_subject)]] = {
                        'docs': {},
                        'centroid': []
                    }
                else:
                    docs[subjects[(int)((id - 1) / docs_count_in_each_subject)]]['docs'][id] = {
                       'path': join(path, f),
                        'terms': {}
                    }
                id += 1
        return docs

    @staticmethod
    def append_to_inverted_index(inverted_index, document_words, document_id):
        position = 1
        indexing_function = lambda array, i: array[i]['document_id']
        for word in document_words:
            if word in inverted_index.keys():
                posting_index = binary_search(inverted_index[word]['posting_list'], document_id, indexing_function)
                if posting_index is not None:
                    inverted_index[word]['term_frequency'] += 1
                    inverted_index[word]['posting_list'][posting_index]['positions'].append(position)
                    inverted_index[word]['posting_list'][posting_index]['frequency'] += 1
                else:
                    inverted_index[word]['term_frequency'] += 1
                    inverted_index[word]['document_frequency'] += 1
                    inverted_index[word]['posting_list'].append({
                        'document_id': document_id,
                        'positions': [position],
                        'frequency': 1
                    })
            else:
                inverted_index[word] = {
                    'document_frequency': 1,
                    'term_frequency': 1,
                    'posting_list': [
                        {
                            'document_id': document_id,
                            'positions': [position],
                            'frequency': 1
                        }
                    ],
                    'champion_list': []
                }
            position += 1
        return inverted_index

    @staticmethod
    def reformat_inverted_index(inverted_index):
        reformatted_inverted_index = []
        for key in inverted_index.keys():
            value = inverted_index[key]
            reformatted_inverted_index.append({
                'term': key,
                'document_frequency': value['document_frequency'],
                'term_frequency': value['term_frequency'],
                'posting_list': value['posting_list']
            })
        return reformatted_inverted_index

    @staticmethod
    def champion_list(inverted_index, champion_list_size):
        for term in inverted_index:
            temp = term['posting_list'].copy()
            temp = heapsort(temp, lambda i, j: i['frequency'] > j['frequency'])
            champion_list = []
            for i in range(min(len(temp), champion_list_size)):
                champion_list.append(temp[i]['document_id'])
            term['champion_list'] = champion_list
        return inverted_index

    @staticmethod
    def tfidf(inverted_index, docs):
        N = len(docs.keys())
        for term in inverted_index:
            for term_doc in term['posting_list']:
                tf = 1 + math.log10(term_doc['frequency'])
                idf = math.log10(N / term['document_frequency'])
                score = tf * idf
                # docs[term_doc['document_id']]['terms'].append({
                #     'term': term['term'],
                #     'score': score
                # })
                docs[term_doc['document_id']]['terms'][term['term']] = score
        return docs


class IO:
    @staticmethod
    def read_doc(path):
        f = io.open(path, mode='r', encoding='utf-8')
        # f = open(path, 'r')
        doc_text = f.read()
        f.close()
        return doc_text

    @staticmethod
    def save_data(inverted_index, dest_path):
        path_directories = dest_path.split(os.sep)
        for i in range(len(path_directories) - 1):
            current_path = ''
            for j in range(i + 1):
                if j < i:
                    current_path += path_directories[j] + os.sep
                else:
                    current_path += path_directories[j]
            if not os.path.exists(current_path):
                os.mkdir(current_path)
        saved_inverted_index = json.dumps(inverted_index)
        f = io.open(dest_path, mode='w', encoding='utf-8')
        f.write(saved_inverted_index)
        f.close()
        return None

    @staticmethod
    def load_data(src_path):
        f = open(src_path, 'r')
        inverted_index_str = f.read()
        f.close()
        inverted_index = json.loads(inverted_index_str)
        return inverted_index


class Scoring:
    @staticmethod
    def similarity(inverted_index, document_scores, query_terms, K):
        N = len(document_scores.keys())
        for query_term in query_terms.keys():
            tf = 1 + math.log10(query_terms[query_term]['term_frequency'])
            term = binary_search(inverted_index, query_term, lambda array, i: array[i]['term'])
            idf = 0.0
            if term is not None:
                idf = math.log10(N / inverted_index[term]['document_frequency'])
            query_terms[query_term]['tfidf'] = tf * idf

        scores = {}
        length = {}
        for query_term in query_terms.keys():
            term = binary_search(inverted_index, query_term, lambda array, i: array[i]['term'])
            if term is not None:
                for doc_id in inverted_index[term]['champion_list']:
                    if doc_id in scores.keys():
                        scores[doc_id] += document_scores[str(doc_id)]['terms'][inverted_index[term]['term']] * query_terms[query_term]['tfidf']
                        length[doc_id] += 1
                    else:
                        scores[doc_id] = document_scores[str(doc_id)]['terms'][inverted_index[term]['term']] * query_terms[query_term]['tfidf']
                        length[doc_id] = 1
        if len(scores) > 0:
            scores_list = []
            for i in scores.keys():
                heapq.heappush(scores_list, DocScore(i, scores[i] / length[i]))
                # scores_list.append(Doccore(i, scores[i] / length[i]))
            # heapq.heapify(scores_list)
            result = []
            for i in range(min(K, len(scores.keys()))):
                a = heapq.heappop(scores_list)
                result.append(a.get_doc_id())
            return result
        else:
            return None

    @staticmethod
    def centroids_similarity(inverted_index, document_scores, query_terms):
        N = len(document_scores.keys())
        for query_term in query_terms.keys():
            tf = 1 + math.log10(query_terms[query_term]['term_frequency'])
            term = binary_search(inverted_index, query_term, lambda array, i: array[i]['term'])
            idf = 0.0
            if term is not None:
                idf = math.log10((N + 1) / inverted_index[term]['document_frequency'])
            query_terms[query_term]['tfidf'] = tf * idf
        scores = {}
        length = {}
        for query_term in query_terms.keys():
            term = binary_search(inverted_index, query_term, lambda array, i: array[i]['term'])
            if term is not None:
                for doc_id in inverted_index[term]['champion_list']:
                    if doc_id in scores.keys():
                        scores[doc_id] += document_scores[str(doc_id)][inverted_index[term]['term']] * \
                                          query_terms[query_term]['tfidf']
                        length[doc_id] += 1
                    else:
                        scores[doc_id] = document_scores[str(doc_id)][inverted_index[term]['term']] * \
                                         query_terms[query_term]['tfidf']
                        length[doc_id] = 1
        if len(scores) > 0:
            scores_list = []
            for i in scores.keys():
                heapq.heappush(scores_list, DocScore(i, scores[i] / length[i]))
            result = heapq.heappop(scores_list)
            return result.get_doc_id()
        else:
            return None


class Cluster:
    @staticmethod
    def calculate_centroid(documents_vector, inverted_index):
        N = len(documents_vector.keys())
        centroid = {}
        for term in inverted_index:
            term_weight = 0
            for term_document in term['posting_list']:
                document_id = term_document['document_id']
                term_weight += documents_vector[document_id]['terms'][term['term']] / N
            centroid[term['term']] = term_weight
        return centroid