import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from datetime import datetime
from external.BaseTypes import Point


class OSMNode(Point):
    """docstring for Node"""

    def __init__(self, node_id, x, y, z, attrs):

        super(OSMNode, self).__init__(x, y)

        if not isinstance(attrs, dict):
            raise TypeError('attrs should be type of dict')

        self.id = node_id
        self.z = z
        self.attrs = attrs


class OSMWay(object):
    """docstring for Way"""

    def __init__(self, way_id, nodes_id, attrs):

        super(OSMWay, self).__init__()
        if not isinstance(attrs, dict):
            raise TypeError('attrs should be type of dict')

        self.id = way_id
        self.nodes_id = nodes_id
        self.attrs = attrs


class OSMGenerator(object):
    def __init__(self, nodes, ways, scale):
        self.nodes = nodes
        self.ways = ways
        self.scale = scale

    def generate(self, filename, debug=False):

        if debug:
            print('OSM info: ')
            print('    node number: ' + str(len(self.nodes)))
            print('    way number: ' + str(len(self.ways)))

        # headers
        osm_attrib = {'version': "0.6", 'generator': "xodr_OSM_converter", 'copyright': "Simon",
                      'attribution': "Simon", 'license': "GNU or whatever"}
        osm_root = ET.Element('osm', osm_attrib)

        bounds_attrib = {'minlat': '0', 'minlon': '0',
                         'maxlat': '1', 'maxlon': '1'}
        ET.SubElement(osm_root, 'bounds', bounds_attrib)

        # add all nodes into osm
        for node in self.nodes:
            node_attrib = {'id': str(node.id), 'visible': 'true', 'version': '1', 'changeset': '1',
                           'timestamp': datetime.utcnow().strftime(
                               '%Y-%m-%dT%H:%M:%SZ'), 'user': 'simon', 'uid': '1', 'lon': str(node.x / self.scale),
                           'lat': str(node.y / self.scale), 'ele': '2'}
            node_root = ET.SubElement(osm_root, 'node', node_attrib)

            for tag_key, tag_value in node.attrs.items():
                ET.SubElement(node_root, 'tag', {'k': tag_key, 'v': str(tag_value)})

        # add all roads
        for way_key, way_value in self.ways.items():
            way_attrib = {'id': str(way_key), 'version': '1', 'changeset': '1',
                          'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'), 'user': 'simon', 'uid': '1'}
            way_root = ET.SubElement(osm_root, 'way', way_attrib)

            # add all nodes of a road
            for way_node in way_value.nodes_id:
                ET.SubElement(way_root, 'nd', {'ref': str(way_node)})

            for tag_key, tag_value in way_value.attrs.items():
                ET.SubElement(way_root, 'tag', {'k': tag_key, 'v': str(tag_value)})

        tree = ET.ElementTree(osm_root)
        tree.write(filename)
