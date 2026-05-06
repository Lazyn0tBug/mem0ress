"""Plane Assembler - compile_status_plane.

Status Plane Design (状态平面设计规范):
==========================================

Purpose (目的):
    显示认知系统的当前状态 - 即"现在在哪"，不是"要去哪"。

Display Format (显示格式):
    ■ {task_id} [{done}/{total}] {STATUS}
       ! {gotcha_ref}
       └─ {subtask_id}

Visual Elements (视觉元素):
    ■  - 任务节点 (task node)
    [x/y] - Todo 完成进度 (x completed, y total), [-] if no todos
    STATUS - CREATED | IN-PROGRESS | COMPLETED | ABANDONED
    !  - Gotcha 偏差记录 (deviation record)
    └─ - 子任务指示 (subtask indicator)

What Status Plane Shows (状态平面显示内容):
    - Task ID (任务标识符)
    - Todo progress (任务清单完成进度)
    - Status (任务状态)
    - Gotcha refs (偏差记录)

What Status Plane Does NOT Show (状态平面不显示内容):
    - Picture (图景) - 这是目标，不是当前状态
    - Requirements (需求) - 这是目标，不是当前状态
    - Constraints (约束) - 这是目标，不是当前状态

Design Principles (设计原则):
    1. 纯展示，无诊断 - 不做任何偏差判断
    2. 实时扫描 - 每次调用直接读文件系统
    3. 全面覆盖 - 显示所有任务，不隐藏任何节点
    4. 非侵入 - 只读不写，不修改任何状态
"""

from pathlib import Path

from mem0ress.core.schema import (
    StatusPlane,
    StatusPlaneEntry,
    TaskManifest,
)
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

    def compile_status_plane(self) -> StatusPlane:
        """Scan tasks directory and generate status plane model.

        See module docstring (Status Plane Design) for full specification.

        Returns:
            StatusPlane model (use .render() to get string output).
        """
        if not self.tasks_dir.exists():
            return StatusPlane(entries=[])

        # Collect all tasks and identify top-level ones (no parent directory)
        all_tasks = self._scan_tasks(self.tasks_dir)

        # Separate root tasks from subtasks
        root_tasks = []
        subtasks_by_parent: dict[str, list[Path]] = {}

        for task_path in all_tasks:
            relative_parts = task_path.relative_to(self.tasks_dir).parts
            if len(relative_parts) == 1:
                root_tasks.append(task_path)
            else:
                parent_id = relative_parts[0]
                if parent_id not in subtasks_by_parent:
                    subtasks_by_parent[parent_id] = []
                subtasks_by_parent[parent_id].append(task_path)

        # Build StatusPlaneEntry tree
        entries = []
        for task_path in sorted(root_tasks):
            manifest = SubstrateParser.parse_manifest(task_path / "index.md")
            entry = self._build_entry(
                manifest,
                subtasks_by_parent.get(task_path.parts[-1], []),
            )
            entries.append(entry)

        return StatusPlane(entries=entries)

    def _scan_tasks(self, tasks_dir: Path) -> list[Path]:
        """Recursively find all task index.md files."""
        result = []
        for index_path in tasks_dir.rglob("index.md"):
            # Skip references/ subdirectories
            if "references" in index_path.parts:
                continue
            result.append(index_path.parent)
        return result

    def _build_entry(
        self,
        manifest: TaskManifest,
        subtask_paths: list[Path],
    ) -> StatusPlaneEntry:
        """Build StatusPlaneEntry from TaskManifest and subtask paths."""
        total_todos = len(manifest.todos)
        completed_todos = sum(1 for t in manifest.todos if t.done)

        subtasks = []
        for subtask_path in sorted(subtask_paths):
            try:
                subtask_manifest = SubstrateParser.parse_manifest(subtask_path / "index.md")
                subtasks.append(self._build_entry(subtask_manifest, []))
            except Exception:
                # Parse failure - include error entry
                subtasks.append(
                    StatusPlaneEntry(
                        task_id=subtask_path.parts[-1],
                        todo_progress=(0, 0),
                        status=manifest.status,  # Use parent status as fallback
                        gotchas=[],
                        subtasks=[],
                    )
                )

        return StatusPlaneEntry(
            task_id=manifest.id,
            todo_progress=(completed_todos, total_todos),
            status=manifest.status,
            gotchas=list(manifest.gotcha_refs),
            subtasks=subtasks,
        )