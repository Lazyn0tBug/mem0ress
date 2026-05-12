需要更新 MVP。而且不是小修小补，是需要把 MVP 的核心边界从“项目级任务状态管理”调整成：

Task-local MVP：一个 Agent / Worker 每次只加载一个 Task 的认知状态。

但好消息是：这不是推翻原来的 MVP，而是让 MVP 更轻、更清楚、更容易落地。

我建议你更新 MVP 的重点
1. MVP 的核心定义要改
原来的 MVP 可以理解成：

mem0ress 维护一棵任务树，并为 Agent 组装状态平面。

现在应该改成：

mem0ress 维护任务树，但每次只为一个当前 Task 组装局部状态平面。

更准确的 MVP 定义：

mem0ress v0.1 是一个基于本地文件系统的 Task-local Agent 状态框架。
它以一个 Task 目录为最小认知单元，为当前绑定 Task 生成状态平面，
帮助 Agent 在单个任务边界内维持 Picture、Requirements、Constraints、Todo、Session、Gotchas 和 Judge 的一致性。
核心变化是：

任务树仍然存在，但不再是默认注入上下文的对象。当前 Task 才是默认上下文。

2. CLI 命令需要稍微调整
原来我建议的是：

mem0ress init
mem0ress task create
mem0ress task status
mem0ress task update
mem0ress session append
mem0ress plane build
mem0ress judge run
现在建议改成更 Task-local 的版本：

mem0ress init

mem0ress task create
mem0ress task show <task_id>
mem0ress task list
mem0ress task close <task_id>

mem0ress bind <task_id>
mem0ress plane build
mem0ress session append
mem0ress judge run

mem0ress child summary <task_id>
mem0ress task activate <task_id>
其中最重要的是新增：

mem0ress bind <task_id>
它表示：

当前 Runtime Worker 绑定到某一个 Task，接下来所有 plane / session / judge 操作都围绕这个 Task 执行。

这样 MVP 就能体现你的核心思想：一个 Agent 在任意时刻只负责一个 Task。

3. plane build 必须改成局部状态平面
原来的 plane build 如果会扫描整棵任务树，那就需要改。

新的规则应该是：

mem0ress plane build
默认只读取当前绑定 Task：

.mem0ress/tasks/{task_id}/task.md
.mem0ress/tasks/{task_id}/session.md
.mem0ress/tasks/{task_id}/gotchas.md
.mem0ress/tasks/{task_id}/judge.md
最多附带：

parent summary
direct children summary
open blockers
completion_summary
不要默认读取所有兄弟任务、所有孙任务、所有历史 session。

也就是说：

默认状态平面 = 当前 Task 的局部完整状态
不是整个 Project 的全局状态
4. 需要增加一个绑定状态文件
为了让 MVP 简单，可以加一个本地文件：

.mem0ress/current
内容很简单：

active_task: oauth_google
这样：

mem0ress bind oauth_google
就是写入：

active_task: oauth_google
之后：

mem0ress plane build
mem0ress session append
mem0ress judge run
都默认针对这个 active task。

这比每个命令都传 --task 更符合“当前 Agent 只负责一个任务”的思想。

当然也可以保留：

mem0ress plane build --task oauth_google
作为显式模式。

5. 文档模型需要增加 completion_summary
MVP 最好不要新增第五个文件。可以直接把它放进 judge.md 或 session.md 的最后一段。

我建议放在 judge.md，因为它是任务检验完成后的边界输出。

例如：

completion_summary:
  task_id: oauth_google
  final_status: COMPLETED
  picture_result: 用户可以通过 Google OAuth 登录，无需输入本地密码
  requirements:
    passed: 3
    total: 3
  constraints:
    violated: false
  blockers: []
  output_refs:
    files:
      - src/auth/google.ts
      - src/auth/callback.ts
    commits:
      - abc123
  residual_risks:
    - production callback URL must match Google Cloud configuration
