"""Core schema definitions - TaskManifest, CognitiveTriad, TodoItem, Gotcha, TaskStatus."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(StrEnum):
    """Task status enumeration."""

    CREATED = "created"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class CognitiveTriad(BaseModel):
    """Cognitive triad: picture, requirements, and constraints."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    picture: str = Field(
        description="图景：任务完成后的终极语义描述"
    )
    requirements: list[str] = Field(
        default_factory=list,
        description="需求：客观、可量化的指标或验证脚本",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="约束：执行过程中不可逾越的红线",
    )


class TodoItem(BaseModel):
    """Todo item for tracking execution steps."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str = Field(description="Todo description text")
    done: bool = Field(default=False, description="Whether this todo is completed")


class TaskManifest(BaseModel):
    """Task manifest - index.md 的内存映射."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(description="任务 ID（冗余但方便，目录名是 source of truth）")
    type: str = Field(default="task", description="类型标识")
    status: TaskStatus = Field(default=TaskStatus.CREATED, description="任务状态")
    cognitive_triad: CognitiveTriad = Field(description="认知三要素")
    gotcha_refs: list[str] = Field(default_factory=list, description="Gotcha 引用列表")
    todos: list[TodoItem] = Field(default_factory=list, description="Todo 列表")


class Gotcha(BaseModel):
    """Gotcha - 认知增量 patch."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(description="Gotcha ID（冗余但方便，文件路径是 source of truth）")
    type: str = Field(default="gotcha", description="类型标识")
    task_id: str = Field(description="关联的 Task ID（冗余但方便）")
    timestamp: str = Field(description="时间戳")
    related_task: str | None = Field(default=None, description="保留声明不用")
    content: str = Field(description="认知增量的核心文本")


class StatusPlaneEntry(BaseModel):
    """Single task entry in status plane.

    Display format: ■ {task_id} [{done}/{total}] {STATUS}
                    ! {gotcha}
                    └─ {subtask}
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    task_id: str = Field(description="任务标识符")
    todo_progress: tuple[int, int] = Field(
        description="Todo 完成进度 (completed, total)"
    )
    status: TaskStatus = Field(description="任务状态")
    gotchas: list[str] = Field(
        default_factory=list,
        description="偏差记录列表 (! marker)",
    )
    subtasks: list["StatusPlaneEntry"] = Field(
        default_factory=list,
        description="子任务列表 (└─ marker)",
    )


class StatusPlane(BaseModel):
    """Status Plane - 认知系统的当前状态快照.

    状态平面显示"现在在哪"，不是"要去哪"。
    它是纯展示模型，不做任何诊断或偏差判断。

    Display format:
        # Status Plane

        ■ {task_id} [{done}/{total}] {STATUS}
           ! {gotcha}
           └─ {subtask}

        ---

        系统法则：
        1. ...
        2. ...
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    entries: list[StatusPlaneEntry] = Field(
        default_factory=list,
        description="顶层任务条目列表",
    )
    system_laws: tuple[str, str] = Field(
        default=(
            "你不可撤销状态，只能覆写向前。",
            "任何父级 Task 的完成，必须以其所有子层级 Task 完成为绝对前提。",
        ),
        description="系统法则（不可违背）",
    )

    def render(self) -> str:
        """Render status plane to string format.

        Returns:
            Formatted status plane string.
        """
        lines = ["# Status Plane\n"]

        if not self.entries:
            lines.append("(no active tasks)")
        else:
            for entry in self.entries:
                lines.append(self._render_entry(entry, depth=0))

        lines.append("\n---\n系统法则：")
        for law in self.system_laws:
            lines.append(f"{self.system_laws.index(law) + 1}. {law}")

        return "\n".join(lines)

    def _render_entry(self, entry: StatusPlaneEntry, depth: int) -> str:
        """Render a single entry with optional subtasks."""
        indent = "  " * depth
        completed, total = entry.todo_progress
        todo_str = f"[{completed}/{total}]" if total > 0 else "[-]"

        lines = [f"{indent}■ {entry.task_id} {todo_str} {entry.status.value.upper()}"]

        for gotcha in entry.gotchas:
            lines.append(f"{indent}   ! {gotcha}")

        for subtask in entry.subtasks:
            lines.append(self._render_entry(subtask, depth + 1))

        return "\n".join(lines)