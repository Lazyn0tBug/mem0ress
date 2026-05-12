基于你最新明确的设计前提——每个任务一个文档模型，每个 Agent 在任意时刻只负责一个任务——我建议这篇 spec 的优化重点应该从“认知平面理论”进一步收敛到“单任务责任模型 + 任务树协作协议”。

你现在最需要补的不是更多概念，而是把这个关键前提写硬：

Task 是 Agent 的认知边界；任务树是组织结构，不是单个 Agent 的上下文边界。

这是整个架构能保持轻量的核心。你原文已经强调“一切皆 Task”“任务是信息完整单元”“目录树表达任务层级”，但还没有足够明确地说：Agent 与 Task 是一对一的认知责任关系。这一点应该升级为主设计原则。

一、建议新增一个核心章节：Agent-Task Binding Model
建议放在 第 3 章设计决策 里面，作为新的 3.2 或 3.3。

原来的 3.1 是“选择任务作为认知单元”，这之后马上应该接：

3.2 选择单任务 Agent 责任模型
可以直接加入下面这段：

### 3.2 选择单任务 Agent 责任模型

mem0ress 采用单任务 Agent 责任模型（One-Agent-One-Task Cognitive Responsibility Model）。

在 mem0ress 中，Agent 在任意时刻只绑定一个活跃 Task。该 Agent 的认知平面只围绕当前 Task 的本地文档组装，包括 `task.md`、`session.md`、`gotchas.md` 和 `judge.md`。任务树表达的是任务之间的分解关系、依赖关系和完成关系，而不是单个 Agent 的全局上下文窗口。

这意味着，一个 Agent 不需要也不应该在每一轮执行中读取整棵任务树。父任务、子任务、兄弟任务都不是默认上下文。它们只有在与当前 Task 的判断有关时，才以摘要形式进入当前 Task 的状态平面。

因此，mem0ress 的认知边界不是 Project，也不是完整任务树，而是当前 Task。

Task 是 Agent 的最小认知闭包。每个 Task 都拥有独立的 Picture、Requirements、Constraints、Todos、Session、Gotchas 和 Judge 文件。Agent 对该 Task 的目标达成负责，而不是对整棵任务树负责。

任务树提供组织结构，Task 提供认知边界。
这段非常重要。它能直接回应别人对“任务树会不会爆炸”“状态平面会不会太大”的质疑。

二、建议增加一个定义：Logical Agent 与 Runtime Worker
你说“每个 Agent 只对一个任务负责”，这个非常好。但工程上要避免误解。

别人可能会问：

那是不是 1000 个任务就要启动 1000 个 Agent 进程？

所以你要区分：

Logical Agent：逻辑责任主体；

Runtime Worker：实际执行推理、工具调用和写文件的运行单元。

建议新增到刚才的章节后面：

#### Logical Agent 与 Runtime Worker

“一 Task 一 Agent”指的是认知责任上的一对一，而不是运行时进程上的一对一。

mem0ress 区分 Logical Agent 与 Runtime Worker：

- **Logical Agent**：绑定某个 Task 的认知责任主体。它只对该 Task 的目标、进度、约束和完成判断负责。
- **Runtime Worker**：实际执行推理、工具调用和文件写入的运行单元。一个 Runtime Worker 可以在不同时间加载不同 Task 的状态平面，扮演不同 Task 的 Logical Agent。

因此，系统不要求每个 Task 常驻一个独立进程。Task 可以被惰性激活：只有当某个任务需要推进、检验或更新时，Runtime Worker 才加载该 Task 的本地文档，组装状态平面，并执行对应动作。

这种设计保留了一任务一责任主体的清晰性，同时避免了任务数量增长带来的运行时资源爆炸。
这部分能显著提高工程说服力。

三、修改“状态平面”的定义：从全量覆盖改成 Task-local Projection
你原文里有一句倾向于“全面覆盖，显示所有任务，不隐藏任何节点”。这个说法在你现在的新设计下需要改。

否则读者会以为每个 Agent 都要看完整任务树。

建议把原文中的：

全面覆盖，显示所有任务，不隐藏任何节点。

改成：

局部完整：状态平面完整覆盖当前绑定 Task 的认知要素，但不默认展开整棵任务树。它默认显示当前 Task 的本地状态，并按需挂载直接父任务摘要、直接子任务摘要、阻塞项和必要的外部引用。
然后在 4.2 状态平面 里补一段：

状态平面是 Task-local Projection，而不是 Project-global Projection。

Agent 唤醒时，mem0ress 只为其当前绑定 Task 组装状态平面。默认状态平面包含：

