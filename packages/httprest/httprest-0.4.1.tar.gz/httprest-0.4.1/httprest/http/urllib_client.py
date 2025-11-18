"""HTTP client which uses `urllib` under the hood."""

import json as _jsonlib
import urllib
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional, Union

from httprest.http import errors as _errors

from .base import HTTPClient, HTTPResponse
from .cert import ClientCertificate


class UrllibHTTPClient(HTTPClient):
    """`urllib` HTTP client."""

    # pylint: disable=too-many-arguments
    def _request(
        self,
        method: str,
        url: str,
        data: Optional[Union[dict, bytes]] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        cert: Optional[ClientCertificate] = None,
    ) -> HTTPResponse:
        headers = headers or {}

        if data is not None:
            if isinstance(data, dict):
                data = urllib.parse.urlencode(data).encode()  # type: ignore
                headers["Content-Type"] = "application/x-www-form-urlencoded"

        if json:
            headers["Content-Type"] = "application/json"
            data = _jsonlib.dumps(json).encode()

        try:
            with urllib.request.urlopen(
                urllib.request.Request(
                    url,
                    data=data,
                    headers=headers,
                    method=method.upper(),
                ),
                timeout=self._timeout.read if self._timeout else None,
            ) as response:
                return HTTPResponse(
                    response.status, response.read(), dict(response.headers)
                )
        except ConnectionError as exc:
            raise _errors.HTTPConnectionError(exc) from exc
        except TimeoutError as exc:
            raise _errors.HTTPTimeoutError(exc) from exc
        except urllib.error.HTTPError as exc:
            return HTTPResponse(
                exc.status or 500, exc.read(), dict(exc.headers)
            )
        except urllib.error.URLError as exc:
            raise _errors.HTTPRequestError(exc) from exc

    def __str__(self) -> str:
        return self.__class__.__name__
