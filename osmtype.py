class Node(object):
    """docstring for Node"""

    def __init__(self, node_id, x, y, z, max_arcrad=0, color = 'y.'):
        super(Node, self).__init__()
        self.id = node_id
        self.x = x
        self.y = y
        self.z = z
        self.max_arcrad = max_arcrad
        self.color = color


class Way(object):
    """docstring for Way"""

    def __init__(self, way_id, nodes_id, is_highway, length):
        super(Way, self).__init__()
        self.id = way_id

        self.nodes_id = nodes_id
        self.width = 0

        self.is_highway = is_highway
        self.length = length


        self.is_connecting = False

        self.offset = 0
        # self.style = 0
        # self.nrightlanes = 0
        # self.nleftlanes = 0
        # self.widthrightwalk = 0
        # self.widthleftwalk = 0