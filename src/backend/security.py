from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from .config import Settings


def hash_password(password: str, *, salt: str | None = None) -> str:
    """Hash a password using SHA-256 with a random salt."""

    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify that a password matches the stored hash."""

    try:
        salt, digest = hashed.split("$", 1)
    except ValueError:
        return False
    candidate = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return hmac.compare_digest(candidate, digest)


def generate_token(length: int = 32) -> str:
    """Generate a secure random token."""

    return secrets.token_urlsafe(length)


def now_utc() -> datetime:
    """Return the current UTC datetime without timezone information."""

    return datetime.now(timezone.utc).replace(tzinfo=None)


def expiration(ttl_seconds: int) -> datetime:
    """Return an expiration timestamp relative to now."""

    return now_utc() + timedelta(seconds=ttl_seconds)


def session_expiration(settings: Settings) -> datetime:
    """Return the default session expiration using configuration."""

    return expiration(settings.access_token_ttl_seconds)


def magic_link_expiration(settings: Settings) -> datetime:
    """Return the default magic link expiration using configuration."""

    return expiration(settings.magic_link_ttl_seconds)


def invitation_expiration(settings: Settings) -> datetime:
    """Return the default invitation expiration using configuration."""

    return expiration(settings.invitation_ttl_seconds)
