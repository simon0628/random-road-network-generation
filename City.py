from RoadTypes import Segment
from Constants import *
from Utils import *
from Point import *
import noise
import math
from pyqtree import Index
import logging

class City(object):
    def __init__(self):
        super(City, self).__init__()
        self.heatmap = HeatMap()
        self.segments = list()
        self.road_id = 0

        self.spindex = Index(bbox=(
            QUADTREE_PARAMS_X,
            QUADTREE_PARAMS_Y,
            QUADTREE_PARAMS_X + QUADTREE_PARAMS_W,
            QUADTREE_PARAMS_Y + QUADTREE_PARAMS_H
        ))

    def gen_segment(self, start, delay, meta, dir, new_segment = False): 
        length = 0
        if meta['highway']:
            length = HIGHWAY_SEGMENT_LENGTH + rand_in_limit(HIGHWAY_SEGMENT_LENGTH_OFFSET_LIMIT)
        else:
            length = STREET_SEGMENT_LENGTH + rand_in_limit(STREET_SEGMENT_LENGTH_OFFSET_LIMIT)

        end = Point(
            start.x + length*math.sin(math.radians(dir)),
            start.y + length*math.cos(math.radians(dir))
        )
        if new_segment:
            meta['id'] = self.road_id
            self.road_id += 1
            if meta['highway']:
                meta['width'] = HIGHWAY_SEGMENT_WIDTH
            else:
                meta['width'] = STREET_SEGMENT_WIDTH + \
                    rand_in_limit(STREET_SEGMENT_WIDTH_OFFSET_LIMIT)

        return Segment(start, end, delay, meta)

    def gen_segment_follow(self, previous_segment, dir):
        return self.gen_segment(
            previous_segment.road.end,
            STRENCH_TIME_DELAY_HIGHWAY if previous_segment.meta['highway'] else STRENCH_TIME_DELAY_STREET,
            previous_segment.meta,
            dir,
            new_segment = False
        )

    def gen_segment_branch(self, previous_segment, dir):
        new_meta = previous_segment.meta

        if previous_segment.meta['highway']:
            if rand_hit_thershold(HIGHWAY_DEGENERATE_PROBABILITY):
                new_meta['highway'] = False
                return self.gen_segment(
                    previous_segment.road.end,
                    BRANCH_TIME_DELAY_HIGHWAY,
                    new_meta,
                    dir,
                    new_segment = True
                )
            else:
                return self.gen_segment(
                    previous_segment.road.end,
                    BRANCH_TIME_DELAY_HIGHWAY,
                    new_meta,
                    dir,
                    new_segment = True
                )
        else:
            return self.gen_segment(
                previous_segment.road.end,
                BRANCH_TIME_DELAY_STREET,
                new_meta,
                dir,
                new_segment = True
            )

    def globalGoals(self, previous_segment):
        proposed_segments = list()

        logging.info("previous: " + previous_segment.road.to_string())

        if 'snapped' not in previous_segment.meta or not previous_segment.meta['snapped']:
            straight_follow_segment = self.gen_segment_follow(
                previous_segment, previous_segment.dir() + rand_in_limit(STREET_CURVE_DIRECTION_OFFSET_LIMIT))
            straight_heat = self.heatmap.road_heat(
                straight_follow_segment.road)

            if previous_segment.meta['highway']:
                logging.info("is highway")
                max_heat = None
                max_heat_offset = 0
                for offset in range(-HIGHWAY_CURVE_DIRECTION_OFFSET_LIMIT, HIGHWAY_CURVE_DIRECTION_OFFSET_LIMIT):
                    curve_follow_segment = self.gen_segment_follow(
                        previous_segment, previous_segment.dir() + offset)
                    heat = self.heatmap.road_heat(curve_follow_segment.road)
                    if max_heat is None or heat > max_heat:
                        max_heat = heat
                        max_heat_offset = offset
                curve_follow_segment = self.gen_segment_follow(
                    previous_segment, previous_segment.dir() + max_heat_offset)
                proposed_segments.append(curve_follow_segment)
                logging.info("---gen [highway] curve follow: " + curve_follow_segment.road.to_string())

                if max_heat > HIGHWAY_BRANCH_HEAT_THRESHOLD:
                    if rand_hit_thershold(HIGHWAY_BRANCH_RIGHT_PROBABILITY):
                        leftHighwayBranch = self.gen_segment_branch(
                            previous_segment, previous_segment.dir() - 90 + rand_in_limit(HIGHWAY_BRANCH_DIRECTION_OFFSET_LIMIT))
                        proposed_segments.append(leftHighwayBranch)
                        logging.info("---gen [highway] left branch: " + leftHighwayBranch.road.to_string())

                    if rand_hit_thershold(HIGHWAY_BRANCH_RIGHT_PROBABILITY):
                        rightHighwayBranch = self.gen_segment_branch(
                            previous_segment, previous_segment.dir() + 90 + rand_in_limit(HIGHWAY_BRANCH_DIRECTION_OFFSET_LIMIT))
                        proposed_segments.append(rightHighwayBranch)
                        logging.info("---gen [highway] right branch: " + rightHighwayBranch.road.to_string())

            else:
                if rand_hit_thershold(straight_heat*3):
                    proposed_segments.append(straight_follow_segment)
                    logging.info("---gen [street] follow branch: " + straight_follow_segment.road.to_string())

            if rand_hit_thershold(straight_heat*3):
                if rand_hit_thershold(STREET_BRANCH_LEFT_PROBABILITY):
                    leftBranch = self.gen_segment_branch(previous_segment, previous_segment.dir(
                    ) - 90 + rand_in_limit(STREET_BRANCH_DIRECTION_OFFSET_LIMIT))
                    proposed_segments.append(leftBranch)
                    logging.info("---gen [highway/street] left branch: " + leftBranch.road.to_string())

                if rand_hit_thershold(STREET_BRANCH_RIGHT_PROBABILITY):
                    rightBranch = self.gen_segment_branch(previous_segment, previous_segment.dir(
                    ) + 90 + rand_in_limit(STREET_BRANCH_DIRECTION_OFFSET_LIMIT))
                    proposed_segments.append(rightBranch)
                    logging.info("---gen [highway/street] left branch: " + rightBranch.road.to_string())

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
            cross = line_cross([segment.road.start, segment.road.end], [
                               other.road.start, other.road.end])
            if cross != False:
                if not cross.equal(segment.road.start) and not cross.equal(segment.road.end):
                    # cross other line with small angle
                    if degree < MINIMUM_INTERSECTION_DEVIATION:
                        return False

                    segment.road.end = cross
                    segment.meta['snapped'] = True

            else:
                # 2. snap to crossing within radius check
                if distance_p2p(segment.road.end, other.road.end) <= ROAD_SNAP_DISTANCE:
                    segment.road.end = other.road.end
                    segment.meta['snapped'] = True

                # 3. intersection within radius check
                distance = distance_p2l(segment.road.end, other.road)
                if distance <= ROAD_SNAP_DISTANCE and distance > EPSILON:
                    if degree >= MINIMUM_INTERSECTION_DEVIATION:
                        project_point = point_projection(
                            segment.road.end, other.e.start, other.road.end)
                        segment.road.end = project_point
                        segment.meta['snapped'] = True
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
            if len(self.segments) % 100 == 0:
                print(len(self.segments))
            # pop smallest road(ti, ri, qi) from Q
            min_t = None
            min_index = 0
            for i, segment in enumerate(priority_queue):
                if min_t is None or segment.delay < min_t:
                    min_t = segment.delay
                    min_index = i

            min_segment = priority_queue.pop(min_index)
            accepted = self.localConstraints(min_segment, self.segments)
            if accepted:
                self.append_segment(min_segment)
                newSegments = self.globalGoals(min_segment)
                for i, newSegment in enumerate(newSegments):
                    newSegments[i].delay = min_segment.delay + 1 + newSegments[i].delay
                    priority_queue.append(newSegment)

            else:
                logging.info('segment is rejected!, which is :')
                logging.info('   ' + min_segment.road.to_string())
                logging.info('   is highway: ' + str(min_segment.meta['highway']))


    def append_segment(self, segment):
        self.segments.append(segment)
        self.spindex.insert(segment, (segment.getBox()))


class HeatMap(object):
    def road_heat(self, road):
        return (self.population(road.start.x, road.start.y) + self.population(road.end.x, road.end.y))/2

    def population(self, x, y):
        value1 = (noise.snoise2(x/10000, y/10000) + 1) / 2
        value2 = (noise.snoise2(x/20000 + 500, y/20000 + 500) + 1) / 2
        value3 = (noise.snoise2(x/20000 + 1000, y/20000 + 1000) + 1) / 2
        return pow((value1 * value2 + value3) / 2, 2)


