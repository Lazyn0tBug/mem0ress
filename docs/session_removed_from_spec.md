# 从 spec.md 删除的章节

本文档记录因不属于接口语义规范（属于实现层/操作层）而从 spec.md 中删除的内容。这些章节的核心理念可能对 MVP 设计有参考价值。

---

## 删除内容一：§3.4 Skill 作为认知操作符

> **删除理由**：这段内容是"告诉实现者 Skill 应如何设计"，属于实现层指引，不是 mem0ress 协议的语义接口定义。Skill 的操作接口应属于 Manifest 层或实现文档，不属于 Spec 层。

### 原文

Skill 不是命令封装器。

Skill 在 Agent 与确定性运行时之间充当认知操作符。

Skill 的存在目的是：协商认知、恢复任务上下文、评估对齐状态、评价进度、消解歧义、决定下一步行动。

Skill 应当暴露认知导向的操作，不应直接暴露运行时命令。

Skill 的具体操作接口定义见 §5。

---

## 删除内容二：§3.5 协议运行时模型

> **删除理由**：CAP Specification 明确声明"不定义运行时架构、编排系统、执行框架"。运行时模型属于实现层，不属于语义规范层。

### 原文

运行时是确定性协议执行器。

运行时负责：持久化认知产物、组装状态平面、校验协议结构、执行客观验证、暴露结构化证据。

运行时不是：规划器、工作流引擎、编排框架、符号推理引擎、集中式认知控制器。

---

## 删除内容三：§3.6 Agent 执行循环

> **删除理由**：同 §3.5，Agent 执行循环的具体序列属于实现层操作定义，不是协议语义接口。

### 原文

mem0ress 的认知循环中，运行时只参与确定性阶段，语义推进的所有权永远属于 Agent。

完整轮次序列定义见 §6.1.1，参与方职责边界定义见 §6.1.2。

---

## 删除内容四：§4 设计决策（全部5个子节）

> **删除理由**：设计决策的推导过程是"为什么会这样设计"，不是"协议实际定义了什么"。Spec 层只定义语义接口，不记录设计推导。设计推导过程对理解协议有帮助，但不是协议的组成部分。

### 原文

#### §4.1 选择任务作为认知单元

洞察一否定了"上下文被动维护"的架构，洞察二确立了任务作为信息完整单元的地位。这两者共同推导出一个结论：认知系统应以任务（Task）为唯一单元。每个任务天然封装目标、可验证条件和执行边界，三者一体构成可判断的认知单元——孤立的知识点或对话片段没有这种结构，无法成为可靠的认知锚点。

每个任务封装目标、可验证条件、不可逾越边界和执行进度——四者的组合使得任务在任意时刻都有一个可判断的状态。同构性是关键的设计选择：如果认知单元种类繁多（里程碑、史诗、故事点、子任务），系统需要为每种类型设计不同的处理逻辑，认知负载倍增。统一的任务模型在任何粒度下都适用，系统复杂性维持在常数级别。

以目录树表达任务层级。父任务目录下嵌套子任务目录，目录深度即依赖关系——`ls` 就能看到边界，不需要额外的状态聚合。

所有认知单元同类同构：父任务是 Task，子任务也是 Task，递归下去每一层都是 Task。没有里程碑、没有史诗、没有故事点，只有 Task。同构性使认知网关只需要一套解析逻辑。认知唯一：对于一个任务，没有两份认知同时存在的状态，不讨论新旧与变更，只维护一份认知。

#### §4.2 选择单任务 Agent 责任模型

mem0ress 采用单任务 Agent 责任模型（One-Agent-One-Task Cognitive Responsibility Model）。

在 mem0ress 中，Agent 在任意时刻只绑定一个活跃 Task。该 Agent 的认知平面只围绕当前 Task 的本地文档组装，包括 `task.md`、`session.md`、`gotchas.md` 和 `judge.md`。任务树表达的是任务之间的分解关系、依赖关系和完成关系，而不是单个 Agent 的全局上下文窗口。

这意味着，一个 Agent 不需要也不应该在每一轮执行中读取整棵任务树。父任务、子任务、兄弟任务都不是默认上下文。它们只有在与当前 Task 的判断有关时，才以摘要形式进入当前 Task 的状态平面。

因此，mem0ress 的认知边界不是 Project，也不是完整任务树，而是当前 Task。

Task 是 Agent 的最小认知闭包。每个 Task 都拥有独立的 Picture、Requirements、Constraints、Todos、Session、Gotchas 和 Judge 文件。Agent 对该 Task 的目标达成负责，而不是对整棵任务树负责。

