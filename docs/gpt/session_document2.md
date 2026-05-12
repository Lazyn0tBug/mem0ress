我看完这四个核心协议文件了。整体判断：方向是对的，已经具备 MVP 协议雏形；但现在最大的问题是“模板像文档，协议还不够像协议”。

也就是说，它们已经能表达你的思想，但如果要给 CLI、Agent hook、Judge、Plane Assembler 使用，还需要再做一次字段结构化、状态统一、边界收紧。

一、总体评价
你现在的四个文件分工是合理的：

task.md：定义任务目标、需求、约束、Todo、子任务依赖；

session.md：记录每轮执行快照；

gotchas.md：记录偏差、冲突、经验；

judge.md：定义 Tier 0-3 的检验逻辑。

这个四件套已经覆盖了 mem0ress MVP 的核心闭环：

任务定义 → 执行记录 → 偏差沉淀 → 检验判断。

这点是成立的。

但从工程角度看，现在还有三个明显问题：

Markdown 可读性强，但机器可解析性不够硬；

四个文件之间的状态字段没有完全统一；

缺少 Task-local / Agent-Task Binding / Completion Summary 这几个新讨论后的核心协议。

二、我对 task.md 的意见
task.md 是四个文件里最关键的一个。你现在已经把 PRC 三要素、Todos、Subtasks 都放进去了，这个结构是正确的。文件 frontmatter 里也定义了字段 schema，包括 picture、requirements、constraints 和 todos，这说明它已经不只是文章模板，而是在朝协议文件发展。

但我建议做几个调整。

1. task.md 应该继续保留，但 frontmatter 要更结构化
现在 task.md 的正文里是 Markdown checklist：

- [ ] Req 1
- [ ] T-1
这对人好读，但对 CLI 不够友好。

我建议你保留正文 Markdown，同时把真正的机器协议放在 frontmatter 里。

例如：

id: oauth_google
title: 实现 Google OAuth 登录
type: task
status: CREATED
version: "0.1"

agent_binding:
  model: one_agent_one_task
  active_scope: task_local

cognitive_triad:
  picture: >
    用户可以通过 Google OAuth 登录，无需输入本地密码。
  requirements:
    - id: R-1
      text: 支持 Google OAuth 登录入口
      status: pending
      evidence: null
    - id: R-2
      text: OAuth callback 可以正确处理授权结果
      status: pending
      evidence: null
  constraints:
    - id: C-1
      text: 不允许在日志中输出 Access Token
      type: hard
      status: clean
      violation: null

todos:
  - id: T-1
    text: 添加 Google OAuth provider 配置
    status: pending
  - id: T-2
    text: 实现 callback handler
    status: pending

subtasks:
  - id: oauth_callback
    path: children/oauth_callback
    status: CREATED

parent:
  path: ../
  relevance: 当前任务属于认证模块的一部分
正文部分可以继续作为人类阅读版，但 CLI 应该优先解析 frontmatter。

2. Requirements 不建议只用 list[string]
你现在的 requirements 是 list[string]，这个太轻了。Requirement 后续要被 Judge 引用、验收、标记证据，所以应该是 list[object]。

建议改成：

requirements:
  type: list[object]
  children:
    id:
      type: string
    text:
      type: string
    status:
      type: enum
      values: [pending, partial, passed, failed]
    evidence:
      type: string|null
否则 judge.md 和 session.md 很难稳定引用某个 Requirement。

3. Constraints 也不要只用 list[string]
你现在对 Constraints 的定义是“绝对不可逾越的物理红线，一旦违反系统必须阻断”。这个定义够硬，我赞成。

但工程上要区分：

hard constraint：违反即失败；

soft constraint：违反时警告或需要人工确认。

建议：

constraints:
  - id: C-1
    text: 不允许在日志中输出 Access Token
    type: hard
    status: clean
    detection: regex|static_scan|manual|test
    violation: null
如果全部都定义成“物理红线”，那 soft constraint 就没有地方放。实际工程里会有很多“语气、体验、风格、可维护性”一类的软约束，它们不一定能自动阻断，但必须能被记录。

4. Subtasks 需要从 checklist 改成摘要协议
现在 Subtasks 是：

- [ ] `{subtask_1_id}/`
建议改成结构化：

subtasks:
  - id: oauth_callback
    path: children/oauth_callback
    status: IN_PROGRESS
    summary_ref: children/oauth_callback/completion_summary.md
原因是父任务不应该读取子任务完整 session，只需要读取子任务的状态和完成摘要。

三、我对 session.md 的意见
session.md 的方向是对的：它记录每个 Turn 的状态快照，追加不覆盖，并且明确不重复记录 Picture / Requirements / Constraints，这点非常好。

但这里有几个需要改的地方。

1. Session 状态枚举太少
你现在的状态只有：

CREATED, IN_PROGRESS, COMPLETED, ABANDONED
并且注明 VERIFYING 是瞬态，不记录于 Session。

这个设计可以成立，但我建议 MVP 至少补两个状态：

