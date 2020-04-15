from RoadTypes import Segment, Point
from Constants import *
from Utils import *
from Point import *
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

    def segmentUsingDirection(self, start, t, q, dir, length, width = None):
        # default to east
        end = Point(
            start.x + length*math.sin(math.radians(dir)),
            start.y + length*math.cos(math.radians(dir))
        )
        return Segment(start, end, t, q, width)

    def gen_segment_follow(self, previous_segment, dir):
        return self.segmentUsingDirection(
            previous_segment.r.end,
            0,
            previous_segment.q,
            dir,
            previous_segment.length,
            previous_segment.width
        )

    def gen_segment_branch(self, previous_segment, dir):
        if previous_segment.q['highway']:
            if random.random() < HIGHWAY_DEGENERATE_PROBABILITY:
                return self.segmentUsingDirection(
                            previous_segment.r.end,
                            BRANCH_TIME_DELAY_HIGHWAY,
                            {'highway': False},
                            dir,
                            STREET_SEGMENT_LENGTH + rand_in_limit(STREET_SEGMENT_LENGTH_OFFSET_LIMIT)
                        )
            else:
                return self.segmentUsingDirection(
                            previous_segment.r.end,
                            BRANCH_TIME_DELAY_HIGHWAY,
                            {'highway': True},
                            dir,
                            HIGHWAY_SEGMENT_LENGTH + rand_in_limit(HIGHWAY_SEGMENT_LENGTH_OFFSET_LIMIT)
                        )
        else:
            return self.segmentUsingDirection(
                        previous_segment.r.end,
                        BRANCH_TIME_DELAY_STREET,
                        {'highway': False},
                        dir,
                        STREET_SEGMENT_LENGTH + rand_in_limit(STREET_SEGMENT_LENGTH_OFFSET_LIMIT)
                    )

    def globalGoals(self, previous_segment):
        proposed_segments = list()
        if 'snapped' not in previous_segment.q or not previous_segment.q['snapped']:

            if previous_segment.q['highway']:
                max_heat = None
                max_heat_offset = 0
                for offset in range(-HIGHWAY_CURVE_DIRECTION_OFFSET_LIMIT, HIGHWAY_CURVE_DIRECTION_OFFSET_LIMIT):
                    curve_follow_segment = self.gen_segment_follow(
                        previous_segment, previous_segment.dir() + offset)
                    heat = self.heatmap.road_heat(curve_follow_segment.r)
                    if max_heat is None or heat > max_heat:
                        max_heat = heat
                        max_heat_offset = offset
                curve_follow_segment = self.gen_segment_follow(
                    previous_segment, previous_segment.dir() + max_heat_offset)
                proposed_segments.append(curve_follow_segment)

                if max_heat > HIGHWAY_BRANCH_HEAT_THRESHOLD:
                    if rand_hit_thershold(HIGHWAY_BRANCH_RIGHT_PROBABILITY):
                        leftHighwayBranch = self.gen_segment_branch(
                            previous_segment, previous_segment.dir() - 90 + rand_in_limit(HIGHWAY_BRANCH_DIRECTION_OFFSET_LIMIT))
                        proposed_segments.append(leftHighwayBranch)
                    else:
                        rightHighwayBranch = self.gen_segment_branch(
                            previous_segment, previous_segment.dir() + 90 + rand_in_limit(HIGHWAY_BRANCH_DIRECTION_OFFSET_LIMIT))
                        proposed_segments.append(rightHighwayBranch)

            else:
                straight_follow_segment = self.gen_segment_follow(
                    previous_segment, previous_segment.dir() + rand_in_limit(STREET_CURVE_DIRECTION_OFFSET_LIMIT))
                straight_heat = self.heatmap.road_heat(
                    straight_follow_segment.r)
                if straight_heat > NORMAL_BRANCH_POPULATION_THRESHOLD:
                    proposed_segments.append(straight_follow_segment)

                if rand_hit_thershold(STREET_BRANCH_PROBABILITY):
                    if rand_hit_thershold(STREET_BRANCH_RIGHT_PROBABILITY):
                        leftBranch = self.gen_segment_branch(previous_segment, previous_segment.dir(
                        ) - 90 + rand_in_limit(STREET_BRANCH_DIRECTION_OFFSET_LIMIT))
                        proposed_segments.append(leftBranch)
                    else:
                        rightBranch = self.gen_segment_branch(previous_segment, previous_segment.dir(
                        ) + 90 + rand_in_limit(STREET_BRANCH_DIRECTION_OFFSET_LIMIT))
                        proposed_segments.append(rightBranch)

        return proposed_segments

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
                if distance_p2p(segment.r.end, other.r.end) <= ROAD_SNAP_DISTANCE:
                    segment.r.end = other.r.end
                    segment.q['snapped'] = True

                # 3. intersection within radius check
                distance = distance_p2l(segment.r.end, other.r)
                if distance <= ROAD_SNAP_DISTANCE and distance > EPSILON:
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
    def road_heat(self, r):
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
