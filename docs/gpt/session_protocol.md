我建议你把核心协议定为 mem0ress Protocol v0.1-alpha。

这版协议的原则是：

Markdown 负责可读，YAML 负责协议。
Task 是认知边界，Session 是执行快照，Gotcha 是偏差记录，Judge 是检验记录，Completion Summary 是跨任务边界输出。

你现有 task.md 已经有 PRC、Todos 和 Subtasks 的基本形态；session.md 已经明确“追加不覆盖”和“不重复记录 PRC”；gotchas.md 已经覆盖偏差背景、冲突事实和修正；judge.md 已经有 Tier 0-3 的验证框架。下面这版是在你现有基础上，把它收紧成更适合 CLI 和 Agent Hook 的协议。

mem0ress Protocol v0.1-alpha
0. 文件组成
建议 MVP 核心协议采用 5 + 1 文件：

task.md
session.md
gotchas.md
judge.md
completion_summary.md
current.yml
其中：

task.md                  当前 Task 的唯一任务声明
session.md               当前 Task 的执行轮次快照
gotchas.md               当前 Task 的偏差、风险、经验记录
judge.md                 当前 Task 的检验计划与检验结果
completion_summary.md    当前 Task 关闭后对父任务暴露的边界摘要
current.yml              当前 Runtime Worker 绑定的 active task
data_plane 第一版不单独做文件，先作为 session.md 和 judge.md 里的字段。这样更轻。

1. current.yml
current.yml 记录当前 Runtime Worker 绑定哪个 Task。

protocol: mem0ress
version: "0.1-alpha"

worker:
  id: default
  mode: runtime_worker

binding:
  active_task: auth_module/children/oauth_google
  scope: task_local
  bound_at: "2026-05-11T10:00:00+09:00"

rules:
  one_agent_one_task: true
  load_full_task_tree_by_default: false
  parent_child_communication: summary_only
说明
active_task 是当前 Agent / Worker 的认知边界。
scope: task_local 表示后续 plane build、session append、judge run 默认只围绕当前 Task 运行。

2. task.md
task.md 是任务声明文件，也是 PRC 的唯一真源。

你原来用 Markdown checklist 表达 Requirements 和 Todos，这对人类好读，但不够适合机器引用。v0.1-alpha 建议把机器协议放进 YAML frontmatter，正文保留人类可读版。

---
protocol: mem0ress
version: "0.1-alpha"
type: task

id: oauth_google
path: auth_module/children/oauth_google
title: 实现 Google OAuth 登录
status: IN_PROGRESS

agent_binding:
  model: one_agent_one_task
  scope: task_local
  logical_agent_id: agent.oauth_google
  runtime_worker_id: default

parent:
  id: auth_module
  path: auth_module
  relevance: 当前任务属于认证模块，负责 Google OAuth 登录路径。

cognitive_triad:
  picture: >
    用户可以通过 Google OAuth 完成登录，
    整个过程中不需要输入本地密码，
    登录成功后进入系统首页。

  requirements:
    - id: R-1
      text: 用户可以点击 Google 登录按钮发起 OAuth 流程。
      status: pending
      evidence: null

    - id: R-2
      text: Google OAuth callback 可以正确接收并处理授权结果。
      status: pending
      evidence: null

    - id: R-3
      text: 登录成功后用户 session 被正确创建。
      status: pending
      evidence: null

  constraints:
    - id: C-1
      text: 不得要求用户输入本地密码。
      type: hard
      status: clean
      detection: semantic
      violation: null

    - id: C-2
      text: 不得在日志中输出 OAuth token。
      type: hard
      status: clean
      detection: static_scan
      violation: null

todos:
  - id: T-1
    text: 添加 Google OAuth provider 配置。
    status: done

  - id: T-2
    text: 实现 callback handler。
    status: in_progress

  - id: T-3
    text: 运行 Google 登录集成测试。
    status: pending

