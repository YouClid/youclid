class Line:
    """Represents a line in 2D"""
    def __init__(self, name):
        self.p1 = None
        self.p2 = None
        self.name = name

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
                'p1': self.p1.name if self.p1 is not None else None,
                'p2': self.p2.name if self.p2 is not None else None,
               }