BLOCKED
NEEDS_USER
原因很现实：长任务中最常见的情况不是完成或废弃，而是：

缺资料；

等用户确认；

外部 API 不通；

测试环境不可用；

子任务未完成；

需求与约束冲突。

如果没有 BLOCKED 和 NEEDS_USER，Agent 很容易把不能推进的任务错误标成 IN_PROGRESS，从而继续乱做。

建议状态改成：

values:
  - CREATED
  - IN_PROGRESS
  - BLOCKED
  - NEEDS_USER
  - COMPLETED
  - ABANDONED
VERIFYING 继续作为瞬态，不进入稳定 session 状态，这个可以保留。

2. Turn 编号不建议绑定 Todo 序号
你现在写：

Turn 编号格式为 {parent_turn}.{child_turn}，N 为 todo 的序列号，如 1.1、1.2、2.1，体现嵌套关系。

我建议改。

因为 Turn 是执行轮次，不应该和 Todo 序号强绑定。一个 Todo 可能执行多轮，一个 Turn 也可能影响多个 Todo。

建议：

turn_id: turn_0001
sequence: 1
related_todos:
  - T-1
  - T-2
如果你需要层级关系，可以用：

parent_turn: null
subturn: null
而不是把它编码进 1.2 里。

否则后面会遇到问题：

Todo 顺序变化怎么办？

一个 Turn 同时推进 T-1 和 T-3 怎么办？

子任务的 Turn 是否继承父任务编号？

Task-local 模型下，子任务本来有自己的 session，为什么要体现父层嵌套？

在“一 Agent 一 Task”的模型下，Session 应该是当前 Task 的局部执行流，不需要强行体现全局嵌套。

3. Session entry 建议结构化为 YAML block
现在 session.md 既有 Markdown 段落，又有伪 YAML。人能看懂，但机器解析会痛苦。

建议每个 Turn 使用固定 fenced block：

## Turn turn_0001

```yaml
turn_id: turn_0001
timestamp: 2026-05-11T10:00:00+09:00
worker_id: default
status_before: CREATED
status_after: IN_PROGRESS
related_todos:
  - T-1
todo_changes:
  - id: T-1
    from: pending
    to: done
requirement_changes:
  - id: R-1
    from: pending
    to: partial
constraint_events: []
data_plane:
  commit_id: abc123
  active_refs:
    - src/auth/google_router.ts
summary: 完成 Google OAuth 路由初版。
next_suggested_actions:
  - 实现 callback handler
```
这样 Markdown 仍然可读，CLI 也可以稳定解析。

四、我对 gotchas.md 的意见
gotchas.md 的价值很明确：记录任务执行中的认知偏差、冲突事实和修正路径。你现在的字段包括 context、deviation、resolution，这个设计是合理的。

但我建议增加几个字段。

1. 需要 severity 和 status
Gotcha 不应该只是经验记录，它还应该影响状态平面。

建议增加：

id: G-001
severity: low|medium|high|critical
status: open|resolved|accepted|superseded
related_todos:
  - T-2
related_requirements:
  - R-1
related_constraints:
  - C-1
这样 plane build 才能输出：

unresolved_gotchas:
  - G-001
否则 Gotcha 只是日志，无法参与认知构建。

2. Resolution 不一定总是存在
很多 Gotcha 发现时还没解决。现在模板里直接要求写 resolution，这会诱导 Agent 编造解决方案。

建议拆成：

status: open
resolution: null
decision_required: true
或者：

resolution:
  type: pending|fixed|accepted_risk|requires_user|new_subtask
  text: null
3. Gotcha 应该能触发新子任务
你现在的示例已经提到“追加相应子任务”。
我建议把它协议化：

follow_up:
  create_subtask: true
  suggested_subtask_title: 修复 OAuth callback URL 配置
这会让 gotcha 和任务拆分机制连接起来。

五、我对 judge.md 的意见
judge.md 是你这套协议里最有潜力、但也最需要收紧的文件。

你现在把 Tier 0/1/2/3 都描述清楚了：约束检查、机械状态检查、需求验收、语义对齐检查。尤其 Tier 0 用静态代码扫描、正则匹配、规则检查来验证 Constraints，这很工程化。

但问题是：现在 judge.md 更像“验证逻辑模板”，还不像“验证结果记录”。

我建议分成两种：

judge.md = 验证计划 + 最近结果
judge_runs.md = 每次验证结果追加记录
如果 MVP 不想多一个文件，那至少在 judge.md 里明确区分：

# Judge Plan
# Judge Runs
1. Tier 3 不应写“完美达成 Picture”
你现在 Tier 3 prompt 里写：

是否在语义和最终体验上完美达成图景描述。

这个词太重了，容易导致 Judge 过度失败，也不符合工程验收。

建议改成：

是否足以达成 Picture 所描述的用户可感知成功状态。
或者：

是否存在会阻止 Picture 被利益相关者认可的语义偏差。
因为实际任务不是追求“完美”，而是追求“可接受地达成”。

