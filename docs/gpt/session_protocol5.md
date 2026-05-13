这是一个非常关键的问题。

因为很多系统最后会变成：

spec 里写了一半 protocol
manifest 里又重复一半 spec
最终：

边界混乱
协议失真
runtime 不知道该信谁
你现在其实已经走到：

“思想规范（Spec）”与“运行时契约（Manifest）”分层的节点。

我建议你用一句话作为根边界：

核心分界原则
Spec 描述“为什么”和“应该是什么”；
Manifest 描述“当前 runtime 实际采用什么”。
或者更工程化一点：

Spec = normative architecture
Manifest = executable contract
一、Spec 应该负责什么？
Spec 是：

架构原则
认知模型
协议语义
行为边界
设计哲学
生命周期定义
抽象规则
它回答的是：

Task 是什么？
Picture 为什么重要？
Faithful Projection 是什么？
Judge 为什么存在？
为什么是 One-Agent-One-Task？
为什么 Parent/Child 要隔离？
也就是说：

Spec 是“协议语义层”。

二、Manifest 应该负责什么？
Manifest 是：

当前 workspace/runtime 的实际配置
它回答的是：

当前启用了哪些 Judge Tier？
completion_summary 是否 mandatory？
当前状态机有哪些状态？
是否允许 parallel worker？
当前 protocol version 是什么？
也就是说：

Manifest 是“协议实例层”。

三、最重要的一句话
你可以这样理解：



层	类比
Spec	编程语言规范
Manifest	当前项目 tsconfig/package.json
Runtime	实际执行器
例如：

JavaScript spec 定义 import 是什么
package.json 决定当前项目 module type
四、章节如何切分（非常重要）
我建议：

Spec 负责“静态协议语义”
也就是：

1. Core Principles
Task boundary
Faithful projection
One-Agent-One-Task
Picture vs Requirements
Residual semantic gaps
2. Cognitive Model
Task
Picture
Requirements
Constraints
Gotchas
Judge
Session
3. Runtime Semantics
注意：

不是 runtime configuration。

而是：

Task lifecycle semantics
Judge semantics
State transition meaning
Completion semantics
Parent-child visibility semantics
例如：

COMPLETED 意味着什么
VERIFYING 意味着什么
Tier 3 为什么存在
4. File Semantics
这里只定义：

task.md 的语义
session.md 的语义
judge.md 的语义
completion_summary 的语义
而不是：

当前 runtime 有没有启用 completion_summary
5. Protocol Guarantees
例如：

faithful projection guarantees
task-local guarantees
judge isolation guarantees
summary-only visibility guarantees
6. Extensibility Model
例如：

future vector memory
future distributed runtime
future skill registry
future worker pools
Manifest 负责“runtime 实例化”
Manifest 只做：

1. Version & Compatibility
protocol:
  version: 0.1-alpha
2. Enabled Features
features:
  tier3_judge: true
  vector_memory: false
3. Runtime Constraints
runtime:
  parallel_workers: false
4. State Machine Selection
states:
  - CREATED
  - IN_PROGRESS
  - BLOCKED
5. File Mapping
files:
  task: task.md
6. Capability Declaration
judge:
  uncertainty_allowed: true
五、Spec 不应该写的东西
这里非常关键。

Spec 不应该写：

tier3: enabled
因为：

enabled 是 runtime choice，不是协议语义。

Spec 只能写：

Tier 3 的含义是什么
Tier 3 的输入输出是什么
Tier 3 的判断边界是什么
六、Manifest 不应该写的东西
Manifest 不应该解释：

为什么要 faithful projection
为什么 Judge 存在
为什么 task-local
Manifest 不讲哲学。

Manifest 只声明：

projection_mode: faithful_projection
七、最容易犯的错误
这是最关键部分。

错误1：Spec 写成配置文件
例如：

默认开启 Tier3
默认关闭 parallel worker
这是 Manifest 内容。

错误2：Manifest 重新定义协议语义
例如：

COMPLETED:
  means: task fully aligned with picture
不行。

COMPLETED 的定义只能在 Spec。

Manifest 只能：

states:
  - COMPLETED
错误3：Manifest 引入新语义
例如：

projection_mode: smart_relevance
但 Spec 根本没定义。

这是绝对不允许的。

八、我建议的最终结构
spec.md
1. Vision
2. Core Principles
3. Cognitive Model
4. Task Lifecycle Semantics
5. Judge Semantics
6. File Semantics
7. Parent/Child Semantics
8. Faithful Projection
9. Protocol Guarantees
10. Extensibility Model
protocol.yaml
protocol:
  version: 0.1-alpha

runtime:
  projection_mode: faithful_projection
  parallel_workers: false

judge:
  tiers:
    - tier0
    - tier1
    - tier2
    - tier3

features:
  completion_summary: true

states:
  - CREATED
  - IN_PROGRESS
  - VERIFYING
  - COMPLETED
九、再进一步（这是高级设计）
未来你甚至可以做到：

Spec 是稳定协议
Manifest 是 runtime dialect
例如：

mem0ress-core
mem0ress-lite
mem0ress-distributed
mem0ress-cloud
它们：

共享同一个 Spec
但 Manifest 不同
这会非常强。

十、最终一句话
最本质的边界是：



Spec	Manifest
定义语义	选择语义
定义规则	声明能力
定义边界	声明配置
定义协议	实例化协议
稳定	可变化
面向架构	面向 runtime
我认为：

你现在已经非常接近“真正协议”的阶段了。

而真正协议最核心的一步，就是：

把“语义定义”与“运行时实例”彻底分离。
这是系统成熟度的重要分水岭。
