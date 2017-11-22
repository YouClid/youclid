#!/usr/bin/python3

import argparse
import re
import json
import primitives
from pprint import pprint

polygons = {3: "Triangle",
            5: "Pentagon",
            6: "Hexagon",
            8: "Octagon"}


class CaseInsensitiveDictionary(dict):
    def __init__(self, d=None):
        self.d = {} if d is None else d

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
    pass


class _Clear():
    """This object will be returned from a call to the parse_clear function
    to represent that we need to clear the current step
    """
    pass


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
    # All of the objects created
    object_dict = {}

    # Regular expression to match any instance of our markup. The idea is as
    # follows: First use a negative look behind to make sure the bracket that
    # we're trying to match wasn't escaped, then match a bracket, then match
    # as many characters as possible until the next unescaped bracket.
    regex = r"(?<!\\)\[([\s\S]*?)(?<!\\)\]"

    # Iterate over all matches in the text
    for match in re.finditer(regex, text):
        # Get the dictionary of name and unnamed arguments
        args_dict, args_list = _parse_match(match)

        try:
            f = parsers[args_dict["type"]]
        except KeyError as e:
            # TODO Print a nice error message
            raise e
        # Call the appropriate parser function
        obj = f(args_dict, args_list, object_dict)

        # Now we need to handle the return value

        # If there is no return value, move on to the next call
        if obj is None:
            continue
        # If we just parsed a step and there are things that were added
        # TODO: Maybe we should add even if curr_step is empty?
        elif type(obj) == _Step:
            if len(curr_step > 0):
                # Add all unique objects we touched to the current animation
                animations.append([x for x in set(curr_step)])
        # Otherwise, if we parsed a clear, reset curr_step
        elif type(obj) == _Clear:
            curr_step = []
        # Otherwise, we created some object, so add them to the current step
        # for display purposes
        else:
            curr_step.extend(e.name for e in obj)

    # Ensure that we have something in the animations variable
    if(len(animations) == 0):
        animations.append(curr_step[:])

    # Create the output from the dictionary of objects
    return create_output(object_dict, text, animations)


def _parse_match(match):
    # Dictionary of named arguments
    args_dict = {}
    # List of non-named arguments (excluding the name)
    args_list = []

    # The entirety of the match
    whole_match = match[1]
    # Split the match up by spaces
    partials = whole_match.split()

    # The type will always be the first thing
    args_dict['type'] = partials[0]

    # Check to see if the second argument is a name
    if len(partials) > 1 and '=' not in partials[1]:
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
            args_list.append(keyword_arg)

    return args_dict, args_list


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
    for i in text:
        i = i.replace('[step]', '')
        i = i.replace('[definitions]', '')
        i = i.replace('[clear]', '')
        if not i.startswith('[loc'):
            newtext.append(i)
    newtext = newtext[:-1]
    text = newtext
    text = ''.join(text)

    pattern = r'(\[)([a-zA-Z]+) ([^\]]+)([\s\S]*?)\]'
    replaced = re.sub(pattern, get_text, text)

    return replaced

def get_text(match):
    match = match.group()
    match = match.replace("[", "").replace("]", "").split(" ")
    obj = object_dict.get(rotate_lex(match[1]))
    # This code is absolutely, and unequivocally, the dumbest thing. There
    # is absolutely no reason why we need to get doing disgusting things like
    # this, but, here we are writing anyways. This MUST get removed at some
    # point because there is a better way to do this.
    # Since sometimes we care about the ordering of the points, and sometimes
    # we don't, we might not get the object we want from doing a sort based
    # upon ordering, so sort it like a normal person would and check that.
    if obj is None:
        obj = object_dict.get(''.join(sorted(match[1])))
    if (match[0].lower() == "polygon"):
        obj_type = polygons.get(len(obj.points), "Polygon")
    else:
        obj_type = match[0]
    span_name = "text_%s_%s" % (type(obj).__name__.lower(), obj.name)
    return " <span name=%s style='background-color: #dddddd'>%s %s</span>" % (span_name, obj_type, match[1])


def parse_line(args, obj):
    name = rotate_lex(args[0])
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

    # Variables to hold the properties of a circle
    circle = None
    center = None
    radius = 0
    name = None

    # Objects that we have created in this parse function, for display purposes
    ret = []

    # For each argument
    for arg in args:
        # Split on space, get the type of the argument and the value, but
        # first make sure that we're parsing an argument with an equal sign,
        # ie: not just a circle with a name, or other keywords that we might
        # end up using
        if "=" not in arg:
            continue
        arg_type, arg_value = arg.split("=")
        # For each argument type that we support, parse it
        if arg_type == "center":
            # If the cetner object does not exist, make it
            if obj.get(arg_value) is None:
                center = primitives.Point(arg_value)
                obj[arg_value] = center
                ret.append(center)
            # Otherwise, get it
            else:
                center = obj[arg_value]
        elif arg_type == "radius":
            # Get the radius as a number
            radius = int(arg_value)
        elif arg_type == "name":
            name = arg_value
            # If the user is specifying a name, look to see if we have the
            # circle already, otherwise create a new one
            if obj.get(arg_value) is None:
                circle = primitives.Circle(arg_value)
                obj[arg_value] = circle
                ret.append(circle)
            else:
                circle = obj[arg_value]

    # If the user did not specify a name when creating the circle, since it's
    # defaulted to be None, this will be True
    if name is None:
        name = ''.join(sorted(args[0]))
        point_list = []

        # If there is not a circle with this name already
        if obj.get(name) is None:
            # Treat each letter as a point
            for p in name:
                # Create each point object if it does not exist
                if obj.get(p) is None:
                    point = primitives.Point(p)
                    obj[p] = point
                    point_list.append(point)
                else:
                    point_list.append(obj[p])
            # Create the circle and assign the points
            circle = primitives.Circle(name)
            circle.p1 = point_list[0]
            circle.p2 = point_list[1]
            circle.p3 = point_list[2]

            obj[name] = circle
        # Otherwise, just grab this circle
        else:
            circle = obj.get(name)

        # Add any points that we've created to our return list
        ret.extend(point_list)

    # Set the radius and the center
    circle.radius = radius
    circle.center = center

    # Add the circle we created to the return list
    ret.append(circle)

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


def parse_polygon(keyword_args, list_args, obj_dict):
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


def parse_location(keyword_args, list_args, obj_dict):
    """Parses the location for a particular point object"""
    name = keyword_args["name"]
    x = float(list_args[0])
    y = float(list_args[1])
    if obj_dict.get("name"):
        o = obj_dict[name]
    else:
        o = primitives.Point(keyword_args["name"])
        obj_dict[name] = o

    o.x = x
    o.y = y

    return None


def parse_step(keyword_args, list_args, obj_dict):
    return _Step()


def parse_clear(keyword_args, list_args, obj_dict):
    return _Clear()


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
    parser = argparse.ArgumentParser(description="Generate html from .yc files")
    parser.add_argument("path", type=str, help="Path to .yc file")
    parser.add_argument("-o", "--output",  type=str, help="Path to output html file")
    args = parser.parse_args()

    with open(args.path) as f:
        text = f.read()

    json_object = parse(text)

    if(args.output):
        with open(args.output, "w") as f:
            f.write(generate_html(json_object))
    else:
        print(json_object)
