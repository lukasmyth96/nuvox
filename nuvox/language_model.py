import itertools
import string

import numpy as np

import tensorflow as tf
from tensorflow.keras.layers import Softmax

from transformers import (TFGPT2LMHeadModel, GPT2Tokenizer)


class GPT2:

    """ My own wrapper class for the hugging face GPT2 model"""

    def __init__(self):

        self.keras_model = TFGPT2LMHeadModel.from_pretrained('/home/luka/PycharmProjects/nuvox/models/language_models/distilled_gpt2')
        print('\n\n Finished loading pretrained model')

        self.max_seq_len = 16
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.tokenizer.pad_token = '[PAD]'
        self.tokenizer.decoder[self.tokenizer.pad_token_id] = self.tokenizer.pad_token

        self.beam_width = 10
        self.top_phrases_so_far = ["."]   # list to store current most likely phrases in beam search

    def _encode(self, text):
        """ encode single string of text"""

        token_ids = self.tokenizer.encode(text, max_length=self.max_seq_len, pad_to_max_length=True)
        token_ids = np.array(token_ids)

        return token_ids

    def get_phrase_probabilities(self, sentences):
        """
        Get the probability of each sentence occuring
        ----------
        sentences: list[str]

        Returns
        -------
        sentence_probs: list
            list storing the probability for each sentence
        """

        batch_size = len(sentences)
        batch = np.zeros((batch_size, self.max_seq_len), dtype=int)
        for idx, sentence in enumerate(sentences):
            token_ids = self._encode(sentence)
            batch[idx] = token_ids

        pred = self.keras_model.predict(batch, batch_size=32)

        sentence_probs = []

        softmax = Softmax()
        for sentence_idx in range(batch_size):

            combined_probs = {}  # dict mapping each word in phrase to the probability that it would appear
            token_ids = batch[sentence_idx]
            idx_of_last_non_pad = np.argmin(token_ids != self.tokenizer.pad_token_id) -1

            for token_idx in range(idx_of_last_non_pad):  # skipping first because will be a fullstop
                logits = pred[0][sentence_idx][token_idx]
                softmax_vector = softmax(logits)

                # Get probability that the next word in the sequence would be the word that it is
                next_word_token_id = batch[sentence_idx, token_idx + 1]
                next_word = self.tokenizer.decoder[batch[sentence_idx, token_idx + 1]]  # get next
                next_word_prob = softmax_vector.numpy()[next_word_token_id]

                combined_probs[next_word] = next_word_prob

            # Calculate the probability for the entire sentence
            sentence_prob = np.product(np.array(list(combined_probs.values())))
            sentence_probs.append(sentence_prob)

        return sentence_probs

    def get_current_top_phrase(self):
        """ return current top phrase"""
        return self.top_phrases_so_far[0].lstrip('. ')

    def get_new_top_phrase(self, pred_words):

        """
        Return the new most likely phrase based on the top predictions for the latest word.

        Here we use the beam algorithm

        Parameters
        ----------
        pred_words: list[str]
            list of the top n possible words predicted by the trace model

        Returns
        -------
        new_phrase
        """

        phrases_to_query = [' '.join([existing_phrase, new_word])
                                for existing_phrase, new_word in itertools.product(self.top_phrases_so_far, pred_words)]

        phrase_probs = self.get_phrase_probabilities(phrases_to_query)

        top_phrase_indices = np.argsort(np.array(phrase_probs))[-self.beam_width:][::-1]

        self.top_phrases_so_far = [phrases_to_query[idx] for idx in top_phrase_indices]
        print('Top phrases so far: ', self.top_phrases_so_far)

        return self.top_phrases_so_far[0].lstrip('. ')  # return just top phrase

    def manually_add_word(self, word):
        """ manually add a single word to all of the current top phrases
        this is used for example when , . ? or a i are pressed on the display
        """
        current_top_phrases = self.top_phrases_so_far
        self.top_phrases_so_far = []
        for phrase in current_top_phrases:
            if word in string.punctuation:
                phrase += word
            else:
                phrase += ' {}'.format(word)
            self.top_phrases_so_far.append(phrase)

    def reset(self):
        """ Reset top phrases - called when clear button is called from display"""
        self.top_phrases_so_far = ['.']

    def delete_last_word(self):
        """ Delete last word from all top phrases - called when del button is pressed on display"""

        current_top_phrases = self.top_phrases_so_far
        self.top_phrases_so_far = []
        for phrase in current_top_phrases:
            words = phrase.split(' ')
            new_phrase = ' '.join(words[:-1])
            self.top_phrases_so_far.append(new_phrase)


if __name__ == '__main__':
    """ testing"""
    _sentences = ['. Hello, what is your', '. Hello, what it your', '. Hello, what if your']
    _next_words = ['favourite', 'only', 'the']
    model = GPT2()
    model.beam_width = 3
    model.top_phrases_so_far = _sentences
    new_top_phrase = model.get_new_top_phrase(_next_words)
    print('stop here')
