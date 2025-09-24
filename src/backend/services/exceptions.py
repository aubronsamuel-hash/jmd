from __future__ import annotations


class DomainError(Exception):
    """Base exception for domain services."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthorizationError(DomainError):
    """Raised when the user lacks the required permission."""

    def __init__(self, message: str = "Permission denied", status_code: int = 403) -> None:
        super().__init__(message, status_code=status_code)
