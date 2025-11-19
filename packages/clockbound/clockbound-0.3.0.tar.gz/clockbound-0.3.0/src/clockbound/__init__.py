from clockbound.clockbound import Clockbound, Snapshot as Snapshot, TimeBound
from clockbound.errors import ClockboundError as ClockboundError

_cb: Clockbound | None = None


def now() -> TimeBound:
    """Get the current time bound"""
    global _cb
    if _cb is None:
        _cb = Clockbound()
    return _cb.now()
