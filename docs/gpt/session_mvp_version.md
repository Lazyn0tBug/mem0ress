这个 MVP 的核心前提是：

Task 是认知边界。Agent 是任务责任主体。任务树是分解结构，不是上下文窗口。

你原 spec 里已经定义了 Task、PRC、状态平面、数据平面、Session、Gotchas、Judge 等核心元素；MVP 要做的不是重写这些思想，而是把它们压缩成一个可运行的本地 CLI + 文件协议。

mem0ress v0.1 MVP
1. MVP 定位
1.1 一句话定义
mem0ress v0.1 是一个基于本地文件系统的 Task-local Agent 认知状态框架。

它的作用是：

在长路径任务中，让 Agent 每次只绑定一个 Task，并围绕该 Task 的 Picture、Requirements、Constraints、Todos、Session、Gotchas 和 Judge 生成局部状态平面，防止 Agent 在多轮执行中遗忘目标、偏离约束或重复错误路径。

2. MVP 不做什么
v0.1 必须克制。

暂时不做
不做多 Agent 并发调度
不做 Worker Pool
不做 Web UI
不做数据库后端
不做向量检索
不做 RAG
不做长期记忆系统
不做复杂权限系统
不做自动任务拆分优化
不做跨任务冲突协调
不做完整项目管理平台
不做云端服务
v0.1 只证明一件事：

当 Agent 每次只加载当前 Task 的局部认知状态时，长任务执行是否更稳定。

3. 核心设计原则
3.1 Task 是认知边界
每个 Task 是一个独立认知闭包。

一个 Task 包含：

Picture
Requirements
Constraints
Todos
Session
Gotchas
Judge
Completion Summary
Agent 不默认读取整个 Project，也不默认读取整棵任务树。

3.2 Agent 每次只绑定一个 Task
v0.1 采用：

One-Agent-One-Task Cognitive Responsibility Model

意思是：

一个 Agent 在任意时刻只对一个 Task 负责。
但这不是说每个任务都要启动一个独立进程。

需要区分：

Logical Agent：逻辑责任主体，对某个 Task 负责。
Runtime Worker：实际运行模型和工具调用的执行单元。
一个 Runtime Worker 可以在不同时间绑定不同 Task。

3.3 任务树是组织结构，不是上下文窗口
任务树用于表达：

父子关系
分解关系
依赖关系
完成关系
但任务树不意味着：

Agent 每轮都要读取所有任务
Agent 每轮都要理解整个项目
父任务要读取子任务完整历史
子任务要继承父任务全部上下文
父子任务之间只通过摘要通信。

3.4 Todo 与 Subtask 的边界
核心原则：

Todo 推进行动，Subtask 承载目标。

Todo 适合：
修改一个函数
运行一次测试
补充一个字段
更新一个文档段落
检查一个 API 返回
提交一次 commit
Subtask 适合：
有独立 Picture
有独立 Requirements
有独立 Constraints
可以独立验收
可以独立关闭
完成结果会被父任务引用
不要把每个动作都拆成 Task，否则会任务爆炸。

4. 文件系统结构
v0.1 使用纯文本文件。

4.1 根目录结构
.mem0ress/
├── current.yml
├── config.yml
└── tasks/
    └── {task_path}/
        ├── task.yml
        ├── session.md
        ├── gotchas.md
        ├── judge.md
        └── children/
我建议 v0.1 用 task.yml，而不是 task.md。

原因很直接：
MVP 阶段需要机器可读，YAML 比 Markdown 更容易解析、校验和生成状态平面。

但可以保留 Markdown 描述字段。

4.2 示例目录
.mem0ress/
├── current.yml
├── config.yml
└── tasks/
    └── auth_module/
        ├── task.yml
        ├── session.md
        ├── gotchas.md
        ├── judge.md
        └── children/
            └── oauth_google/
                ├── task.yml
                ├── session.md
                ├── gotchas.md
                ├── judge.md
                └── children/
5. 核心文件定义
5.1 current.yml
记录当前 Runtime Worker 绑定的 Task。

active_task: auth_module/children/oauth_google
worker_id: default
updated_at: "2026-05-11T10:00:00+09:00"
plane build、session append、judge run 默认都读取这里的 active_task。

5.2 config.yml
version: "0.1"
project_name: "demo-project"

defaults:
  status_plane:
    include_parent_summary: true
    include_direct_children_summary: true
    include_full_task_tree: false
  judge:
    enable_tier_3_semantic_check: false
  session:
    max_recent_entries_in_plane: 3
