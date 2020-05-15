from src.Point import *
from src.OSMGenerator import OSMNode, OSMWay


class Road(object):
    def __init__(self, start, end):
        super(Road, self).__init__()
        self.start = start
        self.end = end
    def to_string(self):
        res = 'start: ( %f, %f )' % (self.start.x, self.start.y)
        res += ' end: ( %f, %f )' % (self.end.x, self.end.y)
        return res


class Segment(object):
    def __init__(self, start, end, delay, meta):
        super(Segment, self).__init__()
        self.road = Road(start, end)
        # time-step delay before this road is evaluated
        self.delay = 0 if delay is None else delay
        # meta-information relevant to global goals
        self.meta = dict() if meta is None else meta

        self.successor = list()
        self.predecessor = list()

        self.length = distance_p2p(start, end)
        # self.road_id = None

    def dir(self):
        vector = self.road.end.subtract(self.road.start)
        cross = cross_product_v2v(Point(0, 1), vector)

        if cross > 0:
            sign = 1
        elif cross == 0:
            sign = 0
        else:
            sign = -1

        return -1 * sign * angle_v2v(Point(0, 1), vector)

    def getBox(self):
        x1 = self.road.start.x
        x2 = self.road.end.x
        y1 = self.road.start.y
        y2 = self.road.end.y
        return min([x1, x2]), min([y1, y2]), max([x1, x2]), max([y1, y2])


class CityNode(OSMNode):
    """docstring for Node"""

    def __init__(self, node_id, x, y):
        attrs = dict()
        attrs['type'] = 'Smart'
        super(CityNode, self).__init__(node_id, x, y, 0, attrs)
        

class CityWay(OSMWay):
    """docstring for Way"""

    def __init__(self, way_id, nodes_id, is_highway, length):
        attrs = dict()
        attrs['name'] = 'road' + str(way_id)
        attrs['streetWidth'] = 0
        super(CityWay, self).__init__(way_id, nodes_id, attrs)

        self.is_highway = is_highway
        self.length = length

    def set_width(self, width):
        self.attrs['streetWdith'] = width



