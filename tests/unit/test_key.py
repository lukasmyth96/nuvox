import pytest

from nuvox.key import Key


@pytest.mark.parametrize('x, y, w, h, key_id, contents', [(0.1, 0.1, 0.1, 0.1, '1', ['abc'])])
def test_valid_key(x, y, w, h, key_id, contents):
    """ Test that no exception raised when creating valid key and that dimensions are correct"""
    key = Key(x, y, w, h, key_id, contents)
    assert (key.x1 == 0.1) and (key.y1 == 0.1) and (key.x2 == 0.2) and (key.y2 == 0.2)


@pytest.mark.parametrize('x, y, w, h, key_id, contents', [(-0.1, 0.1, 0.1, 0.1, '1', ['abc']),
                                                          (0.1, -0.1, 0.1, 0.1, '1', ['abc']),
                                                          (0.1, 0.1, -0.1, 0.1, '1', ['abc']),
                                                          (0.1, 0.1, 0.1, -0.1, '1', ['abc']),
                                                          (0.1, 0.1, 1.1, 0.1, '1', ['abc']),
                                                          (0.1, 0.1, 0.1, 1.1, '1', ['abc'])])
def test_invalid_key(x, y, w, h, key_id, contents):
    """ Test that ValueError raised on invalid dimensions"""
    with pytest.raises(ValueError) as e:
        Key(x, y, w, h, key_id, contents)