5.3 task.yml
这是每个 Task 的唯一任务声明文件。

id: oauth_google
path: auth_module/children/oauth_google
title: "实现 Google OAuth 登录"
status: IN_PROGRESS

picture: >
  用户可以通过 Google OAuth 完成登录，
  整个过程中不需要输入本地密码，
  登录成功后进入系统首页。

requirements:
  - id: req_001
    description: "用户可以点击 Google 登录按钮发起 OAuth 流程"
    status: pending
    evidence: null

  - id: req_002
    description: "Google OAuth callback 可以正确接收并处理授权结果"
    status: pending
    evidence: null

  - id: req_003
    description: "登录成功后用户 session 被正确创建"
    status: pending
    evidence: null

constraints:
  - id: cst_001
    description: "不得要求用户输入本地密码"
    type: hard
    status: clean
    violation: null

  - id: cst_002
    description: "不得在日志中输出 OAuth token"
    type: hard
    status: clean
    violation: null

todos:
  - id: todo_001
    description: "添加 Google OAuth provider 配置"
    status: done

  - id: todo_002
    description: "实现 callback handler"
    status: in_progress

  - id: todo_003
    description: "运行登录集成测试"
    status: pending

parent:
  path: auth_module
  relevance: "当前任务是认证模块的一部分，负责 Google 登录路径"

children: []

created_at: "2026-05-11T09:30:00+09:00"
updated_at: "2026-05-11T10:00:00+09:00"
5.4 session.md
session.md 只追加，不覆盖。

每轮 Agent 执行结束后追加一个 session entry。

## Turn 1

timestamp: 2026-05-11T09:45:00+09:00
worker_id: default
status_before: CREATED
status_after: IN_PROGRESS

### Summary

创建了 Google OAuth provider 配置，并确认需要补充 callback handler。

### Todo Changes

- todo_001: pending -> done
- todo_002: pending -> in_progress

### Requirement Changes

- req_001: pending -> partial

### Constraint Events

- none

### Data Plane

```yaml
repos:
  app:
    commit: "abc123"
Next Suggested Actions
实现 callback handler

检查 token 是否会被日志输出


---

## 5.5 gotchas.md

记录偏差、坑、风险和失败路径。

```markdown
# Gotchas

## G-001

timestamp: 2026-05-11T10:05:00+09:00
status: unresolved
severity: medium
related_task: oauth_google

### Description

本地测试环境的 callback URL 与 Google Cloud Console 配置不一致，导致 OAuth 回调失败。

### Impact

如果不修正，集成测试无法通过。

### Suggested Fix

同步本地环境变量和 Google Cloud Console 中的 callback URL。
5.6 judge.md
记录检验结果。

# Judge Report

## Run 1

timestamp: 2026-05-11T10:20:00+09:00
task: auth_module/children/oauth_google

### Tier 0: Constraints Check

result: passed

- cst_001: passed
- cst_002: passed

### Tier 1: Todo Check

result: failed

- todo_001: done
- todo_002: in_progress
- todo_003: pending

### Tier 2: Requirements Check

result: failed

- req_001: partial
- req_002: pending
- req_003: pending

### Tier 3: Semantic Alignment Check

result: skipped

### Final Result

NOT_READY

### Suggested Next Actions

- 完成 callback handler
- 运行集成测试
5.7 completion_summary.yml
v0.1 可以选择新增这个文件。

我建议新增。

原因是：
父任务读取子任务时，不应该解析子任务完整 judge.md 和 session.md。单独的 completion_summary.yml 会更干净。

task_id: oauth_google
path: auth_module/children/oauth_google
final_status: COMPLETED

picture_result: >
  用户可以通过 Google OAuth 登录，
  不需要输入本地密码，
  登录成功后可以进入系统首页。

requirements_result:
  passed: 3
  total: 3
  items:
    - id: req_001
      status: passed
      evidence: "integration_test_google_login passed"
    - id: req_002
      status: passed
      evidence: "callback handler test passed"
    - id: req_003
      status: passed
      evidence: "session creation verified"

constraints_result:
  violated: false
  violations: []

blockers: []

output_refs:
  commits:
    - "def456"
  files:
    - "src/auth/google.ts"
    - "src/auth/callback.ts"

residual_risks:
  - "生产环境 callback URL 仍需在 Google Cloud Console 中确认"

created_at: "2026-05-11T11:00:00+09:00"
6. 状态定义
v0.1 使用 7 个状态。

