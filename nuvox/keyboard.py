import itertools

from nuvox.utils.intersection_over_union import get_iou


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

        Returns
        -------

        """
        self.key_id_to_key = {key.key_id: key for key in key_list}
        self._check_for_overlaps()

    def _check_for_overlaps(self):
        """
        Check if any of the keys overlap with each other - Raises ValueError if they do.
        """
        keys = list(self.key_id_to_key.values())
        for key_a, key_b in itertools.combinations(keys, 2):
            if key_a.intersects(key_b):
                raise ValueError('Keys: {} and {} have IoU overlap'.format(key_a.key_id, key_b.key_id))

