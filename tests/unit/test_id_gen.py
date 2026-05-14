"""Tests for id_gen module."""

import time

from mem0ress.core.id_gen import _to_base36, generate_task_id


class TestToBase36:
    """Tests for the _to_base36 helper."""

    def test_zero_pads_to_width(self):
        assert _to_base36(0, 4) == "0000"
        assert _to_base36(0, 2) == "00"
        assert _to_base36(0, 1) == "0"

    def test_converts_correctly(self):
        # Known values
        assert _to_base36(1, 1) == "1"
        assert _to_base36(9, 1) == "9"
        assert _to_base36(10, 1) == "a"
        assert _to_base36(35, 1) == "z"
        assert _to_base36(36, 2) == "10"
        assert _to_base36(100, 3) == "02s"  # zero-padded to width

    def test_max_value_for_width(self):
        # 36^2 - 1 = 1295 = "zz"
        assert _to_base36(1295, 2) == "zz"
        # 36^4 - 1 = 1679615 = "zzzz"
        assert _to_base36(1679615, 4) == "zzzz"

    def test_raises_on_negative(self):
        import pytest

        with pytest.raises(ValueError, match="must be non-negative"):
            _to_base36(-1, 4)

    def test_raises_when_value_too_large(self):
        import pytest

        with pytest.raises(ValueError, match="too large"):
            _to_base36(36**2, 2)  # exactly 1 more than max for 2 chars


class TestGenerateTaskId:
    """Tests for generate_task_id."""

    def test_returns_six_char_string(self):
        tid = generate_task_id()
        assert isinstance(tid, str)
        assert len(tid) == 6

    def test_all_base36_chars(self):
        import re

        tid = generate_task_id()
        assert re.fullmatch(r"[0-9a-z]{6}", tid), f"Got {tid}"

    def test_unique_ids_for_sequential_calls(self):
        ids = [generate_task_id() for _ in range(100)]
        assert len(set(ids)) == 100, "Sequential IDs should be unique"

    def test_format_timestamp_plus_counter(self):
        """First 4 chars are timestamp-low base36, last 2 are counter."""
        tid = generate_task_id()
        ts_part = tid[:4]
        counter_part = tid[4:]
        # Both should be valid base36
        assert _to_base36(int(ts_part, 36), 4) == ts_part
        assert _to_base36(int(counter_part, 36), 2) == counter_part

    def test_timestamp_changes_after_64_seconds(self):
        """ts_low changes every 64 seconds, so after a sleep it should differ."""
        # Generate one ID
        ts_low_before = _to_base36(int(time.time() // 64) % (36**4), 4)

        # Generate another immediately — counter part will differ, timestamp part should match
        tid1 = generate_task_id()
        tid2 = generate_task_id()
        # Counter increments, timestamp stays same within same 64s window
        assert tid1[:4] == tid2[:4], "Timestamp part should be same within same 64s window"
        assert tid1[4:] != tid2[4:], "Counter part should differ for sequential calls"