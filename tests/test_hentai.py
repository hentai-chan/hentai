import json
import sys
import unittest
from random import choices
from urllib.parse import urlparse

from hentai import Hentai


class TestHentai(unittest.TestCase):    
    @classmethod
    def setUpClass(cls):
        cls.test_response1 = Hentai(177013)

        read = lambda id: json.load(open(f"./tests/{id}.json", mode='r'))

        cls.test_reference1 = read(177013)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_response(self):
        self.assertNotIn('error', self.test_response1.json, msg=str(self.test_response1))  
    
    def test_media_id(self):
        self.assertEqual(Hentai.get_media_id(self.test_reference1), self.test_response1.media_id, msg=str(self.test_response1))

    def test_title(self):
        self.assertEqual(Hentai.get_title(self.test_reference1), self.test_response1.title(), msg=str(self.test_response1))

    def test_cover(self):
        self.assertEqual(Hentai.get_cover(self.test_reference1), self.test_response1.cover, msg=str(self.test_response1))

    def test_thumbnail(self):
        self.assertEqual(Hentai.get_thumbnail(self.test_reference1), self.test_response1.thumbnail, msg=str(self.test_response1))

    def test_upload_date(self):
        self.assertEqual(Hentai.get_upload_date(self.test_reference1), self.test_response1.upload_date, msg=str(self.test_response1))

    def test_tags(self):
        # out of sync error candidate
        self.assertEqual(Hentai.get_tag(self.test_reference1), self.test_response1.tag, msg=str(self.test_response1))

    def test_language(self):
        self.assertEqual(Hentai.get_language(self.test_reference1), self.test_response1.language, msg=str(self.test_response1))

    def test_artist(self):
        self.assertEqual(Hentai.get_artist(self.test_reference1), self.test_response1.artist, msg=str(self.test_response1))

    def test_category(self):
        # out of sync error candidate
        self.assertEqual(Hentai.get_category(self.test_reference1), self.test_response1.category, msg=str(self.test_response1))

    def test_num_pages(self):
        self.assertEqual(Hentai.get_num_pages(self.test_reference1), self.test_response1.num_pages, msg=str(self.test_response1))

    def test_num_favorites(self):
        self.assertLessEqual(Hentai.get_num_favorites(self.test_reference1), self.test_response1.num_favorites, msg=str(self.test_response1))
        
    def test_image_urls(self):
        for image_url in map(urlparse, choices(self.test_response1.image_urls, k=10)):
            self.assertTrue(image_url.scheme, msg=f"AssertSchemeError: {image_url}")
            self.assertTrue(image_url.netloc, msg=f"AssertNetlocError: {image_url}")
            self.assertTrue(image_url.path, msg=f"AssertPathError: {image_url}")

    def test_exists(self):
        self.assertTrue(Hentai.exists(self.test_response1.id), msg=str(self.test_response1))
        self.assertTrue(Hentai.exists(self.test_response1.id, make_request=False), msg=f"{str(self.test_response1)}: make_request=False")
        self.assertFalse(Hentai.exists(sys.maxsize), msg=f"Should have failed:{sys.maxsize}")
        self.assertFalse(Hentai.exists(-69), msg=f"Should have failed:{-69}")    


if __name__ == '__main__':
    unittest.main()
