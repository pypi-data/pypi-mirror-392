"""Tests for MoogoClient authentication."""

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from pymoogo import MoogoClient
from pymoogo.exceptions import MoogoAuthError, MoogoRateLimitError


class TestAuthentication:
    """Tests for authentication methods."""

    @pytest.mark.asyncio
    async def test_authenticate_success(
        self,
        client: MoogoClient,
        mock_auth_response: dict[str, Any],
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test successful authentication."""
        mock_response_cm = create_response(200, mock_auth_response)
        mock_session.request.return_value = mock_response_cm

        result = await client.authenticate()

        assert result["token"] == "test_token_123"
        assert result["user_id"] == "test_user_123"
        assert result["email"] == "test@example.com"
        assert client._token == "test_token_123"
        assert client._user_id == "test_user_123"
        assert client.is_authenticated is True

    @pytest.mark.asyncio
    async def test_authenticate_invalid_credentials(
        self,
        client: MoogoClient,
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test authentication with invalid credentials."""
        error_response = {
            "code": 10104,
            "message": "Invalid credentials",
            "data": {},
        }

        mock_response_cm = create_response(200, error_response)
        mock_session.request.return_value = mock_response_cm

        with pytest.raises(MoogoAuthError, match="Invalid credentials"):
            await client.authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_rate_limited(
        self,
        client: MoogoClient,
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test authentication when rate limited."""
        error_response = {
            "code": 10000,
            "message": "Rate limited",
            "data": {},
        }

        mock_response_cm = create_response(200, error_response)
        mock_session.request.return_value = mock_response_cm

        with pytest.raises(MoogoRateLimitError, match="Rate limited"):
            await client.authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_without_credentials(self) -> None:
        """Test authentication without email/password."""
        client = MoogoClient()

        with pytest.raises(MoogoAuthError, match="Email and password required"):
            await client.authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_with_override_credentials(
        self,
        client: MoogoClient,
        mock_auth_response: dict[str, Any],
        mock_session: AsyncMock,
        create_response: Callable[[int, dict[str, Any]], MagicMock],
    ) -> None:
        """Test authentication with override credentials."""
        mock_response_cm = create_response(200, mock_auth_response)
        mock_session.request.return_value = mock_response_cm

        result = await client.authenticate(email="other@example.com", password="other_pass")

        assert result["email"] == "test@example.com"  # From mock response
        assert client.is_authenticated is True

    def test_is_authenticated_property(self, client: MoogoClient) -> None:
        """Test is_authenticated property."""
        # Not authenticated initially
        assert client.is_authenticated is False

        # Set token
        client._token = "test_token"
        assert client.is_authenticated is True

        # Expired token
        client._token_expires = datetime.now() - timedelta(hours=1)
        assert client.is_authenticated is False

        # Valid token
        client._token_expires = datetime.now() + timedelta(hours=1)
        assert client.is_authenticated is True


class TestSessionManagement:
    """Tests for authentication session management."""

    def test_get_auth_session(self, authenticated_client: MoogoClient) -> None:
        """Test getting current auth session."""
        session_data = authenticated_client.get_auth_session()

        assert session_data["token"] == "test_token_123"
        assert session_data["user_id"] == "test_user_123"
        assert session_data["is_authenticated"] is True

    def test_set_auth_session(self, client: MoogoClient) -> None:
        """Test setting auth session from saved data."""
        session_data = {
            "token": "restored_token",
            "user_id": "restored_user",
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
        }

        client.set_auth_session(session_data)

        assert client._token == "restored_token"
        assert client._user_id == "restored_user"
        assert client.is_authenticated is True

    def test_set_auth_session_with_invalid_expiry(self, client: MoogoClient) -> None:
        """Test setting auth session with invalid expiry format."""
        session_data = {
            "token": "test_token",
            "user_id": "test_user",
            "expires_at": "invalid_date",
        }

        client.set_auth_session(session_data)

        assert client._token == "test_token"
        assert client._user_id == "test_user"
        assert client._token_expires is None

    def test_set_auth_session_without_expiry(self, client: MoogoClient) -> None:
        """Test setting auth session without expiry."""
        session_data = {
            "token": "test_token",
            "user_id": "test_user",
        }

        client.set_auth_session(session_data)

        assert client._token == "test_token"
        assert client._user_id == "test_user"