subtasks:
  - id: oauth_callback
    path: auth_module/children/oauth_google/children/oauth_callback
    status: CREATED
    summary_ref: auth_module/children/oauth_google/children/oauth_callback/completion_summary.md

metadata:
  created_at: "2026-05-11T09:30:00+09:00"
  updated_at: "2026-05-11T10:00:00+09:00"
---

# Task: 实现 Google OAuth 登录

## Picture

用户可以通过 Google OAuth 完成登录，整个过程中不需要输入本地密码，登录成功后进入系统首页。

## Requirements

- [ ] R-1: 用户可以点击 Google 登录按钮发起 OAuth 流程。
- [ ] R-2: Google OAuth callback 可以正确接收并处理授权结果。
- [ ] R-3: 登录成功后用户 session 被正确创建。

## Constraints

- ⛔ C-1: 不得要求用户输入本地密码。
- ⛔ C-2: 不得在日志中输出 OAuth token。

## Todos

- [x] T-1: 添加 Google OAuth provider 配置。
- [ ] T-2: 实现 callback handler。
- [ ] T-3: 运行 Google 登录集成测试。

## Subtasks

- [ ] oauth_callback
关键设计
requirements 必须是 object，不建议继续用 list[string]。
constraints 也必须是 object，因为 Judge 需要稳定引用 C-1 / C-2。
todos.status 不建议只用 boolean，建议使用：

pending | in_progress | done | blocked
3. session.md
session.md 是追加式执行快照，不是对话记录。你原文件已经明确每轮结束追加、不覆盖，并且不重复记录 Picture / Requirements / Constraints，这个原则要保留。

建议每个 Turn 用 fenced YAML block，方便 CLI 解析。

---
protocol: mem0ress
version: "0.1-alpha"
type: session
task_id: oauth_google
task_path: auth_module/children/oauth_google
append_only: true
---

# Session History

## Turn turn_0001

```yaml
turn_id: turn_0001
sequence: 1
timestamp: "2026-05-11T10:05:00+09:00"
worker_id: default

status:
  before: CREATED
  after: IN_PROGRESS

related_todos:
  - T-1
  - T-2

todo_changes:
  - id: T-1
    from: pending
    to: done
  - id: T-2
    from: pending
    to: in_progress

requirement_changes:
  - id: R-1
    from: pending
    to: partial
    evidence: "Google login button added, callback not verified yet."

constraint_events: []

data_plane:
  repos:
    app:
      commit_id: "abc123"
      dirty: false
  active_refs:
    - src/auth/google_provider.ts
    - src/auth/google_router.ts
  note: "Added Google provider config and initial route."

summary: >
  完成 Google OAuth provider 初版配置，并开始实现 callback handler。

next_suggested_actions:
  - 完成 callback handler
  - 检查 token 是否会被日志输出
  - 运行 Google 登录集成测试
Turn turn_0002
turn_id: turn_0002
sequence: 2
timestamp: "2026-05-11T10:30:00+09:00"
worker_id: default

status:
  before: IN_PROGRESS
  after: BLOCKED

related_todos:
  - T-2

todo_changes: []

requirement_changes: []

constraint_events: []

data_plane:
  repos:
    app:
      commit_id: "abc456"
      dirty: false
  active_refs:
    - src/auth/callback.ts
  note: "Callback implementation blocked by redirect URI mismatch."

summary: >
  callback handler 初版完成，但本地 redirect URI 与 Google Console 配置不一致，导致流程无法验证。

next_suggested_actions:
  - 记录 gotcha
  - 修正 redirect URI 配置

## 状态枚举

建议稳定状态使用：

```text
CREATED
IN_PROGRESS
BLOCKED
NEEDS_USER
COMPLETED
ABANDONED
VERIFYING 作为瞬态，不进入 session 稳定状态。你原来已经把 VERIFYING 排除在 Session 稳定状态之外，这个设计可以保留。

Turn 编号建议
不要再用 1.1 / 1.2 绑定 Todo 序号。

建议：

