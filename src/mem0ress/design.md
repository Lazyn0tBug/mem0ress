# mem0ress Design — Phase 0 实现计划

> 本文档是 mem0ress 运行时的实现层规范，对应 spec.md（协议语义层）。
> spec.md 回答"是什么"，design.md 回答"怎么做"。

---

## 1. 核心定位（本次重构的关键变化）

### 1.1 三层职责划分

| 层 | 名称 | 职责 |
|---|---|---|
| Skill | Semantic Coordination Layer | 定义语义协调协议（问什么问题、如何算补全） |
| Agent | Semantic Reasoning | 在 Skill 引导下执行对话，补全语义 |
| CLI | Protocol Persistence Step | 根据会话结果执行协议持久化（创建/更新文件） |

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
/cog create
  ≠ create_task()
  = 一个认知操作开始

它可能触发：
  - 多轮交互
  - 语义澄清
  - 补全 Constraints
  - Agent 提案
  - Judge 检验 alignment
```

### 1.4 CLI 的定义

CLI = Protocol Persistence Step，不是主要交互界面。

交互的终点，最后才执行文件创建/更新。

---

## 2. 目录结构

Phase 0 使用 `.CAP/` 作为认知基座根目录，与 spec.md 的命名约定保持一致。

```
.CAP/
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
- `.CAP/` 而非 `.mem0ress/` —— 与 spec.md 的 Protocol 术语一致
- `task.md` 而非 `manifest.md` —— filesystem source of truth

---

## 3. Skill 协议（语义协调层）

Skill 通过 SKILL.md 向 Agent 描述语义协调协议，定义"可以请求什么认知操作"。

### 3.1 Skill 文件结构

```
skills/mem0ress/
└── mem0ress/
    ├── SKILL.md              # 语义协调协议描述
    └── references/
        └── protocol.yaml     # task.md 格式规范（从 spec §5.5 提取）
```

### 3.2 Skill 定义的认知操作

| 操作 | 语义含义 | 触发结果 |
|---|---|---|
| `create` | 开始一个任务的语义初始化 | 多轮补全 picture/requirements/constraints |
| `status` | 理解当前认知状态 | 渲染状态平面 |
| `snapshot` | 追加认知增量 | 压缩记录到 session.md |
| `gotcha` | 记录恢复关键发现 | 持久化到 gotchas.md |
| `verify` | 请求 Judge 验证 alignment | 触发隔离检验 |
| `decide` | 基于 Judge 结果决定下一步 | 读取判决，Agent 决策 |

---

## 4. `/cog create` — MVP 最小实现示例

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

### 4.2 `/cog create` 会话协议

```
Agent: /cog create <task_id>
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
CLI persistence：创建 .CAP/tasks/<task_id>/task.md
```

### 4.3 MVP 实现路径

**Phase 1：Skill 层（语义协调协议）**
- [ ] 创建 `skills/mem0ress/mem0ress/SKILL.md`
- [ ] 定义认知状态评估规则（何时需要 Clarification / Analysis / Judge）
- [ ] 创建 `references/protocol.yaml`（从 spec §5.5 提取）

**Phase 2：CLI 层（Persistence）**
- [ ] 简化 `/cog create` 命令，只接收最终补全结果
- [ ] 按 protocol.yaml 创建 task.md
- [ ] 不做复杂交互，交给 Skill 引导的主 Agent 对话

**Phase 3：Agent 侧**
- [ ] Agent 加载 Skill 后，在 `/cog create` 触发时按 Skill 的认知路由进行对话
- [ ] 对话完成后调用 CLI 命令执行持久化

### 4.4 CLI 命令规格（MVP）

```bash
/cog create <task_id> \
  --picture "语义成功状态描述" \
  --requirements "req1; req2; ..." \
  --constraints "红线1; 红线2; ..."
```

MVP 阶段：CLI 只做参数接收和文件创建，语义补全路由交给 Skill 引导的对话。

---

## 5. 文件协议（Phase 0）

### 5.1 task.md

Semantic authority surface（语义权威表面），格式由 `references/protocol.yaml` 定义。

```yaml
---
id: {task_id}
type: task
status: created
cognitive_triad:
  picture: "{语义目标描述}"
  requirements:
    - id: req_01
      description: "{需求描述}"
      verify_cmd: null  # MVP: stub
  constraints:
    - "{约束1}"
    - "{约束2}"
gotcha_refs: []
---
# Todos
- [ ] {todo_1}
- [x] {todo_2}
```

### 5.2 session.md

Append-only cognition delta stream（追加式认知增量流）。

```markdown
## Turn N @ {timestamp}

{压缩后的语义增量}
```

**压缩规则（MVP Phase 0）：**
- 不持久化 chain-of-thought
- 不持久化原始执行日志
- 只记录：发现、决策、进展

### 5.3 gotchas.md

Recovery-critical discoveries（恢复关键发现）。

```markdown
## Gotcha N @ {timestamp}

{关键发现内容}
```

### 5.4 judge.md

Judge verification surface（Judge 验证表面）。

