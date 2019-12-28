def get_iou(bbox1, bbox2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.

    Parameters
    ----------
    bbox1 : nuvox.keyboard.Key

    bbox2 : nuvox.keyboard.Key

    Returns
    -------
    float
        in [0, 1]
    """

    assert bbox2.x1 <= bbox2.x2
    assert bbox2.y1 <= bbox2.y2
    assert bbox1.x1 <= bbox1.x2
    assert bbox1.y1 <= bbox1.y2

    # determine the coordinates of the intersection rectangle
    intersection_rectangle = {
        'x1': max(bbox1.x1, bbox2.x1),
        'y1': max(bbox1.y1, bbox2.y1),
        'x2': min(bbox1.x2, bbox2.x2),
        'y2': min(bbox1.y2, bbox2.y2)}

    if (intersection_rectangle['x2'] < intersection_rectangle['x1']) or (
            intersection_rectangle['y2'] < intersection_rectangle['y1']):
        return 0.0

    intersection_area = compute_area(intersection_rectangle)
    bbox1_area = compute_area(vars(bbox1))
    bbox2_area = compute_area(vars(bbox2))

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the intersection area
    iou = intersection_area / (bbox1_area + bbox2_area - intersection_area)

    assert iou >= 0.0
    assert iou <= 1.0

    return iou


def compute_area(bbox):
    """
    Compute the area of a bounding box
    Parameters
    ----------
    bbox: dict
        containing attributes x1, x2, y1, y2
    Returns
    -------
    area: float
        area of bbox
    """
    # The +1 on each area calculation accounts for pixel not begin aligned with axis
    return (bbox['x2'] - bbox['x1']) * (bbox['y2'] - bbox['y1'])
