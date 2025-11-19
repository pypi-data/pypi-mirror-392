"""Data models for Moogo API."""

from dataclasses import dataclass
from typing import Any


@dataclass
class DeviceStatus:
    """Device status information."""

    device_id: str
    device_name: str
    online_status: int  # 0=offline, 1=online
    run_status: int  # 0=stopped, 1=running
    rssi: int
    temperature: float
    humidity: int
    liquid_level: int
    water_level: int
    mix_ratio: int
    firmware: str
    latest_spraying_duration: int | None = None
    latest_spraying_end: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeviceStatus":
        """Create DeviceStatus from API response dictionary."""
        return cls(
            device_id=data.get("deviceId", ""),
            device_name=data.get("deviceName", ""),
            online_status=data.get("onlineStatus", 0),
            run_status=data.get("runStatus", 0),
            rssi=data.get("rssi", 0),
            temperature=data.get("temperature", 0.0),
            humidity=data.get("humidity", 0),
            liquid_level=data.get("liquid_level", 0),
            water_level=data.get("water_level", 0),
            mix_ratio=data.get("mixRatio", 0),
            firmware=data.get("firmware", ""),
            latest_spraying_duration=data.get("latestSprayingDuration"),
            latest_spraying_end=data.get("latestSprayingEnd"),
        )

    @property
    def is_online(self) -> bool:
        """Check if device is online."""
        return self.online_status == 1

    @property
    def is_running(self) -> bool:
        """Check if device is currently spraying."""
        return self.run_status == 1


@dataclass
class Schedule:
    """Spray schedule information."""

    id: str
    hour: int
    minute: int
    duration: int
    repeat_set: str
    status: int  # 1=enabled, 0=disabled

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Schedule":
        """Create Schedule from API response dictionary."""
        return cls(
            id=data.get("id", ""),
            hour=data.get("hour", 0),
            minute=data.get("minute", 0),
            duration=data.get("duration", 0),
            repeat_set=data.get("repeatSet", ""),
            status=data.get("status", 0),
        )

    @property
    def is_enabled(self) -> bool:
        """Check if schedule is enabled."""
        return self.status == 1

    @property
    def time_str(self) -> str:
        """Get formatted time string."""
        return f"{self.hour:02d}:{self.minute:02d}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to API request dictionary."""
        return {
            "hour": self.hour,
            "minute": self.minute,
            "duration": self.duration,
            "repeatSet": self.repeat_set,
            "status": self.status,
        }
