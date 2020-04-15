import matplotlib.pyplot as plt
from City import City
from RoadTypes import Segment
import numpy as np

city = City()
city.generate()

for segment in city.segments:
    plt.plot(
        [segment.r.start.x,
        segment.r.end.x],
        [segment.r.start.y,
        segment.r.end.y]
    )
plt.show()
