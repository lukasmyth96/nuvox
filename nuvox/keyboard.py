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

    def _build_keyboard(self, key_list):
        """
        Parameters
        ----------
        key_list: list[nuvox.key.Key]
        """
        self.key_id_to_key = {key.key_id: key for key in key_list}
        self._check_for_overlaps()

    def get_key_ids_at_point(self, x, y):
        """
        Returns list of key ids for keys at a given point - can be two if point is right on border
        Parameters
        ----------
        x: float
        y: float

        Returns
        -------
        key_ids: list[str]
        """
        return [key_id for key_id, key in self.key_id_to_key.items() if key.is_point_within_key(x, y)]

    def _check_for_overlaps(self):
        """
        Check if any of the keys overlap with each other - Raises ValueError if they do.
        """
        keys = list(self.key_id_to_key.values())
        for key_a, key_b in itertools.combinations(keys, 2):
            if key_a.intersects(key_b):
                raise ValueError('Keys: {} and {} overlap'.format(key_a.key_id, key_b.key_id))

