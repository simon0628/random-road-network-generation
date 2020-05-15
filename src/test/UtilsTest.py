from RoadTypes import *
from Constants import *
from Utils import *
from Point import *
import noise
import math
from pyqtree import Index
import matplotlib.pyplot as plt


def test1():
    line1 = Road(Point(0,0), Point(2,2))
    line2 = Road(Point(0,2), Point(2,0))
    cross = line_cross([line1.start, line1.end], [line2.start, line2.end])
    if cross != False:
        print(cross.x, cross.y)
    else:
        print('no cross')

def test2():
    line1 = Road(Point(0,1), Point(1,0))
    line2 = Road(Point(0,2), Point(2,0))
    cross = line_cross([line1.start, line1.end], [line2.start, line2.end])
    if cross != False:
        print(cross.x, cross.y)
    else:
        print('no cross')

def test3():
    line1 = Road(Point(0,1), Point(1,0))
    line2 = Road(Point(0,1), Point(2,0))
    cross = line_cross([line1.start, line1.end], [line2.start, line2.end])
    if cross != False:
        print(cross.x, cross.y)
    else:
        print('no cross')

def test4():
    line1 = Road(Point(0,0), Point(1,1))
    line2 = Road(Point(0,5), Point(5,0))
    cross = line_cross([line1.start, line1.end], [line2.start, line2.end])
    if cross != False:
        print(cross.x, cross.y)
    else:
        print('no cross')

test1()
test2()
test3()
test4()