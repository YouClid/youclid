#!/usr/bin/python3

import sys
import re
from . import primitives
import json
import random
import math


def parse_text(arg):
    with open(arg) as infile:
        text = infile.readlines()
    return text

def parse(text):

    parsers = {"line": parse_line,
               "circle": parse_circle,
               "point": parse_point,
               "center": parse_center,
               "triangle": parse_triangle}

    # Dictionary to hold all of the objects that we create.
    # The mapping is between names of the object and the object itself
    object_dict = {}

    pattern = '\\\.*?}'

    for f in text:
        match = re.findall(pattern, f)
        for i in match:
            func = re.findall('\\\.*?{', i)
            arg = re.findall('{.*?}', i)
            parsers[func[0].strip("\\").strip("{")](
                arg[0].strip("{").strip("}"), object_dict)

    # Function that actually mutates the objects in the dictionary to give them
    # coordinates
    plot_elements(object_dict)
    return create_output(object_dict, text)

    print(json.dumps(create_output(object_dict, text), indent=4))


def plot_elements(object_dict):
    """Gives the objects a location on the Cartesian plane"""

    # Iterate over each of the elements and place them somewhere on the
    # Cartesian plane
    for k, v in object_dict.items():
        # NOTE: This code will not work for everything! For now, I'm just
        # getting it to work for the first postulate, which primarily involves
        # circles. The biggest thing that we are about is having circles
        # that don't take up the entire screen
        if type(v) == primitives.Circle:
            # If there are no points defining this circle yet
            if ((v.center is None or v.center.x is None) and
                all([(v.p1 is None or v.p1.x is None),
                     (v.p2 is None or v.p2.x is None),
                     (v.p3 is None or v.p3.x is None)])):
                # Generate a center
                v.center = primitives.Point(name=v.name + "_center")
                v.center.x = random.uniform(-0.5, 0.5)
                v.center.y = random.uniform(-0.5, 0.5)

                radius = random.uniform(0, 0.25)

                theta = random.uniform(0, 2*math.pi)
                v.p1.x = v.center.x + radius * math.cos(theta)
                v.p1.y = v.center.y + radius * math.sin(theta)

                theta = random.uniform(0, 2*math.pi)
                v.p2.x = v.center.x + radius * math.cos(theta)
                v.p2.y = v.center.y + radius * math.sin(theta)

                theta = random.uniform(0, 2*math.pi)
                v.p3.x = v.center.x + radius * math.cos(theta)
                v.p3.y = v.center.y + radius * math.sin(theta)

            # Otherwise, the center is already defined and given a coordinate
            elif (v.center is not None and v.center.x is not None):
                radius = 0
                # If any of the points are given coordinates
                if v.p1 is not None and v.p1.x is not None:
                    radius = math.sqrt(math.pow(v.p1.x - v.center.x, 2) +
                                       math.pow(v.p1.y - v.center.y, 2))
                elif v.p2 is not None and v.p2.x is not None:
                    radius = math.sqrt(math.pow(v.p2.x - v.center.x, 2) +
                                       math.pow(v.p2.y - v.center.y, 2))
                elif v.p3 is not None and v.p3.x is not None:
                    radius = math.sqrt(math.pow(v.p3.x - v.center.x, 2) +
                                       math.pow(v.p3.y - v.center.y, 2))
                # If none of the points are given coordinates
                else:
                    radius = random.uniform(0, 0.25)

                # If p1 isn't given coordinates yet
                if v.p1.x is None:
                    theta = random.uniform(0, 2*math.pi)
                    v.p1.x = radius * math.cos(theta)
                    v.p1.y = radius * math.sin(theta)

                # If p2 isn't given coordinates yet
                if v.p2.x is None:
                    theta = random.uniform(0, 2*math.pi)
                    v.p2.x = radius * math.cos(theta)
                    v.p2.y = radius * math.sin(theta)

                # If p3 isn't given coordinates yet
                if v.p3.x is None:
                    theta = random.uniform(0, 2*math.pi)
                    v.p3.x = radius * math.cos(theta)
                    v.p3.y = radius * math.sin(theta)

            else:
                print("This case happened")
                sys.exit(1)

    # NOTE: This is awful code.
    # If there are any other points, just given them random coordaintes
    for k, v in object_dict.items():
        if type(v) == primitives.Point:
            if v.x is None:
                v.x = random.uniform(-0.5, 0.5)
                v.y = random.uniform(-0.5, 0.5)


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
    name = ''.join(sorted(n))
    point_list = []

    for p in name:
        if obj.get(p) is None:
            point = primitives.Point(p)
            obj[p] = point
            point_list.append(point)
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


def parse_triangle(args, obj):
    n = ''.join(args)
    name = ''.join(sorted(n))
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


def _rotate(l, n):
    return l[-n:] + l[:-n]


def _rotate_lex(l):
    ind = l.index(min(l))
    if(ind != 0):
        rot = len(l) - ind
        return _rotate(l, rot)
    else:
        return l


if __name__ == "__main__":
    t = parse_text(sys.argv[1])
    parse(sys.argv[1])
