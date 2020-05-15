import matplotlib.pyplot as plt
from City import City
from RoadTypes import Segment
import numpy as np
import time
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

logging.basicConfig(filename='road_generate.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT, filemode='w')


def draw():
    for segment in city.segments:
        if segment.meta['highway']:
            plt.plot(
            [segment.road.start.x,
            segment.road.end.x],
            [segment.road.start.y,
            segment.road.end.y],
            color = 'k',
            linewidth = segment.meta['width']
        )
        else:
            plt.plot(
                [segment.road.start.x,
                segment.road.end.x],
                [segment.road.start.y,
                segment.road.end.y],
                color = 'k',
                linewidth = segment.meta['width']
            )
    for node in city.nodes:
        if len(node.r) >= 2 and len(set(node.r)) == 2:
            print(node.r)
            l = str(node.r)
            plt.plot(node.x, node.y, 'ro', label=l)
    
    plt.show()


city = City()
city.generate()


print(len(city.segments))
draw()

