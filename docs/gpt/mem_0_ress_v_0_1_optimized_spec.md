# mem0ress v0.1 规约草案

## 副标题

**面向长路径 AI Agent 的轻量级任务状态牵引框架**  
*A lightweight task-state harness for long-running AI agents.*

---

## 0. 摘要

mem0ress 是一个面向 AI Agent 的任务状态管理与目标对齐框架。它不试图成为新的向量记忆系统，也不试图保存全部历史对话，而是通过结构化任务模型、轮次快照和状态平面，让 Agent 在长路径任务中始终知道：

- 当前目标是什么；
- 已经完成了什么；
- 还有哪些需求未满足；
- 哪些约束不能违反；
- 当前操作对应哪个代码或文件版本；
- 下一步应该继续推进、修正、等待用户，还是终止任务。

mem0ress 的核心假设是：

> 长任务 Agent 的主要失败模式，不是缺少历史信息，而是缺少持续、清晰、可验证的当前任务状态。

因此，mem0ress 的目标不是“让 Agent 记住更多”，而是“让 Agent 更少迷路”。

---

## 1. 问题定义

### 1.1 Agent 长任务中的结构性失败

在多轮代码开发、文档生成、业务分析、复杂项目执行等长路径任务中，Agent 常见的问题包括：

1. **目标漂移**  
   Agent 在多轮执行后逐渐偏离用户最初目标，开始优化局部问题，而忘记整体完成状态。

2. **约束遗忘**  
   用户曾经明确提出的限制条件被后续上下文冲淡，例如“不要改动 API”“不要引入新依赖”“保持现有 UI 风格”。

3. **重复失败路径**  
   Agent 反复尝试已经证明失败的方案，无法稳定记录“这个方向走不通”。

4. **进度感缺失**  
   Agent 能看到大量历史对话，却无法回答“当前任务完成到哪一步”。

5. **恢复能力差**  
   会话中断或上下文压缩后，Agent 很难准确恢复任务状态。

6. **完成判断薄弱**  
   Agent 经常完成 Todo 列表，却没有真正满足用户想要的最终结果。

### 1.2 为什么传统 Memory 不足够

传统 Agent memory 系统通常围绕“历史信息召回”设计。它们擅长回答：

> 之前讨论过什么？

但长任务执行中，Agent 更需要回答的是：

> 我现在在哪里？  
> 我的目标是什么？  
> 我离目标还有多远？  
> 我有没有偏离约束？  
> 我下一步应该做什么？

这类问题不能单靠向量相似度检索解决。因为当前任务状态不是一组相似片段，而是一个由目标、需求、约束、进度、版本和偏差共同构成的结构化状态。

mem0ress 因此不把“当前任务状态”建立在向量检索之上，而是建立在任务结构和状态快照之上。外部知识检索、代码检索、文档检索仍然可以由宿主 Agent 按需完成，但 mem0ress 只负责维护当前任务状态。

---

## 2. 系统定位

### 2.1 mem0ress 是什么

mem0ress 是一个本地文件系统驱动的 Agent task-state harness。

它提供：

- 任务定义协议；
- 任务状态文件；
- 轮次快照记录；
- 状态平面生成；
- 数据版本指针；
- Gotcha 偏差记录；
- 可选 Judge 检验流程；
- CLI 与 Agent Hook 接入方式。

### 2.2 mem0ress 不是什么

mem0ress 不是：

- 不是向量记忆库；
- 不是 RAG 系统；
- 不是 Agent 框架；
- 不是项目管理软件；
- 不是 Todo App；
- 不是测试框架；
- 不是 Observability 平台；
- 不是数据库；
- 不是替代 Git 的版本控制系统。

它只做一件事：

> 为长路径 Agent 提供当前任务状态、目标对齐和执行边界。

### 2.3 与现有系统的关系

mem0ress 位于 Agent 应用架构中的 Harness 层。

