"""Tests for TaskInfoManager."""

from __future__ import annotations

from pathlib import Path

import pytest

from mem0ress.core.schema import TaskStatus
from mem0ress.gateway.task_info import TaskEntry, TaskInfoData, TaskInfoManager


class TestTaskInfoManager:
    """Tests for TaskInfoManager."""

    def test_read_returns_empty_state_when_file_missing(
        self, tmp_path: Path
    ) -> None:
        """Missing .task_info returns empty TaskInfoData."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        data = tim.read()
        assert data.current_task_id is None
        assert data.tasks == []

    def test_read_returns_empty_state_when_file_empty(
        self, tmp_path: Path
    ) -> None:
        """Empty .task_info returns empty TaskInfoData."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        (tmp_path / ".task_info").write_text("", encoding="utf-8")
        data = tim.read()
        assert data.current_task_id is None
        assert data.tasks == []

    def test_read_returns_empty_state_when_invalid_yaml(
        self, tmp_path: Path
    ) -> None:
        """Invalid YAML returns empty TaskInfoData."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        (tmp_path / ".task_info").write_text("not: [valid: yaml", encoding="utf-8")
        data = tim.read()
        assert data.current_task_id is None
        assert data.tasks == []

    def test_add_task_creates_entry(self, tmp_path: Path) -> None:
        """add_task creates new TaskEntry and sets as current."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        tim.add_task("abc123", ".cap/tasks/abc123")

        data = tim.read()
        assert data.current_task_id == "abc123"
        assert len(data.tasks) == 1
        assert data.tasks[0].task_id == "abc123"
        assert data.tasks[0].status == TaskStatus.CREATED
        assert data.tasks[0].path == ".cap/tasks/abc123"
        assert data.tasks[0].created_at is not None
        assert data.tasks[0].activated_at is not None

    def test_add_task_second_task_updates_current(
        self, tmp_path: Path
    ) -> None:
        """add_task sets new task as current, keeps old task in list."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        tim.add_task("abc123", ".cap/tasks/abc123")
        tim.add_task("xyz789", ".cap/tasks/xyz789")

        data = tim.read()
        assert data.current_task_id == "xyz789"
        assert len(data.tasks) == 2

    def test_update_task_status(self, tmp_path: Path) -> None:
        """update_task_status changes task status."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        tim.add_task("abc123", ".cap/tasks/abc123")
        tim.update_task_status("abc123", TaskStatus.IN_PROGRESS)

        data = tim.read()
        assert data.tasks[0].status == TaskStatus.IN_PROGRESS

    def test_update_task_status_raises_if_not_found(
        self, tmp_path: Path
    ) -> None:
        """update_task_status raises ValueError for unknown task_id."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        with pytest.raises(ValueError, match="Task not found"):
            tim.update_task_status("nonexistent", TaskStatus.IN_PROGRESS)

    def test_set_current_task(self, tmp_path: Path) -> None:
        """set_current_task updates current_task_id and activated_at."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        tim.add_task("abc123", ".cap/tasks/abc123")

        # Create second task
        tim.add_task("xyz789", ".cap/tasks/xyz789")

        # Switch back to first
        tim.set_current_task("abc123")

        data = tim.read()
        assert data.current_task_id == "abc123"
        # Find the entry
        for t in data.tasks:
            if t.task_id == "abc123":
                assert t.activated_at is not None

    def test_set_current_task_raises_if_not_found(self, tmp_path: Path) -> None:
        """set_current_task raises ValueError for unknown task_id."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        with pytest.raises(ValueError, match="Task not found"):
            tim.set_current_task("nonexistent")

    def test_get_current_task_id(self, tmp_path: Path) -> None:
        """get_current_task_id returns current task_id or None."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        assert tim.get_current_task_id() is None

        tim.add_task("abc123", ".cap/tasks/abc123")
        assert tim.get_current_task_id() == "abc123"

    def test_get_active_tasks_filters_completed_abandoned(
        self, tmp_path: Path
    ) -> None:
        """get_active_tasks excludes completed and abandoned tasks."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        tim.add_task("task1", ".cap/tasks/task1")
        tim.add_task("task2", ".cap/tasks/task2")
        tim.add_task("task3", ".cap/tasks/task3")

        tim.update_task_status("task2", TaskStatus.COMPLETED)
        tim.update_task_status("task3", TaskStatus.ABANDONED)

        active = tim.get_active_tasks()
        assert len(active) == 1
        assert active[0].task_id == "task1"

    def test_get_active_tasks_includes_created_and_in_progress(
        self, tmp_path: Path
    ) -> None:
        """get_active_tasks includes created and in-progress tasks."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        tim.add_task("task1", ".cap/tasks/task1")
        tim.update_task_status("task1", TaskStatus.IN_PROGRESS)

        active = tim.get_active_tasks()
        assert len(active) == 1
        assert active[0].task_id == "task1"
        assert active[0].status == TaskStatus.IN_PROGRESS

    def test_get_active_tasks_returns_copies(self, tmp_path: Path) -> None:
        """get_active_tasks returns copies, not the same object references."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        tim.add_task("task1", ".cap/tasks/task1")

        active = tim.get_active_tasks()
        # Verify it's a different object from internal state
        data = tim.read()
        assert active[0].task_id == data.tasks[0].task_id
        # But not the same object identity
        assert active[0] is not data.tasks[0]

    def test_concurrent_write_raises_conflict(self, tmp_path: Path) -> None:
        """Concurrent write to .task_info raises ConflictError via safe_write."""
        from mem0ress.substrate.fs import ConflictError, get_file_hash, safe_write

        # Create file with initial content
        path = tmp_path / ".task_info"
        initial_content = (
            "current_task_id: task1\n"
            "tasks:\n"
            "- activated_at: '2026-05-14T10:00:00+09:00'\n"
            "  created_at: '2026-05-14T10:00:00+09:00'\n"
            "  path: .cap/tasks/task1\n"
            "  status: created\n"
            "  task_id: task1\n"
        )
        path.write_text(initial_content)

        # Compute hash of initial content
        hash1 = get_file_hash(path)

        # Simulate another writer modified the file
        new_content = (
            "current_task_id: task2\n"
            "tasks:\n"
            "- activated_at: '2026-05-14T10:00:00+09:00'\n"
            "  created_at: '2026-05-14T10:00:00+09:00'\n"
            "  path: .cap/tasks/task1\n"
            "  status: created\n"
            "  task_id: task1\n"
            "- activated_at: '2026-05-15T10:00:00+09:00'\n"
            "  created_at: '2026-05-15T10:00:00+09:00'\n"
            "  path: .cap/tasks/task2\n"
            "  status: created\n"
            "  task_id: task2\n"
        )
        path.write_text(new_content)

        # Now try to write with the OLD hash - should fail
        with pytest.raises(ConflictError):
            safe_write(path, initial_content, hash1)


class TestTaskEntry:
    """Tests for TaskEntry Pydantic model."""

    def test_task_entry_fields(self) -> None:
        """TaskEntry stores all required fields."""
        entry = TaskEntry(
            task_id="abc123",
            status=TaskStatus.IN_PROGRESS,
            path=".cap/tasks/abc123",
            created_at="2026-05-14T10:00:00+09:00",
            activated_at="2026-05-16T10:00:00+09:00",
        )
        assert entry.task_id == "abc123"
        assert entry.status == TaskStatus.IN_PROGRESS
        assert entry.path == ".cap/tasks/abc123"
        assert entry.created_at == "2026-05-14T10:00:00+09:00"
        assert entry.activated_at == "2026-05-16T10:00:00+09:00"

    def test_task_entry_activated_at_optional(self) -> None:
        """TaskEntry.activated_at can be None."""
        entry = TaskEntry(
            task_id="abc123",
            status=TaskStatus.CREATED,
            path=".cap/tasks/abc123",
            created_at="2026-05-14T10:00:00+09:00",
        )
        assert entry.activated_at is None

    def test_task_entry_is_frozen(self) -> None:
        """TaskEntry is frozen and cannot be modified after creation."""
        entry = TaskEntry(
            task_id="abc123",
            status=TaskStatus.CREATED,
            path=".cap/tasks/abc123",
            created_at="2026-05-14T10:00:00+09:00",
        )
        with pytest.raises(Exception):  # Pydantic ValidationError
            entry.task_id = "tampered"


class TestTaskInfoData:
    """Tests for TaskInfoData Pydantic model."""

    def test_task_info_data_defaults(self) -> None:
        """TaskInfoData defaults to empty state."""
        data = TaskInfoData()
        assert data.current_task_id is None
        assert data.tasks == []

    def test_task_info_round_trip(self, tmp_path: Path) -> None:
        """TaskInfoData survives write-read round trip."""
        tim = TaskInfoManager(substrate_root=tmp_path)
        tim.add_task("abc123", ".cap/tasks/abc123")
        tim.add_task("xyz789", ".cap/tasks/xyz789")
        tim.update_task_status("abc123", TaskStatus.IN_PROGRESS)
        tim.set_current_task("xyz789")

        # Read it back
        data = tim.read()
        assert data.current_task_id == "xyz789"
        assert len(data.tasks) == 2

        # Verify status values
        for t in data.tasks:
            if t.task_id == "abc123":
                assert t.status == TaskStatus.IN_PROGRESS