任务树提供组织结构，Task 提供认知边界。

**Logical Agent 与 Runtime Worker 的区分：** mem0ress 中的 Agent 概念有两个层面。Logical Agent 是认知责任的归属者——创建 Task 的 Agent 对该 Task 的 Picture 达成负有认知责任，这个关系在 Task 创建时锁定，不随运行时 worker 的切换而改变。Runtime Worker 是实际执行任务的运行时实体——它读取当前 Task 的本地文档，执行动作，更新 Todo，在轮次结束时触发状态快照。mem0ress 只规定认知平面围绕哪个 Task 组装（Logical Agent 的绑定关系），不规定执行由哪个 Runtime Worker 承担。同一 Logical Agent 在不同轮次可能由不同的 Runtime Worker 承接，但只要认知边界锁定在 Task 层面，状态平面的组装就不受影响。

**Task 是认知边界，不是资源单位：** mem0ress 中的 Task 边界是认知边界，对应文件系统的目录结构。任务树表达的是任务之间的组织结构和依赖关系，不是单个 Agent 的全局上下文窗口。Agent 对当前 Task 的 Picture 达成负责，不需要也不应该主动加载整棵任务树——除非当前 Task 的 Picture 判断确实需要父任务或子任务的信息，此时这些信息以摘要形式进入状态平面。认知边界与资源分配是两个独立维度，mem0ress 只管前者。

#### §4.3 选择PRC作为任务信息模型

任务作为信息的完整单元，需要结构化的要素来承载其边界——模型既在创建时锚定完成标准，也在检验时提供判断依据。因此为每个任务定义三个要素：`Picture`（语义成功状态）、`Requirements`（可验证条件）、`Constraints`（不可逾越底线）。

定义顺序：先定 `Picture`，再从 `Picture` 推导出 `Requirements` 和 `Constraints`。三者都定义完之后检查有没有矛盾——若存在矛盾，在多轮沟通中引导协作者修正，直到矛盾消除，模型写入 task.md。

#### §4.4 选择双重平面来呈现认知

任务需要同时掌握两个不同维度的事实：做到了什么（数据层面）和推进到哪里（执行层面）。两个问题认知性质不同，必须分开处理。详见 §6.2。

三个核心动作按固定顺序执行：认知构建 → 任务检验 → 状态更新。认知构建先于任务检验，任务检验先于状态更新。

#### §4.5 选择状态变更驱动认知构建

每轮次结束时，Agent 感知本轮任务内容的状态变更，并基于此更新对任务的认知。系统检测本轮中发生的任务相关变化——Todo 完成状态变化、`Constraints` 违反记录、`Requirements` 满足情况、任务状态转移、子任务关闭、新偏差追加——并将这些变化写入 Session 快照。Plane Assembler 从 Session 中提取最新快照，组装为状态平面挂载到 Agent 上下文，使 Agent 在下一轮开始时立即掌握当前任务态势。

认知构建以轮次为周期，感知→构建→挂载构成完整闭环。只记录导致目标推进或路径修正的状态变更，不记录过程录像。

**纯文本持久化的设计理由：** 见 §6.5 文档数据模型。

mem0ress 只管一件事：认知的生命周期管理，也就是任务的创建、检验与认知态势的构建。大模型沙箱隔离、并发控制这些，都交给宿主操作系统。

mem0ress 不是回答问题的引擎，而是呈现状态的窗口。它在任何时刻都完整构建当前认知的所有要素——任务树在哪、做到哪了、约束有没有被触碰、目标偏了没有。不做相关性排序，不挑选，不截断。

---

## 删除内容五：§6 逻辑与流程设计（全部5个子节）

> **删除理由**：这章定义的是"执行循环怎么做、轮次序列是什么、参与方职责边界、状态机转换规则"——全是操作层/实现层语义，不属于接口语义规范。CAP Specification 不定义执行框架，这些内容属于实现文档。

### §6.1 执行循环

Task 的执行循环围绕三个核心动作展开：认知构建、任务检验和状态更新。这三个动作在每个轮次结束后依次执行，构成完整的感知-判断-更新闭环。

#### 5.1.1 标准轮次序列

每个轮次按以下固定顺序执行，不允许跳步或乱序：

