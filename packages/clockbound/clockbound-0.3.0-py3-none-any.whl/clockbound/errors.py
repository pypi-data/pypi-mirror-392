class ClockboundError(Exception):
    pass


class ReadError(ClockboundError):
    """Raised when a read from the clockbound shm fails."""

    pass


class ClockboundSourceError(ClockboundError):
    """Raised when the clockbound source is missing."""


class TimeConstructionError(ClockboundError):
    pass


class ClockStatusError(TimeConstructionError):
    """Raised when the clock is not synchronized and time bounds cannot be guaranteed."""

    pass


class TimeVoidedError(TimeConstructionError):
    """Raised when the requested time is voided (past the void_after time)."""

    pass
