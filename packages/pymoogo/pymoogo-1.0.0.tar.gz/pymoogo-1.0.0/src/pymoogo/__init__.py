"""Moogo API Client Library

A Python client library for the Moogo smart spray system API.
"""

from pymoogo.client import MoogoClient
from pymoogo.exceptions import (
    MoogoAPIError,
    MoogoAuthError,
    MoogoDeviceError,
    MoogoRateLimitError,
)
from pymoogo.models import DeviceStatus, Schedule

__version__ = "1.0.0"
__all__ = [
    "MoogoClient",
    "MoogoAPIError",
    "MoogoAuthError",
    "MoogoDeviceError",
    "MoogoRateLimitError",
    "DeviceStatus",
    "Schedule",
]
