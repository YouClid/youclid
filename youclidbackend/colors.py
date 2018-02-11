import youclidbackend.primitives

BLACK = [0.0, 0.0, 0.0, 1.0]
WHITE = [1.0, 1.0, 1.0, 1.0]
RED = [1.0, 0.0, 0.0, 1.0]
GREEN = [0.0, 1.0, 0.0, 1.0]
BLUE = [0.0, 0.0, 1.0, 1.0]
PURPLE = [1.0, 0.0, 1.0, 1.0]

ICE_BLUE = [0.7176470588235294, 0.8823529411764706, 0.9529411764705882, 1.0]
TEAL = [0.09411764705882353, 0.6039215686274509, 0.6588235294117647, 1.0]
LIGHT_GREEN = [0.666666666666666, 0.8274509803921568, 0.33725490196078434, 1.0]
YELLOW = [0.9764705882352941, 0.788235294117647, 0.03137254901960784, 1.0]
LIGHT_RED = [0.9529411764705882, 0.34509803921568627, 0.26666666666666666, 1.0]


class _object_color():
    def __init__(self):
        self._counter = 0
        self._colors = [LIGHT_RED, TEAL, LIGHT_GREEN, YELLOW, ICE_BLUE]

    def next_color(self):
        r = self._colors[self._counter]
        self._counter = (self._counter + 1) % len(self._colors)
        return r


point_colors = _object_color()
line_colors = _object_color()
circle_colors = _object_color()
polygon_colors = _object_color()


def set_color(obj):
    if type(obj) == youclidbackend.primitives.Point:
        obj.color = point_colors.next_color()
    if type(obj) == youclidbackend.primitives.Line:
        obj.color = line_colors.next_color()
    if type(obj) == youclidbackend.primitives.Circle:
        obj.color = circle_colors.next_color()
    if type(obj) == youclidbackend.primitives.Polygon:
        obj.color = polygon_colors.next_color()
