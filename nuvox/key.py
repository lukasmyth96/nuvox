

class Key:

    def __init__(self, x1, y1, w, h, key_id, contents, widget_type='button'):
        """
        Base class for all keys
        Parameters
        ----------
        x1: float
        y1: float
        w: float
        h: float
        key_id: str
        contents: list[str]
        widget_type: str
            'display', 'button'
        """
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x1 + w, y1 + h
        self.w, self.h = w, h
        self.key_id = key_id
        self.contents = contents
        self.widget_type = widget_type

        self._verify_input()

    def __repr__(self):
        return '\n'.join(['{} : {}'.format(name, value) for name, value in vars(self).items()])

    def contains_point(self, x, y):
        """ Returns True if (x, y) is within bounds of key - otherwise False"""
        return (self.x1 <= x <= self.x2) and (self.y1 <= y <= self.y2)

    def intersects(self, other):
        """
        Returns True if this key intersects with other key - uses separating axis theorem
        Parameters
        ----------
        other: nuvox.key.Key
        """
        return not ((self.x2 <= other.x1) or (self.x1 >= other.x2) or (self.y1 >= other.y2) or (self.y2 <= other.y1))

    def _verify_input(self):

        if not all([isinstance(x, float) for x in [self.x1, self.y1, self.w, self.h]]):
            raise ValueError('Key coordinates must be float')

        if (self.x2 <= self.x1) or (self.y2 <= self.y1):
            raise ValueError('Key cannot have zero area')

        if not all([(0 <= x <= 1) for x in [self.x1, self.y1, self.x2, self.y2]]):
            raise ValueError('Key exceeds border of the window')



