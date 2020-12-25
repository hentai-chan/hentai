import unittest

from hentai import Hentai, Tag

class TestTag(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_response = Hentai(177013)

    def test_get(self):
        language = self.test_response.language
        self.assertEqual(Tag.get(language, 'name'), "english, translated", msg=f"Language Tag: {language}")
