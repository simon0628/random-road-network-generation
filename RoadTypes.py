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
        return math.acos((self.x * p2.x + self.y * p2.y)/ (length1 * length2)) * 180 / math.pi

    def equal(self, p2):
        if self.distance(p2) < EPSILON:
            return True
        else:
            return False

    def distance(self, t):
        if isinstance(t, Point):
            return math.sqrt((t.y - self.y)**2 + (t.x - self.x)**2)
        elif isinstance(t, Segment):
            y1 = t.start_p.y
            y2 = t.end_p.y
            x1 = t.start_p.x
            x2 = t.end_p.x
            x0 = self.x
            y0 = self.y
            return (math.fabs((y2 - y1) * x0 +(x1 - x2) * y0 + ((x2 * y1) -(x1 * y2)))) / (math.sqrt(pow(y2 - y1, 2) + pow(x1 - x2, 2)));

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
        self.roadRevision = 0
        self.dirRevision = None
        self.lengthRevision = None

        self.cachedDir = None
        self.cachedLength = None

        self.successor = list()
        self.predecessor = list()
    
        self.length = start.distance(end)
        # self.road_id = None 

    def setStart(self, start):
        self.start = start
        self.roadRevision += 1

    def setEnd(self, end):
        self.end = end
        self.roadRevision += 1

    def getDir(self):
        vector = self.r.end.subtractPoints(self.r.start)
        cross = Point(0, 1).crossProduct(vector)
        if cross > 0:
            sign = 1
        elif cross == 0:
            sign = 0
        else:
            sign = -1

        self.cachedDir = -1 * sign * Point(0, 1).angleBetween(vector)
        return self.cachedDir

    def startIsBackwards(self):
        if len(self.predecessor) > 0:
            return self.start.equal(self.predecessor[0].start) or self.start.equal(self.predecessor[0].end)
        else:
            return self.end.equal(self.successor[0].start) or self.end.equal(self.successor[0].end)

    def endContaining(self, seg2):
        if self.predecessor.index(seg2) != -1:
            return self.start if self.startIsBackwards else self.end
        elif self.successor.index(seg2) != -1:
            return self.end if self.startIsBackwards else self.start