2. Judge 不应该只定义验证手段，还要记录证据
Tier 2 里现在是：

Req 1 Test Command: npm run test:auth_response_time
建议改成：

tier_2:
  - requirement_id: R-1
    command: npm run test:auth_response_time
    result: passed|failed|skipped
    evidence: tests/logs/auth_response_time.log
    notes: null
Judge 的核心不是“我打算怎么测”，而是“我测了什么，结果是什么，有什么证据”。

3. Judge 输出需要有最终机器可读结论
建议：

final_result: PASS|FAIL|BLOCKED|NEEDS_USER
can_close_task: true|false
recommended_status: COMPLETED|IN_PROGRESS|BLOCKED|NEEDS_USER
这样主 Agent 才能据此决策。

4. Tier 0 的 hard constraint 失败必须阻断
建议明确：

blocking: true
例如：

tier_0:
  result: failed
  blocking: true
  violations:
    - constraint_id: C-1
      evidence: src/auth/callback.ts:52
      message: Access Token printed in log
这比文字说明更适合实现。

六、你现在缺少的两个核心文件/协议
1. data_plane.md / data_plane.yml
四个文件都引用了 data_plane.md，但是你这次没有给出。task.md、session.md、judge.md 都把它列为 requires，说明它在协议里是核心依赖。

我建议 MVP 增加一个非常轻的 data_plane.yml：

version: "0.1"
repos:
  app:
    path: "."
    commit_id: "abc123"
    dirty: false
    active_refs:
      - src/auth/google_router.ts
external_refs:
  - type: api
    name: Google OAuth Console
    note: callback URL must match production domain
updated_at: "2026-05-11T10:00:00+09:00"
但注意：
data_plane 可以作为 session entry 的字段，不一定每个 Task 都有独立文件。

我的建议是：

v0.1：data_plane 放在 session entry 里；

v0.2：再独立成 data_plane.yml。

否则第一版文件太多。

2. completion_summary.md / yml
这是你最新架构中必须补的。

因为父任务不能读取子任务完整 session，只能读取子任务摘要。没有 completion summary，父子任务边界就不完整。

建议新增：

---
type: completion_summary
task_id: oauth_google
status: COMPLETED
requirements_result:
  passed: 3
  total: 3
constraints_result:
  violated: false
blockers: []
output_refs:
  commits: ["abc123"]
  files: ["src/auth/google.ts"]
residual_risks:
  - "生产环境 callback URL 仍需确认"
---

# Completion Summary

## Picture Result

用户可以通过 Google OAuth 登录，无需输入本地密码。

## Evidence

- 集成测试通过
- callback handler 已验证
这个文件对 Task-local 模型非常关键。

七、我建议的最终四件套/五件套
如果你坚持四个文件，我建议是：

task.md
session.md
gotchas.md
judge.md
但我更建议 MVP 用六个文件：

task.md                 任务定义，PRC + Todos + Subtasks
session.md              执行轮次快照
gotchas.md              偏差与经验
judge.md                验证计划与验证结果
completion_summary.md   任务关闭后的边界输出
current.yml             当前 Worker 绑定哪个 Task
data_plane 可以先作为 session.md 的字段，不独立成文件。

也就是说：

data_plane 是每轮快照的一部分；completion_summary 是任务对外暴露的边界。

这比反过来更适合 v0.1。

八、最重要的协议修正：Markdown 不是问题，但必须有机器区
我不建议你完全放弃 Markdown。Markdown 对 Agent 和人类都友好。

但每个文件必须有一个机器可读区。

建议统一格式：

---
type: task
version: "0.1"
...
---

# Human-readable section
或者每个记录用：

```yaml
...
```
核心原则：

Markdown 负责可读，YAML 负责协议。

不要让 CLI 从自然语言段落里猜字段。

九、我建议你现在直接做的修改清单
按优先级：

必改 1：task.md 里的 requirements / constraints 从 string 改 object
否则后面引用不稳。

必改 2：session.md 增加 BLOCKED / NEEDS_USER
否则长任务状态不够真实。

必改 3：gotchas.md 增加 id / status / severity
否则 Gotcha 无法进入状态平面。

必改 4：judge.md 增加 final_result / can_close_task / evidence
否则 Judge 不能驱动状态决策。

必改 5：新增 completion_summary.md
否则父子任务边界不完整。

必改 6：明确 data_plane 先内嵌 session，不作为强依赖文件
否则 MVP 文件依赖过多。

十、我对你这版协议的最终判断
这版文件已经能证明你的核心协议思路：

任务定义、执行快照、偏差记录、任务检验分离。

这个分离是对的。

但它现在还偏“模板说明书”，不是“可执行协议”。

下一步要从：

给 Agent 看得懂

升级为：

Agent 看得懂，CLI 也能稳定解析，Judge 也能稳定引用，父任务也能稳定聚合。

最核心的一句话：

保留 Markdown 外观，但把协议真源放进 YAML 字段。

这会让 mem0ress 既轻、又可读、又能进入真正的工程实现。
