import json
import random
import unittest
import platform
from pathlib import Path
from urllib.parse import urljoin

import requests
from src.hentai import Format, Hentai, Option, Sort, Utils


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tiny_evil = Hentai(269582)
        cls.tiny_evil_file = Path(f"{cls.tiny_evil.title(Format.Pretty)}.json")
        cls.tiny_evil_dir = Path(str(cls.tiny_evil.id))
        cls.tiny_evil_zip = Path(f"{cls.tiny_evil.id}.{'zip' if platform.system() == 'Windows' else 'tar.gz'}")

    @classmethod
    def tearDownClass(cls):
        remove_file = lambda file: Path(file).unlink() if Path(file).exists() else None

        remove_file(cls.tiny_evil_file)
        remove_file(cls.tiny_evil_zip)

    def test_random_id(self):
        random_id = Utils.get_random_id()
        response = requests.get(urljoin(Hentai._URL, str(random_id)))
        self.assertTrue(response.ok, msg=f"Failing ID: {random_id}. Failing URL: {response.url}")

    def test_random_hentai(self):
        random_hentai = Utils.get_random_hentai()
        response = requests.get(random_hentai.url)
        self.assertTrue(response.ok, msg=f"Failing ID: {random_hentai.id}. Failing URL: {response.url}")

    def test_download_queue(self):
        Utils.download([self.tiny_evil], progressbar=True, zip_dir=True)
        self.assertFalse(self.tiny_evil_dir.is_dir())
        self.assertTrue(self.tiny_evil_zip.is_file())

    def test_get_homepage(self):
        homepage = Utils.get_homepage().popular_now
        for doujin in homepage:
            self.assertIsNotNone(doujin.json, msg="Result should not be 'None'.")
            self.assertTrue(doujin.id, msg="ValueError: ID")
            self.assertTrue(doujin.title(), msg="ValueError: Title")
            self.assertTrue(doujin.media_id, msg="ValueError: MediaID")
            self.assertTrue(doujin.upload_date, msg="ValueError: UploadDate")
            self.assertTrue(doujin.cover, msg="ValueError: Cover")
            self.assertTrue(doujin.thumbnail, msg="ValueError: Thumbnail")
            self.assertTrue(doujin.image_urls, msg="ValueError: ImageURLs")
            self.assertTrue(doujin.num_pages, msg="ValueError: NumberOfPages")

    def test_browse_homepage_exception(self):
        with self.assertRaises(ValueError) as context:
            Utils.browse_homepage(start_page=5, end_page=1)
        self.assertTrue('Start page number should not exceed end page number', context.exception)

    def test_search_by_tag(self):
        holo_doujins = Utils.search_by_tag(33918, sort=Sort.PopularWeek)
        for doujin in holo_doujins:
            self.assertIsNotNone(doujin.json, msg="Result should not be 'None'.")
            self.assertTrue(doujin.id, msg="ValueError: ID")
            self.assertTrue(doujin.title(), msg="ValueError: Title")
            self.assertTrue(doujin.media_id, msg="ValueError: MediaID")
            self.assertTrue(doujin.upload_date, msg="ValueError: UploadDate")
            self.assertTrue(doujin.cover, msg="ValueError: Cover")
            self.assertTrue(doujin.thumbnail, msg="ValueError: Thumbnail")
            self.assertTrue(doujin.image_urls, msg="ValueError: ImageURLs")
            self.assertTrue(doujin.num_pages, msg="ValueError: NumberOfPages")

    def test_search_all_by_query(self):
        popular_3d = Utils.search_all_by_query(query="tag:3d", sort=Sort.PopularWeek)
        for doujin in popular_3d:
            self.assertIsNotNone(doujin.json, msg="Result should not be 'None'.")
            self.assertTrue(doujin.id, msg="ValueError: ID")
            self.assertTrue(doujin.title(), msg="ValueError: Title")
            self.assertTrue(doujin.media_id, msg="ValueError: MediaID")
            self.assertTrue(doujin.upload_date, msg="ValueError: UploadDate")
            self.assertTrue(doujin.cover, msg="ValueError: Cover")
            self.assertTrue(doujin.thumbnail, msg="ValueError: Thumbnail")
            self.assertTrue(doujin.image_urls, msg="ValueError: ImageURLs")
            self.assertTrue(doujin.num_pages, msg="ValueError: NumberOfPages")

    def test_export(self):
        # case 1 selects three options at random for populating options in export
        print(f"CASE 1: Exports '{self.tiny_evil.title(Format.Pretty)}' as {self.tiny_evil_file} to '{Path().cwd()}'")
        random_options = random.sample(Option.all(), k=3)
        print(f"CASE 1: Passing {','.join([opt.name for opt in random_options])} as options")
        self.tiny_evil.export(self.tiny_evil_file, options=random_options)

        with open(self.tiny_evil_file, mode='r', encoding='utf-8') as file_handler:
            test_data = json.load(file_handler)[0]
            self.assertEqual(3, len(test_data.keys()), msg="Keys don't match up (expected 3)")
            self.assertIn(random_options[0].value, test_data, msg=f"KeyError: {random_options[0].name} (Option 1)")
            self.assertIn(random_options[1].value, test_data, msg=f"KeyError: {random_options[1].name} (Option 2)")
            self.assertIn(random_options[2].value, test_data, msg=f"KeyError: {random_options[2].name} (Option 3)")

        # case 2 checks if three randomly selected options are in test_data
        print(f"CASE 2: Passing all options available")
        self.tiny_evil.export(self.tiny_evil_file)

        with open(self.tiny_evil_file, mode='r', encoding='utf-8') as file_handler:
            test_data = json.load(file_handler)[0]
            self.assertEqual(len(Option.all()), len(test_data.keys()), msg=f"Keys don't match up (expected {len(Option.all())} keys)")
            self.assertIn(random_options[0].value, test_data, msg=f"KeyError {random_options[0].name} (Option 1)")
            self.assertIn(random_options[1].value, test_data, msg=f"KeyError {random_options[1].name} (Option 2)")
            self.assertIn(random_options[2].value, test_data, msg=f"KeyError {random_options[2].name} (Option 3)")

        # case 3 checks the raw export option
        print(f"CASE 3: Passing Option.Raw")
        self.tiny_evil.export(self.tiny_evil_file, options=[Option.Raw])

        with open(self.tiny_evil_file, mode='r', encoding='utf-8') as file_handler:
            self.assertEqual(self.tiny_evil, Hentai(json=json.load(file_handler)[0]), msg=f"AssumptionError: Build from file should match request")


if __name__ == '__main__':
    unittest.main()
