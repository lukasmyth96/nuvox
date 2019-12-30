import  itertools
from pprint import pprint

import numpy as np

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
            self.char_to_key.update({char: key})

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

    def get_perfect_trace(self, text, skip_spacekey=True, points_per_unit_dist=20):
        """
        Get a trace (list of (x, y) tuples) for the perfect path for a given string of text, that is, the path that
        traverses from centroid to centroid in a straight line.
        Parameters
        ----------
        text: str
            text to trace
        skip_spacekey: bool, optional
            whether to skip the space key between each word in trace
        points_per_unit_dist: int
            number of intermediate points to generate for every unit distance covered

        Returns
        -------
        trace: list[tuple]
            list of (x, y) tuples containing the relative (x, y) coords of every point in the trace
        """
        if not isinstance(text, str):
            raise ValueError('Parameter: text must be a string')

        elif not all([char in list(self.char_to_key) for char in text]):
            invalid_chars = list(set(list(text)) - set(list(self.char_to_key)))
            raise ValueError('text contains following character not included in keybaord: {}'.format(invalid_chars))

        trace = []
        char_list = list(text)

        if skip_spacekey:
            char_list = [char for char in char_list if char != ' ']

        for current_char, next_char in zip(char_list, char_list[1:]):
            current_key = self.char_to_key[current_char]
            next_key = self.char_to_key[next_char]
            if current_key == next_key:
                continue
            else:
                # Get list of intermediate points - the number of which is proportional to the distance between the centroid
                dist = np.linalg.norm(np.array(current_key.centroid) - np.array(next_key.centroid))
                num_points = np.round(dist * points_per_unit_dist)
                intermediate_points = np.linspace(current_key.centroid, next_key.centroid, num_points)
                intermediate_points = [tuple(point) for point in intermediate_points]  # convert to list of tuples
                trace += intermediate_points

        return trace


class Key:

    def __init__(self, x1, y1, w, h, key_id, contents, type):

        self.x1 = x1
        self.y1 = y1
        self.x2 = x1 + w
        self.y2 = y1 + h
        self.w = w
        self.h = h
        self.centroid = ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)
        self.key_id = key_id
        self.contents = contents
        self.type = type


if __name__ == '__main__':

    """ Testing """
    keyboard = Keyboard()
    keyboard.build_keyboard(nuvox_standard_keyboard)
    trace = keyboard.get_perfect_trace('hello my')
    print('STOP HERE')