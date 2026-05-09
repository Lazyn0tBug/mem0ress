# mem0ress - 认知对齐平面 SDK

## 项目概述

mem0ress 是一个面向 AI Agent 开发者的认知对齐平面（Cognitive Alignment Plane）SDK。它以轻量级生命周期钩子的形式注入 Agent 执行循环，提供任务状态管理与目标态势感知能力。

**技术栈**: Python 3.12+ / uv / ruff / ty / Pydantic / Rich

**核心模块**: Plane Assembler（状态平面组装器）/ Tool Interface（工具接口）/ Harness Engine（任务检验引擎）

**文档依赖**:
- `docs/spec.md` — 接口语义规范（做什么）
- `src/mem0ress/design.md` — 实施方案与实现细节

---

## 项目结构

```
mem0ress/
├── src/mem0ress/
│   ├── __init__.py
│   ├── cli.py                  # CLI 入口（status / init / create / done / abandon / report）
│   ├── core/
│   │   └── schema.py          # Pydantic 模型（TaskManifest、CognitiveTriad、TaskStatus 等）
│   ├── gateway/
│   │   ├── plane.py           # PlaneAssembler — 状态平面编译
│   │   ├── actions.py         # TaskServiceImpl — 写操作（create/update/complete/abandon）
│   │   └── intercept.py       # CognitiveContext — 生命周期钩子上下文管理器
│   ├── substrate/
│   │   ├── fs.py              # safe_write / get_file_hash — 乐观锁文件系统操作
│   │   ├── parser.py           # SubstrateParser — Markdown ↔ Pydantic 双向解析
│   │   └── git_ops.py         # Git 操作（待实现）
│   └── harness/
│       └── __init__.py        # HarnessRunner — Tier 1/2/3 检验执行器
├── tests/
│   ├── unit/                  # 单元测试（schema、parser、plane、task_service、harness）
│   └── integration/            # 集成测试（lifecycle、persistence）
├── docs/
│   └── spec.md                # 接口语义规范
├── src/mem0ress/design.md     # 实施方案与实现细节
└── pyproject.toml
```

**模块职责一览**：

| 模块 | 文件 | 职责 |
|------|------|------|
| core | schema.py | 类型定义（TaskManifest、TaskStatus、CognitiveTriad、StatusPlane 等） |
| gateway/plane | plane.py | 只读：扫描文件系统，编译状态平面快照 |
| gateway/actions | actions.py | 写操作：create / complete / abandon / update_todo 等 |
| gateway/intercept | intercept.py | 生命周期钩子：Before Turn 挂载平面，After Turn 快照 Session |
| substrate/fs | fs.py | 文件系统底层：乐观锁写入（safe_write）、Hash 计算 |
| substrate/parser | parser.py | 解析/序列化：Markdown Frontmatter ↔ Pydantic 模型 |
| harness | __init__.py | 任务检验：Tier 1/2/3 执行器 |

---

## 开发规范

### 每次改动必须经过

```bash
# 1. 类型检查（ty 严格模式）
ty check src/

# 2. Lint 检查
ruff check src/

# 3. 格式化
ruff format src/

# 4. 运行测试
pytest tests/ -v

# 5. 完整验证（推荐）
ty check src/ && ruff check src/ && pytest tests/
```

### Git 流程

```bash
# 1. 确认当前分支
git branch --show-current

# 2. 验证通过后，提交
git add -A
git commit -m "type(scope): description"

# type:
#   feat   — 新功能
#   fix    — Bug 修复
#   test   — 测试相关
#   docs   — 文档更新
#   chore  — 构建/工具配置
#   refactor — 代码重构（不影响功能）
#   arch   — 架构调整（对应 design.md 变更）
```

**提交前必须验证通过。验证不通过不提交。**

### 类型注解规范

- 所有公共函数必须有完整类型注解
- 使用 `ty check src/` 强制检查
- 优先用 `Literal` 而非 `Enum` 表示有限状态集
- `Field` 必须提供 `description`，供文档和 LSP 使用

```python
from pydantic import BaseModel, Field
from pathlib import Path


class TaskManifest(BaseModel):
    """Task manifest — index.md 的内存映射。"""

    id: str = Field(description="任务 ID（目录名是 source of truth）")
    status: Literal["CREATED", "IN_PROGRESS", "VERIFYING", "COMPLETED", "ABANDONED"]
    cognitive_triad: CognitiveTriad = Field(description="认知三要素")
```

### Docstring 规范

每个模块文件顶部的 docstring 格式：

```python
"""Module name - one-line description.

Multi-line explanation of what this module does,
why it exists, and what invariants it maintains.
"""
```

每个公共函数/方法的 docstring 格式：

```python
def create_task(task_id: str, picture: str) -> TaskManifest:
    """Create a new task with the given ID and picture.

    Args:
        task_id: Unique task identifier (directory name)
        picture: Semantic goal description

    Returns:
        The newly created TaskManifest

    Raises:
        TaskExistsError: If task_id already exists
        FileNotFoundError: If tasks directory does not exist
    """
```

### 异常命名规范

使用 `{Domain}{Error}` 模式：

```python
class ManifestNotFoundError(Exception):
    """Raised when a manifest file does not exist."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Manifest not found: {path}")


class ConflictError(Exception):
    """Raised when optimistic lock fails — file was modified concurrently."""


class TaskExistsError(Exception):
    """Raised when attempting to create a task that already exists."""
```

---

## 数据模型

核心模型集中在 `core/schema.py`。

