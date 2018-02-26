import sympy
import youclidbackend.colors
from youclidbackend.primitives import YouClidObject


class Polygon(YouClidObject):
    """Represents a triangle in 2D"""
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.points = None
        self.color = youclidbackend.colors.next_color()

    def __str__(self):
        ret = "Polygon %s(" % (str(self.name))
        for i in self.points:
            ret += str(i) + ", "
        ret = ret[:-3]
        ret += ")"
        return ret

    def __repr__(self):
        if self.points is None:
            return "Polygon %s(None)" % (str(self.name))
        p = ', '.join(str(x) for x in self.points)
        return "Polygon %s(%s)" % (str(self.name), p)

    def __eq__(self, other):
        if isinstance(other, Polygon):
            return self.points == other.points
        else:
            return False

    def __hash__(self):
        return hash(str(self))

    def __dict__(self):
        ret_dict = {}
        ret_dict["points"] = [x.name for x in self.points]
        return ret_dict

    def symify(self):
        return sympy.Polygon([x.symify() for x in self.points])
