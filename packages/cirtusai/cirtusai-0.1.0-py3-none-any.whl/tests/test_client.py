from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
import requests

from cirtusai import Attachment, AuthenticationError, CirtusClient


def _mock_response(*, status_code: int = 200, json_data: Any | None = None) -> MagicMock:
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.ok = status_code < 400
    response.text = "mock-response"
    response.json.return_value = json_data
    return response


def _mock_session() -> MagicMock:
    session = MagicMock(spec=requests.Session)
    session.headers = {}
    return session


def _auth_payload() -> dict:
    return {
        "access_token": "token123",
        "expires_at": "2030-01-01T00:00:00+00:00",
        "user": {
            "id": "user-1",
            "agent_name": "agent",
            "display_name": "Agent",
            "mail_address": "agent@example.com",
            "email": "agent@example.com",
            "email_verified": True,
            "email_bound_at": "2024-01-01T00:00:00+00:00",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-01T00:00:00+00:00",
        },
    }


def _identity_payload() -> dict:
    return {
        "id": "cirtus:user-1",
        "name": "Agent",
        "type": "personal",
        "status": "active",
        "create_time": "2024-01-01T00:00:00+00:00",
        "last_active_at": "2024-01-02T00:00:00+00:00",
        "creator": {
            "id": "org:cirtus",
            "name": "Cirtus",
            "auth_provider": "Cirtus",
        },
        "assets": [
            {
                "id": "asset:mail:agent",
                "address": "agent@example.com",
                "type": "mail",
                "status": "connected",
                "scopes": ["read", "send"],
            }
        ],
        "linked_platforms": [
            {
                "name": "Cirtus Mail Bridge",
                "connection_status": "connected",
                "connection_type": "oauth2",
            }
        ],
        "credentials": {
            "issuer": "Cirtus",
            "signature_key": "ed25519:1234abcd",
            "access_token": "cai_token",
            "expires_at": "2024-02-01T00:00:00+00:00",
        },
        "metadata": {"description": "Agent identity", "tags": ["agent"]},
    }


def test_authenticate_populates_profile_and_token() -> None:
    session = _mock_session()
    session.post.return_value = _mock_response(json_data=_auth_payload())
    session.request.return_value = _mock_response(json_data=_identity_payload())

    client = CirtusClient(
        base_url="http://testserver",
        api_key="cai_example_key",
        session=session,
        auto_authenticate=False,
    )

    token = client.authenticate()
    assert token == "token123"
    profile = client.get_identity()
    assert profile.name == "Agent"
    assert profile.assets[0].address == "agent@example.com"
    assert session.headers["Authorization"] == "Bearer token123"


def test_list_messages_returns_typed_objects() -> None:
    session = _mock_session()
    session.post.return_value = _mock_response(json_data=_auth_payload())
    session.request.return_value = _mock_response(
        json_data={
            "items": [
                {
                    "id": 1,
                    "folder": "inbox",
                    "subject": "Hello",
                    "sender": "sender@example.com",
                    "recipient": "agent@example.com",
                    "preview": "Body",
                    "created_at": "2025-01-01T00:00:00+00:00",
                    "unread": True,
                }
            ]
        }
    )

    client = CirtusClient(
        base_url="http://testserver",
        api_key="cai_example_key",
        session=session,
    )

    messages = client.list_messages(unread=True, limit=10)
    assert len(messages) == 1
    assert messages[0].subject == "Hello"
    session.request.assert_called_with(
        "GET",
        "http://testserver/api/mail/messages",
        timeout=10.0,
        params={"folder": "inbox", "limit": "10", "unread": "true"},
    )


def test_send_message_serialises_attachments() -> None:
    session = _mock_session()
    session.post.return_value = _mock_response(json_data=_auth_payload())
    session.request.return_value = _mock_response(json_data={"message": "Message queued for delivery."})

    client = CirtusClient(
        base_url="http://testserver",
        api_key="cai_example_key",
        session=session,
    )

    attachment = Attachment(filename="demo.txt", content="YmFzZTY0", size=6, content_type="text/plain")
    client.send_message(
        to=["dest@example.com"],
        subject="Greetings",
        content="Body",
        attachments=[attachment],
    )
    session.request.assert_called_with(
        "POST",
        "http://testserver/api/mail/send",
        timeout=10.0,
        json={
            "to": ["dest@example.com"],
            "subject": "Greetings",
            "content": "Body",
            "attachments": [
                {"filename": "demo.txt", "content": "YmFzZTY0", "size": 6, "content_type": "text/plain"}
            ],
        },
    )


def test_request_raises_authentication_error_on_401() -> None:
    session = _mock_session()
    session.post.return_value = _mock_response(json_data=_auth_payload())
    session.request.return_value = _mock_response(status_code=401, json_data={"detail": "invalid"})

    client = CirtusClient(
        base_url="http://testserver",
        api_key="cai_example_key",
        session=session,
    )

    with pytest.raises(AuthenticationError):
        client.list_messages()
