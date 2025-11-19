"""Integration tests for Priority 1 features.

These tests require real API credentials set in .env file.
Run with: pytest test_integration_priority1.py -m integration
"""

from datetime import datetime

import pytest

from pymoogo import MoogoAuthError, MoogoClient

# Integration tests marker
pytestmark = pytest.mark.integration


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
class TestAuthentication:
    """Test authentication with real API."""

    async def test_login_success(self, real_credentials):
        """Test successful login with real credentials."""
        async with MoogoClient(
            email=real_credentials["email"], password=real_credentials["password"]
        ) as client:
            auth_data = await client.authenticate()

            assert isinstance(auth_data, dict)
            assert "token" in auth_data
            assert "user_id" in auth_data
            assert client.is_authenticated
            assert client._token is not None
            assert client._user_id is not None

    async def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        async with MoogoClient(email="invalid@example.com", password="wrong_password") as client:
            with pytest.raises(MoogoAuthError):
                await client.authenticate()


@pytest.mark.integration
@pytest.mark.asyncio
class TestDeviceDiscovery:
    """Test device discovery with real API."""

    async def test_get_devices(self, real_credentials):
        """Test getting device list."""
        async with MoogoClient(**real_credentials) as client:
            await client.authenticate()
            devices = await client.get_devices()

            assert isinstance(devices, list)
            # User should have at least one device for full testing
            if len(devices) > 0:
                device = devices[0]
                assert "deviceId" in device
                assert "deviceName" in device
                assert "onlineStatus" in device

    async def test_get_device_status(self, real_credentials, test_device_id):
        """Test getting device status."""
        async with MoogoClient(**real_credentials) as client:
            await client.authenticate()

            # Get device ID
            if test_device_id:
                device_id = test_device_id
            else:
                devices = await client.get_devices()
                if len(devices) == 0:
                    pytest.skip("No devices available for testing")
                device_id = devices[0]["deviceId"]

            # Get device status
            status = await client.get_device_status(device_id)

            assert status.device_id == device_id
            assert hasattr(status, "online_status")
            assert hasattr(status, "run_status")
            assert hasattr(status, "firmware")


@pytest.mark.integration
@pytest.mark.priority1
@pytest.mark.asyncio
class TestDeviceLogs:
    """Test device logs (Priority 1 feature)."""

    async def test_get_device_logs(self, real_credentials, test_device_id):
        """Test getting device operation logs."""
        async with MoogoClient(**real_credentials) as client:
            await client.authenticate()

            # Get device ID
            if test_device_id:
                device_id = test_device_id
            else:
                devices = await client.get_devices()
                if len(devices) == 0:
                    pytest.skip("No devices available for testing")
                device_id = devices[0]["deviceId"]

            # Get logs
            logs = await client.get_device_logs(device_id)

            assert isinstance(logs, dict)
            # Logs may be empty for new devices
            if "items" in logs:
                assert isinstance(logs["items"], list)

    async def test_get_device_logs_with_pagination(self, real_credentials, test_device_id):
        """Test getting device logs with pagination."""
        async with MoogoClient(**real_credentials) as client:
            await client.authenticate()

            # Get device ID
            if test_device_id:
                device_id = test_device_id
            else:
                devices = await client.get_devices()
                if len(devices) == 0:
                    pytest.skip("No devices available for testing")
                device_id = devices[0]["deviceId"]

            # Get logs with pagination
            logs = await client.get_device_logs(device_id, page=1, page_size=10)

            assert isinstance(logs, dict)

    async def test_get_device_logs_with_date_filter(self, real_credentials, test_device_id):
        """Test getting device logs with date filtering."""
        async with MoogoClient(**real_credentials) as client:
            await client.authenticate()

            # Get device ID
            if test_device_id:
                device_id = test_device_id
            else:
                devices = await client.get_devices()
                if len(devices) == 0:
                    pytest.skip("No devices available for testing")
                device_id = devices[0]["deviceId"]

            # Get logs for last 7 days
            today = datetime.now().strftime("%Y-%m-%d")
            logs = await client.get_device_logs(device_id, end_date=today)

            assert isinstance(logs, dict)


