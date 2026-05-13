# mem0ress Protocol

> 本文件定义协议三方参与者的**行为契约**：
> 谁在什么时机做什么、按什么顺序、对哪些文件有什么权限。
>
> 字段格式定义见 SCHEMA.md。
> 文件模板见 task.md / session.md / judge.md / gotchas.md。

---

## 1. 参与方与职责边界

协议有三个参与方，职责严格隔离，不允许跨越。

### 主 Agent（Main Agent）

**职责：** 执行任务。

具体包括：创建任务、拆解 Todo、推进执行、写入 session 快照、触发 Judge、读取 Judge 结论、自主决策下一步（修正 / 完成 / 废弃）。

**不做：** 不执行检验逻辑，不写 judge.md。

### Judge Agent（Judge Agent）

**职责：** 检验任务。

具体包括：被动等待主 Agent 触发，读取文件系统快照，执行四层检验，将结论写入 judge.md。

**不做：** 不执行任何修复，不参与执行决策，不读取主 Agent 的执行历史，不写除 judge.md 之外的任何文件。

### 宿主框架（Host Framework）

**职责：** 保障协议运行的基础设施。

具体包括：管理文件系统布局、保证 Judge Agent 与主 Agent 的上下文隔离、向 Judge Agent 注入 task_id、处理 VERIFYING 超时保护。

**不做：** 不参与任务执行逻辑，不干预 Judge Agent 的检验结论。

---

## 2. 文件读写权限

每个文件有唯一的写入方。

| 文件 | 主 Agent | Judge Agent | 宿主框架 |
|-----|---------|------------|---------|
| `task.md` | 读 + 写 | 只读 | — |
| `session.md` | 只写（追加） | 只读 | — |
| `gotchas.md` | 只写（追加） | 只读 | — |
| `judge.md` | 只读 | 只写（追加） | — |

**写入规则：**
- session.md 和 gotchas.md 只追加，不修改历史内容
- judge.md 只追加，不修改历史内容
- task.md 是唯一允许覆盖写的文件（更新 Todo 状态、更新 status）
- task.md 的 Picture / Requirements / Constraints 一旦写入不允许修改；如需变更，创建新版本任务

---

## 3. 执行循环

### 3.1 标准轮次序列

每个轮次按以下固定顺序执行，不允许跳步或乱序：

```
┌─────────────────────────────────────┐
│            轮次开始                  │
│                                     │
│  1. 认知构建                         │
│     主 Agent 读取状态平面             │
│     （PlaneAssembler 实时组装）       │
│                                     │
│  2. 执行                             │
│     主 Agent 执行 Todo               │
│     可选：带外追加 gotchas.md         │
│                                     │
│  3. Session 写入                     │
│     主 Agent 追加 session.md 快照    │
│     更新 task.md Todo 状态           │
│                                     │
│  4. 检验触发（条件触发，非每轮必须）   │
│     主 Agent 设 status → VERIFYING   │
│     宿主框架启动 Judge Agent          │
│     Judge Agent 执行四层检验         │
│     Judge Agent 写入 judge.md        │
│     主 Agent 读取 judge.md 结论      │
│     主 Agent 退出 VERIFYING 状态     │
│                                     │
│  5. 决策                             │
│     主 Agent 自主决策下一步           │
│                                     │
│            轮次结束                  │
└─────────────────────────────────────┘
```

### 3.2 检验触发条件

检验不在每个轮次都触发。主 Agent 在以下情况触发检验：

1. **所有 Todo 已标记完成**（必须触发）
2. **主 Agent 判断当前阶段性成果需要验证**（主动触发）
3. **利益相关者显式请求检验**（按需触发）

检验触发是主 Agent 的主动动作，不是系统自动行为。

### 3.3 VERIFYING 超时保护

宿主框架负责 VERIFYING 状态的超时保护。

**默认超时：** 180 秒。

超时后宿主框架的处理义务：
1. 强制结束 Judge Agent 调用
2. 在 judge.md 追加超时记录（Turn + Timestamp + `Verdict: TIMEOUT`）
3. 将 task.md status 从 VERIFYING 恢复为 IN_PROGRESS
4. 通知主 Agent 检验超时，由主 Agent 决定是否重试

宿主框架不允许在超时后直接标记任务为 FAILED 或 COMPLETED，决策权属于主 Agent。

---

## 4. 任务创建协议

### 4.1 创建顺序

任务创建必须按以下顺序进行，不允许跳步：

```
Step 1: 定义 Picture
Step 2: 从 Picture 推导 Requirements
Step 3: 从 Picture 推导 Constraints
Step 4: 冲突检测（Requirements 与 Constraints 是否矛盾）
Step 5: 若有矛盾，与利益相关者协商直到矛盾消除
Step 6: 拆解 Todos
Step 7: 写入 task.md，初始化 session.md / gotchas.md / judge.md（空文件）
```

**Step 4 不可跳过。** 矛盾的 Requirements / Constraints 写入后，Judge 永远无法通过。

### 4.2 Requirements 合法性检查

在 Step 2 完成后，对每条 Requirement 执行合法性检查：

- 必须可独立验证：存在可运行的验证命令，或存在明确的数值指标
- 验收标准必须在 task.md 创建时就能确定（不允许"完成后再定"）
- 不合法的 Requirement 不允许写入，必须与利益相关者协商重新定义

### 4.3 子任务创建

