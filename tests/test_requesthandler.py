import unittest

from hentai import RequestHandler


class TestRequestHandler(unittest.TestCase):

    def test_call_api(self):
        response = RequestHandler().call_api(url="https://nhentai.net/api/galleries/all")
        self.assertTrue(response.status_code)
        

if __name__ == '__main__':
    unittest.main()
