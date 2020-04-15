import math
from Constants import *
from Utils import rand_in_limit
from Point import Point

class Road(object):
    def __init__(self, start, end):
        super(Road, self).__init__()
        self.start = start
        self.end = end


class Segment(object):
    def __init__(self, start, end, t, q):
        super(Segment, self).__init__()
        self.r = Road(start, end)
        # time-step delay before this road is evaluated
        self.t = 0 if t is None else t
        # meta-information relevant to global goals
        self.q = dict() if q is None else q

        self.width = HIGHWAY_SEGMENT_WIDTH + \
            rand_in_limit(
                STREET_SEGMENT_WIDTH_OFFSET_LIMIT) if q['highway'] else STREET_SEGMENT_WIDTH

        self.successor = list()
        self.predecessor = list()

        self.length = start.distance(end)
        # self.road_id = None

    def setStart(self, start):
        self.start = start

    def setEnd(self, end):
        self.end = end

    def dir(self):
        vector = self.r.end.subtractPoints(self.r.start)
        cross = Point(0, 1).crossProduct(vector)
        if cross > 0:
            sign = 1
        elif cross == 0:
            sign = 0
        else:
            sign = -1

        return -1 * sign * Point(0, 1).angleBetween(vector)

    def getBox(self):
        x1 = self.r.start.x
        x2 = self.r.end.x
        y1 = self.r.start.y
        y2 = self.r.end.y
        return min([x1, x2]), min([y1, y2]), max([x1, x2]), max([y1, y2])

