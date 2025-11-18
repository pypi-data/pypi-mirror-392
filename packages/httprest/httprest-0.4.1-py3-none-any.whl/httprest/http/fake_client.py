"""Fake client."""

from typing import Any, Dict, List, Optional, Union

from httprest.http.base import HTTPResponse

from .base import HTTPClient
from .cert import ClientCertificate
from .errors import HTTPTimeoutError


class FakeHTTPClient(HTTPClient):
    """Fake HTTP client."""

    def __init__(
        self, responses: Optional[List[Union[Exception, HTTPResponse]]] = None
    ) -> None:
        # pylint:disable=super-init-not-called
        self.history: List[Dict[str, Optional[Any]]] = []
        self._responses = responses

    def _request(
        self,
        method: str,
        url: str,
        data: Optional[Union[dict, bytes]] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        cert: Optional[ClientCertificate] = None,
    ) -> HTTPResponse:
        # pylint:disable=too-many-arguments
        entry: dict = {
            "_method": "_request",
            "method": method,
            "url": url,
        }

        if data is not None:
            entry["data"] = data
        if json is not None:
            entry["json"] = json
        if headers is not None:
            entry["headers"] = headers
        if cert is not None:
            entry["cert"] = cert

        self.history.append(entry)
        if not self._responses:
            raise HTTPTimeoutError("No response provided")

        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response

        return response
