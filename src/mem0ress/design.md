# mem0ress Design — Phase 0 实现计划

> 本文档是 mem0ress 运行时的实现层规范，对应 spec.md（协议语义层）。
> spec.md 回答"是什么"，design.md 回答"怎么做"。

---

## 1. 核心定位

### 1.1 三层职责划分

| 层 | 名称 | 职责 |
|---|---|---|
| Skill | Semantic Coordination Layer | 定义语义协调协议（问什么问题、如何算补全） |
| Agent | Semantic Reasoning | 在 Skill 引导下执行对话，补全语义 |
| Stable Capability Runtime | Protocol Persistence Step | 根据会话结果执行协议持久化（创建/更新文件） |

### 1.2 Skill 的定义

Skill = Semantic Coordination Layer，不是 Workflow Coordinator。

**Skill 可以：**
- 请求补充 Picture
- 请求澄清 Constraints
- 请求验证 Requirement
- 请求 Judge 重新解释 alignment
- 请求 Agent 生成候选方案

**Skill 不得拥有：**
- workflow DAG
- execution pipeline
- state machine orchestration
- procedural execution graph

### 1.3 Slash Command 的定义

Slash Command = Semantic Interaction Entrypoint，不是 Command Binding。

```
/cap create
  ≠ create_task()
  = 一个认知操作开始

它可能触发：
  - 多轮交互
  - 语义澄清
  - 补全 Constraints
  - Agent 提案
  - Judge 检验 alignment
```

### 1.4 Stable Capability Runtime 的定义

Stable Capability Runtime = Protocol Persistence Step，不是主要交互界面。

交互的终点，最后才执行文件创建/更新。

### 1.5 Cognitive Focus Principle

**核心原则**：

Phase 0 使用 `.cap/` 作为认知基座根目录，与 spec.md 的命名约定保持一致。

```
.cap/
└── tasks/
    └── {task_id}/
        ├── task.md           # 任务清单（语义权威表面）
        ├── session.md        # 追加式认知增量流
        ├── gotchas.md        # 关键发现记录
        ├── judge.md          # Judge 验证结果
        │
        └── data/             # data plane
            ├── outputs/      # 执行产物
            ├── evidence/     # 证据文件
            └── artifacts/    # 生成物
```

**与 spec 命名约定的对齐：**
- `.cap/` —— 与 spec.md 的 Protocol 术语一致
- `task.md` 而非 `manifest.md` —— filesystem source of truth

---

## 2. CLI Design

CLI 是 Stable Capability Runtime 的第一种实现形态。

### 2.1 命令表面

| 命令 | 功能 | 类型 |
|------|------|------|
| `mem0 init` | 初始化认知基座 | setup |
| `mem0 status` | 渲染状态平面 | query |
| `mem0 create` | 创建任务（含 task_id 生成） | write |
| `mem0 abandon` | 标记任务废弃 | write |
| `mem0 update` | 追加认知增量到 session.md | write |
| `mem0 judge` | 触发 Tier 0/1/2 验证 | write |
| `mem0 close` | judge 通过后标记 COMPLETED | write |
| `mem0 done` | close 的别名 | write |
| `mem0 report` | 显示最新 judge 报告 | query |

### 2.2 create 命令

```bash
mem0 create \
  --picture "语义成功状态描述" \
  --requirements "req1; req2; ..." \
  --constraints "红线1; 红线2; ..."
```

### 3.2 Skill 定义的认知操作

| 操作 | 语义含义 | 触发结果 |
|---|---|---|
| `/cap create` | 开始一个任务的语义初始化 | 多轮补全 picture/requirements/constraints |
| `/cap status` | 理解当前认知状态 | 渲染状态平面 |
| `/cap amend` | 修正 verify.md 未确认条目 | 交互式条目编辑 |
| `/cap snapshot` | 追加认知增量 | 压缩记录到 session.md |
| `/cap gotcha` | 记录恢复关键发现 | 持久化到 gotchas.md |
| `/cap verify` | 请求 Judge 验证 alignment | 触发隔离检验 |
| `/cap decide` | 基于判决结果决定下一步 | 读取 judge.md 判决摘要 |

---

## 4. `/cap create` — MVP 最小实现示例

### 4.1 核心概念：Semantic Coordination vs Procedural Orchestration

Skill 是 **Semantic Coordination Layer**，不是 Workflow Orchestrator。

