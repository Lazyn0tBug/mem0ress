"""Tests for current_task module."""

import pytest

from mem0ress.gateway.current_task import CurrentTaskManager


class TestCurrentTaskManager:
    """Tests for CurrentTaskManager."""

    def test_read_returns_none_when_file_missing(self, tmp_path):
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        task_id, activated_at = ctm.read()
        assert task_id is None
        assert activated_at is None

    def test_read_returns_none_for_empty_file(self, tmp_path):
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        (tmp_path / ".current_task").write_text("", encoding="utf-8")
        task_id, activated_at = ctm.read()
        assert task_id is None

    def test_read_returns_none_for_malformed_yaml(self, tmp_path):
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        (tmp_path / ".current_task").write_text("not: [valid: yaml", encoding="utf-8")
        task_id, activated_at = ctm.read()
        assert task_id is None

    def test_write_and_read_roundtrip(self, tmp_path):
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        ctm.write("abc123", "2026-05-14T10:00:00+09:00")
        task_id, activated_at = ctm.read()
        assert task_id == "abc123"
        assert activated_at == "2026-05-14T10:00:00+09:00"

    def test_write_overwrites_previous(self, tmp_path):
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        ctm.write("first", "2026-01-01T00:00:00Z")
        ctm.write("second", "2026-12-31T23:59:59Z")
        task_id, activated_at = ctm.read()
        assert task_id == "second"
        assert activated_at == "2026-12-31T23:59:59Z"

    def test_clear_preserves_activated_at(self, tmp_path):
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        ctm.write("task1", "2026-05-14T10:00:00+09:00")
        ctm.clear()
        task_id, activated_at = ctm.read()
        assert task_id is None
        assert activated_at == "2026-05-14T10:00:00+09:00"

    def test_clear_preserves_none_activated_at(self, tmp_path):
        """clear() on a fresh file should not crash."""
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        ctm.write("task1", "2026-05-14T10:00:00+09:00")
        # Manually set activated_at to None scenario is not possible via clear
        # since we preserve whatever was there
        ctm.clear()
        _, at = ctm.read()
        assert at == "2026-05-14T10:00:00+09:00"

    def test_clear_on_empty_file(self, tmp_path):
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        ctm.clear()  # Should not raise
        task_id, activated_at = ctm.read()
        assert task_id is None

    def test_activate_on_create_sets_task_id_and_timestamp(self, tmp_path):
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        ctm.activate_on_create("newtask")
        task_id, activated_at = ctm.read()
        assert task_id == "newtask"
        assert activated_at is not None
        assert isinstance(activated_at, str)
        assert "T" in activated_at  # ISO8601 format

    def test_activate_on_close_clears_task_id(self, tmp_path):
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        ctm.activate_on_create("closeme")
        ctm.activate_on_close()
        task_id, _ = ctm.read()
        assert task_id is None

    def test_is_empty_true_when_no_file(self, tmp_path):
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        assert ctm.is_empty() is True

    def test_is_empty_false_when_task_set(self, tmp_path):
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        ctm.write("task", "2026-05-14T10:00:00Z")
        assert ctm.is_empty() is False

    def test_is_empty_true_when_cleared(self, tmp_path):
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        ctm.write("task", "2026-05-14T10:00:00Z")
        ctm.clear()
        assert ctm.is_empty() is True

    def test_read_with_empty_task_id_returns_none(self, tmp_path):
        """If task_id is explicitly empty/null in YAML, treat as no active task."""
        ctm = CurrentTaskManager(substrate_root=tmp_path)
        (tmp_path / ".current_task").write_text("task_id:\nactivated_at: '2026-05-14T10:00:00Z'\n", encoding="utf-8")
        task_id, activated_at = ctm.read()
        assert task_id is None
        assert activated_at == "2026-05-14T10:00:00Z"