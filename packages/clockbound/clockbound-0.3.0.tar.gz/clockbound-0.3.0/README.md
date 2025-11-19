# Clockbound Python Library

This a library to consume [ClockBound](https://github.com/aws/clock-bound) time error bounds in pure Python.
Instead of operating on timestamps directly, you can call `clockbound.now()` to get a `clockbound.TimeBound` object that represents the earliest and latest possible times according to ClockBound.
You can then use two `TimeBound` objects to deconflict events from eachother.

This allows you to implement interesting algorithms that do an end-run around several distributed systems problems, similar to how [Google uses TrueTime in Spanner](https://research.google/pubs/spanner-truetime-and-the-cap-theorem/).

Any system that uses chrony can use ClockBound, and therefore this library, to get time bounds with very low overhead.
The error bounds will narrow as your chrony time source is improved, with the good results obtained by using the Amazon Time Sync Service NTP Service (automatically used on AWS EC2 instances).
Going beyond that and using the PTP Hardware Clock will yield the best results.

Minimizing your NTP error is outside of the scope of this project, but you can expect the following bounds in practice:

* PC with internet NTP: +/- 10-50 ms
* EC2 using default Amazon Time Sync Service: +/- 500 µs - 2 ms
* EC2 with PTP Hardware Clock: "+/- 40 µs"


## API

To use this library, you need the ClockBound daemon running on your system.
This library will not work without it providing time bounds via shared memory.

For most purposes, you can use the `clockbound.now()` function to get `TimeBound` objects from
the default global `Clockbound` instance.
This library will construct the global on first use.

```python
import clockbound
from clockbound import TimeBound

tb: TimeBound = clockbound.now()
print(str(tb))

# Output:
# 2025-11-17T06:37:47.679501+00:00 ± 506 µs
```

`TimeBound` objects have the following properties:

* `earliest`: (int) The earliest possible time in nanoseconds since the epoch.
* `latest`: (int) The latest possible time in nanoseconds since the epoch.
* `error_ns`: (int) The error in nanoseconds.
* `earliest_dt`: (datetime tz-aware UTC) A convenience accessor to get the earliest time as a datetime rounded down to microseconds.
* `latest_dt`: (datetime tz-aware UTC) A convenience accessor to get the latest time as a datetime rounded _up_ to microseconds.
* `__str__()`: A string representation with the error margin included.


### Errors

All errors subclass `clockbound.ClockboundError`. There are error subclasses for finer grained error handling, but they are not exposed as part of the public API at this time.

You can get errors for the following reasons:

* The daemon is not running or shared memory cannot be accessed.
* ClockBound reports that the clock is not synchronized, and we cannot give out guaranteed time bounds.
* The requested time is voided (past the void_after time). This should be rare in practice, but can happen if the daemon crashes or is really slow to restart. We cannot get fresh time bounds and the last known bounds are now invalid.


## Performance

Calling `clockbound.now()` is acceptable fast, allowing 350,000 calls per second on a fairly modest consumer machine.
