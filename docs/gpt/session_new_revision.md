这版已经从“理论蓝图”进入“可讨论的架构规约”阶段了，但还没有完全达到“合格的 v0.1 协议 spec”标准。

现在最大的问题不再是方向，而是 一致性、边界表达、协议可执行性 三件事。

一、已经明显变好的地方
1. Task-local 定位已经立住了
你把定义改成了“基于本地文件系统的 Task-local Agent 状态框架”，这是对的。文档里也新增了“一 Agent 一 Task”的责任模型，并明确 Agent 不应该每轮读取整棵任务树，当前认知边界是 Task 而不是 Project。这个改动非常关键，已经解决了之前“状态平面是否会膨胀”的核心误解。

2. Logical Agent / Runtime Worker 区分是加分项
你现在写清楚了 Logical Agent 是认知责任归属，Runtime Worker 是实际执行实体，并说明 mem0ress 只规定认知边界，不规定执行资源分配。这部分已经比较成熟。

3. 父子任务边界开始成型
你新增了 Parent-Child Boundary，强调父任务不读取子任务状态平面，子任务也不读取父任务状态平面，父子任务各自保持认知边界。这个方向对。

4. Todo / Subtask 的边界更清楚了
你在任务创建部分补充了：Todo 是任务内部机械步，Subtask 是独立 Task，区别标准是是否有独立 Picture。这个判断很准，能防止任务无限碎片化。

二、目前还不合格的关键问题
问题1：Status Plane 还有明显自相矛盾
这是最需要改的地方。

前面你已经写了：

Agent 只绑定一个活跃 Task，不读取整棵任务树。

但后面在认知构建里又写：

状态平面“全面覆盖，显示所有任务，不隐藏任何节点”。

这两句话冲突。前者是 Task-local，后者像 Project-global。你需要统一。

建议改成：

状态平面是当前绑定 Task 的忠实投影，而不是项目级全量视图。

在当前 Task 边界内，状态平面不做相关性排序、不挑选、不截断；但它不默认展开整棵任务树，也不默认读取父任务、子任务或兄弟任务的完整状态。父子任务信息只有在当前 Task 的 Picture 判断需要时，才以 completion_summary 或状态摘要形式进入状态平面。
你要保留“不排序、不挑选、不截断”，但必须加上限定：

within active Task boundary

否则读者会再次误解。

问题2：父子任务通信被你写得过于极端
你现在写：

父子任务之间只有一条通信通道：父任务的 Picture 拆解为子任务的创建。
子任务中间过程不进入父任务任何文档。

这个方向对，但太绝对。因为你后面又写了 completion_summary 会写入父任务 session.md，作为父任务认知构建输入。

所以应该改成：

父子任务之间有两类合法通信：创建时的任务分解输入，关闭时的 completion_summary 输出。

建议这样写：

父子任务之间存在两条合法通信通道：

1. 创建通道：父任务将自身 Picture 的一部分拆解为子任务的初始 Picture；
2. 关闭通道：子任务完成后向父任务暴露 completion_summary，作为父任务后续认知构建的输入。

除此之外，父任务不读取子任务完整 session、gotchas、judge 或状态平面；子任务也不继承父任务完整状态平面。
这样更准确。

问题3：completion_summary 不应该只写进父任务 session.md
你现在把 completion_summary 设计成“写入父任务 session.md”。这可以作为一种实现，但不建议作为唯一协议。

原因是：completion_summary 是子任务对外暴露的边界输出，它应该首先属于子任务自身，然后被父任务引用或读取。

我建议改成：

子任务目录下生成 completion_summary.md；
父任务 session.md 只记录一条 summary_received 事件或指针。
例如：

child_completion:
  child_task_id: oauth_google
  summary_ref: children/oauth_google/completion_summary.md
  status: COMPLETED
这样父任务不用吞掉子任务 summary 的全部内容，也能保持引用清楚。

问题4：Judge Tier 3 仍然太薄
你现在的 Tier 3 还是“读取 Picture 与实际产出，执行语义对齐判断”。这比旧版好一些，但还没有体现我们讨论过的 Picture Claims / Evidence Mapping / Residual Gap Detection。

目前它仍然容易被理解为：

让 LLM 看一眼，判断是否对齐。

这还不够。

建议你把 5.3 里的 Tier 3 改成：

Tier 3: Picture Alignment Check。

Tier 3 不重复验证 Requirements，而是检查 Requirements 无法穷尽的 Picture 剩余语义偏差。执行时，Judge Agent 将 Picture 拆解为 Picture Claims，并将 Requirements 结果、Constraints 状态、Data Plane 证据、未解决 Gotchas 和实际产出映射到这些 Claims 上。

若存在核心 Picture Claim 缺少证据覆盖，或存在足以阻止利益相关者认可任务完成的 residual gap，则任务不得关闭。若证据不足，Tier 3 必须返回 UNCERTAIN，而不是强行 PASS 或 FAIL。
这部分是你 spec 的技术亮点，不能只写成“语义对齐检查”。

问题5：状态机还不够真实
你现在仍然只有：

CREATED / IN_PROGRESS / VERIFYING / COMPLETED / ABANDONED
这对理论模型够，但对工程执行不够。尤其是长任务中经常会出现：

BLOCKED
NEEDS_USER
你现在文档里说如果 Requirements 与 Constraints 矛盾，会引导协作者修正；如果任务执行卡住，也会产生 Gotcha。但状态机没有表达这些中间状态。

我建议至少在 v0.1 里加入：

