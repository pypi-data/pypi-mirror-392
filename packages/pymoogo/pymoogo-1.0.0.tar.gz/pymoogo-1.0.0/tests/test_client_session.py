"""Tests for MoogoClient session management."""

from typing import Any
from unittest.mock import AsyncMock

import aiohttp
import pytest

from pymoogo import MoogoClient


class TestSessionInjection:
    """Tests for session injection functionality."""

    def test_client_without_session_injection(self) -> None:
        """Test client creates own session when none provided."""
        client = MoogoClient(email="test@example.com", password="password")

        assert client._session is None
        assert client._session_owner is True
        assert client.has_injected_session is False

    def test_client_with_session_injection(self, mock_session: AsyncMock) -> None:
        """Test client uses injected session."""
        client = MoogoClient(email="test@example.com", password="password", session=mock_session)

        assert client._session is mock_session
        assert client._session_owner is False
        assert client.has_injected_session is True

    def test_has_injected_session_property(self, mock_session: AsyncMock) -> None:
        """Test has_injected_session property."""
        # Without injection
        client1 = MoogoClient(email="test@example.com", password="password")
        assert client1.has_injected_session is False

        # With injection
        client2 = MoogoClient(email="test@example.com", password="password", session=mock_session)
        assert client2.has_injected_session is True

    @pytest.mark.asyncio
    async def test_close_without_session_injection(self) -> None:
        """Test close() with client-managed session."""
        client = MoogoClient(email="test@example.com", password="password")

        # Create session
        await client.__aenter__()
        assert client._session is not None

        # Close should close the session
        await client.close()
        # Session should be cleared
        assert client._session is None

    @pytest.mark.asyncio
    async def test_close_with_session_injection(self, mock_session: AsyncMock) -> None:
        """Test close() with injected session."""
        client = MoogoClient(email="test@example.com", password="password", session=mock_session)

        # Close should NOT close injected session
        await client.close()

        # Session should still be there
        assert client._session is mock_session
        # close() should not have been called on the session
        mock_session.close.assert_not_called()

    @pytest.mark.asyncio
    async def test_context_manager_without_injection(self) -> None:
        """Test context manager creates and closes session."""
        client = MoogoClient(email="test@example.com", password="password")

        async with client as c:
            assert c._session is not None
            assert c is client

        # Session should be closed after context
        assert client._session is None

    @pytest.mark.asyncio
    async def test_context_manager_with_injection(self, mock_session: AsyncMock) -> None:
        """Test context manager with injected session."""
        client = MoogoClient(email="test@example.com", password="password", session=mock_session)

        async with client as c:
            assert c._session is mock_session
            assert c is client

        # Session should NOT be closed
        assert client._session is mock_session
        mock_session.close.assert_not_called()


class TestContextManager:
    """Tests for async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_enter(self) -> None:
        """Test async context manager __aenter__."""
        client = MoogoClient(email="test@example.com", password="password")

        result = await client.__aenter__()

        assert result is client
        assert client._session is not None

    @pytest.mark.asyncio
    async def test_context_manager_exit(self, mock_session: AsyncMock) -> None:
        """Test async context manager __aexit__."""
        client = MoogoClient(email="test@example.com", password="password", session=mock_session)

        await client.__aenter__()
        await client.__aexit__(None, None, None)

        # For injected session, it should not be closed
        mock_session.close.assert_not_called()

    @pytest.mark.asyncio
    async def test_context_manager_exception_handling(self) -> None:
        """Test context manager handles exceptions."""
        client = MoogoClient(email="test@example.com", password="password")

        try:
            async with client:
                raise ValueError("Test error")
        except ValueError:
            pass

        # Session should still be cleaned up
        assert client._session is None


class TestSessionProperty:
    """Tests for session property."""

    @pytest.mark.asyncio
    async def test_session_property_lazy_creation(self) -> None:
        """Test session property creates session on access."""
        client = MoogoClient(email="test@example.com", password="password")

        assert client._session is None

        # Access session property in async context
        async with client:
            session = client.session
            assert session is not None
            assert isinstance(session, aiohttp.ClientSession)
            assert client._session is session

    def test_session_property_returns_injected(self, mock_session: AsyncMock) -> None:
        """Test session property returns injected session."""
        client = MoogoClient(email="test@example.com", password="password", session=mock_session)

        assert client.session is mock_session


class TestConnectionTest:
    """Tests for test_connection method."""

    @pytest.mark.asyncio
    async def test_test_connection_public_endpoint(
        self, client: MoogoClient, mock_session: AsyncMock, create_response: Any
    ) -> None:
        """Test connection test uses public endpoint."""
        response = {
            "code": 0,
            "message": "success",
            "data": [],
        }

        mock_response_cm = create_response(200, response)
        mock_session.request.return_value = mock_response_cm

        result = await client.test_connection()

        assert result is True

    @pytest.mark.asyncio
    async def test_test_connection_failure(
        self, client: MoogoClient, mock_session: AsyncMock
    ) -> None:
        """Test connection test handles failures."""
        mock_session.request.side_effect = Exception("Connection failed")

        result = await client.test_connection()

        assert result is False