| | Procedural Orchestration | Semantic Coordination |
|---|---|---|
| 模式 | 先做A，再做B，再做C | 当前缺什么，补什么 |
| 控制流 | 固定流程 | 动态路由 |
| 分派对象 | 子任务/子Agent | 认知模式切换 |

Skill 根据当前认知状态，动态引导主 Agent 进入正确的认知模式：

```
主 Agent + Judge Agent（仅此两者）
    ↓
Skill 评估认知状态
    ↓
Picture 不明确 → 主 Agent 进入 Clarification Mode
Constraints 冲突 → 主 Agent 进入 Analysis Mode
Requirements 需验证 → 主 Agent 请求 Judge Agent 验证
    ↓
补全完成 → CLI persistence
```

### 4.2 `/cap create` 会话协议

```
Agent: /cap create
       ↓
Skill 评估当前认知状态（三要素是否完整）
       ↓
缺失 Picture？
  → 主 Agent Clarification Mode："这个任务的语义成功状态是什么？"
       ↓
Constraints 冲突？
  → 主 Agent Analysis Mode："这些约束之间是否存在矛盾？"
       ↓
Requirements 不可验证？
  → 主 Agent 请求 Judge Agent 确认
       ↓
主 Agent 确认补全完成
       ↓
CLI persistence：创建 .cap/tasks/<task_id>/task.md
```

### 4.3 MVP 实现路径

**Phase 1：Skill 层（语义协调协议）**
- [ ] 创建 `skills/mem0ress/mem0ress/SKILL.md`
- [ ] 定义认知状态评估规则（何时需要 Clarification / Analysis / Judge）
- [ ] 创建 `references/protocol.yaml`（从 spec §5.5 提取）

**Phase 2：CLI 层（Persistence）**
- [ ] 简化 `/cap create` 命令，只接收最终补全结果
- [ ] 按 protocol.yaml 创建 task.md
- [ ] 不做复杂交互，交给 Skill 引导的主 Agent 对话

**Phase 3：Agent 侧**
- [ ] Agent 加载 Skill 后，在 `/cap create` 触发时按 Skill 的认知路由进行对话
- [ ] 对话完成后调用 CLI 命令执行持久化

### 4.4 CLI 命令规格（MVP）

```bash
/cap create \
  --picture "语义成功状态描述" \
  --requirements "req1; req2; ..." \
  --constraints "红线1; 红线2; ..."
```

**内部流程**：

1. 生成 6 位 base36 task_id：`{timestamp_low}{counter}`
2. 创建 `.mem0ress/tasks/<task_id>/`
3. 生成 task.md（via SubstrateParser）
4. 生成 session.md、gotchas.md、judge.md
5. 更新 `.current_task` 指针

### 2.3 close 命令

```bash
mem0 close <task_id>
```

**内部流程**：

1. 解析 task_id
2. 调用 `HarnessRunner.verify_task()` 执行 Tier 0/1/2
3. 任何 Tier FAIL → 打印失败项，exit 1
4. 全部 PASS → `TaskServiceImpl.complete_task()` → status=COMPLETED
5. 清理 `.current_task` 指针

**No bypass rule**：不经过 Judge 验证的任务不得 close。

### 2.4 其他命令

**status**：`mem0 status [--root .mem0ress]`
渲染 Rich tree 状态平面。

**update**：`mem0 update [--content "..."]`
追加 Turn snapshot 到 session.md，压缩记录，不含 chain-of-thought。

**judge**：`mem0 judge [--root .mem0ress]`
执行 Tier 0/1/2，输出纯文本 PASS/FAIL（无 ANSI markup）。

**abandon**：`mem0 abandon <task_id>`
标记 task.md status=ABANDONED。

**done**：close 的别名，内部调用同一逻辑。

**report**：`mem0 report <task_id>`
读取 judge.md，打印最新验证报告。

### 2.5 文件协议落地

| 文件 | CLI 职责 |
|------|---------|
| `task.md` | TaskServiceImpl.create_task() 生成，SubstrateParser 序列化 |
| `session.md` | TaskServiceImpl.update_session() 追加 Turn 块 |
| `gotchas.md` | TaskServiceImpl.append_gotcha() 追加 Gotcha 块 |
| `judge.md` | HarnessRunner.verify_task() 写入验证报告 |
| `verify.md` | 主 Agent 追加 verify marker，Judge Agent 只读 |

所有文件格式见 spec.md §5.4 文档数据模型。

### 2.6 目录结构

