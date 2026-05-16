"""TaskInfoManager - manages .task_info file with centralized task registry.

.task_info stores ALL tasks centrally, replacing .current_task's single-task focus.
This enables the list command to run without filesystem scanning.

YAML format:
    current_task_id: "2k5m3x"
    tasks:
      - task_id: "2k5m3x"
        status: "in-progress"
        path: ".cap/tasks/2k5m3x"
        created_at: "2026-05-14T10:00:00+09:00"
        activated_at: "2026-05-16T10:00:00+09:00"
      - task_id: "a3x7br"
        status: "created"
        path: ".cap/tasks/a3x7br"
        created_at: "2026-05-15T08:00:00+09:00"
        activated_at: null

All write operations use safe_write for optimistic-lock protection.
"""

from __future__ import annotations

import datetime
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from mem0ress.core.constants import DEFAULT_SUBSTRATE_ROOT
from mem0ress.core.schema import TaskStatus
from mem0ress.substrate.fs import get_file_hash, safe_write


class TaskEntry(BaseModel):
    """A single task entry in .task_info."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    task_id: str = Field(description="任务标识符")
    status: TaskStatus = Field(description="任务状态")
    path: str = Field(description="任务目录相对路径")
    created_at: str = Field(description="创建时间 ISO8601")
    activated_at: str | None = Field(default=None, description="激活为当前任务的时间")


class TaskInfoData(BaseModel):
    """Full .task_info contents."""

    current_task_id: str | None = Field(default=None, description="当前任务 ID")
    tasks: list[TaskEntry] = Field(default_factory=list)


class TaskInfoManager:
    """Manages the .task_info centralized task registry.

    All write operations use safe_write for optimistic-lock protection.
    """

    def __init__(self, substrate_root: Path = Path(DEFAULT_SUBSTRATE_ROOT)) -> None:
        """Initialize TaskInfoManager.

        Args:
            substrate_root: Root directory for cognitive substrate (default: .cap)
        """
        self._task_info_path = substrate_root / ".task_info"

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    def read(self) -> TaskInfoData:
        """Read the full .task_info file.

        Returns:
            TaskInfoData with current_task_id and all tasks.
            Returns empty state (current_task_id=None, tasks=[]) if file
            does not exist, is empty, or cannot be parsed.
        """
        path = self._task_info_path
        if not path.exists():
            return TaskInfoData()

        try:
            content = path.read_text(encoding="utf-8").strip()
            if not content:
                return TaskInfoData()
            raw = yaml.safe_load(content)
            if not isinstance(raw, dict):
                return TaskInfoData()
            return self._deserialize(raw)
        except (yaml.YAMLError, OSError):
            return TaskInfoData()

    def _deserialize(self, raw: dict) -> TaskInfoData:
        """Parse raw YAML dict to TaskInfoData."""
        current_task_id = raw.get("current_task_id")
        tasks_raw = raw.get("tasks", [])

        tasks: list[TaskEntry] = []
        if isinstance(tasks_raw, list):
            for t in tasks_raw:
                if isinstance(t, dict):
                    status_str = t.get("status", "")
                    try:
                        status = TaskStatus(status_str) if status_str else TaskStatus.CREATED
                    except ValueError:
                        status = TaskStatus.CREATED

                    tasks.append(
                        TaskEntry(
                            task_id=str(t.get("task_id", "")),
                            status=status,
                            path=str(t.get("path", "")),
                            created_at=str(t.get("created_at", "")),
                            activated_at=t.get("activated_at"),
                        )
                    )

        return TaskInfoData(current_task_id=current_task_id, tasks=tasks)

    # -------------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------------

    def _write(self, data: TaskInfoData) -> None:
        """Write the full .task_info file.

        Uses safe_write for optimistic lock protection.

        Args:
            data: TaskInfoData to serialize and write

        Raises:
            ConflictError: If file was modified concurrently during write
        """
        path = self._task_info_path
        content = self._serialize(data)

        # Optimistic lock: compute expected hash before write
        expected_hash = get_file_hash(path) if path.exists() else ""
        safe_write(path, content, expected_hash)

    def _serialize(self, data: TaskInfoData) -> str:
        """Serialize TaskInfoData to YAML string using yaml.dump."""
        tasks_list = []
        for t in data.tasks:
            tasks_list.append(
                {
                    "task_id": t.task_id,
                    "status": t.status.value,
                    "path": t.path,
                    "created_at": t.created_at,
                    "activated_at": t.activated_at,
                }
            )

        payload = {
            "current_task_id": data.current_task_id,
            "tasks": tasks_list,
        }
        return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)

    # -------------------------------------------------------------------------
    # Task operations
    # -------------------------------------------------------------------------

    def add_task(self, task_id: str, path: str) -> None:
        """Add a new task and set it as current.

        Args:
            task_id: Unique task identifier
            path: Relative path to task directory

        Raises:
            ConflictError: If file was modified concurrently during write
        """
        data = self.read()
        created_at = datetime.datetime.now(datetime.UTC).isoformat()
        new_entry = TaskEntry(
            task_id=task_id,
            status=TaskStatus.CREATED,
            path=path,
            created_at=created_at,
            activated_at=created_at,
        )
        data.tasks.append(new_entry)
        data.current_task_id = task_id
        self._write(data)

    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """Update a task's status.

        Args:
            task_id: Task to update
            status: New status

        Raises:
            ValueError: If task not found
            ConflictError: If file was modified concurrently during write
        """
        data = self.read()
        for task in data.tasks:
            if task.task_id == task_id:
                # Create new TaskEntry with updated status (frozen model)
                updated = TaskEntry(
                    task_id=task.task_id,
                    status=status,
                    path=task.path,
                    created_at=task.created_at,
                    activated_at=task.activated_at,
                )
                idx = data.tasks.index(task)
                data.tasks[idx] = updated
                self._write(data)
                return
        raise ValueError(f"Task not found: {task_id}")

    def set_current_task(self, task_id: str) -> None:
        """Set the current task (updates current_task_id + activated_at).

        Args:
            task_id: Task to set as current

        Raises:
            ValueError: If task not found
            ConflictError: If file was modified concurrently during write
        """
        data = self.read()
        activated_at = datetime.datetime.now(datetime.UTC).isoformat()
        for i, task in enumerate(data.tasks):
            if task.task_id == task_id:
                # Create new TaskEntry with updated activated_at (frozen model)
                updated = TaskEntry(
                    task_id=task.task_id,
                    status=task.status,
                    path=task.path,
                    created_at=task.created_at,
                    activated_at=activated_at,
                )
                data.tasks[i] = updated
                data.current_task_id = task_id
                self._write(data)
                return
        raise ValueError(f"Task not found: {task_id}")

    def get_current_task_id(self) -> str | None:
        """Get the current task ID.

        Returns:
            Current task_id or None if no current task.
        """
        return self.read().current_task_id

    def get_active_tasks(self) -> list[TaskEntry]:
        """Get all non-completed, non-abandoned tasks.

        Returns:
            List of TaskEntry objects (copies) with status not in (completed, abandoned).
        """
        data = self.read()
        inactive = {TaskStatus.COMPLETED, TaskStatus.ABANDONED}
        return [t.model_copy(deep=False) for t in data.tasks if t.status not in inactive]
