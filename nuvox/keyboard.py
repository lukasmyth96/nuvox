import  itertools
from pprint import pprint

from nuvox.config.keyboard_config import required_key_attributes, nuvox_standard_keyboard
from nuvox.utils.intersection_over_union import get_iou


class Keyboard:

    """ Encapsulates functionality of the Keyboard"""

    def __init__(self):

        self.keys = []
        self.char_to_key = {}
        self.key_id_to_contents = {}

    def build_keyboard(self, key_list):
        """
        Build a keyboard from a list of keys
        Parameters
        ----------
        key_list: list[dict]
        """

        if not isinstance(key_list, list):
            raise ValueError('Parameter: key_list must be of type list')

        if not all([isinstance(item, dict) for item in key_list]):
            raise ValueError('Paremeter: key_list must contain only items of type dict')

        for key_dict in key_list:

            self._add_key(key_dict)

        self._check_for_overlaps()  # check if any keys overlap - raise ValueError if so

    def _add_key(self, key_dict):
        """
        Add single key item to keyboard
        Parameters
        ----------
        key_dict: dict containing the information for a single key
        """

        missing_keys = list(set(required_key_attributes) - set(key_dict))
        unexpected_keys = list(set(key_dict) - set(required_key_attributes))
        if missing_keys:
            raise ValueError('Paremeter: key_dict is missing following keys: {}'.format(missing_keys))
        elif unexpected_keys:
            raise ValueError('Paremeter: key_dict contains unexpected keys: {}'.format(unexpected_keys))

        key = Key(x1=key_dict['x1'],
                  y1=key_dict['y1'],
                  w=key_dict['w'],
                  h=key_dict['h'],
                  key_id=key_dict['key_id'],
                  contents=key_dict['contents'],
                  type=key_dict['type'])

        self._check_for_invalid_coords(key)

        self.keys.append(key)
        self.key_id_to_contents[key.key_id] = key.contents
        for char in key.contents:
            self.char_to_key.update({char: key.key_id})

    @staticmethod
    def _check_for_invalid_coords(key):
        """ check if key has valid coords - raises ValueError if not"""
        if key.x1 < 0 or key.y1 < 0 or key.x2 > 1 or key.y2 > 1:
            raise ValueError('Key: {} has invalid coordinates: \n {}'.format(key.key_id, vars(key)))

        elif not 0 < key.w <=1 or not 0 < key.h <= 1:
            raise ValueError('Key: {} has invalid width or height \n {}'.format(key.key_id, vars(key)))

    def _check_for_overlaps(self):
        """
        Check if any of the keys overlap with eachother - Raises ValueError if they do.
        """

        for key_a, key_b in itertools.combinations(self.keys, 2):
            if get_iou(key_a, key_b) > 1e-10:  # allows some tolerance for floating point precision
                raise ValueError('Keys: {} and {} have IoU > 0 so overlap'.format(key_a.key_id, key_b.key_id))


class Key:

    def __init__(self, x1, y1, w, h, key_id, contents, type):

        self.x1 = x1
        self.y1 = y1
        self.x2 = x1 + w
        self.y2 = y1 + h
        self.w = w
        self.h = h
        self.key_id = key_id
        self.contents = contents
        self.type = type


if __name__ == '__main__':

    """ Testing """
    keyboard = Keyboard()
    keyboard.build_keyboard(nuvox_standard_keyboard)
    print('STOP HERE')