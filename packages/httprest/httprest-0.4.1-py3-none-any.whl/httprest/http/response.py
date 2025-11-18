"""HTTP response."""

import json as jsonlib
from typing import Optional

from .errors import HTTPClientError, HTTPInvalidResponseError, HTTPServerError


class HTTPResponse:
    """HTTP response wrapper."""

    def __init__(
        self, status_code: int, body: Optional[bytes], headers: dict
    ) -> None:
        self.status_code = status_code
        self.body = body or b""
        self.headers = headers
        self._json = None

    @property
    def ok(self) -> bool:
        """Return whether the response is successful."""
        return self.status_code >= 200 and self.status_code < 400

    def raise_for_status(self) -> None:
        """Raise exception if the response is not successful."""
        if 400 <= self.status_code < 500:
            raise HTTPClientError(self.status_code)
        if 500 <= self.status_code < 600:
            raise HTTPServerError(self.status_code)

    @property
    def json(self) -> Optional[dict]:
        """Return body as JSON."""
        if self._json is not None:
            return self._json

        headers = {key.lower(): val for key, val in self.headers.items()}
        if "application/json" in headers.get("content-type", ""):
            try:
                self._json = jsonlib.loads(self.body)
            except Exception as exc:
                raise HTTPInvalidResponseError(
                    f"Invalid JSON in response: {exc}"
                ) from exc

        return self._json

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(status={self.status_code})"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"status={self.status_code}, "
            f"body={self.body!r}, "
            f"headers={self.headers}"
            ")"
        )
