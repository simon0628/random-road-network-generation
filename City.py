from RoadTypes import Segment, Point
from Constants import *
from Utils import *
import noise
import math
import random
from pyqtree import Index


class City(object):
    def __init__(self):
        super(City, self).__init__()
        self.heatmap = HeatMap()
        self.segments = list()

        self.spindex = Index(bbox=(
            QUADTREE_PARAMS_X,
            QUADTREE_PARAMS_Y,
            QUADTREE_PARAMS_X + QUADTREE_PARAMS_W,
            QUADTREE_PARAMS_Y + QUADTREE_PARAMS_H
        ))

    def direction_offset(self, limit):
        return limit * (random.random() - 0.5) * 2

    def segmentUsingDirection(self, start, t, q, dir, length):
        if length is None:
            length = STREET_SEGMENT_WIDTH
        # default to east
        end = Point(
            start.x + length*math.sin(math.radians(dir)),
            start.y + length*math.cos(math.radians(dir))
        )
        return Segment(start, end, t, q)

    def gen_segment_follow(self, previous_segment, dir):
        return self.segmentUsingDirection(
            previous_segment.r.end,
            0,
            previous_segment.q,
            dir,
            previous_segment.length
        )

    def segmentBranch(self, previous_segment, dir):
        delay = 0
        if previous_segment.q['highway']:
            delay = NORMAL_BRANCH_TIME_DELAY_FROM_HIGHWAY
        else:
            delay = NORMAL_BRANCH_TIME_DELAY_FROM_STREET

        return self.segmentUsingDirection(
            previous_segment.r.end,
            delay,
            {'highway': False},
            dir,
            STREET_SEGMENT_LENGTH
        )

    def globalGoals(self, previous_segment):
        newBranches = list()
        if 'snapped' not in previous_segment.q or not previous_segment.q['snapped']:

            straight_follow = self.gen_segment_follow(
                previous_segment, previous_segment.dir())
            straightPop = self.heatmap.popOnRoad(straight_follow.r)

            if previous_segment.q['highway']:
                curve_follow = self.gen_segment_follow(
                    previous_segment, previous_segment.dir() + self.direction_offset(CURVE_DIRECTION_OFFSET_LIMIT))
                randomPop = self.heatmap.popOnRoad(curve_follow.r)

                roadPop = randomPop
                if randomPop > straightPop:
                    newBranches.append(curve_follow)
                else:
                    newBranches.append(straight_follow)
                    roadPop = straightPop

                if roadPop > HIGHWAY_BRANCH_POPULATION_THRESHOLD:
                    if random.random() < HIGHWAY_BRANCH_PROBABILITY:
                        leftHighwayBranch = self.gen_segment_follow(
                            previous_segment, previous_segment.dir() - 90 + self.direction_offset(BRANCH_DIRECTION_OFFSET_LIMIT))
                        newBranches.append(leftHighwayBranch)
                    elif random.random() < HIGHWAY_BRANCH_PROBABILITY:
                        rightHighwayBranch = self.gen_segment_follow(
                            previous_segment, previous_segment.dir() + 90 + self.direction_offset(BRANCH_DIRECTION_OFFSET_LIMIT))
                        newBranches.append(rightHighwayBranch)
            elif straightPop > NORMAL_BRANCH_POPULATION_THRESHOLD:
                newBranches.append(straight_follow)

            if straightPop > NORMAL_BRANCH_POPULATION_THRESHOLD:
                if random.random() < STREET_BRANCH_PROBABILITY:
                    leftBranch = self.segmentBranch(previous_segment, previous_segment.dir(
                    ) - 90 + self.direction_offset(BRANCH_DIRECTION_OFFSET_LIMIT))
                    newBranches.append(leftBranch)
                else:
                    rightBranch = self.segmentBranch(previous_segment, previous_segment.dir(
                    ) + 90 + self.direction_offset(BRANCH_DIRECTION_OFFSET_LIMIT))
                    newBranches.append(rightBranch)
        # setup links
        return newBranches

    def localConstraints(self, segment, segments):
        # return True
        # TODO

        minx, miny, maxx, maxy = segment.getBox()
        matchSegments = self.spindex.intersect(
            (minx - ROAD_SNAP_DISTANCE,
             miny - ROAD_SNAP_DISTANCE,
             maxx + ROAD_SNAP_DISTANCE,
             maxy + ROAD_SNAP_DISTANCE)
        )

        for other in matchSegments:
            minDegree = min_intersect_degree(other.dir(), segment.dir())

            # if minDegree < EPSILON:
            #     d1 = segment.r.start.distance(other.r)
            #     d2 = segment.r.end.distance(other.r)
            #     if min([d1, d2]) < EPSILON:
            #         if d1 < d2:
            #             if not segment.r.start.equal(other.r.start) and not segment.r.start.equal(other.r.end):
            #                 return False
            #         else:
            #             if not segment.r.end.equal(other.r.start) and not segment.r.end.equal(other.r.end):
            #                 return False

            # 1. intersection check
            cross = line_cross([segment.r.start, segment.r.end], [
                               other.r.start, other.r.end])
            if cross != False:
                if not cross.equal(segment.r.start) and not cross.equal(segment.r.end):
                    # cross other line with small angle
                    if minDegree < MINIMUM_INTERSECTION_DEVIATION:
                        return False

                    segment.r.end = cross
                    segment.q['snapped'] = True

            else:
                # 2. snap to crossing within radius check
                if segment.r.end.distance(other.r.end) <= ROAD_SNAP_DISTANCE:
                    segment.r.end = other.r.end
                    segment.q['snapped'] = True

                # 3. intersection within radius check
                if segment.r.end.distance(other.r) <= ROAD_SNAP_DISTANCE and segment.r.end.distance(other.r) > EPSILON:
                    if minDegree >= MINIMUM_INTERSECTION_DEVIATION:
                        project_point = point_projection(
                            segment.r.end, other.e.start, other.r.end)
                        segment.r.end = project_point
                        segment.q['snapped'] = True
        return True

    def generate(self):
        priorityQ = list()

        rootSegment = Segment(Point(0, 0), Point(
            HIGHWAY_SEGMENT_LENGTH, 0), 0, {'highway': True})
        oppositeDirection = Segment(
            Point(0, 0), Point(-HIGHWAY_SEGMENT_LENGTH, 0), 0, {'highway': True})
        priorityQ.append(rootSegment)
        priorityQ.append(oppositeDirection)

        while len(priorityQ) > 0 and len(self.segments) < SEGMENT_COUNT_LIMIT:
            # pop smallest r(ti, ri, qi) from Q
            minT = None
            minT_i = 0
            for i, segment in enumerate(priorityQ):
                if minT is None or segment.t < minT:
                    minT = segment.t
                    minT_i = i

            minSegment = priorityQ.pop(minT_i)
            accepted = self.localConstraints(minSegment, self.segments)
            if accepted:
                self.appendSegment(minSegment)
                newSegments = self.globalGoals(minSegment)
                for i, newSegment in enumerate(newSegments):
                    newSegments[i].t = minSegment.t + 1 + newSegments[i].t
                    priorityQ.append(newSegment)

    def appendSegment(self, segment):
        self.segments.append(segment)
        self.spindex.insert(segment, (segment.getBox()))


