class Point:
    """Represents a point object in 2D"""
    def __init__(self, name):
        self.x = None
        self.y = None
        self.name = name

    def __str__(self):
        return "Point(%s, %s)" % (str(self.x), str(self.y))

    def __repr__(self):
        return "Point(%s, %s)" % (str(self.x), str(self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
