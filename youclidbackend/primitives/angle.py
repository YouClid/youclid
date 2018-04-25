import youclidbackend.colors
from youclidbackend.primitives import YouClidObject

class Angle(YouClidObject):
    """Represents an Angle"""
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.big = False
        self.degree = None
        self.color = youclidbackend.colors.next_color()

    def __str__(self):
        return "Angle %s(%s, %s, %s)" % (str(self.name),
                                         str(self.p1),
                                         str(self.p2),
                                         str(self.p3))

    def __repr__(self):
        return "Angle %s(%s, %s, %s)" % (str(self.name),
                                         str(self.p1),
                                         str(self.p2),
                                         str(self.p3))

    def __eq__(self, other):
        if isinstance(other, Angle):
            return (self.p1 == other.p1 and self.p2 == other.p2 and
                    self.p3 == other.p3)
        else:
            return False

    def __hash__(self):
        return hash(str(self))

    def __dict__(self):
        return {
                'points': ["point_"+self.p1.name, "point_"+self.p2.name, "point_"+self.p3.name],
                'degree': self.degree
               }
