import itertools
import os
import numpy as np

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

        start_key, end_key, intermediate_keys = self.get_start_end_intermediate_keys(key_id_sequence)

        grouped_intermediate_keys, counts = self.get_intermediate_key_counts(intermediate_keys)
        scaled_key_probs = self.get_scaled_probs_for_counts(counts)
        sub_lists, sub_list_probs = self.get_all_sub_lists_and_probs(grouped_intermediate_keys, scaled_key_probs)

        # first has highest prob
        ranked_sub_lists = sorted(l for l, p in sorted(zip(sub_lists, sub_list_probs), key=lambda pair: pair[1]))[::-1]
        most_likely_discrete_reprs = [''.join([start_key, ''.join(inter_keys), end_key]) for inter_keys in ranked_sub_lists[:20]]

        possible_words = list(itertools.chain.from_iterable([self.discrete_repr_to_words.get(discrete_repr, []) for discrete_repr in most_likely_discrete_reprs]))

        return possible_words

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
    def get_intermediate_key_counts(intermediate_keys):
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

    @staticmethod
    def get_all_sub_lists_and_probs(key_list, key_probs):
        sub_lists = []
        sub_list_probs = []
        for sub_list_len in range(len(key_list) + 1):
            for index_sub_list in itertools.combinations(list(range(len(key_list))), sub_list_len):
                sub_lists.append([key_list[idx] for idx in index_sub_list])
                joint_prob = 1  # calculate joint of this sub list
                for i in range(len(key_list)):
                    if i in index_sub_list:
                        joint_prob *= key_probs[i]
                    else:
                        joint_prob *= (1 - key_probs[i])
                sub_list_probs.append(joint_prob)

        return sub_lists, sub_list_probs

    @staticmethod
    def get_scaled_probs_for_counts(counts):
        return 3/4 * (np.array(counts) / max(counts))




