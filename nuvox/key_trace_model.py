import os


from nuvox.utils.common import pickle_load
from definition import ROOT_DIR


class KeyTraceModel:

    def __init__(self, min_req=3):
        """

        Parameters
        ----------
        min_req: int
            The minimum number of occurrences of a given key to include it in the discrete representation
        """

        self.min_req = min_req
        self.discrete_repr_to_words = pickle_load(os.path.join(ROOT_DIR, 'discrete_representation_to_words.pkl'))

    def get_possible_words(self, key_trace):
        """
        Get a list of possible words for a given key trace
        Parameters
        ----------
        key_trace: list[int]
            list of key ids that have been recorded in a single swype

        Returns
        -------
        possible_words: list[str]
            list of possible words
        """
        unique_key_idx = 0
        unique_keys = [key_trace[0]]
        counts = [0]
        for key in key_trace:
            if key != unique_keys[-1]:
                unique_keys.append(key)
                counts.append(0)
                unique_key_idx += 1
            counts[unique_key_idx] += 1

        discrete_repr = ''.join([str(key_id) for key_id, count in zip(unique_keys, counts) if count >= self.min_req])

        print('discrete represenation is: ', discrete_repr)
        possible_words = self.discrete_repr_to_words.get(discrete_repr, [])

        return possible_words