```
.mem0ress/
├── .current_task              # 当前激活任务指针
└── tasks/
    └── {task_id}/
        ├── task.md           # 任务清单
        ├── session.md        # 认知增量流
        ├── gotchas.md        # 关键发现
        ├── judge.md          # 验证报告
        ├── verify.md         # 验证 marker
        │
        └── data/             # data plane
            ├── outputs/
            ├── evidence/
            └── artifacts/
```

### 2.7 .current_task 指针

```yaml
task_id: '2k5m3x'
activated_at: '2026-05-14T10:00:00+09:00'
```

- `create` → 写入 task_id + timestamp
- `update/judge/close` → 无 task_id 时读取此指针
- `close` 成功 → 清除 task_id，保留 activated_at

**安全机制**：`safe_write` + SHA-256 hash comparison，并发写入触发 ConflictError。

### 2.8 task_id 生成算法

6 位 base36 字符串：

```
{4 chars: timestamp_low}{2 chars: counter}
```

- **timestamp_low**：`floor(unix_time / 64) % 36^4`，约 12 天循环
- **counter**：进程内单调计数器，保证同窗口内唯一

---

## 6. 生命周期（Phase 0）

```
1. /cap create          → Skill 引导补全 picture/requirements/constraints
2. Execute Work         → (Agent 自主执行)
3. /cap amend           → 修正 verify.md 未确认条目（任意时刻）
4. /cap snapshot        → 追加认知增量到 session.md
5. /cap gotcha          → 记录关键发现（可选）
6. /cap verify          → 触发 Judge 隔离验证
7. /cap decide          → 基于判决结果决定下一步
```

---

## 7. 其他命令规格

### 7.1 `/cap status`

渲染当前状态平面（Tree 可视化）。

```
输入: /cap status [--root .cap]
输出: Rich tree
  ■ {task_id} [{done}/{total}] {STATUS}
     ! {gotcha}
     └─ {subtask}
```

### 7.2 `/cap recover`

解析协议文件，重建认知表面，返回给 Agent 恢复所需的关键信息。

```
输入: /cap recover [--root .cap]
输出:
  picture: {picture}
  active requirements: [{id}: {description}]
  active todos: [{text}]
  unresolved gotchas: [{content}]
  recent deltas: [{turn} {content}]
  latest verification state: {status}
```

### 7.3 `/cap snapshot`

追加认知增量到 session.md。

```
输入: /cap snapshot {content} [--root .cap]
规则:
  - 必须压缩（不得包含原始日志、chain-of-thought）
  - 必须有语义（记录发现、决策、进展）
  - 追加不覆盖
格式:
  ## Turn N @ {timestamp}
  {content}
```

### 7.4 `/cap gotcha`

追加关键发现到 gotchas.md。

```
输入: /cap gotcha {content} [--root .cap]
适用场景:
  - 语义模糊
  - 不稳定假设
  - 漂移风险
  - 未解 blocker
格式:
  ## Gotcha N @ {timestamp}
  {content}
```

### 7.5 `/cap verify`

触发 Judge 隔离验证。

```
输入: /cap verify [--root .cap]
隔离保证:
  - Judge 只接收 task_id + filesystem protocol
  - Judge 不得接收 runtime memory / hidden state / full history
Tier 执行:
  - Tier 0: constraint violations（同步执行）
  - Tier 1: todo completion（同步执行）
  - Tier 2: verify.md marker（读取 `[(.)/(.)/{.}]` 执行命令；`[\✓]/(\✓)/{\✓}` 为已完成状态，不可 amend）
  - Tier 3: semantic alignment（Agent 自主判断）
输出:
  Tier 0: SUSPEND（violation → 暂停，不 FAIL；解决后继续；人可 override）
  Tier 1: PASS/FAIL
  Tier 2: PASS/FAIL（stub）
  Tier 3: UNCERTAIN / PASS / FAIL

Tier 0 语义约束：Constraint 违规不等于任务失败。违规时任务 SUSPEND，等待解决；解决后继续。人判断无法解决时可 override 继续（附理由）。Tier 3 语义约束：证据不足时必须返回 UNCERTAIN，不得强行 PASS。

### 7.5.1 verify.md 三类实体状态机

**Non-persistent requirement：**

```
[] → [.] → [\✓]  (永久完成，不退回)
```

**Persistent requirement：**

```
[] → [.] → [\✓]  (阶段性完成；下一轮次出现新的语义漂移时，可退回 [.] 重新验证)
```

- `[\✓]` 标记时机：至少一个 todo 完成 + 至少一轮次结束 + Tier 2 验证通过
- 退回触发：下一轮次发现新的语义漂移，由 Judge 或人主动提出

**Constraint：**

```
[] → [.] → [\✓]  (已解决)
           ↓
        [×]  (violated — suspended，等待解决)
