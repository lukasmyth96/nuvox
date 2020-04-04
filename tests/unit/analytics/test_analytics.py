import os

import pytest

from nuvox.analytics.analytics import Analytics
from definition import TESTS_DIR


@pytest.mark.parametrize('start_date,end_date,expected_num_sessions', [(None, None, 3),
                                                                       ('2019_01_01', None, 3),
                                                                       ('2022_01_01', None, 1),
                                                                       (None, '2022_01_01', 2),
                                                                       ('2020_01_01', '2022_01_01', 1)])
def test_analytics_load_sessions(start_date, end_date, expected_num_sessions):
    """ Test that sessions loaded by date lead to correct number of sessions being loaded"""
    directory = os.path.join(TESTS_DIR, 'data', 'analytics_fixtures', 'sessions')
    analytics = Analytics()
    analytics.load_sessions(directory, start_date, end_date)
    assert len(analytics.sessions) == expected_num_sessions


@pytest.mark.parametrize('start_date,end_date', [('2020-01-01', None),
                                                 (None, '2020-01-01'),
                                                 ('2020_15_01', None),
                                                 ('2020_01_32', None)])
def test_analytics_load_invalid_input(start_date, end_date):
    """ Test that ValueError gets raised when dates are invalid or wrongly formatted"""
    directory = os.path.join(TESTS_DIR, 'data', 'analytics_fixtures', 'sessions')
    analytics = Analytics()
    with pytest.raises(ValueError) as e:
        analytics.load_sessions(directory, start_date, end_date)

