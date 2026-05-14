# mem0ress MVP Design

> Protocol Version: `0.1-alpha`  
> Document Status: Design Specification  
> Tech Stack: Python · pyproject · uv · ruff · ty · Typer · Pydantic v2

---

## 1. 问题与定位

### 现有 Memory 系统的结构性缺陷

当前主流 Agent 框架的 memory 机制本质上是**信息检索**——把过去发生过的事情存储并召回。这解决了"agent 记得什么"的问题，却没有解决"agent 是否在做对的事"的问题。

agent 在多轮执行中会发生两类认知失效：

- **目标漂移**：执行着执行着偏离了最初的 Picture，但每一步局部来看都"合理"
- **幻觉关闭**：agent 认为任务完成了，但实际上 Requirements 并未被满足

mem0ress 是一个**认知对齐协议**，不存储信息，而是在 agent 的每个执行轮次建立一个可验证的状态平面，确保 agent 始终知道：自己在哪里、目标是什么、偏差在哪里。

### MVP 的核心假设

> 一个 agent 要有意义地完成任何任务，最少需要三件事：
> **声明目标 → 推进执行 → 验证是否达成**

MVP 只交付这个最短闭环，但在架构上为完整协议预留所有扩展点。

---

## 2. 协议核心概念

### 2.1 PRC 模型

每个任务由三个要素锚定：

| 要素 | 定义 | 作用 |
|---|---|---|
| **Picture** | 任务完成时的理想状态描述 | 语义目标锚点，防漂移 |
| **Requirements** | 可机械验证的完成条件（含 `verify_cmd`） | 客观验收标准 |
| **Constraints** | 执行过程中不得违反的硬性约束 | 边界条件，持续监控 |

### 2.2 状态机

```
CREATED ──→ IN_PROGRESS ──→ [VERIFYING] ──→ COMPLETED
                 ↑                │
                 └────────────────┘ (judge FAILED，继续执行)
```

- `VERIFYING` 是 `/judge` 和 `/close` 执行期间的瞬态，不持久化
- MVP 不提供 `ABANDONED`（v0.2 引入）

### 2.3 五个协议文件

文件名固定，不可自定义：

| 文件 | 类型 | 内容 |
|---|---|---|
| `task.md` | 单文档，可覆写 | PRC + Todos + 当前状态 |
| `session.md` | 追加写，多文档 | 每轮执行快照 |
| `gotchas.md` | 追加写（MVP 为 stub） | 偏差记录 |
| `judge.md` | 追加写，多文档 | 检验报告历史 |
| `completion_summary.md` | 可选（v0.2） | 关闭摘要 |

### 2.4 工作区结构

```
<project_root>/
└── .mem0ress/
    ├── .current_task          # 当前活跃任务指针
    └── tasks/
        └── <task_id>/
            ├── task.md
            ├── session.md
            ├── gotchas.md
            └── judge.md
```

`.current_task` 格式：

```yaml
task_id: "implement-auth-flow"
activated_at: "2025-05-13T10:00:00+00:00"
```

---

## 3. 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│  Agent（Hermes）                                             │
│  职责：高层推理、创意工作、复杂决策                           │
│  不做：文件管理、协议执行、上下文压缩、模式检测               │
├─────────────────────────────────────────────────────────────┤
│  Skill（认知基础设施层）                                      │
│  职责：语义判断、上下文压缩、洞察生成、漂移检测               │
│  不做：具体文件读写、命令执行                                 │
│  实现：调用 Claude API + 调用 CLI                            │
├─────────────────────────────────────────────────────────────┤
│  CLI（协议物理执行层）                                        │
│  职责：确定性 I/O、verify_cmd 执行、状态机转换               │
│  不做：任何需要理解上下文的判断                               │
│  实现：mem0ress <command> [args]                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心原则

> **CLI 做机械执行，Skill 做认知处理。**  
> 判断标准：如果一个操作需要"理解"上下文才能做，它属于 Skill；如果给定输入就有确定输出，它属于 CLI。

Skill 不是 CLI 的套壳。它调用 CLI 获取原始数据，再通过 Claude API 对数据进行语义处理，最终输出的是 **agent 下一步推理所需的洞察**，而不是原始文件内容。

