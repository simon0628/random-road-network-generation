import random
from BaseTypes import Point


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


# q is on line(p,r)
def on_segment(q, p, r):
    if ((q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
           (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
        return True
    return False


# get the cross of two segments (with begin & end nodes), if not cross returns False
def line_cross(line1, line2):
    if line1[0].equal(line2[0]) or line1[0].equal(line2[1]):
        return line1[0]
    if line1[1].equal(line2[0]) or line1[1].equal(line2[1]):
        return line1[1]

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

    res = intersection(L1, L2)
    return res
    if res and on_segment(res, line1[0], line1[1]) and on_segment(res, line2[0], line2[1]):
        return res
    else:
        return False
