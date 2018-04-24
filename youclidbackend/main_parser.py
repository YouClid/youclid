#!/usr/bin/env python3.6
import sympy
import argparse
import math
import json
import re
import shlex
import random
import math
import sys

import youclidbackend
from youclidbackend import primitives, colors
from youclidbackend.utils import _Step, _Clear, CaseInsensitiveDictionary
from pprint import pprint
import os
import shutil

polygons = {3: "Triangle",
            5: "Pentagon",
            6: "Hexagon",
            8: "Octagon"}

obj_dict = {'polygon':{}, 'line':{}, 'point':{}, 'circle':{}, 'angle':{}}


def error(name=None, msg=None, lineno=None):
    """Wrapper function for error handling"""
    if name is not None:
        print("\033[31;1;4mError:\033[0m %s" % name, file=sys.stderr)
    if msg is not None:
        print(msg, file=sys.stderr)
    if lineno is not None:
        print("\033[32;1;4mLine Number:\033[0m %d" % int(lineno), file=sys.stderr)
    sys.exit(1)


def parse(text):
    tokens = tokenize(text)
    parsers = CaseInsensitiveDictionary({
                                         "line": parse_line,
                                         "circle": parse_circle,
                                         "point": parse_point,
                                         "center": parse_center,
                                         "polygon": parse_polygon,
                                         "loc": parse_location,
                                         "step": parse_step,
                                         "clear": parse_clear,
                                         "angle": parse_angle
                                        })

    # A list of the objects that need to be drawn at each step
    animations = []
    # Ojbects that we've added at this step
    curr_step = set()

    # Iterate over all matches in the text

    a = []
    for structure in tokens:
        match = structure['data']
        lineno = structure['lineno']
        # Get the dictionary of name and unnamed arguments
        args_dict = _parse_match(match)

        try:
            f = parsers[args_dict["type"]]
        except KeyError as e:
            error(name="Undefined object name",
                  msg="%s is not a valid object name" % args_dict["type"],
                  lineno=lineno)
        # Call the appropriate parser function
        if(args_dict['type'] == 'angle'):
            a.append(args_dict)
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
                n2 = obj[0].split("_")[1]
                obj_dict[args_dict['type']][n2].color = colors.hex_to_rgba(args_dict['color'])
            for e in obj:
                curr_step.add(e)

    # Ensure that we have something in the animations variable
    animations.append([x for x in curr_step])
    for angle in a:
        parse_angle(angle)

    constrain(obj_dict)
    # Create the output from the dictionary of objects
    return create_output(obj_dict, text, animations)


def tokenize(text):
    """Turn text into a list of dictionaries. Each dictionary has two keys:
   'lineno': The line number of the source code where this declaration started
   'data': The actual matched content
   """

    s = shlex.shlex(text, punctuation_chars=']')
    # The next line is needed to remove the fact that shlex treats the "#"
    # character as a comment, which messes everything up if you use that
    # character!
    s.commenters = ""

    # List of dictionaries to be returned
    tokens = []
    # For recursive purposes TODO: make this work
    inner_tokens = []
    # Ensure that there are always matching brackets
    depth = 0
    # All the starting line numbers for the syntax that we are currently
    # processing (we treat this as a stack). This is used so that we know
    # what line to tell the user if they have mismatching brackets
    linenumbers = []
    # The previous character (so that we can make sure that we don't parse
    # things that are escaped)
    previous = ''
    for x in s:
        # If we've found an unescaped starting bracket, it's the start
        # of our syntax
        if x == '[' and previous != '\\':
            # Increase our depth by one since we're parsing our syntax
            depth += 1
            # Push this line number on to the stack
            linenumbers.append(s.lineno)
            # Append a new dictionary
            inner_tokens.append({'lineno': s.lineno, 'data': []})
        # If we're parsing our syntax (ie if depth is > 0) and we've found
        # an unescaped closing bracket, it's the end of our syntax
        elif depth and x == ']' and previous != '\\':
            # Decrease our depth since we're no longer parsing this syntax,
            # but we may still be in a nested statement, so decrease depth
            # by 1
            depth -= 1
            # Add the last thing we processed (which will be completely parsed
            # since we're using a stack for storage) to our list of objects
            tokens.append(inner_tokens.pop())
            # We found the matching bracket, so remove the line number from
            # the stack
            linenumbers.pop()
        # If we're still parsing our syntax, add this token to the data of the
        # structure that we're currently working with
        elif depth:
            inner_tokens[-1]['data'].append(x)
        # Store the previous character
        previous = x

    # Raise error if we've reached the end of the file and there are still
    # closing brackets that we're expecting
    if depth > 0:
        error(name="Mismatching brackets",
              msg="Opening bracket with no closing bracket",
              lineno=linenumbers[-1])

    return tokens