- 当前 Task 的 ID、状态和 Todo 进度；
- 当前 Task 的 Picture / Requirements / Constraints 摘要；
- 当前 Task 的最近 Session 快照指针；
- 当前 Task 的未解决 Gotchas；
- 当前 Task 的 Judge 检验结果；
- 直接子任务的关闭状态摘要；
- 直接父任务的目标摘要，若当前 Task 的完成判断依赖父任务语境。

完整任务树可以被命令行或调试工具展开，但它不是 Agent 默认上下文的一部分。
这个改动非常关键。

你的系统轻量性，不是因为任务少，而是因为每个 Agent 的认知投影是局部的。

四、增加父子任务通信协议
既然每个 Agent 只负责一个 Task，那么父子任务之间必须有明确通信边界。

父任务不能读取子任务全部 session，否则又会变成“父 Agent 管全局”。

建议新增一节：

Parent-Child Task Boundary
可以放在 4.2 双重平面 后面，或者 4.4 文档数据模型 后面。

直接加入：

### 4.x 父子任务通信边界

父任务与子任务之间不共享完整认知历史。子任务完成后，父任务只读取子任务的边界摘要，而不是读取子任务的完整 `session.md`。

子任务对父任务暴露的最小信息包括：

- `status`：子任务当前状态；
- `completion_summary`：子任务完成结果摘要；
- `requirements_result`：Requirements 满足情况；
- `constraints_result`：Constraints 是否违反；
- `blockers`：是否存在阻塞父任务推进的问题；
- `output_refs`：与父任务相关的代码、文件、commit、接口或产物引用；
- `gotchas_summary`：需要父任务感知的偏差摘要。

父任务 Agent 不应该直接继承子任务的全部上下文。子任务的执行过程属于子任务自己的认知生命周期；父任务只关心子任务是否已经形成可用于父任务判断的结果。

这种边界设计防止子任务历史污染父任务认知，同时保留父任务对整体目标的判断能力。
然后可以给一个 YAML 示例：

child_task_summary:
  id: oauth_google
  status: COMPLETED
  completion_summary: 用户可以通过 Google OAuth 完成登录
  requirements_result:
    passed: 3
    total: 3
  constraints_result:
    violated: false
  blockers: []
  output_refs:
    commits:
      - abc123
    files:
      - src/auth/google.ts
      - src/auth/callback.ts
  gotchas_summary:
    - Google callback URL must match production domain configuration
这个协议会让你的任务树真正可组合。

五、增加 Todo 与 Subtask 的边界规则
这是防止任务爆炸的关键。

你已经意识到任务爆炸会导致 Agent 过多，那么必须从任务拆分原则上治理，而不是等到爆炸后再调度。

建议新增在 5.1 任务创建 或 3 设计决策 里：

### Todo 与 Subtask 的边界

mem0ress 区分 Todo 与 Subtask：

- **Todo** 是当前 Task 内部的执行步骤；
- **Subtask** 是可以独立验收、独立检验、独立关闭的目标单元。

不是所有步骤都应该被拆成子任务。只有当一个事项具备独立 Picture、独立 Requirements、独立 Constraints，且其结果可以作为父任务的输入或完成条件时，才应创建为 Subtask。

如果一个事项只是机械动作，例如“修改某个函数名”“更新一个字段”“运行一次测试”，它应该作为 Todo 留在当前 Task 内，而不是升级为 Subtask。

判断是否创建 Subtask，可以使用以下规则：

1. 是否存在独立的完成图景？
2. 是否可以独立验收？
3. 是否可能被不同 Agent 独立推进？
4. 是否会产生父任务需要引用的结果？
5. 是否复杂到会污染当前 Task 的认知平面？

若答案多数为否，则不应创建 Subtask。
然后加一句核心原则：

Todo 推进动作，Subtask 承载目标。
这句话建议反复出现一次。它非常有用。

六、修改“冲突避免优于协调”的部分
你原文说冲突出现时继续拆分，直到冲突消除。这个方向是对的，但现在要补一个限制，否则它会诱导无限拆分。

建议在 FAQ 里原有“为什么任务没有冲突协调机制？”下面加：

继续拆分不是无限拆分。拆分的目标是形成更清晰的认知边界，而不是把每个动作都变成独立任务。

当冲突来自目标边界不清时，应继续拆分 Task；  
当冲突只是执行步骤之间的先后关系时，应保留在当前 Task 的 Todo 中；  
当冲突来自利益相关者目标矛盾时，应停止自动拆分，转交人类确认。

