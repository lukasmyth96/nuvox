import pytest

from tests.data.keyboard_fixtures import valid_keyboard
from nuvox.utils.swype import get_discrete_representation_for_word
from nuvox.keyboard import Keyboard

keyboard = Keyboard(valid_keyboard)


@pytest.mark.parametrize('word, expected', [('hello', ['3', '2', '4', '6']),
                                            ('on', ['6'])])
def test_get_discrete_representation_for_word(word, expected):
    assert get_discrete_representation_for_word(keyboard, word) == expected