def _parse_match(partials):
    # Dictionary of named arguments
    args_dict = {}

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


def parse_line(keyword_args):
    name = keyword_args["name"]
    point_list = []
    ret = []

    for p in name:
        if obj_dict['line'].get(p) is None:
            point = primitives.Point(p)
            point_list.append(point)
            obj_dict['point'][p] = point
        else:
            point_list.append(obj_dict['point'][p])

    if obj_dict['line'].get(name) is None:
        line = primitives.Line(name)
        line.p1 = point_list[0]
        line.p2 = point_list[1]
        obj_dict['line'][name] = line
    else:
        line = obj_dict['line'].get(name)

    for p in point_list:
        p.constraints.add(line)

    ret.extend(("line_"+line.name, "point_"+line.p1.name, "point_"+line.p2.name))

    return ret


def parse_circle(keyword_args):
    """Creates a circle object from the given parameters"""

    # Objects that we have created in this parse function, for display purposes
    ret = []
    name = keyword_args["name"]

    circle = obj_dict['circle'].get(name)

    if circle is not None:
        # TODO: We need to figure out what to do here. IE: do we just update
        # parameters? What if the update affects other objects? Do we not
        # update anything?
        return ["circle_"+circle.name, "point_"+circle.p1.name, "point_"+circle.p2.name, "point_"+circle.p3.name]
    else:
        circle = primitives.Circle(name)
        obj_dict['circle'][name] = circle
        ret.append("circle_"+circle.name)
        # TODO: JANKY WORKAROUND! MUST BE CHANGED
        if len(name) == 3:
            p1 = obj_dict['point'].get(name[0])
            # TODO: Call parse point?
            if p1 is None:
                p1 = primitives.Point(name[0])
                obj_dict['point'][name[0]] = p1
            p1.constraints.add(circle)
            ret.append("point_"+p1.name)
            p2 = obj_dict['point'].get(name[1])
            # TODO: Call parse point?
            if p2 is None:
                p2 = primitives.Point(name[1])
                obj_dict['point'][name[1]] = p2
            p2.constraints.add(circle)
            ret.append("point_"+p2.name)
            p3 = obj_dict['point'].get(name[2])
            # TODO: Call parse point?
            if p3 is None:
                p3 = primitives.Point(name[2])
                obj_dict['point'][name[2]] = p3
            p3.constraints.add(circle)
            ret.append("point_"+p3.name)

            circle.p1 = p1
            circle.p2 = p2
            circle.p3 = p3

    center = keyword_args.get("center")
    if center is not None:
        center = obj_dict['point'].get("center")

        if center is None:
            center = primitives.Point(keyword_args.get("center"))
            obj_dict['point'][keyword_args.get("center")] = center
            ret.append("point_"+center.name)
        circle.center = center

    radius = keyword_args.get("radius")
    if radius is not None:
        try:
            circle.radius = float(radius)
        except ValueError:
            circle.radius = (obj_dict['point'].get(radius[0]), obj_dict['point'].get(radius[1]))
    if center is not None and circle.center.x is not None and radius is None:
        point = None
        if circle.p1.x is not None:
            point = circle.p1
        elif circle.p2.x is not None:
            point = circle.p2
        elif circle.p3.x is not None:
            point = circle.p3
        if point is not None:
            circle.radius = math.sqrt((point.x - circle.center.x)**2 +
                                      (point.y - circle.center.y)**2)

    return ret