class HeatMap(object):
    def popOnRoad(self, r):
        return (self.populationAt(r.start.x, r.start.y) + self.populationAt(r.end.x, r.end.y))/2

    def populationAt(self, x, y):
        value1 = (noise.snoise2(x/10000, y/10000) + 1) / 2
        value2 = (noise.snoise2(x/20000 + 500, y/20000 + 500) + 1) / 2
        value3 = (noise.snoise2(x/20000 + 1000, y/20000 + 1000) + 1) / 2
        return pow((value1 * value2 + value3) / 2, 2)


# class City(object):
#     # self.xmin = 0
#     # self.xmax = 0
#     # self.ymin = 0
#     # self.ymax = 0
#     def __init__(self):
#         super(City, self).__init__()
#         self.points = list()
#         self.roads = list()

# class potential_field(object):
#     alpha = 1
#     beta = 1
#     def dmin(self, x, C):
#         min_distance = -1
#         for c in C.points:
#             if x.distance(c) < min_distance:
#                 min_distance = x.distance(c)
#         return min_distance

#     def potential(self, x, C, alpha, beta):
#         part1 = alpha / self.dmin(x, C) - beta / math.sqrt(self.dmin(x, C))
#         part2 = 0
#         for road in C.roads:
#             part2 = part2 + road.length / math.sqrt(x.distance(road))
#         return part1 * part2
