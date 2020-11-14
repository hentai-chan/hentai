import json
import sys
import unittest
from random import choices
from urllib.parse import urlparse

from hentai import Hentai


class TestHentai(unittest.TestCase):    
    @classmethod
    def setUpClass(cls):
        cls.test_response = Hentai(177013)

        read = lambda id: json.load(open(f"./tests/{id}.json", mode='r'))

        cls.test_reference = Hentai(json=read(177013))

    @classmethod
    def tearDownClass(cls):
        pass

    def test_response_json(self):
        self.assertNotIn('error', self.test_response.json, msg=str(self.test_response))  
    
    def test_media_id(self):
        self.assertEqual(self.test_reference.media_id, self.test_response.media_id, msg=str(self.test_response))

    def test_title(self):
        self.assertEqual(self.test_reference.title(), self.test_response.title(), msg=str(self.test_response))

    def test_scanlator(self):
        self.assertEqual(self.test_reference.scanlator, self.test_response.scanlator, msg=str(self.test_response))

    def test_cover(self):
        self.assertEqual(self.test_reference.cover, self.test_response.cover, msg=str(self.test_response))

    def test_thumbnail(self):
        self.assertEqual(self.test_reference.thumbnail, self.test_response.thumbnail, msg=str(self.test_response))

    def test_upload_date(self):
        self.assertEqual(self.test_reference.upload_date, self.test_response.upload_date, msg=str(self.test_response))

    def test_tag(self):
        self.assertEqual(self.test_reference.tag, self.test_response.tag, msg=str(self.test_response))

    def test_group(self):
        self.assertEqual(self.test_reference.group, self.test_response.group, msg=str(self.test_response))

    def test_parody(self):
        self.assertEqual(self.test_reference.parody, self.test_response.parody, msg=str(self.test_response))

    def test_character(self):
        self.assertEqual(self.test_reference.character, self.test_response.character, msg=str(self.test_response))

    def test_language(self):
        self.assertEqual(self.test_reference.language, self.test_response.language, msg=str(self.test_response))

    def test_artist(self):
        self.assertEqual(self.test_reference.artist, self.test_response.artist, msg=str(self.test_response))

    def test_category(self):
        self.assertEqual(self.test_reference.category, self.test_response.category, msg=str(self.test_response))

    def test_num_pages(self):
        self.assertEqual(self.test_reference.num_pages, self.test_response.num_pages, msg=str(self.test_response))

    def test_num_favorites(self):
        self.assertLessEqual(self.test_reference.num_favorites, self.test_response.num_favorites, msg=str(self.test_response))
        
    def test_image_urls(self):
        for image_url in map(urlparse, choices(self.test_response.image_urls, k=10)):
            self.assertTrue(image_url.scheme, msg=f"AssertSchemeError: {image_url}")
            self.assertTrue(image_url.netloc, msg=f"AssertNetlocError: {image_url}")
            self.assertTrue(image_url.path, msg=f"AssertPathError: {image_url}")

    def test_exists(self):
        self.assertTrue(Hentai.exists(self.test_response.id), msg=str(self.test_response))
        self.assertFalse(Hentai.exists(sys.maxsize), msg=f"Should have failed:{sys.maxsize}")
        self.assertFalse(Hentai.exists(-69), msg=f"Should have failed:{-69}")    


if __name__ == '__main__':
    unittest.main()
