import pytest

from tests.data.keyboard_fixtures import valid_keyboard, invalid_keyboard_1, invalid_keyboard_2
from nuvox.keyboard import Keyboard


@pytest.mark.parametrize('key_list', [valid_keyboard])
def test_valid_keyboard(key_list):
    """ Test no exception is raised on building valid keyboard and that keys have been stored correctly"""
    keyboard = Keyboard(key_list)
    assert all([(key.key_id, key) in keyboard.key_id_to_key.items() for key in valid_keyboard])


@pytest.mark.parametrize('key_list', [invalid_keyboard_1, invalid_keyboard_2])
def test_invalid_keyboard(key_list):
    with pytest.raises(ValueError) as e:
        Keyboard(key_list)


def test_get_key_at_point():
    keyboard = Keyboard(valid_keyboard)
    assert keyboard.get_key_at_point(0.1, 0.1).key_id == 'display'
    assert keyboard.get_key_at_point(1.1, 1.1) is None

