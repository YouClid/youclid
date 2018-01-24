import unittest
import youclidbackend


class TestParser(unittest.TestCase):

    def subtest_extract(self, text, parse_list):
        with self.subTest(text=text, parse_list=parse_list):
            extracted = [x.group(0) for x in
                         list(youclidbackend.main_parser.extract(text))]
            self.assertEqual(extracted, parse_list)

    def test_extract(self):
        """Ensure that the parser extracts just our markup"""

        # Test basic extraction
        text = "[point A]"
        parse_list = ['[point A]']
        self.subtest_extract(text, parse_list)

        # Test multiple elements on the same line
        text = "[point A][circle ABC]"
        parse_list = ["[point A]", "[circle ABC]"]
        self.subtest_extract(text, parse_list)

        # Test text interspersed with markup
        text = "[point A]"\
               "[circle ABC]"\
               "This is some text with a reference to [point A]."\
               "This is some text with a reference to [circle name=ABC]."\
               "[step]"
        parse_list = ["[point A]",
                      "[circle ABC]",
                      "[point A]",
                      "[circle name=ABC]",
                      "[step]"]
        self.subtest_extract(text, parse_list)

        # Test what should be none of our markup
        text = "\[This should just be some text\]"
        parse_list = []
        self.subtest_extract(text, parse_list)

        # Test everything that we support
        text = "\[This should just be some text\]"\
               "[circle ABC] [center D circle=ABC]"\
               "[line AB]"\
               "[point D]"\
               "[polygon ABCD]"\
               "[loc A x=0 y=0]"\
               "[step]"\
               "[clear]"
        parse_list = ["[circle ABC]",
                      "[center D circle=ABC]",
                      "[line AB]",
                      "[point D]",
                      "[polygon ABCD]",
                      "[loc A x=0 y=0]",
                      "[step]",
                      "[clear]"]
        self.subtest_extract(text, parse_list)

        # Test using a ] in an element name
        text = "[circle name=myname\]]"
        parse_list = ["[circle name=myname\]]"]
        self.subtest_extract(text, parse_list)

    def subtest_parse_match(self, text, kwargs):
        with self.subTest(text=text, kwargs=kwargs):
            parsed = youclidbackend.main_parser._parse_match(text)
            self.assertEqual(parsed, kwargs)

    def test_parse_match(self):
        """Test that we extract attributes of vaious elements correctly"""

        # Test basic single letter name
        text = "point A"
        kwargs = {
                  'name': 'A',
                  'type': 'point'
                 }
        self.subtest_parse_match(text, kwargs)

        text = "point B"
        kwargs = {
                  'name': 'B',
                  'type': 'point'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test multiple character name
        text = "point hello"
        kwargs = {
                  'name': 'hello',
                  'type': 'point'
                 }
        self.subtest_parse_match(text, kwargs)

        # Keyword argument tests

        # Test keyword argument for name with single letter
        text = "point name=A"
        kwargs = {
                  'name': 'A',
                  'type': 'point'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test keyword argument for name with multiple letters
        text = "point name=mypoint"
        kwargs = {
                  'name': 'mypoint',
                  'type': 'point'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test keyword argument for name with an escaped bracket
        # TODO: How do we handle this; does the name have the backslash in it?
        text = "point name=mypoint\]"
        kwargs = {
                  'name': 'mypoint]',
                  'type': 'point'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test keyword argument for name with multiple letters
        text = "point name=\"mypoint with spaces\""
        kwargs = {
                  'name': 'mypoint with spaces',
                  'type': 'point'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test non-keyword arguments
        text = "point A hidden somethingelse"
        kwargs = {
                  'name': 'A',
                  'type': 'point',
                  'hidden': True,
                  'somethingelse': True
                 }
        self.subtest_parse_match(text, kwargs)

        # Test the line extraction
        text = "line AB"
        kwargs = {
                  'name': 'AB',
                  'type': 'line'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test line extraction with a name
        text = "line AB name=test"
        kwargs = {
                  'name': 'test',
                  'type': 'line'
                 }
        self.subtest_parse_match(text, kwargs)

        text = "line name=test"
        kwargs = {
                  'name': 'test',
                  'type': 'line'
                 }
        self.subtest_parse_match(text, kwargs)

        # TODO: I'm not sure if this is how we will do this; it may change
        text = "line name=test p1=A p2=B"
        kwargs = {
                  'name': 'test',
                  'type': 'line',
                  'p1': 'A',
                  'p2': 'B'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test non-keyword arguments
        text = "line AB hidden"
        kwargs = {
                  'name': 'AB',
                  'type': 'line',
                  'hidden': True
                 }
        self.subtest_parse_match(text, kwargs)

        # Test circle extraction
        text = "circle ABC"
        kwargs = {
                  'name': 'ABC',
                  'type': 'circle'
                 }
        self.subtest_parse_match(text, kwargs)

        text = "circle name=ABC"
        kwargs = {
                  'name': 'ABC',
                  'type': 'circle'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test circle extraction with center
        text = "circle ABC center=D"
        kwargs = {
                  'name': 'ABC',
                  'type': 'circle',
                  'center': 'D'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test circle extraction with center and radius
        text = "circle ABC center=E radius=10"
        kwargs = {
                  'name': 'ABC',
                  'type': 'circle',
                  'center': 'E',
                  'radius': '10'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test circle extraction with center and radius and named keyword
        text = "circle name=XYZ center=L radius=1"
        kwargs = {
                  'name': 'XYZ',
                  'type': 'circle',
                  'center': 'L',
                  'radius': '1'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test circle extraction spaces in name
        text = "circle name=\"My circle\" center=\"My point\" radius=1"
        kwargs = {
                  'name': 'My circle',
                  'type': 'circle',
                  'center': 'My point',
                  'radius': '1'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test circle extraction with center and radius and named keyword
        text = "circle name=XYZ hidden"
        kwargs = {
                  'name': 'XYZ',
                  'type': 'circle',
                  'hidden': True
                 }
        self.subtest_parse_match(text, kwargs)

        # Test circle extraction with center and radius and named keyword, with
        # the order of hidden and name switched
        # TODO: This unittest breaks, presumably because it thinks that the
        # name is "hidden"; do we do anything about this?
        text = "circle hidden name=XYZ"
        kwargs = {
                  'name': 'XYZ',
                  'type': 'circle',
                  'hidden': True
                 }
        self.subtest_parse_match(text, kwargs)

        # Test center extraction
        text = "center A circle=BCD"
        kwargs = {
                  'name': 'A',
                  'type': 'center',
                  'circle': 'BCD'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test center extraction
        text = "center A hidden circle=BCD"
        kwargs = {
                  'name': 'A',
                  'type': 'center',
                  'circle': 'BCD',
                  'hidden': True
                 }
        self.subtest_parse_match(text, kwargs)

        # Test center extraction with named keyword argument
        text = "center name=\"Center BCD\" circle=BCD"
        kwargs = {
                  'name': 'Center BCD',
                  'type': 'center',
                  'circle': 'BCD'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test basic polygon extraction
        text = "polygon ABCD"
        kwargs = {
                  'name': 'ABCD',
                  'type': 'polygon'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test basic polygon extraction with keyword name
        text = "polygon name=EFGH"
        kwargs = {
                  'name': 'EFGH',
                  'type': 'polygon'
                 }
        self.subtest_parse_match(text, kwargs)

        # Test basic polygon extraction with keyword name
        text = "polygon name=vbce hidden"
        kwargs = {
                  'name': 'vbce',
                  'type': 'polygon',
                  'hidden': True
                 }
        self.subtest_parse_match(text, kwargs)

        # Test basic polygon extraction with keyword name and spaces in name
        text = "polygon name=\"My polygon\" hidden"
        kwargs = {
                  'name': 'My polygon',
                  'type': 'polygon',
                  'hidden': True
                 }
        self.subtest_parse_match(text, kwargs)

        # TODO: These next 3 tests are broken
        text = "loc A x=0 y=0"
        kwargs = {
                  'name': 'A',
                  'type': 'loc',
                  'x': '0',
                  'y': '0'
                 }
        self.subtest_parse_match(text, kwargs)

        text = "loc test x=2 y=2"
        kwargs = {
                  'name': 'test',
                  'type': 'loc',
                  'x': '2',
                  'y': '2'
                 }
        self.subtest_parse_match(text, kwargs)

        text = "loc \"Name with spaces\" x=2 y=2"
        kwargs = {
                  'name': 'Name with spaces',
                  'type': 'loc',
                  'x': '2',
                  'y': '2'
                 }
        self.subtest_parse_match(text, kwargs)

        text = "step"
        kwargs = {
                  'type': 'step'
                 }
        self.subtest_parse_match(text, kwargs)

        text = "clear"
        kwargs = {
                  'type': 'clear'
                 }
        self.subtest_parse_match(text, kwargs)

    def subtest_count_equal(self, parser_output, expected_list):
        """Wrapper around the assertCountEqual using a subtest
        Ensure that the output from each parser function is what we expect
        the output to be
        """
        with self.subTest(parser_output=parser_output,
                          expected_list=expected_list):
            self.assertCountEqual(parser_output, expected_list)

    def test_parse_point(self):
        """Test the point parser function"""

        # Reset the object dictionary, since there are tests that could have
        # been run before this one
        youclidbackend.main_parser.obj_dict = {}

        # [point A]
        kwargs = {
                  'name': 'A',
                  'type': 'point'
                 }
        parser_output = youclidbackend.main_parser.parse_point(kwargs)
        self.subtest_count_equal(parser_output,
                                 [youclidbackend.primitives.Point("A")])

        # [point A], with point A existing already
        parser_output = youclidbackend.main_parser.parse_point(kwargs)
        self.subtest_count_equal(parser_output,
                                 [youclidbackend.primitives.Point("A")])

        # [point mypoint]
        kwargs = {
                  'name': 'mypoint',
                  'type': 'point'
                 }
        parser_output = youclidbackend.main_parser.parse_point(kwargs)
        self.subtest_count_equal(parser_output,
                                 [youclidbackend.primitives.Point("mypoint")])

        # [point strange_char3cter!_in\[_here]
        kwargs = {
                  'name': 'strange_char3cter!_in\[_here',
                  'type': 'point'
                 }
        # TODO: What do we do about a bracket in a name?
        parser_output = youclidbackend.main_parser.parse_point(kwargs)
        self.subtest_count_equal(parser_output,
                                 [youclidbackend.primitives.Point(
                                    "strange_char3cter!_in\[_here")])

    def test_parse_line(self):
        """Test the line parser function"""

        # Reset the object dictionary, since there are tests that could have
        # been run before this one
        youclidbackend.main_parser.obj_dict = {}

        # [line AB] with nothing existing
        kwargs = {
                  'name': 'AB',
                  'type': 'line'
                 }
        line_AB = youclidbackend.primitives.Line("AB")
        point_A = youclidbackend.primitives.Point("A")
        point_B = youclidbackend.primitives.Point("B")
        parser_output = youclidbackend.main_parser.parse_line(kwargs)
        self.subtest_count_equal(parser_output,
                                 [line_AB, point_A, point_B])

        # [line AB] with everything existing
        parser_output = youclidbackend.main_parser.parse_line(kwargs)
        self.subtest_count_equal(parser_output,
                                 [line_AB, point_A, point_B])

        # [line name=my_line p1=A p2=B] with A and B existing
        kwargs = {
                  'name': 'my_line',
                  'type': 'line',
                  'p1': 'A',
                  'p2': 'B'
                 }
        # TODO: Is this how we want to do this? Do we want to pass the objects?
        line_my_line = youclidbackend.primitives.Line("my_line",
                                                      p1="A",
                                                      p2="B")
        parser_output = youclidbackend.main_parser.parse_line(kwargs)
        self.subtest_count_equal(parser_output,
                                 [line_my_line, point_A, point_B])

        # [line name=your_line p1=B p2=D] with nothing existing
        kwargs = {
                  'name': 'my_line',
                  'type': 'line',
                  'p1': 'B',
                  'p2': 'D'
                 }
        line_your_line = youclidbackend.primitives.Line("your_line",
                                                        p1="B",
                                                        p2="D")
        point_D = youclidbackend.primitives.Point("D")
        parser_output = youclidbackend.main_parser.parse_line(kwargs)
        self.subtest_count_equal(parser_output
                                 [line_your_line, point_B, point_D])

        # [line AB hidden] with everything existing
        kwargs = {
                  'name': 'my_line',
                  'type': 'line',
                  'p1': 'A',
                  'p2': 'B',
                  'hidden': True
                 }
        parser_output = youclidbackend.main_parser.parse_line(kwargs)
        self.subtest_count_equal(parser_output,
                                 [line_AB, point_A, point_B])

        # [line XY hidden] with nothing existing
        kwargs = {
                  'name': 'XY',
                  'type': 'line',
                  'p1': 'X',
                  'p2': 'Y',
                  'hidden': True
                 }
        point_X = youclidbackend.primitives.Point("X")
        point_Y = youclidbackend.primitives.Point("Y")
        line_XY = youclidbackend.primitives.Line("XY")
        parser_output = youclidbackend.main_parser.parse_line(kwargs)
        self.subtest_count_equal(parser_output,
                                 [line_XY, point_X, point_Y])

    def test_parse_circle(self):
        """Test the circle parser function"""

        # Reset the object dictionary, since there are tests that could have
        # been run before this one
        youclidbackend.main_parser.obj_dict = {}

        # [circle ABC] with nothing existing
        kwargs = {
                  'name': 'ABC',
                  'type': 'circle'
                 }

        circle_ABC = youclidbackend.primitives.Circle("ABC")
        point_A = youclidbackend.primitives.Point("A")
        point_B = youclidbackend.primitives.Point("B")
        point_C = youclidbackend.primitives.Point("C")
        parser_output = youclidbackend.main_parser.parse_circle(kwargs)
        self.subtest_count_equal(parser_output,
                                 [circle_ABC, point_A, point_B, point_C])

        # [circle ABC] with everything existing
        parser_output = youclidbackend.main_parser.parse_circle(kwargs)
        self.subtest_count_equal(parser_output,
                                 [circle_ABC, point_A, point_B, point_C])

        # [circle name=my_circle p1=A p2=B p3=C] with A, B, and C existing
        kwargs = {
                  'name': 'my_circle',
                  'type': 'circle',
                  'p1': 'A',
                  'p2': 'B',
                  'p3': 'C',
                 }

        circle_my_circle = youclidbackend.primitives.Circle("my_circle",
                                                        p1="A",
                                                        p2="B",
                                                        p3="C")

        parser_output = youclidbackend.main_parser.parse_circle(kwargs)
        self.subtest_count_equal(parser_output,
                                 [circle_my_circle, point_A, point_B, point_C])

        # [circle name=your_circle p1=D p2=E p3=F] with nothing existing
        kwargs = {
                  'name': 'your_circle',
                  'type': 'circle',
                  'p1': 'C',
                  'p2': 'D',
                  'p3': 'E',
                 }

        circle_your_circle = youclidbackend.primitives.Circle("your_circle",
                                                        p1="C",
                                                        p2="D",
                                                        p3="E")

        point_D = youclidbackend.primitives.Point("D")
        point_E = youclidbackend.primitives.Point("E")
        parser_output = youclidbackend.main_parser.parse_circle(kwargs)
        self.subtest_count_equal(parser_output,
                                 [circle_your_circle, point_C, point_D, point_E])

        # [circle ABC hidden] with everything existing
        kwargs = {
                  'name': 'my_circle',
                  'type': 'circle',
                  'p1': 'A',
                  'p2': 'B',
                  'p3': 'C',
                  'hidden': True
                 }

        parser_output = youclidbackend.main_parser.parse_circle(kwargs)
        self.subtest_count_equal(parser_output,
                                 [circle_ABC, point_A, point_B, point_C])

        # [circle XYZ hidden] with nothing existing
        kwargs = {
                  'name': 'XYZ',
                  'type': 'circle',
                  'p1': 'X',
                  'p2': 'Y',
                  'p3': 'Z',
                  'hidden': True
                 }

        circle_XYZ = youclidbackend.primitives.Circle("XYZ")
        point_X = youclidbackend.primitives.Point("X")
        point_Y = youclidbackend.primitives.Point("Y")
        point_Z = youclidbackend.primitives.Point("Z")
        parser_output = youclidbackend.main_parser.parse_circle(kwargs)
        self.subtest_count_equal(parser_output,
                                 [circle_XYZ, point_X, point_Y, point_Z])

    def test_parse_center(self):
        """Test the center parser function"""
        pass

    def test_parse_polygon(self):
        """Test the polygon parser function"""
        pass

    def test_parse_location(self):
        """Test the location parser function"""

        # Reset the object dictionary
        youclidbackend.main_parser.obj_dict = {}

        # Test implicit point generation
        kwargs = {
                  'name': 'A',
                  'type': 'loc',
                  'x': '0',
                  'y': '0'
                 }
        pointA = youclidbackend.main_parser.parse_location(kwargs)
        realPointA = youclidbackend.primitives.Point("A")
        realPointA.x = 0
        realPointA.y = 0

        self.assertEqual(pointA, realPointA)

        kwargs = {
                  'name': 'A',
                  'type': 'loc',
                  'x': '2',
                  'y': '3'
                 }
        realPointA.x = 2
        realPointA.y = 3
        pointA = youclidbackend.main_parser.parse_location(kwargs)

        self.assertEqual(pointA, realPointA)

        kwargs = {
                  'name': 'A',
                  'type': 'loc',
                  'x': '2.5',
                  'y': '3'
                 }
        realPointA.x = 2.5
        realPointA.y = 3
        pointA = youclidbackend.main_parser.parse_location(kwargs)

        self.assertEqual(pointA, realPointA)

        # Equality should hold regardless of name
        kwargs = {
                  'name': 'location',
                  'type': 'loc',
                  'x': '2.5',
                  'y': '3'
                 }
        realPointA.x = 2.5
        realPointA.y = 3
        pointA = youclidbackend.main_parser.parse_location(kwargs)

        self.assertEqual(pointA, realPointA)

    def test_parse_step(self):
        """Test the step parser function"""
        kwargs = {
                  'type': 'step'
                 }
        step = youclidbackend.main_parser._Step()
        parser_output = youclidbackend.main_parser.parse_step(kwargs)
        self.subtest_count_equal(parser_output, [step])

    def test_parse_clear(self):
        """Test the clear parser function"""
        kwargs = {
                  'type': 'clear'
                 }
        clear = youclidbackend.main_parser._Clear()
        parser_output = youclidbackend.main_parser.parse_clear(kwargs)
        self.subtest_count_equal(parser_output, [clear])

    def test_intermediate_representation(self):
        """Test that we generate the correct intermediate representation"""
        pass

    def test_html_generation(self):
        """TODO: Maybe we want to do this?"""
        pass


if __name__ == '__main__':
    unittest.main()
