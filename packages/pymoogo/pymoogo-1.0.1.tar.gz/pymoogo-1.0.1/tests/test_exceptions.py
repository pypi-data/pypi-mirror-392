"""Tests for pymoogo exception classes."""

import pytest

from pymoogo.exceptions import (
    MoogoAPIError,
    MoogoAuthError,
    MoogoDeviceError,
    MoogoRateLimitError,
)


def test_moogo_api_error() -> None:
    """Test MoogoAPIError base exception."""
    error = MoogoAPIError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_moogo_auth_error() -> None:
    """Test MoogoAuthError inherits from MoogoAPIError."""
    error = MoogoAuthError("Authentication failed")
    assert str(error) == "Authentication failed"
    assert isinstance(error, MoogoAPIError)
    assert isinstance(error, Exception)


def test_moogo_device_error() -> None:
    """Test MoogoDeviceError inherits from MoogoAPIError."""
    error = MoogoDeviceError("Device offline")
    assert str(error) == "Device offline"
    assert isinstance(error, MoogoAPIError)
    assert isinstance(error, Exception)


def test_moogo_rate_limit_error() -> None:
    """Test MoogoRateLimitError inherits from MoogoAPIError."""
    error = MoogoRateLimitError("Rate limited")
    assert str(error) == "Rate limited"
    assert isinstance(error, MoogoAPIError)
    assert isinstance(error, Exception)


def test_exception_hierarchy() -> None:
    """Test exception hierarchy relationships."""
    # All specific errors should inherit from MoogoAPIError
    assert issubclass(MoogoAuthError, MoogoAPIError)
    assert issubclass(MoogoDeviceError, MoogoAPIError)
    assert issubclass(MoogoRateLimitError, MoogoAPIError)

    # All should ultimately inherit from Exception
    assert issubclass(MoogoAPIError, Exception)
    assert issubclass(MoogoAuthError, Exception)
    assert issubclass(MoogoDeviceError, Exception)
    assert issubclass(MoogoRateLimitError, Exception)


def test_exception_with_context() -> None:
    """Test exceptions can be raised with context."""
    try:
        raise ValueError("Original error")
    except ValueError as e:
        with pytest.raises(MoogoAPIError) as exc_info:
            raise MoogoAPIError("Wrapped error") from e

        assert str(exc_info.value) == "Wrapped error"
        assert exc_info.value.__cause__ is e