```
轮次开始
  1. 认知构建：主 Agent 读取状态平面（PlaneAssembler 实时组装）
  2. 执行：主 Agent 执行 Todo；可选：带外追加 gotchas.md
  3. Session 写入：主 Agent 追加 session.md 快照；更新 task.md Todo 状态
  4. 检验触发（条件触发，非每轮必须）：
     主 Agent 设 status → VERIFYING
     宿主框架启动 Judge Agent
     Judge Agent 执行四层检验
     Judge Agent 写入 judge.md
     主 Agent 读取 judge.md 结论
     主 Agent 退出 VERIFYING 状态
  5. 决策：主 Agent 自主决策下一步
轮次结束
```

#### 5.1.2 参与方与职责边界

协议有三个参与方，职责严格隔离，不允许跨越。

**主 Agent（Main Agent）**负责执行任务，包括：创建任务、拆解 Todo、推进执行、写入 session 快照、触发 Judge、读取 Judge 结论、自主决策下一步（修正 / 完成 / 废弃）。主 Agent 不执行检验逻辑，不写 judge.md。

**Judge Agent（Judge Agent）**负责检验任务，包括：被动等待主 Agent 触发，读取文件系统快照，执行四层检验，将结论写入 judge.md。Judge Agent 不执行任何修复，不参与执行决策，不读取主 Agent 的执行历史，不写除 judge.md 之外的任何文件。

**宿主框架（Host Framework）**负责保障协议运行的基础设施，包括：管理文件系统布局、保证 Judge Agent 与主 Agent 的上下文隔离、向 Judge Agent 注入 task_id、处理 VERIFYING 超时保护。宿主框架不参与任务执行逻辑，不干预 Judge Agent 的检验结论。

#### 5.1.3 检验触发条件

检验不在每个轮次都触发。主 Agent 在以下情况触发检验：

1. **所有 Todo 已标记完成**（必须触发）
2. **主 Agent 判断当前阶段性成果需要验证**（主动触发）
3. **利益相关者显式请求检验**（按需触发）

检验触发是主 Agent 的主动动作，不是系统自动行为。

#### 5.1.4 VERIFYING 超时保护

宿主框架负责 VERIFYING 状态的超时保护。**默认超时：180 秒。**

超时后宿主框架的处理义务：
1. 强制结束 Judge Agent 调用
2. 在 judge.md 追加超时记录（Turn + Timestamp + `Verdict: TIMEOUT`）
3. 将 task.md status 从 VERIFYING 恢复为 IN_PROGRESS
4. 通知主 Agent 检验超时，由主 Agent 决定是否重试

宿主框架不允许在超时后直接标记任务为 FAILED 或 COMPLETED，决策权属于主 Agent。

### §6.2 认知构建

认知构建是轮次结束后生成状态平面快照的动作。它在任何节点（刚启动时、执行中、或检验失败后）都需要执行，为 Agent 提供当前任务的可判断状态。

状态平面是当前绑定 Task 的忠实投影，具有以下特性：只输出当前状态，不做偏差判断；实时扫描，每次调用直接读文件系统，不缓存；状态平面是当下组装的结果，不是被维护的缓存——不存在任何时刻的状态被后续快照覆盖的可能性；在当前 Task 边界内不做相关性排序、不挑选、不截断；非侵入，只读不写，不改变任何状态。状态平面不默认展开整棵任务树，也不默认读取父任务或子任务的完整状态——父子任务信息只有在当前 Task 的 Picture 判断需要时，才以摘要形式进入状态平面。

状态平面的显示内容包括：任务树结构（父子关系）；每个任务的 todo 完成度（如 "2/3 Todos 完成"）；任务状态（CREATED / IN_PROGRESS / COMPLETED / ABANDONED）；偏差记录（Gotchas）指针；Session 最近变化指针（指向 Session 中最近的状态快照位置，供 Agent 按需追溯）。`Picture`/`Requirements`/`Constraints` 从 task.md 获取，不显示在状态平面中。

Session 快照是认知构建的数据来源。每个轮次的状态快照记录`code_progress`、`docs_progress`、`todos`和`status`。Session 采用版本快照模型，只追加不覆盖。

### §6.3 任务创建

任务创建是确立认知边界的起点。Agent 在创建任务或子任务时，首要目标不是写代码，而是明确定义任务的 `Picture`、`Requirements` 和 `Constraints`。模型的定义应从 `Picture` 开始——先定义 `Picture` 作为目标锚，再从中推导出 `Requirements` 和 `Constraints`。冲突检测在三者全部定义后进行——若 `Requirements` 与 `Constraints` 相互矛盾，在多轮沟通中引导协作者修正，直到矛盾消除，模型写入 task.md。

