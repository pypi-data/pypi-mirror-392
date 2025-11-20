"""Utility functions for django-api-orm."""

from typing import Any


def build_query_params(**filters: Any) -> dict[str, str]:
    """Build query parameters from filter kwargs.

    Args:
        **filters: Key-value pairs to convert to query parameters

    Returns:
        Dictionary of query parameters with string values
    """
    params: dict[str, str] = {}
    for key, value in filters.items():
        if value is not None:
            params[key] = str(value)
    return params


def merge_dicts(*dicts: dict[str, Any] | None) -> dict[str, Any]:
    """Merge multiple dictionaries, with later dicts taking precedence.

    Args:
        *dicts: Variable number of dictionaries to merge

    Returns:
        Merged dictionary
    """
    result: dict[str, Any] = {}
    for d in dicts:
        if d is not None:
            result.update(d)
    return result


def chunk_list(items: list[Any], chunk_size: int) -> list[list[Any]]:
    """Split a list into chunks of specified size.

    Args:
        items: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunked lists
    """
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
