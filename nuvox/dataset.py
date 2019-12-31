
import numpy as np

from keras.preprocessing.text import text_to_word_sequence


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



