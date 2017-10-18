#!/usr/bin/python3

import sys
import re
import json
import primitives
from pprint import pprint


def parse_text(arg):
    with open(arg) as infile:
        text = infile.readlines()
    return text


def parse(text):

    parsers = {"line": parse_line,
               "circle": parse_circle,
               "point": parse_point,
               "center": parse_center,
               "triangle": parse_triangle,
               "loc": parse_location}

    # Dictionary to hold all of the objects that we create.
    # The mapping is between names of the object and the object itself
    object_dict = {}

    pattern = r'[^\\]?`([\s\S]*?)`'

    for f in text:
        match = re.findall(pattern, f)
        for i in match:
            data = i.split(' ')
            element_type = data[0]
            arguments = data[1:]
            parsers[element_type](arguments, object_dict)

    return create_output(object_dict, text)


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
            obj[p] = point
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
    args = ''.join(args)
    name = args
    if obj.get(name) is None:
        point = primitives.Point(name)
        obj[name] = point
    else:
        point = obj[name]

    return point


def parse_center(args, obj):
    # ASSUME CIRCLE ALREADY EXISTS
    name = args[0]
    circle = args[1].split("=")[1]

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


def parse_location(args, obj):
    """Parses the location for a particular object"""
    name = args[0]
    x = float(args[1])
    y = float(args[2])
    o = obj[name]

    o.x = x
    o.y = y

    return o


def generate_html(json_object):
    html = ""
    with open("../frontend/template.html", 'r') as f:
        html = f.read()

    html = html.replace("// insert json here", json.dumps(json_object,
                                                          indent=4))
    html = html.replace("<!-- Insert the text here -->",
                        json_object['text'].replace("\n", "<br>"))

    return html


if __name__ == "__main__":
    t = parse_text(sys.argv[1])
    json_object = parse(t)
    print(generate_html(json_object))
