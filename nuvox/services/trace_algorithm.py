from collections import OrderedDict
import itertools

import numpy as np

from nuvox.utils.io import pickle_load


class TraceAlgorithm:

    def __init__(self, vocab_path, max_count):
        """
        The trace algorithm is responsible for identifying a set of potential intended words given the sequence of
        key ids that were in focus at each interval during the swype
        Parameters
        ----------
        vocab_path: str
            path to a pkl file containing a dict mapping from discrete representation e.g. '3246' to the set of
            possible words for that discrete repr
        max_count: int
            maximum number of times a single key can be in focus in a row
            equal to int(config.REQ_DWELL_TIME / config.GAZE_INTERVAL)
        """

        self.vocab_path = vocab_path
        self.discrete_repr_to_words = pickle_load(vocab_path)
        self.max_count = max_count

    def get_possible_word_to_trace_prob(self, key_id_sequence):
        """
        Returns a dict mapping all possible intended words to the probability of that word being intended based on the
        trace ONLY - NO language modelling occurs at this stage
        Parameters
        ----------
        key_id_sequence: list[str]
            list of key ids that have been recorded in a single swype

        Returns
        -------
        possible_word_to_prob: dict
            dict mapping a possible word to it's probability based solely on the trace - NOT how likely that word is
            to appear in the current context
        """

        start_key, end_key, intermediate_keys = self.get_start_end_intermediate_keys(key_id_sequence)

        if intermediate_keys:
            grouped_intermediate_keys, counts = self.get_grouped_intermediate_keys_with_counts(intermediate_keys)

            # get dict mapping all possible sub-seq of intermediate keys to it's probability
            discrete_repr_to_prob = self.get_discrete_repr_to_prob(start_key, end_key, grouped_intermediate_keys, counts)
        else:
            if start_key == end_key:
                discrete_repr = start_key
            else:
                discrete_repr = ''.join([start_key, end_key])
            discrete_repr_to_prob = {discrete_repr: 1.0}

        # possible word to prob
        possible_word_to_prob = {}
        for discrete_repr, prob in discrete_repr_to_prob.items():
            words = self.discrete_repr_to_words.get(discrete_repr, [])
            possible_word_to_prob.update({word: prob for word in words})

        # Normalize so probs sum to 1
        possible_word_to_prob = self.normalize_word_to_prob(possible_word_to_prob)

        # Order so that most likely appear first
        possible_word_to_prob = OrderedDict({w: p for w, p in sorted(possible_word_to_prob.items(), key=lambda item: item[1], reverse=True)})

        return possible_word_to_prob

    @staticmethod
    def get_start_end_intermediate_keys(key_id_sequence):
        """
        Split key sequence into start_key, end_key and intermediate_keys
        e.g. [3, 3, 3, 2, 2 ,4, 4, 6, 6, 6] -> (3, 6, [2, 2, 4, 4])
        Parameters
        ----------
        key_id_sequence: list[str]

        Returns
        -------
        start_key: str
        end_key: str
        intermediate_keys: list[str]
        """
        start_key = key_id_sequence[0]
        end_key = key_id_sequence[-1]

        intermediate_keys = []
        try:
            last_leading_start_key_idx = next(idx for idx, key_id in enumerate(key_id_sequence) if key_id != start_key)
            first_trailing_end_key_idx = len(key_id_sequence) - next(idx for idx, key_id in enumerate(reversed(key_id_sequence)) if key_id != end_key)
            intermediate_keys = key_id_sequence[last_leading_start_key_idx: first_trailing_end_key_idx]
        except StopIteration:
            pass

        return start_key, end_key, intermediate_keys

    @staticmethod
    def get_grouped_intermediate_keys_with_counts(intermediate_keys):
        """
        returns a group list of intermediate keys and the counts
        e.g. [2, 2, 1, 4, 4, 2] --> ([2, 1, 4, 2], [2, 1, 2, 1)
        Parameters
        ----------
        intermediate_keys: list[str]

        Returns
        -------
        grouped_keys: list[str]
        counts: list[int]
        """
        position = -1
        grouped_keys = []
        counts = []
        for key in intermediate_keys:
            if (not grouped_keys) or (key != grouped_keys[-1]):
                grouped_keys.append(key)
                counts.append(0)
                position += 1
            counts[position] += 1

        return grouped_keys, counts

    def get_discrete_repr_to_prob(self, start_key, end_key, grouped_intermediate_keys, intermediate_key_counts):

        discrete_repr_to_prob = {}
        all_sub_lists = list(itertools.product([True, False], repeat=len(grouped_intermediate_keys)))
        for sub_list_bools in all_sub_lists:
            joint_prob = 1
            discrete_repr = str(start_key)
            for is_key_included, key_id, key_count in zip(sub_list_bools, grouped_intermediate_keys, intermediate_key_counts):
                key_prob = 1 / (1 + np.exp(-10*((key_count / self.max_count) - 0.5)))
                if is_key_included:
                    discrete_repr += str(key_id)
                    joint_prob *= key_prob
                else:
                    joint_prob *= (1-key_prob)

            discrete_repr += str(end_key)
            discrete_repr_to_prob[discrete_repr] = joint_prob

        return discrete_repr_to_prob

    @staticmethod
    def normalize_word_to_prob(word_to_prob):
        """
        Normalize initial word_to_prob so that the sum of all word probs is 1
        Parameters
        ----------
        word_to_prob: dict

        Returns
        -------
        normalized_word_to_prob: dict
        """
        _sum = sum([prob for prob in word_to_prob.values()])
        return {word: prob/_sum for word, prob in word_to_prob.items()}


if __name__ == '__main__':
    """ Testing """
    import os
    from definition import ROOT_DIR
    vocab = os.path.join(ROOT_DIR, 'nuvox', 'config', 'top_25k_vocab.pkl')
    algo = TraceAlgorithm(vocab_path=vocab, max_count=10)
    word_to_prob = algo.get_possible_word_to_trace_prob(key_id_sequence=[3, 2, 2, 2, 2, 2, 2, 1, 1, 4, 4, 4, 4, 4, 4, 4, 5,  6, 6])
    print('stop here')








