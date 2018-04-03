import youclidbackend.colors
from youclidbackend.primitives import YouClidObject

class Angle(YouClidObject):
    """Represents an Angle"""
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.p1 = None
        self.l1 = None
        self.l2 = None
        self.color = youclidbackend.colors.next_color()

    def __str__(self):
        return "Angle %s(%s, %s, %s)" % (str(self.name),
                                         str(self.p1),
                                         str(self.l1),
                                         str(self.l2))

    def __repr__(self):
        return "Angle %s(%s, %s, %s)" % (str(self.name),
                                         str(self.p1),
                                         str(self.l1),
                                         str(self.l2))

    def __eq__(self, other):
        if isinstance(other, Angle):
            myattribs = [self.p1, self.l1, self.l2]
            otherattribs = [other.p1, other.l1, other.l2]
            return (all([x in otherattribs for x in myattribs]) and
                    all([x in myattribs for x in otherattribs]))
        else:
            return False

    def __hash__(self):
        return hash(str(self))

    def __dict__(self):
        return {
                'p1': self.p1.name if self.p1 is not None else None,
                'l1': self.l1.name if self.l1 is not None else None,
                'l2': self.l2.name if self.l2 is not None else None
               }