---

## 4. MVP 功能边界

### 纳入 MVP

| 功能 | 层级 | 说明 |
|---|---|---|
| Task 创建（PRC + Todos） | CLI | `mem0ress create` |
| Session 追加写 | CLI | 每轮快照持久化 |
| Todos 状态更新 | CLI | 覆写 task.md |
| .current_task 会话管理 | CLI | 单任务绑定，主动切换 |
| 状态机转换 | CLI | 机械判断 |
| Tier 0（Constraints 监控） | Skill | 语义扫描，非机械匹配 |
| Tier 2（Requirements 验收） | CLI + Skill | CLI 执行命令，Skill 解读失败 |
| 漂移检测 | Skill | 对比 Picture 与累积 session |
| 状态平面组装 | Skill | 压缩为 agent 可用上下文 |
| 关闭摘要 | Skill | Judge FAILED 时生成行动清单 |

### 推迟到 v0.2+

| 功能 | 原因 |
|---|---|
| Tier 3（语义 gap 检测） | 依赖独立 Judge Agent，复杂度跃升 |
| 父子任务可见性通道 | 单任务 MVP 中无意义 |
| completion_summary | `protocol.yaml` 已标记 optional |
| ABANDONED 状态 | MVP 单任务场景不需要 |
| 数据平面（Git 集成） | 独立的 diff 追踪体系 |
| 多 Worker 并发写 | `protocol.yaml` 已明确 v0.1 不支持 |
| Schema 严格校验 | Pydantic 字段校验已足够 |

---

## 5. Skill 设计：四个 Slash Commands

Skill 名称：`mem0ress`  
调用形式：`/create` `/turn` `/judge` `/close`

---

### `/create` — 任务声明

**输入参数：**

```yaml
task_id:      string   # slug 格式，如 "implement-auth-flow"
picture:      string   # 成功状态的自然语言描述
requirements: array    # 每项含 id / description / verify_cmd
constraints:  array    # 字符串列表，执行边界
todos:        array    # 可选，初始 todo 列表（字符串）
```

**CLI 做：**
- 检测 `.current_task` 是否非空，若非空则**警告并中止**（不静默覆盖）
- 创建 `.mem0ress/tasks/<task_id>/` 目录
- 写入 `task.md`（status: IN_PROGRESS）
- 初始化空的 `session.md` / `gotchas.md`（stub）/ `judge.md`
- 写入 `.current_task`（task_id + activated_at）

**Skill 做：**
- 校验 `requirements` 的 `verify_cmd` 字段是否全部存在（创建时即执行，不留"之后再定"的口子）
- 返回确认信息 + 初始状态平面

**输出：**

```
✓ Task created: implement-auth-flow
  Picture: mem0ress CLI 的 task.create 命令可用
  Requirements: 5 (all with verify_cmd)
  Constraints: 3
  Todos: 6
  Status: IN_PROGRESS
```

---

### `/turn` — 轮次推进

**输入参数：**

```yaml
progress:   string   # 本轮做了什么（自然语言）
todos_done: array    # 本轮完成的 todo id 列表（可选）
```

**CLI 做：**
- 读取 `.current_task`，若空则报错
- 读取 `task.md`，计算当前 turn 编号
- 追加 `TurnSnapshot` 到 `session.md`
- 更新 `task.md` 中对应 todos 的 `done` 状态

**Skill 做（这是关键）：**

1. **语义 T0（Constraint 监控）**  
   不是机械匹配 constraint_violations 字段，而是：  
   读取 `progress` 文本 + `constraints` 列表，通过 Claude API 判断：  
   "本轮进展中是否存在隐性约束违反？"  
   即使 agent 没有显式报告，也能从行为描述中检测信号。

2. **漂移检测**  
   对比 `picture`（目标锚点）与累积 `session` 内容，判断：  
   "执行方向是否偏离了 Picture 描述的成功状态？"  
   返回：`ON_TRACK` / `DRIFT_WARNING`（附偏离点描述）

3. **状态平面组装**  
   不返回原始文件内容，而是压缩为 agent 下一轮推理所需的信息：
   - 完成了什么 / 还剩什么
   - T0 结果（有无约束风险）
   - 漂移状态
   - 建议的下一步重点（非指令，是信息）

