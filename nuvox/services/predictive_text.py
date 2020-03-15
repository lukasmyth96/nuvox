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

    def predict_next_word(self, prompt, key_id_sequence):
        """

        Parameters
        ----------
        prompt: str
            previous text
        key_id_sequence: list[str]
            sequence of key_ids that were in focus at each interval during a swype

        Returns
        -------
        ranked_suggestions: list[str]
            ranked list of other suggested words
        """
        # Phase 1) Predict set of possible words based on the swype pattern ONLY
        potential_words = self.trace_algorithm.get_possible_words(key_id_sequence=key_id_sequence)
        potential_words = potential_words[:self.config.MAX_POTENTIAL_WORDS]
        print('Top {} potential words are: {}'.format(len(potential_words), potential_words))

        # Phase 2) Predict the probability that each word appears next in the sentence
        word_to_prob = self.language_model.predict_next_word_prob(prompt, potential_words=potential_words)

        ranked_suggestions = sorted(word_to_prob.keys(), key=lambda k: word_to_prob.get(k, 0), reverse=True)

        return ranked_suggestions







