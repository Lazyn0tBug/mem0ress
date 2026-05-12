从协议设计的角度，现在的四个文件只覆盖了格式层（数据长什么样），还缺两个层：

缺什么
第一层缺失：行为协议（最关键）
四个模板定义了"数据格式"，但没有定义"谁在什么时机做什么、按什么顺序、谁能写谁只读"。

这是协议里最容易出错的地方，也是目前完全空白的部分。需要一份 PROTOCOL.md，明确三个参与方的契约：

主 Agent 的契约：

必须在每个轮次结束后写 session.md（不能跳过）
必须在触发 Judge 前将状态切换到 VERIFYING
读取 judge.md 后自主决策，不得等待外部指令
是唯一可以调用 complete_task / abandon_task 的参与方
Judge Agent 的契约：

只读 task.md / session.md / gotchas.md
只写 judge.md
不修改任何其他文件
Tier 失败必须立即停止，不继续执行后续 Tier
宿主框架的契约：

必须保证 Judge Agent 和主 Agent 的上下文隔离
必须在主 Agent 调用 trigger_judge 后，将 task_id 注入 Judge Agent
负责 VERIFYING 的超时保护（Judge 卡死时如何恢复）
第二层缺失：Schema（字段定义）
你把 frontmatter 里的字段说明删掉是对的，但这些定义不是消失了，是要搬到一个独立的 SCHEMA.md 里。

当前这些东西没有一个权威的定义：

status 的合法值是什么（VERIFYING 可以持久化吗？）
Turn 编号格式的正则是什么（^\d+\.\d+$？）
task_id 的命名规范是什么（允许哪些字符？）
R-N / T-N / C-N / G-N 的编号是在任务内唯一，还是全局唯一？
没有 SCHEMA.md，两个独立实现的框架无法保证互操作。

第三层缺失：data_plane.md
session.md 里有 Data Plane 字段，judge.md 的 Tier 3 prompt 里引用了 Data Plane，但这个文件的模板从来没提供过。它被引用但未定义，是一个悬空引用。

这个文件相对简单——就是 commit ID + 涉及文件列表——但它需要一个独立模板，否则"数据平面"只是一个概念，不是协议。

第四层缺失（实用性）：一个完整的填写示例
模板告诉 Agent"这里填什么"，但 Agent（尤其是新接入的宿主框架）需要看到一个真实填写的完整示例，才能知道协议在实际运行时长什么样。

这不是文档装饰，是协议可执行性的一部分。没有示例的协议，每个实现者都会在细节上做出不同的解读。

总结


文件	性质	优先级
PROTOCOL.md	行为契约（谁做什么、什么时机、权限边界）	最高，现在完全缺失
SCHEMA.md	字段定义（类型、合法值、命名规范）	高，frontmatter 删掉后定义无处安放
data_plane.md	数据模板（被引用但未提供）	高，悬空引用
EXAMPLE.md	完整填写示例	中，影响协议可操作性
需要我来写这几个文件吗？


PROTOCOL.md 是最需要思考的，其他三个相对直接。我会按这个顺序：SCHEMA → data_plane → PROTOCOL → EXAMPLE，因为 PROTOCOL 引用前两个的定义，EXAMPLE 依赖全部。最后是 EXAMPLE.md，这个要真实填写，不留占位符：四个文件的设计思路说明：

SCHEMA.md — 把原来散落在各文件 frontmatter 里的字段定义集中到一处，形成单一权威来源。重点定义了两个之前模糊的地方：Turn 编号的完整规则（与 Todo 解耦后怎么递增）；以及 VERIFYING 的精确约束（它是瞬态、不记录在 session 的 status 字段、宿主框架负责超时保护）。

data_plane.md — 解决了悬空引用问题。同时澄清了一个容易混淆的点：data_plane 不是一个独立文件，而是 session.md 每个 Turn 块里的嵌入字段，本文件只是格式规范。还定义了 Active Refs 的边界——"读取但未修改"的文件不计入，避免 Active Refs 变成无意义的全量文件列表。

PROTOCOL.md — 核心是三件事：第一，把读写权限写成一张表，任何参与方对任何文件能做什么一眼可查；第二，把执行循环画成有顺序编号的步骤图，明确"谁先谁后"不能含糊；第三，把不支持的场景明确列出（并发子任务、多 Agent 并行执行等），这是协议设计里最容易被忽略但最重要的部分——知道边界在哪，比知道能做什么更关键。

EXAMPLE.md — 故意选了一个有失败-修正-重试的完整路径，而不是一帆风顺的例子。因为协议最容易在边缘情况下被误用，示例应该展示 FAILED 的 judge.md 长什么样、Gotcha 是怎么触发的、Turn 编号在修正后如何继续。最后附的时序图是这个文件的核心价值——把散落在四个文件里的事件还原成一条时间线。
