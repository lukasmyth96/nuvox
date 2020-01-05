import string

import numpy as np

from tensorflow.keras.preprocessing.text import text_to_word_sequence

from nuvox.utils.common import pickle_load


class Dataset:

    def __init__(self):

        self.vocab = []
        self.vocab_size = 0
        self.word_to_idx = {}
        self.idx_to_word = {}

        self.word_seq = []
        self.num_examples = 0

    def fit_on_text(self, text):
        """ build vocab based on text"""

        self.word_seq = text_to_word_sequence(text)
        self.num_examples = len(self.word_seq)
        self.vocab = sorted(list(set(self.word_seq)))
        self.vocab_size = len(self.vocab)
        self.word_to_idx = {word: idx for idx, word in enumerate(self.vocab)}
        self.idx_to_word = {idx: word for idx, word in enumerate(self.vocab)}


def build_dataset_from_vocab(vocab_file):

    """ build and return a dataset containing the top n most frequent words
    Parameters
    ----------
    vocab_file: intstr
        path to vocab pil file - will load as a list of words
    """

    vocab = pickle_load(vocab_file)

    dataset_obj = Dataset()
    dataset_obj.fit_on_text(' '.join(vocab))

    return dataset_obj

