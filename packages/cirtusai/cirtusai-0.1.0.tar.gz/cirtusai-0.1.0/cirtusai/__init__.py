"""Public interface for the CirtusAI Python SDK."""

from .client import CirtusClient
from .exceptions import APIError, AuthenticationError, CirtusSDKError
from .models import Attachment, IdentityProfile, MailMessage, MessageFilters, UserProfile

__all__ = [
    "CirtusClient",
    "CirtusSDKError",
    "AuthenticationError",
    "APIError",
    "Attachment",
    "IdentityProfile",
    "MailMessage",
    "MessageFilters",
    "UserProfile",
]
