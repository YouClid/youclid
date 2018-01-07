import unittest
import youclidbackend


class TestStringMethods(unittest.TestCase):

    def test_extract(self):
        """Ensure that we extract the correct things"""
        pass

    def test_parse_match(self):
        pass

    def test_parse_point(self):
        """Test the point parser function"""

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

        # Test keyword argument for name with multiple letters
        text = "[point name=\"mypoint with spaces\"]"
        for match in youclidbackend.main_parser.extract(text):
            kwargs, arglist = youclidbackend.main_parser._parse_match(match[1])
            self.assertEqual(arglist, [])
            self.assertEqual(kwargs, {
                                      'name': 'mypoint with spaces',
                                      'type': 'point'
                                     })

    def test_parse_line(self):
        pass

    def test_parse_circle(self):
        pass

    def test_parse_center(self):
        pass

    def test_parse_polygon(self):
        pass

    def test_parse_location(self):
        pass

    def test_parse_step(self):
        pass

    def test_parse_clear(self):
        pass


if __name__ == '__main__':
    unittest.main()
