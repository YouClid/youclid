class Polygon:
    """Represents a triangle in 2D"""
    def __init__(self, name):
        self.name = name
        self.points = None

    def __str__(self):
        ret =  "Polygon %s(" % (str(self.name))
        for i in self.points:
            ret += i + ", "
        ret = ret[:-3]
        ret += ")"
        return ret

    def __repr__(self):
        ret =  "Polygon %s(" % (str(self.name))
        for i in self.points:
            ret += i + ", "
        ret = ret[:-3]
        ret += ")"
        return ret

    def __eq__(self, other):
        if isinstance(other, Polygon):
            return self.points == other.points
        else:
            return False

    def __hash__(self):
        return hash(str(self))

    def __dict__(self):
        ret_dict = {}
        for i in range(len(self.points)):
            ret_dict["p"+str(i+1)] = self.points[i].name
        return ret_dict