```text
Agent
  │
Skills / Workflows
  │
Tools / API / MCP / CLI / Files / Git
  │
Host Environment

mem0ress 横向贯穿上述结构：
Context + Task State + Progress + Constraints + Verification
```

它不替代 API、MCP、CLI、RAG、Git 或 Agent 框架，而是把这些工具的执行过程绑定到一个清晰的任务状态中。

---

## 3. 核心设计原则

### 3.1 当前状态优先于历史回忆

mem0ress 不追求保存完整历史，而是追求在任意时刻生成一个紧凑、准确、可判断的当前任务视图。

### 3.2 任务是认知单元

mem0ress 以 Task 作为唯一基本单元。父任务、子任务、检查任务都使用同构结构，避免引入 Epic、Story、Milestone 等额外概念。

### 3.3 目标、需求、约束必须分离

一个任务必须同时具备：

- Picture：任务完成后的语义图景；
- Requirements：可验证需求；
- Constraints：不可逾越或需要警告的边界。

Todo 只是执行路径，不是任务完成的最终标准。

### 3.4 状态与数据版本分离

状态平面回答“任务推进到哪里”；数据平面回答“当前操作对应哪个代码或文件版本”。

Git 可以回滚代码，但用户反馈、外部 API 状态、协作者输入等外部状态不能回滚。因此认知状态默认向前构建，数据版本可以按需回溯。

### 3.5 默认投影 Active Context，而不是全量状态

mem0ress 保留完整状态源，但默认只向 Agent 注入当前活跃任务路径，以避免状态平面自身变成新的上下文污染源。

默认注入内容包括：

- 当前任务；
- 父任务链；
- 直接子任务；
- 未完成 Requirements；
- 被违反或待确认 Constraints；
- 未解决 Gotchas；
- 最近状态变化；
- 下一步建议。

全量任务树可以按需展开。

---

## 4. 核心概念

### 4.1 Task

Task 是 mem0ress 的基本认知单元。

每个 Task 代表一个有明确目标、完成标准、约束边界和进度状态的工作单元。

一个 Task 可以包含子任务。父任务完成的前提是所有直接子任务均处于已关闭状态。

已关闭状态包括：

- COMPLETED；
- ABANDONED；
- SUPERSEDED。

### 4.2 Picture

Picture 是任务完成后的语义成功状态。

它回答：

> 如果任务完成了，利益相关者看到的结果应该是什么样子？

Picture 必须描述结果，而不是实现路径。

示例：

```text
好的 Picture：用户无需输入密码，即可通过 Google 或 GitHub 完成登录。
不好的 Picture：使用 OAuth 2.0 实现 Google Login。
```

Picture 是任务完成的最终判断锚点。Requirements 是必要条件，但 Requirements 全部满足不必然等于 Picture 达成。

### 4.3 Requirements

Requirements 是从 Picture 推导出的可验证需求。

它回答：

> 为了证明 Picture 基本达成，哪些条件必须被验证？

每个 Requirement 应当具备明确验收方式。

示例：

```yaml
requirements:
  - id: R1
    text: 支持 Google OAuth 登录
    verification: 用户可以通过 Google 账号完成登录并进入首页
  - id: R2
    text: 支持 GitHub OAuth 登录
    verification: 用户可以通过 GitHub 账号完成登录并进入首页
```

### 4.4 Constraints

Constraints 是任务执行过程中不能违反或需要警告的边界。

建议分为两类：

#### Hard Constraints

可自动检测，违反后应阻断任务完成。

示例：

```yaml
constraints:
  - id: C1
    type: hard
    text: 不得修改 public API 签名
    detection: diff_check
```

#### Soft Constraints

需要人工或语义判断，违反后应提示警告，不一定阻断流程。

示例：

```yaml
constraints:
  - id: C2
    type: soft
    text: 文档语气应保持专业、克制、非营销化
    detection: human_or_llm_review
```

### 4.5 Todos

Todos 是执行路径，不是最终完成标准。

Todo 用于推进任务，但任务是否完成仍然取决于：

