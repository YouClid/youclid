import random

BLACK = [0.0, 0.0, 0.0, 1.0]
WHITE = [1.0, 1.0, 1.0, 1.0]
NAVY = [0.0, 0.12156862745098039, 0.24705882352941178, 1.0]
BLUE = [0.0, 0.4549019607843137, 0.8509803921568627, 1.0]
AQUA = [0.4980392156862745, 0.8588235294117647, 1.0, 1.0]
TEAL = [0.2235294117647059, 0.8, 0.8, 1.0]
OLIVE = [0.23921568627450981, 0.6, 0.4392156862745098, 1.0]
GREEN = [0.1803921568627451, 0.8, 0.25098039215686274, 1.0]
LIME = [0.00392156862745098, 1.0, 0.4392156862745098, 1.0]
YELLOW = [1.0, 0.8627450980392157, 0.0, 1.0]
ORANGE = [1.0, 0.5215686274509804, 0.10588235294117647, 1.0]
RED = [1.0, 0.2549019607843137, 0.21176470588235294, 1.0]
MAROON = [0.5215686274509804, 0.0784313725490196, 0.29411764705882354, 1.0]
FUCHSIA = [0.9411764705882353, 0.07058823529411765, 0.7450980392156863, 1.0]
PURPLE = [0.6941176470588235, 0.050980392156862744, 0.788235294117647, 1.0]
GRAY = [0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 1.0]
SILVER = [0.8666666666666667, 0.8666666666666667, 0.8666666666666667, 1.0]


class _object_color():
    def __init__(self):
        self._counter = 0
        self._colors = [BLUE, AQUA, TEAL, OLIVE, GREEN, LIME, ORANGE, RED,
                        MAROON, FUCHSIA, PURPLE, GRAY]
        random.shuffle(self._colors)

    def next_color(self):
        r = self._colors[self._counter]
        self._counter = (self._counter + 1) % len(self._colors)
        return r


_o = _object_color()


def next_color():
    return _o.next_color()
