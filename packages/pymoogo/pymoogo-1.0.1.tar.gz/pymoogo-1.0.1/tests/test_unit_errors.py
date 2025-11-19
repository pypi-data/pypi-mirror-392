"""Unit tests for error handling and retry logic."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from pymoogo import (
    MoogoAPIError,
    MoogoAuthError,
    MoogoClient,
    MoogoDeviceError,
    MoogoRateLimitError,
)
from pymoogo.client import retry_with_backoff


@pytest.mark.unit
class TestExceptions:
    """Test custom exception classes."""

    def test_moogo_api_error(self):
        """Test MoogoAPIError exception."""
        error = MoogoAPIError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_moogo_auth_error(self):
        """Test MoogoAuthError exception."""
        error = MoogoAuthError("Authentication failed")
        assert str(error) == "Authentication failed"
        assert isinstance(error, MoogoAPIError)

    def test_moogo_device_error(self):
        """Test MoogoDeviceError exception."""
        error = MoogoDeviceError("Device offline")
        assert str(error) == "Device offline"
        assert isinstance(error, MoogoAPIError)

    def test_moogo_rate_limit_error(self):
        """Test MoogoRateLimitError exception."""
        error = MoogoRateLimitError("Rate limited")
        assert str(error) == "Rate limited"
        assert isinstance(error, MoogoAPIError)


@pytest.mark.unit
@pytest.mark.asyncio
class TestRetryDecorator:
    """Test retry with backoff decorator."""

    async def test_retry_success_on_first_attempt(self):
        """Test function succeeds on first attempt."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, initial_delay=0.01)
        async def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await successful_function()
        assert result == "success"
        assert call_count == 1

    async def test_retry_success_after_failures(self):
        """Test function succeeds after some failures."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, initial_delay=0.01)
        async def eventually_successful():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise MoogoDeviceError("Temporary error")
            return "success"

        result = await eventually_successful()
        assert result == "success"
        assert call_count == 3

    async def test_retry_exhausts_attempts(self):
        """Test retry exhausts all attempts."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, initial_delay=0.01)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise MoogoDeviceError("Persistent error")

        with pytest.raises(MoogoDeviceError, match="Persistent error"):
            await always_fails()

        assert call_count == 3

    async def test_retry_respects_retry_on_parameter(self):
        """Test retry only retries specified exceptions."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, initial_delay=0.01, retry_on=(MoogoDeviceError,))
        async def wrong_exception():
            nonlocal call_count
            call_count += 1
            raise MoogoAuthError("Auth error")

        with pytest.raises(MoogoAuthError):
            await wrong_exception()

        # Should not retry for non-specified exceptions
        assert call_count == 1

    async def test_retry_does_not_retry_rate_limit(self):
        """Test retry does not retry on rate limit errors."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, initial_delay=0.01)
        async def rate_limited():
            nonlocal call_count
            call_count += 1
            raise MoogoRateLimitError("Rate limited")

        with pytest.raises(MoogoRateLimitError):
            await rate_limited()

        # Should not retry rate limit errors
        assert call_count == 1

    async def test_retry_backoff_delay_increases(self):
        """Test that retry delays increase with backoff."""
        call_times = []

        @retry_with_backoff(
            max_attempts=3,
            initial_delay=0.1,
            backoff_factor=2.0,
            jitter=False,  # Disable jitter for predictable testing
        )
        async def track_delays():
            call_times.append(asyncio.get_event_loop().time())
            if len(call_times) < 3:
                raise MoogoDeviceError("Error")
            return "success"

        await track_delays()

        # Verify delays increase (without jitter, delays should be predictable)
        assert len(call_times) == 3
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        # Second delay should be roughly 2x first delay
        assert delay2 > delay1
        assert delay1 >= 0.1  # At least initial delay
        assert delay2 >= 0.2  # At least 2x initial delay


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.skip(reason="TODO: Fix async mock setup for _request method testing")
class TestRequestErrorHandling:
    """Test _request method error handling."""

    async def test_request_handles_success_code(self, mock_credentials, mock_api_response_success):
        """Test request handles success response code."""
        client = MoogoClient(**mock_credentials)

        with patch.object(client, "_session") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_api_response_success)
            mock_session.request = AsyncMock(return_value=mock_response)
            mock_session.request.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.request.return_value.__aexit__ = AsyncMock()

            response = await client._request("GET", "v1/test")
            assert response["code"] == 0

    async def test_request_handles_auth_error_code(self, mock_credentials):
        """Test request handles authentication error code."""
        client = MoogoClient(**mock_credentials)

        error_response = {
            "code": 10104,
            "message": "Invalid credentials",
            "data": None,
        }

        with patch.object(client, "_session") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=error_response)
            mock_session.request = AsyncMock(return_value=mock_response)
            mock_session.request.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.request.return_value.__aexit__ = AsyncMock()

            with pytest.raises(MoogoAuthError, match="Invalid credentials"):
                await client._request("GET", "v1/test")

    async def test_request_handles_rate_limit_code(self, mock_credentials):
        """Test request handles rate limit error code."""
        client = MoogoClient(**mock_credentials)

        error_response = {
            "code": 10000,
            "message": "Rate limited",
            "data": None,
        }

        with patch.object(client, "_session") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=error_response)
            mock_session.request = AsyncMock(return_value=mock_response)
            mock_session.request.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.request.return_value.__aexit__ = AsyncMock()

            with pytest.raises(MoogoRateLimitError, match="Rate limited"):
                await client._request("GET", "v1/test")

    async def test_request_handles_device_offline_code(self, mock_credentials):
        """Test request handles device offline error code."""
        client = MoogoClient(**mock_credentials)

        error_response = {
            "code": 10201,
            "message": "Device offline",
            "data": None,
        }

        with patch.object(client, "_session") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=error_response)
            mock_session.request = AsyncMock(return_value=mock_response)
            mock_session.request.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.request.return_value.__aexit__ = AsyncMock()

            with pytest.raises(MoogoDeviceError, match="Device offline"):
                await client._request("GET", "v1/test")

    async def test_request_handles_http_error_status(self, mock_credentials):
        """Test request handles HTTP error status codes."""
        client = MoogoClient(**mock_credentials)

        with patch.object(client, "_session") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.reason = "Not Found"
            mock_session.request = AsyncMock(return_value=mock_response)
            mock_session.request.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_session.request.return_value.__aexit__ = AsyncMock()

            with pytest.raises(MoogoAPIError, match="HTTP 404"):
                await client._request("GET", "v1/test")