**输出示例：**

```
Turn 3 recorded
────────────────────────────────────────
Task: implement-auth-flow  [IN_PROGRESS]
Todos: 3/6 done
  ✓ Define TaskModel
  ✓ Implement workspace.py
  ✓ Implement CLI create
  ○ Write .current_task logic
  ○ Duplicate create warning
  ○ Write tests

T0 (Constraints): PASS
  No constraint violations detected

Alignment: ON_TRACK
  Progress aligns with Picture target
────────────────────────────────────────
```

**T0 WARN 时的输出示例：**

```
T0 (Constraints): WARN
  ⚠ Potential violation: "added requests library for HTTP call"
    Constraint: "不得在 create 时执行任何网络请求"
    Signal found in progress description. Verify intent.
```

---

### `/judge` — 主动检验

无输入参数（读取当前 task）。

**适用场景：** 开发调试阶段，agent 在认为"应该完成了"时主动触发，不必等到 `/close`。

**CLI 做：**
- 读取 `task.md` 获取所有 requirements
- 按顺序执行每个 `verify_cmd`（subprocess，60s timeout）
- 捕获 exit code + stdout + stderr
- **快速失败**：第一个 FAIL 后停止，不继续执行后续 requirements
- 追加原始结果到 `judge.md`

**Skill 做：**

1. **先运行 T0**（语义 Constraint 扫描，同 `/turn`）
2. T0 PASS 后才触发 T2（CLI 执行）
3. **失败解读**  
   不只返回"req_02 FAILED"，而是：  
   分析 verify_cmd 的 stdout/stderr + task 上下文，生成：  
   "具体哪里失败了，为什么失败，建议修复方向"

**输出示例（FAILED）：**

```
Judge Result: FAILED
────────────────────────────────────────
T0 (Constraints): PASS

T2 (Requirements):
  ✓ req_01: mem0ress create 执行成功
  ✓ req_02: 目录结构符合规范
  ✓ req_03: task.md 字段齐全
  ✗ req_04: .current_task 写入验证
    Exit code: 1
    Error: AssertionError: activated_at field missing

  ⊘ req_05: skipped (fast-fail)

Analysis:
  .current_task 文件存在且包含 task_id，但缺少 activated_at 字段。
  workspace.py 的 write_current_task() 可能未调用
  datetime.now().isoformat()。检查该函数的返回值构建逻辑。
────────────────────────────────────────
```

**输出示例（PASSED）：**

```
Judge Result: PASSED
────────────────────────────────────────
T0 (Constraints): PASS
T2 (Requirements): 5/5 PASS
  ✓ req_01 ✓ req_02 ✓ req_03 ✓ req_04 ✓ req_05

Ready to close.
────────────────────────────────────────
```

---

### `/close` — 任务关闭

无输入参数。`judge + complete` 的原子操作，不可分离。

**CLI 做：**
- 执行完整 T2（同 `/judge`）
- 全部 PASS → 写入最终 `judge.md`，状态转换 → `COMPLETED`，清空 `.current_task`
- 任何 FAIL → 拒绝关闭，写入 `judge.md`（记录失败历史）

**Skill 做：**

1. 先执行语义 T0
2. T0 PASS → 触发 CLI T2
3. **若 FAILED：生成 Closure Gap Analysis**  
   不是简单列出失败项，而是：  
   "距离关闭还差什么，按修复优先级排列，每项的预计修复成本（轮次估算）"  
   agent 拿到的是行动清单，不是失败报告

4. **若 PASSED：生成关闭确认**  
   简洁地确认任务关闭，附 Picture 的对齐验证

**关闭失败时的输出示例：**

```
Close: REJECTED
────────────────────────────────────────
T0: PASS  |  T2: 4/5 PASS

Gap Analysis (priority order):
  1. [HIGH] req_04: .current_task 缺少 activated_at 字段
     Fix: workspace.py write_current_task() 补充时间戳字段
     Estimated: 1 turn

  2. [BLOCKED] req_05: 依赖 req_04 修复后重新验证

Recommended: fix req_04 → run /judge → then /close
────────────────────────────────────────
```