你原文里有 5 个状态：CREATED / IN_PROGRESS / VERIFYING / COMPLETED / ABANDONED。
我建议 MVP 加两个非常实用的状态：

BLOCKED
NEEDS_USER
6.1 状态表
CREATED       任务已创建，尚未开始
IN_PROGRESS   任务正在推进
VERIFYING     正在检验，瞬态状态
COMPLETED     任务完成
ABANDONED     任务废弃
BLOCKED       被外部条件阻塞
NEEDS_USER    需要用户补充信息或确认
6.2 状态转换
CREATED -> IN_PROGRESS
CREATED -> ABANDONED

IN_PROGRESS -> VERIFYING
IN_PROGRESS -> BLOCKED
IN_PROGRESS -> NEEDS_USER
IN_PROGRESS -> ABANDONED

VERIFYING -> COMPLETED
VERIFYING -> IN_PROGRESS
VERIFYING -> BLOCKED

BLOCKED -> IN_PROGRESS
BLOCKED -> ABANDONED

NEEDS_USER -> IN_PROGRESS
NEEDS_USER -> ABANDONED

COMPLETED -> END
ABANDONED -> END
7. CLI 命令设计
7.1 最小命令清单
mem0ress init
mem0ress task create
mem0ress task list
mem0ress task show <task_path>
mem0ress task update <task_path>
mem0ress task close <task_path>

mem0ress bind <task_path>
mem0ress active

mem0ress plane build
mem0ress session append
mem0ress gotcha add
mem0ress judge run

mem0ress child summary <task_path>
7.2 init
mem0ress init
创建：

.mem0ress/
├── current.yml
├── config.yml
└── tasks/
7.3 task create
mem0ress task create oauth_google \
  --parent auth_module \
  --title "实现 Google OAuth 登录"
生成：

.mem0ress/tasks/auth_module/children/oauth_google/
├── task.yml
├── session.md
├── gotchas.md
├── judge.md
└── children/
7.4 bind
mem0ress bind auth_module/children/oauth_google
写入：

active_task: auth_module/children/oauth_google
worker_id: default
updated_at: "2026-05-11T10:00:00+09:00"
这是 MVP 最重要的命令之一。

它表达：

当前 Runtime Worker 只对这个 Task 负责。

7.5 active
mem0ress active
输出：

Active task: auth_module/children/oauth_google
Status: IN_PROGRESS
Title: 实现 Google OAuth 登录
7.6 plane build
mem0ress plane build
默认基于 current.yml 中的 active task 生成状态平面。

也支持：

mem0ress plane build --task auth_module/children/oauth_google
7.7 session append
mem0ress session append
交互式追加，或者支持文件输入：

mem0ress session append --from turn.yml
7.8 judge run
mem0ress judge run
执行当前 Task 的四层检验：

Tier 0: Constraints
Tier 1: Todos
Tier 2: Requirements
Tier 3: Semantic Alignment 可选
v0.1 里 Tier 3 默认关闭。

7.9 task close
mem0ress task close auth_module/children/oauth_google --status COMPLETED
关闭任务并生成：

completion_summary.yml
8. 状态平面格式
8.1 status_plane.yml
plane build 输出一个结构化状态平面。

status_plane:
  generated_at: "2026-05-11T10:30:00+09:00"
  scope: task-local

  active_task:
    id: oauth_google
    path: auth_module/children/oauth_google
    title: "实现 Google OAuth 登录"
    status: IN_PROGRESS

  picture:
    summary: >
      用户可以通过 Google OAuth 登录，
      不需要输入本地密码，
      登录成功后进入系统首页。

  progress:
    todos:
      completed: 1
      total: 3
      open:
        - id: todo_002
          description: "实现 callback handler"
          status: in_progress
        - id: todo_003
          description: "运行登录集成测试"
          status: pending

    requirements:
      passed: 0
      total: 3
      pending:
        - req_001
        - req_002
        - req_003

    constraints:
      violated: false
      open_violations: []

  local_context:
    recent_session:
      latest_turn: 1
      summary: "创建了 Google OAuth provider 配置"
    unresolved_gotchas:
      - id: G-001
        severity: medium
        description: "callback URL 与 Google Cloud Console 配置不一致"

  parent:
    path: auth_module
    summary: "当前任务属于认证模块，负责 Google 登录路径"

  children:
    open: []
    completed: []

  data_plane:
    repos:
      app:
        commit: "abc123"

  next_suggested_actions:
    - "完成 callback handler"
    - "检查 token 是否会被日志输出"
    - "运行 Google 登录集成测试"
