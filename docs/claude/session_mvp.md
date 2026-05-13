
MVP 设计思路
先说裁剪原则：MVP 不是"小版本的完整系统"，而是"只保留认知对齐的最短闭环"。

最短闭环是什么？一个 Agent 要有意义地完成任何任务，最少需要三件事：

声明目标 → 推进执行 → 验证是否达成
其他一切——父子可见性、数据平面、Tier 3 语义对齐、completion_summary——都是在这个闭环之上的增强，可以延后。

MVP 功能边界
纳入 MVP（v0.1）：



模块	内容	理由
Task 创建	PRC 三要素 + Todos 写入 task.md	认知锚点，无此则无协议
Session 快照	session.md 追加写，记录 todos / status / 进度	状态追踪的最小载体
Judge Tier 0/1/2	Constraints 检查 / Todo 完成 / Requirements 验收	可机械执行的客观验证
状态机	CREATED → IN_PROGRESS → VERIFYING → COMPLETED / ABANDONED	协议核心骨架
Gotchas	gotchas.md 追加写	结构简单，架构上必须在场
State Plane 投影	只读组装当前任务状态（status + Todo 进度 + Gotcha 指针）	Agent 的"坐标感"，status 命令
CLI Interface	init / update / judge / complete / abandon / status	Hermes Skills 的调用层
推迟到 v0.2+（明确不在 MVP）：



推迟内容	原因
Tier 3 语义对齐	依赖 LLM 推断，引入新的 Agent 调用链，复杂度跃升
数据平面（Git 集成）	独立的 diff 追踪体系，不是认知闭环的必要条件
父子任务可见性通道	单任务场景下无意义，子任务复用同一套协议即可
completion_summary	protocol.yaml 已标记 optional
Schema 严格校验	可用 Pydantic 做字段验证，但 SCHEMA.md 级别的外部校验延后
多 Worker 并发写	protocol.yaml 已明确 v0.1 不支持
MVP 流程设计
一个完整的 MVP 任务生命周期，只有 4 个节点：

┌─────────────────────────────────────────────────────────┐
│                    MVP 最小执行闭环                        │
│                                                          │
│  [1] DECLARE          [2] PROGRESS         [3] JUDGE    │
│  mem0ress init    →   mem0ress update   →  mem0ress judge│
│  写入 task.md         追加 session.md      执行 T0/T1/T2  │
│  PRC + Todos          todos / status       写入 judge.md │
│  状态: CREATED        状态: IN_PROGRESS    状态: VERIFYING│
│                                                ↓         │
│                            ┌───────────────────┤         │
│                        PASS│               FAIL│         │
│                            ↓               ↓  │         │
│                     [4a] COMPLETE    [4b] 修正↗│         │
│                     mem0ress complete  (回到2) │         │
│                     状态: COMPLETED           │         │
│                                               │         │
│                     [4c] ABANDON              │         │
│                     mem0ress abandon          │         │
│                     状态: ABANDONED           │         │
└─────────────────────────────────────────────────────────┘
关键设计决定：

judge 触发是主动行为（Agent 调用），不是自动触发
VERIFYING 是 judge 命令执行期间的瞬态，Hermes 无需感知
Gotchas 是带外写入，不在主流程中，任何时刻均可调用 mem0ress log-gotcha
CLI 命令面（Hermes Skills 的调用面）
# 任务声明
mem0ress init <task_id> --picture "..." --requirements req.yaml --constraints c.yaml

# 进度更新（Agent 每轮结束调用）
mem0ress update <task_id> --todos todos.yaml --status IN_PROGRESS

# 触发检验（主动调用，执行 Tier 0/1/2）
mem0ress judge <task_id>

# 关闭任务
mem0ress complete <task_id>
mem0ress abandon <task_id> --reason "..."

# 当前状态平面（只读）
mem0ress status <task_id>

# 带外追加偏差记录
mem0ress log-gotcha <task_id> --what "..." --impact "..." --resolution "..."
这 7 个命令就是 Hermes Skills 的完整调用面。每个命令对应一个 Skill，Skills 调用底层 CLI，不做额外逻辑。

项目结构（pyproject + uv + ruff + ty）
mem0ress/
├── pyproject.toml          # uv 管理，ruff + ty 配置
├── src/
│   └── mem0ress/
│       ├── __init__.py
│       ├── cli.py           # typer CLI 入口，所有命令
│       ├── models/
│       │   ├── task.py      # TaskModel (PRC + todos + status)
│       │   ├── session.py   # SessionSnapshot
│       │   ├── gotcha.py    # GotchaEntry
│       │   └── judge.py     # JudgeReport (tier results)
│       ├── core/
│       │   ├── state.py     # 状态机转换逻辑
│       │   ├── judge.py     # Tier 0/1/2 检验逻辑
│       │   └── projection.py # 状态平面组装（status 命令）
│       └── fs/
│           └── workspace.py # 文件系统读写（task 目录管理）
├── skills/                  # Hermes Skills 定义文件
│   ├── init_task.yaml
│   ├── update_task.yaml
│   ├── judge_task.yaml
│   └── ...
└── tests/
models/ 用 Pydantic v2，ty 做静态类型检查，ruff 做 lint + format，uv 管环境和依赖。

