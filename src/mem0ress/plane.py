"""Plane Assembler - compile_status_plane."""

from pathlib import Path
from typing import List

from mem0ress.core.schema import TaskManifest, TaskStatus
from mem0ress.storage.parser import SubstrateParser


class PlaneAssembler:
    """Compiles the cognitive status plane from the substrate."""

    def __init__(self, substrate_root: Path = Path(".mem0ress")):
        """Initialize PlaneAssembler.

        Args:
            substrate_root: Root directory for cognitive substrate (default: .mem0ress)
        """
        self.substrate_root = substrate_root
        self.tasks_dir = substrate_root / "tasks"

    def compile_status_plane(self) -> str:
        """Scan tasks directory and generate indented status plane.

        Returns:
            Formatted status plane string with system laws appended.
        """
        lines = ["# Status Plane (当前态势感知)\n"]

        if not self.tasks_dir.exists():
            lines.append("(无活动任务)")
            return self._add_system_laws(lines)

        # Collect all tasks and identify top-level ones (no parent directory)
        all_tasks = self._scan_tasks(self.tasks_dir)

        # Separate root tasks from subtasks
        root_tasks = []
        subtasks_by_parent = {}

        for task_path in all_tasks:
            relative_parts = task_path.relative_to(self.tasks_dir).parts
            if len(relative_parts) == 1:
                root_tasks.append(task_path)
            else:
                parent_id = relative_parts[0]
                if parent_id not in subtasks_by_parent:
                    subtasks_by_parent[parent_id] = []
                subtasks_by_parent[parent_id].append(task_path)

        # Render root tasks with their subtasks
        for task_path in sorted(root_tasks):
            task_id = task_path.parts[-1]
            manifest = SubstrateParser.parse_manifest(task_path / "index.md")
            lines.append(self._render_task(manifest, 0, subtasks_by_parent.get(task_id, [])))

        return self._add_system_laws(lines)

    def _scan_tasks(self, tasks_dir: Path) -> List[Path]:
        """Recursively find all task index.md files."""
        result = []
        for index_path in tasks_dir.rglob("index.md"):
            # Skip references/ subdirectories
            if "references" in index_path.parts:
                continue
            result.append(index_path.parent)
        return result

    def _render_task(
        self,
        manifest: TaskManifest,
        depth: int,
        subtasks: List[Path],
    ) -> str:
        """Render a single task and its subtasks.

        Args:
            manifest: TaskManifest to render
            depth: Indentation depth (0 for top-level)
            subtasks: List of subtask directory paths

        Returns:
            Formatted task string with subtasks indented
        """
        indent = "  " * depth
        task_id = manifest.id
        status_display = manifest.status.value.upper().replace("-", "-")

        # Render picture - check for ref: prefix
        picture = manifest.cognitive_triad.picture
        if picture.startswith("ref:"):
            picture_display = f"[脱水指针: {picture[4:]}]"
        else:
            picture_display = picture

        # Count completed todos
        total_todos = len(manifest.todos)
        completed_todos = sum(1 for t in manifest.todos if t.done)
        progress = f"{completed_todos}/{total_todos} Todos 完成" if total_todos > 0 else "无 Todos"

        lines = []
        lines.append(f"{indent}■ Task ID: {task_id} [{status_display}]")
        lines.append(f"{indent}   目标图景: {picture_display}")
        lines.append(f"{indent}   进度: {progress}")

        # Render subtasks recursively
        for subtask_path in sorted(subtasks):
            subtask_id = subtask_path.parts[-1]
            try:
                subtask_manifest = SubstrateParser.parse_manifest(subtask_path / "index.md")
                lines.append(self._render_task(subtask_manifest, depth + 1, []))
            except Exception:
                # If we can't parse a subtask, just show basic info
                lines.append(f"{indent}  └─ Task ID: {subtask_id} [解析失败]")

        return "\n".join(lines)

    def _add_system_laws(self, lines: List[str]) -> str:
        """Append system laws to the lines list and return joined string."""
        lines.append("\n---\n系统法则：")
        lines.append("1. 你不可撤销状态，只能覆写向前。")
        lines.append("2. 任何父级 Task 的完成，必须以其所有子层级 Task 完成为绝对前提。")
        return "\n".join(lines)