BLOCKED：被外部条件、子任务、环境、依赖或错误阻塞
NEEDS_USER：需要利益相关者补充信息或确认
如果你不想让 v0.1 变复杂，可以标注：

BLOCKED / NEEDS_USER 为 v0.1-beta 推荐状态，v0.1-alpha 可先以 Gotcha + IN_PROGRESS 表达。
但最好别完全不提。

三、还需要补的“合格线内容”
如果你问“怎样才算合格”，我认为至少要补这 6 个小节。

1. Core Principles 独立小节
现在原则散落在各章里。建议在第 1 章或第 3 章前新增：

## Core Principles

1. Task is the cognitive boundary.
2. Agent is the task responsibility holder.
3. Task tree is decomposition, not context.
4. Status plane is faithful projection.
5. Session records state changes, not full history.
6. Requirements are necessary but not sufficient for Picture.
7. Judge detects residual semantic gaps.
这能极大提升文档可读性。

2. Faithful Projection 正式定义
你现在最后仍然写“不做相关性排序，不挑选，不截断”，但没有给它一个正式概念。建议加：

### Faithful Projection

状态平面的边界由当前绑定 Task 决定，而不是由相关性算法决定。

在当前 Task 边界内，mem0ress 不通过相关性排序、语义挑选或摘要截断来决定哪些状态重要，而是从协议文件中直接组装当前完整可判断状态。
这会把你最重要的差异化讲清楚。

3. Picture Alignment Judge 独立小节
不要把 Tier 3 淹没在 5.3 里。建议新增：

### 5.4 Picture Alignment Judge
或者在第 4 章后新增独立小节：

### Picture Claims and Residual Gap Detection
至少要包含：

Picture Claims
Evidence Mapping
Residual Gaps
Stakeholder Acceptance Risk
UNCERTAIN
can_close_task
suggested_requirement_updates
4. 文件协议要补 completion_summary.md
你现在四个核心文档还是：

task.md / session.md / gotchas.md / judge.md
但后文已经引入 completion_summary。这里不一致。

建议改成五个核心文档：

task.md
session.md
gotchas.md
judge.md
completion_summary.md
如果你暂时不想加独立文件，也要写清楚：

v0.1-alpha 中 completion_summary 可作为 session.md 的结构化记录；
v0.1-beta 起推荐独立 completion_summary.md。
但协议层面必须有它的位置。

5. 模板协议要收紧
你现在在“协议规范”里列了：

PROTOCOL.md
SCHEMA.md
EXAMPLE.md
judge.md
这部分有点奇怪。judge.md 既是核心文档，又出现在 docs/templates 规范表里，角色混乱。

建议改成：

**配套规范：**

| 文件 | 用途 | 阶段 |
|---|---|---|
| PROTOCOL.md | 行为契约 | v0.1-alpha |
| TEMPLATES.md | 核心文件模板 | v0.1-alpha |
| EXAMPLE.md | 完整示例 | v0.1-alpha |
| SCHEMA.md | 字段约束与校验规则 | v0.1-beta |
不要把 judge.md 放在“协议规范”表里，它应该是 Task 目录下的核心运行文件。

6. MVP Scope / Roadmap 需要放进正文
现在文档还是“Master Blueprint”，但定义已经写成 Task-local Agent 状态框架。建议明确版本边界：

## MVP Scope

v0.1-alpha 必须支持：
- 本地文件系统
- Task-local 状态平面
- task/session/gotcha/judge/completion_summary
- One-Agent-One-Task
- Judge Tier 0/1/2
- Tier 3 结构化输出协议

v0.1-alpha 不支持：
- 多 Worker 并发写入
- 全自动任务拆分
- 多 Agent 调度
- 数据库后端
- 向量记忆
- 完整 Schema 校验
没有这个边界，读者会不知道它是理论规约还是 MVP 协议。

四、我的合格标准
我会这样判断：

目前评分
思想完整度：8.5/10
架构清晰度：8/10
Task-local 表达：8/10
协议可执行性：6.5/10
Judge Tier 3 成熟度：6/10
MVP 边界清晰度：6/10
改完这些以后
如果你补上：

Faithful Projection 正式定义
Picture Alignment Judge 独立小节
completion_summary.md 位置
MVP Scope / Roadmap
状态机补 BLOCKED / NEEDS_USER 或标注路线图
修正状态平面“显示所有任务”的冲突表达
那这份 spec 就可以到：

架构规约合格：是
MVP 协议合格：基本合格
可交给开发者实现：可以，但仍需模板和字段约束
五、最应该优先改的 5 处
按优先级来：

第一，改 5.2 认知构建中“全面覆盖，显示所有任务”这句话。
这是当前最大冲突。

第二，把 4.2 父子任务边界改成“两条通信通道”：创建通道 + completion_summary 通道。

第三，把 completion_summary 从“写入父任务 session”改成“子任务边界输出，父任务引用”。

第四，把 Tier 3 扩展为 Picture Alignment Judge，而不是普通语义对齐。

第五，增加 MVP Scope / Roadmap，明确哪些是 v0.1-alpha 必须实现，哪些是后续。

最终结论
这版已经比原版强很多，特别是 One-Agent-One-Task、Logical Agent / Runtime Worker、父子任务边界、Todo/Subtask 区分 都已经补上了。

但要“合格”，还必须解决一个核心问题：

你现在已经接受 Task-local，但文档里仍残留了一些 Project-global 语言。

把这些残留清掉，再把 Faithful Projection、Picture Alignment Judge、completion_summary、MVP Scope 四块写硬，这份 spec 就基本成型了。