```

- `[\✓]` = 约束已解决
- `[×]` = 约束违规中（suspended，不 FAIL，解决后继续）
- 每轮次必须重新验证
```

### 7.6 `/cap decide`

读取 judge.md 判决结果，Agent 决定下一步动作。

```
输入: /cap decide [--root .cap]
决策权永远属于 Hermes，skill 不得自主决定。
输出:
  - 最新 judge 判决摘要
  - Tier 0/1 是否通过
  - Tier 3 判决状态
  - 下一步建议（给 Agent 参考，不是指令）
```

### 7.7 `/cap amend`

在任意时刻修正 verify.md 条目。仅允许未确认条目（`[]`/`()`/`{}`）。

```
输入: /cap amend [--root .cap]
交互:
  - 仅展示未确认条目
  - TUI: 更新现有 / 新增
  - 已确认条目（[.]/(.)/.）不可修改
  - 已完成条目（[\✓]/(\✓)/{\✓}）不可修改
输出:
  - session.md 追加 amend 记录
```

---

## 8. 实现步骤

### Step 1: 目录改名 + data plane 结构

- [x] 将 `.mem0ress/` 改为 `.cap/`
- [ ] 在 `init` 命令中创建 `data/outputs/`, `data/evidence/`, `data/artifacts/` 目录
- [x] 将 `--root` 默认值从 `.mem0ress` 改为 `.cap`

### Step 2: `/cap recover` 命令

- [ ] 实现 `RecoveredCognition` 数据类
- [ ] 实现 `recover_cognition()` 函数，解析 task.md + session.md + gotchas.md
- [ ] 添加 CLI 命令 `/cap recover`

### Step 3: `/cap gotcha` 命令

- [ ] 实现 `append_gotcha()` 函数
- [ ] 添加 CLI 命令 `/cap gotcha`
- [ ] 模板：`gotchas.md`

### Step 4: `/cap decide` 命令

- [ ] 实现 `read_judge_verdict()` 函数
- [ ] 添加 CLI 命令 `/cap decide`
- [ ] 输出格式化判决摘要

### Step 5: Skill 层（语义协调协议）

- [ ] 创建 `skills/mem0ress/mem0ress/SKILL.md`
- [ ] 创建 `skills/mem0ress/mem0ress/references/protocol.yaml`
- [ ] 定义 `create` 的对话协议（三要素补全）
- [ ] 定义其他命令的语义协调协议

### Step 6: 验证 + 清理

- [ ] 运行 `ty check src/`
- [ ] 运行 `ruff check src/`
- [ ] 运行 `pytest tests/`
- [ ] 提交

---

## 9. 技术栈

| 层级 | 技术 |
|------|------|
| Runtime | Python 3.12 |
| 依赖管理 | uv |
| 项目管理 | pyproject.toml |
| CLI | Typer |
| 验证模型 | Pydantic |
| Lint | Ruff |
| 类型检查 | ty |
| 可视化 | Rich |

---

## 4. 验证场景

### Scenario A — 白皮书写作

```
/cap recover
    ↓
write section
    ↓
/cap snapshot
    ↓
identify ambiguity
    ↓
/cap gotcha
    ↓
/cap verify
```

成功标准：白皮书存活于中断；认知从协议重建；gotchas 改善连续性。

### Scenario B — 软件开发

```
/cap recover
    ↓
implement feature
    ↓
/cap snapshot
    ↓
run tests
    ↓
/cap verify
    ↓
/cap decide
```

成功标准：实现存活于 context reset；snapshots 保持压缩；Judge 验证保持隔离；runtime 保持确定性。

---

## 5. 失败条件

| 失败 | 含义 |
|------|------|
| session.md 变成 transcript | 压缩失败 |
| recovery 需要完整回放 | 认知失败 |
| runtime 吸收 reasoning | 架构失败 |
| Judge 收到 hidden state | 隔离失败 |
| slash commands 变成 workflows | 协议失败 |
| Skill 变成 workflow coordinator | CAP 回归 orchestration 框架 |

---

## 6. 实现步骤

### Step 1: 验证

- [ ] 运行 `ty check src/`
- [ ] 运行 `ruff check src/`
- [ ] 运行 `pytest tests/`
- [ ] 提交

---

*其余内容待补充。*