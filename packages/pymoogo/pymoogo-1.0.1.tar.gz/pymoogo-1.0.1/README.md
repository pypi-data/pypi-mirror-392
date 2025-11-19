# pymoogo

Python client library for the Moogo smart spray system API.

> **Note:** This is a community-created project and is not an official implementation by Moogo. It was developed through reverse engineering of the Android app and is maintained independently. Use at your own risk.

## Features

- **Async/Await Support** - Built with `aiohttp` for non-blocking operations
- **Session Injection** - Support for external aiohttp session management (Home Assistant compatible)
- **Automatic Authentication** - Token-based auth with automatic reauthentication
- **Device Management** - Discover, monitor, and control Moogo devices
- **Schedule Management** - Create and manage spray schedules with custom durations
- **Type Hints** - Full type annotations for better IDE support
- **Error Handling** - Comprehensive exception handling with specific error types

## Installation

```bash
pip install pymoogo
```

For development:
```bash
pip install pymoogo[dev]
```

## Quick Start

```python
import asyncio
from pymoogo import MoogoClient

async def main():
    async with MoogoClient(email="your@email.com", password="your_password") as client:
        # Authenticate
        await client.authenticate()

        # Get devices
        devices = await client.get_devices()
        print(f"Found {len(devices)} devices")

        # Get device status
        if devices:
            device_id = devices[0]["deviceId"]
            status = await client.get_device_status(device_id)
            print(f"Device: {status.device_name}")
            print(f"Online: {status.is_online}")
            print(f"Running: {status.is_running}")

            # Start spray
            await client.start_spray(device_id)

            # Wait a bit
            await asyncio.sleep(5)

            # Stop spray
            await client.stop_spray(device_id)

asyncio.run(main())
```

## Usage Examples

### Authentication

```python
from pymoogo import MoogoClient

client = MoogoClient(email="your@email.com", password="your_password")
await client.authenticate()

# Check authentication status
if client.is_authenticated:
    print("Authenticated successfully!")
```

### Session Injection (Home Assistant Pattern)

The client supports injecting an external `aiohttp.ClientSession`, which is useful for Home Assistant integrations or applications that manage a shared session pool.

```python
import aiohttp
from pymoogo import MoogoClient

# Create a shared session (e.g., provided by Home Assistant)
session = aiohttp.ClientSession()

# Inject the session into the client
client = MoogoClient(
    email="your@email.com",
    password="your_password",
    session=session  # Injected session
)

# Use the client
await client.authenticate()
devices = await client.get_devices()

# Check if using injected session
print(f"Using injected session: {client.has_injected_session}")

# Close the client (does NOT close the injected session)
await client.close()

# Caller is responsible for closing the injected session
await session.close()
```

**Key points about session injection:**
- When a session is injected, the client will **NOT** close it when `close()` is called
- The caller is responsible for managing the session lifecycle
- Multiple clients can share the same session
- Use `client.has_injected_session` to check if a session was injected

### Session Persistence

Save and restore authentication sessions to avoid re-authenticating on every restart:

```python
from pymoogo import MoogoClient
import json

# Authenticate and save session
client = MoogoClient(email="...", password="...")
auth_data = await client.authenticate()

# Save to file/database
with open("session.json", "w") as f:
    json.dump(auth_data, f)

# Later, restore the session
with open("session.json", "r") as f:
    saved_session = json.load(f)

client = MoogoClient()
client.set_auth_session(saved_session)

if client.is_authenticated:
    # Use client without re-authenticating
    devices = await client.get_devices()
else:
    # Session expired, need to re-authenticate
    await client.authenticate()
```

**Session management methods:**
- `await client.authenticate()` - Returns session data dictionary
- `client.get_auth_session()` - Get current session state
- `client.set_auth_session(data)` - Restore saved session
- `client.is_authenticated` - Check if session is valid

### Device Discovery and Status

```python
# Get all devices
devices = await client.get_devices()

for device in devices:
    device_id = device["deviceId"]

    # Get detailed status
    status = await client.get_device_status(device_id)

    print(f"Device: {status.device_name}")
    print(f"  Online: {status.is_online}")
    print(f"  Running: {status.is_running}")
    print(f"  Temperature: {status.temperature}°C")
    print(f"  Humidity: {status.humidity}%")
    print(f"  Water Level: {status.water_level}")
    print(f"  Liquid Level: {status.liquid_level}")
```

### Spray Control

```python
device_id = "your_device_id"

# Start spray
await client.start_spray(device_id)

# Stop spray
await client.stop_spray(device_id)
```

### Schedule Management

```python
device_id = "your_device_id"

# Get existing schedules
schedules = await client.get_device_schedules(device_id)
for schedule in schedules:
    print(f"Schedule: {schedule.time_str} for {schedule.duration}s")

# Create a new schedule
# Spray every day at 8:00 AM for 60 seconds
await client.create_schedule(
    device_id=device_id,
    hour=8,
    minute=0,
    duration=60,
    repeat_set="0,1,2,3,4,5,6",  # All days
    enabled=True
)

# Update a schedule
await client.update_schedule(
    device_id=device_id,
    schedule_id="schedule_id",
    duration=120,  # Change to 120 seconds
    enabled=False  # Disable schedule
)

# Delete a schedule
await client.delete_schedule(device_id, schedule_id)
```

### Public Endpoints (No Authentication Required)

```python
# Get available liquid types
liquid_types = await client.get_liquid_types()

# Get recommended schedules
schedules = await client.get_recommended_schedules()
```

## Data Models

### DeviceStatus

```python
@dataclass
class DeviceStatus:
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
    latest_spraying_duration: Optional[int]
    latest_spraying_end: Optional[int]

    @property
    def is_online(self) -> bool

    @property
    def is_running(self) -> bool
```

### Schedule

```python
@dataclass
class Schedule:
    id: str
    hour: int
    minute: int
    duration: int
    repeat_set: str
    status: int  # 1=enabled, 0=disabled

    @property
    def is_enabled(self) -> bool

    @property
    def time_str(self) -> str
```

## Exception Handling

```python
from pymoogo import (
    MoogoClient,
    MoogoAPIError,
    MoogoAuthError,
    MoogoDeviceError,
    MoogoRateLimitError,
)

try:
    await client.start_spray(device_id)
except MoogoAuthError:
    print("Authentication failed")
except MoogoDeviceError:
    print("Device is offline or operation failed")
except MoogoRateLimitError:
    print("Rate limited - wait 24 hours")
except MoogoAPIError as e:
    print(f"API error: {e}")
```

## Error Codes

- `0` - Success
- `10000` - Rate limited (24-hour lockout, do not retry)
- `10104` - Invalid credentials
- `10201` - Device offline
- `401` - Unauthorized
- `500` - Server error

## Development

```bash
# Clone repository
git clone https://github.com/joyfulhouse/pymoogo.git
cd pymoogo

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black pymoogo

# Type checking
mypy pymoogo

# Linting
ruff pymoogo
```

## API Documentation

See [openapi.yaml](docs/openapi.yaml) for complete API documentation.

## Publishing

For information on publishing this package to PyPI, see:
- [docs/PUBLISHING.md](docs/PUBLISHING.md) - Complete publishing guide
- [docs/NEXT_STEPS.md](docs/NEXT_STEPS.md) - Quick setup checklist

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Disclaimer

This is an unofficial API client reverse-engineered from the Moogo Android app. It is not affiliated with or endorsed by Moogo.
