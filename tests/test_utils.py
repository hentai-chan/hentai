import json
import random
import shutil
import unittest
from pathlib import Path
from urllib.parse import urljoin

import requests
from hentai import Format, Hentai, Option, Sort, Utils


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tiny_evil = Hentai(269582)
        cls.tiny_evil_file = Path(f"{cls.tiny_evil.title(Format.Pretty)}.json")
        cls.tiny_evil_dir = Path(cls.tiny_evil.title(Format.Pretty))
    
    @classmethod
    def tearDownClass(cls):
        # missing_ok=True is only available in python 3.8+
        remove_file = lambda file: Path(file).unlink()
        remove_dir = lambda dir: shutil.rmtree(dir, ignore_errors=True)

        remove_file(cls.tiny_evil_file)
        remove_dir(cls.tiny_evil_dir)
    
    def test_random_id(self):
        random_id = Utils.get_random_id()
        response = requests.get(urljoin(Hentai._URL, str(random_id)))
        self.assertTrue(response.ok, msg=f"Failing ID: {random_id}. Failing URL: {response.url}")

    def test_random_hentai(self):
        random_hentai = Utils.get_random_hentai()
        response = requests.get(random_hentai.url)
        self.assertTrue(response.ok, msg=f"Failing ID: {random_hentai.id}. Failing URL: {response.url}")

    def test_download_queue(self):
        Utils.download([self.tiny_evil.id])
        self.assertTrue(self.tiny_evil_dir.is_dir())

    def test_get_homepage(self):
        homepage = Utils.get_homepage()
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
        random_options = random.sample([opt for opt in Option if opt.value != 'raw'], k=3)
        print(f"CASE 1: Passing {','.join([opt.name for opt in random_options])} as options")
        self.tiny_evil.export(self.tiny_evil_file, options=random_options)

        with open(self.tiny_evil_file, mode='r', encoding='utf-8') as file_handler:
            test_data = json.load(file_handler)['result'][0]
            self.assertEqual(3, len(test_data.keys()), msg="Keys don't match up (expected 3)")
            self.assertIn(random_options[0].value, test_data, msg=f"KeyError: {random_options[0].name} (Option 1)")
            self.assertIn(random_options[1].value, test_data, msg=f"KeyError: {random_options[1].name} (Option 2)")
            self.assertIn(random_options[2].value, test_data, msg=f"KeyError: {random_options[2].name} (Option 3)")  

        # case 2 checks if three randomly selected options are in test_data
        print(f"CASE 2: Passing all options available")
        self.tiny_evil.export(self.tiny_evil_file)    

        with open(self.tiny_evil_file, mode='r', encoding='utf-8') as file_handler:
            test_data = json.load(file_handler)['result'][0]
            self.assertEqual(19, len(test_data.keys()), msg="Keys don't match up (expected 15)")
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
