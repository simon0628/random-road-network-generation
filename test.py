import matplotlib.pyplot as plt
from City import City
from RoadTypes import Segment
import numpy as np
import time

city = City()
city.generate()

# plt.axis([-5000, 5000, -5000, 5000])
plt.ion()

for segment in city.segments:
    if segment.q['highway']:
        plt.plot(
        [segment.r.start.x,
        segment.r.end.x],
        [segment.r.start.y,
        segment.r.end.y],
        color = 'r'
    )
    else:
        plt.plot(
            [segment.r.start.x,
            segment.r.end.x],
            [segment.r.start.y,
            segment.r.end.y],
            color = 'b'
        )
    # time.sleep(0.1)
    plt.draw()
    plt.pause(0.0001)
