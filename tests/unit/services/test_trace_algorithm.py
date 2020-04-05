import os

import pytest

from definition import TESTS_DIR
from nuvox.services.trace_algorithm import TraceAlgorithm

vocab_path = os.path.join(TESTS_DIR, 'data', 'config_fixtures', 'top_25k_vocab.pkl')


@pytest.mark.parametrize('key_id_sequence, expected', [(['1'], ('1', '1', [])),
                                                       (['1', '2'], ('1', '2', [])),
                                                       (['1', '2', '3'], ('1', '3', ['2'])),
                                                       (['1', '1', '2', '3', '3'], ('1', '3', ['2']))])
def test_get_start_end_intermediate_keys(key_id_sequence, expected):
    trace_algo = TraceAlgorithm(vocab_path)
    assert trace_algo.get_start_end_intermediate_keys(key_id_sequence) == expected


@pytest.mark.parametrize('intermediate_keys, expected', [(['1', '2', '2', '3'], (['1', '2', '3'], [1, 2, 1]))])
def test_get_grouped_intermediate_keys_with_counts(intermediate_keys, expected):
    trace_algo = TraceAlgorithm(vocab_path)
    assert trace_algo.get_grouped_intermediate_keys_with_counts(intermediate_keys) == expected





