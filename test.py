import matplotlib.pyplot as plt
from City import City
from RoadTypes import Segment
import numpy as np
import time
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

logging.basicConfig(filename='road_generate.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT, filemode='w')


def draw(debug = False):
    if debug:
        plt.ion()
        for segment in city.segments:
            if segment.meta['highway']:
                plt.plot(
                [segment.road.start.x,
                segment.road.end.x],
                [segment.road.start.y,
                segment.road.end.y],
                color = 'road',
                linewidth = segment.meta['width']/2
            )
            else:
                plt.plot(
                    [segment.road.start.x,
                    segment.road.end.x],
                    [segment.road.start.y,
                    segment.road.end.y],
                    color = 'b',
                    linewidth = segment.meta['width']/2
                )
            plt.draw()
            plt.pause(0.001)

    else:
        for segment in city.segments:
            if segment.meta['highway']:
                plt.plot(
                [segment.road.start.x,
                segment.road.end.x],
                [segment.road.start.y,
                segment.road.end.y],
                color = 'k',
                linewidth = segment.meta['width']/2
            )
            else:
                plt.plot(
                    [segment.road.start.x,
                    segment.road.end.x],
                    [segment.road.start.y,
                    segment.road.end.y],
                    color = 'k',
                    linewidth = segment.meta['width']/2
                )
        plt.show()


city = City()
city.generate()


print(len(city.segments))
draw(False)

