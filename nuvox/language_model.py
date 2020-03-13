import itertools
import math

import numpy as np

import tensorflow as tf
from tensorflow.keras.layers import Softmax

from transformers import (TFGPT2LMHeadModel, GPT2Tokenizer)


class GPT2:

    """ My own wrapper class for the hugging face GPT2 model"""

    def __init__(self):

        self.keras_model = None

        self.max_seq_len = 16

        self.tokenizer = None  # set when load_model is called

        self.beam_width = 10
        self.top_phrases_so_far = ["."]   # list to store current most likely phrases in beam search

    def load_model(self, model_name_or_dir='distilgpt2'):
        """
        load model and tokenizer.
        ----------
        model_name_or_dir: str, optional
            either local dir containing the tf_model.h5, vocab.json, config.json, merges.txt OR the model
            shortcut name 'distilgpt2'
        """

        self.tokenizer = GPT2Tokenizer.from_pretrained(pretrained_model_name_or_path=model_name_or_dir)
        self.tokenizer.pad_token = '[PAD]'
        self.tokenizer.decoder[self.tokenizer.pad_token_id] = self.tokenizer.pad_token
        self.keras_model = TFGPT2LMHeadModel.from_pretrained(model_name_or_dir)
        self.get_phrase_probabilities('warm up')  # to prevent first real prediction being slow
        print('\n\n Finished loading pretrained model')

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

        pred = self.keras_model.predict(batch, batch_size=self.beam_width**2)

        sentence_probs = []

        softmax = Softmax()
        for sentence_idx in range(batch_size):

            if sentence_idx == len(sentences):
                break

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

    def get_new_top_phrases(self, pred_words):

        """
        Return the new most likely phrase based on the top predictions for the latest word.

        Here we use the beam algorithm

        Parameters
        ----------
        pred_words: list[str]
            list of the top n possible words predicted by the trace model

        Returns
        -------
        top_phrases: list[str]
            list of top n=beam_width phrases

        """

        phrases_to_query = [' '.join([existing_phrase, new_word])
                                for existing_phrase, new_word in itertools.product(self.top_phrases_so_far, pred_words)]

        phrase_probs = self.get_phrase_probabilities(phrases_to_query)

        top_phrase_indices = np.argsort(np.array(phrase_probs))[-self.beam_width:][::-1]

        self.top_phrases_so_far = [phrases_to_query[idx] for idx in top_phrase_indices]

        top_phrases = [phrase.lstrip('. ') for phrase in self.top_phrases_so_far]
        print('New top phrases are: ', top_phrases)

        return top_phrases

    def get_current_top_phrases(self):
        """ return current top phrase"""
        return [phrase.lstrip('. ') for phrase in self.top_phrases_so_far]

    def manually_add_word(self, word, sep=' '):
        """ manually add a text to all of the current top phrases -
        """
        current_top_phrases = self.top_phrases_so_far
        self.top_phrases_so_far = []
        for phrase in current_top_phrases:
            phrase = sep.join([phrase, word])
            self.top_phrases_so_far.append(phrase)

    def reset(self):
        """ Reset top phrases - called when clear button is called from display"""
        self.top_phrases_so_far = ['.']

    def set_top_phrases(self, phrases):

        self.top_phrases_so_far = ['. {}'.format(phrase) for phrase in phrases]


if __name__ == '__main__':
    """ testing"""
    _sentences = ['. Hello, what is your']
    _next_words = ['favourite', 'only', 'the']
    _language_model = GPT2()
    _language_model.load_model()
    _language_model.beam_width = 3
    _language_model.top_phrases_so_far = _sentences
    _language_model.get_new_top_phrases(pred_words=_next_words)
    print('stop here')