1. Constraints 是否未被违反；
2. Todos 和直接子任务是否关闭；
3. Requirements 是否满足；
4. Picture 是否在语义上达成。

### 4.6 Gotchas

Gotchas 是偏差、失败路径、风险事件和重要经验的记录。

Gotcha 不阻塞主流程，但会在状态平面中显示为提醒。

示例：

```yaml
- id: G1
  status: open
  text: 直接修改 auth middleware 会破坏现有 session 流程，已尝试失败。
  linked_task: oauth_login
  created_at: 2026-05-11T10:30:00+09:00
```

### 4.7 Session

Session 是轮次快照序列。

每个 Agent 执行轮次结束后，mem0ress 追加一条 Session 快照，用于记录本轮发生的状态变化。

Session 不保存完整对话，也不替代日志系统。它只记录与任务状态推进有关的信息。

### 4.8 Status Plane

Status Plane 是 mem0ress 注入给 Agent 的当前状态视图。

它回答：

> 我当前在做什么？  
> 做到哪里了？  
> 有哪些未完成或风险？  
> 下一步应该注意什么？

Status Plane 是运行时组装结果，不是单独维护的数据库表。

### 4.9 Data Plane

Data Plane 是代码、文件或数据版本指针。

在 v0.1 中，Data Plane 主要记录 Git commit ID。

示例：

```yaml
data_plane:
  repos:
    frontend: "a1b2c3d"
    backend: "e4f5g6h"
```

Data Plane 默认不完整展开，只作为状态恢复和溯源指针。

---

## 5. 任务状态机

### 5.1 状态定义

```yaml
states:
  - CREATED
  - IN_PROGRESS
  - BLOCKED
  - NEEDS_USER
  - VERIFYING
  - COMPLETED
  - FAILED
  - ABANDONED
  - SUPERSEDED
```

### 5.2 状态说明

| 状态 | 含义 |
|---|---|
| CREATED | 任务已创建，PRC 已定义，但尚未开始执行 |
| IN_PROGRESS | 任务正在执行 |
| BLOCKED | 任务因外部条件或依赖问题被阻塞 |
| NEEDS_USER | 任务需要用户补充信息或确认 |
| VERIFYING | 任务正在检验中，属于瞬态 |
| COMPLETED | 任务目标已达成 |
| FAILED | 当前执行失败，但任务未必放弃 |
| ABANDONED | 任务被放弃 |
| SUPERSEDED | 任务被新任务替代 |

### 5.3 推荐状态转换

```text
CREATED -> IN_PROGRESS
CREATED -> NEEDS_USER
CREATED -> ABANDONED

IN_PROGRESS -> VERIFYING
IN_PROGRESS -> BLOCKED
IN_PROGRESS -> NEEDS_USER
IN_PROGRESS -> FAILED
IN_PROGRESS -> ABANDONED

VERIFYING -> COMPLETED
VERIFYING -> IN_PROGRESS
VERIFYING -> NEEDS_USER
VERIFYING -> FAILED

BLOCKED -> IN_PROGRESS
BLOCKED -> ABANDONED

NEEDS_USER -> IN_PROGRESS
NEEDS_USER -> ABANDONED

FAILED -> IN_PROGRESS
FAILED -> ABANDONED
FAILED -> SUPERSEDED
```

---

## 6. 文件系统协议

### 6.1 目录结构

```text
.mem0ress/
  config.yaml
  tasks/
    {task_id}/
      task.yaml
      session.md
      gotchas.yaml
      judge.md
      subtasks/
        {subtask_id}/
          task.yaml
          session.md
          gotchas.yaml
          judge.md
```

### 6.2 为什么 v0.1 使用 YAML + Markdown

v0.1 建议采用 YAML 和 Markdown 混合模式：

- task.yaml：机器可读任务真源；
- session.md：人类可读轮次快照；
- gotchas.yaml：机器可读偏差记录；
- judge.md：检验结果与解释，适合人类审阅。

