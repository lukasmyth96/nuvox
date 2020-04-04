

class Swype:

    def __init__(self, key_trace, ranked_suggestions, accepted_word=None):
        """
        Single swype
        Parameters
        ----------
        key_trace: list[str]
            list of key_ids that were recorded at every timesteps during the swype
        ranked_suggestions: list[str]
            list of ranked suggestions that was predicted for the swype
        """

        self.key_trace = key_trace
        self.ranked_suggestions = ranked_suggestions
        self._accepted_word = None
        self.accepted_word = accepted_word  # call setter

    @property
    def accepted_word(self):
        return self._accepted_word

    @accepted_word.setter
    def accepted_word(self, word):
        if word not in self.ranked_suggestions:
            raise ValueError('word \'{}\' is not in ranked suggestions for swype'.format(word))
        self._accepted_word = word