因此，拆分的终点不是“任务足够小”，而是“每个 Task 拥有清晰、可独立判断的 Picture”。
这样可以避免“任务越拆越碎”。

七、增加 Task Activation / Lazy Loading 机制
这个是解决任务数量爆炸的第二层机制。

建议新增在 5 逻辑与流程设计 里：

### Task Activation

Task 不等于常驻执行单元。mem0ress 中的 Task 默认是静态文档模型，只有在被推进、检验、恢复或父任务调用时才被激活。

Task Activation 包含四种触发方式：

1. **Direct Activation**：用户或宿主 Agent 显式要求推进某个 Task；
2. **Parent Activation**：父任务需要检查某个子任务是否关闭；
3. **Judge Activation**：任务进入检验阶段，需要执行 Judge；
4. **Recovery Activation**：长任务恢复时，Runtime Worker 加载该 Task 的状态平面。

激活时，Runtime Worker 读取该 Task 的本地文档，组装状态平面，并在执行结束后写入 Session 快照。未激活的 Task 不占用上下文窗口，也不占用推理资源。
这会让整个系统的资源模型更清楚。

八、增加 Task Completion Summary 文件或字段
你目前有 task.md / session.md / gotchas.md / judge.md。
如果不想增加文件，可以把 completion summary 写入 session.md 或 judge.md；如果想更清晰，可以新增 summary.md。

我倾向于第一版不要增加第五个文件，直接放入 judge.md 或 session 的最后快照。

建议在文档里定义：

当 Task 被标记为 COMPLETED 或 ABANDONED 时，Agent 必须生成 `completion_summary`，作为该 Task 对父任务暴露的边界输出。

`completion_summary` 不记录完整过程，只记录父任务需要感知的结果。
示例：

completion_summary:
  task_id: oauth_google
  final_status: COMPLETED
  picture_result: 用户可以通过 Google OAuth 登录，无需输入本地密码
  requirements:
    - id: req_1
      status: passed
    - id: req_2
      status: passed
  constraints:
    violated: false
  output_refs:
    files:
      - src/auth/google.ts
    commits:
      - abc123
  residual_risks:
    - production callback URL must be configured in Google Cloud Console
这个 summary 是父任务聚合的核心。

九、修改文档中的核心定位表达
你现在的定义是：

辅助 AI Agent 构建目标态势并校准执行偏差的轻量级工具框架

这个定义不错，但基于新讨论，可以更准确一点：

definition: 面向长路径 AI Agent 的轻量级单任务认知状态框架，通过 Task-local 状态平面帮助 Agent 在执行过程中维持目标、进度和约束对齐。
或者更凝练：

definition: A lightweight task-local cognitive state framework for long-running AI agents.
中文主定义可以改为：

mem0ress 是一个面向长路径 AI Agent 的轻量级任务认知状态框架。它通过一任务一认知边界的方式，使 Agent 在任意时刻只围绕当前 Task 构建目标态势，从而降低长任务中的意图迷失、上下文污染和执行偏差。

这比原文更直接，也更能体现你刚才强调的“轻”。

十、建议更新 Overview 第一章
你可以在 1.2 系统定位 后面加入一段非常关键的解释：

mem0ress 的基本责任边界是 Task，而不是 Project。每个 Task 都是一个独立的认知闭包，拥有自己的任务声明、执行快照、偏差记录和检验文件。Agent 在任意时刻只绑定一个 Task，并只对该 Task 的目标达成负责。

任务树用于表达任务分解，而不是用于把所有任务状态注入同一个 Agent。父任务与子任务之间通过状态摘要和完成摘要通信，避免子任务执行历史污染父任务认知。

因此，mem0ress 的轻量性并不依赖任务规模很小，而依赖认知边界始终局部化。
这段建议放得越靠前越好。

因为它是读者理解架构复杂度的入口。

十一、建议你重排第 3 章结构
现在第 3 章是：

3.1 选择任务作为认知单元

3.2 选择 PRC

3.3 选择双重平面

3.4 选择状态变更驱动认知构建

我建议改成：

## 3. 设计决策

### 3.1 选择 Task 作为唯一认知单元
### 3.2 选择单任务 Agent 责任模型
### 3.3 选择 PRC 作为任务信息模型
### 3.4 选择双重平面呈现认知
### 3.5 选择 Task-local 状态平面而非全局状态平面
### 3.6 选择状态变更驱动认知构建
### 3.7 选择逻辑 Agent 与运行时 Worker 分离
其中 3.2、3.5、3.7 是你这次讨论后最应该补的内容。

