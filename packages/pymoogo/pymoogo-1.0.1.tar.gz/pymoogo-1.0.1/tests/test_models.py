"""Tests for pymoogo data models."""

from typing import Any

from pymoogo.models import DeviceStatus, Schedule


class TestDeviceStatus:
    """Tests for DeviceStatus model."""

    def test_from_dict(self, mock_device_data: dict[str, Any]) -> None:
        """Test creating DeviceStatus from dictionary."""
        status = DeviceStatus.from_dict(mock_device_data)

        assert status.device_id == "device_123"
        assert status.device_name == "Test Device"
        assert status.online_status == 1
        assert status.run_status == 0
        assert status.rssi == -50
        assert status.temperature == 25.5
        assert status.humidity == 60
        assert status.liquid_level == 80
        assert status.water_level == 90
        assert status.mix_ratio == 100
        assert status.firmware == "1.0.0"
        assert status.latest_spraying_duration == 30
        assert status.latest_spraying_end == 1234567890

    def test_from_dict_with_missing_fields(self) -> None:
        """Test creating DeviceStatus with minimal data."""
        minimal_data: dict[str, Any] = {}
        status = DeviceStatus.from_dict(minimal_data)

        assert status.device_id == ""
        assert status.device_name == ""
        assert status.online_status == 0
        assert status.run_status == 0
        assert status.rssi == 0
        assert status.temperature == 0.0
        assert status.humidity == 0
        assert status.liquid_level == 0
        assert status.water_level == 0
        assert status.mix_ratio == 0
        assert status.firmware == ""
        assert status.latest_spraying_duration is None
        assert status.latest_spraying_end is None

    def test_is_online_property(self, mock_device_data: dict[str, Any]) -> None:
        """Test is_online property."""
        # Online device
        status = DeviceStatus.from_dict(mock_device_data)
        assert status.is_online is True

        # Offline device
        mock_device_data["onlineStatus"] = 0
        status = DeviceStatus.from_dict(mock_device_data)
        assert status.is_online is False

    def test_is_running_property(self, mock_device_data: dict[str, Any]) -> None:
        """Test is_running property."""
        # Not running
        status = DeviceStatus.from_dict(mock_device_data)
        assert status.is_running is False

        # Running
        mock_device_data["runStatus"] = 1
        status = DeviceStatus.from_dict(mock_device_data)
        assert status.is_running is True


class TestSchedule:
    """Tests for Schedule model."""

    def test_from_dict(self, mock_schedule_data: dict[str, Any]) -> None:
        """Test creating Schedule from dictionary."""
        schedule = Schedule.from_dict(mock_schedule_data)

        assert schedule.id == "schedule_123"
        assert schedule.hour == 8
        assert schedule.minute == 30
        assert schedule.duration == 60
        assert schedule.repeat_set == "0,1,2,3,4,5,6"
        assert schedule.status == 1

    def test_from_dict_with_missing_fields(self) -> None:
        """Test creating Schedule with minimal data."""
        minimal_data: dict[str, Any] = {}
        schedule = Schedule.from_dict(minimal_data)

        assert schedule.id == ""
        assert schedule.hour == 0
        assert schedule.minute == 0
        assert schedule.duration == 0
        assert schedule.repeat_set == ""
        assert schedule.status == 0

    def test_is_enabled_property(self, mock_schedule_data: dict[str, Any]) -> None:
        """Test is_enabled property."""
        # Enabled schedule
        schedule = Schedule.from_dict(mock_schedule_data)
        assert schedule.is_enabled is True

        # Disabled schedule
        mock_schedule_data["status"] = 0
        schedule = Schedule.from_dict(mock_schedule_data)
        assert schedule.is_enabled is False

    def test_time_str_property(self, mock_schedule_data: dict[str, Any]) -> None:
        """Test time_str property formatting."""
        schedule = Schedule.from_dict(mock_schedule_data)
        assert schedule.time_str == "08:30"

        # Test different times
        mock_schedule_data["hour"] = 0
        mock_schedule_data["minute"] = 0
        schedule = Schedule.from_dict(mock_schedule_data)
        assert schedule.time_str == "00:00"

        mock_schedule_data["hour"] = 23
        mock_schedule_data["minute"] = 59
        schedule = Schedule.from_dict(mock_schedule_data)
        assert schedule.time_str == "23:59"

    def test_to_dict(self, mock_schedule_data: dict[str, Any]) -> None:
        """Test converting Schedule to dictionary."""
        schedule = Schedule.from_dict(mock_schedule_data)
        result = schedule.to_dict()

        assert result["hour"] == 8
        assert result["minute"] == 30
        assert result["duration"] == 60
        assert result["repeatSet"] == "0,1,2,3,4,5,6"
        assert result["status"] == 1
        assert "id" not in result  # ID is not included in to_dict()

    def test_schedule_equality(self, mock_schedule_data: dict[str, Any]) -> None:
        """Test Schedule dataclass equality."""
        schedule1 = Schedule.from_dict(mock_schedule_data)
        schedule2 = Schedule.from_dict(mock_schedule_data)

        assert schedule1 == schedule2

    def test_device_status_equality(self, mock_device_data: dict[str, Any]) -> None:
        """Test DeviceStatus dataclass equality."""
        status1 = DeviceStatus.from_dict(mock_device_data)
        status2 = DeviceStatus.from_dict(mock_device_data)

        assert status1 == status2
