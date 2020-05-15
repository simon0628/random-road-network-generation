import math

EPSILON = 1e-2


class Point(object):

    def __init__(self, x, y):
        super(Point, self).__init__()
        self.x = x
        self.y = y

    def subtract(self, p2):
        return Point(self.x - p2.x, self.y - p2.y)

    def equal(self, p2):
        if self.distance(p2) < EPSILON:
            return True
        else:
            return False

    def distance(self, t):
        return math.sqrt((t.y - self.y)**2 + (t.x - self.x)**2)


def distance_p2l(p, l):
    a = l.end.y-l.start.y
    b = l.start.x-l.end.x
    c = l.end.x*l.start.y-l.start.x*l.end.y
    dis = (math.fabs(a*p.x+b*p.y+c))/(math.pow(a*a+b*b, 0.5))
    return dis


def distance_p2p(p1, p2):
    return p1.distance(p2)


def angle_v2v(v1, v2):
    length1 = math.sqrt(v1.x * v1.x + v1.y * v1.y)
    length2 = math.sqrt(v2.x * v2.x + v2.y * v2.y)
    if length1 * length2 == 0:
        return 0
    return math.acos((v1.x * v2.x + v1.y * v2.y) / (length1 * length2)) * 180 / math.pi


def cross_product_v2v(v1, v2):
    return v1.x * v2.y - v2.x * v1.y


def dot_product_v2v(v1, v2):
    return v1.x * v2.x + v1.y * v2.y


def point_projection(a, b, p):
    ap = Point(p.x-a.x, p.y-a.y)
    ab = Point(b.x-a.x, b.y-a.y)
    k = dot_product_v2v(ap, ab)/dot_product_v2v(ab, ab)
    result = Point(
        a.x + ab.x * k,
        a.y + ab.y * k
    )
    return result
