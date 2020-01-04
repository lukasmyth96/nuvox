import string

import numpy as np

from tensorflow.keras.preprocessing.text import text_to_word_sequence

from wordfreq import top_n_list


class Dataset:

    def __init__(self):

        self.vocab = []
        self.vocab_size = 0
        self.word_to_idx = {}

        self.word_seq = []
        self.num_examples = 0

    def fit_on_text(self, text):
        """ build vocab based on text"""

        self.word_seq = text_to_word_sequence(text)
        self.num_examples = len(self.word_seq)
        self.vocab = sorted(list(set(self.word_seq)))
        self.vocab_size = len(self.vocab)
        self.word_to_idx = {word: idx for idx, word in enumerate(self.vocab)}


def get_dataset_of_top_n_words(n, min_length=1):

    """ build and return a dataset containing the top n most frequent words
    Parameters
    ----------
    n: int
        num of words to get
    min_length: int
        min length of words to include
    """

    # TODO should fine better way of doing this
    blacklist = list(string.ascii_lowercase)
    blacklist.remove('a')
    blacklist.remove('i')

    words = top_n_list('en', 2*n)  # purposely get too many to allow for filtering

    # Filtering
    words = [w for w in words if w.isalpha()]
    words = [w for w in words if len(w) >= min_length]
    words = [w for w in words if w not in blacklist]

    top_n_words = words[:n -1]
    top_n_words.append('nuvox')  # gotta include this one

    dataset_obj = Dataset()
    dataset_obj.fit_on_text(' '.join(top_n_words))

    return dataset_obj

