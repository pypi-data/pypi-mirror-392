"""Exception classes for Moogo API client."""


class MoogoAPIError(Exception):
    """Base exception for Moogo API errors."""


class MoogoAuthError(MoogoAPIError):
    """Authentication related errors."""


class MoogoDeviceError(MoogoAPIError):
    """Device operation errors."""


class MoogoRateLimitError(MoogoAPIError):
    """Rate limiting errors (24-hour lockout)."""
