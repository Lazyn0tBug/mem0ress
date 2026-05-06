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