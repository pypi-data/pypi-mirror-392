class APIClientError(Exception):
    def __init__(self, message, response=None, body=None):
        super().__init__(message)
        self.response = response
        self.body = body


class AuthenticationError(APIClientError):
    pass


class NotFoundError(APIClientError):
    pass
