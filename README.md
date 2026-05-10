# mem0ress — 认知对齐平面 SDK

mem0ress 是一个面向 AI Agent 开发者的**认知对齐平面（Cognitive Alignment Plane）** SDK。它以轻量级生命周期钩子的形式注入 Agent 执行循环，提供任务状态管理与目标态势感知能力。

**核心定位**：不是记忆检索系统，而是**前向的认知系统**——让 AI Agent 始终知道"我在哪、要到哪、还差什么"。

---

## 核心概念

### 认知三要素（PRC Framework）

每个任务由三个要素定义，判断未来动作是否偏离：

| 要素 | 说明 | 定义者 |
|------|------|--------|
| **Picture** | 语义层面的终极成功状态（利益相关者感知到的结果） | 利益相关者 |
| **Requirements** | 从 Picture 推导的可验证条件（每个都必须可独立判断通过/失败） | Agent 推导 |
| **Constraints** | 不可逾越的红线（一旦违反系统必须阻断） | Agent + 领域知识 |

### 双平面正交

| 平面 | 回答 | 触发时机 |
|------|------|----------|
| **状态平面**（Status Plane） | "我在哪？" | 每次 Agent 唤醒时强制挂载 |
| **数据平面**（Data Plane） | "操作的是哪个版本的代码？" | Agent 需要操作具体数据时按需挂载 |

### 四层检验（Tiers）

| Tier | 内容 | 执行者 |
|------|------|--------|
| Tier 0 | Constraints 违反检查 | 自动触发 |
| Tier 1 | Todo 完成 + 子任务关闭检查 | 自动触发 |
| Tier 2 | Requirements 满足检查 | 自动触发 |
| Tier 3 | 语义对齐判断（Picture vs 实际产出） | Agent 主动决策 |

---

## 目录结构

```
.mem0ress/                          # 认知基座根目录
└── tasks/
    └── {task_id}/
        ├── task.md                  # 任务定义（Picture/Requirements/Constraints + Todos）
        ├── session.md               # 轮次快照（每轮追加，含 data_plane 快照）
        ├── gotchas.md               # 偏差记录（每条追加）
        └── judge.md                 # 检验报告（每轮追加，含时间戳）
```

---

## 快速开始

### 安装

```bash
uv add mem0ress
# 或从源码安装
pip install -e .
```

### CLI 命令

```bash
# 初始化认知基座
mem0 init

# 查看状态平面
mem0 status

# 创建任务
mem0 create implement_login --picture "用户无需输入密码即可登录"

# 更新认知三要素（定义 Picture/Requirements/Constraints）
# 直接编辑 .mem0ress/tasks/{task_id}/task.md 的 frontmatter

# 标记 Todo 完成
# 直接编辑 task.md 中的 - [x] / - [ ] 行

# 标记任务完成
mem0 done implement_login

# 标记任务废弃
mem0 abandon implement_login

# 查看最新 Judge 报告
mem0 report implement_login

# 指定根目录（默认 .mem0ress）
mem0 status --root /path/to/.mem0ress
mem0 create auth --parent implement_login
```

### Python API 使用

#### 状态平面（只读）

```python
from mem0ress.gateway.plane import PlaneAssembler

assembler = PlaneAssembler(".mem0ress")
plane = assembler.compile_status_plane()
print(plane.render())  # 获取状态平面字符串
```

#### 写操作（TaskService）

```python
from mem0ress.gateway.actions import TaskServiceImpl

svc = TaskServiceImpl(Path(".mem0ress"))

# 创建任务
manifest = svc.create_task("my_task", picture="完成什么目标")

# 获取任务
manifest = svc.get_task("my_task")

# 更新 Cognitive Triad
svc.update_cognitive_triad(
    "my_task",
    picture="新的成功状态",
    requirements=["可验证条件1", "shell:echo test"],
    constraints=["不可逾越的红线"],
)

# 更新 Todo
svc.update_todo("my_task", index=0, done=True)

# 标记完成/废弃
svc.complete_task("my_task")
svc.abandon_task("my_task")
```

#### 认知拦截器（Agent 生命周期钩子）

```python
from mem0ress.gateway.intercept import CognitiveContext

# Before Turn：挂载状态平面
with CognitiveContext(".mem0ress") as ctx:
    status_plane = ctx.status_plane  # 注入 Agent 上下文
    # Agent 执行思考...

# __exit__ 自动触发：
#   - Tier 0 约束检查
#   - Session 快照追加（含 data_plane 快照）
```

#### Git 操作（数据平面）

```python
from mem0ress.substrate.git_ops import get_data_plane, snapshot_data_plane

# 获取当前所有 clean repo 的 commit ID 快照
data_plane = get_data_plane(Path("/path/to/workspace"))
# -> {"/path/to/repo": "abc1234", ...}

# 将 data plane 快照写入 task session.md
snapshot_data_plane(
    task_id="my_task",
    substrate_root=Path(".mem0ress"),
)
```

#### 任务检验（Harness Engine）

```python
from mem0ress.harness import HarnessRunner

runner = HarnessRunner()
results = runner.verify_task(manifest, subtasks=None)

for r in results:
    tier_pass = "✅" if r.passed else "❌"
    print(f"Tier {r.tier} {tier_pass}: {r.message}")

if runner.is_complete(results):
    print("所有层级检验通过！")
```

---

## 数据流总览

```
宿主 Event Loop
    │
    ▼
with CognitiveContext(".mem0ress") as ctx:
    │
    ├── __enter__（Before Turn）
    │   └── PlaneAssembler.compile_status_plane()
    │       └── status_plane → 注入 Agent 上下文
    │
    ├── Agent 执行思考...
    │   ├── 调用 TaskServiceImpl 读写任务
    │   ├── 调用 HarnessRunner.verify_task() 检验
    │   └── 调用 get_data_plane() 记录代码版本
    │
    └── __exit__（After Turn）
        ├── Tier 0 约束检查
        └── snapshot_session() → session.md 追加轮次快照
            └── 含 data_plane commit ID 快照
```

---

## 开发规范

```bash
# 类型检查
ty check src/

# Lint 检查
ruff check src/

# 格式化
ruff format src/

# 运行测试
pytest tests/ -v

# 完整验证（提交前必须）
ty check src/ && ruff check src/ && pytest tests/
```

---

## 测试覆盖

- **单元测试**：schema、parser、plane、task_service、harness、git_ops
- **集成测试**：task_lifecycle、task_cognition_persistence
- 运行 `pytest tests/ -v` 查看全部 85+ 测试用例

---

## 相关文档

| 文档 | 说明 |
|------|------|
| `docs/spec.md` | 接口语义规范（做什么） |
| `src/mem0ress/design.md` | 实施方案（如何做） |
| `src/mem0ress/core/schema.py` | Pydantic 数据模型 |
| `src/mem0ress/gateway/actions.py` | TaskService 写操作实现 |
| `src/mem0ress/substrate/git_ops.py` | 数据平面 Git 追踪 |
| `src/mem0ress/harness/__init__.py` | Tier 1/2/3 检验引擎 |