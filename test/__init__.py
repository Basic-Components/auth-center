import unittest

from App import create_app


class Test_auth(unittest.TestCase):

    def test_number_3_4(self):
        self.assertEqual(multiply(3,4),12)
    def test_string_a_3(self):
        self.assertEqual(multiply('a',3),'aaa'