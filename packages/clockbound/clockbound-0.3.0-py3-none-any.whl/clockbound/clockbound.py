# Shared memory segment to read to get time repeatably with low overhead
import mmap
from sys import byteorder
import time
from datetime import datetime, timedelta, timezone

from clockbound import errors


def next_b(sl: slice, size: int) -> slice:
    return slice(sl.stop, sl.stop + size)


SHM_PATH = "/var/run/clockbound/shm0"
V2_LEN = 20 * 4

# https://github.com/aws/clock-bound/blob/main/docs/PROTOCOL.md
F_MAG1 = slice(0, 4)  # 2x u32 Magic number
F_MAG2 = slice(4, 8)  # 2x u32 Magic number
F_SSZ = next_b(F_MAG2, 4)  # u32 Segment size
F_VER = next_b(F_SSZ, 2)  # u16 Version
F_GEN = next_b(F_VER, 2)  # u16 Generation
F_ASOF_S = next_b(F_GEN, 8)  # u64 As of time (s)
F_ASOF_NS = next_b(F_ASOF_S, 8)  # u64 As of time (ns)
F_VOIDA_S = next_b(F_ASOF_NS, 8)  # u64 Void after time (s)
F_VOIDA_NS = next_b(F_VOIDA_S, 8)  # u64 Void after time (ns)
F_BOUND = next_b(F_VOIDA_NS, 8)  # u64 Bound time (ns)
F_DISR = next_b(F_BOUND, 8)  # u64 Disruption marker
F_DRFT = next_b(F_DISR, 4)  # u32 Max Drift
F_STAT = next_b(F_DRFT, 4)  # u32 Clock status
F_DSP = next_b(F_STAT, 2)  # u16 Disruption support
F_PAD = next_b(F_DSP, 7)

assert F_PAD.stop == V2_LEN + 1, "Field length mismatch"

CLOCK_UNKNOWN = 0
CLOCK_SYNC = 1
CLOCK_FREERUN = 2
CLOCK_DISRUPTED = 3


class Snapshot:
    def __init__(self, data: bytes):
        self._data = data

    @property
    def magic1(self) -> int:
        return int.from_bytes(self._data[F_MAG1], byteorder)

    @property
    def magic2(self) -> int:
        return int.from_bytes(self._data[F_MAG2], byteorder)

    @property
    def segment_size(self) -> int:
        return int.from_bytes(self._data[F_SSZ], byteorder)

    @property
    def version(self) -> int:
        return int.from_bytes(self._data[F_VER], byteorder)

    @property
    def generation(self) -> int:
        return int.from_bytes(self._data[F_GEN], byteorder)

    @property
    def as_of_s(self) -> int:
        return int.from_bytes(self._data[F_ASOF_S], byteorder)

    @property
    def as_of_ns(self) -> int:
        return int.from_bytes(self._data[F_ASOF_NS], byteorder)

    @property
    def void_after_s(self) -> int:
        return int.from_bytes(self._data[F_VOIDA_S], byteorder)

    @property
    def void_after_ns(self) -> int:
        return int.from_bytes(self._data[F_VOIDA_NS], byteorder)

    @property
    def bound(self) -> int:
        return int.from_bytes(self._data[F_BOUND], byteorder)

    @property
    def disruption_marker(self) -> int:
        return int.from_bytes(self._data[F_DISR], byteorder)

    @property
    def max_drift(self) -> int:
        return int.from_bytes(self._data[F_DRFT], byteorder)

    @property
    def clock_status(self) -> int:
        return int.from_bytes(self._data[F_STAT], byteorder)

    @property
    def disruption_support(self) -> int:
        return int.from_bytes(self._data[F_DSP], byteorder)

    def as_dict(self):
        return {
            "magic1": self.magic1,
            "magic2": self.magic2,
            "segment_size": self.segment_size,
            "version": self.version,
            "generation": self.generation,
            "as_of_s": self.as_of_s,
            "as_of_ns": self.as_of_ns,
            "void_after_s": self.void_after_s,
            "void_after_ns": self.void_after_ns,
            "bound": self.bound,
            "disruption_marker": self.disruption_marker,
            "max_drift": self.max_drift,
            "clock_status": self.clock_status,
            "disruption_support": self.disruption_support,
        }


