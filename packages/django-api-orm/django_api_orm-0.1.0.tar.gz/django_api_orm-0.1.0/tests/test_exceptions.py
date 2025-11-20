"""Tests for exception system."""

import pytest

from django_api_orm.exceptions import (
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


class TestExceptionHierarchy:
    """Test exception inheritance and hierarchy."""

    def test_all_exceptions_inherit_from_api_exception(self) -> None:
        """All custom exceptions should inherit from APIException."""
        assert issubclass(ValidationException, APIException)
        assert issubclass(DoesNotExist, APIException)
        assert issubclass(MultipleObjectsReturned, APIException)
        assert issubclass(ConnectionError, APIException)
        assert issubclass(TimeoutError, APIException)
        assert issubclass(AuthenticationError, APIException)
        assert issubclass(RateLimitError, APIException)
        assert issubclass(HTTPStatusError, APIException)

    def test_api_exception_inherits_from_exception(self) -> None:
        """APIException should inherit from built-in Exception."""
        assert issubclass(APIException, Exception)


class TestExceptionMessages:
    """Test exception message formatting."""

    def test_api_exception_message(self) -> None:
        """Test APIException with custom message."""
        exc = APIException("Custom error message")
        assert str(exc) == "Custom error message"

    def test_validation_exception_message(self) -> None:
        """Test ValidationException with custom message."""
        exc = ValidationException("Validation failed: name is required")
        assert "Validation failed" in str(exc)

    def test_does_not_exist_message(self) -> None:
        """Test DoesNotExist with custom message."""
        exc = DoesNotExist("User with id=123 does not exist")
        assert "does not exist" in str(exc)

    def test_multiple_objects_returned_message(self) -> None:
        """Test MultipleObjectsReturned with custom message."""
        exc = MultipleObjectsReturned("Expected 1, got 5")
        assert "Expected 1, got 5" in str(exc)

    def test_connection_error_message(self) -> None:
        """Test ConnectionError with custom message."""
        exc = ConnectionError("Failed to connect to API")
        assert "Failed to connect" in str(exc)

    def test_timeout_error_message(self) -> None:
        """Test TimeoutError with custom message."""
        exc = TimeoutError("Request timed out after 30s")
        assert "timed out" in str(exc)

    def test_authentication_error_message(self) -> None:
        """Test AuthenticationError with custom message."""
        exc = AuthenticationError("Invalid token")
        assert "Invalid token" in str(exc)

    def test_rate_limit_error_message(self) -> None:
        """Test RateLimitError with custom message."""
        exc = RateLimitError("Rate limit exceeded")
        assert "Rate limit" in str(exc)

    def test_http_status_error_message(self) -> None:
        """Test HTTPStatusError with custom message."""
        exc = HTTPStatusError("500 Internal Server Error")
        assert "500" in str(exc)


class TestExceptionRaising:
    """Test raising and catching exceptions."""

    def test_raise_and_catch_does_not_exist(self) -> None:
        """Test raising and catching DoesNotExist."""
        with pytest.raises(DoesNotExist) as exc_info:
            raise DoesNotExist("Not found")
        assert "Not found" in str(exc_info.value)

    def test_catch_as_api_exception(self) -> None:
        """Test catching specific exception as APIException."""
        with pytest.raises(APIException):
            raise ValidationException("Validation failed")

    def test_catch_multiple_exceptions(self) -> None:
        """Test catching multiple exception types."""
        with pytest.raises((DoesNotExist, MultipleObjectsReturned)):
            raise DoesNotExist("Not found")

        with pytest.raises((DoesNotExist, MultipleObjectsReturned)):
            raise MultipleObjectsReturned("Multiple found")