turn_0001
turn_0002
turn_0003
因为一个 Turn 可能影响多个 Todo，一个 Todo 也可能执行多轮。

4. gotchas.md
gotchas.md 记录偏差、冲突、经验。你原文件的 context / deviation / resolution 三段结构是好的，但需要增加 id / status / severity / related_refs，这样 Gotcha 才能进入状态平面。

---
protocol: mem0ress
version: "0.1-alpha"
type: gotchas
task_id: oauth_google
task_path: auth_module/children/oauth_google
append_only: true
---

# Gotchas

## G-001: Google callback URL 与本地环境不一致

```yaml
id: G-001
title: Google callback URL 与本地环境不一致
timestamp: "2026-05-11T10:32:00+09:00"
turn_reference: turn_0002

status: open
severity: medium

related_todos:
  - T-2

related_requirements:
  - R-2

related_constraints: []

context: >
  在验证 Google OAuth callback handler 时，本地 redirect URI 与 Google Console 中配置的 callback URL 不一致。

deviation: >
  代码实现可以接收 callback，但 OAuth provider 拒绝回调请求，导致 R-2 无法验证。

resolution:
  type: pending
  text: null

decision_required: false

follow_up:
  create_subtask: false
  suggested_subtask_title: null
Context
在验证 Google OAuth callback handler 时，本地 redirect URI 与 Google Console 中配置的 callback URL 不一致。

Deviation
代码实现可以接收 callback，但 OAuth provider 拒绝回调请求，导致 R-2 无法验证。

Resolution
待修正。


## Gotcha 状态

```text
open
resolved
accepted
superseded
Resolution 类型
pending
fixed
accepted_risk
requires_user
new_subtask
5. judge.md
judge.md 不应该只是验证模板，还要记录验证结果。你现有文件已经有 Tier 0-3 的框架，其中 Tier 0 检查约束、Tier 1 检查 Todos 和子任务、Tier 2 检查 Requirements、Tier 3 检查 Picture 语义对齐，这个框架可以保留。

建议结构分为：

Judge Plan
Judge Runs
---
protocol: mem0ress
version: "0.1-alpha"
type: judge
task_id: oauth_google
task_path: auth_module/children/oauth_google
---

# Judge

## Judge Plan

```yaml
tiers:
  tier_0:
    name: constraints_check
    required: true
    blocking_on_failure: true

  tier_1:
    name: mechanical_check
    required: true
    blocking_on_failure: true

  tier_2:
    name: requirements_check
    required: true
    blocking_on_failure: true

  tier_3:
    name: semantic_alignment_check
    required: false
    trigger:
      - picture_involves_user_experience
      - stakeholder_requests_semantic_review
      - requirements_passed_but_picture_uncertain
Judge Run judge_0001
run_id: judge_0001
timestamp: "2026-05-11T10:45:00+09:00"
turn_reference: turn_0002
worker_id: default

data_plane:
  repos:
    app:
      commit_id: "abc456"
      dirty: false
  active_refs:
    - src/auth/callback.ts
    - src/auth/google_provider.ts

tier_0:
  name: constraints_check
  result: passed
  blocking: false
  checks:
    - constraint_id: C-1
      result: passed
      method: semantic_review
      evidence: "No local password prompt found in login flow."
    - constraint_id: C-2
      result: passed
      method: static_scan
      evidence: "No token logging found in active refs."

tier_1:
  name: mechanical_check
  result: failed
  blocking: true
  checks:
    - item: todos
      result: failed
      evidence: "T-2 is in_progress, T-3 is pending."
    - item: direct_subtasks
      result: passed
      evidence: "No open direct subtasks."

tier_2:
  name: requirements_check
  result: failed
  blocking: true
  checks:
    - requirement_id: R-1
      result: partial
      method: manual_review
      evidence: "Login button exists, full OAuth flow not verified."
    - requirement_id: R-2
      result: failed
      method: integration_test
      command: "npm run test:google-callback"
      evidence: "Redirect URI mismatch."
    - requirement_id: R-3
      result: pending
      method: integration_test
      command: "npm run test:session-create"
      evidence: null

tier_3:
  name: semantic_alignment_check
  result: skipped
  reason: "Tier 1 and Tier 2 have not passed."

final:
  result: FAIL
  can_close_task: false
  recommended_status: BLOCKED
  blocking_reasons:
    - "R-2 failed because redirect URI mismatch prevents callback verification."
  next_suggested_actions:
    - "Fix Google Console redirect URI."
    - "Re-run callback integration test."

## Judge final.result 枚举

```text
PASS
FAIL
BLOCKED
NEEDS_USER
recommended_status 枚举
IN_PROGRESS
BLOCKED
NEEDS_USER
COMPLETED
ABANDONED
Tier 3 Prompt 修改建议
你现有 prompt 里写“完美达成 Picture”，这个标准太重。建议改成：

