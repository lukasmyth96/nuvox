from wordfreq import zipf_frequency

from nuvox.services.gpt2 import GPT2
from nuvox.services.trace_algorithm import TraceAlgorithm


class PredictiveText:

    def __init__(self, config):
        """

        Parameters
        ----------
        config: nuvox.config.config.Config

        """

        self.config = config
        self.language_model = GPT2()
        self.trace_algorithm = TraceAlgorithm(vocab_path=config.VOCAB_PATH)

    def predict_next_word(self, prompt, key_trace):
        """

        Parameters
        ----------
        prompt: str
            previous text
        key_trace: list[str]
            sequence of key_ids that were in focus at each interval during a swype

        Returns
        -------
        ranked_suggestions: list[str]
            ranked list of other suggested words
        """
        key_trace = self.remove_blacklisted_keys(key_trace)

        if not key_trace:
            return []

        # Phase 0 - check if punctuation key was selected
        intended_punctuation = self.get_intended_punctuation(key_trace)
        if intended_punctuation:
            return [intended_punctuation]

        # Phase 1) Get dict mapping word --> prob(word | trace) for all possibly intended words using trace algorithm
        word_to_trace_prob = self.trace_algorithm.get_possible_word_to_trace_prob(key_id_sequence=key_trace)
        candidate_words = list(word_to_trace_prob)

        # Phase 2) Get dict mapping word --> prob(word | prompt) all possibly intended words using language model
        word_to_language_prob = self.language_model.predict_next_word_prob(prompt, candidate_words=candidate_words)
        _sum = sum([prob for prob in word_to_language_prob])  # normalize so probs sum to 1
        word_to_language_prob = {word: prob/_sum for word, prob in word_to_language_prob.items()}

        # Phase 3) Get dict mapping word --> prob(word | trace) * prob(word | prompt) (i.e. the joint probability)
        # TODO - need some sort of scaling factor to control influence of each model
        word_to_joint_prob = {word: (word_to_trace_prob[word] * word_to_language_prob[word]) for word in candidate_words}

        ranked_suggestions = sorted(word_to_joint_prob.keys(), key=lambda k: word_to_joint_prob.get(k, 0), reverse=True)

        if self.need_to_capitalize(prompt):
            ranked_suggestions = [word.capitalize() for word in ranked_suggestions]

        return ranked_suggestions

    def get_intended_punctuation(self, key_id_sequence):
        """
        Config contains a hardcoded mapping from key_id to punctuation
        Parameters
        ----------
        key_id_sequence: list[str]

        Returns
        -------
        punctuation: str
            or None if no punctation
        """
        if len(set(key_id_sequence)) == 1:
            key_id = key_id_sequence[0]
            punctuation = self.config.FIXED_KEY_ID_TO_PUNCTUATION.get(key_id)
            return punctuation

    def remove_blacklisted_keys(self, key_id_sequence):
        """ Remove key_ids from sequence that are to be ignored e.g. the blank key at center of screen"""
        return [key_id for key_id in key_id_sequence if key_id not in self.config.KEYS_TO_IGNORE]

    @staticmethod
    def need_to_capitalize(prompt):
        return (not prompt) or (list(prompt)[-1] in ['.', '?', '!'])








