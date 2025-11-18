"""HTTP auth."""

import base64
from abc import ABC, abstractmethod


class BaseAuth(ABC):
    """Auth."""

    def apply(self, headers: dict) -> dict:
        """Apply auth headers."""
        headers["Authorization"] = self._get_auth_header()
        return headers

    @abstractmethod
    def _get_auth_header(self) -> str:
        """Get auth header."""


class BasicAuth(BaseAuth):
    """HTTP basic auth."""

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

    def _get_auth_header(self) -> str:
        credentials = base64.b64encode(
            f"{self.username}:{self.password}".encode("utf-8")
        ).decode("utf-8")
        return f"Basic {credentials}"
