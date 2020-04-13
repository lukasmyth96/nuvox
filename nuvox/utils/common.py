
def normalize_word_to_prob_dict(word_to_prob):
    """
    Normalize a dictionary mapping words to probabilities such that the probabilities sum to 1
    Used by language model and trace algorithm.
    Parameters
    ----------
    word_to_prob: dict

    Returns
    -------
    normalized_word_to_prob: dict
    """
    _sum = sum([prob for prob in word_to_prob.values()])
    return {word: prob / _sum for word, prob in word_to_prob.items()}