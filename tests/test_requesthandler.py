import unittest

from requests.status_codes import codes

from hentai import RequestHandler


class TestRequestHandler(unittest.TestCase):

    def test_call_api(self):
        response = RequestHandler().call_api(url="https://nhentai.net/api/galleries/all")
        self.assertEqual(response.status_code, codes.ok)
        

if __name__ == '__main__':
    unittest.main()
