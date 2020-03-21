import os

from nuvox.utils.io import pickle_load
from definition import ROOT_DIR


class TraceAlgorithm:

    def __init__(self, vocab_path, min_req=3):
        """
        The trace algorithm is responsible for identifying a set of potential intended words given the sequence of
        key ids that were in focus at each interval during the swype
        Parameters
        ----------
        vocab_path: str
            path to a pkl file containing a dict mapping from discrete representation e.g. '3246' to the set of
            possible words for that discrete repr
        min_req: int
            The minimum number of occurrences of a given key to include it in the discrete representation
        """

        self.vocab_path = vocab_path
        self.min_req = min_req
        self.discrete_repr_to_words = pickle_load(vocab_path)

    def get_possible_words(self, key_id_sequence):
        """
        Returns a list of possible words for a given key trace.
        Parameters
        ----------
        key_id_sequence: list[str]
            list of key ids that have been recorded in a single swype

        Returns
        -------
        possible_words: list[str]
            list of possible words
        """
        unique_key_idx = 0
        unique_keys = [key_id_sequence[0]]
        counts = [0]
        for key in key_id_sequence:
            if key != unique_keys[-1]:
                unique_keys.append(key)
                counts.append(0)
                unique_key_idx += 1
            counts[unique_key_idx] += 1

        discrete_repr = ''.join([str(key_id) for key_id, count in zip(unique_keys, counts) if count >= self.min_req])
        possible_words = self.discrete_repr_to_words.get(discrete_repr, [])

        return possible_words