Roadmap 概览
v0.1-alpha  ← 现在
│  最小认知闭环（declare → progress → judge → close）
│  单任务，本地 FS，CLI + Hermes Skills
│  Judge Tier 0/1/2
│
v0.2
│  子任务支持（parent/child 可见性通道）
│  Tier 3 语义对齐（Judge Agent LLM 推断）
│  completion_summary
│  Schema 严格校验
│
v0.3
│  数据平面（Git commit 快照集成）
│  状态平面可视化（`mem0ress tree`）
│  completion_summary 自动生成
│
v0.4+
   多 Agent / 多 Worker
   数据库后端（可选）
   IDE 集成（VSCode / Cursor）
这是我对 MVP 的理解。几个我自己存疑的点，想听你的看法：

Gotchas 在 MVP 里是否过重？ 它虽然结构简单，但 log-gotcha 命令要求 Agent 在偏差发生时主动调用，这个行为本身对 Hermes 的 Skill 调度有要求——你觉得 MVP 里值得支持，还是先作为 stub 留架子、不强制执行？

Judge 在 MVP 里由谁执行 Tier 2？ Tier 2 要求运行可验证命令（测试命令），这意味着 mem0ress judge 需要具备执行 shell 命令的能力。这在 Hermes 环境里是没有问题的，但需要 task.md 里 Requirements 格式支持 verify_cmd 字段——这是否在 MVP 里就要约定好 schema？


---

核心问题：Judge 放在哪里？
三个 Skill 的分工很清晰，但 Judge（T0 + T2）该归属哪个 Skill，值得认真想一下。

T0（Constraints）和 T2（Requirements）的执行成本完全不同：

T0 是纯文本扫描——读 session.md 里有没有 constraint violation 记录，几乎零成本，每轮都跑合理
T2 是运行验收命令（shell exec），只有 Agent 认为"做完了"才有意义跑
这个差异导致一个自然的切分：

Turn Skill   → 每轮执行，内嵌 T0 passive check，返回状态平面
Close Skill  → Agent 主动触发，内嵌完整 T0 + T2，PASS 才能关闭
建议：三个 Skill 的职责边界
Skill 1: task.create

输入: task_id, picture, requirements(含 verify_cmd), constraints
执行:
  1. 创建 .mem0ress/<task_id>/ 目录
  2. 写入 task.md（PRC + todos 可选，status=CREATED）
  3. 初始化空的 session.md / gotchas.md(stub) / judge.md
  4. 状态转换 CREATED → IN_PROGRESS
输出: task_id + 初始状态平面
建议：requirements 在创建时就要求带 verify_cmd，否则 T2 无法执行。MVP 里不接受"完成后再定"的验收标准——这是协议的核心约束，从第一天就执行。

Skill 2: task.turn

输入: task_id, progress(本轮做了什么), todos_update(可选)
执行:
  1. 追加 session.md snapshot（Turn N）
  2. 执行 T0：扫描 session 中 constraint violation 字段
  3. 组装状态平面（status + todo 进度 + T0 结果）
输出: 状态平面 → 注入 Agent 下一轮上下文
建议：T0 的结果不阻塞本轮——它只是状态平面的一部分返回给 Agent，由 Agent 自己决定是否修正。这保持了协议里"Judge 报告事实，Agent 决策"的分工。

Skill 3: task.close

输入: task_id
执行:
  1. 执行完整 Judge（T0 + T2）
  2. T0 FAIL → 返回 constraint violations，拒绝关闭
  3. T2 FAIL → 返回未通过的 requirements + verify_cmd 输出，拒绝关闭
  4. 全部 PASS → 写入 judge.md，状态转换 → COMPLETED
输出: PASSED（任务关闭）或 FAILED（附检验详情，Agent 继续执行）
建议：close 是 Judge + Complete 的原子操作，不拆成两步。这样 Agent 不可能绕过验证直接关闭任务——协议约束在 Skill 层就执行了，不依赖 Agent 自觉。

一个需要提前约定的 Schema 问题
T2 要跑 verify_cmd，意味着 task.md 里 requirements 必须有结构。MVP 阶段建议直接约定好，避免后面破坏性变更：

