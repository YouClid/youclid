#!/usr/bin/python3

import sys, re
import primitives

def main(argv):

    parsers = {"line" : parse_line,
               "circle" : parse_circle,
               "point" : parse_point,
               "center" : parse_center,
               "triangle" : parse_triangle}

    # List to hold all of the objects that we create
    # TODO: We probably want to make this a dictionary, however, that means
    # we need a way of showing that something like line AB is the same as
    # line BA, and that if a circle has 5 points that are defining it, any
    # combination of the 3 of the 5 are defining the same thing... sounds
    # like a problem for the future
    object_list = []

    with open(argv) as infile:
        text = infile.readlines()
    pattern = '\\\.*?}'
    for f in text:
        match = re.findall(pattern, f)
        for i in match:
            func = re.findall('\\\.*?{', i)
            arg = re.findall('{.*?}', i)
            parsers[func[0].strip("\\").strip("{")](
                arg[0].strip("{").strip("}"), object_list)

    print(object_list)

def parse_line(args, obj):
    name = args
    point_list = []

    for p in name:
        point = primitives.Point(p)
        if point not in obj:
            obj.append(point)
        point_list.append(point)

    line = primitives.Line(name)
    line.p1 = point_list[0]
    line.p2 = point_list[1]

    if line not in obj:
        obj.append(line)

    return line

def parse_circle(args, obj):
    pass

def parse_point(args, obj):
    name = args
    point = primitives.Point(name)

    if point not in obj:
        obj.append(point)

    return point

def parse_center(args, obj):
    pass

def parse_triangle(args, obj):
    pass

#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    main(sys.argv[1])
