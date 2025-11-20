"""Django ORM-like interface for external REST APIs.

This library provides a familiar Django ORM interface for interacting with REST APIs,
with Pydantic validation and httpx for modern HTTP support (both sync and async).

Example:
    >>> from django_api_orm import ServiceClient, APIModel
    >>> from pydantic import BaseModel
    >>>
    >>> class UserSchema(BaseModel):
    ...     id: int
    ...     name: str
    ...     email: str
    >>>
    >>> class User(APIModel):
    ...     _schema_class = UserSchema
    ...     _endpoint = "/api/v1/users/"
    >>>
    >>> with ServiceClient(base_url="https://api.example.com") as client:
    ...     User.objects = Manager(User, client)
    ...     users = User.objects.filter(status="active")
    ...     for user in users:
    ...         print(user.name)
"""

from .async_base import AsyncAPIModel, AsyncManager, AsyncQuerySet, register_async_models
from .async_client import AsyncServiceClient
from .base import APIModel, Manager, QuerySet, register_models
from .client import APIResponse, ServiceClient
from .exceptions import (
    APIException,
    AuthenticationError,
    ConnectionError,
    DoesNotExist,
    HTTPStatusError,
    MultipleObjectsReturned,
    RateLimitError,
    TimeoutError,
    ValidationException,
)

__version__ = "0.1.0"

__all__ = [
    # Clients
    "ServiceClient",
    "AsyncServiceClient",
    "APIResponse",
    # Sync ORM
    "APIModel",
    "Manager",
    "QuerySet",
    "register_models",
    # Async ORM
    "AsyncAPIModel",
    "AsyncManager",
    "AsyncQuerySet",
    "register_async_models",
    # Exceptions
    "APIException",
    "ValidationException",
    "DoesNotExist",
    "MultipleObjectsReturned",
    "ConnectionError",
    "TimeoutError",
    "AuthenticationError",
    "RateLimitError",
    "HTTPStatusError",
]
