import numpy as np

import nuvox


def get_random_trace(keyboard, text, add_gradients=True, skip_spacekey=True, min_dist_between_points=0.05):
    """
    Get a trace (list of (x, y) tuples) for the perfect path for a given string of text, that is, the path that
    traverses from centroid to centroid in a straight line.
    Parameters
    ----------
    keyboard: nuvox.keyboard.Keyboard
        keyboard object
    text: str
        text to trace
    add_gradients: bool
        whether to add the gradient at each point as the third item in each tuple
    skip_spacekey: bool, optional
        whether to skip the space key between each word in trace
    min_dist_between_points: float
        minimum distance between two consecutive points - this should really be equal to the min distance used when
        recording mouse movement in diplay.py

    Returns
    -------
    trace: list[tuple]
        list of (x, y) tuples containing the relative (x, y) coords of every point in the trace
    """

    if not isinstance(keyboard, nuvox.keyboard.Keyboard):
        raise ValueError('Parameter: keyboard must be an instance of nuvox.keyboard.Keyboard class')

    if not isinstance(text, str):
        raise ValueError('Parameter: text must be a string')

    if not text:
        raise ValueError('Paremeter: text is empty - cannot get trace for empty string')

    text = text.lower()
    char_list = list(text)
    char_list = [char for char in char_list if char != '\'']

    if not all([char in list(keyboard.char_to_key) for char in char_list]):
        invalid_chars = list(set(char_list) - set(list(keyboard.char_to_key)))
        raise ValueError('text contains following character not included in keybaord: {}'.format(invalid_chars))

    if skip_spacekey:
        char_list = [char for char in char_list if char != ' ']

    trace = []

    for idx in range(max(1, len(char_list)-1)):

        curr_key = keyboard.char_to_key[char_list[idx]]

        if len(char_list) == 1:
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

        # Get intermediate points
        intermediate_points = get_intermediate_points(start_point, end_point)

        trace += intermediate_points

        # Add start and end point
        if idx == 0:
            trace.insert(0, start_point)
        trace.append(end_point)

    # Remove points that are too close to the previous point

    trace = remove_near_consecutive_points(trace, min_dist_between_points)

    if add_gradients:
        trace = add_gradients_to_trace(trace)

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


def get_intermediate_points(start, end, random_delta_sd=0.005):
    """
    Get intermediate points between start and end
    Parameters
    ----------
    start: tuple
    end: tuple
        (x, y) coord
    random_delta_sd: float, optional
        standard deviation for randomly altering position of each point. new position is sampled from normal distribution
        where the mean is the original position and the stddev is random_delta_sd
    Returns
    -------
    intermediate_points: list[tuple]
        list of (x, y) rel coordinates
    """

    assert 0 <= random_delta_sd <= 0.005  # enforce sensible range in case of typo

    intermediate_points = np.linspace(start, end, 25)  # start with many and them remove some based on min_dist_between_points
    intermediate_points = [tuple(point) for point in intermediate_points]  # convert to list of tuples

    # Apply small random delta to each point
    intermediate_points = [tuple(np.random.normal(point, random_delta_sd)) for point in intermediate_points]

    return intermediate_points


def remove_near_consecutive_points(trace, min_dist):
    """ remove points that are within a min distance of the previous points
    Parameters
    ----------
    trace: list[tuple]
    min_dist: float
        minimum distance between two consecutive points in the final trace

    Returns
    -------
    new_trace: list[tuple]
    """
    # Remove points that are within min_dist_between_points of the last point
    new_trace = [trace[0]]  # always keep first point
    for point in trace[1:]:
        previous_point = new_trace[-1]  # last point that we are keeping
        euclidean_dist = np.linalg.norm(np.array(point) - np.array(previous_point))
        if euclidean_dist > min_dist:
            new_trace.append(point)

    return new_trace


def add_gradients_to_trace(trace):
    """ At the first derivative at each point as the third item in each tuple within the trace

    Parameters
    ----------
    trace: list[tuple]
        list of relative(x, y) coords in trace

     Returns
     -------
     updated_trace: list[tuple]
        list of (x, y, dy/dx) tuples for each point in trace
    """

    gradients = get_trace_first_derivatives(trace)
    updated_trace = [x_y + (dy_dx,) for x_y, dy_dx in zip(trace, gradients)]

    return updated_trace


def get_trace_first_derivatives(trace):

    """
    get list of first derivatives dy/dx at every point in a trace, which we define as the gradient of the inbound vector
    to a point. The gradient for the start point is always zero.

    Parameters
    ----------
    trace: list[tuple]
        list of (x,y) tuples

    Returns
    -------
    derivatives: list[float]
    """

    derivatives = []
    for idx in range(1, len(trace)):
        try:
            grad_inbound = np.array((trace[idx][1] - trace[idx-1][1]) / (trace[idx][0] - trace[idx-1][0]))
        except ZeroDivisionError:
            # If no change in x coordinate then assign a 100 or -100 gradient
            grad_inbound = np.copysign(100, trace[idx][1] - trace[idx-1][1])

        derivatives.append(grad_inbound)

    derivatives.append(0)  # gradient at start point is always zero

    assert len(derivatives) == len(trace)

    return derivatives


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








