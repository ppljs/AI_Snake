import numpy as np


def angle_between(p1, p2):
    ang1 = np.arctan2(*p1[::-1])
    ang2 = np.arctan2(*p2[::-1])
    return np.rad2deg((ang1 - ang2) % (2 * np.pi))


def distance(point_a, point_b):
    return (np.abs(point_a[0] - point_b[0]) + np.abs(point_a[1] - point_b[1]))