8.2 状态平面默认读取范围
默认读取：

当前 Task 的 task.yml
当前 Task 的 session.md 最近 N 条
当前 Task 的 gotchas.md 未解决项
当前 Task 的 judge.md 最近一次结果
当前 Task 的 completion_summary.yml，如存在
直接父 Task 的摘要
直接子 Task 的 completion_summary 或状态摘要
默认不读取：

兄弟任务完整内容
孙任务完整内容
父任务完整 session
子任务完整 session
整棵任务树
历史所有 turn
这就是 Task-local。

9. Judge 逻辑
9.1 Tier 0：Constraints 检查
检查所有 constraints。

constraints:
  - id: cst_001
    type: hard
    status: clean
如果发现 violation：

status: violated
violation:
  turn: 3
  description: "日志中输出了 OAuth token"
Hard constraint 违反时，Judge 结果必须失败。

9.2 Tier 1：Todo 检查
所有 Todo 必须是：

done
否则失败。

9.3 Tier 2：Requirements 检查
所有 Requirement 必须是：

passed
否则失败。

9.4 Tier 3：语义对齐检查
v0.1 默认不自动执行。

只在以下情况开启：

mem0ress judge run --semantic
或者 config 中：

judge:
  enable_tier_3_semantic_check: true
Tier 3 可以只是生成提示，不一定调用模型。

例如输出：

请检查当前产出是否真正达成 Picture：
“用户可以通过 Google OAuth 登录，不需要输入本地密码。”
MVP 阶段不要把 Tier 3 做重。

10. Parent / Child 通信协议
父任务不读取子任务完整历史。

父任务只读取：

子任务 status
子任务 completion_summary
子任务 blockers
子任务 output_refs
子任务 residual_risks
10.1 child summary 输出
mem0ress child summary auth_module/children/oauth_google
输出：

child_task_summary:
  id: oauth_google
  path: auth_module/children/oauth_google
  status: COMPLETED
  picture_result: >
    用户可以通过 Google OAuth 登录，
    不需要输入本地密码。
  requirements_result:
    passed: 3
    total: 3
  constraints_result:
    violated: false
  blockers: []
  output_refs:
    commits:
      - def456
    files:
      - src/auth/google.ts
      - src/auth/callback.ts
  residual_risks:
    - "生产环境 callback URL 仍需确认"
11. MVP 执行流程
11.1 初始化
mem0ress init
11.2 创建父任务
mem0ress task create auth_module \
  --title "实现认证模块"
生成父任务。

11.3 创建子任务
mem0ress task create oauth_google \
  --parent auth_module \
  --title "实现 Google OAuth 登录"
11.4 绑定子任务
mem0ress bind auth_module/children/oauth_google
11.5 构建状态平面
mem0ress plane build
Agent 读取输出，开始工作。

11.6 执行一轮后追加 Session
mem0ress session append --from turn.yml
11.7 运行 Judge
mem0ress judge run
11.8 继续执行直到通过
mem0ress plane build
mem0ress session append
mem0ress judge run
11.9 关闭任务
mem0ress task close auth_module/children/oauth_google --status COMPLETED
生成：

completion_summary.yml
11.10 父任务读取子任务摘要
mem0ress bind auth_module
mem0ress child summary auth_module/children/oauth_google
mem0ress plane build
父任务只看到子任务结果，不继承完整历史。

12. 开发实现建议
12.1 技术栈
v0.1 建议用 Python 或 Node.js。

我个人建议 Python。

原因：

YAML/Markdown 文件处理简单
CLI 开发快
适合原型验证
方便未来接入脚本、Git、测试命令
推荐依赖：

typer 或 click
pyyaml
rich
pydantic
12.2 项目结构
mem0ress/
├── mem0ress/
│   ├── __init__.py
│   ├── cli.py
│   ├── paths.py
│   ├── task.py
│   ├── plane.py
│   ├── session.py
│   ├── judge.py
│   ├── gotcha.py
│   └── summary.py
├── tests/
├── pyproject.toml
└── README.md
12.3 核心模块职责
paths.py
  负责 .mem0ress 路径解析

task.py
  创建、读取、更新 task.yml

plane.py
  构建 Task-local status plane

session.py
  追加 session.md

judge.py
  执行 Tier 0/1/2 检查

gotcha.py
  追加和读取 gotchas.md

