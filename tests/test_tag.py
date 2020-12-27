import unittest
from urllib.parse import urljoin

from hentai import Hentai, Tag, Option

class TestTag(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_response = Hentai(177013)

    def test_get(self):
        language = self.test_response.language
        self.assertEqual(Tag.get(language, 'name'), "english, translated", msg=f"Language Tag: {language}")

    def test_list(self):
        characters = Tag.list(Option.Character)
        for char in characters:
            if char.name == 'holo':
                holo = char

                self.assertEqual(holo.id, 33918)
                self.assertEqual(holo.type, 'character')
                self.assertEqual(holo.name, 'holo')
                self.assertEqual(holo.url, urljoin(Hentai.HOME, '/character/holo/'))
                self.assertEqual(holo.count, 160)
                break
