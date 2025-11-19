"""Tests for MoogoClient schedule operations."""

from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from pymoogo import MoogoClient
from pymoogo.exceptions import MoogoAuthError
from pymoogo.models import Schedule


class TestScheduleOperations:
    """Tests for schedule management."""

    @pytest.mark.asyncio
    async def test_get_device_schedules_success(
        self,
        authenticated_client: MoogoClient,
        mock_schedule_data: dict[str, Any],
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test getting device schedules successfully."""
        response = {
            "code": 0,
            "message": "success",
            "data": {
                "items": [mock_schedule_data],
            },
        }

        mock_response_cm = create_response(200, response)
        mock_session.request.return_value = mock_response_cm

        schedules = await authenticated_client.get_device_schedules("device_123")

        assert len(schedules) == 1
        assert isinstance(schedules[0], Schedule)
        assert schedules[0].id == "schedule_123"
        assert schedules[0].hour == 8
        assert schedules[0].minute == 30

    @pytest.mark.asyncio
    async def test_get_device_schedules_not_authenticated(self, client: MoogoClient) -> None:
        """Test getting schedules without authentication."""
        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.get_device_schedules("device_123")

    @pytest.mark.asyncio
    async def test_create_schedule_success(
        self,
        authenticated_client: MoogoClient,
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test creating a schedule successfully."""
        response = {
            "code": 0,
            "message": "success",
            "data": {},
        }

        mock_response_cm = create_response(200, response)
        mock_session.request.return_value = mock_response_cm

        result = await authenticated_client.create_schedule(
            device_id="device_123",
            hour=8,
            minute=30,
            duration=60,
            repeat_set="1,2,3,4,5",
            enabled=True,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_create_schedule_not_authenticated(self, client: MoogoClient) -> None:
        """Test creating schedule without authentication."""
        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.create_schedule(device_id="device_123", hour=8, minute=30, duration=60)

    @pytest.mark.asyncio
    async def test_update_schedule_success(
        self,
        authenticated_client: MoogoClient,
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test updating a schedule successfully."""
        response = {
            "code": 0,
            "message": "success",
            "data": {},
        }

        mock_response_cm = create_response(200, response)
        mock_session.request.return_value = mock_response_cm

        result = await authenticated_client.update_schedule(
            device_id="device_123",
            schedule_id="schedule_123",
            hour=9,
            minute=0,
            duration=120,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_update_schedule_partial(
        self,
        authenticated_client: MoogoClient,
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test partially updating a schedule."""
        response = {
            "code": 0,
            "message": "success",
            "data": {},
        }

        mock_response_cm = create_response(200, response)
        mock_session.request.return_value = mock_response_cm

        # Update only duration
        result = await authenticated_client.update_schedule(
            device_id="device_123",
            schedule_id="schedule_123",
            duration=90,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_update_schedule_not_authenticated(self, client: MoogoClient) -> None:
        """Test updating schedule without authentication."""
        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.update_schedule(
                device_id="device_123", schedule_id="schedule_123", duration=60
            )

    @pytest.mark.asyncio
    async def test_delete_schedule_success(
        self,
        authenticated_client: MoogoClient,
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test deleting a schedule successfully."""
        response = {
            "code": 0,
            "message": "success",
            "data": {},
        }

        mock_response_cm = create_response(200, response)
        mock_session.request.return_value = mock_response_cm

        result = await authenticated_client.delete_schedule(
            device_id="device_123", schedule_id="schedule_123"
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_schedule_not_authenticated(self, client: MoogoClient) -> None:
        """Test deleting schedule without authentication."""
        with pytest.raises(MoogoAuthError, match="Authentication required"):
            await client.delete_schedule(device_id="device_123", schedule_id="schedule_123")


class TestPublicEndpoints:
    """Tests for public endpoints (no auth required)."""

    @pytest.mark.asyncio
    async def test_get_liquid_types_success(
        self,
        client: MoogoClient,
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test getting liquid types from public endpoint."""
        response = {
            "code": 0,
            "message": "success",
            "data": [
                {"id": "1", "name": "Type A"},
                {"id": "2", "name": "Type B"},
            ],
        }

        mock_response_cm = create_response(200, response)
        mock_session.request.return_value = mock_response_cm

        liquids = await client.get_liquid_types()

        assert len(liquids) == 2
        assert liquids[0]["name"] == "Type A"

    @pytest.mark.asyncio
    async def test_get_recommended_schedules_success(
        self,
        client: MoogoClient,
        mock_schedule_data: dict[str, Any],
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test getting recommended schedules from public endpoint."""
        response = {
            "code": 0,
            "message": "success",
            "data": {
                "items": [mock_schedule_data],
            },
        }

        mock_response_cm = create_response(200, response)
        mock_session.request.return_value = mock_response_cm

        schedules = await client.get_recommended_schedules()

        assert len(schedules) == 1