请判断当前产出是否足以达成 Picture 所描述的用户可感知成功状态。
如果存在会阻止利益相关者认可该 Picture 的偏差，请返回 FAIL 并说明原因。
如果没有实质偏差，请返回 PASS。
6. completion_summary.md
这是我建议你新增的关键文件。

因为你现在已经明确：每个 Agent 只负责一个 Task，父任务不应该读取子任务完整 Session。那子任务关闭后必须有一个边界输出文件。

---
protocol: mem0ress
version: "0.1-alpha"
type: completion_summary

task_id: oauth_google
task_path: auth_module/children/oauth_google
final_status: COMPLETED
created_at: "2026-05-11T11:20:00+09:00"

picture_result: >
  用户可以通过 Google OAuth 完成登录，
  整个过程中不需要输入本地密码，
  登录成功后进入系统首页。

requirements_result:
  passed: 3
  total: 3
  items:
    - id: R-1
      status: passed
      evidence: "Google login entry verified."
    - id: R-2
      status: passed
      evidence: "Callback integration test passed."
    - id: R-3
      status: passed
      evidence: "Session creation test passed."

constraints_result:
  violated: false
  violations: []

todos_result:
  completed: 3
  total: 3

blockers: []

output_refs:
  commits:
    - "def789"
  files:
    - src/auth/google_provider.ts
    - src/auth/callback.ts
    - tests/e2e/google_oauth.test.ts

residual_risks:
  - "生产环境 Google Console callback URL 仍需上线前确认。"

gotchas_summary:
  - id: G-001
    status: resolved
    summary: "本地 redirect URI 与 Google Console 不一致，已修正。"
---

# Completion Summary

## Picture Result

用户可以通过 Google OAuth 完成登录，整个过程中不需要输入本地密码，登录成功后进入系统首页。

## Evidence

- Google 登录入口验证通过。
- Callback 集成测试通过。
- Session 创建测试通过。

## Residual Risks

- 生产环境 Google Console callback URL 仍需上线前确认。
作用
父任务读取子任务时，只读取这个文件。

父任务不读取：

子任务完整 session.md
子任务完整 gotchas.md
子任务完整 judge.md
除非显式调试。

7. status_plane 输出协议
status_plane 可以不是一个持久文件，而是 plane build 的输出。

protocol: mem0ress
version: "0.1-alpha"
type: status_plane
scope: task_local
generated_at: "2026-05-11T11:30:00+09:00"

active_task:
  id: oauth_google
  path: auth_module/children/oauth_google
  title: 实现 Google OAuth 登录
  status: BLOCKED

picture:
  summary: >
    用户可以通过 Google OAuth 完成登录，
    不需要输入本地密码，
    登录成功后进入系统首页。

progress:
  todos:
    completed: 1
    total: 3
    open:
      - id: T-2
        status: in_progress
        text: 实现 callback handler。
      - id: T-3
        status: pending
        text: 运行 Google 登录集成测试。

  requirements:
    passed: 0
    total: 3
    pending:
      - R-1
      - R-2
      - R-3

  constraints:
    violated: false
    open_violations: []

