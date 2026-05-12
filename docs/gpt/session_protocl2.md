这几个文件是协议的“数据载体”，但还不够构成完整协议。

一个真正可实现、可验证、可扩展的协议，除了 task.md / session.md / gotchas.md / judge.md / completion_summary.md / current.yml 这些文件模板，还应该提供以下几类东西。

1. Protocol Manifest：协议总说明
你需要一个协议入口文件，例如：

protocol.md
或者：

SPEC.md
它回答：

mem0ress 是什么
协议版本是多少
有哪些核心文件
每个文件的职责是什么
文件之间的关系是什么
什么是 Task-local
什么是一 Agent 一 Task
哪些字段是必须的
哪些字段是可选的
哪些状态是合法的
哪些行为是不允许的
现在你的 task.md、session.md、gotchas.md、judge.md 已经分别定义了任务、执行快照、偏差记录和检验逻辑，但还缺少一个“总协议入口”把它们串起来。

建议结构：

docs/
└── protocol.md
核心内容：

# mem0ress Protocol v0.1-alpha

## Core Principle

Task is the cognitive boundary.
Agent is the task responsibility holder.
Task tree is the decomposition structure, not the context window.

## Core Files

- task.md
- session.md
- gotchas.md
- judge.md
- completion_summary.md
- current.yml

## Runtime Outputs

- status_plane
2. JSON Schema / YAML Schema：机器校验规则
这是非常关键的。

如果你只提供 Markdown 模板，开发者知道“应该怎么写”，但程序无法稳定判断“写得对不对”。

所以每个协议文件最好都有 schema。

建议提供：

schemas/
├── task.schema.json
├── session_turn.schema.json
├── gotcha.schema.json
├── judge_run.schema.json
├── completion_summary.schema.json
├── current.schema.json
└── status_plane.schema.json
这些 schema 用来校验：

字段是否存在
字段类型是否正确
状态值是否合法
ID 格式是否正确
引用的 Requirement / Todo / Constraint 是否存在
completion_summary 是否完整
judge final_result 是否符合枚举
例如：

{
  "$id": "mem0ress.task.schema.json",
  "type": "object",
  "required": ["protocol", "version", "type", "id", "status", "cognitive_triad", "todos"],
  "properties": {
    "protocol": { "const": "mem0ress" },
    "version": { "type": "string" },
    "type": { "const": "task" },
    "status": {
      "enum": ["CREATED", "IN_PROGRESS", "BLOCKED", "NEEDS_USER", "COMPLETED", "ABANDONED"]
    }
  }
}
我的意见很明确：
没有 schema，就还不是工程协议，只是模板。

3. State Machine：状态机规范
你需要单独提供一个状态机文档。

建议：

docs/state-machine.md
它定义：

Task 有哪些状态
哪些状态可以互相转换
哪些状态是终态
哪些状态是瞬态
谁有权改变状态
Judge 结果如何影响状态
BLOCKED 和 NEEDS_USER 的区别
COMPLETED 后是否可以 reopen
ABANDONED 后是否可以 supersede
建议状态：

CREATED
IN_PROGRESS
BLOCKED
NEEDS_USER
COMPLETED
ABANDONED
瞬态：

VERIFYING
推荐状态转换：

CREATED -> IN_PROGRESS
CREATED -> ABANDONED

IN_PROGRESS -> BLOCKED
IN_PROGRESS -> NEEDS_USER
IN_PROGRESS -> VERIFYING
IN_PROGRESS -> ABANDONED

VERIFYING -> COMPLETED
VERIFYING -> IN_PROGRESS
VERIFYING -> BLOCKED
VERIFYING -> NEEDS_USER

BLOCKED -> IN_PROGRESS
BLOCKED -> ABANDONED

NEEDS_USER -> IN_PROGRESS
NEEDS_USER -> ABANDONED

COMPLETED -> REOPENED 可选
ABANDONED -> SUPERSEDED 可选
MVP 可以不实现 REOPENED / SUPERSEDED，但协议里可以预留。

4. ID Convention：ID 命名规范
你必须给所有对象统一 ID 规则。

建议提供：

docs/id-conventions.md
例如：

Task ID:       oauth_google
Requirement:  R-1, R-2, R-3
Constraint:   C-1, C-2, C-3
Todo:         T-1, T-2, T-3
Gotcha:       G-001, G-002
Turn:         turn_0001, turn_0002
Judge Run:    judge_0001, judge_0002
Worker:       worker.default
Agent:        agent.oauth_google
还要规定：

ID 是否可以改名
改名后如何引用
Turn ID 是否全局唯一还是 Task-local 唯一
Gotcha ID 是否 Task-local 唯一
Task path 是否允许空格
Task path 是否区分大小写
我的建议：

所有子对象 ID 都是 Task-local 唯一；Task path 是项目内唯一。

5. Directory Layout：目录布局规范
除了文件模板，你还需要明确目录结构。