```python
# 状态枚举
class TaskStatus(StrEnum):
    CREATED = "created"
    IN_PROGRESS = "in-progress"
    VERIFYING = "verifying"    # 瞬态，检验完成必须离开
    COMPLETED = "completed"
    ABANDONED = "abandoned"

# 认知三要素
class CognitiveTriad(BaseModel):
    picture: str                           # 语义成功状态
    requirements: list[str] = Field(...)  # 可验证条件
    constraints: list[str] = Field(...)   # 不可逾越的红线

# Todo 项
class TodoItem(BaseModel):
    text: str
    done: bool = False

# 任务清单（index.md 的内存映射）
class TaskManifest(BaseModel):
    id: str
    type: str = "task"
    status: TaskStatus = TaskStatus.CREATED
    cognitive_triad: CognitiveTriad
    gotcha_refs: list[str] = Field(default_factory=list)
    todos: list[TodoItem] = Field(default_factory=list)

# 状态平面条目（展示用）
class StatusPlaneEntry(BaseModel):
    task_id: str
    todo_progress: tuple[int, int]        # (completed, total)
    status: TaskStatus
    gotchas: list[str]
    subtasks: list["StatusPlaneEntry"]

# 状态平面（顶层）
class StatusPlane(BaseModel):
    entries: list[StatusPlaneEntry]
    system_laws: tuple[str, str]          # 两条系统法则
```

**SSOT 原则**：
- `id` 字段冗余方便，**目录名是 source of truth**
- 所有 Pydantic 模型为 `frozen=True`，状态更新通过构造新实例实现
- 运行时工作区内新认知直接覆写旧认知，不做合并

---

## CLI 命令

| 命令 | 说明 |
|------|------|
| `mem0 status` | 展示当前状态平面（树形可视化） |
| `mem0 init` | 初始化认知基座（创建 .mem0ress/ 目录） |
| `mem0 create <task_id>` | 创建任务（含 index.md / session.md / gotchas.md / judge.md） |
| `mem0 create <task_id> --parent <parent_id>` | 创建子任务 |
| `mem0 done <task_id>` | 标记任务完成 |
| `mem0 abandon <task_id>` | 标记任务废弃 |
| `mem0 report <task_id>` | 显示最新一次 judge 检验报告 |

所有命令支持 `--root / -r` 指定基座路径（默认 `.mem0ress`）。

---

## 测试策略

**命名约定**：`tests/unit/test_{name}.py` — 模块名即文件名

**结构规范**：

```python
class TestTaskServiceImpl:
    """Tests for TaskServiceImpl."""

    def test_create_task_raises_if_exists(self, tmp_path: Path) -> None:
        """Creating a duplicate task raises TaskExistsError."""
        ...

    def test_update_todo_optimistic_lock(self, tmp_path: Path) -> None:
        """Concurrent update raises ConflictError."""
        ...
```

**覆盖要求**：
- 新功能必须添加测试
- 所有公共接口必须有测试
- 边界情况（不存在、已存在、并发冲突）必须有测试

**运行测试**：

```bash
# 全部测试
pytest tests/ -v

# 指定模块
pytest tests/unit/test_parser.py -v

# 带覆盖率（未来）
pytest tests/ -v --cov=src/mem0ress
```

---

## Skills 利用

开发过程中推荐使用以下 Skills：

| Skill | 用途 |
|-------|------|
| `devtools` | 命令行工具参考 |
| `brainstorming` | 需求澄清与方案设计 |
| `writing-plans` | 实现计划编写 |
| `code-review-expert` | 代码审查 |
| `spec-review` | 规范评审 |

**使用方式**：

```bash
# 加载 skill
/ag:skill brainstorming

# 审查前加载
/ag:skill code-review-expert
```

---

## 调试规范

### 日志规范

| 级别 | 使用场景 | 生产环境 |
|------|----------|----------|
| `logging.debug` | 详细排查 | ❌ 禁止 |
| `logging.info` | 重要操作（创建/完成/废弃任务） | ✅ 允许 |
| `logging.warning` | 潜在问题（约束接近边界） | ✅ 允许 |
| `logging.error` | 操作失败 | ✅ 允许 |

### 提交前检查

```bash
# 检查遗留 debug 日志
grep -r "logger.debug" src/
grep -r "print(" src/

# 检查硬编码路径
grep -r "/Users/" src/
grep -r "C:\\\\" src/
```

---

## 依赖管理

```bash
# 添加依赖
uv add pydantic typer

# 添加开发依赖
uv add --dev pytest ruff ty

# 同步环境
uv sync

# 锁文件更新
uv lock
```

---

## 项目命令

```bash
# 类型检查
ty check src/

# Lint 检查
ruff check src/

# 格式化
ruff format src/

# 运行测试
pytest tests/ -v

# 完整验证
ty check src/ && ruff check src/ && pytest tests/

# CLI 帮助
python -m mem0ress.cli --help
```

---

## 相关文档

- [docs/spec.md](./docs/spec.md) — 接口语义规范
- [src/mem0ress/design.md](./src/mem0ress/design.md) — 实施方案与实现细节

---

## 注意事项

1. **使用 uv 管理依赖** — 锁文件 `uv.lock` 必须提交
2. **ty 严格模式** — 所有公共接口必须有完整类型注解
3. **零隐藏状态** — 所有认知数据以 Markdown/YAML 存储
4. **测试必须** — 任何功能改动必须更新测试并验证通过
5. **验证通过再提交** — `ty check && ruff && pytest` 是强制门槛
6. **禁止硬编码** — 不在代码中硬编码路径、密钥或环境特定配置
7. **frozen 模型** — TaskManifest 等模型不可变，状态更新通过构造新实例
8. **frozen=True 的 model_dump()** — 调用时无需 `.model_dump()`，直接访问字段
