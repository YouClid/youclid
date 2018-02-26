#!/usr/bin/env python3.6
import sympy
import argparse
import json
import re
import shlex
import random
import math

import youclidbackend
from youclidbackend import primitives, colors
from pprint import pprint

polygons = {3: "Triangle",
            5: "Pentagon",
            6: "Hexagon",
            8: "Octagon"}

obj_dict = {}


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


def extract(text):
    # Regular expression to match any instance of our markup. The idea is as
    # follows: First use a negative look behind to make sure the bracket that
    # we're trying to match wasn't escaped, then match a bracket, then match
    # as many characters as possible until the next unescaped bracket.
    regex = r"(?<!\\)\[([\s\S]*?)(?<!\\)\]"
    return re.finditer(regex, text)


def parse(text):
    parsers = CaseInsensitiveDictionary({
                                         "line": parse_line,
                                         "circle": parse_circle,
                                         "point": parse_point,
                                         "center": parse_center,
                                         "polygon": parse_polygon,
                                         "loc": parse_location,
                                         "step": parse_step,
                                         "clear": parse_clear
                                        })

    # A list of the objects that need to be drawn at each step
    animations = []
    # Ojbects that we've added at this step
    curr_step = set()

    # Iterate over all matches in the text
    for match in extract(text):
        # Get the dictionary of name and unnamed arguments
        args_dict = _parse_match(match[1])

        try:
            f = parsers[args_dict["type"]]
        except KeyError as e:
            # TODO Print a nice error message
            raise e
        # Call the appropriate parser function
        obj = f(args_dict)
        # Now we need to handle the return value

        # Don't do anything special for locations
        if args_dict["type"] == "loc":
            continue
        # If there is no return value, move on to the next call
        # If we just parsed a step and there are things that were added
        # TODO: Maybe we should add even if curr_step is empty?
        if type(obj[0]) == _Step:
            # Add all unique objects we touched to the current animation
            animations.append([x for x in curr_step])
        # Otherwise, if we parsed a clear, reset curr_step
        elif type(obj[0]) == _Clear:
            curr_step = set()
        # Otherwise, we created some object, so add them to the current step
        # for display purposes
        else:
            if args_dict.get('color'):
                obj[0].color = colors.hex_to_rgba(args_dict['color'])
            for e in obj:
                curr_step.add(e.name)

    # Ensure that we have something in the animations variable
    animations.append([x for x in curr_step])

    constrain(obj_dict)

    # Create the output from the dictionary of objects
    return create_output(obj_dict, text, animations)


def constrain(obj_dict):
    """Takes in a object dictionary and modifies points, giving them
    coordinates"""

    points = set()
    for obj in obj_dict.values():
        if type(obj) == primitives.Point and (obj.x is obj.y is None):
            points.add(obj)

    while True:
        updated = False
        for p in points:
            try:
                symified_constraints = [x.symify() for x in p.constraints
                                        if x.symify() is not None]
                intersection = sympy.intersection(*symified_constraints)
                if intersection == []:
                    tmp = symified_constraints[0].arbitrary_point()
                    t = sympy.Symbol('t', real=True)
                    r = random.uniform(0, 2*math.pi)
                    intersection = [sympy.Point(tmp.x.subs(t, r), tmp.y.subs(t, r))]
                if p.x is not None:
                    continue
                p.x = intersection[0].x
                p.y = intersection[0].y
                updated = True
            except Exception as e:
                continue
        if not updated:
            break

    for p in points:
        p.x = float(p.x)
        p.y = float(p.y)


def _tokenize(match):
    return shlex.split(match)


def _parse_match(whole_match):
    # Dictionary of named arguments
    args_dict = {}

    # Split the match up by spaces
    partials = _tokenize(whole_match)
    # The type will always be the first thing
    args_dict['type'] = partials[0]

    # Check to see if the second argument is a name
    if len(partials) > 1 and '=' not in partials[1]:
        # TODO: Maybe the first argument isn't a name and they don't specify
        # the name as a keyword argument; ie, we need to default to something
        args_dict['name'] = partials[1]
        start_index = 2
    else:
        start_index = 1

    # start_index represents the index of the start of keyword arguments
    for keyword_arg in partials[start_index:]:
        # Get the key and the value and put them in the dictionary
        if '=' in keyword_arg:
            key, value = keyword_arg.split('=')
            args_dict[key] = value
        # Otherwise, it's a non-named argument so add it to the list
        else:
            # TODO: We need to do something about the loc keyword
            args_dict[keyword_arg] = True

    return args_dict


