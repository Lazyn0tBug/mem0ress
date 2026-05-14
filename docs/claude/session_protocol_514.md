> Q: 我们的MVP已经完成了初步设计，我现在有一个新的问题，在设计中，我们用skill的slash command调用cli的命令， 对于agent操作而言，这是一个好的模式吗？是否仅仅变成了应用套壳，agent判断执行什么命令。

> 对于很多工作来说，并不具备编码完成一切的条件，比如判断一个条件是否满足。

> 那么问题来了，有哪些内容，是应该交给skill做的，哪些是留给cli来做的。
我希望我们完成的产品，是真正符合agent应用模式的，而不只是一个agent替代我访问应用而已，do u get me?

---

MVP 的整体定位已经改变了。
你现在已经从：

CLI-centered tool system
演化成：

Agent-native cognition runtime
这意味着：

CLI

skill

runtime

API

judge

的边界都必须重新收敛。

最大变化是什么？
之前：

Agent
  ↓
skill
  ↓
CLI commands
本质上还是：

command execution model
而现在：

Agent
  ↓
cognitive skills
  ↓
protocol runtime
已经变成：

cognition negotiation model
这是完全不同的。

所以 MVP 的核心目标也变了
之前：

“验证 protocol 是否成立”
现在：

“验证 agent-native cognition loop 是否成立”
这是巨大升级。

新 MVP 的核心问题
现在 MVP 要验证的是：



问题	是否成立
Agent 是否能基于 plane 恢复认知	?
Skill 是否真正承担 cognition operator	?
Runtime 是否保持 deterministic	?
Semantic authority 是否始终属于 agent	?
长任务是否真的更稳定	?
所以 MVP 架构必须更新
我会把 MVP 重新收敛成：

┌────────────────────┐
│ Hermes Agent       │
│ semantic cognition │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ mem0ress skills    │
│ cognitive operator │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ protocol runtime   │
│ deterministic core │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ filesystem state   │
└────────────────────┘
CLI 必须重新定位
这是重点。

旧定位（错误方向）
CLI = 用户操作入口
这会导致：

command-centric

shell automation

workflow thinking

新定位（正确方向）
CLI = deterministic runtime surface
CLI：

不是给“人”用的。
而是：

给 skill/runtime 调用的 deterministic boundary。
这是非常关键的。

所以 CLI 应该做什么？
CLI 只应该暴露：

protocol-level deterministic operations
例如：



CLI	作用
append_snapshot	persistence
render_plane	projection
validate_protocol	structural validation
execute_tests	objective execution
persist_task	storage
transition_state	deterministic state update
CLI 不应该做什么？
例如：

task analyze
task plan
task decide
task assess
task align
task repair
这些：

都是 semantic cognition。
应该属于：

skill + agent。
Skill 必须大幅升级
这是重点。

之前：

create_task()
run_judge()
太 application wrapper 了。

新 Skill 应该是什么？
Skill：

必须直接面向 cognition。
我建议的新 Skill API
Cognitive Recovery
recover_context()
render_current_picture()
summarize_progress()
identify_open_loops()
Cognitive Evaluation
evaluate_alignment()
assess_requirement_coverage()
detect_scope_drift()
evaluate_completion_confidence()
Cognitive Mutation
record_progress()
record_decision()
record_gotcha()
update_understanding()
Deterministic Validation
validate_constraints()
execute_tests()
verify_todos()
注意：

validate ≠ judge semantics
这里只是：

evidence collection。
这时 runtime 才真正“干净”
Runtime：

完全 deterministic。
例如：

Runtime
负责：

- append snapshot
- parse markdown
- execute pytest
- validate schema
- assemble plane
Agent
负责：

- 是否真正完成
- 是否 drift
- 是否重构
- 是否偏离 picture
- 是否该拆任务
MVP 流程也必须更新
这是关键。

旧流程
Agent
  ↓
run command
  ↓
CLI
本质：

tool automation
新流程
应该是：

recover_context
  ↓
reconstruct cognition
  ↓
execute work
  ↓
record progress
  ↓
collect evidence
  ↓
evaluate semantic alignment
  ↓
decide next cognition step
这才是：

cognition loop。
所以 MVP 的“验证点”也变了
以前验证：

protocol

state machine

judge

现在：

验证 cognition continuity。
新 MVP 最关键的验证指标


指标	含义
Context Recovery Stability	是否能恢复认知
Semantic Drift Resistance	是否抗漂移
Plane Sufficiency	plane 是否足够
Cognitive Compression	是否降低 context entropy
Long-Horizon Stability	长任务是否稳定
Skill Cognition Quality	skill 是否真正 cognitive
我甚至认为：
现在可以删掉很多 CLI 命令。

因为：

很多命令本来就是 semantic operation。
例如：

应删掉
mem0ress judge semantic
mem0ress analyze task
mem0ress repair task
保留
mem0ress snapshot append
mem0ress plane render
mem0ress tests run
mem0ress protocol validate
这是一次非常重要的“哲学收敛”
因为现在：

你终于明确：

“runtime 不能拥有 cognition”
这会极大减少未来：

orchestration creep

workflow creep

planner creep

rule-engine creep

最后一个非常重要的建议
我建议：

MVP 第一版甚至不要给用户 CLI。
只给：

Hermes Skill Interface。
因为：

真正的产品是 cognitive protocol
不是 terminal app。

CLI 只是：

runtime transport layer。
