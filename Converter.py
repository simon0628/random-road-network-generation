import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from datetime import datetime



def generate_osm(nodes, ways, scale, filename, debug = False):
    if debug:
        for node in nodes:
            plt.plot(node.x, node.y, node.color)
        plt.show()

    osm_attrib = {'version': "0.6", 'generator': "xodr_OSM_converter", 'copyright': "Simon",
                    'attribution': "Simon", 'license': "GNU or whatever"}
    osm_root = ET.Element('osm', osm_attrib)

    bounds_attrib = {'minlat': '0', 'minlon': '0',
                        'maxlat': '1', 'maxlon': '1'}
    ET.SubElement(osm_root, 'bounds', bounds_attrib)

    # add all nodes into osm
    for node in nodes:
        node_attrib = {'id': str(node.id), 'visible': 'true', 'version': '1', 'changeset': '1', 'timestamp': datetime.utcnow().strftime(
            '%Y-%m-%dT%H:%M:%SZ'), 'user': 'simon', 'uid': '1', 'lon': str(node.x / scale), 'lat': str(node.y / scale), 'ele':'2'}
        node_root = ET.SubElement(osm_root, 'node', node_attrib)

        ET.SubElement(node_root, 'tag', {'k': "type", 'v': 'Smart'})
        ET.SubElement(node_root, 'tag', {'k': "height", 'v': str(node.z)})
        ET.SubElement(node_root, 'tag', {
                        'k': "minArcRadius", 'v': str(node.max_arcrad)})

    for way_key, way_value in ways.items():
        way_attrib = {'id': str(way_key), 'version': '1', 'changeset': '1',
                        'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'), 'user': 'simon', 'uid': '1'}
        way_root = ET.SubElement(osm_root, 'way', way_attrib)

        # add all nodes of a road
        for way_node in way_value.nodes_id:
            ET.SubElement(way_root, 'nd', {'ref': str(way_node)})

        # ET.SubElement(way_root, 'tag', {'k': "highway", 'v':'tertiary'})
        ET.SubElement(way_root, 'tag', {
                        'k': "name", 'v': 'road'+str(way_value.id)})
        ET.SubElement(way_root, 'tag', {
                        'k': "streetWidth", 'v': str(way_value.width)})
        # ET.SubElement(way_root, 'tag', {
        #                 'k': "streetOffset", 'v': str(way_value.offset)})
        # ET.SubElement(way_root, 'tag', {
        #                 'k': "sidewalkWidthLeft", 'v': str(way_value.widthleftwalk)})
        # ET.SubElement(way_root, 'tag', {
        #                 'k': "sidewalkWidthRight", 'v': str(way_value.widthrightwalk)})
        # ET.SubElement(way_root, 'tag', {
        #                 'k': "NbrOfRightLanes", 'v': str(way_value.nrightlanes)})

        # ET.SubElement(way_root, 'tag', {
        #                 'k': "nLanesTotal", 'v': str(way_value.nrightlanes + way_value.nleftlanes)})
        # if way_value.nrightlanes == 0 or way_value.nleftlanes == 0:
        #     ET.SubElement(way_root, 'tag', {
        #         'k': "Centerline", 'v': "none"})

    tree = ET.ElementTree(osm_root)
    tree.write(filename)

