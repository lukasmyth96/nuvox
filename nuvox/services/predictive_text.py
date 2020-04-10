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

        # Phase 1) Get a dict mapping all possibly intended words to their probability based on the trace ONLY
        possible_word_to_prob = self.trace_algorithm.get_possible_word_to_trace_prob(key_id_sequence=key_trace)

        # Phase 2) Calculate a scaled likelihood by multiplying each words trace probability by log10(frequency(word))
        # this is used to narrow the list of candidates down to a suitable number for the language model
        possible_word_to_joint_prob = {word: trace_prob * zipf_frequency(word, 'en') for word, trace_prob in possible_word_to_prob.items()}
        sorted_candidates = [word for word, _ in sorted(possible_word_to_joint_prob.items(), key=lambda item: item[1], reverse=True)]
        final_candidates = sorted_candidates[:self.config.MAX_POTENTIAL_WORDS]

        # Phase 3) Predict the probability that each word appears next in the sentence
        final_candidate_to_prob = self.language_model.predict_next_word_prob(prompt, candidate_words=final_candidates)

        ranked_suggestions = sorted(final_candidate_to_prob.keys(), key=lambda k: final_candidate_to_prob.get(k, 0), reverse=True)

        if self.need_to_capitalize(prompt):
            ranked_suggestions = self.capitalize(ranked_suggestions)

        print('Key trace: \n ', key_trace, '\n ranked suggestions: ', ranked_suggestions)

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

    @staticmethod
    def capitalize(words):
        return [word.capitalize() for word in words]







