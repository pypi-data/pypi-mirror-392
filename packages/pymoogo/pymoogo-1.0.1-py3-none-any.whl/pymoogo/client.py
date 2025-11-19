"""Moogo API Client - Optimized implementation."""

import asyncio
import logging
import random
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps
from types import TracebackType
from typing import Any, TypeVar

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from pymoogo.exceptions import (
    MoogoAPIError,
    MoogoAuthError,
    MoogoDeviceError,
    MoogoRateLimitError,
)
from pymoogo.models import DeviceStatus, Schedule

_LOGGER = logging.getLogger(__name__)

# Type variable for retry decorator
T = TypeVar("T")


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 30.0,
    jitter: bool = True,
    retry_on: tuple[type[Exception], ...] = (MoogoDeviceError,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for retrying async functions with exponential backoff.

    Features:
    - Exponential backoff: delay doubles after each retry (configurable)
    - Jitter: adds 0-1 second randomization to prevent thundering herd
    - Max delay cap: prevents excessive wait times
    - Selective retry: only retries on specific exceptions
    - Never retries rate limit errors (24-hour lockout)

    Args:
        max_attempts: Maximum number of attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        backoff_factor: Multiplier for delay after each attempt (default: 2.0)
        max_delay: Maximum delay cap in seconds (default: 30.0)
        jitter: Whether to add 0-1s randomization (default: True)
        retry_on: Tuple of exceptions to retry on (default: MoogoDeviceError only)

    Returns:
        Decorated async function with retry logic

    Example:
        @retry_with_backoff(max_attempts=5, initial_delay=2.0)
        async def start_spray(device_id: str) -> bool:
            # Will retry up to 5 times with 2s initial delay
            pass
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception: Exception | None = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except MoogoRateLimitError:
                    # NEVER retry rate limit errors - 24-hour lockout
                    _LOGGER.error(f"{func.__name__}: Rate limited (24-hour lockout). Do not retry.")
                    raise
                except retry_on as e:
                    last_exception = e
                    if attempt == max_attempts:
                        _LOGGER.error(
                            f"Max retry attempts ({max_attempts}) reached for {func.__name__}: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    current_delay = min(delay, max_delay)
                    if jitter:
                        # Add 0-1s random jitter to prevent synchronized retries
                        current_delay += random.random()

                    _LOGGER.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )

                    await asyncio.sleep(current_delay)
                    delay *= backoff_factor

            # Should never reach here, but satisfies type checker
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected retry logic state")

        return wrapper

    return decorator


class MoogoClient:
    """
    Moogo API Client

    Features:
    - Email/password authentication with automatic token management
    - Device discovery and status monitoring
    - Manual spray control (start/stop)
    - Schedule management with custom durations
    - Public data access (liquid types, schedules)
    - Automatic retry with exponential backoff
    - Circuit breaker for offline devices
    """

    BASE_URL = "https://api.moogo.com"
    DEFAULT_TIMEOUT = 30

    # Response codes
    SUCCESS_CODE = 0
    AUTH_INVALID_CODE = 10104
    RATE_LIMITED_CODE = 10000
    DEVICE_OFFLINE_CODE = 10201
    UNAUTHORIZED_CODE = 401
    SERVER_ERROR_CODE = 500

    # API Endpoints
    ENDPOINTS = {
        "login": "v1/user/login",
        "devices": "v1/devices",
        "device_detail": "v1/devices/{device_id}",
        "device_start": "v1/devices/{device_id}/start",
        "device_stop": "v1/devices/{device_id}/stop",
        "device_schedules": "v1/devices/{device_id}/schedules",
        "device_schedule_detail": "v1/devices/{device_id}/schedules/{schedule_id}",
        "device_logs": "v1/devices/{device_id}/logs",
        "device_config": "v1/devices/{device_id}/configs",
        "device_configs": "v1/devices/{device_id}/configs",  # Alias for compatibility
        "device_ota_check": "v1/devices/{device_id}/otaCheck",
        "device_ota_update": "v1/devices/{device_id}/otaUpdate",
        "schedule_enable": "v1/devices/{device_id}/schedules/{schedule_id}/enable",
        "schedule_disable": "v1/devices/{device_id}/schedules/{schedule_id}/disable",
        "schedule_skip": "v1/devices/{device_id}/schedules/{schedule_id}/skip",
        "schedules_enable_all": "v1/devices/{device_id}/schedules/switch/open",
        "schedules_disable_all": "v1/devices/{device_id}/schedules/switch/close",
        "liquid_types": "v1/liquid",
        "recommended_schedules": "v1/devices/schedules",
    }

    def __init__(
        self,
        email: str | None = None,
        password: str | None = None,
        base_url: str = BASE_URL,
        session: ClientSession | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize Moogo API client.

        Args:
            email: User email for authentication
            password: User password for authentication
            base_url: API base URL
            session: Optional aiohttp ClientSession for session injection.
                     If provided, the client will use this session and will NOT
                     close it on cleanup. The caller is responsible for managing
                     the session lifecycle. This is useful for Home Assistant
                     integrations that use a shared session.
            timeout: Request timeout in seconds (only used if session is not provided)

        Example:
            # Without session injection (client manages session)
            async with MoogoClient(email="...", password="...") as client:
                await client.authenticate()

            # With session injection (caller manages session)
            session = aiohttp.ClientSession()
            client = MoogoClient(email="...", password="...", session=session)
            await client.authenticate()
            await client.close()  # Won't close the session
            await session.close()  # Caller closes the session
        """
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.password = password
        self.timeout = ClientTimeout(total=timeout)

        # Session management
        self._session = session
        self._session_owner = session is None

        # Authentication state
        self._token: str | None = None
        self._user_id: str | None = None
        self._token_expires: datetime | None = None

        # Caching
        self._devices_cache: list[dict[str, Any]] | None = None
        self._devices_cache_time: datetime | None = None
        self._devices_cache_ttl = timedelta(minutes=5)

        # Circuit breaker for offline devices
        self._device_circuit_breakers: dict[str, dict[str, Any]] = {}
        self._circuit_breaker_threshold = 5  # failures before opening circuit
        self._circuit_breaker_timeout = timedelta(minutes=5)  # cooldown period

    async def __aenter__(self) -> "MoogoClient":
        """Async context manager entry."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """
        Close the client and cleanup resources.

        Note: If a session was injected via the constructor, it will NOT be closed.
        Only sessions created internally by the client will be closed.
        """
        if self._session_owner and self._session:
            await self._session.close()
            self._session = None

    @property
    def session(self) -> ClientSession:
        """Get or create aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    @property
    def has_injected_session(self) -> bool:
        """Check if client is using an injected session (not owned by client)."""
        return not self._session_owner

    @property
    def is_authenticated(self) -> bool:
        """Check if client is authenticated with valid token."""
        return self._token is not None and (
            self._token_expires is None or datetime.now() < self._token_expires
        )

    def _get_headers(self, authenticated: bool = True) -> dict[str, str]:
        """Build request headers."""
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Moogo API Client/1.0",
        }
        if authenticated and self._token:
            headers["token"] = self._token
        return headers

    def _is_circuit_open(self, device_id: str) -> bool:
        """
        Check if circuit breaker is open for a device.

        Returns:
            True if circuit is open (device is in cooldown period)
        """
        if device_id not in self._device_circuit_breakers:
            return False

        breaker = self._device_circuit_breakers[device_id]
        failures = breaker.get("failures", 0)
        last_failure = breaker.get("last_failure")

        # Circuit is open if failures exceed threshold
        if failures >= self._circuit_breaker_threshold:
            # Check if cooldown period has passed
            if last_failure and datetime.now() - last_failure < self._circuit_breaker_timeout:
                return True
            # Cooldown passed, reset circuit
            breaker["failures"] = 0

        return False

    def _record_device_failure(self, device_id: str, error: Exception | None = None) -> None:
        """
        Record a device failure for circuit breaker logic.

        Args:
            device_id: Device ID
            error: Optional exception for logging (unused, for API compatibility)
        """
        if device_id not in self._device_circuit_breakers:
            self._device_circuit_breakers[device_id] = {"failures": 0, "last_failure": None}

        breaker = self._device_circuit_breakers[device_id]
        breaker["failures"] = breaker.get("failures", 0) + 1
        breaker["last_failure"] = datetime.now()

        if breaker["failures"] >= self._circuit_breaker_threshold:
            _LOGGER.warning(
                f"Circuit breaker opened for device {device_id} "
                f"after {breaker['failures']} failures. "
                f"Cooldown: {self._circuit_breaker_timeout.total_seconds()}s"
            )

    def _record_device_success(self, device_id: str) -> None:
        """Record a device success, resetting circuit breaker."""
        if device_id not in self._device_circuit_breakers:
            self._device_circuit_breakers[device_id] = {
                "failures": 0,
                "last_failure": None,
                "last_success": datetime.now(),
            }
        else:
            self._device_circuit_breakers[device_id]["failures"] = 0
            self._device_circuit_breakers[device_id]["last_success"] = datetime.now()
        _LOGGER.debug(f"Circuit breaker reset for device {device_id}")

    def get_device_circuit_status(self, device_id: str) -> dict[str, Any]:
        """
        Get circuit breaker status for a device.

        Args:
            device_id: Device ID

        Returns:
            Dictionary with circuit breaker status:
            - circuit_open: Whether circuit is currently open
            - is_open: Whether circuit is currently open (alias)
            - failures: Number of consecutive failures
            - last_failure: Timestamp of last failure (or None)
            - last_success: Timestamp of last success (or None)
        """
        if device_id not in self._device_circuit_breakers:
            return {
                "circuit_open": False,
                "is_open": False,
                "failures": 0,
                "last_failure": None,
                "last_success": None,
            }

        breaker = self._device_circuit_breakers[device_id]
        is_open = self._is_circuit_open(device_id)
        return {
            "circuit_open": is_open,  # For backward compatibility with tests
            "is_open": is_open,  # More intuitive naming
            "failures": breaker.get("failures", 0),
            "last_failure": breaker.get("last_failure"),
            "last_success": breaker.get("last_success"),
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        authenticated: bool = True,
        retry_auth: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Make API request with error handling.

        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            authenticated: Whether request requires authentication
            retry_auth: Whether to retry with reauthentication on 401
            **kwargs: Additional arguments for aiohttp request

        Returns:
            Parsed JSON response

        Raises:
            MoogoAPIError, MoogoAuthError, MoogoRateLimitError, MoogoDeviceError
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers(authenticated)

        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        try:
            async with self.session.request(method, url, headers=headers, **kwargs) as response:
                # Handle HTTP errors
                if response.status != 200:
                    if response.status == 401 and authenticated and retry_auth:
                        if await self._reauthenticate():
                            return await self._request(
                                method, endpoint, authenticated, False, **kwargs
                            )
                        raise MoogoAuthError("Reauthentication failed")
                    raise MoogoAPIError(f"HTTP {response.status}: {response.reason}")

                data: dict[str, Any] = await response.json()

                # Handle API error codes
                code = data.get("code")
                message = data.get("message", "Unknown error")

                if code == self.SUCCESS_CODE:
                    return data

                # Handle specific error codes
                if code == self.AUTH_INVALID_CODE:
                    raise MoogoAuthError(f"Invalid credentials: {message}")
                if code == self.RATE_LIMITED_CODE:
                    raise MoogoRateLimitError(f"Rate limited: {message}")
                if code == self.DEVICE_OFFLINE_CODE:
                    raise MoogoDeviceError(f"Device offline: {message}")
                if code == self.UNAUTHORIZED_CODE and authenticated and retry_auth:
                    if await self._reauthenticate():
                        return await self._request(method, endpoint, authenticated, False, **kwargs)
                    raise MoogoAuthError("Reauthentication failed")
                if code == self.UNAUTHORIZED_CODE:
                    raise MoogoAuthError(f"Unauthorized: {message}")

                raise MoogoAPIError(f"API error {code}: {message}")

        except aiohttp.ClientError as e:
            raise MoogoAPIError(f"Request failed: {e}") from e

    async def _reauthenticate(self) -> bool:
        """Attempt to reauthenticate with stored credentials."""
        if not self.email or not self.password:
            return False

        _LOGGER.warning("Token expired, attempting reauthentication...")
        self._token = None

        try:
            await self.authenticate(self.email, self.password)
            _LOGGER.info("Reauthentication successful")
            return True
        except Exception as e:
            _LOGGER.error(f"Reauthentication failed: {e}")
            return False

    async def authenticate(
        self, email: str | None = None, password: str | None = None
    ) -> dict[str, Any]:
        """
        Authenticate with Moogo API.

        Args:
            email: User email (uses instance email if not provided)
            password: User password (uses instance password if not provided)

        Returns:
            Dictionary containing authentication session data:
            {
                "token": str,
                "user_id": str,
                "email": str,
                "expires_at": str (ISO format),
                "ttl": int (seconds)
            }

        Raises:
            MoogoAuthError: If authentication fails
        """
        auth_email = email or self.email
        auth_password = password or self.password

        if not auth_email or not auth_password:
            raise MoogoAuthError("Email and password required")

        payload = {
            "email": auth_email,
            "password": auth_password,
            "keep": True,
        }

        response = await self._request("POST", "v1/user/login", authenticated=False, json=payload)

        user_data = response.get("data", {})
        self._token = user_data.get("token")
        self._user_id = user_data.get("userId")

        # Calculate token expiration
        ttl = user_data.get("ttl", 31536000)  # Default 1 year
        self._token_expires = datetime.now() + timedelta(seconds=ttl)

        _LOGGER.info(f"Authenticated user: {user_data.get('email')}")

        # Return session data for storage
        return {
            "token": self._token,
            "user_id": self._user_id,
            "email": user_data.get("email"),
            "expires_at": self._token_expires.isoformat() if self._token_expires else None,
            "ttl": ttl,
        }

    def get_auth_session(self) -> dict[str, Any]:
        """
        Get current authentication session data for storage.

        Returns:
            Dictionary containing session data:
            {
                "token": str | None,
                "user_id": str | None,
                "expires_at": str | None (ISO format),
                "is_authenticated": bool
            }

        Example:
            # Store session for later restoration
            session_data = client.get_auth_session()
            save_to_storage(session_data)

            # Later, restore the session
            client.set_auth_session(session_data)
        """
        return {
            "token": self._token,
            "user_id": self._user_id,
            "expires_at": self._token_expires.isoformat() if self._token_expires else None,
            "is_authenticated": self.is_authenticated,
        }

    def set_auth_session(self, session_data: dict[str, Any]) -> None:
        """
        Restore authentication session from stored data.

        This allows you to restore a previously authenticated session without
        re-authenticating, useful for persisting sessions across restarts.

        Args:
            session_data: Dictionary containing session data from get_auth_session()
                         or authenticate() response.

        Example:
            # Restore from stored session
            session_data = load_from_storage()
            client.set_auth_session(session_data)

            if client.is_authenticated:
                devices = await client.get_devices()
        """
        self._token = session_data.get("token")
        self._user_id = session_data.get("user_id")

        expires_at = session_data.get("expires_at")
        if expires_at:
            try:
                self._token_expires = datetime.fromisoformat(expires_at)
            except (ValueError, TypeError):
                _LOGGER.warning(f"Invalid expires_at format: {expires_at}")
                self._token_expires = None

        _LOGGER.info(f"Restored auth session for user: {self._user_id}")

    async def get_devices(self, force_refresh: bool = False) -> list[dict[str, Any]]:
        """
        Get list of user's devices.

        Args:
            force_refresh: Force refresh of cached device list

        Returns:
            List of device dictionaries
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        # Check cache
        now = datetime.now()
        if (
            not force_refresh
            and self._devices_cache
            and self._devices_cache_time
            and now - self._devices_cache_time < self._devices_cache_ttl
        ):
            return self._devices_cache

        response = await self._request("GET", "v1/devices")
        data = response.get("data", {})
        devices: list[dict[str, Any]] = data.get("items", []) if isinstance(data, dict) else []

        # Update cache
        self._devices_cache = devices
        self._devices_cache_time = now

        return devices

    async def get_device_status(self, device_id: str) -> DeviceStatus:
        """
        Get detailed device status.

        Args:
            device_id: Device ID

        Returns:
            DeviceStatus object
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        response = await self._request("GET", f"v1/devices/{device_id}")
        return DeviceStatus.from_dict(response.get("data", {}))

    @retry_with_backoff(max_attempts=5, initial_delay=2.0, backoff_factor=2.0)
    async def start_spray(self, device_id: str, mode: str | None = None) -> bool:
        """
        Start device spray/misting with retry logic and circuit breaker.

        Features:
        - Pre-flight check: Verifies device status before attempting
        - Retry with backoff: 5 attempts with 2s initial delay (up to 30-40s total)
        - Circuit breaker: Stops trying after 5 consecutive failures
        - Jitter: 0-1s randomization prevents thundering herd

        Args:
            device_id: Device ID
            mode: Optional spray mode ("manual", "schedule")

        Returns:
            True if successful

        Raises:
            MoogoAuthError: If not authenticated
            MoogoDeviceError: If device is persistently offline or operation fails
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        # Check circuit breaker
        if self._is_circuit_open(device_id):
            raise MoogoDeviceError(
                f"Device {device_id} circuit breaker is open. "
                f"Device appears persistently offline. "
                f"Retry after {self._circuit_breaker_timeout.total_seconds()}s cooldown."
            )

        # Pre-flight check: Get device status for better error messages
        try:
            status = await self.get_device_status(device_id)
            if not status.is_online:
                _LOGGER.warning(
                    f"Device {device_id} reports offline status. "
                    "Attempting start anyway (device may be waking up)..."
                )
        except Exception as e:
            _LOGGER.warning(f"Could not check device status before start: {e}")

        payload = {"mode": mode} if mode else {}

        try:
            await self._request("POST", f"v1/devices/{device_id}/start", json=payload)
            # Success - reset circuit breaker
            self._record_device_success(device_id)
            _LOGGER.info(f"Started spray for device {device_id}")
            return True
        except MoogoDeviceError as e:
            # Record failure for circuit breaker
            self._record_device_failure(device_id)
            raise MoogoDeviceError(f"Failed to start spray: {e}") from e
        except Exception as e:
            # Record failure for circuit breaker
            self._record_device_failure(device_id)
            raise MoogoDeviceError(f"Failed to start spray: {e}") from e

    @retry_with_backoff(max_attempts=5, initial_delay=2.0, backoff_factor=2.0)
    async def stop_spray(self, device_id: str) -> bool:
        """
        Stop device spray/misting with retry logic and circuit breaker.

        Features:
        - Pre-flight check: Verifies device status before attempting
        - Retry with backoff: 5 attempts with 2s initial delay (up to 30-40s total)
        - Circuit breaker: Stops trying after 5 consecutive failures
        - Jitter: 0-1s randomization prevents thundering herd

        Args:
            device_id: Device ID

        Returns:
            True if successful

        Raises:
            MoogoAuthError: If not authenticated
            MoogoDeviceError: If device is persistently offline or operation fails
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        # Check circuit breaker
        if self._is_circuit_open(device_id):
            raise MoogoDeviceError(
                f"Device {device_id} circuit breaker is open. "
                f"Device appears persistently offline. "
                f"Retry after {self._circuit_breaker_timeout.total_seconds()}s cooldown."
            )

        # Pre-flight check: Get device status for better error messages
        try:
            status = await self.get_device_status(device_id)
            if not status.is_online:
                _LOGGER.warning(
                    f"Device {device_id} reports offline status. "
                    "Attempting stop anyway (device may be waking up)..."
                )
        except Exception as e:
            _LOGGER.warning(f"Could not check device status before stop: {e}")

        try:
            await self._request("POST", f"v1/devices/{device_id}/stop", json={})
            # Success - reset circuit breaker
            self._record_device_success(device_id)
            _LOGGER.info(f"Stopped spray for device {device_id}")
            return True
        except MoogoDeviceError as e:
            # Record failure for circuit breaker
            self._record_device_failure(device_id)
            raise MoogoDeviceError(f"Failed to stop spray: {e}") from e
        except Exception as e:
            # Record failure for circuit breaker
            self._record_device_failure(device_id)
            raise MoogoDeviceError(f"Failed to stop spray: {e}") from e

    async def get_device_schedules(self, device_id: str) -> list[Schedule]:
        """
        Get device schedules.

        Args:
            device_id: Device ID

        Returns:
            List of Schedule objects
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        response = await self._request("GET", f"v1/devices/{device_id}/schedules")
        items = response.get("data", {}).get("items", [])
        return [Schedule.from_dict(item) for item in items]

    async def create_schedule(
        self,
        device_id: str,
        hour: int,
        minute: int,
        duration: int,
        repeat_set: str = "0,1,2,3,4,5,6",
        enabled: bool = True,
    ) -> bool:
        """
        Create a new spray schedule.

        Args:
            device_id: Device ID
            hour: Hour (0-23)
            minute: Minute (0-59)
            duration: Spray duration in seconds
            repeat_set: Days to repeat (0=Sunday, 6=Saturday)
            enabled: Whether to enable schedule immediately

        Returns:
            True if successful
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        payload = {
            "hour": hour,
            "minute": minute,
            "duration": duration,
            "repeatSet": repeat_set,
            "status": 1 if enabled else 0,
        }

        response = await self._request("POST", f"v1/devices/{device_id}/schedules", json=payload)
        success = response.get("code") == self.SUCCESS_CODE

        if success:
            _LOGGER.info(
                f"Created schedule for device {device_id}: {hour:02d}:{minute:02d} for {duration}s"
            )

        return success

    async def update_schedule(
        self,
        device_id: str,
        schedule_id: str,
        hour: int | None = None,
        minute: int | None = None,
        duration: int | None = None,
        repeat_set: str | None = None,
        enabled: bool | None = None,
    ) -> bool:
        """
        Update an existing schedule.

        Args:
            device_id: Device ID
            schedule_id: Schedule ID
            hour: Hour (0-23)
            minute: Minute (0-59)
            duration: Spray duration in seconds
            repeat_set: Days to repeat
            enabled: Whether schedule is enabled

        Returns:
            True if successful
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        payload: dict[str, Any] = {}
        if hour is not None:
            payload["hour"] = hour
        if minute is not None:
            payload["minute"] = minute
        if duration is not None:
            payload["duration"] = duration
        if repeat_set is not None:
            payload["repeatSet"] = repeat_set
        if enabled is not None:
            payload["status"] = 1 if enabled else 0

        response = await self._request(
            "PUT", f"v1/devices/{device_id}/schedules/{schedule_id}", json=payload
        )
        success = response.get("code") == self.SUCCESS_CODE

        if success:
            _LOGGER.info(f"Updated schedule {schedule_id} for device {device_id}")

        return success

    async def delete_schedule(self, device_id: str, schedule_id: str) -> bool:
        """
        Delete a spray schedule.

        Args:
            device_id: Device ID
            schedule_id: Schedule ID

        Returns:
            True if successful
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        response = await self._request("DELETE", f"v1/devices/{device_id}/schedules/{schedule_id}")
        success = response.get("code") == self.SUCCESS_CODE

        if success:
            _LOGGER.info(f"Deleted schedule {schedule_id} for device {device_id}")

        return success

    async def enable_schedule(self, device_id: str, schedule_id: str) -> bool:
        """
        Enable a specific schedule.

        Args:
            device_id: Device ID
            schedule_id: Schedule ID

        Returns:
            True if successful
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        response = await self._request(
            "POST", f"v1/devices/{device_id}/schedules/{schedule_id}/enable", json={}
        )
        success = response.get("code") == self.SUCCESS_CODE

        if success:
            _LOGGER.info(f"Enabled schedule {schedule_id} for device {device_id}")

        return success

    async def disable_schedule(self, device_id: str, schedule_id: str) -> bool:
        """
        Disable a specific schedule.

        Args:
            device_id: Device ID
            schedule_id: Schedule ID

        Returns:
            True if successful
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        response = await self._request(
            "POST", f"v1/devices/{device_id}/schedules/{schedule_id}/disable", json={}
        )
        success = response.get("code") == self.SUCCESS_CODE

        if success:
            _LOGGER.info(f"Disabled schedule {schedule_id} for device {device_id}")

        return success

    async def skip_schedule(self, device_id: str, schedule_id: str) -> bool:
        """
        Skip the next occurrence of a schedule.

        Args:
            device_id: Device ID
            schedule_id: Schedule ID

        Returns:
            True if successful
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        response = await self._request(
            "POST", f"v1/devices/{device_id}/schedules/{schedule_id}/skip", json={}
        )
        success = response.get("code") == self.SUCCESS_CODE

        if success:
            _LOGGER.info(
                f"Skipped next occurrence of schedule {schedule_id} for device {device_id}"
            )

        return success

    async def enable_all_schedules(self, device_id: str) -> bool:
        """
        Enable all schedules for a device.

        Args:
            device_id: Device ID

        Returns:
            True if successful
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        response = await self._request(
            "PUT", f"v1/devices/{device_id}/schedules/switch/open", json={}
        )
        success = response.get("code") == self.SUCCESS_CODE

        if success:
            _LOGGER.info(f"Enabled all schedules for device {device_id}")

        return success

    async def disable_all_schedules(self, device_id: str) -> bool:
        """
        Disable all schedules for a device.

        Args:
            device_id: Device ID

        Returns:
            True if successful
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        response = await self._request(
            "PUT", f"v1/devices/{device_id}/schedules/switch/close", json={}
        )
        success = response.get("code") == self.SUCCESS_CODE

        if success:
            _LOGGER.info(f"Disabled all schedules for device {device_id}")

        return success

    async def get_device_logs(
        self,
        device_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """
        Get device operation logs with optional date filtering and pagination.

        Args:
            device_id: Device ID
            start_date: Start date filter (YYYY-MM-DD format), optional
            end_date: End date filter (YYYY-MM-DD format), optional
            page: Page number (default: 1)
            page_size: Items per page (default: 20)

        Returns:
            Dictionary containing logs and pagination info
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        params: dict[str, Any] = {"page": page, "pageSize": page_size}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        response = await self._request("GET", f"v1/devices/{device_id}/logs", params=params)
        data: dict[str, Any] = response.get("data", {})
        return data

    async def get_device_config(self, device_id: str) -> dict[str, Any]:
        """
        Get device configuration settings.

        Args:
            device_id: Device ID

        Returns:
            Dictionary containing device configuration
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        response = await self._request("GET", f"v1/devices/{device_id}/configs")
        data: dict[str, Any] = response.get("data", {})
        return data

    async def set_device_config(self, device_id: str, config: dict[str, Any]) -> bool:
        """
        Update device configuration settings.

        Args:
            device_id: Device ID
            config: Configuration dictionary

        Returns:
            True if successful
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        response = await self._request("PUT", f"v1/devices/{device_id}/configs", json=config)
        success = response.get("code") == self.SUCCESS_CODE

        if success:
            _LOGGER.info(f"Updated configuration for device {device_id}")

        return success

    async def check_firmware_update(self, device_id: str) -> dict[str, Any]:
        """
        Check if firmware update is available for a device.

        Args:
            device_id: Device ID

        Returns:
            Dictionary containing update information (available, version, url, etc.)
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        response = await self._request("POST", f"v1/devices/{device_id}/otaCheck", json={})
        data: dict[str, Any] = response.get("data", {})
        return data

    async def trigger_firmware_update(self, device_id: str) -> bool:
        """
        Trigger OTA firmware update for a device.

        Args:
            device_id: Device ID

        Returns:
            True if update was triggered successfully
        """
        if not self.is_authenticated:
            raise MoogoAuthError("Authentication required")

        response = await self._request("POST", f"v1/devices/{device_id}/otaUpdate", json={})
        success = response.get("code") == self.SUCCESS_CODE

        if success:
            _LOGGER.info(f"Triggered firmware update for device {device_id}")

        return success

    async def get_liquid_types(self) -> list[dict[str, Any]]:
        """
        Get available liquid concentrate types (public endpoint).

        Returns:
            List of liquid type dictionaries
        """
        response = await self._request("GET", "v1/liquid", authenticated=False)
        data = response.get("data", [])
        return data if isinstance(data, list) else []

    async def get_recommended_schedules(self) -> list[dict[str, Any]]:
        """
        Get recommended spray schedules (public endpoint).

        Returns:
            List of schedule dictionaries
        """
        response = await self._request("GET", "v1/devices/schedules", authenticated=False)
        data = response.get("data", {})
        items = data.get("items", []) if isinstance(data, dict) else []
        return items if isinstance(items, list) else []

    async def test_connection(self) -> bool:
        """
        Test API connectivity.

        Returns:
            True if API is accessible
        """
        try:
            await self.get_liquid_types()
            if self.is_authenticated:
                await self.get_devices()
            return True
        except Exception as e:
            _LOGGER.error(f"Connection test failed: {e}")
            return False
