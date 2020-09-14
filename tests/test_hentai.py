import unittest
from hentai import Hentai

class TestHentai(unittest.TestCase):
    def test_hello_world(self):
        result = Hentai.hello_world()
        self.assertEqual(result, "Hello, World!")

if __name__ == '__main__':
    unittest.main()