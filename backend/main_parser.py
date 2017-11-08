#!/usr/bin/python3

import argparse
import re
import json
import primitives
from pprint import pprint

object_dict = {}

polygons = {3: "Triangle",
            5: "Pentagon",
            6: "Hexagon",
            8: "Octagon"}

class CaseInsensitiveDictionary(dict):
    def __init__(self):
        self.d = {}

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


def parse_text(arg):
    with open(arg) as infile:
        text = infile.readlines()
    return text


def parse(text):
    parsers = CaseInsensitiveDictionary()
    parsers["line"] = parse_line
    parsers["circle"] = parse_circle
    parsers["point"] = parse_point
    parsers["center"] = parse_center
    parsers["polygon"] = parse_polygon
    parsers["loc"] = parse_location

    # Dictionary to hold all of the objects that we create.
    # The mapping is between names of the object and the object itself
    animations = []
    curr_step = []

    pattern = r'[^\\]?\[([\s\S]*?)\]'

    def_index = 0

    definitions_pattern = r'\[definitions\]'
    definitions_re = re.compile(definitions_pattern, re.IGNORECASE)

    for c, d in enumerate(text):
        if definitions_re.match(d):
            def_index = c
            break

    for e in text[def_index+1:]:
        match = re.findall(pattern, e)
        for i in match:
            data = i.split(' ')
            element_type = data[0]
            arguments = data[1:]
            obj = parsers[element_type](arguments, object_dict)

    for f in text[:def_index]:
        match = re.findall(pattern, f)
        for i in match:
            data = i.split(' ')
            element_type = data[0]
            arguments = data[1:]
            if element_type.lower() == 'step':
                if(len(curr_step) > 0):
                    animations.append(curr_step[:])
            elif element_type.lower() == 'clear':
                    curr_step = []
            else:
                obj = parsers[element_type](arguments, object_dict)
                if obj is not None:
                    for e in obj:
                        if(e.name not in curr_step):
                            curr_step.append(e.name)

    if(len(animations) == 0):
        animations.append(curr_step[:])

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
        i = i.replace('[step]', '')
        i = i.replace('[definitions]', '')
        i = i.replace('[clear]', '')
        if not i.startswith('[loc'):
            newtext.append(i)
    newtext = newtext[:-1]
    text = newtext
    text = ''.join(text)
    pattern = r'([^\\]?\[)([a-zA-Z]+) ([^\]]+)([\s\S]*?)\]'
    replaced = re.sub(pattern, get_text, text)

    # We need the name in the ID field to be sorted, so we need to replace all
    # of the unsorted versions with the sorted versions
    p = r"<span id=(.*?_.*?_.*?) "
    for m in re.findall(p, replaced):
        t = m.split("_")
        t[2] = ''.join(sorted(t[2]))
        t = '_'.join(t)
        replaced = re.sub(m, t, replaced)

    return replaced


def get_text(match):
    match = match.group()
    match = match.replace("[", "").replace("]", "").split(" ")
    del match[0]
    obj = object_dict.get(match[1])
    if (match[0].lower() == "polygon"):
        name = polygons.get(len(obj.points), "Polygon")
    else:
        name = match[0]
    span_id = "text_%s_%s" % (match[0].lower() if match[0].lower() != "center" else "point",
                              match[1])
    return " <span id=%s style='background-color: #dddddd'>%s %s</span>" % (span_id, name, match[1])


def parse_line(args, obj):
    name = ''.join(sorted([x for x in args[0]]))
    point_list = []
    ret = []

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
        line = obj.get(name)

    ret.extend((line, line.p1, line.p2))

    return ret


def parse_circle(args, obj):

    if len(args) > 1:
        center = ''
        radius = 0
        name = ''
        for i in args:
            for j, k in enumerate(i):
                if k == '=':
                    if i[:j] == "center":
                        center = i[j+1:]
                    elif i[:j] == "radius":
                        radius = int(i[j+1:])
                    elif i[:j] == "name":
                        name = i[j+1:]
                    break

        point_list = []
        ret = []

        if obj.get(center) is None:
            point = primitives.Point(center)
            obj[center] = point
            point_list.append(point)
        else:
            point_list.append(obj[center])

        if obj.get(name) is None:
            circle = primitives.Circle(name)
            circle.center = point_list[0]
            circle.radius = radius
            obj[name] = circle
        else:
            circle = obj.get(name)

    else:
        n = ''.join(args)
        name = ''.join(sorted(n))
        point_list = []
        ret = []

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
            circle = obj.get(name)

    ret.append(circle)
    ret.extend(point_list)

    return ret


def parse_point(args, obj):
    args = ''.join(args)
    name = args
    ret = []
    if obj.get(name) is None:
        point = primitives.Point(name)
        ret = [point]
        obj[name] = point
    else:
        point = obj.get(name)

    ret.append(point)
    return ret


def parse_center(args, obj):
    # ASSUME CIRCLE ALREADY EXISTS
    name = args[0]
    circle = args[1].split("=")[1]
    ret = []

    if obj.get(name):
        point = obj.get(name)
    else:
        point = primitives.Point(name=name)
        ret = [point]
        obj[name] = point

    circle = obj[circle]
    circle.center = point
    ret.append(point)
    return ret


def parse_polygon(args, obj):
    n = ''.join(args)
    name = ''.join(sorted(n))
    point_list = []
    ret = []

    for p in name:
        if obj.get(p) is None:
            point_list.append(primitives.Point(p))
        else:
            point_list.append(obj[p])

    if obj.get(name) is None:
        polygon = primitives.Polygon(name)
        polygon.points = point_list
        ret = [polygon] + point_list
        obj[name] = polygon
    else:
        polygon = obj.get(name)
        ret.append(polygon)
        ret.extend(point_list)

    return ret


def parse_location(args, obj):
    """Parses the location for a particular object"""
    name = args[0]
    x = float(args[1])
    y = float(args[2])
    parse_point(name, obj)
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
                        json_object['text'].replace("\n", "<br>\n        "))

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
