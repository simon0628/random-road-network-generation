import matplotlib.pyplot as plt
from City import City
from RoadTypes import Segment
import numpy as np
import time

def draw():
    for segment in city.segments:
        if segment.meta['highway']:
            plt.plot(
            [segment.r.start.x,
            segment.r.end.x],
            [segment.r.start.y,
            segment.r.end.y],
            color = 'r',
            linewidth = segment.meta['width']/2
        )
        else:
            plt.plot(
                [segment.r.start.x,
                segment.r.end.x],
                [segment.r.start.y,
                segment.r.end.y],
                color = 'b' if segment.meta['snapped'] else 'g',
                linewidth = segment.meta['width']/2
            )
    plt.show()


city = City()
city.generate(False)


print(len(city.segments))
draw()