**关闭成功时的输出示例：**

```
✓ Task COMPLETED: implement-auth-flow
────────────────────────────────────────
All requirements verified
Picture alignment confirmed
7 turns · 2 judge runs · 0 constraint violations
.current_task cleared
────────────────────────────────────────
```

---

## 6. 数据 Schema

### task.md（YAML，可覆写）

```yaml
task_id: "implement-auth-flow"
status: "IN_PROGRESS"
picture: |
  mem0ress CLI 的 task.create 命令可用。开发者执行 mem0ress create
  后，本地出现正确的目录结构和四个初始化文件，状态为 IN_PROGRESS。
requirements:
  - id: req_01
    description: "mem0ress create 命令执行成功（exit 0）"
    verify_cmd: "mem0ress create --task-id test-01 --picture 'test' --dry-run"
  - id: req_02
    description: "创建后目录结构符合协议规范"
    verify_cmd: "pytest tests/test_create.py::test_directory_structure"
constraints:
  - "只使用 Python 标准库 + typer + pydantic"
  - "不得在 create 时执行任何网络请求"
  - ".mem0ress 目录创建失败时必须以非零 exit code 退出"
todos:
  - id: todo_01
    description: "定义 TaskModel（pydantic）"
    done: true
  - id: todo_02
    description: "实现 fs/workspace.py 目录初始化逻辑"
    done: false
created_at: "2025-05-13T10:00:00+00:00"
updated_at: "2025-05-13T10:30:00+00:00"
```

### session.md（YAML，追加写，`---` 分隔）

```yaml
---
turn: 1
timestamp: "2025-05-13T10:05:00+00:00"
status: "IN_PROGRESS"
progress: "定义 TaskModel，字段齐全，pydantic v2，ty 检查通过"
todos_done: ["todo_01"]
constraint_violations: []
---
turn: 2
timestamp: "2025-05-13T10:20:00+00:00"
status: "IN_PROGRESS"
progress: "实现 workspace.py，create_task_dir() 创建四个文件"
todos_done: ["todo_02"]
constraint_violations: []
```

### judge.md（YAML，追加写，`---` 分隔）

```yaml
---
timestamp: "2025-05-13T11:00:00+00:00"
verdict: "FAILED"
t0:
  passed: true
  details: ""
t2:
  - req_id: req_01
    passed: true
    output: "OK"
    error: ""
  - req_id: req_02
    passed: false
    output: ""
    error: "AssertionError: activated_at field missing"
stopped_at: "req_02"
```

### gotchas.md（MVP 为 stub）

```yaml
# gotchas stub — v0.2 will implement full deviation tracking
```

---

## 7. CLI 命令参考

```bash
# 任务声明
mem0ress create \
  --task-id "implement-auth-flow" \
  --picture "CLI 的 create 命令可用..." \
  --requirements '[{"id":"req_01","description":"...","verify_cmd":"..."}]' \
  --constraints '["只使用标准库"]' \
  --todos '["定义 TaskModel", "实现 workspace.py"]'

# 轮次推进（Skill 调用，返回 JSON 供 Skill 处理）
mem0ress update \
  --progress "完成 TaskModel 定义" \
  --todos-done "todo_01,todo_02"

# 执行检验（返回原始结构化结果）
mem0ress judge

# 关闭任务（原子操作）
mem0ress close

# 会话管理
mem0ress current            # 查看当前绑定 task
mem0ress switch <task_id>  # 手动切换 task

# 开发辅助
mem0ress create --dry-run  # 不写文件，验证参数
mem0ress status            # 打印当前状态平面（原始）
```

所有命令输出 JSON（stdout），错误输出到 stderr，遵循 Unix exit code 约定。

---

## 8. 项目结构

