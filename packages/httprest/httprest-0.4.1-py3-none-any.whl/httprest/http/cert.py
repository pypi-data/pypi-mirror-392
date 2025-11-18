"""Certificates."""

from typing import Optional


class ClientCertificate:
    """Client certificate."""

    def __init__(self, cert_path: str, key_path: Optional[str] = None) -> None:
        self.cert_path = cert_path
        self.key_path = key_path
