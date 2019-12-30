import numpy as np

import nuvox


def get_random_trace(keyboard, text, skip_spacekey=True, points_per_unit_dist=20):
    """
    Get a trace (list of (x, y) tuples) for the perfect path for a given string of text, that is, the path that
    traverses from centroid to centroid in a straight line.
    Parameters
    ----------
    keyboard: nuvox.keyboard.Keyboard
        keyboard object
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

    if not isinstance(keyboard, nuvox.keyboard.Keyboard):
        raise ValueError('Parameter: keyboard must be an instance of nuvox.keyboard.Keyboard class')

    if not isinstance(text, str):
        raise ValueError('Parameter: text must be a string')

    text = text.lower()
    char_list = list(text)

    if not all([char in list(keyboard.char_to_key) for char in text]):
        invalid_chars = list(set(char_list) - set(list(keyboard.char_to_key)))
        raise ValueError('text contains following character not included in keybaord: {}'.format(invalid_chars))

    if skip_spacekey:
        char_list = [char for char in char_list if char != ' ']

    trace = []

    for idx, (current_char, next_char) in enumerate(zip(char_list, char_list[1:])):
        curr_key = keyboard.char_to_key[current_char]
        next_key = keyboard.char_to_key[next_char]
        if curr_key == next_key:
            continue
        else:
            # Get list of intermediate points - the number of which is proportional to the distance between the centroid

            if idx == 0:
                start_point = get_random_point(curr_key)
            else:
                start_point = end_point

            end_point = get_random_point(next_key)

            dist = np.linalg.norm(np.array(start_point) - np.array(end_point))
            num_points = np.round(dist * points_per_unit_dist)
            intermediate_points = np.linspace(start_point, end_point, num_points)
            intermediate_points = [tuple(point) for point in intermediate_points]  # convert to list of tuples
            trace += intermediate_points

    return trace


def get_random_point(key, distribution='trunc_normal'):
    """
    get a random point from within the keys border
    Parameters
    ----------
    key: nuvox.keyboard.Key
    distribution: str

    Returns
    -------
    (x, y): tuple
        x, y coord of random point
    """

    if distribution == 'trunc_normal':
        x = trunc_normal(mean=key.centroid[0], stddev=key.w / 4, lower=key.x1, upper=key.x2)
        y = trunc_normal(mean=key.centroid[1], stddev=key.h / 4, lower=key.y1, upper=key.y2)
        return (x, y)

    else:
        raise ValueError('Parameter: distribution value {} not handled yet'.format(distribution))


def trunc_normal(mean, stddev, lower, upper):
    while True:
        num = np.random.normal(mean, stddev)
        if lower < num < upper:
            break
    return num
