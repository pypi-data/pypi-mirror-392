"""Asynchronous HTTP client for django-api-orm using httpx."""

from typing import Any

import httpx

from .client import APIResponse
from .exceptions import (
    APIException,
    AuthenticationError,
    ConnectionError,
    DoesNotExist,
    HTTPStatusError,
    RateLimitError,
    TimeoutError,
)


class AsyncServiceClient:
    """Asynchronous HTTP client using httpx.

    This client provides async/await interface for making HTTP requests to REST APIs
    with automatic error handling, authentication, connection pooling, and optional HTTP/2 support.

    Args:
        base_url: Base URL for the API
        auth_token: Optional authentication token
        timeout: Request timeout in seconds (default: 30.0)
        verify_ssl: Whether to verify SSL certificates (default: True)
        follow_redirects: Whether to follow redirects (default: True)
        max_retries: Maximum number of retries for failed requests (default: 3)
        http2: Enable HTTP/2 support (default: False)

    Example:
        >>> async with AsyncServiceClient(base_url="https://api.example.com") as client:
        ...     response = await client.get("/api/v1/users/")
        ...     print(response.data)
    """

    def __init__(
        self,
        base_url: str,
        auth_token: str | None = None,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        follow_redirects: bool = True,
        max_retries: int = 3,
        http2: bool = False,
    ) -> None:
        """Initialize the async service client."""
        self.base_url = base_url.rstrip("/")

        # Build headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if auth_token:
            headers["Authorization"] = f"Token {auth_token}"

        # Configure httpx async client
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=httpx.Timeout(timeout),
            verify=verify_ssl,
            follow_redirects=follow_redirects,
            transport=httpx.AsyncHTTPTransport(retries=max_retries),
            http2=http2,
        )

    async def __aenter__(self) -> "AsyncServiceClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the client and release connections."""
        await self._client.aclose()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> APIResponse:
        """Make async HTTP request using httpx.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            **kwargs: Additional arguments to pass to httpx

        Returns:
            APIResponse with data, status code, and headers

        Raises:
            DoesNotExist: If resource not found (404)
            AuthenticationError: If authentication fails (401)
            RateLimitError: If rate limit exceeded (429)
            HTTPStatusError: For other HTTP errors
            TimeoutError: If request times out
            ConnectionError: If connection fails
            APIException: For other errors
        """
        try:
            response = await self._client.request(
                method=method, url=endpoint, params=params, json=data, **kwargs
            )

            response.raise_for_status()

            return APIResponse(
                data=response.json() if response.content else {},
                status_code=response.status_code,
                headers=dict(response.headers),
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise DoesNotExist(f"Resource not found: {endpoint}") from e
            elif e.response.status_code == 401:
                raise AuthenticationError(f"Authentication failed: {e}") from e
            elif e.response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded: {e}") from e
            else:
                raise HTTPStatusError(f"HTTP error: {e}") from e

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timeout: {e}") from e

        except httpx.ConnectError as e:
            raise ConnectionError(f"Connection failed: {e}") from e

        except Exception as e:
            raise APIException(f"Request failed: {e}") from e

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> APIResponse:
        """Make an async GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            APIResponse with data, status code, and headers
        """
        return await self._make_request("GET", endpoint, params=params)

    async def post(self, endpoint: str, data: dict[str, Any] | None = None) -> APIResponse:
        """Make an async POST request.

        Args:
            endpoint: API endpoint path
            data: Request body data

        Returns:
            APIResponse with data, status code, and headers
        """
        return await self._make_request("POST", endpoint, data=data)

    async def patch(self, endpoint: str, data: dict[str, Any] | None = None) -> APIResponse:
        """Make an async PATCH request.

        Args:
            endpoint: API endpoint path
            data: Request body data

        Returns:
            APIResponse with data, status code, and headers
        """
        return await self._make_request("PATCH", endpoint, data=data)

    async def put(self, endpoint: str, data: dict[str, Any] | None = None) -> APIResponse:
        """Make an async PUT request.

        Args:
            endpoint: API endpoint path
            data: Request body data

        Returns:
            APIResponse with data, status code, and headers
        """
        return await self._make_request("PUT", endpoint, data=data)

    async def delete(self, endpoint: str) -> APIResponse:
        """Make an async DELETE request.

        Args:
            endpoint: API endpoint path

        Returns:
            APIResponse with data, status code, and headers
        """
        return await self._make_request("DELETE", endpoint)
