#!/usr/bin/python3

import sys, re
import primitives
import pprint
import json

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
    print(json.dumps(create_output(object_dict, text)))

def create_output(dict, text):
    output = {}

    output['text'] = ''.join(text)
    output['geometry'] = []
    for k, v in dict.items():
        output['geometry'].append({
                                   'type': v.__class__.__name__,
                                   'id': v.name,
                                   'data': v.__dict__()
                                  })

    return output

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
    n = ''.join(args)
    name = rotate_lex(n)
    point_list = []

    for p in name:
        if obj.get(p) is None:
            point_list.append(primitives.Point(p))
        else:
            point_list.append(obj[p])

    if obj.get(name) is None:
        circle = primitives.Circle(name)
        circle.p1 = point_list[0]
        circle.p2 = point_list[1]
        circle.p3 = point_list[2]
        obj[name] = circle
    else:
        circle = obj[name]

    return circle

def parse_point(args, obj):
    name = args
    if obj.get(name) is None:
        point = primitives.Point(name)
        obj[name] = point
    else:
        point = obj[name]

    return point

def parse_center(args, obj):
    # ASSUME CIRCLE ALREADY EXISTS
    split = args.split(", ")
    name = split[0]
    circle = split[1].split("=")[1]

    if obj.get(name):
        point = obj[name]
    else:
        point = primitives.Point(name=name)

    obj[name] = point

    circle = obj[circle]
    circle.center = point
    return point


    pass

def parse_triangle(args, obj):
    n = ''.join(args)
    name = rotate_lex(n)
    point_list = []

    for p in name:
        if obj.get(p) is None:
            point_list.append(primitives.Point(p))
        else:
            point_list.append(obj[p])

    if obj.get(name) is None:
        triangle = primitives.Triangle(name)
        triangle.p1 = point_list[0]
        triangle.p2 = point_list[1]
        triangle.p3 = point_list[2]
        obj[name] = triangle
    else:
        triangle = obj[name]

    return triangle

def rotate(l, n):
    return l[-n:] + l[:-n]

def rotate_lex(l):
    ind = l.index(min(l))
    if(ind != 0):
        rot = len(l) - ind
        return rotate(l, rot)
    else:
        return l
#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    main(sys.argv[1])
