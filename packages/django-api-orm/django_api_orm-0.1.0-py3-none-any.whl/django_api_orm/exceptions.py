"""Custom exceptions for django-api-orm.

This module defines all custom exceptions used throughout the library,
providing Django ORM-like exception handling for API interactions.
"""


class APIException(Exception):
    """Base exception for all API-related errors."""

    pass


class ValidationException(APIException):
    """Raised when Pydantic validation fails."""

    pass


class DoesNotExist(APIException):
    """Raised when a query returns no results (similar to Django's DoesNotExist)."""

    pass


class MultipleObjectsReturned(APIException):
    """Raised when a query expected one result but returned multiple."""

    pass


class ConnectionError(APIException):
    """Raised when connection to the API fails."""

    pass


class TimeoutError(APIException):
    """Raised when an API request times out."""

    pass


class AuthenticationError(APIException):
    """Raised when authentication fails (401 status)."""

    pass


class RateLimitError(APIException):
    """Raised when API rate limit is exceeded (429 status)."""

    pass


class HTTPStatusError(APIException):
    """Raised when an HTTP request returns an error status code.

    This wraps httpx.HTTPStatusError to provide a consistent exception interface.
    """

    pass
