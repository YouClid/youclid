from youclidbackend import colors
from youclidbackend.primitives import YouClidObject


class Circle(YouClidObject):
    """Represents a circle in 2D"""
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.center = None
        self.radius = None
        self.color = colors.PURPLE

    def __str__(self):
        return "Circle %s(%s, %s, %s)" % (str(self.name),
                                          str(self.p1),
                                          str(self.p2),
                                          str(self.p3))

    def __repr__(self):
        return "Circle %s(%s, %s, %s)" % (str(self.name),
                                          str(self.p1),
                                          str(self.p2),
                                          str(self.p3))

    def __eq__(self, other):
        if isinstance(other, Circle):
            mypoints = [self.p1, self.p2, self.p3]
            otherpoints = [other.p1, other.p2, other.p3]
            return (all([x in otherpoints for x in mypoints]) and
                    all([x in mypoints for x in otherpoints]))
        else:
            return False

    def __hash__(self):
        return hash(str(self))

    def __dict__(self):
        return {
                'p1': self.p1.name if self.p1 is not None else None,
                'p2': self.p2.name if self.p2 is not None else None,
                'p3': self.p3.name if self.p3 is not None else None,
                'radius': self.radius if self.radius is not None else None,
                'center': self.center.name if self.center is not None else None
               }
