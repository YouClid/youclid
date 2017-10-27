#!/usr/bin/python3
import argparse
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
    animations = []
    curr_step = []

    pattern = r'[^\\]?`([\s\S]*?)`'

    for f in text:
        match = re.findall(pattern, f)
        for i in match:
            data = i.split(' ')
            element_type = data[0]
            arguments = data[1:]
            if element_type == 'step':
                if(len(curr_step) > 0):
                    animations.append(curr_step)
                    curr_step = []
            else:
                obj = parsers[element_type](arguments, object_dict)
                if obj is not None:
                    for e in obj:
                        curr_step.append(e.name)

    return create_output(object_dict, text, animations)


def create_output(dict, text, animations):
    output = {}

    output['text'] = format_text(text, dict)
    output['geometry'] = {}
    output['animations'] = animations

    for k, v in dict.items():
        output['geometry'][v.name] = {
                                   'type': v.__class__.__name__,
                                   'id': v.name,
                                   'data': v.__dict__()
                                  }

    return output

def format_text(text, dict):
    newtext = []
    for i in text:
        i = i.replace('`step`', '')
        if not i.startswith('`loc'):
            newtext.append(i)
    newtext = newtext[:-1]
    text = newtext
    text =  ''.join(text)
    pattern = r'([^\\]?`)([a-zA-Z]+) ([a-zA-Z]+)([\s\S]*?)`'
    return re.sub(pattern, r" <span id=text_\2_\3 style='background-color: #dddddd'>\2 \3</span>", text)

def get_text(match):
    match = match.group()
    match = match.replace("`", "").split(" ")
    return match[0] + " " + match[1]

def parse_line(args, obj):
    name = ''.join(sorted([x for x in args[0]]))
    point_list = []
    ret = None

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
        ret = [line] + point_list
        obj[name] = line
    else:
        line = None

    return ret


def parse_circle(args, obj):
    n = ''.join(args)
    name = ''.join(sorted(n))
    point_list = []
    ret = None

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
        ret = [circle] + point_list
        obj[name] = circle
    else:
        circle = None

    return ret


def parse_point(args, obj):
    args = ''.join(args)
    name = args
    ret = None
    if obj.get(name) is None:
        point = primitives.Point(name)
        ret = [point]
        obj[name] = point
    else:
        point = None

    return ret


def parse_center(args, obj):
    # ASSUME CIRCLE ALREADY EXISTS
    name = args[0]
    circle = args[1].split("=")[1]
    ret = None

    if obj.get(name):
        point = None
    else:
        point = primitives.Point(name=name)
        ret = [point]
        obj[name] = point

    circle = obj[circle]
    circle.center = point
    return ret


def parse_triangle(args, obj):
    n = ''.join(args)
    name = ''.join(sorted(n))
    point_list = []
    ret = None

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
        ret = [triangle] + point_list
        obj[name] = triangle
    else:
        triangle = None

    return ret


def parse_location(args, obj):
    """Parses the location for a particular object"""
    name = args[0]
    x = float(args[1])
    y = float(args[2])
    o = obj[name]

    o.x = x
    o.y = y

    return None


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
    parser = argparse.ArgumentParser(description="Generate html from .yc files")
    parser.add_argument("path", type=str, help="Path to .yc file")
    parser.add_argument("-o", "--output",  type=str, help="Path to output html file")
    args = parser.parse_args()
    t = parse_text(args.path)
    json_object = parse(t)
    if(args.output):
        with open(args.output, "w") as f:
            f.write(generate_html(json_object))

    else:
        print(json_object)
