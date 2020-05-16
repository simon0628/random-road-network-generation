from src.external.Utils import *
from src.external.BaseTypes import *
import unittest


class TestStringMethods(unittest.TestCase):
    def test1(self):
        line1 = Line(Point(0,0), Point(2,2))
        line2 = Line(Point(0,2), Point(2,0))
        cross = line_cross([line1.start, line1.end], [line2.start, line2.end])
        self.assertTrue(cross.equal(Point(1, 1)))

    def test2(self):
        line1 = Line(Point(0,1), Point(1,0))
        line2 = Line(Point(0,2), Point(2,0))
        cross = line_cross([line1.start, line1.end], [line2.start, line2.end])
        self.assertEqual(cross, False)

    def test3(self):
        line1 = Line(Point(0,1), Point(1,0))
        line2 = Line(Point(0,1), Point(2,0))
        cross = line_cross([line1.start, line1.end], [line2.start, line2.end])
        self.assertTrue(cross.equal(Point(0, 1)))

    def test4(self):
        line1 = Line(Point(0,0), Point(1,1))
        line2 = Line(Point(0,5), Point(5,0))
        cross = line_cross([line1.start, line1.end], [line2.start, line2.end])
        self.assertEqual(cross, False)


if __name__ == '__main__':
    unittest.main()