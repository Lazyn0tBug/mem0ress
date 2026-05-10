---
title: mem0ress 实现设计
version: 0.2
definition: 认知对齐平面的实现架构文档，描述模块划分、接口签名、错误处理和技术流程
---

# mem0ress 实现设计

> **与规范的关系：** 本文档是 `docs/spec.md` 的实现承接文档。规范定义接口语义（做什么），本文档描述实现方案（如何做）。规范不引用本文档，依赖方向单一。

---

## 1. 项目目录结构

```
src/mem0ress/
├── __init__.py
├── cli.py                  # CLI 入口（typer + Rich 可视化）
├── core/
│   └── schema.py          # Pydantic 模型（TaskManifest、TaskStatus、CognitiveTriad 等）
├── gateway/
│   ├── plane.py           # PlaneAssembler — 状态平面编译（只读）
│   ├── actions.py         # TaskServiceImpl — 写操作实现
│   └── intercept.py       # CognitiveContext — 生命周期钩子
├── substrate/
│   ├── fs.py              # safe_write / get_file_hash — 乐观锁文件系统操作
│   ├── parser.py           # SubstrateParser — Markdown ↔ Pydantic 双向转换
│   └── git_ops.py         # Git 操作（待实现）
└── harness/
    └── __init__.py        # HarnessRunner — Tier 1/2/3 检验执行器
```

---

## 2. 模块架构

### 2.1 模块边界

| 模块 | 类型 | 公开接口 | 说明 |
|------|------|----------|------|
| `gateway/plane.py` | 只读 | `PlaneAssembler(substrate_root)` / `compile_status_plane() -> StatusPlane` | 扫描文件系统，编译状态平面快照，无缓存 |
| `gateway/actions.py` | 写操作 | `TaskServiceImpl(substrate_root)` / `create_task()` / `complete_task()` / `abandon_task()` / `update_todo()` / `update_cognitive_triad()` / `get_task()` / `get_all_tasks()` / `delete_task()` / `add_todo()` / `remove_todo()` | 所有写操作通过此处，乐观锁保护 |
| `gateway/intercept.py` | 钩子 | `CognitiveContext(substrate_root)` / `__enter__()` / `__exit__()` / `status_plane: StatusPlane` | Before Turn 挂载平面，After Turn 自动触发 Session 快照和 Tier 0 检查 |
| `substrate/parser.py` | 解析 | `SubstrateParser.parse_manifest(path) -> TaskManifest` / `serialize_manifest(manifest, path) -> str` | Frontmatter ↔ Pydantic 双向转换 |
| `substrate/fs.py` | 文件系统 | `safe_write(path, content, expected_hash)` / `get_file_hash(path) -> str` | 乐观锁写入，SHA-256 Hash 比对 |
| `harness/__init__.py` | 检验 | `HarnessRunner()` / `verify_task(manifest, subtasks) -> list[HarnessResult]` / `is_complete(results) -> bool` | Tier 1/2/3 执行，结果为 `HarnessResult` 列表 |
| `harness/judge.py` | 上下文 | `prepare_judge_context(task_id, picture, artifacts, constraints, data_plane_summary) -> JudgeResult` | Tier 3 语义对齐上下文准备（实际判断由 Agent 执行） |

### 2.2 Plane Assembler（平面组装器）

**职责：** 认知构建的执行单元。只读扫描文件系统，编译状态平面快照。

**接口：**

```python
class PlaneAssembler:
    def __init__(self, substrate_root: Path = Path(".mem0ress")) -> None:
        """Args:
            substrate_root: 认知基座根目录（默认 .mem0ress）
        """

    def compile_status_plane(self) -> StatusPlane:
        """扫描 tasks/ 目录，编译状态平面快照。

        实时扫描，每次调用直接读文件系统，不缓存。
        只输出当前状态，不做偏差判断。

        Returns:
            StatusPlane — 使用 .render() 获取字符串格式
        """
```

**设计原则：**
- 纯展示，无诊断
- 实时扫描，不缓存
- 全面覆盖，不隐藏任何节点
- 非侵入，只读不写

### 2.3 Tool Interface（工具接口）

**职责：** 认知操作的写入入口，通过 `TaskServiceImpl` 实现。

**接口：**