def parse_point(keyword_args):
    name = keyword_args["name"]
    ret = []
    if obj_dict['point'].get(name) is None:
        point = primitives.Point(name)
        ret = ["point_"+point.name]
        obj_dict['point'][name] = point
    else:
        point = obj_dict['point'].get(name)
        ret.append("point_"+point.name)
    return ret



def parse_center(keyword_args):
    # ASSUME CIRCLE ALREADY EXISTS
    name = keyword_args["name"]
    circle = keyword_args["circle"]
    ret = []

    if obj_dict['point'].get(name):
        point = obj_dict['point'].get(name)
    else:
        point = primitives.Point(name=name)
        obj_dict['point'][name] = point
    circle = obj_dict['circle'][circle]
    circle.center = point
    ret.append("point_"+point.name)
    return ret


def parse_polygon(keyword_args):
    name = keyword_args['name']
    point_list = []
    ret = []

    for p in name:
        if obj_dict['point'].get(p) is None:
            point_list.append(primitives.Point(p))
        else:
            point_list.append(obj_dict['point'][p])

    if obj_dict['polygon'].get(name) is None:
        polygon = primitives.Polygon(name)
        polygon.points = point_list
        ret = ["polygon_"+polygon.name] + ["point_"+i.name for i in point_list]
        obj_dict['polygon'][name] = polygon
    else:
        polygon = obj_dict['polygon'].get(name)
        ret.append("polygon_"+polygon.name)
        ret.extend(["point_"+i.name for i in point_list])

    for p in point_list:
        p.constraints.add(polygon)

    return ret


def parse_angle(keyword_args):
    """Creates an angle object from the given parameters"""

    ret = []
    name = keyword_args['name']
    angle = obj_dict['angle'].get(name)

    #if angle is not None:
    #    return [angle, angle.p1, angle.p2, angle.p3]
    if angle is None:
        angle = primitives.Angle(name)
        obj_dict['angle'][name] = angle
    if name and not (keyword_args.get("p1") or keyword_args.get("p2") or keyword_args.get("p3")):
        p1 = obj_dict['point'].get(name[0])
        if p1 is None:
            p1 = primitives.Point(name[0])
            obj_dict['point'][name[0]] = p1
        p2 = obj_dict['point'].get(name[1])
        if p2 is None:
            p2 = primitives.Point(name[1])
            obj_dict['point'][name[1]] = p2
        p3 = obj_dict['point'].get(name[2])
        if p3 is None:
            p3 = primitives.Point(name[2])
            obj_dict['point'][name[2]] = p3

    else:
        p1 = keyword_args.get("p1")
        if p1 is not None:
            p1 = obj_dict['point'].get(p1)
            if p1 is None:
                p1 = primitives.Point(keyword_args.get("p1"))
                obj_dict['point'][keyword_args.get("p1")] = p1
        p2 = keyword_args.get("p2")
        if p2 is not None:
            p2 = obj_dict['point'].get(p2)
            if p2 is None:
                p2 = primitives.Point(keyword_args.get("p2"))
                obj_dict['point'][keyword_args.get("p2")] = p2
        p3 = keyword_args.get("p3")
        if p3 is not None:
            p3 = obj_dict['point'].get(p3)
            if p3 is None:
                p3 = primitives.Point(keyword_args.get("p3"))
                obj_dict['point'][keyword_args.get("p3")] = p3

    big = keyword_args.get("big")
    if big is not None:
        angle.big = big

    if (p1.x is not None and p2.x is not None and p3.x is not None):

        degree = get_degree(p1, p2, p3)

        if angle.big:
            if degree < 0:
                p4 = p1
                p1 = p3
                p3 = p4
                degree = 360 + degree
            else:
                degree = 360 - degree
        else:
            if degree > 0:
                p4 = p1
                p1 = p3
                p3 = p4
            else:
                degree = -1 * degree

        angle.degree = degree

    angle.p1 = p1
    angle.p2 = p2
    angle.p3 = p3
    ret.append("angle_"+angle.name)
    ret.append("point_"+p1.name)
    ret.append("point_"+p2.name)
    ret.append("point_"+p3.name)

    return ret


