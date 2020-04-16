import matplotlib.pyplot as plt
from City import City
from RoadTypes import Segment
import numpy as np
import time

def draw(debug = False):
    if debug:
        plt.ion()
        for segment in city.segments:
            if segment.q['highway']:
                plt.plot(
                [segment.r.start.x,
                segment.r.end.x],
                [segment.r.start.y,
                segment.r.end.y],
                color = 'r',
                linewidth = segment.width/2
            )
            else:
                plt.plot(
                    [segment.r.start.x,
                    segment.r.end.x],
                    [segment.r.start.y,
                    segment.r.end.y],
                    color = 'b',
                    linewidth = segment.width/2
                )
            plt.draw()
            plt.pause(0.001)

    else:
        for segment in city.segments:
            if segment.q['highway']:
                plt.plot(
                [segment.r.start.x,
                segment.r.end.x],
                [segment.r.start.y,
                segment.r.end.y],
                color = 'b',
                linewidth = segment.width/2
            )
            else:
                plt.plot(
                    [segment.r.start.x,
                    segment.r.end.x],
                    [segment.r.start.y,
                    segment.r.end.y],
                    color = 'b',
                    linewidth = segment.width/2
                )
        plt.show()


city = City()
city.generate()


print(len(city.segments))
draw(False)