父任务读取子任务时，只读取这个 summary，不读取子任务完整 session。

这是防止父任务 Agent 被污染的关键。

6. MVP 暂时不需要真正启动多个 Agent
这一点很重要。

你不需要在 v0.1 里真的实现多 Agent 调度。

MVP 里只需要做到：

一个 Runtime Worker 可以 bind 不同 Task。
每次 bind 后，它只加载当前 Task。
也就是说，MVP 实现的是：

Logical Agent model，不是 full multi-agent runtime。

这非常合理。

不要一上来做 worker pool、队列、并发调度、多 Agent 通信。那些是 v0.2 或 v0.3 的事情。

7. MVP 应该新增 task activate
为了表达“Task 不常驻，只按需激活”，可以有：

mem0ress task activate <task_id>
它做的事情其实可以很轻：

设置 active_task；

读取该 task 的本地文档；

生成 status plane；

输出给 Agent。

本质上它可以等价于：

mem0ress bind <task_id>
mem0ress plane build
但从语义上，activate 很好，因为它表达了：

Task 是静态文档模型，只有被推进时才被加载。

我建议的 v0.1 MVP 最小功能清单
如果现在重定 MVP，我会这样写：

mem0ress v0.1 MVP

1. init
   创建 .mem0ress 目录结构

2. task create
   创建一个 Task 目录和 task.md / session.md / gotchas.md / judge.md

3. bind / activate
   将 Runtime Worker 绑定到一个 active Task

4. plane build
   只基于 active Task 生成 Task-local status plane

5. session append
   向 active Task 的 session.md 追加一轮状态快照

6. judge run
   基于 active Task 的 PRC / Todo / Gotchas / 子任务摘要执行检验

7. child summary
   为父任务生成或读取子任务 completion_summary

8. task close
   将 active Task 标记为 COMPLETED 或 ABANDONED，并生成 completion_summary
这就是最小闭环。

暂时不要做的内容
v0.1 不建议做：

全局任务树智能调度
多 Agent 并发执行
复杂权限系统
向量检索
数据库后端
Web UI
长期记忆
自动任务拆分优化
多 Worker 池
跨任务冲突协调
这些都会把 MVP 搞重。

你现在要证明的是一个非常具体的命题：

当 Agent 每次只围绕一个 Task-local 状态平面工作时，长任务执行是否更稳定、更少偏航。

不是证明一个完整操作系统。

最关键的代码/结构更新
目录结构建议改成这样：

.mem0ress/
├── current
└── tasks/
    └── auth_module/
        ├── task.md
        ├── session.md
        ├── gotchas.md
        ├── judge.md
        └── oauth_google/
            ├── task.md
            ├── session.md
            ├── gotchas.md
            └── judge.md
.mem0ress/current：

active_task: auth_module/oauth_google
worker_id: default
plane build 输出：

status_plane:
  active_task:
    id: auth_module/oauth_google
    status: IN_PROGRESS
    picture: 用户可以通过 Google OAuth 登录，无需输入本地密码

  progress:
    todos:
      completed: 2
      total: 4

  requirements:
    passed: 1
    total: 3

  constraints:
    violated: false

  gotchas:
    unresolved:
      - callback URL mismatch in local environment

  parent:
    id: auth_module
    summary: 当前任务属于认证模块，负责 Google OAuth 登录路径

  children:
    open: []
    completed: []

  next_actions:
    - verify callback flow
    - run integration test
这个就足够轻。

我的结论
需要更新 MVP。

但更新方向不是增加复杂度，而是削减复杂度：

从：

项目级任务树状态系统

改成：

Task-local 单任务认知状态系统

从：

Agent 管理整棵任务树

改成：

Agent 每次只绑定一个 Task

从：

全局状态平面

改成：

当前 Task 的局部完整状态平面

从：

多 Agent 常驻系统

改成：

Logical Agent + Runtime Worker 按需加载

这会让你的 MVP 更容易实现，也更能体现你这个设计真正的优势。
