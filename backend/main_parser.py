#!/usr/bin/python3

import sys, re
import primitives
import pprint

def main(argv):

    parsers = {"line": parse_line,
               "circle": parse_circle,
               "point": parse_point,
               "center": parse_center,
               "triangle": parse_triangle}

    # List to hold all of the objects that we create
    object_dict = {}

    with open(argv) as infile:
        text = infile.readlines()
    pattern = '\\\.*?}'
    for f in text:
        match = re.findall(pattern, f)
        for i in match:
            func = re.findall('\\\.*?{', i)
            arg = re.findall('{.*?}', i)
            parsers[func[0].strip("\\").strip("{")](
                arg[0].strip("{").strip("}"), object_dict)

    pprint.pprint(object_dict)

def parse_line(args, obj):
    name = ''.join(sorted([x for x in args]))
    point_list = []

    for p in name:
        if obj.get(p) is None:
            point = primitives.Point(p)
            point_list.append(point)
        else:
            point_list.append(obj[p])

    if obj.get(name) is None:
        line = primitives.Line(name)
        line.p1 = point_list[0]
        line.p2 = point_list[1]
        obj[name] = line
    else:
        line = obj[name]

    return line

def parse_circle(args, obj):
    pass

def parse_point(args, obj):
    name = args
    if obj.get(name) is None:
        point = primitives.Point(name)
        obj[name] = point
    else:
        point = obj[name]

    return point

def parse_center(args, obj):
    pass

def parse_triangle(args, obj):
    pass

#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    main(sys.argv[1])
