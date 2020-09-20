import unittest
from datetime import datetime
from itertools import chain
from random import choices

import requests

from hentai import Format, Hentai


class TestHentai(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.test_case1 = Hentai(177013)
        cls.test_case2 = Hentai(269582)
        cls.test_case3 = Hentai(228922)
        cls.test_case4 = Hentai(297974)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_response(self):
        self.assertNotIn('error', self.test_case1.json, msg=str(self.test_case1))
        self.assertNotIn('error', self.test_case2.json, msg=str(self.test_case2))
        self.assertNotIn('error', self.test_case3.json, msg=str(self.test_case3))
        self.assertNotIn('error', self.test_case4.json, msg=str(self.test_case4))      
    
    def test_media_id(self):
        self.assertEqual(987560, self.test_case1.media_id, msg=str(self.test_case1))
        self.assertEqual(1401397, self.test_case2.media_id, msg=str(self.test_case2))
        self.assertEqual(1205270, self.test_case3.media_id, msg=str(self.test_case3))
        self.assertEqual(1553654, self.test_case4.media_id, msg=str(self.test_case4))

    def test_title(self):
        self.assertEqual('METAMORPHOSIS', self.test_case1.title(Format.Pretty), msg=str(self.test_case1))
        self.assertEqual('Tiny Evils chans!tachi no Ecchi na Tanpenshuu-', self.test_case2.title(Format.Pretty), msg=str(self.test_case2))
        self.assertEqual('EROGROS Vol. 2', self.test_case3.title(Format.Pretty), msg=str(self.test_case3))
        self.assertEqual('Joshi Kōsei Rich Thots', self.test_case4.title(Format.Pretty), msg=str(self.test_case4))

    def test_cover(self):
        self.assertEqual('https://t.nhentai.net/galleries/987560/cover.jpg', self.test_case1.cover, msg=str(self.test_case1))
        self.assertEqual('https://t.nhentai.net/galleries/1401397/cover.jpg', self.test_case2.cover, msg=str(self.test_case2))
        self.assertEqual('https://t.nhentai.net/galleries/1205270/cover.jpg', self.test_case3.cover, msg=str(self.test_case3))
        self.assertEqual('https://t.nhentai.net/galleries/1553654/cover.png', self.test_case4.cover, msg=str(self.test_case4))

    def test_thumbnail(self):
        self.assertEqual('https://t.nhentai.net/galleries/987560/thumb.jpg', self.test_case1.thumbnail, msg=str(self.test_case1))
        self.assertEqual('https://t.nhentai.net/galleries/1401397/thumb.jpg', self.test_case2.thumbnail, msg=str(self.test_case2))
        self.assertEqual('https://t.nhentai.net/galleries/1205270/thumb.jpg', self.test_case3.thumbnail, msg=str(self.test_case3))
        self.assertEqual('https://t.nhentai.net/galleries/1553654/thumb.png', self.test_case4.thumbnail, msg=str(self.test_case4))

    def test_upload_date(self):
        format = "%Y/%m/%d"
        self.assertEqual(datetime(2016, 10, 18, 14, 28, 49).strftime(format), self.test_case1.upload_date.strftime(format), msg=str(self.test_case1))
        self.assertEqual(datetime(2019, 4, 20, 14, 54, 7).strftime(format), self.test_case2.upload_date.strftime(format), msg=str(self.test_case2))
        self.assertEqual(datetime(2018, 4, 1, 4, 46, 39).strftime(format), self.test_case3.upload_date.strftime(format), msg=str(self.test_case3))
        self.assertEqual(datetime(2020, 1, 17, 11, 19, 24).strftime(format), self.test_case4.upload_date.strftime(format), msg=str(self.test_case4))

    def test_tags(self):
        self.assertEqual('dark skin', self.test_case1.tags[0].name, msg=str(self.test_case1))
        self.assertEqual('miniguy', self.test_case2.tags[0].name, msg=str(self.test_case2))
        self.assertEqual('anal birth', self.test_case3.tags[0].name, msg=str(self.test_case3))
        self.assertEqual('crossdressing', self.test_case4.tags[0].name, msg=str(self.test_case4))

    def test_language(self):
        self.assertEqual('english', self.test_case1.language[0].name, msg=str(self.test_case1))
        self.assertEqual('english', self.test_case2.language[0].name, msg=str(self.test_case2))
        self.assertEqual('japanese', self.test_case3.language[0].name, msg=str(self.test_case3))
        self.assertEqual('english', self.test_case4.language[0].name, msg=str(self.test_case4))

    def test_artist(self):
        self.assertEqual('shindol', self.test_case1.artist[0].name, msg=str(self.test_case1))
        self.assertEqual('muk', self.test_case2.artist[0].name, msg=str(self.test_case2))
        self.assertEqual('ai7n', self.test_case3.artist[0].name, msg=str(self.test_case3))
        self.assertEqual('sky', self.test_case4.artist[0].name, msg=str(self.test_case4))

    def test_category(self):
        self.assertEqual('manga', self.test_case1.category[0].name, msg=str(self.test_case1))
        self.assertEqual('doujinshi', self.test_case2.category[0].name, msg=str(self.test_case2))
        self.assertEqual('manga', self.test_case3.category[0].name, msg=str(self.test_case3))
        self.assertEqual('doujinshi', self.test_case4.category[0].name, msg=str(self.test_case4))

    def test_num_pages(self):
        self.assertEqual(225, self.test_case1.num_pages, msg=str(self.test_case1))
        self.assertEqual(14, self.test_case2.num_pages, msg=str(self.test_case2))
        self.assertEqual(244, self.test_case3.num_pages, msg=str(self.test_case3))
        self.assertEqual(55, self.test_case4.num_pages, msg=str(self.test_case4))

    def test_num_favorites(self):
        self.assertLessEqual(44548, self.test_case1.num_favorites, msg=str(self.test_case1))
        self.assertLessEqual(6163, self.test_case2.num_favorites, msg=str(self.test_case2))
        self.assertLessEqual(2900, self.test_case3.num_favorites, msg=str(self.test_case3))
        self.assertLessEqual(26671, self.test_case4.num_favorites, msg=str(self.test_case4))

    def test_image_urls(self):
        choice1 = choices(self.test_case1.image_urls, k=5)
        choice2 = choices(self.test_case2.image_urls, k=5)
        choice3 = choices(self.test_case3.image_urls, k=5)
        choice4 = choices(self.test_case4.image_urls, k=5)
        for image_url in chain(choice1, choice2, choice3, choice4):
            response = requests.get(image_url)
            self.assertTrue(response.ok, msg=f"Failing URL: {image_url}")

    def test_random_id(self):
        random_id = Hentai.get_random_id()
        response = requests.get(f"{Hentai._URL}{random_id}")
        self.assertTrue(response.ok, msg=f"Failing ID: {random_id}")


if __name__ == '__main__':
    unittest.main()
