from RoadTypes import Segment
from Constants import *
from Utils import *
from Point import *
import noise
import math
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

    def gen_segment(self, start, t, q, dir, length, width=None):
        end = Point(
            start.x + length*math.sin(math.radians(dir)),
            start.y + length*math.cos(math.radians(dir))
        )
        return Segment(start, end, t, q, width)

    def gen_segment_follow(self, previous_segment, dir):
        return self.gen_segment(
            previous_segment.r.end,
            STRENCH_TIME_DELAY_HIGHWAY if previous_segment.q['highway'] else STRENCH_TIME_DELAY_STREET,
            previous_segment.q,
            dir,
            previous_segment.length,
            previous_segment.width
        )

    def gen_segment_branch(self, previous_segment, dir):
        if previous_segment.q['highway']:
            if rand_hit_thershold(HIGHWAY_DEGENERATE_PROBABILITY):
                return self.gen_segment(
                    previous_segment.r.end,
                    BRANCH_TIME_DELAY_HIGHWAY,
                    {'highway': False},
                    dir,
                    STREET_SEGMENT_LENGTH +
                    rand_in_limit(STREET_SEGMENT_LENGTH_OFFSET_LIMIT)
                )
            else:
                return self.gen_segment(
                    previous_segment.r.end,
                    BRANCH_TIME_DELAY_HIGHWAY,
                    {'highway': True},
                    dir,
                    HIGHWAY_SEGMENT_LENGTH +
                    rand_in_limit(HIGHWAY_SEGMENT_LENGTH_OFFSET_LIMIT)
                )
        else:
            return self.gen_segment(
                previous_segment.r.end,
                BRANCH_TIME_DELAY_STREET,
                {'highway': False},
                dir,
                STREET_SEGMENT_LENGTH +
                rand_in_limit(STREET_SEGMENT_LENGTH_OFFSET_LIMIT)
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

                if max_heat > HIGHWAY_BRANCH_HEAT_THRESHOLD or rand_hit_thershold(HIGHWAY_BRANCH_PROBABILITY):
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
                if straight_heat > STREET_HEAT_THRESHOLD:
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
        minx, miny, maxx, maxy = segment.getBox()
        matchSegments = self.spindex.intersect(
            (minx - ROAD_SNAP_DISTANCE,
             miny - ROAD_SNAP_DISTANCE,
             maxx + ROAD_SNAP_DISTANCE,
             maxy + ROAD_SNAP_DISTANCE)
        )

        for other in matchSegments:
            degree = min_intersect_degree(other.dir(), segment.dir())

            # 1. intersection check
            cross = line_cross([segment.r.start, segment.r.end], [
                               other.r.start, other.r.end])
            if cross != False:
                if not cross.equal(segment.r.start) and not cross.equal(segment.r.end):
                    # cross other line with small angle
                    if degree < MINIMUM_INTERSECTION_DEVIATION:
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
                    if degree >= MINIMUM_INTERSECTION_DEVIATION:
                        project_point = point_projection(
                            segment.r.end, other.e.start, other.r.end)
                        segment.r.end = project_point
                        segment.q['snapped'] = True
        return True

    def generate(self):
        priority_queue = list()

        init_segment = Segment(Point(0, 0), Point(
            HIGHWAY_SEGMENT_LENGTH, 0), 0, {'highway': True})
        second_segment = Segment(
            Point(0, 0), Point(-HIGHWAY_SEGMENT_LENGTH, 0), 0, {'highway': True})
        priority_queue.append(init_segment)
        priority_queue.append(second_segment)

        while len(priority_queue) > 0 and len(self.segments) < SEGMENT_COUNT_LIMIT:
            # pop smallest r(ti, ri, qi) from Q
            min_t = None
            min_index = 0
            for i, segment in enumerate(priority_queue):
                if min_t is None or segment.t < min_t:
                    min_t = segment.t
                    min_index = i

            min_segment = priority_queue.pop(min_index)
            accepted = self.localConstraints(min_segment, self.segments)
            if accepted:
                self.append_segment(min_segment)
                newSegments = self.globalGoals(min_segment)
                for i, newSegment in enumerate(newSegments):
                    newSegments[i].t = min_segment.t + 1 + newSegments[i].t
                    priority_queue.append(newSegment)

    def append_segment(self, segment):
        self.segments.append(segment)
        self.spindex.insert(segment, (segment.getBox()))


class HeatMap(object):
    def road_heat(self, r):
        return (self.population(r.start.x, r.start.y) + self.population(r.end.x, r.end.y))/2

    def population(self, x, y):
        value1 = (noise.snoise2(x/10000, y/10000) + 1) / 2
        value2 = (noise.snoise2(x/20000 + 500, y/20000 + 500) + 1) / 2
        value3 = (noise.snoise2(x/20000 + 1000, y/20000 + 1000) + 1) / 2
        return pow((value1 * value2 + value3) / 2, 2)


