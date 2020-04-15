import math
from Constants import *
from Utils import rand_in_limit
from Point import *

class Road(object):
    def __init__(self, start, end):
        super(Road, self).__init__()
        self.start = start
        self.end = end


class Segment(object):
    def __init__(self, start, end, t, q, width = None):
        super(Segment, self).__init__()
        self.r = Road(start, end)
        # time-step delay before this road is evaluated
        self.t = 0 if t is None else t
        # meta-information relevant to global goals
        self.q = dict() if q is None else q

        self.width = 0
        if width is None:
            if q['highway']:
                self.width = HIGHWAY_SEGMENT_WIDTH
            else:
                self.width = STREET_SEGMENT_WIDTH + rand_in_limit(STREET_SEGMENT_WIDTH_OFFSET_LIMIT)
        else:
            self.width = width

        self.successor = list()
        self.predecessor = list()

        self.length = distance_p2p(start, end)
        # self.road_id = None

    def dir(self):
        vector = self.r.end.subtract(self.r.start)
        cross = cross_product_v2v(Point(0, 1), vector)
        
        if cross > 0:
            sign = 1
        elif cross == 0:
            sign = 0
        else:
            sign = -1

        return -1 * sign * angle_v2v(Point(0, 1), vector)

    def getBox(self):
        x1 = self.r.start.x
        x2 = self.r.end.x
        y1 = self.r.start.y
        y2 = self.r.end.y
        return min([x1, x2]), min([y1, y2]), max([x1, x2]), max([y1, y2])

