import math
import sympy
import youclidbackend.colors
from youclidbackend.primitives import YouClidObject


class Point(YouClidObject):
    """Represents a point object in 2D"""
    def __init__(self, name):
        super().__init__()
        self.x = None
        self.y = None
        self.name = name
        self.color = youclidbackend.colors.next_color()
        self.constraints = set()

    def __str__(self):
        return "Point %s(%s, %s)" % (str(self.name),
                                     str(self.x),
                                     str(self.y))

    def __repr__(self):
        return "Point %s(%s, %s)" % (str(self.name),
                                     str(self.x),
                                     str(self.y))

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        else:
            return False

    def __hash__(self):
        return hash(str(self))

    def __dict__(self):
        return {
                'x': self.x,
                'y': self.y
               }

    def dist(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def symify(self):
        if self.x is None:
            return None
        return sympy.Point(self.x, self.y)