summary.py
  生成和读取 completion_summary.yml

cli.py
  暴露命令行接口
13. 最小数据模型
13.1 TaskModel
class TaskModel:
    id: str
    path: str
    title: str
    status: str
    picture: str
    requirements: list[Requirement]
    constraints: list[Constraint]
    todos: list[Todo]
    parent: ParentRef | None
    children: list[str]
    created_at: str
    updated_at: str
13.2 Requirement
class Requirement:
    id: str
    description: str
    status: Literal["pending", "partial", "passed", "failed"]
    evidence: str | None
13.3 Constraint
class Constraint:
    id: str
    description: str
    type: Literal["hard", "soft"]
    status: Literal["clean", "violated", "warning"]
    violation: str | None
13.4 Todo
class Todo:
    id: str
    description: str
    status: Literal["pending", "in_progress", "done", "blocked"]
14. v0.1 验收标准
MVP 完成不看功能多，而看闭环是否成立。

14.1 必须完成
可以 init 项目
可以 create task
可以 create child task
可以 bind active task
可以 build task-local status plane
可以 append session
可以 add gotcha
可以 run judge Tier 0/1/2
可以 close task
可以生成 completion_summary
父任务可以读取子任务 summary
14.2 不合格的 MVP
如果出现以下情况，说明 MVP 跑偏：

plane build 默认扫描整棵任务树
父任务读取子任务完整 session
每个 Task 都必须启动常驻 Agent
Judge 强依赖 LLM
Session 变成完整对话记录
Gotchas 被当成长期记忆库
任务拆分到每个机械动作
CLI 必须依赖云服务才能运行
15. README 首页应该怎么写
建议 README 第一屏这样写：

# mem0ress

A lightweight task-local cognitive state framework for long-running AI agents.

mem0ress helps an AI agent stay aligned with a single active task by maintaining:

- Picture: what success looks like
- Requirements: what must be verified
- Constraints: what must not be violated
- Todos: what remains to be done
- Session: what changed in each turn
- Gotchas: what went wrong or may go wrong
- Judge: whether the task is ready to close

Core principle:

Task is the cognitive boundary.
Agent is the task responsibility holder.
Task tree is the decomposition structure, not the context window.
中文版本：

# mem0ress

mem0ress 是一个面向长路径 AI Agent 的轻量级 Task-local 认知状态框架。

它帮助 Agent 在每一轮执行中始终围绕一个当前 Task 维持目标、进度和约束对齐。

核心原则：

Task 是认知边界。
Agent 是任务责任主体。
任务树是分解结构，不是上下文窗口。
16. v0.1 最小 Demo
建议你用这个 Demo 验证：

场景
让 Agent 实现一个 Google OAuth 登录功能。
不使用 mem0ress 时观察
Agent 是否忘记“不允许输入本地密码”
是否重复尝试失败 callback 配置
是否完成代码但没有跑测试
是否完成 Todo 但没有真正达成 Picture
使用 mem0ress 后观察
每轮是否知道当前 Picture
是否知道哪些 Requirement 没过
是否知道哪些 Constraint 不能碰
是否知道当前被哪个 Gotcha 阻塞
是否能在恢复任务后继续推进
父任务是否只读取子任务 completion_summary
17. 推荐版本路线
v0.1
本地文件
CLI
Task-local plane
Session append
Judge Tier 0/1/2
Completion Summary
v0.2
Git data plane 自动采集
更好的 schema validation
Task activation
父子任务聚合
更多状态转换
v0.3
Agent hook
Claude Code / Cursor / Codex CLI 接入
自动 session extraction
自动 judge suggestion
v0.4
Worker pool
多任务调度
任务优先级
阻塞任务 parking
v1.0
稳定协议
插件生态
MCP server
多 Agent runtime
可观测性 dashboard
18. 最终 MVP 总结
mem0ress v0.1 的完整形态应该是：

一个本地 CLI
一套文件协议
一个 current active task 绑定机制
一个 Task-local status plane 生成器
一个 Session 追加机制
一个 Gotcha 记录机制
一个 Judge 检验机制
一个 Completion Summary 边界输出机制
它的核心不是“记住所有历史”，而是：

让当前 Agent 在当前 Task 上始终知道：目标是什么、做到哪了、还差什么、不能碰什么、是否可以关闭。

最终你要证明的不是“认知理论正确”，而是这个具体命题：

Task-local 状态平面可以显著降低 Agent 在长路径任务中的意图迷失和上下文污染。
