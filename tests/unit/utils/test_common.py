import pytest

from nuvox.utils.common import normalize_word_to_prob_dict


@pytest.mark.parametrize('d, expected', [({'a': 0.1, 'b': 0.3}, {'a': 0.25, 'b': 0.75})])
def test_normalize_word_to_prob_dict(d, expected):
    assert set(d) == set(expected)
    normalized_dict = normalize_word_to_prob_dict(d)
    assert all([(abs(normalized_dict[key] - expected[key]) < 1e-5) for key in d.keys()])
