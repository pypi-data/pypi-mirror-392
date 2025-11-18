"""HTTP client for the CirtusAI backend."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional, Sequence

import requests

from .exceptions import APIError, AuthenticationError, CirtusSDKError
from .models import (
    Attachment,
    IdentityProfile,
    MailMessage,
    MessageFilters,
    UserProfile,
    parse_messages,
    _parse_datetime,
)

_DEFAULT_TIMEOUT = 10.0
_CLOCK_SKEW = timedelta(seconds=30)


class CirtusClient:
    """Synchronous client for the CirtusAI backend API."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        api_prefix: str = "/api",
        timeout: float = _DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
        auto_authenticate: bool = True,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required")
        if not api_key:
            raise ValueError("api_key is required")

        self.base_url = base_url.rstrip("/")
        self.api_prefix = api_prefix if api_prefix.startswith("/") else f"/{api_prefix}"
        self.api_key = api_key
        self.timeout = timeout
        self._session = session or requests.Session()
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._profile: Optional[UserProfile] = None
        self._identity: Optional[IdentityProfile] = None

        if auto_authenticate:
            self.authenticate()

    # ------------------------------------------------------------------ #
    # Lifecycle helpers
    # ------------------------------------------------------------------ #
    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> "CirtusClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()

    # ------------------------------------------------------------------ #
    # Authentication
    # ------------------------------------------------------------------ #
    def authenticate(self, *, force: bool = False) -> str:
        """Exchange the API key for an access token."""
        if not force and self._token and not self._token_expired():
            return self._token

        url = self._build_url("/auth/api-key/login")
        try:
            response = self._session.post(url, json={"secret": self.api_key}, timeout=self.timeout)
        except requests.RequestException as exc:  # pragma: no cover - network failure
            raise CirtusSDKError("Request failed during authentication") from exc

        if response.status_code in (401, 403):
            raise AuthenticationError("API key was rejected by the server.")

        data = self._handle_response(response)
        token = data.get("access_token")
        expires_at_raw = data.get("expires_at")
        profile_raw = data.get("user")
        if not token or not profile_raw:
            raise APIError(response.status_code, detail=data, response_text=response.text)

        self._token = token
        self._token_expiry = _parse_datetime(expires_at_raw) if isinstance(expires_at_raw, str) else None
        self._profile = UserProfile.from_dict(profile_raw)
        self._identity = None
        self._session.headers.update({"Authorization": f"Bearer {token}"})
        return token

    def _token_expired(self) -> bool:
        if not self._token or not self._token_expiry:
            return True
        now = datetime.now(timezone.utc)
        return now + _CLOCK_SKEW >= self._token_expiry

    def _ensure_authenticated(self) -> None:
        if self._token_expired():
            self.authenticate(force=True)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def get_identity(self, *, force_refresh: bool = False) -> IdentityProfile:
        """Return the identity document linked to the API key."""
        self._ensure_authenticated()
        if self._identity and not force_refresh:
            return self._identity

        payload = self._request("GET", "/identity/me")
        identity = IdentityProfile.from_dict(payload)
        self._identity = identity
        return identity

    def list_messages(
        self,
        *,
        filters: Optional[MessageFilters] = None,
        folder: str = "inbox",
        sender: Optional[str] = None,
        unread: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 30,
    ) -> list[MailMessage]:
        """Retrieve mailbox messages with optional filtering."""
        self._ensure_authenticated()
        applied_filters = filters or MessageFilters(
            folder=folder,
            sender=sender,
            unread=unread,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
        payload = self._request("GET", "/mail/messages", params=applied_filters.to_params())
        items = payload.get("items", [])
        if not isinstance(items, Iterable):
            raise APIError(500, detail="Unexpected response payload", response_text=str(payload))
        return parse_messages(items)

    def send_message(
        self,
        *,
        to: Sequence[str],
        subject: str,
        content: str,
        attachments: Optional[Sequence[Attachment]] = None,
    ) -> dict:
        """Send an email on behalf of the authenticated identity."""
        self._ensure_authenticated()
        if not to:
            raise ValueError("Parameter 'to' must contain at least one recipient.")

        payload = {
            "to": list(to),
            "subject": subject,
            "content": content,
            "attachments": [attachment.to_payload() for attachment in attachments or []],
        }
        return self._request("POST", "/mail/send", json=payload)

    def set_read_state(self, *, ids: Sequence[int], unread: bool) -> None:
        """Mark supplied message ids as read or unread."""
        self._ensure_authenticated()
        if not ids:
            raise ValueError("Parameter 'ids' must contain at least one identifier.")
        payload = {"ids": list(ids), "unread": unread}
        self._request("POST", "/mail/messages/read", json=payload, expect_json=False)

    def delete_messages(self, *, ids: Sequence[int]) -> None:
        """Delete the supplied messages."""
        self._ensure_authenticated()
        if not ids:
            raise ValueError("Parameter 'ids' must contain at least one identifier.")
        payload = {"ids": list(ids)}
        self._request("DELETE", "/mail/messages", json=payload, expect_json=False)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _build_url(self, path: str) -> str:
        path = path if path.startswith("/") else f"/{path}"
        return f"{self.base_url}{self.api_prefix}{path}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        expect_json: bool = True,
        **kwargs,
    ):
        url = self._build_url(path)
        try:
            response = self._session.request(method.upper(), url, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:  # pragma: no cover - network failure
            raise CirtusSDKError("Request failed") from exc

        if response.status_code in (401, 403):
            raise AuthenticationError("Request is not authorized.")

        if expect_json and response.status_code == 204:
            return {}
        if not response.ok:
            detail = None
            try:
                detail = response.json()
            except ValueError:
                detail = None
            raise APIError(response.status_code, detail=detail, response_text=response.text)

        if not expect_json:
            return {}
        return self._handle_response(response)

    @staticmethod
    def _handle_response(response: requests.Response):
        try:
            return response.json()
        except ValueError as exc:
            raise APIError(response.status_code, detail="Response is not valid JSON", response_text=response.text) from exc