local_context:
  latest_session:
    turn_id: turn_0002
    summary: callback handler 初版完成，但 redirect URI mismatch 阻塞验证。
  unresolved_gotchas:
    - id: G-001
      severity: medium
      title: Google callback URL 与本地环境不一致

judge:
  latest_run: judge_0001
  final_result: BLOCKED
  can_close_task: false
  recommended_status: BLOCKED

parent:
  id: auth_module
  path: auth_module
  relevance: 当前任务属于认证模块，负责 Google OAuth 登录路径。

children:
  open: []
  completed: []

data_plane:
  repos:
    app:
      commit_id: "abc456"
      dirty: false
  active_refs:
    - src/auth/callback.ts
    - src/auth/google_provider.ts

next_suggested_actions:
  - 修正 Google Console redirect URI
  - 重新运行 callback 集成测试
  - 更新 G-001 resolution
8. 状态协议
Task status
CREATED
IN_PROGRESS
BLOCKED
NEEDS_USER
COMPLETED
ABANDONED
Transient state
VERIFYING
VERIFYING 只存在于 judge run 执行期间，不写入 task.md 的稳定状态。

9. ID 规则
建议统一：

Requirement: R-1, R-2, R-3
Constraint:  C-1, C-2, C-3
Todo:        T-1, T-2, T-3
Gotcha:      G-001, G-002
Turn:        turn_0001, turn_0002
Judge Run:   judge_0001, judge_0002
不要让 Turn ID 绑定 Todo 序号。

10. 文件写入规则
task.md
可更新。
只保存当前 Task 的任务声明与最新状态。
PRC 的唯一真源。
session.md
只追加。
每轮结束追加一个 Turn。
不重复记录 PRC。
gotchas.md
只追加。
Gotcha 允许后续追加 resolution update。
不删除历史 Gotcha。
judge.md
Judge Plan 可更新。
Judge Runs 只追加。
completion_summary.md
任务关闭时生成。
任务重新打开后可 supersede，但不应静默覆盖。
11. 目录结构
.mem0ress/
├── current.yml
└── tasks/
    └── auth_module/
        ├── task.md
        ├── session.md
        ├── gotchas.md
        ├── judge.md
        ├── completion_summary.md
        └── children/
            └── oauth_google/
                ├── task.md
                ├── session.md
                ├── gotchas.md
                ├── judge.md
                ├── completion_summary.md
                └── children/
12. 最小 CLI 映射
mem0ress init

mem0ress task create auth_module
mem0ress task create oauth_google --parent auth_module

mem0ress bind auth_module/children/oauth_google
mem0ress active

mem0ress plane build

mem0ress session append --from turn.yml
mem0ress gotcha add --from gotcha.yml
mem0ress judge run

mem0ress task close --status COMPLETED
mem0ress child summary auth_module/children/oauth_google
13. 我认为这版协议的优点
这版比你现在的模板更适合落地，原因很简单：

所有关键对象都有稳定 ID，Judge、Session、Gotcha 可以互相引用。

Markdown 仍然友好，Agent 和人都能读。

YAML 是机器真源，CLI 不需要从自然语言里猜。

支持 Task-local 模型，不会把任务树误当上下文窗口。

completion_summary 补齐了父子任务边界。

状态更真实，加入了 BLOCKED 和 NEEDS_USER。

Judge 从“验证模板”升级成“验证计划 + 验证结果”。

14. 最终建议
我建议你下一版就按这个版本推进，命名为：

mem0ress Protocol v0.1-alpha
它不是最终协议，但已经足够支持 MVP。

最重要的取舍是：

不要为了纯 Markdown 的美感牺牲机器可解析性；也不要为了机器可解析性放弃 Markdown 的可读性。

所以最佳形态就是：

YAML frontmatter + Markdown body + fenced YAML records
这会让 mem0ress 既像一个开发者工具，也像一个 Agent 能自然读写的认知协议。
