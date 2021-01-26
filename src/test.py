from City import City
import logging
from external.OSMGenerator import *
import argparse
import numpy as np
import matplotlib.pyplot as plt

RUNTIME_DIR = "../runtime/"
LOG_DIR = RUNTIME_DIR+"log/"
DATA_DIR = RUNTIME_DIR+"out/"


def init_logging(debug = False):
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%m/%d/%Y %H:%M:%S %p"

    if debug:
        logging.basicConfig(
            filename=LOG_DIR + 'road-gen-DEBUG.log',
            level=logging.DEBUG,
            format=log_format,
            datefmt=date_format,
            filemode='w')
    else:
        logging.basicConfig(
            filename=LOG_DIR + 'road-gen-INFO.log',
            level=logging.INFO,
            format=log_format,
            datefmt=date_format,
            filemode='w')


def draw(filename, debug = False):

    u = np.linspace(-20000, 20000, 1000)
    x, y = np.meshgrid(u, u)
    f = np.vectorize(city.heatmap.population)
    z = f(x, y)
    # z = heatmap.population(x, y)
    plt.contourf(x, y, z)

    for segment in city.segments:
        width = city.ways[segment.meta['id']].get_width()
        plt.plot(
            [segment.start.x,
             segment.end.x],
            [segment.start.y,
             segment.end.y],
            color='k',
            linewidth=width
        )

    if debug:
        # for node in city.nodes:
        #     plt.plot(node.x, node.y, 'r.')
        plt.show()

    plt.savefig(filename, dpi=512)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A random road generator')
    parser.add_argument('--debug', type=bool, default=False, help='Is using debug mode')
    parser.add_argument('--road_num', type=int, default=2000, help='Road number to generate')
    parser.add_argument('--generate', type=bool, default=True, help='Should generate road OSM file')
    parser.add_argument('--osm_filename', type=str, default='test.osm', help='Output OSM file name')
    parser.add_argument('--plt_filename', type=str, default='test.png', help='Output OSM file name')
    args = parser.parse_args()

    init_logging(args.debug)
    print(args)
    print('')

    print('Start generating city...')
    city = City(args.road_num)
    city.generate()
    print('Done generate, segment num=%d, road num=%d' % (len(city.segments), len(city.ways)))
    print('')

    if args.generate:
        osm = OSMGenerator(city.nodes, city.ways, 1000000)
        print('Writing OSM file...')
        osm.generate(DATA_DIR + args.osm_filename, args.debug)
        print('Written to ' + DATA_DIR + args.osm_filename)
        print('')

    print('Drawing...')
    draw(DATA_DIR + args.plt_filename, args.debug)
    print('Saved to ' + DATA_DIR + args.plt_filename)
    print('All done')
