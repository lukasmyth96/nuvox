

class Swype:

    def __init__(self, key_trace,
                 ranked_suggestions=None,
                 accepted_word=None,
                 word_to_trace_prob=None,
                 word_to_language_prob=None,
                 word_to_joint_prob=None):
        """
        Single swype
        Parameters
        ----------
        key_trace: list[str]
            list of key_ids that were recorded at every timesteps during the swype
        ranked_suggestions: list[str], optional
            list of ranked suggestions that was predicted for the swype
        accepted_word: str, optional
        word_to_trace_prob: dict, optional
        word_to_language_prob: dict, optional
        word_to_joint_prob: dict, optional
        """

        self.key_trace = key_trace
        self.ranked_suggestions = ranked_suggestions
        self._accepted_word = None
        if accepted_word:
            self.accepted_word = accepted_word  # call setter
        self.word_to_trace_prob = word_to_trace_prob
        self.word_to_language_prob = word_to_language_prob
        self.word_to_joint_prob = word_to_joint_prob
        self.was_deleted = False

    def __repr__(self):
        return self.accepted_word

    @property
    def accepted_word(self):
        return self._accepted_word

    @accepted_word.setter
    def accepted_word(self, word):
        if self.ranked_suggestions is None:
            raise BaseException('cannot set accepted word while ranked_suggestions attribute is None')
        if word not in self.ranked_suggestions:
            raise ValueError('word \'{}\' is not in ranked suggestions for swype'.format(word))
        self._accepted_word = word

    @property
    def accepted_word_rank(self):
        return self.ranked_suggestions.index(self.accepted_word) + 1  # rank of the accepted word in the suggestions



