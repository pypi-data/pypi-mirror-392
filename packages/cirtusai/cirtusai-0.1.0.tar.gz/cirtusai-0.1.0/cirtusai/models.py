"""Data models used by the CirtusAI SDK."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Optional


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Convert ISO-like strings to timezone-aware datetime objects."""
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


@dataclass(slots=True)
class UserProfile:
    """Serializable representation of the authenticated user."""

    id: str
    agent_name: str
    display_name: Optional[str]
    mail_address: Optional[str]
    email: Optional[str]
    email_verified: bool
    email_bound_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        return cls(
            id=data["id"],
            agent_name=data["agent_name"],
            display_name=data.get("display_name"),
            mail_address=data.get("mail_address"),
            email=data.get("email"),
            email_verified=bool(data.get("email_verified")),
            email_bound_at=_parse_datetime(data.get("email_bound_at")),
            is_active=bool(data.get("is_active")),
            created_at=_parse_datetime(data.get("created_at")) or datetime.fromtimestamp(0, tz=timezone.utc),
            updated_at=_parse_datetime(data.get("updated_at")) or datetime.fromtimestamp(0, tz=timezone.utc),
        )


@dataclass(slots=True)
class IdentityCreator:
    """Issuer information for an identity."""

    id: str
    name: str
    auth_provider: str


@dataclass(slots=True)
class IdentityAsset:
    """Asset bound to the identity."""

    id: str
    address: str
    type: str
    status: str
    scopes: list[str]


@dataclass(slots=True)
class IdentityLinkedPlatform:
    """External platform link metadata."""

    name: str
    connection_status: str
    connection_type: str


@dataclass(slots=True)
class IdentityCredentials:
    """Credential metadata describing issuer signatures."""

    issuer: str
    signature_key: str
    access_token: Optional[str]
    expires_at: Optional[datetime]


@dataclass(slots=True)
class IdentityMetadata:
    """Free-form metadata describing the identity."""

    description: Optional[str]
    tags: list[str]


@dataclass(slots=True)
class IdentityProfile:
    """Structured representation of the agent identity document."""

    id: str
    name: str
    type: str
    status: str
    create_time: datetime
    last_active_at: Optional[datetime]
    creator: IdentityCreator
    assets: list[IdentityAsset]
    linked_platforms: list[IdentityLinkedPlatform]
    credentials: IdentityCredentials
    metadata: IdentityMetadata

    @classmethod
    def from_dict(cls, data: dict) -> "IdentityProfile":
        creator_raw = data.get("creator") or {}
        assets_raw = data.get("assets") or []
        linked_raw = data.get("linked_platforms") or []
        credentials_raw = data.get("credentials") or {}
        metadata_raw = data.get("metadata") or {}

        assets = [
            IdentityAsset(
                id=asset.get("id") or "",
                address=asset.get("address") or "",
                type=asset.get("type") or "",
                status=asset.get("status") or "",
                scopes=list(asset.get("scopes") or []),
            )
            for asset in assets_raw
        ]
        linked = [
            IdentityLinkedPlatform(
                name=item.get("name") or "",
                connection_status=item.get("connection_status") or "",
                connection_type=item.get("connection_type") or "",
            )
            for item in linked_raw
        ]

        return cls(
            id=data.get("id") or "",
            name=data.get("name") or "",
            type=data.get("type") or "personal",
            status=data.get("status") or "active",
            create_time=_parse_datetime(data.get("create_time"))
            or datetime.fromtimestamp(0, tz=timezone.utc),
            last_active_at=_parse_datetime(data.get("last_active_at")),
            creator=IdentityCreator(
                id=creator_raw.get("id") or "",
                name=creator_raw.get("name") or "",
                auth_provider=creator_raw.get("auth_provider") or "",
            ),
            assets=assets,
            linked_platforms=linked,
            credentials=IdentityCredentials(
                issuer=credentials_raw.get("issuer") or "",
                signature_key=credentials_raw.get("signature_key") or "",
                access_token=credentials_raw.get("access_token"),
                expires_at=_parse_datetime(credentials_raw.get("expires_at")),
            ),
            metadata=IdentityMetadata(
                description=metadata_raw.get("description"),
                tags=list(metadata_raw.get("tags") or []),
            ),
        )


@dataclass(slots=True)
class Attachment:
    """Attachment metadata for outbound messages."""

    filename: str
    content: str
    size: int
    content_type: Optional[str] = None

    def to_payload(self) -> dict:
        payload = {
            "filename": self.filename,
            "content": self.content,
            "size": self.size,
        }
        if self.content_type:
            payload["content_type"] = self.content_type
        return payload


@dataclass(slots=True)
class MailMessage:
    """Structured mail message returned by the API."""

    id: int
    folder: str
    subject: str
    sender: str
    recipient: str
    preview: Optional[str]
    created_at: Optional[datetime]
    unread: bool

    @classmethod
    def from_dict(cls, data: dict) -> "MailMessage":
        return cls(
            id=int(data["id"]),
            folder=data.get("folder", "inbox"),
            subject=data.get("subject") or "",
            sender=data.get("sender") or "",
            recipient=data.get("recipient") or "",
            preview=data.get("preview"),
            created_at=_parse_datetime(data.get("created_at")),
            unread=bool(data.get("unread", True)),
        )


@dataclass(slots=True)
class MessageFilters:
    """Convenience container used when fetching messages."""

    folder: str = "inbox"
    sender: Optional[str] = None
    unread: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 30

    def to_params(self) -> dict[str, str]:
        params: dict[str, str] = {"folder": self.folder, "limit": str(self.limit)}
        if self.sender:
            params["sender"] = self.sender
        if self.unread is not None:
            params["unread"] = "true" if self.unread else "false"
        if self.start_date:
            params["start_date"] = self.start_date.isoformat()
        if self.end_date:
            params["end_date"] = self.end_date.isoformat()
        return params


def parse_messages(items: Iterable[dict]) -> list[MailMessage]:
    """Convert raw response payloads into typed message objects."""
    return [MailMessage.from_dict(item) for item in items]