```
mem0ress/
├── pyproject.toml              # uv 管理，ruff + ty 配置
│
├── src/mem0ress/
│   ├── __init__.py
│   ├── cli.py                  # typer CLI，所有 mem0ress 命令
│   │
│   ├── models/
│   │   ├── task.py             # Task, Requirement, Todo, TaskStatus
│   │   ├── session.py          # TurnSnapshot
│   │   ├── judge.py            # JudgeReport, TierResult, RequirementResult
│   │   └── current.py          # CurrentTask
│   │
│   ├── core/
│   │   ├── state.py            # 状态机转换逻辑
│   │   ├── judge.py            # T2 verify_cmd 执行逻辑
│   │   └── projection.py       # 原始状态平面组装（供 Skill 消费）
│   │
│   └── fs/
│       └── workspace.py        # 所有文件系统读写操作
│
├── skills/mem0ress/
│   ├── skill.yaml              # Skill manifest（命令定义 + 参数 schema）
│   └── skill.py                # Skill handler（调用 CLI + Claude API）
│
└── tests/
    ├── test_create.py
    ├── test_turn.py
    ├── test_judge.py
    └── test_close.py
```

---

## 9. 验证场景

### 场景一：白皮书撰写

**任务核心**：一份 4000-6000 字的 mem0ress 技术白皮书，包含五个指定章节，接入指南含可运行代码示例。

| 轮次 | 操作 | 结果 |
|---|---|---|
| — | `/create` | PRC 写入，verify_cmd 为 Python 脚本（字数、章节、代码块检查） |
| Turn 1-3 | `/turn` | 完成五章，T0 PASS，ON_TRACK |
| Turn 4 | `/judge` | req_02 FAIL：字数 3720 < 4000，Skill 定位至架构章节（最薄弱） |
| Turn 5 | `/turn` | 扩充架构和接入指南，总字数 4150 |
| Turn 6 | `/close` | 全部 PASS，COMPLETED |

**验证要点**：verify_cmd 不依赖测试框架，自定义脚本同样有效；Skill 对失败的定向分析优于"字数不够"。

---

### 场景二：软件开发

**任务核心**：mem0ress CLI `create` 命令可用，目录结构、文件 schema、`.current_task` 写入、重复创建警告均通过测试。

| 轮次 | 操作 | 结果 |
|---|---|---|
| — | `/create` | 5 个 requirements 全带 verify_cmd（pytest） |
| Turn 1-4 | `/turn` | 完成实现 + 测试，T0 全 PASS |
| Turn 5 | `/judge` | req_04 FAIL：`.current_task` 缺少 `activated_at`，Skill 定位至 `write_current_task()` |
| Turn 6 | `/turn` | 修复字段遗漏 |
| Turn 7 | `/close` | 5/5 PASS，COMPLETED |

**验证要点**：Judge 精确定位实现遗漏（不是需求歧义）；`/judge` 作为独立命令让修复循环更短。

---

## 10. Roadmap

```
v0.1-alpha（MVP）← 当前
  最小认知闭环
  单任务，本地 FS，CLI + Hermes Skill
  Tier 0（语义）+ Tier 2（机械）
  漂移检测，失败解读，关闭 Gap Analysis

v0.2
  子任务支持（parent/child 可见性通道）
  Tier 3：语义 gap 检测（Judge Agent）
  ABANDONED 状态
  completion_summary 自动生成
  Gotchas 完整实现（偏差追踪）

v0.3
  数据平面（Git commit 快照集成）
  状态平面可视化（mem0ress tree）
  Schema 严格校验

v0.4+
  多 Agent / 多 Worker 支持
  数据库后端（可选替换 FS）
  IDE 集成（VSCode / Cursor）
```

---

## 11. 设计约定与边界

### 必须在 MVP 中执行的约定

1. **Requirements 创建时即需 `verify_cmd`**，不接受"之后再补"——这是协议的核心约束
2. **`/create` 检测到 `.current_task` 非空时警告并中止**，不静默覆盖
3. **`/close` 是 judge + complete 的原子操作**，不可绕过验证直接关闭
4. **`.current_task` 关闭后清空（`task_id: ""`）而非删除**，保留文件以便明确报错
5. **CLI 全部输出 JSON**，不做人类可读格式化——格式化由 Skill 完成

### 协议不关心的事

- `verify_cmd` 用什么框架（pytest / 自定义脚本 / shell 命令均可）
- task_id 的命名约定（slug 是建议，不是约束）
- Picture 的长度和格式（自然语言即可）
- Todos 的粒度（agent 自己决定分解粒度）

---

*mem0ress — cognitive alignment, not just memory.*
