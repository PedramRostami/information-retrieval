import pandas as pd
import re, io


def search_in_per_nouns(dictionary, word):
    if word[0] in dictionary.keys():
        if word in dictionary[word[0]]:
            return True
        else:
            return False
    else:
        return False


class Dictionaries:
    verbs_list = []
    plural_nouns_dictionary = {}
    persian_nouns_dictionary = {}
    arabic_nouns_list = []

    def __init__(self, verbs_dict_path, p_nouns_dict_path, per_nouns_dict_path, ar_nouns_dict_path):
        # create verbs list from past and present tense
        verbs_df = pd.read_csv(verbs_dict_path, encoding='utf-8-sig')
        past_verbs = verbs_df['past'].tolist()
        present_verbs = verbs_df['present'].tolist()
        self.verbs_list += past_verbs
        self.verbs_list += present_verbs
        self.verbs_list = list(set(self.verbs_list))

        # create plural nouns dictionary from Mokassar and singular forms of nouns
        plural_nouns_df = pd.read_csv(p_nouns_dict_path)
        for index, row in plural_nouns_df.iterrows():
            self.plural_nouns_dictionary[row['plural']] = row['singular']

        # create persian nouns dictionary
        # because of huge size of persian words list (44k words), here we use a
        # dictionary from mapping of first letter of words
        f = io.open(per_nouns_dict_path, mode='r', encoding='utf-8')
        text = f.read()
        words = list(set(re.split('\s', text)))
        for word in words:
            if len(word) > 0:
                if word[0] not in self.persian_nouns_dictionary.keys():
                    self.persian_nouns_dictionary[word[0]] = [word]
                else:
                    self.persian_nouns_dictionary[word[0]].append(word)
        f.close()

        # create arabic nouns list
        f = io.open(ar_nouns_dict_path, mode='r', encoding='utf-8')
        text = f.read()
        self.arabic_nouns_list = list(set(re.split('\s', text)))
        f.close()
