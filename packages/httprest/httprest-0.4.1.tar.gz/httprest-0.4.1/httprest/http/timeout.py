"""Timeout wrappers."""

from typing import Optional


class Timeout:
    """HTTP request timeout."""

    def __init__(
        self, connect: Optional[float] = None, read: Optional[float] = None
    ) -> None:
        """Init timeout.

        :param connect: connect timeout in seconds
        :param read: read timeout in seconds
        """
        self.connect = connect
        self.read = read
