class CaseInsensitiveDictionary(dict):
    def __init__(self, d=None):
        self.d = {}
        if d is not None:
            self.d = {key.lower() if type(key) is str else key: d[key]
                      for key in d}

    def __getitem__(self, key):
        if type(key) == str:
            return self.d.__getitem__(key.lower())
        else:
            return self.d.__getitem__(key)

    def __setitem__(self, key, value):
        if type(key) == str:
            return self.d.__setitem__(key.lower(), value)
        else:
            return self.d.__setitem__(key, value)

    def __repr__(self):
        return self.d.__repr__()

    def __str__(self):
        return self.d.__str__()


class _Step():
    """This object will be returned from a call to the parse_step function
    to represent that we are done parsing the current step
    """
    def __eq__(self, other):
        return type(other) == _Step


class _Clear():
    """This object will be returned from a call to the parse_clear function
    to represent that we need to clear the current step
    """
    def __eq__(self, other):
        return type(other) == _Clear


def lerp(a, b, t):
    return (b * t) + ((1 - t) * a)