```markdown
# Judge Report — {task_id}

**Generated**: {timestamp}

## Tier 0 — PASS/FAIL
{message}

## Tier 1 — PASS/FAIL
{message}

## Tier 3 — (Agent 自主判断)
{reasoning}
```

---

## 6. 生命周期（Phase 0）

```
1. /cog create          → Skill 引导补全 picture/requirements/constraints
2. Execute Work         → (Agent 自主执行)
3. /cog snapshot        → 追加认知增量到 session.md
4. /cog gotcha          → 记录关键发现（可选）
5. /cog verify          → 触发 Judge 隔离验证
6. /cog decide          → 基于判决结果决定下一步
```

---

## 7. 其他命令规格

### 7.1 `/cog status`

渲染当前状态平面（Tree 可视化）。

```
输入: /cog status [--root .CAP]
输出: Rich tree
  ■ {task_id} [{done}/{total}] {STATUS}
     ! {gotcha}
     └─ {subtask}
```

### 7.2 `/cog recover`

解析协议文件，重建认知表面，返回给 Agent 恢复所需的关键信息。

```
输入: /cog recover [--root .CAP]
输出:
  picture: {picture}
  active requirements: [{id}: {description}]
  active todos: [{text}]
  unresolved gotchas: [{content}]
  recent deltas: [{turn} {content}]
  latest verification state: {status}
```

### 7.3 `/cog snapshot`

追加认知增量到 session.md。

```
输入: /cog snapshot {content} [--root .CAP]
规则:
  - 必须压缩（不得包含原始日志、chain-of-thought）
  - 必须有语义（记录发现、决策、进展）
  - 追加不覆盖
格式:
  ## Turn N @ {timestamp}
  {content}
```

### 7.4 `/cog gotcha`

追加关键发现到 gotchas.md。

```
输入: /cog gotcha {content} [--root .CAP]
适用场景:
  - 语义模糊
  - 不稳定假设
  - 漂移风险
  - 未解 blocker
格式:
  ## Gotcha N @ {timestamp}
  {content}
```

### 7.5 `/cog verify`

触发 Judge 隔离验证。

```
输入: /cog verify [--root .CAP]
隔离保证:
  - Judge 只接收 task_id + filesystem protocol
  - Judge 不得接收 runtime memory / hidden state / full history
Tier 执行:
  - Tier 0: constraint violations（同步执行）
  - Tier 1: todo completion（同步执行）
  - Tier 2: verify_cmd（MVP: stub 不执行，v0.2+ 实现）
  - Tier 3: semantic alignment（Agent 自主判断）
输出:
  Tier 0: PASS/FAIL
  Tier 1: PASS/FAIL
  Tier 2: (stub)
  Tier 3: (Agent 判断请求)
```

### 7.6 `/cog decide`

读取 judge.md 判决结果，Agent 决定下一步动作。

```
输入: /cog decide [--root .CAP]
决策权永远属于 Hermes，skill 不得自主决定。
输出:
  - 最新 judge 判决摘要
  - Tier 0/1 是否通过
  - Tier 3 判决状态
  - 下一步建议（给 Agent 参考，不是指令）
```

---

## 8. 实现步骤

### Step 1: 目录改名 + data plane 结构

- [ ] 将 `.mem0ress/` 改为 `.CAP/`
- [ ] 在 `init` 命令中创建 `data/outputs/`, `data/evidence/`, `data/artifacts/` 目录
- [ ] 将 `--root` 默认值从 `.mem0ress` 改为 `.CAP`

### Step 2: `/cog recover` 命令

- [ ] 实现 `RecoveredCognition` 数据类
- [ ] 实现 `recover_cognition()` 函数，解析 task.md + session.md + gotchas.md
- [ ] 添加 CLI 命令 `/cog recover`

### Step 3: `/cog gotcha` 命令

- [ ] 实现 `append_gotcha()` 函数
- [ ] 添加 CLI 命令 `/cog gotcha`
- [ ] 模板：`gotchas.md`

### Step 4: `/cog decide` 命令

- [ ] 实现 `read_judge_verdict()` 函数
- [ ] 添加 CLI 命令 `/cog decide`
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

## 10. 验证场景

### Scenario A — 白皮书写作

```
/cog recover
    ↓
write section
    ↓
/cog snapshot
    ↓
identify ambiguity
    ↓
/cog gotcha
    ↓
/cog verify
```

成功标准：
- 白皮书存活于中断
- 认知从协议重建
- gotchas 改善连续性

### Scenario B — 软件开发

```
/cog recover
    ↓
implement feature
    ↓
/cog snapshot
    ↓
run tests
    ↓
/cog verify
    ↓
/cog decide
```

成功标准：
- 实现存活于 context reset
- snapshots 保持压缩
- Judge 验证保持隔离
- runtime 保持确定性

---

## 11. 失败条件

| 失败 | 含义 |
|------|------|
| session.md 变成 transcript | 压缩失败 |
| recovery 需要完整回放 | 认知失败 |
| runtime 吸收 reasoning | 架构失败 |
| Judge 收到 hidden state | 隔离失败 |
| slash commands 变成 workflows | 协议失败 |
| Skill 变成 workflow coordinator | CAP 回归 orchestration 框架 |