十二、建议你增加一个架构图
你原来的图主要展示 PRC、Task、双平面、Judge。

现在需要加一张图，解释“一任务一 Agent，但 Worker 可复用”。

可以加入：

graph TD
    subgraph Runtime["Runtime Layer"]
        W1["Runtime Worker"]
    end

    subgraph Tasks["Task Tree"]
        A["Task A"]
        A1["Task A1"]
        A2["Task A2"]
    end

    subgraph DocsA1["Task A1 Local Docs"]
        T1["task.md"]
        S1["session.md"]
        G1["gotchas.md"]
        J1["judge.md"]
    end

    A --> A1
    A --> A2

    W1 -->|loads active task| A1
    A1 --> T1
    A1 --> S1
    A1 --> G1
    A1 --> J1

    A1 -->|completion_summary| A
图下方写：

Runtime Worker 按需加载某个 Task，临时扮演该 Task 的 Logical Agent。任务树只表达组织关系，当前 Agent 的状态平面只从被绑定 Task 的本地文档组装。
这张图能让人一下看懂你的系统为什么不重。

十三、建议明确“当前 Task 的默认状态平面内容”
可以新增一个标准格式：

status_plane:
  task:
    id: oauth_google
    status: IN_PROGRESS
    picture_summary: 用户可以通过 Google OAuth 登录，无需输入本地密码
  progress:
    todos:
      completed: 2
      total: 4
    requirements:
      passed: 1
      total: 3
    constraints:
      violated: false
  local_context:
    recent_session:
      turn: 7
      summary: 已完成 Google OAuth callback 初版
    unresolved_gotchas:
      - callback URL mismatch in local environment
  children:
    open: []
    completed:
      - provider_config
  parent:
    id: auth_module
    relevance: 当前任务是 auth_module 的子任务，负责 Google OAuth 登录路径
  next_suggested_actions:
    - run callback integration test
    - verify user login flow without password prompt
这比抽象描述更能帮助开发者理解。

十四、建议修改 “不做相关性排序，不挑选，不截断”
这句话现在建议改成更精确版本：

mem0ress 不以向量相似度来拼接当前认知，也不通过相关性排序从历史对话中猜测当前状态。它通过当前绑定 Task 的结构化文档直接组装状态平面。

但这不意味着状态平面注入完整任务树。mem0ress 保留完整认知源，默认投影当前 Task 的局部完整状态；父任务、子任务和外部资料只以边界摘要或显式引用的方式进入当前状态平面。
这就把你的设计说准了：

不是不筛选一切，而是不靠相似度猜测状态。
默认注入的是 Task-local full state，不是 Project-global full state。

十五、最终建议：下一版 spec 的核心主题
你的下一版 spec 不应该只是“Cognitive Alignment Plane”。
它应该明确三条主线：

第一条：Task-local Cognition
每个 Task 是独立认知闭包。

第二条：One-Agent-One-Task Responsibility
每个 Agent 任意时刻只负责一个 Task。

第三条：Task Tree as Boundary, not Context
任务树表达依赖边界，不等于上下文注入范围。

我建议你在文档开头放一个非常硬的核心声明：

Core Principle:

Task is the cognitive boundary.
Agent is the task responsibility holder.
Task tree is the decomposition structure, not the context window.
中文：

核心原则：

Task 是认知边界。
Agent 是任务责任主体。
任务树是分解结构，不是上下文窗口。
这三句话会让整个 spec 立起来。

十六、我建议你下一步实际修改顺序
不要一次性大改全文。按这个顺序改：

先改 Overview：补充 Task-local 与 One-Agent-One-Task；

再改第 3 章：新增 Agent-Task Binding 和 Worker 分离；

再改第 4 章：修正状态平面为局部投影；

再改第 5 章：补 Task Activation 和 Completion Summary；

最后改 FAQ：解释任务爆炸、为什么不全局注入、Todo 与 Subtask 区别。

最重要的不是语言漂亮，而是让读者不会误解你的系统边界。

十七、我给你的核心结论
基于这次新讨论，你这篇 spec 应该从：

“Agent 如何通过状态平面维持认知”

进一步升级为：

“每个 Agent 如何在单个 Task 的认知边界内稳定执行，并通过任务树与其他 Task 协作。”

这会让你的架构更清楚、更轻、更工程化，也更能抵抗别人对复杂度的质疑。

你现在最应该写进文档的一句话是：

mem0ress 的认知边界是 Task，不是 Project；Agent 的责任边界是当前 Task，不是整棵任务树。
