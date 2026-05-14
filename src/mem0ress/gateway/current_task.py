"""Current task pointer — tracks the active task via .current_task file.

YAML format:
    task_id: "2k5m3x"
    activated_at: "2026-05-14T10:00:00+09:00"

The activated_at is preserved across close() calls to allow safe detection
of stale pointers. On create, if task_id is non-empty, a warning is logged.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    pass


class CurrentTaskManager:
    """Manages the .current_task pointer file.

    All write operations use safe_write for optimistic-lock protection.
    """

    def __init__(self, substrate_root: Path = Path(".mem0ress")) -> None:
        """Initialize CurrentTaskManager.

        Args:
            substrate_root: Root directory for cognitive substrate (default: .mem0ress)
        """
        self.substrate_root = substrate_root
        self._current_task_path = substrate_root / ".current_task"

    def _path(self) -> Path:
        """Return path to .current_task file."""
        return self._current_task_path

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    def read(self) -> tuple[str | None, str | None]:
        """Read the current task pointer.

        Returns:
            Tuple of (task_id, activated_at). Returns (None, None) if the file
            does not exist, is empty, or cannot be parsed.
        """
        path = self._path()
        if not path.exists():
            return None, None

        try:
            content = path.read_text(encoding="utf-8").strip()
            if not content:
                return None, None
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                return None, None
            task_id = data.get("task_id")
            activated_at = data.get("activated_at")
            # Return None if task_id is empty string
            if task_id is None or task_id == "":
                return None, activated_at
            return task_id, activated_at
        except (yaml.YAMLError, OSError):
            return None, None

    # -------------------------------------------------------------------------
    # Write (full replace)
    # -------------------------------------------------------------------------

    def write(self, task_id: str, activated_at: str) -> None:
        """Write the full pointer file.

        Uses safe_write for optimistic lock protection.

        Args:
            task_id: Task identifier
            activated_at: ISO8601 timestamp string
        """
        from mem0ress.substrate.fs import get_file_hash, safe_write

        path = self._path()
        if task_id:
            content = f"task_id: {task_id}\nactivated_at: {activated_at}\n"
        else:
            content = f"task_id:\nactivated_at: {activated_at}\n"

        # Optimistic lock: compute expected hash before write
        expected_hash = get_file_hash(path) if path.exists() else ""
        safe_write(path, content, expected_hash)

    # -------------------------------------------------------------------------
    # Clear (task_id to null, preserve activated_at)
    # -------------------------------------------------------------------------

    def clear(self) -> None:
        """Clear task_id, preserve activated_at for stale-pointer detection.

        Writes task_id as empty string, keeping activated_at for audit trail.
        """
        _task_id, activated_at = self.read()
        # Preserve activated_at if available
        path = self._path()
        content = f"task_id:\nactivated_at: {activated_at}\n"
        from mem0ress.substrate.fs import get_file_hash, safe_write

        expected_hash = get_file_hash(path) if path.exists() else ""
        safe_write(path, content, expected_hash)

    # -------------------------------------------------------------------------
    # Convenience helpers
    # -------------------------------------------------------------------------

    def activate_on_create(self, task_id: str) -> None:
        """Write task_id and current timestamp for newly created task.

        Args:
            task_id: Task identifier (already validated as non-empty)
        """
        activated_at = datetime.datetime.now(datetime.UTC).isoformat()
        self.write(task_id, activated_at)

    def activate_on_close(self) -> None:
        """Clear task_id on close, preserving activated_at."""
        self.clear()

    def is_empty(self) -> bool:
        """Return True if there is no active task (task_id is None or "")."""
        task_id, _ = self.read()
        return task_id is None or task_id == ""
