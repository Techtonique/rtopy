"""Custom exceptions for rtopy."""


class RtopyError(Exception):
    """Base exception for rtopy errors."""

    pass


class RNotFoundError(RtopyError):
    """Raised when R is not found in PATH."""

    pass


class RExecutionError(RtopyError):
    """Raised when R script execution fails."""

    pass


class RTypeError(RtopyError, TypeError):
    """Raised when type conversion fails."""

    pass
