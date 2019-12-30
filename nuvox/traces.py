import numpy as np

import nuvox

def get_perfect_trace(keyboard, text, skip_spacekey=True, points_per_unit_dist=20):
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

    for current_char, next_char in zip(char_list, char_list[1:]):
        current_key = keyboard.char_to_key[current_char]
        next_key = keyboard.char_to_key[next_char]
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