@pytest.mark.unit
@pytest.mark.asyncio
class TestAuthenticationRequired:
    """Test authentication requirement checks."""

    async def test_get_devices_requires_auth(self, mock_credentials):
        """Test get_devices raises error without authentication."""
        client = MoogoClient(**mock_credentials)

        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.get_devices()

    async def test_get_device_status_requires_auth(self, mock_credentials):
        """Test get_device_status raises error without authentication."""
        client = MoogoClient(**mock_credentials)

        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.get_device_status("device_123")

    async def test_start_spray_requires_auth(self, mock_credentials):
        """Test start_spray raises error without authentication."""
        client = MoogoClient(**mock_credentials)

        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.start_spray("device_123")

    async def test_get_device_logs_requires_auth(self, mock_credentials):
        """Test get_device_logs raises error without authentication."""
        client = MoogoClient(**mock_credentials)

        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.get_device_logs("device_123")

    async def test_enable_schedule_requires_auth(self, mock_credentials):
        """Test enable_schedule raises error without authentication."""
        client = MoogoClient(**mock_credentials)

        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.enable_schedule("device_123", "schedule_456")

    async def test_get_device_config_requires_auth(self, mock_credentials):
        """Test get_device_config raises error without authentication."""
        client = MoogoClient(**mock_credentials)

        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.get_device_config("device_123")

    async def test_check_firmware_update_requires_auth(self, mock_credentials):
        """Test check_firmware_update raises error without authentication."""
        client = MoogoClient(**mock_credentials)

        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.check_firmware_update("device_123")
