"""Tests for synchronous ServiceClient."""

import httpx
import pytest
import respx

from django_api_orm import (
    AuthenticationError,
    ConnectionError,
    DoesNotExist,
    HTTPStatusError,
    RateLimitError,
    ServiceClient,
    TimeoutError,
)
from django_api_orm.client import APIResponse


class TestServiceClientInit:
    """Test ServiceClient initialization."""

    def test_init_with_base_url(self) -> None:
        """Test initialization with just base URL."""
        client = ServiceClient(base_url="https://api.example.com")
        assert client.base_url == "https://api.example.com"
        client.close()

    def test_init_strips_trailing_slash(self) -> None:
        """Test that trailing slash is stripped from base URL."""
        client = ServiceClient(base_url="https://api.example.com/")
        assert client.base_url == "https://api.example.com"
        client.close()

    def test_init_with_auth_token(self) -> None:
        """Test initialization with auth token."""
        client = ServiceClient(base_url="https://api.example.com", auth_token="test-token")
        assert "Authorization" in client._client.headers
        assert client._client.headers["Authorization"] == "Token test-token"
        client.close()

    def test_init_with_custom_timeout(self) -> None:
        """Test initialization with custom timeout."""
        client = ServiceClient(base_url="https://api.example.com", timeout=60.0)
        assert client._client.timeout.read == 60.0
        client.close()


class TestServiceClientContextManager:
    """Test ServiceClient context manager."""

    def test_context_manager(self) -> None:
        """Test using client as context manager."""
        with ServiceClient(base_url="https://api.example.com") as client:
            assert isinstance(client, ServiceClient)
        # Client should be closed after exiting context

    def test_close_method(self) -> None:
        """Test explicit close method."""
        client = ServiceClient(base_url="https://api.example.com")
        client.close()
        # Should not raise any errors


class TestServiceClientRequests:
    """Test ServiceClient HTTP requests."""

    @respx.mock
    def test_get_request(self) -> None:
        """Test GET request."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(200, json={"results": [{"id": 1, "name": "John"}]})
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            response = client.get("/api/v1/users/")

            assert isinstance(response, APIResponse)
            assert response.status_code == 200
            assert response.data == {"results": [{"id": 1, "name": "John"}]}
            assert isinstance(response.headers, dict)

    @respx.mock
    def test_get_request_with_params(self) -> None:
        """Test GET request with query parameters."""
        respx.get("https://api.example.com/api/v1/users/", params={"status": "active"}).mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            response = client.get("/api/v1/users/", params={"status": "active"})
            assert response.status_code == 200

    @respx.mock
    def test_post_request(self) -> None:
        """Test POST request."""
        respx.post("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(201, json={"id": 1, "name": "John"})
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            response = client.post("/api/v1/users/", data={"name": "John"})

            assert response.status_code == 201
            assert response.data["name"] == "John"

    @respx.mock
    def test_patch_request(self) -> None:
        """Test PATCH request."""
        respx.patch("https://api.example.com/api/v1/users/1/").mock(
            return_value=httpx.Response(200, json={"id": 1, "name": "Jane"})
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            response = client.patch("/api/v1/users/1/", data={"name": "Jane"})

            assert response.status_code == 200
            assert response.data["name"] == "Jane"

    @respx.mock
    def test_put_request(self) -> None:
        """Test PUT request."""
        respx.put("https://api.example.com/api/v1/users/1/").mock(
            return_value=httpx.Response(
                200, json={"id": 1, "name": "Jane", "email": "jane@example.com"}
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            response = client.put(
                "/api/v1/users/1/", data={"name": "Jane", "email": "jane@example.com"}
            )

            assert response.status_code == 200

    @respx.mock
    def test_delete_request(self) -> None:
        """Test DELETE request."""
        respx.delete("https://api.example.com/api/v1/users/1/").mock(
            return_value=httpx.Response(204)
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            response = client.delete("/api/v1/users/1/")

            assert response.status_code == 204


class TestServiceClientErrorHandling:
    """Test ServiceClient error handling."""

    @respx.mock
    def test_404_raises_does_not_exist(self) -> None:
        """Test that 404 raises DoesNotExist."""
        respx.get("https://api.example.com/api/v1/users/999/").mock(
            return_value=httpx.Response(404)
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            with pytest.raises(DoesNotExist) as exc_info:
                client.get("/api/v1/users/999/")
            assert "not found" in str(exc_info.value).lower()

    @respx.mock
    def test_401_raises_authentication_error(self) -> None:
        """Test that 401 raises AuthenticationError."""
        respx.get("https://api.example.com/api/v1/users/").mock(return_value=httpx.Response(401))

        with ServiceClient(base_url="https://api.example.com") as client:
            with pytest.raises(AuthenticationError):
                client.get("/api/v1/users/")

    @respx.mock
    def test_429_raises_rate_limit_error(self) -> None:
        """Test that 429 raises RateLimitError."""
        respx.get("https://api.example.com/api/v1/users/").mock(return_value=httpx.Response(429))

        with ServiceClient(base_url="https://api.example.com") as client:
            with pytest.raises(RateLimitError):
                client.get("/api/v1/users/")

    @respx.mock
    def test_500_raises_http_status_error(self) -> None:
        """Test that 500 raises HTTPStatusError."""
        respx.get("https://api.example.com/api/v1/users/").mock(return_value=httpx.Response(500))

        with ServiceClient(base_url="https://api.example.com") as client:
            with pytest.raises(HTTPStatusError):
                client.get("/api/v1/users/")

    @respx.mock
    def test_timeout_raises_timeout_error(self) -> None:
        """Test that timeout raises TimeoutError."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            side_effect=httpx.TimeoutException("Request timeout")
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            with pytest.raises(TimeoutError):
                client.get("/api/v1/users/")

    @respx.mock
    def test_connection_error_raises_connection_error(self) -> None:
        """Test that connection error raises ConnectionError."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            side_effect=httpx.ConnectError("Connection failed")
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            with pytest.raises(ConnectionError):
                client.get("/api/v1/users/")


class TestServiceClientAuthentication:
    """Test ServiceClient authentication."""

    @respx.mock
    def test_auth_token_in_headers(self) -> None:
        """Test that auth token is included in request headers."""
        route = respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        with ServiceClient(
            base_url="https://api.example.com", auth_token="test-token-123"
        ) as client:
            client.get("/api/v1/users/")

            # Check that the request was made with the auth header
            assert route.called
            request = route.calls.last.request
            assert request.headers["Authorization"] == "Token test-token-123"

    @respx.mock
    def test_no_auth_token(self) -> None:
        """Test requests without auth token."""
        route = respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            client.get("/api/v1/users/")

            # Check that no Authorization header is present
            request = route.calls.last.request
            assert (
                "Authorization" not in request.headers or request.headers.get("Authorization") == ""
            )