```python
class TaskServiceImpl:
    def __init__(self, substrate_root: Path = Path(".mem0ress")) -> None:
        """Args:
            substrate_root: 认知基座根目录
        """

    # 写操作
    def create_task(self, task_id: str, picture: str) -> TaskManifest:
        """创建新任务目录（含 task.md / session.md / gotchas.md / judge.md）。

        Raises:
            TaskExistsError: 任务已存在
        """

    def complete_task(self, task_id: str) -> TaskManifest:
        """标记任务为 COMPLETED。乐观锁保护。

        Raises:
            FileNotFoundError: 任务不存在
            ConflictError: 文件已被修改
        """

    def abandon_task(self, task_id: str) -> TaskManifest:
        """标记任务为 ABANDONED。乐观锁保护。

        Raises:
            FileNotFoundError: 任务不存在
            ConflictError: 文件已被修改
        """

    def update_todo(self, task_id: str, index: int, done: bool) -> TaskManifest:
        """更新指定 Todo 的完成状态。乐观锁保护。

        Raises:
            FileNotFoundError: 任务不存在
            IndexError: Todo 索引越界
            ConflictError: 文件已被修改
        """

    def update_cognitive_triad(
        self,
        task_id: str,
        picture: str,
        requirements: list[str],
        constraints: list[str],
    ) -> TaskManifest:
        """更新认知三要素（Picture / Requirements / Constraints）。

        Raises:
            FileNotFoundError: 任务不存在
            ConflictError: 文件已被修改
        """

    def add_todo(self, task_id: str, text: str) -> TaskManifest:
        """追加一个新 Todo 项。"""

    def remove_todo(self, task_id: str, index: int) -> TaskManifest:
        """删除指定 Todo 项。"""

    # 读操作
    def get_task(self, task_id: str) -> TaskManifest:
        """获取指定任务的 Manifest。"""

    def get_all_tasks(self) -> list[TaskManifest]:
        """获取所有任务的 Manifest 列表。"""

    def delete_task(self, task_id: str) -> None:
        """删除任务目录及其所有文件。"""
```

**设计原则：**
- 所有写操作均通过 `safe_write`，乐观锁 Hash 校验
- `frozen=True` 模型，状态更新通过构造新实例实现
- Upsert 语义：`create_task` 不存在时自动创建

### 2.4 Judge Agent（任务检验执行器）

**职责：** 执行任务检验，只读数据。检验完成后，结果写入 `judge.md`（每轮追加），通过 hook 返回值通知主 Agent。

**Tier 执行内容：**

| Tier | 检查内容 | 输入来源 |
|------|---------|---------|
| Tier 0 | Constraints 违反检查 | Constraints（task.md）、当前代码状态（文件系统） |
| Tier 1 | Todo 完成 + 子任务关闭 | todos（task.md）、Session 当前快照、子任务 task.md |
| Tier 2 | Requirements 满足检查 | Requirements（task.md）、实际产出（文件系统） |
| Tier 3 | 语义对齐判断 | Picture（task.md）、实际产出（文件系统） |

**接口：**

```python
class HarnessRunner:
    def verify_task(
        self,
        manifest: TaskManifest,
        subtasks: list[TaskManifest] | None = None,
    ) -> list[HarnessResult]:
        """执行 Tier 1 → 2 → 3 完整检验链路。

        Tier 3 的实际判断由 Agent 执行，本方法只准备上下文。
        Returns:
            list[HarnessResult] — 每层一个结果
        """

    def is_complete(self, results: list[HarnessResult]) -> bool:
        """判断所有层是否通过。"""


class HarnessResult(BaseModel):
    """单个 Tier 的检验结果。"""

    tier: int                           # 1, 2 或 3
    passed: bool
    message: str                        # 人类可读的结果描述
    deviation: str | None = None        # 失败时的偏差原因


def prepare_judge_context(
    task_id: str,
    picture: str,
    artifacts: list[Path] | None = None,
    constraints: list[str] | None = None,
    data_plane_summary: str | None = None,
) -> JudgeResult:
    """准备 Tier 3 语义对齐的判断上下文。

    实际判断由 Agent 执行，本函数只准备 Briefing 文本。
    """
```

**文件存储：**

```
.mem0ress/tasks/{task_id}/
├── task.md       # Task 定义
├── session.md     # 轮次快照（每轮追加）
├── gotchas.md     # 偏差记录（每条追加）
└── judge.md       # 检验报告（每轮追加，含时间戳）
```

---

## 3. 错误处理

### 3.1 异常体系

```python
# substrate/fs.py
class ConflictError(Exception):
    """乐观锁失败 — 文件在操作期间被外部修改。"""


# gateway/actions.py
class TaskExistsError(Exception):
    """尝试创建已存在的任务。"""
```

### 3.2 错误传播规则

| 场景 | 异常 | 调用方处理 |
|------|------|-----------|
| 并发写冲突 | `ConflictError` | 重新读取 → 重新构造 → 重试写入 |
| 任务不存在 | `FileNotFoundError` | 退出或提示用户 |
| 任务已存在 | `TaskExistsError` | 提示用户 |
| Todo 索引越界 | `IndexError` | 提示用户 |
| Manifest 格式非法 | `ValueError` | （解析层抛出，转换为此表对应异常） |

**调用方必须处理 `ConflictError` 并重试，不应该静默忽略。**

---

## 4. 认知拦截器（Gateway Interceptor）

`gateway/intercept.py` 的 `CognitiveContext` 是 SDK 参与 Agent 循环的唯一入口。

```python
class CognitiveContext:
    """SDK 生命周期钩子 — 供宿主系统集成到 Event Loop。"""

    def __init__(self, substrate_root: str | Path = ".mem0ress") -> None:
        """Args:
            substrate_root: 认知基座根目录
        """

    @property
    def status_plane(self) -> StatusPlane:
        """获取状态平面快照。只在 __enter__ 后可用。"""

    def __enter__(self) -> CognitiveContext:
        """Before Turn — 编译状态平面，供宿主注入 Agent 上下文。"""

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """After Turn — 自动触发 Tier 0 检查和 Session 快照。"""
```

