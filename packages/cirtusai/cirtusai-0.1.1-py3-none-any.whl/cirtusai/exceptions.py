"""SDK specific exception hierarchy."""

from __future__ import annotations

from typing import Any


class CirtusSDKError(Exception):
    """Base class for all SDK exceptions."""


class AuthenticationError(CirtusSDKError):
    """Raised when authentication with the backend fails."""


class APIError(CirtusSDKError):
    """Raised for non-successful HTTP responses."""

    def __init__(self, status_code: int, detail: Any | None = None, response_text: str | None = None) -> None:
        super().__init__(f"API request failed with status {status_code}")
        self.status_code = status_code
        self.detail = detail
        self.response_text = response_text