Todo 步进拆解：在锚定模型后，Agent 将任务拆解为具体的机械步（Todo）。这些 Todo 构成了后续检验进度的基准线。

**Todo 与 Subtask 的边界：** Todo 是任务内部的机械步，不是独立的认知单元。Subtask 是独立的 Task，有自己的 Picture/Requirements/Constraints 三要素，是完整的认知闭包。区分标准是：是否有独立的 Picture——有独立 Picture 的是 Subtask，没有独立 Picture 的是 Todo。父任务的 Todo 完成后，父任务本身即进入 VERIFYING 状态；父任务的 Subtask 完成后，只向父任务传递完成信号，不改变父任务的状态。

**任务创建顺序：** 任务创建必须按以下顺序进行，不允许跳步：Step 1 定义 Picture → Step 2 从 Picture 推导 Requirements → Step 3 从 Picture 推导 Constraints → Step 4 冲突检测（Requirements 与 Constraints 是否矛盾）→ Step 5 若有矛盾与利益相关者协商直到矛盾消除 → Step 6 拆解 Todos → Step 7 写入 task.md，初始化 session.md / gotchas.md / judge.md（空文件）。Step 4 不可跳过——矛盾的 Requirements / Constraints 写入后，Judge 永远无法通过。

**Requirements 合法性检查：** 在 Step 2 完成后，对每条 Requirement 执行合法性检查——必须可独立验证（存在可运行的验证命令或明确的数值指标），验收标准必须在 task.md 创建时就能确定（不允许"完成后再定"），不合法的 Requirement 不允许写入。

**子任务创建：** 子任务是独立的任务节点，拥有独立的 PRC 模型和四个协议文件。父任务的完成以所有直接子任务关闭（COMPLETED 或 ABANDONED）为前提。主 Agent 不允许在子任务处于 CREATED 或 IN_PROGRESS 状态时完成父任务。

### §6.4 任务检验

任务检验在认知构建之后执行，负责判断当前状态是否满足 `Picture`。检验在轮次结束后自动触发，是只读操作，不执行写操作。

**四层关卡（Tiers）：**

任务检验按顺序执行以下四层关卡。其中 Tier 0/1/2 为客观检验条件，由 Judge Agent 自动执行并判断是否通过，无需主 Agent 主观决策；Tier 3 为语义对齐关卡，由 Agent 根据任务属性决定是否启用。

* **Tier 0: `Constraints` 约束检查。** 检查 `Constraints` 是否被逾越，若有逾越报告违反事实，由主 Agent 决定是否修复及如何修复。
* **Tier 1: Todo 完成检查。** 检查所有 Todo 步是否已完成、所有直接子任务是否已关闭。子任务处于 COMPLETED 或 ABANDONED 状态即为已关闭；处于 CREATED 或 IN_PROGRESS 状态则视为未完成。
* **Tier 2: `Requirements` 满足检查。** 验证每个 Requirement 是否达标。
* **Tier 3: Picture Alignment Check。** Tier 3 不重复验证 Requirements（那是 Tier 2 的职责），而是检查 Requirements 无法穷尽的 Picture 剩余语义偏差。执行时，Judge Agent 将 Picture 拆解为 Picture Claims，并将 Tier 1/2 的检验结果、Constraints 状态、Data Plane 证据、未解决 Gotchas 和实际产出映射到这些 Claims 上。若存在核心 Picture Claim 缺少证据覆盖，或存在足以阻止利益相关者认可任务完成的 residual gap，则任务不得关闭。若证据不足，Tier 3 必须返回 UNCERTAIN，而不是强行 PASS 或 FAIL。

**决策执行规则：**

检验完成后结果写入 `judge.md`，由主 Agent 从 `judge.md` 读取并决策下一步。任务完成后是否标记完成，由 Agent 自主决定。ABANDONED 由 Agent 主动标记，与检验结果无关。

检验通过 → Agent 可标记任务完成；检验未通过 → Agent 决定下一步（修正、重试或废弃）。

**Judge Agent 上下文构成：** Judge Agent 被调用时，宿主框架注入的上下文仅包含 `task_id`（用于定位文件）和 Judge Agent 系统提示（固定，不含主 Agent 执行历史）。Judge Agent 从文件系统读取检验依据，不接收主 Agent 传递的任何运行时信息。

**四层检验执行规则：**

