import sympy
import math
import random
import youclidbackend.colors
from youclidbackend.primitives import YouClidObject
from youclidbackend.utils import lerp


class Line(YouClidObject):
    """Represents a line in 2D"""
    def __init__(self, name):
        super().__init__()
        self.p1 = None
        self.p2 = None
        self.name = name
        self.color = youclidbackend.colors.next_color()
        self.constraints = set()

    def __str__(self):
        return "Line %s(%s, %s)" % (str(self.name),
                                    str(self.p1),
                                    str(self.p2))

    def __repr__(self):
        return "Line %s(%s, %s)" % (str(self.name),
                                    str(self.p1),
                                    str(self.p2))

    def __eq__(self, other):
        if isinstance(other, Line):
            return ((self.p1 == other.p1 or self.p1 == other.p2) and
                    (self.p2 == other.p2 or self.p2 == other.p1))
        else:
            return False

    def __hash__(self):
        return hash(str(self))

    def __dict__(self):
        return {
                'p1': "point_"+self.p1.name if self.p1 is not None else None,
                'p2': "point_"+self.p2.name if self.p2 is not None else None,
               }

    def length(self):
        if (self.p1 is None or self.p2 is None or
                self.p1.x is None or self.p2.x is None):
            return None
        else:
            return math.sqrt((self.p2.x - self.p1.x)**2 +
                             (self.p2.y - self.p1.y)**2)

    def arbitrary_point(self):
        t = random.uniform(0.2, 0.8)  # Add a pad so its not too close to endpoints
        nx = lerp(self.p1.x, self.p2.x, t)
        ny = lerp(self.p1.y, self.p2.y, t)

        return (nx, ny)

    def symify(self):
        if self.p1.x is None or self.p2.x is None:
            return None
        sym_p1 = self.p1.symify()
        sym_p2 = self.p2.symify()
        if sym_p1 is None or sym_p2 is None:
            return None
        return sympy.Segment(sym_p1, sym_p2)
