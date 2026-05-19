# mem0ress — 认知对齐平面 SDK

mem0ress 是一个面向 AI Agent 开发者的**认知对齐平面（Cognitive Alignment Plane）** SDK。它以轻量级生命周期钩子的形式注入 Agent 执行循环，提供任务状态管理与目标态势感知能力。

**核心定位**：不是记忆检索系统，而是**前向的认知系统**——让 AI Agent 始终知道"我在哪、要到哪、还差什么"。

---

## 文档索引

| 文档 | 说明 |
|------|------|
| **[教程 (docs/TUTORIAL.md)](docs/TUTORIAL.md)** | 快速上手指南——安装、命令、文件协议、Skill 命令、Judge 验证 |
| `docs/SPEC.md` | 接口语义规范 |
| `src/mem0ress/design.md` | 实施方案 |

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

| Tier | 内容 | 执行者 | 性质 |
|------|------|--------|------|
| Tier 0 | Constraints 违反检查 | 自动触发 | 参考信号（loop 或忽略，不阻塞） |
| Tier 1 | Todo 完成 + 子任务关闭检查 | 自动触发 | 参考约束（loop 或忽略，不阻塞） |
| Tier 2 | Requirements 满足检查 | 自动触发 | 评估参考（逐步满足，不阻塞） |
| Tier 3 | 语义对齐判断（Picture vs 实际产出） | Agent 主动决策 | **唯一硬门槛**（FAIL → amend 循环） |

**进入 Tier 3 前置条件**：所有 Tier 1/2 条目已满足或已由人确认跳过。

---

## 目录结构

```
mem0ress/
├── src/mem0ress/            # 源代码
│   ├── cli.py               # CLI 入口（mem0 init/create/status/list/update/judge/close/done/abandon/report）
│   ├── core/                # 核心类型
│   │   ├── schema.py        # Pydantic 模型（TaskManifest、CognitiveTriad、TaskStatus）
│   │   ├── constants.py     # 常量（DEFAULT_SUBSTRATE_ROOT = ".cap"）
│   │   └── id_gen.py        # 任务 ID 生成器（base36，6位）
│   ├── gateway/             # 核心逻辑
│   │   ├── actions.py       # 写操作（create/update/complete/abandon）
│   │   ├── plane.py         # 状态平面组装器（只读扫描）
│   │   ├── intercept.py     # 生命周期钩子（Before/After Turn）
│   │   ├── protocol.py      # TaskServiceProtocol 接口定义
│   │   ├── task_info.py     # 集中式任务注册表（.task_info）
│   │   └── current_task.py  # 当前任务指针（legacy）
│   ├── harness/             # 任务检验
│   │   └── judge.py         # Tier 1/2/3 验证执行器
│   └── substrate/           # 底层组件
│       ├── fs.py            # 乐观锁文件系统（safe_write）
│       ├── parser.py        # Markdown ↔ Pydantic 双向解析
│       └── git_ops.py       # Git 操作（数据平面快照）
├── tests/                   # 测试
│   ├── unit/               # 单元测试
│   └── integration/        # 集成测试
├── docs/                   # 文档
│   ├── SPEC.md             # 接口语义规范
│   ├── PROTOCOL.md         # 协议解释
│   ├── FAQ.md              # 设计哲学
│   ├── SCHEMA.md           # 数据模型说明
│   ├── TUTORIAL.md         # 入门教程
│   ├── TEMPLATES/          # 任务模板
│   ├── BRAINSTORMS/        # 头脑风暴
│   ├── ARCHIVE/            # 归档文档
│   ├── CLAUDE/             # Claude 会话
│   ├── DESIGN/             # 设计文档
│   ├── GEMINI/             # Gemini 会话
│   ├── GPT/                # GPT 会话
│   ├── PLANS/              # 实施计划
│   ├── REVIEW/             # 评审文档
│   └── TUTORIALS/          # 教程
└── pyproject.toml
```

---

## 认知基座结构

```
.cap/                              # 认知基座根目录（.mem0ress 的别名）
└── tasks/
    └── {task_id}/
        ├── task.md               # 任务定义（Picture/Requirements/Constraints + Todos）
        ├── session.md            # 轮次快照（每轮追加，含 data_plane 快照）
        ├── gotchas.md           # 偏差记录（每条追加）
        └── judge.md             # 检验报告（每轮追加，含时间戳）
```

## 快速开始

### 安装

**Python 包（CLI 命令行工具）：**

```bash
# 方式一：从源码安装（当前测试阶段）
pip install -e .

# 方式二：从 PyPI 安装（发布后）
pip install mem0ress
```

安装后，`mem0` CLI 命令可用。

**Skill（`/cap` 命令）：**

Skill 不需要 pip 安装。Agent runtime 读取 `src/mem0ress/skill/SKILL.md` 即可激活 `/cap` 命令集。Skill 和 CLI 共用同一套代码库。

### CLI 命令

```bash
# 初始化认知基座
mem0 init

# 查看状态平面
mem0 status

# 创建任务
mem0 create --picture "用户无需输入密码即可登录"

# 列出所有任务并选择当前任务
mem0 list

# 追加会话快照（使用当前任务）
mem0 update --content "完成了 OAuth provider 配置"

# 运行 Judge 验证（使用当前任务）
mem0 judge

# 标记当前任务完成（先 Judge 验证）
mem0 done

# 标记任务废弃
mem0 abandon

# 查看最新 Judge 报告（使用当前任务）
mem0 report

# 指定根目录（默认 .cap）
mem0 status --root /path/to/.cap
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
| `docs/SPEC.md` | 接口语义规范（做什么） |
| `docs/PROTOCOL.md` | 协议解释 |
| `docs/FAQ.md` | 设计哲学 |
| `docs/SCHEMA.md` | 数据模型说明 |
| `src/mem0ress/design.md` | 实施方案（如何做） |