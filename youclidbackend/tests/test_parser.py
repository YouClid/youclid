import unittest
import youclidbackend


class TestParser(unittest.TestCase):

    def test_extract(self):
        """Ensure that the parser extracts just our markup"""

        # Test basic extraction
        text = "[point A]"
        extracted = [x.group(0) for x in
                     list(youclidbackend.main_parser.extract(text))]
        self.assertEqual(extracted, ['[point A]'])

        # Test multiple elements on the same line
        text = "[point A][circle ABC]"
        extracted = [x.group(0) for x in
                     list(youclidbackend.main_parser.extract(text))]
        self.assertEqual(extracted, ["[point A]", "[circle ABC]"])

        # Test text interspersed with markup
        text = "[point A]"\
               "[circle ABC]"\
               "This is some text with a reference to [point A]."\
               "This is some text with a reference to [circle name=ABC]."\
               "[step]"
        extracted = [x.group(0) for x in
                     list(youclidbackend.main_parser.extract(text))]
        self.assertEqual(extracted, ["[point A]",
                                     "[circle ABC]",
                                     "[point A]",
                                     "[circle name=ABC]",
                                     "[step]"])

        # Test what should be none of our markup
        text = "\[This should just be some text\]"
        extracted = list(youclidbackend.main_parser.extract(text))
        self.assertEqual(extracted, [])

        # Test everything that we support
        text = "\[This should just be some text\]"\
               "[circle ABC] [center D circle=ABC]"\
               "[line AB]"\
               "[point D]"\
               "[polygon ABCD]"\
               "[loc A 0 0]"\
               "[step]"\
               "[clear]"
        extracted = [x.group(0) for x in
                     list(youclidbackend.main_parser.extract(text))]
        self.assertEqual(extracted, ["[circle ABC]",
                                     "[center D circle=ABC]",
                                     "[line AB]",
                                     "[point D]",
                                     "[polygon ABCD]",
                                     "[loc A 0 0]",
                                     "[step]",
                                     "[clear]"])

        # Test using a ] in an element name
        text = "[circle name=myname\]]"
        extracted = [x.group(0) for x in
                     list(youclidbackend.main_parser.extract(text))]
        self.assertEqual(extracted, ["[circle name=myname\]]"])

    def test_parse_match(self):
        """Test that we extract attributes of vaious elements correctly"""

        # Test basic single letter name
        text = "[point A]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'A',
                                      'type': 'point'
                                     })
        text = "[point B]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'B',
                                      'type': 'point'
                                     })
        # Test multiple character name
        text = "[point hello]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'hello',
                                      'type': 'point'
                                     })

        # Keyword argument tests

        # Test keyword argument for name with single letter
        text = "[point name=A]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'A',
                                      'type': 'point'
                                     })
        # Test keyword argument for name with multiple letters
        text = "[point name=mypoint]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'mypoint',
                                      'type': 'point'
                                     })

        # Test keyword argument for name with an escaped bracket
        # TODO: How do we handle this; does the name have the backslash in it?
        text = "[point name=mypoint\]]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'mypoint]',
                                      'type': 'point'
                                     })

        # Test keyword argument for name with multiple letters
        text = "[point name=\"mypoint with spaces\"]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'mypoint with spaces',
                                      'type': 'point'
                                     })

        # Test non-keyword arguments
        text = "[point A hidden somethingelse]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, ["hidden", "somethingelse"])
            self.assertEqual(kwargs, {
                                      'name': 'A',
                                      'type': 'point'
                                     })

        # Test the line extraction
        text = "[line AB]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'AB',
                                      'type': 'line'
                                     })

        # Test line extraction with a name
        text = "[line AB name=test]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'test',
                                      'type': 'line'
                                     })
        text = "[line name=test]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'test',
                                      'type': 'line'
                                     })

        # TODO: I'm not sure if this is how we will do this; it may change
        text = "[line name=test p1=A p2=B]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'test',
                                      'type': 'line',
                                      'p1': 'A',
                                      'p2': 'B'
                                     })

        # Test non-keyword arguments
        text = "[line AB hidden]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, ["hidden"])
            self.assertEqual(kwargs, {
                                      'name': 'AB',
                                      'type': 'line'
                                     })

        # Test circle extraction
        text = "[circle ABC]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'ABC',
                                      'type': 'circle'
                                     })

        text = "[circle name=ABC]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'ABC',
                                      'type': 'circle'
                                     })

        # Test circle extraction with center
        text = "[circle ABC center=D]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'ABC',
                                      'type': 'circle',
                                      'center': 'D'
                                     })

        # Test circle extraction with center and radius
        text = "[circle ABC center=E radius=10]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'ABC',
                                      'type': 'circle',
                                      'center': 'E',
                                      'radius': '10'
                                     })

        # Test circle extraction with center and radius and named keyword
        text = "[circle name=XYZ center=L radius=1]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'XYZ',
                                      'type': 'circle',
                                      'center': 'L',
                                      'radius': '1'
                                     })

        # Test circle extraction spaces in name
        text = "[circle name=\"My circle\" center=\"My point\" radius=1]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'My circle',
                                      'type': 'circle',
                                      'center': 'My point',
                                      'radius': '1'
                                     })

        # Test circle extraction with center and radius and named keyword
        text = "[circle name=XYZ hidden]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, ["hidden"])
            self.assertEqual(kwargs, {
                                      'name': 'XYZ',
                                      'type': 'circle'
                                     })

        # Test circle extraction with center and radius and named keyword, with
        # the order of hidden and name switched
        # TODO: This unittest breaks, presumably because it thinks that the
        # name is "hidden"; do we do anything about this?
        text = "[circle hidden name=XYZ]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, ["hidden"])
            self.assertEqual(kwargs, {
                                      'name': 'XYZ',
                                      'type': 'circle'
                                     })

        # Test center extraction
        text = "[center A circle=BCD]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'A',
                                      'type': 'center',
                                      'circle': 'BCD'
                                     })

        # Test center extraction
        text = "[center A hidden circle=BCD]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, ["hidden"])
            self.assertEqual(kwargs, {
                                      'name': 'A',
                                      'type': 'center',
                                      'circle': 'BCD'
                                     })

        # Test center extraction with named keyword argument
        text = "[center name=\"Center BCD\" circle=BCD]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'Center BCD',
                                      'type': 'center',
                                      'circle': 'BCD'
                                     })

        # Test basic polygon extraction
        text = "[polygon ABCD]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'ABCD',
                                      'type': 'polygon'
                                     })

        # Test basic polygon extraction with keyword name
        text = "[polygon name=EFGH]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'EFGH',
                                      'type': 'polygon'
                                     })

        # Test basic polygon extraction with keyword name
        text = "[polygon name=vbce hidden]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, ["hidden"])
            self.assertEqual(kwargs, {
                                      'name': 'vbce',
                                      'type': 'polygon'
                                     })

        # Test basic polygon extraction with keyword name and spaces in name
        text = "[polygon name=\"My polygon\" hidden]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, ["hidden"])
            self.assertEqual(kwargs, {
                                      'name': 'My polygon',
                                      'type': 'polygon'
                                     })

        text = "[loc A 0 0]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, ['0', '0'])
            self.assertEqual(kwargs, {
                                      'name': 'A',
                                      'type': 'loc'
                                     })

        text = "[loc test 2 2]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, ['2', '2'])
            self.assertEqual(kwargs, {
                                      'name': 'test',
                                      'type': 'loc'
                                     })

        text = "[loc \"Name with spaces\" 2 2]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, ['2', '2'])
            self.assertEqual(kwargs, {
                                      'name': 'Name with spaces',
                                      'type': 'loc'
                                     })

        text = "[step]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'type': 'step'
                                     })

        text = "[clear]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'type': 'clear'
                                     })

    def test_parse_point(self):
        """Test the point parser function"""

        # [point A]
        arglist = []
        kwargs = {
                  'name': 'A',
                  'type': 'point'
                 }
        self.assertEqual(youclidbackend.main_parser.parse_point(kwargs,
                                                                arglist),
                         [youclidbackend.primitives.Point("A")])

        # [point A], with point A existing already
        self.assertEqual(youclidbackend.main_parser.parse_point(kwargs,
                                                                arglist),
                         [youclidbackend.primitives.Point("A")])

        # [point mypoint]
        arglist = []
        kwargs = {
                  'name': 'mypoint',
                  'type': 'point'
                 }
        self.assertEqual(youclidbackend.main_parser.parse_point(kwargs,
                                                                arglist),
                         [youclidbackend.primitives.Point("mypoint")])

        # [point strange_char3cter!_in\[_here]
        arglist = []
        kwargs = {
                  'name': 'strange_char3cter!_in\[_here',
                  'type': 'point'
                 }
        # TODO: What do we do about a bracket in a name?
        self.assertEqual(youclidbackend.main_parser.parse_point(kwargs,
                                                                arglist),
                         [youclidbackend.primitives.Point(
                            "strange_char3cter!_in\[_here")])

    def test_parse_line(self):
        """Test the line parser function"""
        pass

    def test_parse_circle(self):
        """Test the circle parser function"""
        pass

    def test_parse_center(self):
        """Test the center parser function"""
        pass

    def test_parse_polygon(self):
        """Test the polygon parser function"""
        pass

    def test_parse_location(self):
        """Test the location parser function"""
        pass

    def test_parse_step(self):
        """Test the step parser function"""
        pass

    def test_parse_clear(self):
        """Test the clear parser function"""
        pass

    def test_intermediate_representation(self):
        """Test that we generate the correct intermediate representation"""
        pass

    def test_html_generation(self):
        """TODO: Maybe we want to do this?"""
        pass


if __name__ == '__main__':
    unittest.main()
