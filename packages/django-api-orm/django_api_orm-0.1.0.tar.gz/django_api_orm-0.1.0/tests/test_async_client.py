"""Tests for asynchronous AsyncServiceClient."""

import httpx
import pytest
import respx

from django_api_orm import (
    AsyncServiceClient,
    AuthenticationError,
    ConnectionError,
    DoesNotExist,
    HTTPStatusError,
    RateLimitError,
    TimeoutError,
)
from django_api_orm.client import APIResponse


class TestAsyncServiceClientInit:
    """Test AsyncServiceClient initialization."""

    @pytest.mark.asyncio
    async def test_init_with_base_url(self) -> None:
        """Test initialization with just base URL."""
        client = AsyncServiceClient(base_url="https://api.example.com")
        assert client.base_url == "https://api.example.com"
        await client.close()

    @pytest.mark.asyncio
    async def test_init_strips_trailing_slash(self) -> None:
        """Test that trailing slash is stripped from base URL."""
        client = AsyncServiceClient(base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com"
        await client.close()

    @pytest.mark.asyncio
    async def test_init_with_auth_token(self) -> None:
        """Test initialization with auth token."""
        client = AsyncServiceClient(base_url="https://api.example.com", auth_token="test-token")
        assert "Authorization" in client._client.headers
        assert client._client.headers["Authorization"] == "Token test-token"
        await client.close()

    @pytest.mark.asyncio
    async def test_init_with_custom_timeout(self) -> None:
        """Test initialization with custom timeout."""
        client = AsyncServiceClient(base_url="https://api.example.com", timeout=60.0)
        assert client._client.timeout.read == 60.0
        await client.close()

    @pytest.mark.asyncio
    async def test_init_with_http2(self) -> None:
        """Test initialization with HTTP/2 enabled."""
        client = AsyncServiceClient(base_url="https://api.example.com", http2=True)
        # HTTP/2 is enabled internally, but there's no simple way to test it directly
        # The client will use HTTP/2 when connecting to a server that supports it
        assert isinstance(client, AsyncServiceClient)
        await client.close()


class TestAsyncServiceClientContextManager:
    """Test AsyncServiceClient context manager."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self) -> None:
        """Test using client as async context manager."""
        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            assert isinstance(client, AsyncServiceClient)
        # Client should be closed after exiting context

    @pytest.mark.asyncio
    async def test_close_method(self) -> None:
        """Test explicit close method."""
        client = AsyncServiceClient(base_url="https://api.example.com")
        await client.close()
        # Should not raise any errors


class TestAsyncServiceClientRequests:
    """Test AsyncServiceClient HTTP requests."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_request(self) -> None:
        """Test async GET request."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(200, json={"results": [{"id": 1, "name": "John"}]})
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            response = await client.get("/api/v1/users/")

            assert isinstance(response, APIResponse)
            assert response.status_code == 200
            assert response.data == {"results": [{"id": 1, "name": "John"}]}
            assert isinstance(response.headers, dict)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_request_with_params(self) -> None:
        """Test async GET request with query parameters."""
        respx.get("https://api.example.com/api/v1/users/", params={"status": "active"}).mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            response = await client.get("/api/v1/users/", params={"status": "active"})
            assert response.status_code == 200

    @pytest.mark.asyncio
    @respx.mock
    async def test_post_request(self) -> None:
        """Test async POST request."""
        respx.post("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(201, json={"id": 1, "name": "John"})
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            response = await client.post("/api/v1/users/", data={"name": "John"})

            assert response.status_code == 201
            assert response.data["name"] == "John"

    @pytest.mark.asyncio
    @respx.mock
    async def test_patch_request(self) -> None:
        """Test async PATCH request."""
        respx.patch("https://api.example.com/api/v1/users/1/").mock(
            return_value=httpx.Response(200, json={"id": 1, "name": "Jane"})
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            response = await client.patch("/api/v1/users/1/", data={"name": "Jane"})

            assert response.status_code == 200
            assert response.data["name"] == "Jane"

    @pytest.mark.asyncio
    @respx.mock
    async def test_put_request(self) -> None:
        """Test async PUT request."""
        respx.put("https://api.example.com/api/v1/users/1/").mock(
            return_value=httpx.Response(
                200, json={"id": 1, "name": "Jane", "email": "jane@example.com"}
            )
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            response = await client.put(
                "/api/v1/users/1/", data={"name": "Jane", "email": "jane@example.com"}
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    @respx.mock
    async def test_delete_request(self) -> None:
        """Test async DELETE request."""
        respx.delete("https://api.example.com/api/v1/users/1/").mock(
            return_value=httpx.Response(204)
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            response = await client.delete("/api/v1/users/1/")

            assert response.status_code == 204


class TestAsyncServiceClientErrorHandling:
    """Test AsyncServiceClient error handling."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_404_raises_does_not_exist(self) -> None:
        """Test that 404 raises DoesNotExist."""
        respx.get("https://api.example.com/api/v1/users/999/").mock(
            return_value=httpx.Response(404)
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            with pytest.raises(DoesNotExist) as exc_info:
                await client.get("/api/v1/users/999/")
            assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    @respx.mock
    async def test_401_raises_authentication_error(self) -> None:
        """Test that 401 raises AuthenticationError."""
        respx.get("https://api.example.com/api/v1/users/").mock(return_value=httpx.Response(401))

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            with pytest.raises(AuthenticationError):
                await client.get("/api/v1/users/")

    @pytest.mark.asyncio
    @respx.mock
    async def test_429_raises_rate_limit_error(self) -> None:
        """Test that 429 raises RateLimitError."""
        respx.get("https://api.example.com/api/v1/users/").mock(return_value=httpx.Response(429))

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            with pytest.raises(RateLimitError):
                await client.get("/api/v1/users/")

    @pytest.mark.asyncio
    @respx.mock
    async def test_500_raises_http_status_error(self) -> None:
        """Test that 500 raises HTTPStatusError."""
        respx.get("https://api.example.com/api/v1/users/").mock(return_value=httpx.Response(500))

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            with pytest.raises(HTTPStatusError):
                await client.get("/api/v1/users/")

    @pytest.mark.asyncio
    @respx.mock
    async def test_timeout_raises_timeout_error(self) -> None:
        """Test that timeout raises TimeoutError."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            side_effect=httpx.TimeoutException("Request timeout")
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            with pytest.raises(TimeoutError):
                await client.get("/api/v1/users/")

    @pytest.mark.asyncio
    @respx.mock
    async def test_connection_error_raises_connection_error(self) -> None:
        """Test that connection error raises ConnectionError."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            side_effect=httpx.ConnectError("Connection failed")
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            with pytest.raises(ConnectionError):
                await client.get("/api/v1/users/")


class TestAsyncServiceClientAuthentication:
    """Test AsyncServiceClient authentication."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_auth_token_in_headers(self) -> None:
        """Test that auth token is included in request headers."""
        route = respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        async with AsyncServiceClient(
            base_url="https://api.example.com", auth_token="test-token-123"
        ) as client:
            await client.get("/api/v1/users/")

            # Check that the request was made with the auth header
            assert route.called
            request = route.calls.last.request
            assert request.headers["Authorization"] == "Token test-token-123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_no_auth_token(self) -> None:
        """Test requests without auth token."""
        route = respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            await client.get("/api/v1/users/")

            # Check that no Authorization header is present
            request = route.calls.last.request
            assert (
                "Authorization" not in request.headers or request.headers.get("Authorization") == ""
            )


class TestAsyncServiceClientConcurrency:
    """Test AsyncServiceClient concurrent requests."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_concurrent_requests(self) -> None:
        """Test making multiple concurrent requests."""
        import asyncio

        respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(200, json={"results": []})
        )
        respx.get("https://api.example.com/api/v1/posts/").mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            users_response, posts_response = await asyncio.gather(
                client.get("/api/v1/users/"), client.get("/api/v1/posts/")
            )

            assert users_response.status_code == 200
            assert posts_response.status_code == 200