@pytest.mark.integration
@pytest.mark.priority1
@pytest.mark.asyncio
class TestScheduleManagement:
    """Test schedule management (Priority 1 features)."""

    async def test_get_device_schedules(self, real_credentials, test_device_id):
        """Test getting device schedules."""
        async with MoogoClient(**real_credentials) as client:
            await client.authenticate()

            # Get device ID
            if test_device_id:
                device_id = test_device_id
            else:
                devices = await client.get_devices()
                if len(devices) == 0:
                    pytest.skip("No devices available for testing")
                device_id = devices[0]["deviceId"]

            # Get schedules
            schedules = await client.get_device_schedules(device_id)

            assert isinstance(schedules, list)

    async def test_create_and_delete_schedule(self, real_credentials, test_device_id):
        """Test creating and deleting a schedule."""
        async with MoogoClient(**real_credentials) as client:
            await client.authenticate()

            # Get device ID
            if test_device_id:
                device_id = test_device_id
            else:
                devices = await client.get_devices()
                if len(devices) == 0:
                    pytest.skip("No devices available for testing")
                device_id = devices[0]["deviceId"]

            # Create a test schedule
            success = await client.create_schedule(
                device_id=device_id,
                hour=10,
                minute=30,
                duration=60,
                repeat_set="1,2,3,4,5",  # Weekdays
            )

            assert success is True

            # Get schedules to find the one we created
            schedules = await client.get_device_schedules(device_id)

            # Find our test schedule
            test_schedule = None
            for schedule in schedules:
                if schedule.hour == 10 and schedule.minute == 30:
                    test_schedule = schedule
                    break

            if test_schedule:
                # Delete the schedule
                schedule_id = test_schedule.id
                success = await client.delete_schedule(device_id, schedule_id)
                assert success is True

    @pytest.mark.device
    async def test_enable_disable_schedule(self, real_credentials, test_device_id):
        """Test enabling and disabling a schedule."""
        async with MoogoClient(**real_credentials) as client:
            await client.authenticate()

            # Get device ID
            if test_device_id:
                device_id = test_device_id
            else:
                devices = await client.get_devices()
                if len(devices) == 0:
                    pytest.skip("No devices available for testing")
                device_id = devices[0]["deviceId"]

            # Get existing schedules
            schedules = await client.get_device_schedules(device_id)

            if len(schedules) == 0:
                pytest.skip("No schedules available for testing")

            schedule_id = schedules[0].id

            # Disable schedule
            success = await client.disable_schedule(device_id, schedule_id)
            assert success is True

            # Enable schedule
            success = await client.enable_schedule(device_id, schedule_id)
            assert success is True

    @pytest.mark.device
    async def test_skip_schedule(self, real_credentials, test_device_id):
        """Test skipping a schedule occurrence."""
        async with MoogoClient(**real_credentials) as client:
            await client.authenticate()

            # Get device ID
            if test_device_id:
                device_id = test_device_id
            else:
                devices = await client.get_devices()
                if len(devices) == 0:
                    pytest.skip("No devices available for testing")
                device_id = devices[0]["deviceId"]

            # Get existing schedules
            schedules = await client.get_device_schedules(device_id)

            if len(schedules) == 0:
                pytest.skip("No schedules available for testing")

            schedule_id = schedules[0].id

            # Skip next occurrence
            success = await client.skip_schedule(device_id, schedule_id)
            assert success is True

    @pytest.mark.device
    async def test_enable_disable_all_schedules(self, real_credentials, test_device_id):
        """Test bulk enable/disable all schedules."""
        async with MoogoClient(**real_credentials) as client:
            await client.authenticate()

            # Get device ID
            if test_device_id:
                device_id = test_device_id
            else:
                devices = await client.get_devices()
                if len(devices) == 0:
                    pytest.skip("No devices available for testing")
                device_id = devices[0]["deviceId"]

            # Disable all schedules
            success = await client.disable_all_schedules(device_id)
            assert success is True

            # Enable all schedules
            success = await client.enable_all_schedules(device_id)
            assert success is True


@pytest.mark.integration
@pytest.mark.priority1
@pytest.mark.asyncio
class TestDeviceConfiguration:
    """Test device configuration (Priority 1 features)."""

    async def test_get_device_config(self, real_credentials, test_device_id):
        """Test getting device configuration."""
        async with MoogoClient(**real_credentials) as client:
            await client.authenticate()

            # Get device ID
            if test_device_id:
                device_id = test_device_id
            else:
                devices = await client.get_devices()
                if len(devices) == 0:
                    pytest.skip("No devices available for testing")
                device_id = devices[0]["deviceId"]

            # Get config
            config = await client.get_device_config(device_id)

            assert isinstance(config, dict)

    @pytest.mark.device
    async def test_set_device_config(self, real_credentials, test_device_id):
        """Test setting device configuration."""
        async with MoogoClient(**real_credentials) as client:
            await client.authenticate()

            # Get device ID
            if test_device_id:
                device_id = test_device_id
            else:
                devices = await client.get_devices()
                if len(devices) == 0:
                    pytest.skip("No devices available for testing")
                device_id = devices[0]["deviceId"]

            # Get current config
            current_config = await client.get_device_config(device_id)

            # Set config (using same values to avoid changing device state)
            success = await client.set_device_config(device_id, current_config)
            assert success is True


@pytest.mark.integration
@pytest.mark.priority1
@pytest.mark.asyncio
class TestFirmwareUpdate:
    """Test firmware update (Priority 1 features)."""

    async def test_check_firmware_update(self, real_credentials, test_device_id):
        """Test checking for firmware updates."""
        async with MoogoClient(**real_credentials) as client:
            await client.authenticate()

            # Get device ID
            if test_device_id:
                device_id = test_device_id
            else:
                devices = await client.get_devices()
                if len(devices) == 0:
                    pytest.skip("No devices available for testing")
                device_id = devices[0]["deviceId"]

            # Check for updates
            update_info = await client.check_firmware_update(device_id)

            assert isinstance(update_info, dict)
            # Update may or may not be available
            if "available" in update_info:
                assert isinstance(update_info["available"], bool)


@pytest.mark.integration
@pytest.mark.asyncio
class TestPublicEndpoints:
    """Test public endpoints (no authentication required)."""

    async def test_get_liquid_types(self, base_url):
        """Test getting liquid types without authentication."""
        async with MoogoClient(base_url=base_url) as client:
            liquid_types = await client.get_liquid_types()

            assert isinstance(liquid_types, list)
            # Should have at least one liquid type
            assert len(liquid_types) > 0

    async def test_get_recommended_schedules(self, base_url):
        """Test getting recommended schedules without authentication."""
        async with MoogoClient(base_url=base_url) as client:
            schedules = await client.get_recommended_schedules()

            assert isinstance(schedules, list)