这样既保留纯文本可编辑性，也提高 Agent 和 CLI 的解析稳定性。

### 6.3 task.yaml Schema

```yaml
id: oauth_login
parent_id: auth_module
status: IN_PROGRESS
created_at: 2026-05-11T10:00:00+09:00
updated_at: 2026-05-11T10:45:00+09:00

picture: >
  用户无需输入密码，即可通过 Google 或 GitHub 完成登录，并进入自己的账户首页。

requirements:
  - id: R1
    text: 支持 Google OAuth 登录
    verification: 用户可以通过 Google 账号完成登录并进入首页
    status: satisfied
    evidence: tests/auth_google.spec.ts passed

  - id: R2
    text: 支持 GitHub OAuth 登录
    verification: 用户可以通过 GitHub 账号完成登录并进入首页
    status: pending
    evidence: null

constraints:
  - id: C1
    type: hard
    text: 不得修改 public API 签名
    detection: diff_check
    status: clear

  - id: C2
    type: soft
    text: 保持现有登录页 UI 风格
    detection: visual_or_human_review
    status: warning

todos:
  - id: T1
    text: 添加 Google OAuth provider
    status: done
  - id: T2
    text: 添加 GitHub OAuth provider
    status: pending
  - id: T3
    text: 更新登录页按钮
    status: pending

data_plane:
  repos:
    app: a1b2c3d

next_actions:
  - 完成 GitHub OAuth provider
  - 检查登录页 UI 是否偏离现有风格
```

### 6.4 gotchas.yaml Schema

```yaml
gotchas:
  - id: G1
    status: open
    severity: medium
    linked_task: oauth_login
    text: 直接修改 auth middleware 会破坏现有 session 流程，已尝试失败。
    evidence: Turn 3 failed test output
    created_at: 2026-05-11T10:30:00+09:00
    resolved_at: null
```

### 6.5 session.md 格式

```markdown
## Turn 4 — 2026-05-11 10:45 JST

### Summary
完成 Google OAuth provider，GitHub provider 尚未完成。

### State Changes
- T1 marked done
- R1 marked satisfied
- C2 changed from clear to warning

### Data Plane
- app: a1b2c3d

### Evidence
- tests/auth_google.spec.ts passed

### Next Suggested Action
继续完成 GitHub OAuth provider，并检查登录页 UI 风格。
```

---

## 7. Status Plane 输出协议

### 7.1 默认输出原则

Status Plane 默认输出 active context，而不是完整任务库。

默认包含：

- active_task；
- parent_chain；
- direct_subtasks；
- open_requirements；
- violated_or_warning_constraints；
- unresolved_gotchas；
- recent_changes；
- data_plane pointers；
- next_actions。

### 7.2 示例输出

```yaml
status_plane:
  active_task:
    id: oauth_login
    status: IN_PROGRESS
    picture_summary: 用户可通过 Google 或 GitHub 无密码登录
    progress: 1/3 todos done, 1/2 requirements satisfied

  parent_chain:
    - auth_module

  direct_subtasks: []

  open_requirements:
    - R2: 支持 GitHub OAuth 登录

  constraints:
    hard_violations: []
    warnings:
      - C2: 登录页 UI 风格可能偏离现有设计

  unresolved_gotchas:
    - G1: 不要直接修改 auth middleware

  recent_changes:
    - T1 marked done
    - R1 marked satisfied

  data_plane:
    repos:
      app: a1b2c3d

  next_actions:
    - 完成 GitHub OAuth provider
    - 检查 UI 风格约束
```

---

## 8. Judge 检验流程

### 8.1 v0.1 的 Judge 定位

v0.1 中，Judge 不应被设计为复杂的自主 Agent，而应被设计为一个可重复执行的检查流程。

Judge 的职责是生成检验结果，不负责最终决策。

最终是否标记任务完成，由主 Agent 或人类确认。

### 8.2 四层检验

#### Tier 0: Constraints 检查

