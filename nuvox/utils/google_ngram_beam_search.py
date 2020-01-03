

class NgramBeamSearch:

    """ This class performs a form of beam search by using the frequency of a given n-gram according to the google
    n-gram api as a proxy for the probability of that n-gram occuring in natural text"""

    def __init__(self, beam_width):

        """
        Parameters
        ----------
        beam_width: int
        """

        self.beam_width = beam_width

        self.top_n_so_far = []  # list containing current top-n predicted phrases

    def get_new_top_phrase(self, pred_dict):

        """
        Return the new most likely phrase based on the top predictions for the latest word
        Parameters
        ----------
        pred_dict: dict
            dict mapping each of the top n predictions for the latest word to their predicted probabilities

        Returns
        -------
        new_phrase: str
        """

        if not self.top_n_so_far:
            return True


    def get_ngram_freqs(self, phrases):

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

        query_list = []
        for phrase in phrases:

            words = phrase.split(' ')
            query = ' '.join(words[-5:])  # can only n-grams of max length 5
            query_list.append(query)


