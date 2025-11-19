import unittest
from orcatech_client.client import APIClient
from orcatech_client.config import Config, APIOption

class TestAPIClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Config.validate()
        cls.host = Config.HOST_URL
        cls.token = Config.AUTH_TOKEN
        cls.client = APIClient(cls.host)
        cls.client.headers['Authorization'] = f"Bearer {cls.token}"

    def test_get_scope(self):
        pathname = "/scopes/study/2"
        options = [APIOption(header={"Custom-Header": "value"})]

        try:
            result = self.client.get_scope(self.client.base_url, pathname, *options)
            print(result)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"get_scope method failed with exception: {e}")
    def test_get_scopes(self):
        pathname = "/scopes/organization"
        options = [APIOption(header={"Custom-Header": "value"})]

        try:
            result = self.client.get_scopes(self.client.base_url, pathname, *options)
            print("result is printing",result)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"get_scopes method failed with exception: {e}")

if __name__ == '__main__':
    unittest.main()