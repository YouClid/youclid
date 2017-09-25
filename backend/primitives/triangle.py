class Triangle:
    """Represents a triangle in 2D"""
    def __init__(self, name):
        self.name = name
        self.p1 = None
        self.p2 = None
        self.p3 = None

    def __str__(self):
        return "Triangle %s(%s, %s, %s)" % (str(self.name),
                                     str(self.p1),
                                     str(self.p2),
                                     str(self.p3))

    def __repr__(self):
        return "Triangle %s(%s, %s, %s)" % (str(self.name),
                                     str(self.p1),
                                     str(self.p2),
                                     str(self.p3))

    def __eq__(self, other):
        if isinstance(other, Line):
            return ((self.p1 == other.p1 or self.p1 == other.p2 or self.p1 == other.p3) and
                    (self.p2 == other.p1 or self.p2 == other.p2 or self.p2 == other.p3) and
                    (self.p3 == other.p1 or self.p2 == other.p2 or self.p3 == other.p3))
        else:
            return False

    def __hash__(self):
        return hash(str(self))

    def __dict__(self):
        return {
                'p1': self.p1.name if self.p1 is not None else None,
                'p2': self.p2.name if self.p2 is not None else None,
                'p3': self.p3.name if self.p3 is not None else None,
               }
