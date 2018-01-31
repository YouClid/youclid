#!/usr/bin/python3

import argparse
import re
import json
from youclidbackend import primitives
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
    curr_step = []

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

        # If there is no return value, move on to the next call
        if obj is None:
            continue
        # If we just parsed a step and there are things that were added
        # TODO: Maybe we should add even if curr_step is empty?
        elif type(obj[0]) == _Step:
            if len(curr_step) > 0:
                # Add all unique objects we touched to the current animation
                animations.append([x for x in set(curr_step)])
        # Otherwise, if we parsed a clear, reset curr_step
        elif type(obj[0]) == _Clear:
            curr_step = []
        # Otherwise, we created some object, so add them to the current step
        # for display purposes
        else:
            curr_step.extend(e.name for e in obj)

    # Ensure that we have something in the animations variable
    if(len(animations) == 0):
        animations.append(curr_step[:])

    # Create the output from the dictionary of objects
    return create_output(obj_dict, text, animations)


def _parse_match(whole_match):
    # Dictionary of named arguments
    args_dict = {}

    # Split the match up by spaces
    partials = whole_match.split()

    # The type will always be the first thing
    args_dict['type'] = partials[0].title()

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
                                      'data': v.__dict__()
                                     }

    return output


def format_text(text):
    newtext = []
    text = text.split('\n')
    for i in text:
        i = i.replace('[step]', '')
        i = i.replace('[definitions]', '')
        i = i.replace('[clear]', '')
        if not i.startswith('[loc'):
            newtext.append(i)
    newtext = newtext[:-1]
    text = newtext
    text = '\n'.join(text)

    regex = r"(?<!\\)\[([\s\S]*?)(?<!\\)\]"
    #pattern = r'(\[)([a-zA-Z]+) ([^\]]+)([\s\S]*?)\]'
    replaced = re.sub(regex, get_text, text)

    return replaced


def get_text(match):
    match = match[1]
    args_dict = _parse_match(match)
    span_name = "text_%s_%s" % (args_dict['type'].lower(), args_dict['name'])
    output = " <span name=%s style='background-color: #dddddd'>{text}</span>" % span_name
    if (args_dict.get('hidden', False)):
        return ""
    if(args_dict.get('text', False)):
        return output.format(text=args_dict['text'])
    if (args_dict['type'] == "polygon"):
        args_dict['type'] = polygons.get(len(args_dict["points"]), "Polygon")
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
            ret.append(p1)
            p2 = obj_dict.get(name[1])
            # TODO: Call parse point?
            if p2 is None:
                p2 = primitives.Point(name[1])
                obj_dict[name[1]] = p2
            ret.append(p2)
            p3 = obj_dict.get(name[2])
            # TODO: Call parse point?
            if p3 is None:
                p3 = primitives.Point(name[2])
                obj_dict[name[2]] = p3
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
        # TODO: Support a line as the radius, not just a value?
        circle.radius = float(radius)

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

    return ret


def parse_location(keyword_args):
    """Parses the location for a particular point object"""
    name = keyword_args["name"]
    x = float(keyword_args["x"])
    y = float(keyword_args["y"])
    if obj_dict.get("name"):
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


def generate_html(json_object):
    html = ""
    with open("../frontend/template.html", 'r') as f:
        html = f.read()

    html = html.replace("// insert json here", json.dumps(json_object,
                                                          indent=4))
    html = html.replace("<!-- Insert the text here -->",
                        json_object['text'].replace("\n", "<br>\n        "))

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
    args = parser.parse_args()

    with open(args.path) as f:
        text = f.read()

    json_object = parse(text)

    if(args.output):
        with open(args.output, "w") as f:
            f.write(generate_html(json_object))
    else:
        print(json_object)
