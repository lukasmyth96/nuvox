import itertools
from pprint import pprint

import numpy as np

from nuvox.utils.google_ngram_getter import get_ngram_freqs


class NgramBeamSearch:

    """ This class performs a form of beam search by using the frequency of a given n-gram according to the google
    n-gram api as a proxy for the probability of that n-gram occuring in natural text"""

    def __init__(self, beam_width, case_insensitive=True):

        """
        Parameters
        ----------
        beam_width: int
        """

        self.beam_width = beam_width
        self.case_insensitive = case_insensitive

        self.top_n_so_far = []  # list containing current top-n predicted phrases

    def get_new_top_phrase(self, pred_words):

        """
        Return the new most likely phrase based on the top predictions for the latest word
        Parameters
        ----------
        pred_words: list
            list of the top n predicted words

        Returns
        -------
        new_phrase: str
        """

        print('pred words: ', pred_words)  #TODO delete after debugging

        if not self.top_n_so_far:
            self.top_n_so_far = pred_words  # if first word in phrase
        else:
            phrases_to_query = [' '.join([existing_phrase, new_word])
                                for existing_phrase, new_word in itertools.product(self.top_n_so_far, pred_words)]

            freq_dict = self.get_ngram_frequencies(phrases_to_query)  # mapping phrase to freq
            ranked_list = sorted(freq_dict, key=freq_dict.get)[::-1]
            self.top_n_so_far = ranked_list[:self.beam_width]

            pprint(freq_dict)

        print('top n so far: ', self.top_n_so_far)  # TODO delete after debugging
        return self.top_n_so_far[0]

    def get_ngram_frequencies(self, phrases):

        """
        Get the mean frequency of each phrase in the input: phrases
        Parameters
        ----------
        phrases: list[str]
            list of phrases to get freqs for
        Returns
        -------
        freq_dict: dict
            dict mapping phrase to it's frequency
        """
        # TODO Warning this will currently only return the phrase of last 5 words

        query_list = []
        for phrase in phrases:

            words = phrase.split(' ')
            query_list.append(' '.join(words[-3:]))  # can only n-grams of max length 5

        combined_query = ', '.join(query_list)

        _, _, freq_df = get_ngram_freqs(combined_query, case_insensitive=self.case_insensitive)

        freq_dict = dict.fromkeys(phrases)
        for phrase in phrases:
            if self.case_insensitive:
                col_name = phrase + ' (All)'
            else:
                col_name = phrase

            if col_name in freq_df.columns:
                freq_values = list(freq_df[col_name])
                freq_dict[phrase] = np.mean(freq_values)  # (All) get case insensitive freqs
            else:
                freq_dict[phrase] = 0.0
                print('warning! no data returned by google API for phrase \'{}\' - assuming frequency value is zero'.format(phrase))

        return freq_dict

    def clear(self):
        """ clear list of current top n"""
        self.top_n_so_far = []

    def delete_last_word(self):
        """ delete the last word from each of the top n phrases"""
        current_top_phrases = self.top_n_so_far
        self.top_n_so_far = []
        for phrase in current_top_phrases:
            words = phrase.split(' ')
            new_phrase = ' '.join(words[:-1])
            self.top_n_so_far.append(new_phrase)


if __name__ == '__main__':
    """ testing"""
    beam = NgramBeamSearch(beam_width=2)
    beam.top_n_so_far = ['what']
    pred_words = ['adfdsd', 'is']
    new_phrase = beam.get_new_top_phrase(pred_words)
    print('new top phrase is: ', new_phrase)

