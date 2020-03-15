import itertools

import numpy as np

from tensorflow.keras.layers import Softmax

from transformers import (TFGPT2LMHeadModel, GPT2Tokenizer)


class GPT2:

    def __init__(self, model_name='distilgpt2'):
        """ Wrapper class for the hugging face GPT2 model"""
        self.model_name = model_name
        self.keras_model = None
        self.tokenizer = None
        self._initialise_model_and_tokenizer()

        self.max_seq_len = 16

    def _initialise_model_and_tokenizer(self):
        """
        Initialise model and tokenizer.
        ----------
        model_name_or_dir: str, optional
            either local dir containing the tf_model.h5, vocab.json, config.json, merges.txt OR the model
            shortcut name 'distilgpt2'
        """

        self.tokenizer = GPT2Tokenizer.from_pretrained(pretrained_model_name_or_path=self.model_name)
        self.tokenizer.pad_token = '[PAD]'
        self.tokenizer.decoder[self.tokenizer.pad_token_id] = self.tokenizer.pad_token
        self.keras_model = TFGPT2LMHeadModel.from_pretrained(self.model_name)

    def predict_next_word_prob(self, prompt, potential_words):
        """
        Returns a dict mapping each of the potential_words to the probability that it's the next word in the
        current_sentence
        ----------
        prompt: str

        Returns
        -------
        word_to_prob: dict
            dict mapping each of the potential words to it's predicted probability
        """
        word_to_prob = {}
        softmax = Softmax()

        potential_word_tokens = [self.tokenizer.encode(word) for word in potential_words]

        prompt_tokens = self.tokenizer.encode(prompt)
        initial_pred, past = self.keras_model(np.array(prompt_tokens), past=None)
        softmax_vector = softmax(initial_pred[..., -1, :]).numpy()  # gives probabilities for next token

        for word, word_tokens in zip(potential_words, potential_word_tokens):
            if len(word_tokens) == 1:
                word_to_prob[word] = softmax_vector[word_tokens[0]]
            else:
                joint_prob = 1
                pred, _ = self.keras_model(np.array(word_tokens), past=past)
                for idx, token in enumerate(word_tokens):
                    token_softmax = softmax(pred[..., idx, :]).numpy()
                    joint_prob *= token_softmax[token]
                word_to_prob[word] = joint_prob

        return word_to_prob


if __name__ == '__main__':
    """ testing"""
    _sentence = 'what is you favorite'
    _possible_words = ['food', 'thing', 'leg']
    _language_model = GPT2()
    word_to_prob = _language_model.predict_next_word_prob(_sentence, _possible_words)
    print(word_to_prob)