def create_output(d, text, animations):
    output = {}

    output['text'] = format_text(text)
    output['geometry'] = {}
    output['animations'] = animations

    for k, v in d.items():
        output['geometry'][v.name] = {
                                      'type': v.__class__.__name__,
                                      'id': v.name,
                                      'color': v.color,
                                      'data': v.__dict__(),
                                     }

    return output


def format_text(text):
    newtext = []
    text = text.split('\n')
    step =[0]
    for i in text:
        #i = i.replace('[step]', '')
        i = i.replace('[definitions]', '')
        i = i.replace('[clear]', '')
        if not i.startswith('[loc'):
            newtext.append(i)
    newtext = newtext[:-1]
    text = newtext
    text = '\n'.join(text)

    regex = r"(?<!\\)\[([\s\S]*?)(?<!\\)\]"
    # pattern = r'(\[)([a-zA-Z]+) ([^\]]+)([\s\S]*?)\]'
    replaced = re.sub(regex, lambda text: get_text(text, step), text)
    start = "<div id='step_0'>"
    end = "</div>"
    result = "%s %s %s" % (start, replaced, end)
    return result


def get_text(match, step):
    match = match[1]
    if(match == 'step'):
        step[0] += 1
        return "</div><div id='step_%d'>" % step[0]
    args_dict = _parse_match(match)
    # We need to replace "center" with "point" in order to get the correct
    # highlighting on the frontend
    t = args_dict['type'] if args_dict['type'] != 'center' else 'point'
    span_name = "text_%s_%s" % (t, args_dict['name'])
    output = " <span name=%s class='GeoElement'>{text}</span>" % span_name
    if (args_dict.get('hidden', False)):
        return ""
    if(args_dict.get('text', False)):
        return output.format(text=args_dict['text'])
    if (args_dict['type'] == "Polygon"):
        length = (len(args_dict['points']) if args_dict.get('points', False)
                  else len(args_dict['name']))
        args_dict['type'] = polygons.get(length, "Polygon")
    obj_text = "%s %s" % (args_dict['type'], args_dict['name'])
    return output.format(text=obj_text)


def parse_line(keyword_args):
    name = rotate_lex(keyword_args["name"])
    point_list = []
    ret = []

    for p in name:
        if obj_dict.get(p) is None:
            point = primitives.Point(p)
            point_list.append(point)
            obj_dict[p] = point
        else:
            point_list.append(obj_dict[p])

    if obj_dict.get(name) is None:
        line = primitives.Line(name)
        line.p1 = point_list[0]
        line.p2 = point_list[1]
        obj_dict[name] = line
    else:
        line = obj_dict.get(name)

    for p in point_list:
        p.constraints.add(line)

    ret.extend((line, line.p1, line.p2))

    return ret


def parse_circle(keyword_args):
    """Creates a circle object from the given parameters"""

    # Objects that we have created in this parse function, for display purposes
    ret = []
    name = keyword_args["name"]

    circle = obj_dict.get(name)

    if circle is not None:
        # TODO: We need to figure out what to do here. IE: do we just update
        # parameters? What if the update affects other objects? Do we not
        # update anything?
        return [circle, circle.p1, circle.p2, circle.p3]
    else:
        circle = primitives.Circle(name)
        obj_dict[name] = circle
        ret.append(circle)
        # TODO: JANKY WORKAROUND! MUST BE CHANGED
        if len(name) == 3:
            p1 = obj_dict.get(name[0])
            # TODO: Call parse point?
            if p1 is None:
                p1 = primitives.Point(name[0])
                obj_dict[name[0]] = p1
            p1.constraints.add(circle)
            ret.append(p1)
            p2 = obj_dict.get(name[1])
            # TODO: Call parse point?
            if p2 is None:
                p2 = primitives.Point(name[1])
                obj_dict[name[1]] = p2
            p2.constraints.add(circle)
            ret.append(p2)
            p3 = obj_dict.get(name[2])
            # TODO: Call parse point?
            if p3 is None:
                p3 = primitives.Point(name[2])
                obj_dict[name[2]] = p3
            p3.constraints.add(circle)
            ret.append(p3)

            circle.p1 = p1
            circle.p2 = p2
            circle.p3 = p3

    center = keyword_args.get("center")
    if center is not None:
        center = obj_dict.get("center")
        if center is None:
            center = primitives.Point(keyword_args.get("center"))
            obj_dict[keyword_args.get("center")] = center
            ret.append(center)
        circle.center = center

    radius = keyword_args.get("radius")
    if radius is not None:
        try:
            circle.radius = float(radius)
        except ValueError:
            circle.radius = (obj_dict.get(radius[0]), obj_dict.get(radius[1]))
    return ret