class Clockbound:
    def __init__(self, path: str | None = None):
        path = path or SHM_PATH
        try:
            self._clock = mmaped(path)
        except Exception as e:
            raise errors.ClockboundSourceError(f"Failed to read clockbound shm at {path}: {e}")

    def _snapshot(self) -> Snapshot:
        return Snapshot(self._clock.mmap[:V2_LEN])

    def snapshot(self) -> Snapshot:
        """Get a consistent snapshot of the shm clock bound data"""
        for i in range(10000):
            # We know we have a consistent snapshot if we have two in a row with the same
            # generation (no changes occurred, to prevent write tearing),
            # and the general is even (indicating not in the middle of a write)
            snap1, snap2 = self._snapshot(), self._snapshot()

            if snap1.generation % 2 == 0 and snap1.generation == snap2.generation:
                return snap1

        raise errors.ReadError("Failed to get consistent snapshot from clockbound shm")

    def now(self) -> "TimeBound":
        snap = self.snapshot()
        real = time.clock_gettime_ns(time.CLOCK_REALTIME)
        mono = time.clock_gettime_ns(time.CLOCK_MONOTONIC)

        if snap.clock_status != CLOCK_SYNC and snap.clock_status != CLOCK_FREERUN:
            raise errors.ClockStatusError("Clock is not synchronized; time bounds cannot be guaranteed.")

        void_after = snap.void_after_s * 1_000_000_000 + snap.void_after_ns
        as_of = snap.as_of_s * 1_000_000_000 + snap.as_of_ns

        if mono > void_after:
            raise errors.TimeVoidedError("Requested time is voided (past the void_after time).")

        # Calculate growth of error bound since as_of time
        # Since max drift is in ppb, we multiply the elapsed time (in ns) by max_drift and divide by 1e9
        drift_ns = (mono - as_of) * snap.max_drift // 1_000_000_000
        bound = snap.bound + drift_ns

        return TimeBound(earliest=real - bound, latest=real + bound)

    def close(self):
        self._clock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class TimeBound:
    """Represents a time bound with earliest and latest possible times."""

    def __init__(self, earliest: int, latest: int):
        self.earliest = earliest
        self.latest = latest

    @property
    def earliest_dt(self) -> datetime:
        """Return the earliest time as a datetime object, only widening the error bounds for rounding to microseconds."""
        dt = datetime.fromtimestamp(self.earliest // 1_000_000_000, tz=timezone.utc)
        leftover_ns = self.earliest % 1_000_000_000
        return dt.replace(microsecond=leftover_ns // 1_000)

    @property
    def latest_dt(self) -> datetime:
        """Return the latest time as a datetime object, only widening the error bounds for rounding to microseconds."""
        dt = datetime.fromtimestamp(self.latest // 1_000_000_000, tz=timezone.utc)
        leftover_ns = self.latest % 1_000_000_000
        leftover_us = leftover_ns % 1_000
        return dt.replace(microsecond=(leftover_ns // 1_000) + (1 if leftover_us > 0 else 0))

    @property
    def error_ns(self) -> int:
        """Return the error in nanoseconds."""
        return (self.latest - self.earliest) // 2

    @property
    def error_td(self) -> timedelta:
        """Return the error bound as a timedelta."""
        leftover_ns = self.error_ns % 1_000
        return timedelta(microseconds=(self.error_ns // 1_000) + (1 if leftover_ns > 0 else 0))

    def __str__(self):
        midpoint = (self.earliest + self.latest) // 2
        error = (self.latest - self.earliest) // 2
        error_unit = "ns"

        midpoint_dt = datetime.fromtimestamp(midpoint // 1_000_000_000, tz=timezone.utc).replace(
            microsecond=(midpoint % 1_000_000_000) // 1_000
        )

        if error >= 1_000_000:
            error = error // 1_000_000
            error_unit = "ms"
        elif error >= 1_000:
            error = error // 1_000
            error_unit = "µs"

        return f"{midpoint_dt.isoformat()} ± {error} {error_unit}"


class mmaped:
    def __init__(self, filename: str):
        self.fp = open(filename, "rb")
        self.mmap = mmap.mmap(self.fp.fileno(), 0, access=mmap.ACCESS_READ)

    def close(self):
        self.mmap.close()
        self.fp.close()
