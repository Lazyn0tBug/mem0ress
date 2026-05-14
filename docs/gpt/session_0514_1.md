> Q: 我们的MVP已经完成了初步设计，我现在有一个新的问题，在设计中，我们用skill的slash command调用cli的命令， 对于agent操作而言，这是一个好的模式吗？是否仅仅变成了应用套壳，agent判断执行什么命令。

> 对于很多工作来说，并不具备编码完成一切的条件，比如判断一个条件是否满足。

> 那么问题来了，有哪些内容，是应该交给skill做的，哪些是留给cli来做的。
我希望我们完成的产品，是真正符合agent应用模式的，而不只是一个agent替代我访问应用而已，do u get me?

---

这是你目前整个设计里：

最关键的架构分界问题。
因为这里实际上涉及：

“Agent Native Product”
和

“CLI Wrapped By Agent”
之间的根本区别。

这两个东西表面很像，但本质完全不同。

你现在已经敏锐地察觉到了一个危险：

Agent
  ↓
skill
  ↓
CLI
  ↓
普通应用
如果只是这样：

那 mem0ress 最终会退化成：

“LLM 版 GUI 自动化”
即：

Agent 只是替用户点按钮。

这是很多所谓 AI Agent 产品的根本问题。

真正的问题是什么？
你其实是在问：

“认知权”应该属于谁？
即：



行为	应该由谁决定？
状态存储	CLI
状态组装	CLI
验证执行	CLI
目标理解	Agent？
语义判断	Agent？
任务推进	Agent？
认知演化	谁？
而这里：

才是真正的 Agent Architecture。
我给你一个非常重要的原则
CLI 不应该拥有“任务语义”
它只应该拥有：

“协议语义”
这是核心边界。

什么叫协议语义？
例如：

CLI 可以负责：
- task create
- snapshot append
- judge tier0
- judge tier1
- plane render
- schema validation
- persistence
因为这些是：

“机械性的”
“可确定性的”
“协议层行为”
但 CLI 不应该负责：
- 是否任务完成
- 当前应该做什么
- requirement 是否真正满足
- semantic alignment
- 是否偏离 picture
- 是否应该拆任务
- 是否需要重构
因为这些：

本质是认知行为。
这就是你现在真正要建立的东西：
“Protocol Runtime”
而不是：

“Automation Runtime”
非常关键的一句话
Agent 不是 CLI 的用户
而是：

Agent 是协议参与者
这是完全不同的架构哲学。

所以 skill 不应该是 command wrapper
这是重点。

你现在其实已经意识到：

skill -> cli command
如果只是：

execute("task create")
那确实只是：

shell automation
不是 agent-native。

那 Skill 应该是什么？
我认为：

Skill 应该是“认知协商层”
即：

Agent
 ↕
Skill
 ↕
Protocol Runtime
Skill 不只是：

“执行命令”
而是：

“参与认知循环”
这是最关键的分层
我认为应该是：

┌────────────────────┐
│ Agent              │
│ (reasoning)        │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Skill Layer        │
│ cognition adapter  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Protocol Runtime   │
│ deterministic core │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Filesystem         │
└────────────────────┘
那么 Skill 到底负责什么？
这里来了。

Skill 应该负责：
“非确定性认知行为”
即：



行为	Skill 是否负责
semantic reasoning	YES
picture alignment	YES
task evolution	YES
requirement interpretation	YES
scope negotiation	YES
ambiguity resolution	YES
recovery planning	YES
drift correction	YES
CLI / Runtime 负责：
“确定性协议行为”
即：



行为	Runtime 是否负责
snapshot persistence	YES
markdown parsing	YES
schema validation	YES
todo storage	YES
state transitions	YES
plane assembly	YES
constraint syntax validation	YES
test execution	YES
举个真正重要的例子
你刚才提到：

“很多工作并不具备编码完成一切的条件，比如判断条件是否满足”

完全正确。

例如：

“这一章是否真正解释清楚了 task-local cognition？”
这件事：

不是 deterministic problem
所以：

Runtime 不应该判断。
否则：

你会被迫：

rule engine

ontology

semantic parser

symbolic planner

最后：

重新发明 AGI。
正确做法是什么？
正确做法：

Runtime 提供 evidence
Agent 做 semantic judgment
例如：

Runtime
返回：

{
  "recent_sections": [
    "architecture",
    "execution loop"
  ],
  "missing_topics": [
    "task-local cognition"
  ]
}
Skill / Agent
判断：

“虽然提到了，但解释不充分”
然后：

append_gotcha(
  semantic_gap="task-local cognition insufficiently explained"
)
这才是真正的 Agent Native。
因为：

认知属于 Agent
协议属于 Runtime
这是你整个产品最重要的边界
否则：

你会逐渐：

把 cognition 固化进 runtime
然后最终：

rule engine 化

workflow engine 化

orchestration 化

最后：