def get_degree(p1, p2, p3):
    """Returns degree of the angle defined by three points"""
    in_radians = math.atan2(p3.y - p2.y, p3.x - p2.x) - \
                 math.atan2(p1.y - p2.y, p1.x - p2.x)
    in_degrees = math.degrees(in_radians)
    return in_degrees

def parse_location(keyword_args):
    """Parses the location for a particular point object"""
    name = keyword_args["name"]
    x = float(keyword_args["x"])
    y = float(keyword_args["y"])
    if obj_dict['point'].get(name):
        o = obj_dict['point'][name]
    else:
        o = primitives.Point(keyword_args["name"])
        obj_dict['point'][name] = o
    ret = o

    o.x = x
    o.y = y

    return ["point_"+ret.name]


def parse_step(keyword_args):
    return [_Step()]


def parse_clear(keyword_args):
    return [_Clear()]

def constrain(obj_dict):
    """Takes in a object dictionary and modifies points, giving them
    coordinates"""

    points = set()
    for val in obj_dict.values():
        for obj in val.values():
            if type(obj) == primitives.Point and (obj.x is obj.y is None):
                points.add(obj)


    #for obj in obj_dict.values():
    #    if type(obj) == primitives.Point and (obj.x is obj.y is None):
    #        points.add(obj)

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
                    intersection = [sympy.Point(tmp.x.subs(t, r),
                                                tmp.y.subs(t, r))]
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
        try:
            p.x = float(p.x)
            p.y = float(p.y)
        except TypeError:
            error(name="Underconstrained System",
                  msg="The following object is underconstrained: %s" % p.name)


def format_text(text):
    newtext = []
    text = text.split('\n')
    step = [0]
    for i in text:
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
    args_dict = _parse_match(shlex.split(match))
    # We need to replace "center" with "point" in order to get the correct
    # highlighting on the frontend
    t = args_dict['type'] if args_dict['type'] != 'center' else 'point'
    span_name = "text_%s_%s_%s" % (t, t, args_dict['name'])
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


def create_output(d, text, animations):
    output = {}

    output['text'] = format_text(text)
    output['geometry'] = {}
    output['animations'] = animations

    for k, val in d.items():
        for key, v in val.items():
            output['geometry'][k + "_" + v.name] = {
                                          'type': v.__class__.__name__,
                                          'id': k + "_" + v.name,
                                          'color': v.color,
                                          'data': v.__dict__(),
                                          'label': v.name
                                         }

    return output


def generate_html(json_object, final, path=None):
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
        html = html.replace("styles/default.css",
                            youclidbackend.__path__[0] + "/data/styles/default.css")
        html = html.replace("draw.js",
                            youclidbackend.__path__[0] + "/data/draw.js")
        html = html.replace("index.js",
                            youclidbackend.__path__[0] + "/data/index.js")
    else:
        with open(path + "/index.html", 'w') as f:
            f.write(html)
        to_copy = [
            "/styles/default.css",
            "/styles/light.css",
            "/draw.js",
            "/index.js"
        ]
        for fname in to_copy:
            shutil.copyfile(youclidbackend.__path__[0] + "/data" + fname, path+fname)

    return html


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

    if(args.output and not args.final):
        with open(args.output, "w") as f:
            f.write(generate_html(json_object, args.final))
    elif(args.output and args.final):
        os.makedirs(args.output + "/styles", exist_ok=True)
        generate_html(json_object, args.final, path=args.output)
    else:
        print(json_object)