def parse_point(keyword_args):
    name = keyword_args["name"]
    ret = []
    if obj_dict.get(name) is None:
        point = primitives.Point(name)
        ret = [point]
        obj_dict[name] = point
    else:
        point = obj_dict.get(name)
        ret.append(point)
    return ret


def parse_center(keyword_args):
    # ASSUME CIRCLE ALREADY EXISTS
    name = keyword_args["name"]
    circle = keyword_args["circle"]
    ret = []

    if obj_dict.get(name):
        point = obj_dict.get(name)
    else:
        point = primitives.Point(name=name)
        obj_dict[name] = point

    circle = obj_dict[circle]
    circle.center = point
    ret.append(point)
    return ret


def parse_polygon(keyword_args):
    name = ''.join(rotate_lex(keyword_args['name']))
    point_list = []
    ret = []

    for p in name:
        if obj_dict.get(p) is None:
            point_list.append(primitives.Point(p))
        else:
            point_list.append(obj_dict[p])

    if obj_dict.get(name) is None:
        polygon = primitives.Polygon(name)
        polygon.points = point_list
        ret = [polygon] + point_list
        obj_dict[name] = polygon
    else:
        polygon = obj_dict.get(name)
        ret.append(polygon)
        ret.extend(point_list)

    for p in point_list:
        p.constraints.add(polygon)

    return ret


def parse_location(keyword_args):
    """Parses the location for a particular point object"""
    name = keyword_args["name"]
    x = float(keyword_args["x"])
    y = float(keyword_args["y"])
    if obj_dict.get(name):
        o = obj_dict[name]
    else:
        o = primitives.Point(keyword_args["name"])
        obj_dict[name] = o
    ret = o

    o.x = x
    o.y = y

    return [ret]


def parse_step(keyword_args):
    return [_Step()]


def parse_clear(keyword_args):
    return [_Clear()]


def generate_html(json_object, final):
    html = ""
    # I hope that this is the right way to do this? If not, someone tell me
    basepath = youclidbackend.__path__[0]
    with open(basepath + "/data/template.html", 'r') as f:
        html = f.read()

    html = html.replace("// insert json here", json.dumps(json_object,
                                                          indent=4))
    html = html.replace("<!-- Insert the text here -->",
                        json_object['text'].replace("\n", "<br>\n        "))

    if not final:
        html = html.replace("default.css",
                            youclidbackend.__path__[0] + "/data/default.css")
        html = html.replace("draw.js",
                            youclidbackend.__path__[0] + "/data/draw.js")
        html = html.replace("index.js",
                            youclidbackend.__path__[0] + "/data/index.js")
    else:
        with open(youclidbackend.__path__[0] + "/data/default.css") as f:
            data = f.read()
        html = html.replace('<link rel="stylesheet" href="default.css">',
                            '<style>' + data + '</style>')
        with open(youclidbackend.__path__[0] + "/data/draw.js") as f:
            data = f.read()
        html = html.replace('<script src="draw.js"></script>',
                            '<script>' + data + '</script>')
        with open(youclidbackend.__path__[0] + "/data/index.js") as f:
            data = f.read()
        html = html.replace('<script src="index.js"></script>',
                            '<script>' + data + '</script>')

    return html


def rotate(l, n):
    return l[-n:] + l[:-n]


def rotate_lex(l):
    ind = l.index(min(l))
    if(ind != 0):
        rot = len(l) - ind
        return rotate(l, rot)
    else:
        return l


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate html from .yc files")
    parser.add_argument("path", type=str, help="Path to .yc file")
    parser.add_argument("-o",
                        "--output",
                        type=str,
                        help="Path to output html file")
    parser.add_argument("-f",
                        "--final",
                        help="If present, output a copy of the HTML "
                             "for distrubition",
                        action='store_true')
    args = parser.parse_args()

    with open(args.path) as f:
        text = f.read()

    json_object = parse(text)

    if(args.output):
        with open(args.output, "w") as f:
            f.write(generate_html(json_object, args.final))
    else:
        print(json_object)