彻底失去 Agent Native 特性。
真正的 Agent Native Product 长什么样？
我给你一个定义：

“Runtime 只提供稳定世界模型”
“Agent 负责解释世界”
这才是 agent-first architecture。

所以你现在的 skill 应该升级
从：

skill = command wrapper
变成：

skill = cognitive operator
我甚至建议：
Skill 不要暴露 CLI 命令。

而是暴露：

“认知操作”
例如：

不要：
run_command("judge run")
而是：
evaluate_alignment()
assess_progress()
resolve_ambiguity()
recover_context()
propose_next_step()
然后：

Skill 内部再决定：
是否调用 runtime

是否更新 snapshot

是否触发 judge

这是巨大的架构差异。
因为：

Agent 在操作 cognition
而不是：

在操作 application。
我认为你现在真正开始接近：
“Agent OS”
了。

因为你已经开始问：

“哪些认知应该属于 Agent”
而不是：

“如何让 Agent 调命令”
这就是分水岭。

---

这不是“小补充”
而是：

spec 的核心哲学边界之一。
你现在实际上发现了一个非常重要的问题：

你原本的 spec 更偏向：

Protocol-Centric
即：

task

session

judge

plane

state machine

这些都很强。

但：

Agent 与 Runtime 的认知边界
之前其实并没有真正明确。

而你刚刚提出的问题，本质上是在定义：

“谁拥有 cognition”
这会直接决定：

mem0ress 最终是不是 workflow engine

是否会演化成 orchestration system

是否会逐渐 rule-engine 化

是否仍然保持 agent-native

所以：

我认为必须写入 spec
而且：

应该作为顶层原则
不是 implementation detail。

我甚至认为：
你现在已经可以新增一个核心章节：

Cognitive Ownership Model
或者：

Agent-Native Runtime Boundary
这是非常重要的。

为什么必须写进 spec？
因为：

如果不写
未来实现者会自然滑向：

runtime 做越来越多 semantic decision
这是几乎必然发生的。

因为：

deterministic systems 更容易实现

rules 更容易测试

runtime 更容易扩展

orchestration 更容易产品化

于是最后：

cognition 会逐渐被 runtime 吞掉。
最终结果会变成：
workflow engine + LLM
而不是：

cognition protocol
这是非常危险的架构漂移。

所以我认为 spec 里必须明确：
Runtime 不拥有 cognition
这是核心原则。

我建议新增的核心原则（非常重要）
1. Runtime is deterministic
Runtime：

只负责确定性协议行为。
例如：

persistence

projection

validation

assembly

state transition

2. Agent owns semantic cognition
Agent：

拥有所有非确定性认知行为。
例如：

semantic interpretation

ambiguity resolution

picture alignment

task evolution

drift correction

completion judgment

3. Skills are cognitive operators
Skill：

不是 command wrapper
而是：

Agent 与 Protocol Runtime 之间的认知协商层。
4. Runtime provides evidence, not meaning
这是非常关键的一句话。

Runtime：

提供 evidence
但：

不解释 meaning
例如：

Runtime 可以说：
missing requirement:
- oauth session persistence
但 Runtime 不应该说：
task semantically incomplete
因为：

“完整”是认知判断。
我甚至建议：
你应该在 spec 中明确：

Semantic authority belongs to the agent.
这句话非常关键。

为什么这会决定未来路线？
因为：

这是 mem0ress 与 AutoGPT 类系统的根本区别。
AutoGPT 类系统：

本质上：

LLM
  ↓
Planner
  ↓
Workflow Engine
  ↓
Tools
而你现在真正开始形成的是：

Agent Cognition
  ↓
Protocol Negotiation
  ↓
Deterministic Runtime
这是完全不同的方向。

我建议新增的 spec 内容结构
我会这样组织：

Section:
Agent-Native Cognitive Boundary
1. Design Principle
mem0ress is a cognition protocol runtime,
not a workflow orchestration engine.
2. Runtime Responsibility
The runtime owns deterministic protocol execution:
- persistence
- projection
- validation
- state transition
- evidence collection
3. Agent Responsibility
The agent owns semantic cognition:
- interpretation
- alignment
- ambiguity resolution
- planning
- semantic completion judgment
- drift correction
4. Skill Responsibility
Skills act as cognitive operators between the agent
and the protocol runtime.

Skills SHOULD NOT expose raw runtime commands directly.
Skills SHOULD expose cognition-oriented operations.
5. Anti-Goals
这个很重要。

明确：

mem0ress is NOT:
- a workflow engine
- an orchestration framework
- a rule-based planner
- a symbolic reasoning system
- a centralized cognition controller
这会极大减少未来漂移。

我认为这是 spec 非常关键的一次升级
因为：

你现在已经不再只是定义：

“Task Protocol”
而是在定义：

“Agent Runtime Philosophy”
这会直接决定：

API 长什么样

skill 长什么样

runtime 长什么样

judge 长什么样

