"""Base client."""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Union
from urllib.parse import urlencode

from .auth import BaseAuth
from .cert import ClientCertificate
from .response import HTTPResponse
from .timeout import Timeout


class HTTPClient(ABC):
    """Base HTTP client."""

    def __init__(self, timeout: Optional[Timeout] = None) -> None:
        self._timeout = timeout

    @abstractmethod
    def _request(
        self,
        method: str,
        url: str,
        data: Optional[Union[dict, bytes]] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        cert: Optional[ClientCertificate] = None,
    ) -> HTTPResponse:
        # pylint: disable=too-many-arguments
        """Perform request.

        This method must handle all possible HTTP exceptions and raise them
        as `HTTPRequestError`.

        Headers may be extended if necessary.

        .. warning:: there is no unified handling for `cert`. The client must
          raise NotImplementedError if client side certificates are not
          supported
        """

    def request(
        self,
        method: str,
        url: str,
        data: Optional[Union[dict, bytes]] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        auth: Optional[BaseAuth] = None,
        cert: Optional[ClientCertificate] = None,
    ) -> HTTPResponse:
        # pylint: disable=too-many-arguments
        """Perform HTTP request with a given HTTP method.

        :param method: HTTP method to use
        :param url: API URL
        :param data: data to post. If dict is provided,
          application/x-www-form-urlencoded is set automatically
        :param json: JSON data to post
        :param headers: headers
        :param params: query parameters. If provided, the url will be extended
        :param auth: authorization to use. If provided, the headers will be
          extended
        :param cert: client side certificate
        """
        logging.info("%s %s", method.upper(), url)
        if auth:
            headers = auth.apply(headers or {})
        if params:
            url = f"{url}?{urlencode(params)}"
        return self._request(
            method, url, data, json, headers=headers, cert=cert
        )
