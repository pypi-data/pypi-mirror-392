"""Unit tests for MoogoClient core functionality."""

from datetime import datetime, timedelta

import pytest

from pymoogo import (
    MoogoClient,
    MoogoDeviceError,
)


@pytest.mark.unit
class TestClientInitialization:
    """Test client initialization and configuration."""

    def test_client_init_with_credentials(self, mock_credentials):
        """Test client initialization with email and password."""
        client = MoogoClient(
            email=mock_credentials["email"],
            password=mock_credentials["password"],
        )

        assert client.email == mock_credentials["email"]
        assert client.password == mock_credentials["password"]
        assert client.base_url == "https://api.moogo.com"
        assert not client.is_authenticated

    def test_client_init_without_credentials(self):
        """Test client initialization without credentials."""
        client = MoogoClient()

        assert client.email is None
        assert client.password is None
        assert not client.is_authenticated

    def test_client_init_custom_base_url(self, mock_credentials):
        """Test client initialization with custom base URL."""
        custom_url = "https://api-test.moogo.com"
        client = MoogoClient(
            email=mock_credentials["email"],
            password=mock_credentials["password"],
            base_url=custom_url,
        )

        assert client.base_url == custom_url

    def test_client_base_url_trailing_slash_removed(self, mock_credentials):
        """Test that trailing slash is removed from base URL."""
        client = MoogoClient(
            email=mock_credentials["email"],
            password=mock_credentials["password"],
            base_url="https://api.moogo.com/",
        )

        assert client.base_url == "https://api.moogo.com"


@pytest.mark.unit
class TestAuthenticationState:
    """Test authentication state management."""

    def test_is_authenticated_false_initially(self, mock_credentials):
        """Test that client is not authenticated initially."""
        client = MoogoClient(**mock_credentials)
        assert not client.is_authenticated

    def test_is_authenticated_with_valid_token(self, mock_credentials):
        """Test authentication state with valid token."""
        client = MoogoClient(**mock_credentials)
        client._token = "test_token"
        client._authenticated = True
        client._token_expires = datetime.now() + timedelta(hours=1)

        assert client.is_authenticated

    def test_is_authenticated_with_expired_token(self, mock_credentials):
        """Test authentication state with expired token."""
        client = MoogoClient(**mock_credentials)
        client._token = "test_token"
        client._authenticated = True
        client._token_expires = datetime.now() - timedelta(hours=1)

        assert not client.is_authenticated

    def test_is_authenticated_with_no_expiry(self, mock_credentials):
        """Test authentication state with no token expiry set."""
        client = MoogoClient(**mock_credentials)
        client._token = "test_token"
        client._authenticated = True
        client._token_expires = None

        assert client.is_authenticated


@pytest.mark.unit
class TestHeaders:
    """Test request header generation."""

    def test_headers_without_auth(self, mock_credentials):
        """Test headers for unauthenticated requests."""
        client = MoogoClient(**mock_credentials)
        headers = client._get_headers(authenticated=False)

        assert "token" not in headers
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert "User-Agent" in headers

    def test_headers_with_auth_and_token(self, mock_credentials):
        """Test headers for authenticated requests with token."""
        client = MoogoClient(**mock_credentials)
        client._token = "test_token_12345"
        headers = client._get_headers(authenticated=True)

        assert headers["token"] == "test_token_12345"
        assert headers["Content-Type"] == "application/json"

    def test_headers_with_auth_but_no_token(self, mock_credentials):
        """Test headers for authenticated requests without token."""
        client = MoogoClient(**mock_credentials)
        headers = client._get_headers(authenticated=True)

        assert "token" not in headers


