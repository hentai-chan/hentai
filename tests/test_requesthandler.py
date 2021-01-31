import unittest

from src.hentai import RequestHandler


class TestRequestHandler(unittest.TestCase):
    def test_call_api(self):
        response = RequestHandler().get(url="https://nhentai.net/api/galleries/all")
        self.assertTrue(response.ok)
        self.assertNotIn('error', response.json())
        

if __name__ == '__main__':
    unittest.main()