**使用方式（宿主 Event Loop）：**

```python
with CognitiveContext(".mem0ress") as ctx:
    status_plane = ctx.status_plane  # 注入 Agent 上下文
    # Agent 执行思考...
# __exit__ 自动触发 Tier 0 检查 + Session 快照
```

---

## 5. CLI 命令

| 子命令 | 参数 | 说明 |
|--------|------|------|
| `status` | `--root / -r` | 展示状态平面（树形可视化） |
| `init` | `--root / -r` | 初始化认知基座 |
| `create` | `<task_id>` / `--parent <id>` / `--root / -r` | 创建任务或子任务 |
| `done` | `<task_id>` / `--root / -r` | 标记任务完成 |
| `abandon` | `<task_id>` / `--root / -r` | 标记任务废弃 |
| `report` | `<task_id>` / `--root / -r` | 显示最新 judge 报告 |

所有命令默认根路径 `.mem0ress`，可通过 `--root` 覆盖。

---

## 6. 核心机制

### 6.1 乐观锁机制

`substrate/fs.py` 在写入任何文件前，必须比对内容 SHA-256 Hash：

```python
def safe_write(file_path: Path, content: str, expected_hash: str) -> None:
    """写入文件，附带乐观锁检查。

    若文件存在且 Hash 不匹配，抛出 ConflictError。
    """
```

### 6.2 SSOT 与绝对覆写

- 运行时工作区内新认知直接覆写旧认知，不做合并
- `TaskManifest` 等 Pydantic 模型为 `frozen=True`
- 状态更新通过构造新实例实现：`TaskManifest(..., status=TaskStatus.COMPLETED)`

### 6.3 零隐藏状态

所有认知数据以纯文本（Markdown/YAML）存储，无二进制或隐藏状态：
- `task.md` — Task 定义
- `session.md` — 轮次快照（每轮追加）
- `gotchas.md` — 偏差记录（每条追加）
- `judge.md` — 检验报告（每轮追加，含时间戳）

---

## 7. 数据模型

### 7.1 TaskManifest（task.md 的内存映射）

```python
class TaskManifest(BaseModel):
    """Task manifest — frozen Pydantic model."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str                              # 目录名是 source of truth
    type: str = "task"
    status: TaskStatus = TaskStatus.CREATED
    cognitive_triad: CognitiveTriad       # Picture / Requirements / Constraints
    gotcha_refs: list[str] = []         # Gotcha 引用列表
    todos: list[TodoItem] = []           # Todo 列表
```

### 7.2 CognitiveTriad（认知三要素）

```python
class CognitiveTriad(BaseModel):
    """Picture / Requirements / Constraints 三要素。"""

    model_config = ConfigDict(frozen=True, extra="forbid")

    picture: str                         # 语义成功状态（利益相关者定义）
    requirements: list[str] = []        # 可验证条件（Agent 推导）
    constraints: list[str] = []         # 不可逾越红线（Agent + 领域知识）
```

### 7.3 StatusPlane（状态平面）

```python
class StatusPlane(BaseModel):
    """认知系统的当前状态快照 — 纯展示模型，不做诊断。"""

    entries: list[StatusPlaneEntry]      # 顶层任务列表
    system_laws: tuple[str, str]         # 两条系统法则

    def render(self) -> str:
        """渲染为字符串格式，供 Agent 上下文使用。"""


class StatusPlaneEntry(BaseModel):
    """单个任务条目。"""

    task_id: str
    todo_progress: tuple[int, int]       # (completed, total)
    status: TaskStatus
    gotchas: list[str]
    subtasks: list["StatusPlaneEntry"]
```

---

## 8. 技术流程

### 8.1 Agent 驱动的业务闭环

```
1. 认知构建：Agent 调用 get_status_plane() → 了解当前状态
2. 任务检验：Agent 调用 verify() → Judge Agent 执行检验，结果写入 judge.md
3. 状态更新：Agent 根据结果决策 → complete / abandon / update_todo
```

### 8.2 宿主集成方式

```
宿主 Event Loop
    ↓
with CognitiveContext(".mem0ress") as ctx:
    status_plane = ctx.status_plane  ← Before Turn：挂载状态平面
    # Agent 执行...
    # （__exit__ 自动触发 Tier 0 + Session 快照）
```

---

## 9. MVP 落地状态

| Phase | 描述 | 状态 |
|-------|------|------|
| Phase 1 | 物理契约与类型安全（schema + fs + parser） | ✅ 完成 |
| Phase 2 | 拦截器与态势投影（plane + intercept） | ✅ 完成 |
| Phase 3 | 动作网关（actions + git_ops 待实现） | ✅ actions 完成 |
| Phase 4 | 属性对齐验证（harness Tier 1/2/3） | ✅ 完成 |
| Phase 5 | CLI 可观测性（cli.py status / init / create / done / abandon / report） | ✅ 完成 |
| 待办 | git_ops.py — Data Plane 的 commit ID 管理 | ✅ 完成 |
