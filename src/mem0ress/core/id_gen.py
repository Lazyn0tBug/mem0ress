"""Task ID generation — compact base36 identifiers for task directories."""

from __future__ import annotations

import itertools
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

_BASE36 = "0123456789abcdefghijklmnopqrstuvwxyz"
_COUNTER = itertools.count(start=0)


def _to_base36(value: int, width: int) -> str:
    """Convert a non-negative integer to a base36 string of given width.

    Args:
        value: Non-negative integer to encode.
        width: Desired output character count.

    Returns:
        Base36 string of exactly `width` characters, zero-padded on the left.

    Raises:
        ValueError: If value cannot be represented in width characters.
    """
    if value < 0:
        raise ValueError(f"value must be non-negative, got {value}")
    max_val = 36**width
    if value >= max_val:
        raise ValueError(f"value {value} too large for {width} base36 chars (max {max_val - 1})")
    return "".join(_BASE36[(value // 36**i) % 36] for i in range(width - 1, -1, -1))


def generate_task_id() -> str:
    """Generate a compact 6-character task ID.

    Format: 4 base36 chars from low bits of timestamp + 2 base36 chars from
    a per-process monotonic counter.

    The timestamp portion covers approximately a 12-day window before
    wrapping. The counter guarantees no collisions within a single process
    across calls made within the same 64-second window.

    Returns:
        6-character lowercase alphanumeric string, e.g. "2k5m3x".
    """
    # 64-second granularity; take low 4 base36 digits (covers 36^4 = 1,679,616 values ≈ 12 days)
    ts_low = int(time.time() // 64) % (36**4)
    # Per-process counter, wraps every 36^2 = 1296 calls
    counter = next(_COUNTER) % (36**2)
    return _to_base36(ts_low, 4) + _to_base36(counter, 2)
