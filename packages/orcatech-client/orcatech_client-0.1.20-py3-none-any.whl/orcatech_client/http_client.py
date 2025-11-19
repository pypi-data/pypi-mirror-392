import requests
from .exceptions import APIClientError


class HTTPClient:
    @staticmethod
    def request(method, url, headers=None, params=None, json=None):
        try:
            response = requests.request(
                method, url, headers=headers, params=params, json=json
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise APIClientError(str(e), response=e.response)

    @staticmethod
    def get(url, headers=None, params=None):
        return HTTPClient.request("GET", url, headers=headers, params=params)

    @staticmethod
    def post(url, headers=None, json=None):
        return HTTPClient.request("POST", url, headers=headers, json=json)

    @staticmethod
    def put(url, headers=None, json=None):
        return HTTPClient.request("PUT", url, headers=headers, json=json)

    @staticmethod
    def delete(url, headers=None):
        return HTTPClient.request("DELETE", url, headers=headers)