```
Tier 0 → Tier 1 → Tier 2 → Tier 3（条件触发）

任何 Tier FAIL → 立即停止 → 输出 FAILED
所有 Tier PASS（+ Tier 3 PASS 或 SKIPPED）→ 输出 PASSED
```

**快速失败原则：** Tier 失败后不执行后续 Tier。Judge Agent 不累积所有问题再报告，而是在发现第一个阻断性问题时立即停止。

**Tier 执行方式表：**

| Tier | 名称 | 执行方式 | 依赖文件 |
|------|------|---------|---------|
| Tier 0 | Constraints 约束检查 | 纯逻辑：扫描 session.md + gotchas.md 中的违反记录 | task.md, session.md, gotchas.md |
| Tier 1 | Todo & Subtask 完成检查 | 纯逻辑：读取 task.md Todo 状态 + 扫描子任务目录 | task.md |
| Tier 2 | Requirements 验收检查 | 运行测试命令：执行可验证动作，记录命令输出 | task.md, session.md |
| Tier 3 | 语义对齐检查 | LLM 推断：Judge Agent 读取 Picture + 实际产出进行语义比对 | task.md, session.md |

**Tier 2 的关键约束：** Tier 2 不允许依赖 LLM 推断判断 Requirement 是否满足。每条 Requirement 必须有对应的可运行验证命令。若 Requirement 无法自动化验证，在任务创建阶段应被标记为无效 Requirement。

**Judge Agent 输出约束：** Judge Agent 只报告事实，不给出修复建议，不判断"主 Agent 应该怎么做"，不修改 task.md / session.md / gotchas.md，不直接标记任务为 COMPLETED 或 ABANDONED。FAIL 结论写入 judge.md 后，Judge Agent 的职责结束，决策权回到主 Agent。

### §6.5 状态更新

状态更新将检验结果反映到 Task 状态，并处理决策执行。

**子任务关闭协议：** 子任务进入 COMPLETED 时，父任务的认知锁定在"子任务 ID + 最终状态（COMPLETED / ABANDONED）"这条最小记录上。子任务可选择生成 closure note 作为人类可读归档，不影响父任务的状态平面组装。

**主 Agent 决策空间：** 主 Agent 读取 judge.md 后可选择以下任意一条路径，无需外部批准：PASSED + 所有 Todo 完成后 → 调用 `complete_task` 进入 COMPLETED；PASSED + 发现新的 Todo → 继续执行；FAILED + 问题可修正 → 修正后重新触发检验；FAILED + 问题复杂 → 拆解子任务将问题分解；FAILED + 问题无解 → 调用 `abandon_task` 进入 ABANDONED；TIMEOUT → 重试检验或调用 `abandon_task`。主 Agent 不允许在 Judge 未通过时调用 `complete_task`。

**ABANDONED 的处理义务：** 任务进入 ABANDONED 时，主 Agent 有以下义务：在 gotchas.md 追加废弃原因（`如何处理` 字段写"任务废弃"及原因）；确保所有直接子任务也处于终态（COMPLETED 或 ABANDONED）。ABANDONED 不需要经过 Judge 检验，主 Agent 可在任意时刻主动废弃。

**Gotcha 追加协议：** Gotcha 是带外操作，不在标准轮次序列内，不阻塞主流程。必须追加 Gotcha 的情况：session.md 的 `Constraint Violations` 字段有记录（由宿主框架自动触发）；任务进入 ABANDONED。应当追加 Gotcha 的情况：执行路径发生非预期变更（发现原 Todo 无法执行）；发现 Requirements 或 Constraints 存在歧义并已处理。写入时机：在发现偏差的当前轮次写入，不要积累到任务结束再补写。

**协议一致性保证：** mem0ress 不提供数据库级别的事务保证，一致性依赖调用方遵守以下规则——单写入方原则（每个文件只有一个写入方，不允许并发写入）；顺序追加原则（session.md / gotchas.md / judge.md 只追加不修改历史）；先写后读原则（主 Agent 写入 session.md 后再触发 Judge Agent 读取）。以下场景超出本协议当前版本的支持范围：并发子任务执行（多个子任务同时向同一父任务写入 session.md，未定义合并规则）；多 Agent 并行执行同一任务（违反单写入方原则）；事务性多步写入（若宿主框架崩溃在 session 写入和 judge 触发之间，协议不定义恢复行为）；跨 workspace 的任务依赖（协议只在单 workspace 内定义）。遇到这些场景时，宿主框架应在进入该场景前让度给人工干预。