子任务是独立的任务节点，拥有独立的 PRC 模型和四个协议文件。

父任务的完成以所有直接子任务关闭（COMPLETED 或 ABANDONED）为前提。
主 Agent 不允许在子任务处于 CREATED 或 IN_PROGRESS 状态时完成父任务。

---

## 5. Judge Agent 检验协议

### 5.1 Judge Agent 的上下文构成

Judge Agent 被调用时，宿主框架注入的上下文仅包含：

1. `task_id`（用于定位文件）
2. Judge Agent 系统提示（固定，不含主 Agent 执行历史）

Judge Agent 从文件系统读取检验依据，不接收主 Agent 传递的任何运行时信息。

### 5.2 四层检验执行规则

```
Tier 0 → Tier 1 → Tier 2 → Tier 3（条件触发）

任何 Tier FAIL → 立即停止 → 输出 FAILED
所有 Tier PASS（+ Tier 3 PASS 或 SKIPPED）→ 输出 PASSED
```

**快速失败原则：** Tier 失败后不执行后续 Tier。Judge Agent 不累积所有问题再报告，而是在发现第一个阻断性问题时立即停止。理由：后续 Tier 的检验在前置 Tier 失败时结论不可信。

### 5.3 Tier 执行方式

| Tier | 名称 | 执行方式 | 依赖文件 |
|------|------|---------|---------|
| Tier 0 | Constraints 约束检查 | 纯逻辑：扫描 session.md + gotchas.md 中的违反记录 | task.md, session.md, gotchas.md |
| Tier 1 | Todo & Subtask 完成检查 | 纯逻辑：读取 task.md Todo 状态 + 扫描子任务目录 | task.md |
| Tier 2 | Requirements 验收检查 | 运行测试命令：执行可验证动作，记录命令输出 | task.md, session.md |
| Tier 3 | 语义对齐检查 | LLM 推断：Judge Agent 读取 Picture + 实际产出进行语义比对 | task.md, session.md |

**Tier 2 的关键约束：** Tier 2 不允许依赖 LLM 推断判断 Requirement 是否满足。每条 Requirement 必须有对应的可运行验证命令。若 Requirement 无法自动化验证，在任务创建阶段应被标记为无效 Requirement。

### 5.4 Judge Agent 输出约束

Judge Agent 只报告事实，不做以下任何事：

- 不给出修复建议
- 不判断"主 Agent 应该怎么做"
- 不修改 task.md / session.md / gotchas.md
- 不直接标记任务为 COMPLETED 或 ABANDONED

FAIL 结论写入 judge.md 后，Judge Agent 的职责结束。决策权回到主 Agent。

---

## 6. 主 Agent 决策协议

### 6.1 读取 Judge 结论后的决策空间

主 Agent 读取 judge.md 后可选择以下任意一条路径，无需外部批准：

| Judge 结论 | 可选决策 |
|-----------|---------|
| PASSED | 调用 `complete_task`，任务进入 COMPLETED |
| PASSED | 继续执行（例如发现新的 Todo）|
| FAILED | 修正后重新触发检验 |
| FAILED | 拆解子任务，将问题分解 |
| FAILED | 调用 `abandon_task`，任务进入 ABANDONED |
| TIMEOUT | 重试检验 |
| TIMEOUT | 调用 `abandon_task` |

主 Agent 不允许在 Judge 未通过时调用 `complete_task`。

### 6.2 ABANDONED 的处理义务

任务进入 ABANDONED 时，主 Agent 有以下义务：

1. 在 gotchas.md 追加废弃原因（`如何处理` 字段写"任务废弃"及原因）
2. 确保所有直接子任务也处于终态（COMPLETED 或 ABANDONED）

ABANDONED 不需要经过 Judge 检验，主 Agent 可在任意时刻主动废弃。

---

## 7. Gotcha 追加协议

Gotcha 是带外操作，不在标准轮次序列内，不阻塞主流程。

**必须追加 Gotcha 的情况：**
1. session.md 的 `Constraint Violations` 字段有记录（由宿主框架自动触发）
2. 任务进入 ABANDONED（见 §6.2）

**应当追加 Gotcha 的情况：**
1. 执行路径发生非预期变更（发现原 Todo 无法执行）
2. 发现 Requirements 或 Constraints 存在歧义并已处理

**Gotcha 的写入时机：** 在发现偏差的当前轮次写入，不要积累到任务结束再补写。

---

## 8. 协议一致性保证

### 8.1 调用方的一致性责任

mem0ress 不提供数据库级别的事务保证。一致性依赖调用方遵守以下规则：

1. **单写入方原则**：每个文件只有一个写入方（见第 2 节权限表），不允许并发写入
2. **顺序追加原则**：session.md / gotchas.md / judge.md 只追加，不修改历史
3. **先写后读原则**：主 Agent 写入 session.md 后，再触发 Judge Agent 读取

### 8.2 不支持的场景

以下场景超出本协议当前版本的支持范围：

- **并发子任务执行**：多个子任务同时向同一父任务写入 session.md（未定义合并规则）
- **多 Agent 并行执行同一任务**：违反单写入方原则
- **事务性多步写入**：若宿主框架崩溃在 session 写入和 judge 触发之间，协议不定义恢复行为
- **跨 workspace 的任务依赖**：协议只在单 workspace 内定义

遇到这些场景时，宿主框架应在进入该场景前让度给人工干预。