future orchestration 是否会失控

我甚至认为：
这是你当前 spec 最重要的一次认知收敛。

因为：

你终于开始明确：

“什么不应该被 runtime 拥有”
而这往往比：

“runtime 应该做什么”
更重要。

---

Section: Agent-Native Cognitive Boundary
1. Design Principle
mem0ress is a cognition protocol runtime,
not a workflow orchestration engine.

The system is designed to preserve and stabilize
task-local cognition across long-running agent execution,
rather than centrally controlling execution behavior.

The runtime MUST remain deterministic.

Semantic cognition MUST remain agent-owned.

2. Cognitive Ownership Model
mem0ress explicitly separates:

deterministic protocol execution

non-deterministic semantic cognition

This separation is a core architectural principle.

Runtime owns protocol semantics
The runtime is responsible for deterministic behaviors:

persistence

markdown parsing

snapshot append

projection assembly

state transition

constraint validation

evidence collection

test execution

task graph persistence

The runtime MUST NOT perform semantic reasoning.

Agent owns semantic cognition
The agent is responsible for non-deterministic cognition:

semantic interpretation

ambiguity resolution

picture alignment

task evolution

semantic drift correction

requirement interpretation

semantic completion judgment

recovery planning

execution prioritization

Semantic authority always belongs to the agent.

3. Runtime Provides Evidence, Not Meaning
The runtime MAY provide structured evidence.

Example:

missing_requirements:
- oauth_session_persistence

failed_tests:
- test_refresh_session

constraint_violations:
- introduced_new_database
However, the runtime MUST NOT interpret semantic meaning.

The runtime MUST NOT conclude:

- task is semantically complete
- implementation quality is sufficient
- explanation is conceptually clear
- architecture is aligned
These are agent cognition responsibilities.

4. Skills as Cognitive Operators
Skills are NOT command wrappers.

Skills act as cognitive operators between
the agent and the deterministic runtime.

The purpose of a skill is to:

negotiate cognition

recover task context

assess alignment

evaluate progress

resolve ambiguity

decide next actions

Skills SHOULD expose cognition-oriented operations.

Example:

recover_context()
evaluate_alignment()
assess_progress()
propose_next_step()
resolve_ambiguity()
Skills SHOULD NOT expose raw runtime commands directly.

Avoid:

run_command("judge run")
run_command("task create")
Prefer:

evaluate_constraints()
append_progress_snapshot()
recover_task_cognition()
5. Protocol Runtime Model
The runtime is a deterministic protocol executor.

The runtime:

persists cognition artifacts

assembles status planes

validates protocol structure

executes objective verification

exposes structured evidence

The runtime is NOT:

a planner

a workflow engine

an orchestration framework

a symbolic reasoning engine

a centralized cognition controller

6. Agent Execution Loop
mem0ress follows an agent-native cognition loop:

load_plane
  ↓
recover_cognition
  ↓
execute
  ↓
append_snapshot
  ↓
evaluate_alignment
  ↓
decide_next_action
The runtime participates only in deterministic stages.

The agent retains ownership of semantic progression.

7. Deterministic vs Semantic Boundaries


Behavior	Runtime	Agent
snapshot persistence	YES	NO
markdown parsing	YES	NO
state transitions	YES	NO
plane assembly	YES	NO
test execution	YES	NO
semantic interpretation	NO	YES
ambiguity resolution	NO	YES
task completion judgment	NO	YES
drift correction	NO	YES
picture alignment	NO	YES
recovery planning	NO	YES
Section: Skill Architecture
1. Skill Philosophy
Skills are cognition adapters.

A skill exists to bridge:

Agent Cognition
    ↕
Skill Layer
    ↕
Deterministic Runtime
The skill layer preserves the separation between:

semantic cognition

deterministic execution

2. Skill Categories
mem0ress defines three skill categories.

Cognitive Skills
Responsible for cognition recovery and alignment.

Examples:

recover_context

render_plane

evaluate_alignment

assess_progress

Execution Skills
Responsible for deterministic protocol mutation.

Examples:

create_task

append_snapshot

update_todo

close_task

Validation Skills
Responsible for objective verification.

Examples:

run_tests

validate_constraints

execute_judge

3. Skill Execution Model
Skills MAY internally invoke runtime commands.

However:

the agent SHOULD reason in cognition space

the runtime SHOULD execute in protocol space

The agent SHOULD NOT reason about CLI behavior directly.

4. Cognitive Recovery
Cognitive recovery is a first-class operation.

Agents SHOULD recover cognition through planes,
rather than reconstructing context from conversation history.

Preferred:

load_plane
  ↓
recover task cognition
Avoid:

reconstruct cognition from raw chat history
5. Skill Anti-Goals
Skills MUST NOT evolve into:

workflow orchestrators

centralized planners

hidden autonomous controllers

semantic rule engines

Skills exist to support cognition continuity,
not replace agent reasoning.
