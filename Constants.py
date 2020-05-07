
EPSILON = 1e-2

SEGMENT_COUNT_LIMIT = 2000

# length
STREET_SEGMENT_LENGTH = 300
STREET_SEGMENT_LENGTH_OFFSET_LIMIT = 0
HIGHWAY_SEGMENT_LENGTH = 400
HIGHWAY_SEGMENT_LENGTH_OFFSET_LIMIT = 0

# width
STREET_SEGMENT_WIDTH = 5
STREET_SEGMENT_WIDTH_OFFSET_LIMIT = 1
HIGHWAY_SEGMENT_WIDTH = 10

# extend
HIGHWAY_CURVE_DIRECTION_OFFSET_LIMIT = 3
STREET_CURVE_DIRECTION_OFFSET_LIMIT = 3

# heat
STREET_HEAT_THRESHOLD = 0.1
HIGHWAY_BRANCH_HEAT_THRESHOLD = 0.1
STREET_BRANCH_HEAT_THRESHOLD = 0.1

# branch
STREET_BRANCH_PROBABILITY = 0.6
STREET_BRANCH_RIGHT_PROBABILITY = 0.4
STREET_BRANCH_LEFT_PROBABILITY = 0.4
HIGHWAY_BRANCH_PROBABILITY = 0.2
HIGHWAY_BRANCH_RIGHT_PROBABILITY = 0.05
HIGHWAY_BRANCH_LEFT_PROBABILITY = 0.05

HIGHWAY_BRANCH_DIRECTION_OFFSET_LIMIT = 3
STREET_BRANCH_DIRECTION_OFFSET_LIMIT = 0

# degeneration
HIGHWAY_DEGENERATE_PROBABILITY = 0.8

# time delay: control the ratio of highway & street
BRANCH_TIME_DELAY_HIGHWAY = 5
BRANCH_TIME_DELAY_STREET = 0
EXTEND_TIME_DELAY_HIGHWAY = 0
EXTEND_TIME_DELAY_STREET = 0

# local constrains
MINIMUM_INTERSECTION_DEVIATION = 30 
ROAD_SNAP_DISTANCE = 50
QUADTREE_PARAMS_X = -20000
QUADTREE_PARAMS_Y = -20000
QUADTREE_PARAMS_W = -40000
QUADTREE_PARAMS_H = -40000
