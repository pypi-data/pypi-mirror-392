"""Tests for MoogoClient device operations."""

from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from pymoogo import MoogoClient
from pymoogo.exceptions import MoogoAuthError, MoogoDeviceError
from pymoogo.models import DeviceStatus


class TestDeviceOperations:
    """Tests for device discovery and status."""

    @pytest.mark.asyncio
    async def test_get_devices_success(
        self,
        authenticated_client: MoogoClient,
        mock_devices_response: dict[str, Any],
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test getting devices successfully."""
        mock_response_cm = create_response(200, mock_devices_response)
        mock_session.request.return_value = mock_response_cm

        devices = await authenticated_client.get_devices()

        assert len(devices) == 1
        assert devices[0]["deviceId"] == "device_123"
        assert devices[0]["deviceName"] == "Test Device"

    @pytest.mark.asyncio
    async def test_get_devices_not_authenticated(self, client: MoogoClient) -> None:
        """Test getting devices without authentication."""
        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.get_devices()

    @pytest.mark.asyncio
    async def test_get_devices_caching(
        self,
        authenticated_client: MoogoClient,
        mock_devices_response: dict[str, Any],
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test device list caching."""
        mock_response_cm = create_response(200, mock_devices_response)
        mock_session.request.return_value = mock_response_cm

        # First call - should hit API
        devices1 = await authenticated_client.get_devices()
        assert mock_session.request.call_count == 1

        # Second call - should use cache
        devices2 = await authenticated_client.get_devices()
        assert mock_session.request.call_count == 1  # No additional call
        assert devices1 == devices2

    @pytest.mark.asyncio
    async def test_get_devices_force_refresh(
        self,
        authenticated_client: MoogoClient,
        mock_devices_response: dict[str, Any],
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test force refresh bypasses cache."""
        mock_response_cm = create_response(200, mock_devices_response)
        mock_session.request.return_value = mock_response_cm

        # First call
        await authenticated_client.get_devices()
        assert mock_session.request.call_count == 1

        # Force refresh - should hit API again
        await authenticated_client.get_devices(force_refresh=True)
        assert mock_session.request.call_count == 2

    @pytest.mark.asyncio
    async def test_get_device_status_success(
        self,
        authenticated_client: MoogoClient,
        mock_device_data: dict[str, Any],
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test getting device status successfully."""
        response = {
            "code": 0,
            "message": "success",
            "data": mock_device_data,
        }

        mock_response_cm = create_response(200, response)
        mock_session.request.return_value = mock_response_cm

        status = await authenticated_client.get_device_status("device_123")

        assert isinstance(status, DeviceStatus)
        assert status.device_id == "device_123"
        assert status.device_name == "Test Device"
        assert status.is_online is True

    @pytest.mark.asyncio
    async def test_get_device_status_not_authenticated(self, client: MoogoClient) -> None:
        """Test getting device status without authentication."""
        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.get_device_status("device_123")


class TestSprayControl:
    """Tests for spray control operations."""

    @pytest.mark.asyncio
    async def test_start_spray_success(
        self,
        authenticated_client: MoogoClient,
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test starting spray successfully."""
        # Mock spray start
        spray_response = {
            "code": 0,
            "message": "success",
            "data": {},
        }

        mock_spray_cm = create_response(200, spray_response)
        mock_session.request.return_value = mock_spray_cm

        result = await authenticated_client.start_spray("device_123")

        assert result is True

    @pytest.mark.asyncio
    async def test_start_spray_with_mode(
        self,
        authenticated_client: MoogoClient,
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test starting spray with mode parameter."""
        spray_response = {
            "code": 0,
            "message": "success",
            "data": {},
        }

        mock_spray_cm = create_response(200, spray_response)
        mock_session.request.return_value = mock_spray_cm

        result = await authenticated_client.start_spray("device_123", mode="auto")

        assert result is True

    @pytest.mark.asyncio
    async def test_start_spray_device_offline(
        self,
        authenticated_client: MoogoClient,
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test starting spray when device is offline."""
        # Mock API error for offline device
        spray_error = {
            "code": 10201,
            "message": "Device offline",
            "data": {},
        }

        mock_spray_cm = create_response(200, spray_error)
        mock_session.request.return_value = mock_spray_cm

        with pytest.raises(MoogoDeviceError, match="Device offline"):
            await authenticated_client.start_spray("device_123")

    @pytest.mark.asyncio
    async def test_start_spray_not_authenticated(self, client: MoogoClient) -> None:
        """Test starting spray without authentication."""
        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.start_spray("device_123")

    @pytest.mark.asyncio
    async def test_stop_spray_success(
        self,
        authenticated_client: MoogoClient,
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test stopping spray successfully."""
        response = {
            "code": 0,
            "message": "success",
            "data": {},
        }

        mock_response_cm = create_response(200, response)
        mock_session.request.return_value = mock_response_cm

        result = await authenticated_client.stop_spray("device_123")

        assert result is True

    @pytest.mark.asyncio
    async def test_stop_spray_not_authenticated(self, client: MoogoClient) -> None:
        """Test stopping spray without authentication."""
        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.stop_spray("device_123")
