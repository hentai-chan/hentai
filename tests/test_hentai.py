from build.lib import hentai
import sys
import json
import unittest
from datetime import datetime
from itertools import chain
from random import choices

import requests

from hentai import Format, Hentai


class TestHentai(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.test_response1 = Hentai(177013)
        cls.test_response2 = Hentai(269582)
        cls.test_response3 = Hentai(228922)
        cls.test_response4 = Hentai(297974)

        read = lambda id: json.load(open(f"./tests/{id}.json", mode='r'))

        cls.test_reference1 = read(177013)
        cls.test_reference2 = read(269582)
        cls.test_reference3 = read(228922)
        cls.test_reference4 = read(297974)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_response(self):
        self.assertNotIn('error', self.test_response1.json, msg=str(self.test_response1))
        self.assertNotIn('error', self.test_response2.json, msg=str(self.test_response2))
        self.assertNotIn('error', self.test_response3.json, msg=str(self.test_response3))
        self.assertNotIn('error', self.test_response4.json, msg=str(self.test_response4))      
    
    def test_media_id(self):
        self.assertEqual(Hentai.get_media_id(self.test_reference1), self.test_response1.media_id, msg=str(self.test_response1))
        self.assertEqual(Hentai.get_media_id(self.test_reference2), self.test_response2.media_id, msg=str(self.test_response2))
        self.assertEqual(Hentai.get_media_id(self.test_reference3), self.test_response3.media_id, msg=str(self.test_response3))
        self.assertEqual(Hentai.get_media_id(self.test_reference4), self.test_response4.media_id, msg=str(self.test_response4))

    def test_title(self):
        self.assertEqual(Hentai.get_title(self.test_reference1), self.test_response1.title(), msg=str(self.test_response1))
        self.assertEqual(Hentai.get_title(self.test_reference2), self.test_response2.title(), msg=str(self.test_response2))
        self.assertEqual(Hentai.get_title(self.test_reference3), self.test_response3.title(), msg=str(self.test_response3))
        self.assertEqual(Hentai.get_title(self.test_reference4), self.test_response4.title(), msg=str(self.test_response4))

    def test_cover(self):
        self.assertEqual(Hentai.get_cover(self.test_reference1), self.test_response1.cover, msg=str(self.test_response1))
        self.assertEqual(Hentai.get_cover(self.test_reference2), self.test_response2.cover, msg=str(self.test_response2))
        self.assertEqual(Hentai.get_cover(self.test_reference3), self.test_response3.cover, msg=str(self.test_response3))
        self.assertEqual(Hentai.get_cover(self.test_reference4), self.test_response4.cover, msg=str(self.test_response4))

    def test_thumbnail(self):
        self.assertEqual(Hentai.get_thumbnail(self.test_reference1), self.test_response1.thumbnail, msg=str(self.test_response1))
        self.assertEqual(Hentai.get_thumbnail(self.test_reference2), self.test_response2.thumbnail, msg=str(self.test_response2))
        self.assertEqual(Hentai.get_thumbnail(self.test_reference3), self.test_response3.thumbnail, msg=str(self.test_response3))
        self.assertEqual(Hentai.get_thumbnail(self.test_reference4), self.test_response4.thumbnail, msg=str(self.test_response4))

    def test_upload_date(self):
        format = "%Y/%m/%d"
        self.assertEqual(Hentai.get_upload_date(self.test_reference1).strftime(format), self.test_response1.upload_date.strftime(format), msg=str(self.test_response1))
        self.assertEqual(Hentai.get_upload_date(self.test_reference2).strftime(format), self.test_response2.upload_date.strftime(format), msg=str(self.test_response2))
        self.assertEqual(Hentai.get_upload_date(self.test_reference3).strftime(format), self.test_response3.upload_date.strftime(format), msg=str(self.test_response3))
        self.assertEqual(Hentai.get_upload_date(self.test_reference4).strftime(format), self.test_response4.upload_date.strftime(format), msg=str(self.test_response4))

    def test_tags(self):
        # out of sync error candidate
        self.assertEqual(Hentai.get_tags(self.test_reference1), self.test_response1.tags, msg=str(self.test_response1))
        self.assertEqual(Hentai.get_tags(self.test_reference2), self.test_response2.tags, msg=str(self.test_response2))
        self.assertEqual(Hentai.get_tags(self.test_reference3), self.test_response3.tags, msg=str(self.test_response3))
        self.assertEqual(Hentai.get_tags(self.test_reference4), self.test_response4.tags, msg=str(self.test_response4))

    def test_language(self):
        self.assertEqual(Hentai.get_language(self.test_reference1), self.test_response1.language, msg=str(self.test_response1))
        self.assertEqual(Hentai.get_language(self.test_reference2), self.test_response2.language, msg=str(self.test_response2))
        self.assertEqual(Hentai.get_language(self.test_reference3), self.test_response3.language, msg=str(self.test_response3))
        self.assertEqual(Hentai.get_language(self.test_reference4), self.test_response4.language, msg=str(self.test_response4))

    def test_artist(self):
        self.assertEqual(Hentai.get_artist(self.test_reference1), self.test_response1.artist, msg=str(self.test_response1))
        self.assertEqual(Hentai.get_artist(self.test_reference2), self.test_response2.artist, msg=str(self.test_response2))
        self.assertEqual(Hentai.get_artist(self.test_reference3), self.test_response3.artist, msg=str(self.test_response3))
        self.assertEqual(Hentai.get_artist(self.test_reference4), self.test_response4.artist, msg=str(self.test_response4))

    def test_category(self):
        # out of sync error candidate
        self.assertEqual(Hentai.get_category(self.test_reference1), self.test_response1.category, msg=str(self.test_response1))
        self.assertEqual(Hentai.get_category(self.test_reference2), self.test_response2.category, msg=str(self.test_response2))
        self.assertEqual(Hentai.get_category(self.test_reference3), self.test_response3.category, msg=str(self.test_response3))
        self.assertEqual(Hentai.get_category(self.test_reference4), self.test_response4.category, msg=str(self.test_response4))

    def test_num_pages(self):
        self.assertEqual(Hentai.get_num_pages(self.test_reference1), self.test_response1.num_pages, msg=str(self.test_response1))
        self.assertEqual(Hentai.get_num_pages(self.test_reference2), self.test_response2.num_pages, msg=str(self.test_response2))
        self.assertEqual(Hentai.get_num_pages(self.test_reference3), self.test_response3.num_pages, msg=str(self.test_response3))
        self.assertEqual(Hentai.get_num_pages(self.test_reference4), self.test_response4.num_pages, msg=str(self.test_response4))

    def test_num_favorites(self):
        self.assertLessEqual(Hentai.get_num_favorites(self.test_reference1), self.test_response1.num_favorites, msg=str(self.test_response1))
        self.assertLessEqual(Hentai.get_num_favorites(self.test_reference2), self.test_response2.num_favorites, msg=str(self.test_response2))
        self.assertLessEqual(Hentai.get_num_favorites(self.test_reference3), self.test_response3.num_favorites, msg=str(self.test_response3))
        self.assertLessEqual(Hentai.get_num_favorites(self.test_reference4), self.test_response4.num_favorites, msg=str(self.test_response4))

    def test_image_urls(self):
        choice1 = choices(self.test_response1.image_urls, k=5)
        choice2 = choices(self.test_response2.image_urls, k=5)
        choice3 = choices(self.test_response3.image_urls, k=5)
        choice4 = choices(self.test_response4.image_urls, k=5)
        for image_url in chain(choice1, choice2, choice3, choice4):
            response = requests.get(image_url)
            self.assertTrue(response.ok, msg=f"Failing URL: {image_url}")

    def test_exists(self):
        self.assertTrue(Hentai.exists(self.test_response1.id), msg=str(self.test_response1))
        self.assertTrue(Hentai.exists(self.test_response2.id), msg=str(self.test_response2))
        self.assertTrue(Hentai.exists(self.test_response3.id), msg=str(self.test_response3))
        self.assertTrue(Hentai.exists(self.test_response4.id), msg=str(self.test_response4))
        self.assertFalse(Hentai.exists(sys.maxsize), msg=f"Should have failed:{sys.maxsize}")
        self.assertFalse(Hentai.exists(-69), msg=f"Should have failed:{-69}")    

    def test_random_id(self):
        random_id = Hentai.get_random_id()
        response = requests.get(f"{Hentai._URL}{random_id}")
        self.assertTrue(response.ok, msg=f"Failing ID: {random_id} and URL: {response.url}")


if __name__ == '__main__':
    unittest.main()