建议：

docs/directory-layout.md
示例：

.mem0ress/
├── current.yml
├── protocol.lock
├── config.yml
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
还要定义：

父子任务如何表达
children/ 是否必须存在
completion_summary.md 什么时候生成
task path 如何映射到文件路径
任务移动后如何处理 path
是否允许软链接
是否允许跨项目引用
MVP 建议不要支持跨项目引用。

6. Read / Write Rules：读写规则
协议不能只定义文件长什么样，还要定义谁能改、什么时候改。

建议：

docs/read-write-rules.md
例如：

task.md
可更新。
保存当前 Task 的声明和最新状态。
PRC 是唯一真源。
Todos 最新状态也在 task.md。
session.md
只追加。
每轮执行结束追加 Turn。
不重复记录 Picture / Requirements / Constraints。
gotchas.md
只追加。
Gotcha 可以追加 resolution update。
不删除历史记录。
judge.md
Judge Plan 可更新。
Judge Runs 只追加。
Judge final 不能静默覆盖。
completion_summary.md
任务关闭时生成。
父任务默认只读取 completion_summary。
重新打开任务后，旧 summary 标记 superseded。
这类规则很重要，否则不同实现会乱写文件，协议就会分裂。

7. Plane Assembler Spec：状态平面组装规则
你现在定义了文件，但还需要定义：

如何从这些文件组装 status_plane。

建议提供：

docs/status-plane.md
它回答：

plane build 默认读取哪些文件
读取多少条 session
是否读取 gotchas 全量
如何读取父任务
如何读取子任务
什么时候读取 completion_summary
data_plane 从哪里来
next_suggested_actions 从哪里来
字段冲突时以谁为准
推荐规则：

默认读取：
- 当前 Task 的 task.md
- 当前 Task 的 session.md 最近 N 条
- 当前 Task 的 unresolved gotchas
- 当前 Task 的 latest judge run
- 当前 Task 的 completion_summary，如存在
- 直接父任务的摘要
- 直接子任务的 status / completion_summary

默认不读取：
- 兄弟任务
- 孙任务
- 父任务完整 session
- 子任务完整 session
- 全项目历史
这就是 Task-local 的核心实现。

8. Judge Execution Spec：Judge 执行规范
judge.md 只是文件，但还需要一个 Judge 执行规则文档。

建议：

docs/judge-spec.md
定义：

Tier 0 如何执行
Tier 1 如何执行
Tier 2 如何执行
Tier 3 何时触发
每一层失败是否阻断
Judge 是否有写权限
Judge run 如何追加
final.result 如何计算
can_close_task 何时为 true
recommended_status 如何确定
建议规则：

Tier 0 hard constraint failed -> final.result = FAIL 或 BLOCKED
Tier 1 failed -> can_close_task = false
Tier 2 failed -> can_close_task = false
Tier 3 skipped 不阻断
Tier 3 failed -> can_close_task = false
所有 required tier passed -> can_close_task = true
Judge 不应该直接把 task 改成 COMPLETED。
Judge 只输出：

can_close_task: true/false
recommended_status: ...
最后由主 Agent 或 Runtime Worker 更新状态。

9. Parent-Child Boundary Spec：父子任务通信协议
这是你新架构最重要的补充之一。

建议：

docs/parent-child-boundary.md
规定：

父任务不能默认读取子任务完整 session
父任务只能读取子任务 completion_summary
子任务未完成时，父任务只能读取 status / blocker summary
子任务完成后，父任务读取 picture_result / requirements_result / constraints_result / output_refs / residual_risks
核心规则：

Child Task exposes summary, not history.

示例：

child_task_summary:
  id: oauth_google
  status: COMPLETED
  picture_result: 用户可以通过 Google OAuth 登录
  requirements_result:
    passed: 3
    total: 3
  constraints_result:
    violated: false
  blockers: []
  output_refs:
    commits: ["abc123"]
    files: ["src/auth/google.ts"]
没有这个规范，你的“每个 Agent 只负责一个 Task”会被父任务读取子任务历史破坏掉。

10. Agent-Task Binding Spec：Agent 与 Task 绑定协议
你需要单独定义：

docs/agent-task-binding.md
它说明：

什么是 Logical Agent
什么是 Runtime Worker
一个 Worker 如何 bind 一个 Task
bind 之后哪些命令默认作用于 active_task
是否允许多个 Worker 同时绑定同一 Task
如果并发写入怎么办
MVP 建议非常克制：

一个 Task 同一时刻只允许一个 Runtime Worker 写入。
多个 Worker 可以读取。
并发锁用简单 lock 文件解决。
可以提供：

.mem0ress/tasks/{task_path}/.lock
或者：

lock:
  holder: worker.default
  acquired_at: ...
MVP 也可以先不做复杂并发，但协议里要说明：

