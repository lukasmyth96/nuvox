import itertools


class Keyboard:

    def __init__(self, key_list):
        """ This class is the 'Model' of the MVC structure
        Parameters
        ----------
        key_list:list[nuvox.key.Key]
            list of dictionaries defining the keyboard
        """
        self.key_id_to_key = {}
        self._build_keyboard(key_list)

    @property
    def keys(self):
        return list(self.key_id_to_key.values())

    def _build_keyboard(self, key_list):
        """
        Parameters
        ----------
        key_list: list[nuvox.key.Key]
        """
        self.key_id_to_key = {key.key_id: key for key in key_list}
        self._check_for_overlaps()

    def get_key_at_point(self, x, y):
        """
        Returns list of key ids for keys at a given point - can be two if point is right on border
        Parameters
        ----------
        x: float
        y: float

        Returns
        -------
        key: nuvox.key.Key
            returns None if no key at point
        """
        return next((key for key in self.keys if key.contains_point(x, y)), None)

    def _check_for_overlaps(self):
        """
        Check if any of the keys overlap with each other - Raises ValueError if they do.
        """
        for key_a, key_b in itertools.combinations(self.keys, 2):
            if key_a.intersects(key_b):
                raise ValueError('Keys: {} and {} overlap'.format(key_a.key_id, key_b.key_id))


if __name__ == '__main__':
    """ testing """
    from nuvox.config.keyboard_layouts import nuvox_standard_keyboard
    _keyboard = Keyboard(key_list=nuvox_standard_keyboard)
    print('stop here')