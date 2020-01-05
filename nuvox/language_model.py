import numpy as np

import tensorflow as tf
from tensorflow.keras.layers import Softmax

from transformers import (TFGPT2LMHeadModel, GPT2Tokenizer)


class GPT2:

    """ My own wrapper class for the hugging face GPT2 model"""

    def __init__(self):

        self.keras_model = TFGPT2LMHeadModel.from_pretrained('/home/luka/PycharmProjects/nuvox/models/distilled_gpt2')
        print('\n\n Finished loading pretrained model')

        self.max_seq_len = 32
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.tokenizer.pad_token = '[PAD]'
        self.tokenizer.decoder[self.tokenizer.pad_token_id] = self.tokenizer.pad_token

        self.top_phrases_so_far = []  # list to store current most likely phrases in beam search

    def _encode(self, text):
        """ encode single string of text"""

        token_ids = self.tokenizer.encode(text, max_length=self.max_seq_len, pad_to_max_length=True)
        token_ids = np.array(token_ids)

        return token_ids

    def predict_probabilities(self, sentences):
        """
        Predict the probability that the next word in each sentence is each word in the vocabulary
        ----------
        sentences: list[str]

        Returns
        -------

        """
        batch_size = len(sentences)
        batch = np.zeros((batch_size, self.max_seq_len), dtype=int)
        for idx, sentence in enumerate(sentences):
            token_ids = self._encode(sentence)
            batch[idx] = token_ids

        pred = self.keras_model.predict_on_batch(batch)

        probabilities = np.zeros((batch_size, self.tokenizer.vocab_size))

        softmax = Softmax()
        for idx in range(batch_size):
            token_ids = batch[idx]
            idx_of_last_non_pad = np.argmin(token_ids != self.tokenizer.pad_token_id) -1
            logits = pred[0][idx][idx_of_last_non_pad]
            probs = softmax(logits)
            probabilities[idx] = probs.numpy()

        return probabilities


if __name__ == '__main__':

    _sentences = ['hello, what is your favourite', 'hello, what is your favourite game', 'hello what is your favourite game to']
    model = GPT2()
    _probs = model.predict_probabilities(_sentences)
    print('stop here')