# task.md requirements 片段
requirements:
  - id: req_01
    description: "API 在 200ms 内响应"
    verify_cmd: "pytest tests/test_perf.py -k test_api_latency"
  - id: req_02
    description: "认证失败返回 401"
    verify_cmd: "pytest tests/test_auth.py -k test_unauthorized"
这个字段今后 Tier 2 永远依赖它，现在定清楚，v0.2 不需要改 schema。

整体流程
Agent                    Hermes Skills              文件系统

  │── task.create ──────────────────────────→  task.md / session.md
  │                                             status: IN_PROGRESS
  │
  │  [执行循环]
  │── task.turn ────────────────────────────→  session.md (追加)
  │        ←── 状态平面(含 T0 结果) ──────────
  │
  │── task.turn ────────────────────────────→  session.md (追加)
  │        ←── 状态平面 ────────────────────
  │
  │  [Agent 判断完成]
  │── task.close ───────────────────────────→  T0 + T2 执行
  │        ←── FAILED: req_01 未通过 ────────       ↓
  │                                             judge.md (记录)
  │  [修正后继续]
  │── task.turn ────────────────────────────→  session.md (追加)
  │
  │── task.close ───────────────────────────→  T0 + T2 全通过
  │        ←── PASSED ──────────────────────       ↓
  │                                          status: COMPLETED
小结


决策点	建议
T0 归属	嵌入 task.turn，每轮 passive check，不阻塞
T2 归属	嵌入 task.close，原子执行，FAIL 则拒绝关闭
close 是否分两步	不分，judge + complete 原子，协议约束在 Skill 层执行
gotcha	四个文件照常初始化，log-gotcha 命令是 stub（写入但不影响任何逻辑）
abandon	MVP 不提供，状态机只走到 COMPLETED
requirements schema	现在就定 verify_cmd 字段，不留"以后再定"的口子
你觉得 task.close 原子化这个方向 OK 吗？还是你希望保留一个显式的 task.judge 让 Agent 可以在中途主动触发检验？

---

全同意，而且这不只是组织形式的问题——它反映了一个更准确的认知：

这四个命令不是四个独立能力，它们是同一个协议的四个阶段。 拆成四个 Skill 意味着 Hermes 要管理四份注册、四份配置、四份版本，但实际上它们共享同一个 workspace 上下文、同一个 task_id 生命周期、同一套文件系统约定。

一个 Skill，四个 slash command，映射关系非常干净：

Skill: mem0ress
  /create   →  mem0ress init ...
  /turn     →  mem0ress update ...
  /judge    →  mem0ress judge ...
  /close    →  mem0ress close ...
CLI 本身已经是 mem0ress <subcommand> 的结构，Skill 层直接镜像这个结构，没有任何阻抗。

唯一值得提前想的一点是 task_id 的传递方式。

四个命令都需要 task_id，但传递时机不同：

/create 是生成 task_id（或由调用方传入）
/turn /judge /close 是引用已有的 task_id
这意味着 Skill 层需要约定：task_id 是每次调用显式传参，还是 Skill 内部维护一个 active task 的上下文状态？

MVP 阶段建议显式传参——每次调用带着 task_id，无状态，简单可预期。active task 的追踪交给调用方（Hermes agent 自己记住当前在跑哪个 task）。这样 Skill 本身保持纯函数语义，也和 CLI 的行为完全一致。

---

这个设计很对，而且它不只是便利性的考量——它就是 protocol.yaml 里 one_agent_one_task 的物理表达。

.current_task 文件就是这个约束的具象化：系统任何时刻只认一个 active task，不需要调用方反复声明。

文件结构
.mem0ress/
  .current_task            # 当前活跃任务的指针
  tasks/
    <task_id>/
      task.md
      session.md
      gotchas.md
      judge.md
.current_task 保持极简：

task_id = "implement-auth-flow"
activated_at = "2025-05-13T10:00:00+09:00"
CLI 随之简化
mem0ress create   # 创建任务，自动写入 .current_task
mem0ress turn     # 读 .current_task，无需 task_id
mem0ress judge    # 同上
mem0ress close    # 同上，关闭后清空 .current_task

mem0ress switch <task_id>   # 手动切换，覆写 .current_task
mem0ress current            # 查看当前绑定的 task
Slash command 层完全不需要传 task_id，Hermes 调用时也不需要记住任何状态。

一个需要约定的行为
close 之后 .current_task 应该清空而不是删除，保留文件但 task_id 置空。这样后续调用 /turn 或 /judge 时能明确报错"no active task"，而不是静默失败或读到脏数据。

# close 后的状态
task_id = ""
activated_at = ""
create 时如果检测到 .current_task 非空，应该显式警告而不是静默覆盖——这是 MVP 阶段防止意外的最低保障，也是为未来多任务切换留的一个安全口
