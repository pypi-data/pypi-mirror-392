# CirtusAI Python SDK

`CirtusAI` provides a lightweight Python wrapper around the CirtusAI backend API. It enables:

- Exchanging API keys for access tokens;
- Reading the identity linked to an API key;
- Filtering mailbox content (folder, sender, unread flag, date range);
- Sending messages with optional Base64 attachments;
- Consistent error handling and session management.

> **Prerequisite:** the backend must expose `/api/auth/api-key/login` and allow JWT access to mail endpoints.

## Installation

```bash
pip install cirtusai
```

For local development inside this repository:

```bash
pip install -e ./sdk
```

## Quick Start

```python
from datetime import datetime, timedelta, timezone
from cirtusai import CirtusClient

client = CirtusClient(
    base_url="https://api.cirtusai.com",
    api_key="cai_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
)

# Read identity information
identity = client.get_identity()
print(identity.id, identity.credentials.signature_key)
for asset in identity.assets:
    print(asset.type, asset.address)

# Fetch unread messages from the past week
now = datetime.now(timezone.utc)
messages = client.list_messages(
    unread=True,
    start_date=now - timedelta(days=7),
)
for msg in messages:
    print(msg.subject, msg.created_at)

# Send a message
client.send_message(
    to=["teammate@example.com"],
    subject="Weekly summary",
    content="Please see attached report.",
)
```

> **Production vs local:** Use `https://api.cirtusai.com` for production traffic. During development you can point `base_url` at your sandbox instance (for example `http://127.0.0.1:8000`) and keep the defaults for `api_prefix` (`/api`) and timeouts.

## Configuration

`CirtusClient` accepts a few optional parameters for advanced scenarios:

- `api_prefix`: change the API namespace if your deployment serves the backend under a different path.
- `timeout`: override the default 10s request timeout.
- `session`: supply a pre-configured `requests.Session` (proxy settings, retries, etc.).
- `auto_authenticate`: set to `False` when you need to defer authentication and call `authenticate()` manually.

Every public method ensures a valid token is present and will automatically re-authenticate if the server indicates expiration.

## Filtering Mail

`list_messages` supports inline keyword arguments or an explicit `MessageFilters` object if you prefer strong typing:

```python
from datetime import datetime, timezone
from cirtusai import CirtusClient, MessageFilters

client = CirtusClient(base_url="https://api.cirtusai.com", api_key="cai_...")

last_week = datetime.now(timezone.utc) - timedelta(days=7)
filters = MessageFilters(folder="inbox", unread=True, start_date=last_week, limit=50)

messages = client.list_messages(filters=filters)
```

You can mix and match: passing `folder`, `sender`, `unread`, `start_date`, `end_date`, or `limit` directly to `list_messages` will automatically build the same filter payload.

## Attachments

Attach Base64 encoded content along with file metadata. You can optionally supply `content_type` to hint MIME information to downstream systems:

```python
import base64
from cirtusai import Attachment, CirtusClient

client = CirtusClient(base_url="https://api.cirtusai.com", api_key="cai_...")
content = base64.b64encode(b"example").decode()
attachment = Attachment(
    filename="demo.txt",
    content=content,
    size=len(content),
    content_type="text/plain",
)

client.send_message(
    to=["recipient@example.com"],
    subject="Demo",
    content="Sample with attachment",
    attachments=[attachment],
)
```

## Read State & Cleanup

The client exposes helpers for day-to-day mailbox maintenance:

```python
client.set_read_state(ids=[101, 102], unread=False)
client.delete_messages(ids=[203, 204])
```

Both methods accept any iterable of numeric message IDs and raise if you accidentally pass an empty list so you do not trigger no-op API calls.

## Error Handling

The SDK raises a small hierarchy of exceptions:

- `AuthenticationError`: API key invalid or session expired;
- `APIError`: non-2xx responses with structured error details;
- `CirtusSDKError`: networking or client side failures.

```python
from cirtusai import AuthenticationError, APIError

try:
    client.list_messages()
except AuthenticationError:
    client.authenticate(force=True)
except APIError as exc:
    print("Request failed", exc.status_code, exc.detail)
```

## Tests

```bash
pytest
```

Tests rely on `unittest.mock` to stub HTTP behaviour and can run in CI without network access.

## Contributing

1. Fork and clone the repository;
2. Install dependencies: `pip install -e ./sdk[dev]`;
3. Ensure `pytest` passes before submitting pull requests.