@pytest.mark.unit
class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_circuit_breaker_initially_closed(self, mock_credentials):
        """Test that circuit breaker is closed initially."""
        client = MoogoClient(**mock_credentials)
        assert not client._is_circuit_open("device_123")

    def test_record_device_failure(self, mock_credentials):
        """Test recording device failures."""
        client = MoogoClient(**mock_credentials)
        error = MoogoDeviceError("Test error")

        client._record_device_failure("device_123", error)
        circuit = client._device_circuit_breakers["device_123"]

        assert circuit["failures"] == 1
        assert circuit["last_failure"] is not None

    def test_circuit_opens_after_threshold(self, mock_credentials):
        """Test that circuit opens after failure threshold."""
        client = MoogoClient(**mock_credentials)
        client._circuit_breaker_threshold = 3
        error = MoogoDeviceError("Test error")

        # Record failures up to threshold
        for _ in range(3):
            client._record_device_failure("device_123", error)

        assert client._is_circuit_open("device_123")

    def test_record_device_success_resets_circuit(self, mock_credentials):
        """Test that success resets circuit breaker."""
        client = MoogoClient(**mock_credentials)
        error = MoogoDeviceError("Test error")

        # Record some failures
        client._record_device_failure("device_123", error)
        client._record_device_failure("device_123", error)

        # Record success
        client._record_device_success("device_123")

        circuit = client._device_circuit_breakers["device_123"]
        assert circuit["failures"] == 0
        assert circuit["last_success"] is not None

    def test_circuit_closes_after_timeout(self, mock_credentials):
        """Test that circuit closes after timeout period."""
        client = MoogoClient(**mock_credentials)
        client._circuit_breaker_threshold = 3
        client._circuit_breaker_timeout = timedelta(seconds=1)
        error = MoogoDeviceError("Test error")

        # Open the circuit
        for _ in range(3):
            client._record_device_failure("device_123", error)

        assert client._is_circuit_open("device_123")

        # Manually set last failure to past timeout
        client._device_circuit_breakers["device_123"]["last_failure"] = datetime.now() - timedelta(
            seconds=2
        )

        # Circuit should now be closed
        assert not client._is_circuit_open("device_123")

    def test_get_device_circuit_status(self, mock_credentials):
        """Test getting circuit breaker status."""
        client = MoogoClient(**mock_credentials)

        # No circuit data
        status = client.get_device_circuit_status("device_123")
        assert not status["circuit_open"]
        assert status["failures"] == 0

        # With circuit data
        error = MoogoDeviceError("Test error")
        client._record_device_failure("device_456", error)
        status = client.get_device_circuit_status("device_456")

        assert status["failures"] == 1
        assert status["last_failure"] is not None


@pytest.mark.unit
class TestDeviceCaching:
    """Test device list caching."""

    def test_cache_initially_empty(self, mock_credentials):
        """Test that device cache is empty initially."""
        client = MoogoClient(**mock_credentials)
        assert client._devices_cache is None
        assert client._devices_cache_time is None

    def test_cache_ttl_configuration(self, mock_credentials):
        """Test cache TTL configuration."""
        client = MoogoClient(**mock_credentials)
        assert client._devices_cache_ttl == timedelta(minutes=5)


@pytest.mark.unit
class TestEndpointConfiguration:
    """Test endpoint URL configuration."""

    def test_all_endpoints_defined(self, mock_credentials):
        """Test that all required endpoints are defined."""
        client = MoogoClient(**mock_credentials)

        required_endpoints = [
            "login",
            "devices",
            "device_detail",
            "device_start",
            "device_stop",
            "device_schedules",
            "device_configs",
            "device_logs",
            "device_ota_check",
            "device_ota_update",
            "liquid_types",
        ]

        for endpoint in required_endpoints:
            assert endpoint in client.ENDPOINTS

    def test_endpoint_formatting(self, mock_credentials):
        """Test endpoint URL formatting with parameters."""
        client = MoogoClient(**mock_credentials)

        # Test device endpoint formatting
        device_endpoint = client.ENDPOINTS["device_detail"].format(device_id="test_device_123")
        assert device_endpoint == "v1/devices/test_device_123"

        # Test schedule endpoint formatting
        schedule_endpoint = client.ENDPOINTS["device_schedule_detail"].format(
            device_id="device_123", schedule_id="schedule_456"
        )
        assert schedule_endpoint == "v1/devices/device_123/schedules/schedule_456"


@pytest.mark.unit
class TestResponseCodes:
    """Test API response code constants."""

    def test_response_codes_defined(self, mock_credentials):
        """Test that response codes are properly defined."""
        client = MoogoClient(**mock_credentials)

        assert client.SUCCESS_CODE == 0
        assert client.AUTH_INVALID_CODE == 10104
        assert client.RATE_LIMITED_CODE == 10000
        assert client.DEVICE_OFFLINE_CODE == 10201
        assert client.SERVER_ERROR_CODE == 500
        assert client.UNAUTHORIZED_CODE == 401