优先检查 Hard Constraints。

若存在 hard violation，任务不得进入 COMPLETED。

#### Tier 1: Todo 与子任务关闭检查

检查：

- 所有 Todo 是否 done；
- 所有直接子任务是否处于关闭状态。

#### Tier 2: Requirements 满足检查

检查每个 Requirement 是否有 evidence。

Requirement 不应只被标记为 satisfied，而必须有证据来源。

#### Tier 3: Picture 语义对齐检查

可选检查。

适用场景：

- Picture 涉及用户体验；
- Picture 涉及主观质量；
- Requirements 无法完全覆盖 Picture；
- 用户或主 Agent 显式要求。

### 8.3 judge.md 示例

```markdown
# Judge Report — oauth_login

## Result
NOT_READY

## Tier 0: Constraints
- C1 clear
- C2 warning: UI style may diverge from existing login page

## Tier 1: Todos
- T1 done
- T2 pending
- T3 pending

## Tier 2: Requirements
- R1 satisfied, evidence: tests/auth_google.spec.ts passed
- R2 pending, no evidence

## Tier 3: Picture Alignment
Skipped. Task not ready for semantic check because R2 is pending.

## Recommendation
Continue implementation. Do not mark task completed.
```

---

## 9. CLI 设计

### 9.1 MVP 命令

```bash
mem0ress init
mem0ress task create
mem0ress task list
mem0ress task show <task_id>
mem0ress task update <task_id>
mem0ress task done <task_id>
mem0ress task block <task_id>
mem0ress task need-user <task_id>
mem0ress session append <task_id>
mem0ress gotcha add <task_id>
mem0ress plane build <task_id>
mem0ress judge run <task_id>
```

### 9.2 命令职责

| 命令 | 职责 |
|---|---|
| init | 创建 .mem0ress 目录 |
| task create | 创建任务并写入 task.yaml |
| task list | 展示任务树 |
| task show | 展示任务详情 |
| task update | 更新 PRC、Todo 或状态 |
| task done | 请求将任务标记为完成，通常应先触发 judge |
| task block | 标记任务被阻塞 |
| task need-user | 标记任务需要用户输入 |
| session append | 追加轮次快照 |
| gotcha add | 追加偏差记录 |
| plane build | 生成 Status Plane |
| judge run | 执行检验并写入 judge.md |

---

## 10. Agent Hook 集成

### 10.1 执行前 Hook

在 Agent 每轮执行开始前：

```text
1. 确定 active_task
2. 运行 mem0ress plane build
3. 将 Status Plane 注入 Agent 上下文
```

### 10.2 执行后 Hook

在 Agent 每轮执行结束后：

```text
1. 检测 Todo / Requirements / Constraints / Gotchas / Data Plane 变化
2. 追加 session.md
3. 必要时更新 task.yaml
4. 必要时运行 judge
5. 输出下一轮 Status Plane
```

### 10.3 Human-in-the-loop

以下动作建议要求用户或人类确认：

- 创建 Picture；
- 修改 Hard Constraints；
- 将任务标记为 COMPLETED；
- 将任务标记为 ABANDONED；
- 处理高风险 Gotcha；
- 执行不可逆外部操作。

---

## 11. MVP 实现范围

### 11.1 v0.1 必须实现

- 本地 `.mem0ress` 目录初始化；
- task.yaml 创建和更新；
- session.md 追加；
- gotchas.yaml 追加；
- Status Plane 生成；
- 基础 Judge 检查；
- Git commit ID Data Plane 捕获；
- CLI 基础命令。

### 11.2 v0.1 暂不实现

- 向量检索；
- 数据库后端；
- 多用户权限系统；
- 分布式同步；
- Web UI；
- 复杂多 Agent 协调；
- 自动任务调度；
- 完整 Observability 平台。

### 11.3 v0.1 成功标准

mem0ress v0.1 的成功不以功能数量衡量，而以是否降低 Agent 长任务偏航为标准。