v0.1 不保证多 Worker 并发写入安全。

11. Config Spec：配置文件规范
建议提供：

config.yml
以及：

docs/config.md
示例：

protocol: mem0ress
version: "0.1-alpha"

project:
  name: demo-project

status_plane:
  recent_session_limit: 3
  include_parent_summary: true
  include_direct_children: true
  include_full_task_tree: false

judge:
  semantic_check_default: false

runtime:
  default_worker_id: default
  lock_writes: true

paths:
  tasks_root: ".mem0ress/tasks"
配置文件不是必须复杂，但有了它，CLI 行为才可控。

12. Error Codes：错误码规范
如果你想做成开发者协议，错误码很有必要。

建议：

docs/errors.md
示例：

MRS001 Task not found
MRS002 No active task bound
MRS003 Invalid task schema
MRS004 Invalid status transition
MRS005 Missing required file
MRS006 Broken reference
MRS007 Judge failed
MRS008 Constraint violation
MRS009 Completion summary missing
MRS010 Concurrent write lock detected
错误码会让 CLI、Agent Hook、MCP Server 都更好接入。

13. Reference CLI Contract：CLI 行为契约
协议最好给出最小命令契约。

建议：

docs/cli-contract.md
例如：

mem0ress init
mem0ress task create
mem0ress bind <task_path>
mem0ress active
mem0ress plane build
mem0ress session append
mem0ress gotcha add
mem0ress judge run
mem0ress task close
mem0ress child summary
mem0ress validate
尤其需要一个：

mem0ress validate
它根据 schema 检查当前 Task 是否协议合法。

14. Examples：完整示例包
协议必须有 examples。

建议：

examples/
└── oauth_login/
    └── .mem0ress/
        ├── current.yml
        └── tasks/
            └── auth_module/
                └── children/
                    └── oauth_google/
                        ├── task.md
                        ├── session.md
                        ├── gotchas.md
                        ├── judge.md
                        └── completion_summary.md
一个完整例子比一百段解释更有效。

15. Conformance Tests：一致性测试
如果未来要做生态，必须有一致性测试。

建议：

conformance/
├── valid_task/
├── invalid_missing_picture/
├── invalid_broken_requirement_ref/
├── invalid_status_transition/
├── invalid_parent_reads_child_session/
└── valid_completion_summary/
这些测试用于验证第三方实现是否符合协议。

MVP 不一定马上做完，但协议设计上要预留。

16. Versioning / Migration：版本与迁移规则
建议提供：

docs/versioning.md
定义：

protocol version 如何声明
v0.1-alpha 到 v0.1-beta 如何迁移
字段废弃如何处理
旧协议文件如何升级
每个文件 frontmatter 都有：

protocol: mem0ress
version: "0.1-alpha"
这是对的，但还要说明版本兼容策略。

17. 最小完整协议包应该长这样
我建议你的协议仓库结构是：

mem0ress-protocol/
├── README.md
├── SPEC.md
├── schemas/
│   ├── task.schema.json
│   ├── session_turn.schema.json
│   ├── gotcha.schema.json
│   ├── judge_run.schema.json
│   ├── completion_summary.schema.json
│   ├── current.schema.json
│   └── status_plane.schema.json
├── templates/
│   ├── task.md
│   ├── session.md
│   ├── gotchas.md
│   ├── judge.md
│   ├── completion_summary.md
│   └── current.yml
├── docs/
│   ├── directory-layout.md
│   ├── state-machine.md
│   ├── id-conventions.md
│   ├── read-write-rules.md
│   ├── status-plane.md
│   ├── judge-spec.md
│   ├── parent-child-boundary.md
│   ├── agent-task-binding.md
│   ├── config.md
│   ├── errors.md
│   └── cli-contract.md
├── examples/
│   └── oauth_login/
└── conformance/
    ├── valid/
    └── invalid/
18. MVP 阶段最该优先补哪些？
如果你不想一次性做这么多，我建议优先级是：

第一优先级
SPEC.md
schemas/
status-plane.md
state-machine.md
parent-child-boundary.md
这五个最重要。

第二优先级
agent-task-binding.md
read-write-rules.md
id-conventions.md
completion_summary.md 模板
第三优先级
errors.md
cli-contract.md
examples/
conformance/
versioning.md
最终结论
作为协议，文件模板只是数据格式，不是完整协议。

完整协议至少还需要：

总规范
Schema
状态机
ID 规则
目录布局
读写规则
状态平面组装规则
Judge 执行规则
父子任务边界
Agent-Task 绑定规则
配置规范
错误码
CLI 行为契约
示例
一致性测试
版本迁移规则
但 MVP 不要贪多。你现在最应该先补的是：

Schema + State Machine + Status Plane Assembly + Parent-Child Boundary + Agent-Task Binding。

这五个补齐以后，mem0ress 才真正从“几个好模板”变成“一个可以被实现的协议”。
