import math
from Constants import *

class Point(object):

    def __init__(self, x, y):
        super(Point, self).__init__()
        self.x = x
        self.y = y
        self.id = None

    def subtractPoints(self, p2):
        return Point(self.x - p2.x, self.y - p2.y)

    def crossProduct(self, p2):
        return self.x * p2.y - p2.x * self.y 

    def angleBetween(self, p2):
        length1 = math.sqrt(self.x * self.x + self.y * self.y)
        length2 = math.sqrt(p2.x * p2.x + p2.y * p2.y)
        if length1 * length2 == 0:
            return 0
        return math.acos((self.x * p2.x + self.y * p2.y)/ (length1 * length2)) * 180 / math.pi

    def equal(self, p2):
        if self.distance(p2) < EPSILON:
            return True
        else:
            return False

    def distance(self, t):
        if isinstance(t, Point):
            return math.sqrt((t.y - self.y)**2 + (t.x - self.x)**2)
        elif isinstance(t, Road):
            a=t.end.y-t.start.y
            b=t.start.x-t.end.x
            c=t.end.x*t.start.y-t.start.x*t.end.y
            dis=(math.fabs(a*self.x+b*self.y+c))/(math.pow(a*a+b*b,0.5))
            return dis

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

        self.width = HIGHWAY_SEGMENT_WIDTH if q['highway'] else DEFAULT_SEGMENT_WIDTH

        self.successor = list()
        self.predecessor = list()
    
        self.length = start.distance(end)
        # self.road_id = None 

    def setStart(self, start):
        self.start = start

    def setEnd(self, end):
        self.end = end

    def getDir(self):
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


