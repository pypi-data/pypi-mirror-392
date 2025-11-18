"""HTTP errors."""


class HTTPRequestError(Exception):
    """Base HTTP request error."""


class HTTPConnectionError(HTTPRequestError):
    """Any error related to connection."""


class HTTPTimeoutError(HTTPRequestError):
    """HTTP request timed out."""


class HTTPInvalidResponseError(HTTPRequestError):
    """HTTP response is invalid."""


class HTTPError(HTTPRequestError):
    """HTTP error based on the status code."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"HTTP error {status_code}")


class HTTPClientError(HTTPError):
    """HTTP client error."""


class HTTPServerError(HTTPError):
    """HTTP server error."""
