"""TaskService implementation - concrete implementation of TaskServiceProtocol."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mem0ress.harness import HarnessResult

from mem0ress.core.schema import (
    CognitiveTriad,
    Requirement,
    TaskManifest,
    TaskStatus,
    TodoItem,
)
from mem0ress.substrate.fs import get_file_hash, safe_write
from mem0ress.substrate.parser import SubstrateParser


class TaskExistsError(Exception):
    """Raised when attempting to create a task that already exists."""

    pass


class TaskServiceImpl:
    """TaskService implementation with optimistic locking."""

    def __init__(self, substrate_root: Path = Path(".mem0ress")):
        """Initialize TaskService.

        Args:
            substrate_root: Root directory for cognitive substrate (default: .mem0ress)
        """
        self.substrate_root = substrate_root
        self.tasks_dir = substrate_root / "tasks"

    def _task_index_path(self, task_id: str) -> Path:
        """Get path to task's task.md."""
        return self.tasks_dir / task_id / "task.md"

    def create_task(self, task_id: str, picture: str) -> TaskManifest:
        """Create a new task with given ID and picture."""
        task_dir = self.tasks_dir / task_id
        index_path = task_dir / "task.md"

        if index_path.exists():
            raise TaskExistsError(f"Task '{task_id}' already exists")

        # Create directory structure
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "references").mkdir(exist_ok=True)

        # Create initial manifest
        manifest = TaskManifest(
            id=task_id,
            type="task",
            status=TaskStatus.CREATED,
            cognitive_triad=CognitiveTriad(
                picture=picture,
                requirements=[],
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[TodoItem(text="梳理具体执行步骤", done=False)],
        )

        # Write initial file
        content = SubstrateParser.serialize_manifest(manifest, index_path)
        index_path.write_text(content, encoding="utf-8")

        return manifest

    def get_task(self, task_id: str) -> TaskManifest:
        """Get task by ID."""
        index_path = self._task_index_path(task_id)
        if not index_path.exists():
            raise FileNotFoundError(f"Task '{task_id}' does not exist")
        return SubstrateParser.parse_manifest(index_path)

    def update_todo(self, task_id: str, index: int, done: bool) -> TaskManifest:
        """Update todo completion status."""
        index_path = self._task_index_path(task_id)
        if not index_path.exists():
            raise FileNotFoundError(f"Task '{task_id}' does not exist")

        # Read current state
        manifest = SubstrateParser.parse_manifest(index_path)
        expected_hash = get_file_hash(index_path)

        # Update todo
        if index < 0 or index >= len(manifest.todos):
            raise IndexError(f"Todo index {index} out of range (0-{len(manifest.todos) - 1})")

        # Create new todos list with updated item (frozen model requires new instance)
        new_todos = []
        for i, todo in enumerate(manifest.todos):
            if i == index:
                new_todos.append(TodoItem(text=todo.text, done=done))
            else:
                new_todos.append(todo)

        updated_manifest = TaskManifest(
            id=manifest.id,
            type=manifest.type,
            status=manifest.status,
            cognitive_triad=manifest.cognitive_triad,
            gotcha_refs=manifest.gotcha_refs,
            todos=new_todos,
        )

        # Write with optimistic lock
        content = SubstrateParser.serialize_manifest(updated_manifest, index_path)
        safe_write(index_path, content, expected_hash)

        return updated_manifest

    def update_cognitive_triad(
        self,
        task_id: str,
        picture: str,
        requirements: list[Requirement],
        constraints: list[str],
    ) -> TaskManifest:
        """Update the cognitive triad (picture, requirements, constraints)."""
        index_path = self._task_index_path(task_id)
        if not index_path.exists():
            raise FileNotFoundError(f"Task '{task_id}' does not exist")

        # Read current state
        manifest = SubstrateParser.parse_manifest(index_path)
        expected_hash = get_file_hash(index_path)

        # Update cognitive triad
        updated_manifest = TaskManifest(
            id=manifest.id,
            type=manifest.type,
            status=manifest.status,
            cognitive_triad=CognitiveTriad(
                picture=picture,
                requirements=requirements,
                constraints=constraints,
            ),
            gotcha_refs=manifest.gotcha_refs,
            todos=manifest.todos,
        )

        # Write with optimistic lock
        content = SubstrateParser.serialize_manifest(updated_manifest, index_path)
        safe_write(index_path, content, expected_hash)

        return updated_manifest

    def get_all_tasks(self) -> list[TaskManifest]:
        """Get all tasks in the substrate."""
        if not self.tasks_dir.exists():
            return []

        manifests = []
        for index_path in self.tasks_dir.rglob("task.md"):
            try:
                manifest = SubstrateParser.parse_manifest(index_path)
                manifests.append(manifest)
            except Exception:
                continue

        return manifests

    def delete_task(self, task_id: str) -> None:
        """Delete a task and all its files."""
        task_dir = self.tasks_dir / task_id
        if not task_dir.exists():
            raise FileNotFoundError(f"Task '{task_id}' does not exist")

        shutil.rmtree(task_dir)

    def add_todo(self, task_id: str, text: str) -> TaskManifest:
        """Add a new todo to task."""
        index_path = self._task_index_path(task_id)
        if not index_path.exists():
            raise FileNotFoundError(f"Task '{task_id}' does not exist")

        # Read current state
        manifest = SubstrateParser.parse_manifest(index_path)
        expected_hash = get_file_hash(index_path)

        # Add new todo
        updated_manifest = TaskManifest(
            id=manifest.id,
            type=manifest.type,
            status=manifest.status,
            cognitive_triad=manifest.cognitive_triad,
            gotcha_refs=manifest.gotcha_refs,
            todos=manifest.todos + [TodoItem(text=text, done=False)],
        )

        # Write with optimistic lock
        content = SubstrateParser.serialize_manifest(updated_manifest, index_path)
        safe_write(index_path, content, expected_hash)

        return updated_manifest

    def remove_todo(self, task_id: str, index: int) -> TaskManifest:
        """Remove a todo from task."""
        index_path = self._task_index_path(task_id)
        if not index_path.exists():
            raise FileNotFoundError(f"Task '{task_id}' does not exist")

        # Read current state
        manifest = SubstrateParser.parse_manifest(index_path)
        expected_hash = get_file_hash(index_path)

        # Validate index
        if index < 0 or index >= len(manifest.todos):
            raise IndexError(f"Todo index {index} out of range (0-{len(manifest.todos) - 1})")

        # Remove todo
        updated_manifest = TaskManifest(
            id=manifest.id,
            type=manifest.type,
            status=manifest.status,
            cognitive_triad=manifest.cognitive_triad,
            gotcha_refs=manifest.gotcha_refs,
            todos=manifest.todos[:index] + manifest.todos[index + 1 :],
        )

        # Write with optimistic lock
        content = SubstrateParser.serialize_manifest(updated_manifest, index_path)
        safe_write(index_path, content, expected_hash)

        return updated_manifest

    def complete_task(self, task_id: str) -> TaskManifest:
        """Mark a task as COMPLETED.

        Args:
            task_id: Task identifier

        Returns:
            Updated TaskManifest with status COMPLETED

        Raises:
            FileNotFoundError: If task does not exist
            ConflictError: If file was modified concurrently
        """
        index_path = self._task_index_path(task_id)
        if not index_path.exists():
            raise FileNotFoundError(f"Task '{task_id}' does not exist")

        manifest = SubstrateParser.parse_manifest(index_path)
        expected_hash = get_file_hash(index_path)

        updated_manifest = TaskManifest(
            id=manifest.id,
            type=manifest.type,
            status=TaskStatus.COMPLETED,
            cognitive_triad=manifest.cognitive_triad,
            gotcha_refs=manifest.gotcha_refs,
            todos=manifest.todos,
        )

        content = SubstrateParser.serialize_manifest(updated_manifest, index_path)
        safe_write(index_path, content, expected_hash)

        return updated_manifest

    def abandon_task(self, task_id: str) -> TaskManifest:
        """Mark a task as ABANDONED.

        Args:
            task_id: Task identifier

        Returns:
            Updated TaskManifest with status ABANDONED

        Raises:
            FileNotFoundError: If task does not exist
            ConflictError: If file was modified concurrently
        """
        index_path = self._task_index_path(task_id)
        if not index_path.exists():
            raise FileNotFoundError(f"Task '{task_id}' does not exist")

        manifest = SubstrateParser.parse_manifest(index_path)
        expected_hash = get_file_hash(index_path)

        updated_manifest = TaskManifest(
            id=manifest.id,
            type=manifest.type,
            status=TaskStatus.ABANDONED,
            cognitive_triad=manifest.cognitive_triad,
            gotcha_refs=manifest.gotcha_refs,
            todos=manifest.todos,
        )

        content = SubstrateParser.serialize_manifest(updated_manifest, index_path)
        safe_write(index_path, content, expected_hash)

        return updated_manifest

    def update_session(self, task_id: str, content: str) -> None:
        """Append a turn snapshot to session.md.

        Each snapshot records what happened in a turn, preserving the
        "long task memory" that an Agent needs to resume after context switch.

        Args:
            task_id: Task identifier
            content: Free-form text describing this turn's work

        Raises:
            FileNotFoundError: If task does not exist
        """
        task_dir = self.tasks_dir / task_id
        if not task_dir.exists():
            raise FileNotFoundError(f"Task '{task_id}' does not exist")

        session_path = task_dir / "session.md"
        import datetime

        timestamp = datetime.datetime.now().isoformat()
        # Count existing snapshots
        snapshot_count = 0
        if session_path.exists():
            text = session_path.read_text(encoding="utf-8")
            snapshot_count = text.count("## Turn ")

        turn_marker = f"## Turn {snapshot_count + 1} @ {timestamp}\n\n{content}\n\n---\n\n"

        with session_path.open("a", encoding="utf-8") as f:
            f.write(turn_marker)

    def judge_task(self, task_id: str) -> list[HarnessResult]:
        """Run Tier 0/1/2 verification and write results to judge.md.

        Returns:
            List of HarnessResult (one per tier)

        Raises:
            FileNotFoundError: If task does not exist
        """
        from mem0ress.harness import HarnessRunner

        index_path = self._task_index_path(task_id)
        if not index_path.exists():
            raise FileNotFoundError(f"Task '{task_id}' does not exist")

        manifest = SubstrateParser.parse_manifest(index_path)
        runner = HarnessRunner()
        results = runner.verify_task(manifest)

        # Write results to judge.md
        judge_path = index_path.parent / "judge.md"
        self._write_judge_report(judge_path, task_id, results)

        return results

    def _write_judge_report(
        self, judge_path: Path, task_id: str, results: list[HarnessResult]
    ) -> None:
        """Write judge report to judge.md file."""
        import datetime

        timestamp = datetime.datetime.now().isoformat()
        lines = [
            f"# Judge Report — {task_id}",
            "",
            f"**Generated**: {timestamp}",
            "",
        ]

        for result in results:
            tier_label = f"Tier {result.tier}"
            status = "PASS" if result.passed else "FAIL"
            lines.append(f"## {tier_label} — {status}")
            lines.append("")
            lines.append(f"{result.message}")
            if result.deviation:
                lines.append("")
                lines.append(f"**Deviation**: {result.deviation}")
            lines.append("")

        lines.append("---\n")
        judge_path.write_text("\n".join(lines), encoding="utf-8")

    def close_task(self, task_id: str) -> TaskManifest:
        """Atomically close a task: judge first, then mark COMPLETED.

        This is the MVP's "no bypass" rule: a task cannot be closed
        without passing all verification tiers.

        Args:
            task_id: Task identifier

        Returns:
            Updated TaskManifest with status COMPLETED

        Raises:
            FileNotFoundError: If task does not exist
            RuntimeError: If any verification tier fails
        """
        # Run verification first
        results = self.judge_task(task_id)

        # Check if all tiers passed
        failed_tiers = [r for r in results if not r.passed]
        if failed_tiers:
            tier_labels = [f"Tier {r.tier}" for r in failed_tiers]
            messages = "\n".join(f"  - {r.tier}: {r.deviation or r.message}" for r in failed_tiers)
            raise RuntimeError(
                f"Cannot close task '{task_id}': verification failed\n"
                f"Failed tiers: {', '.join(tier_labels)}\n"
                f"{messages}"
            )

        # All passed — update status to COMPLETED
        return self.complete_task(task_id)