建议验证指标：

- Agent 是否能在恢复会话后准确说明当前任务状态；
- Agent 是否减少重复尝试失败路径；
- Agent 是否更少违反用户约束；
- Agent 是否能区分 Todo 完成与 Picture 达成；
- Agent 是否能在任务无法继续时进入 NEEDS_USER 或 BLOCKED，而不是胡乱推进。

---

## 12. 示例场景

### 12.1 场景：Claude Code 修改认证模块

用户目标：

> 为现有应用增加 Google 和 GitHub OAuth 登录，但不能破坏已有邮箱密码登录，也不能修改 public API。

mem0ress 创建任务：

```yaml
picture: >
  用户可以使用 Google、GitHub 或原有邮箱密码方式登录，三种方式都能进入同一个账户系统。

requirements:
  - 支持 Google OAuth 登录
  - 支持 GitHub OAuth 登录
  - 原有邮箱密码登录保持可用
  - 三种登录方式进入同一账户体系

constraints:
  - type: hard
    text: 不得修改 public API 签名
  - type: hard
    text: 不得破坏原有邮箱密码登录
  - type: soft
    text: 登录页 UI 风格保持一致
```

Agent 每轮开始时收到 Status Plane，而不是翻完整历史。它知道当前完成了 Google OAuth，GitHub OAuth 还没完成，且 auth middleware 直接修改方案已经失败。

最终 Judge 检查：

- 所有 Hard Constraints clear；
- 所有 Todo done；
- 所有 Requirements 有测试或人工证据；
- Picture 语义上达成。

任务才可标记为 COMPLETED。

---

## 13. Roadmap

### v0.1 — Local Task-State Harness

- 文件系统协议；
- CLI；
- Status Plane；
- 基础 Judge；
- Git Data Plane。

### v0.2 — Agent Adapter

- Claude Code Hook；
- Cursor / Codex CLI 适配；
- MCP Server 版本；
- 更稳定的自动状态变更检测。

### v0.3 — Evaluation Suite

- 长任务 benchmark；
- 有无 mem0ress 对照实验；
- 偏航率、重复失败率、约束违反率指标。

### v0.4 — Multi-Agent / Team Mode

- 多 Agent 任务分配；
- 任务锁；
- 冲突提示；
- 人类审批流。

---

## 14. 设计边界与风险

### 14.1 主要边界

mem0ress 只负责任务状态，不负责替 Agent 做专业判断。

它可以提醒 Agent：

> 当前 Requirement 没有证据。

但不能保证：

> 这个 Requirement 在真实业务上一定正确。

### 14.2 主要风险

1. **状态维护负担**  
   如果 Hook 设计不好，Agent 需要手动维护状态，使用成本会过高。

2. **概念过重**  
   如果对开发者一次性暴露太多术语，采用门槛会变高。

3. **Judge 误判**  
   LLM-based Judge 可能产生错误判断，因此 v0.1 应优先依赖结构化检查和 evidence。

4. **状态平面膨胀**  
   如果默认注入全量任务树，mem0ress 可能制造新的上下文污染。

5. **与项目管理工具混淆**  
   mem0ress 必须强调自己服务的是 Agent 执行态，而不是人类项目管理。

---

## 15. 最终定义

mem0ress 是一个面向长路径 AI Agent 的任务状态牵引框架。

它通过 Picture、Requirements、Constraints、Todos、Session、Gotchas、Status Plane 和 Data Plane，把 Agent 的执行过程绑定到一个可读、可检验、可恢复的当前状态中。

它不追求记住一切，而是确保 Agent 在每一轮执行前都能回答：

> 我正在做什么？  
> 成功图景是什么？  
> 哪些需求已经满足？  
> 哪些约束不能违反？  
> 哪些路径已经证明有风险？  
> 当前代码或文件版本是什么？  
> 下一步最应该做什么？

一句话概括：

> mem0ress does not make agents remember more. It helps agents stay oriented.

