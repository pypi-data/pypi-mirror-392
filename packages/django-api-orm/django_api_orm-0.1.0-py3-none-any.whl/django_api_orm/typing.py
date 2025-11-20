"""Type hints and protocols for django-api-orm."""

from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

# Generic type variable for model instances
T = TypeVar("T")

# Type variable bound to Pydantic BaseModel
ModelT = TypeVar("ModelT", bound=BaseModel)


class SupportsToDict(Protocol):
    """Protocol for objects that can be converted to dictionaries."""

    def to_dict(self, exclude_unset: bool = False, exclude_none: bool = False) -> dict[str, Any]:
        """Convert object to dictionary."""
        ...


# Common type aliases
JSON = dict[str, Any]
QueryParams = dict[str, str]
Headers = dict[str, str]
