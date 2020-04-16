from math import fabs, sqrt
import random
from Point import Point


def min_intersect_degree(d1, d2):
    diff = abs(d1 - d2) % 180
    return min(diff, abs(diff-180))


def rand_in_limit(limit):
    # rand in [-limit, limit]
    return limit * (random.random() - 0.5) * 2


def rand_hit_thershold(thershold):
    if random.random() < thershold:
        return True
    else:
        return False


def line_cross(line1, line2):
    v1 = line1[0].subtract(line1[1])
    v2 = line2[0].subtract(line2[1])
    if fabs(v1.x * v2.y - v1.y * v2.x) < 1e-2:
        return False

    def is_online(line, p):
        v1 = line[0].subtract(p)
        v2 = p.subtract(line[1])
        return fabs(v1.x * v2.y - v1.y * v2.x) < 1e-2

    def line(p1, p2):
        A = (p1.y - p2.y)
        B = (p2.x - p1.x)
        C = (p1.x*p2.y - p2.x*p1.y)
        return A, B, -C

    def intersection(L1, L2):
        D = L1[0] * L2[1] - L1[1] * L2[0]
        Dx = L1[2] * L2[1] - L1[1] * L2[2]
        Dy = L1[0] * L2[2] - L1[2] * L2[0]
        if D != 0:
            x = Dx / D
            y = Dy / D
            return Point(x, y)
        else:
            return False

    L1 = line(line1[0], line1[1])
    L2 = line(line2[0], line2[1])

    point = intersection(L1, L2)
    if is_online(line1, point):
        return False
    if is_online(line2, point):
        return False
    return point
