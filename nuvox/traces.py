import numpy as np

import nuvox


def get_random_trace(keyboard, text, skip_spacekey=True, points_per_unit_dist=(15, 25)):
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
    points_per_unit_dist: tuple
        range for number of intermediate points to generate for every unit distance covered - value gets randomly
        selected from range each time

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

    for idx in range(max(1, len(text)-1)):

        curr_key = keyboard.char_to_key[char_list[idx]]

        if len(text) == 1:
            next_key = curr_key
        else:
            next_key = keyboard.char_to_key[char_list[idx+1]]

        # Get list of intermediate points - the number of which is proportional to the distance between the centroid

        if idx == 0:
            start_point = get_random_point(curr_key)
        else:
            start_point = end_point  # start point becomes the end point from the previous iteration

        if idx > 0 and curr_key == next_key:
            continue

        end_point = get_random_point(next_key)

        dist = np.linalg.norm(np.array(start_point) - np.array(end_point))
        points_per_unit = np.math.ceil(np.random.uniform(points_per_unit_dist[0], points_per_unit_dist[1]))
        num_points = np.math.ceil(dist * points_per_unit)
        intermediate_points = np.linspace(start_point, end_point, num_points)
        intermediate_points = [tuple(point) for point in intermediate_points]  # convert to list of tuples
        trace += intermediate_points

        if idx == 0:
            trace.insert(0, start_point)
        trace.append(end_point)

    trace = [trace[idx] for idx in range(len(trace) - 1) if trace[idx] != trace[idx+1]]  # filter out adjacent duplicates

    if not trace:
        raise Exception('No trace was created - this should never happen')

    return trace


def get_trance_angles(trace):
    """
    get list of angles (radians) at every point in a trace, that is, the angle made between the inbound and outbound vectors at
    every point in the trace.
    Parameters
    ----------
    trace: list[tuple]
        list of (x,y) tuples

    Returns
    -------
    angles: list[float]
    """

    def unit_vector(vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    def angle_between(v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2'::

        """
        v1_u = unit_vector(v1)
        v2_u = unit_vector(v2)
        eps = 1e-10
        angle = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0 + eps, 1.0 - eps))
        return angle

    angles=[]
    for idx in range(1, len(trace) - 1):
        vector_in = np.array(trace[idx]) - np.array(trace[idx - 1])
        vector_out = np.array(trace[idx + 1]) - np.array(trace[idx])
        angle = angle_between(vector_in, vector_out)
        angles.append(angle)
    angles.append(0)
    angles.insert(0, 0)
    assert len(angles) == len(trace)

    return angles


def get_trace_first_derivatives(trace):

    """
    get list of first derivatives dy/dx at every point in a trace, that is, the mean of the gradients of the inbound
    and outboud vectors at a given point
    Parameters
    ----------
    trace: list[tuple]
        list of (x,y) tuples

    Returns
    -------
    derivatives: list[float]
    """

    derivatives = []
    for idx in range(1, len(trace) - 1):
        grad_inbound = np.array((trace[idx][1] - trace[idx-1][1]) / (trace[idx][0] - trace[idx-1][0]))
        grad_outbound = np.array((trace[idx+1][1] - trace[idx][1]) / (trace[idx+1][0] - trace[idx][0]))

        derivatives.append(np.mean([grad_inbound, grad_outbound]))

    derivatives.append(0)
    derivatives.insert(0, 0)
    assert len(derivatives) == len(trace)

    return derivatives


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



