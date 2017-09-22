#!/usr/bin/python3

import sys, re

def main(argv):

    parsers = {"line" : parse_line,
               "circle" : parse_circle,
               "point" : parse_point,
               "center" : parse_center,
               "triangle" : parse_triangle}

    with open(argv) as infile:
        text = infile.readlines()
    pattern = '\\\.*?}'
    for f in text:
        match = re.findall(pattern, f)
        for i in match:
            print(i)
            func = re.findall('\\\.*?{', i)
            arg = re.findall('{.*?}', i)
            parsers[func[0].strip("\\").strip("{")](arg[0].strip("{").strip("}"))

def parse_line(args):
    print("I'm the parse_line function")
    print(args)

def parse_circle(args):
    print("I'm the parse_circle function")
    print(args)

def parse_point(args):
    print("I'm the parse_point function")
    print(args)

def parse_center(args):
    print("I'm the parse_center function")
    print(args)

def parse_triangle(args):
    print("I'm the parse_triangle function")
    print(args)

#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    main(sys.argv[1])
