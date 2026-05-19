# mem0ress Behavioral Protocol

> protocol.md defines WHAT the system means.
> schema.md defines the canonical structural authority.
> protocol.yaml defines HOW the runtime executes.
> yaml MUST NOT introduce semantics not defined in schema.md.

本文档是 mem0ress 的 behavioral protocol layer — 回答"参与方如何行为"。

---

## 1. 参与方

| 参与方 | 职责 |
|--------|------|
| **主 Agent（Main Agent）** | 执行任务：创建任务、拆解 Todo、推进执行、写入 session 快照、触发 Verify Agent、读取 Verify 结论、自主决策 |
| **Verify Agent** | 检验任务：被动等待触发、执行四层任务验证、写入 VERIFY.md |
| **宿主框架（Host Framework）** | 基础设施：管理文件系统布局、隔离上下文、注入 task_id、处理 VERIFYING 超时（默认 180s） |

---

## 2. 文件读写权限

| 文件 | 主 Agent | Verify Agent |
|------|---------|------------|
| task.md | 读 + 写（覆盖写） | 只读 |
| session.md | 追加写 | 只读 |
| gotchas.md | 追加写 | 只读 |
| VERIFY.md | 追加写 | 追加写 |

---

## 3. 执行轮次

```
轮次开始
  1. 认知构建 → 2. 执行（可选追加 gotchas.md）→ 3. Session 写入 → 4. 检验触发（条件）→ 5. 决策
轮次结束
```

**检验触发条件**（满足以下任一条件即触发）：所有 Todo 已完成；主 Agent 主动请求；利益相关者显式请求。

---

## 4. 状态语义

| 状态 | 语义 |
|------|------|
| CREATED | 任务已声明，Picture 尚未开始执行 |
| IN_PROGRESS | 任务正在执行，认知演化中 |
| VERIFYING | 瞬态，Verify Agent 检验中（不可停留） |
| COMPLETED | 达到 Picture 描述的语义成功状态 |
| ABANDONED | 任务终止（未达 Picture） |

### 状态转换

| From | To | 触发 |
|------|----|------|
| CREATED | IN_PROGRESS | 任意 todo 标记完成 |
| IN_PROGRESS | VERIFYING | Agent 请求 Verify 验证 |
| VERIFYING | COMPLETED | Verify Agent 返回 PASS |
| VERIFYING | IN_PROGRESS | Verify Agent 返回 FAIL |
| CREATED / IN_PROGRESS | ABANDONED | 任务终止 |

---

## 5. 任务验证语义

| Tier | 检查层 | 语义职责 | 性质 | 是否触发 Tier 3 |
|------|--------|---------|------|--------------|
| Tier 0 | 约束验证 | Constraint 约束检查 — 是否触碰红线 | 参考信号（loop 或忽略） | 路径一 + 路径二 |
| Tier 1 | 进度验证 | Todo 完成检查 — 是否完成计划项 | 观察动作（每轮次执行），不属于 verify 操作 | 路径二（兜底） |
| Tier 2 | 需求验证 | VERIFY.md marker 执行 — requirements 条件是否满足 | 评估参考（逐步满足） | 路径一 + 路径二 |
| Tier 3 | 语义对齐验证 | 语义对齐 — Requirements 能否支撑 Picture | **唯一硬门槛**，无独立触发语义 | 仅作路径末端 |

**双路径触发模型：**
- **路径一（自然操作）：** 每 todo 完成时触发 Tier 0 → Tier 2 → Tier 3
- **路径二（主动操作）：** 人主动 verify / 达到最大间隔阈值时触发 Tier 0 → Tier 1 → Tier 2 → Tier 3
- **Tier 1 特殊定位：** 每轮次自动执行（观察动作），更新状态快照，不触发 Tier 3；仅在路径二中作为 verify 操作的一环执行

**Tier 3 进入条件：**
- 路径一：Tier 0 无 violation + Tier 2 满足 → 进入 Tier 3
- 路径二：Tier 0 无 violation + Tier 1 满足 + Tier 2 满足 → 进入 Tier 3

**语义对齐失败流程**：若语义对齐判定未对齐 → 触发 amend 循环 → 新增/修改 Requirement 或 Constraint → 重规划 Todo → 继续执行 → 重新检验。

语义对齐语义约束：证据不足时必须返回 **UNCERTAIN**，不得强行 PASS。

---

## 6. Verify Agent 调用约定

- 上下文仅含：`task_id` + 系统提示（不含主 Agent 执行历史）
- 从文件系统读取依据，不接收运行时信息
- 写入 VERIFY.md，不修改其他文件

---

## 7. VERIFYING 超时

- 默认：180 秒
- 超时处理：强制结束 Verify Agent、写入 `Verdict: TIMEOUT`、恢复为 IN_PROGRESS

---

## 8. 主 Agent 决策速查

| Verify 结论 | 可选决策 |
|------------|---------|
| PASSED | complete_task / 继续执行 |
| FAILED | 修正重试 / 拆解子任务 / abandon_task |
| TIMEOUT | 重试 / abandon_task |

---

## 9. 协议边界（不支持的场景）

- 并发子任务写入同一 session.md
- 多 Agent 并行执行同一任务
- 跨 workspace 任务依赖
- 事务性多步写入（无恢复协议）

遇到上述场景时，让度给人。

---

## 10. 写入规则

| 文件 | 写入者 | 约束 |
|------|--------|------|
| task.md | 主 Agent | cognitive_triad 创建后不可修改 |
| session.md | 主 Agent | 追加，不覆盖历史 |
| gotchas.md | 主 Agent | 追加，不删除历史 |
| VERIFY.md | 主 Agent / Verify Agent | 追加；`[.] / (.) / {.}` 条目可作为执行依据，`[] / () / {}` 仅作记录；已完成条目（`[\✓]` / `(\✓)` / `{\✓}`）不可 amend |

**写入权限语义**：
- **主 Agent** 对 task.md 只有一次写入权（创建时），之后不可修改认知三要素
- **Verify Agent** 对 VERIFY.md 追加，不读取 runtime 内存状态（隔离验证）

---

## 11. 文件语义（详述）

### task.md — 任务声明

语义权威表面。包含：

- **id**：任务标识符（目录名为 source of truth）
- **status**：当前生命周期阶段
- **cognitive_triad**：认知三要素
  - **picture**：语义成功状态（任务完成时看起来是什么样的）
  - **requirements**：可验证条件列表（验证方式定义在 VERIFY.md）
  - **constraints**：不可逾越的红线列表
- **gotcha_refs**：引用到 gotchas.md 的偏差记录
- **todos**：可执行检查清单

### session.md — 执行快照

追加式认知增量流。

规则：
- 仅记录 discoveries、decisions、progress
- 禁止记录：raw logs、chain-of-thought、transcript

### gotchas.md — 偏差记录

追加式recovery-critical 发现记录。

规则：
- 追加，不删除历史
- 解决记录可追加，不覆盖原发现

### VERIFY.md — 验证定义

主 Agent 和 Verify Agent 追加写的验证条目集合。包含所有 Requirement 和 Constraint 的验证方式定义，以及 Verify Agent 的检验结论记录。

**状态转移规则：**

```
未确认 → 确认：人机对话确认验证方式 → [.] / (.) / {.}]
确认 → 已完成：验证执行（pass/skip/fail）→ [\✓] / (\✓) / {\✓}]
已完成后不可逆向转移
```

**三类实体的状态机差异：**

| 实体 | `[]` → `[.]` | `[.]` → `[\✓]` | `[\✓]` 可逆？ | 完成概念 |
|------|-------------|----------------|-------------|---------|
| Non-persistent requirement | ✅ | ✅ | ❌ | ✅（永久） |
| Persistent requirement | ✅ | ✅（阶段性） | ✅（语义漂移时） | ✅（阶段性） |
| Constraint | ✅ | ✅（违规解决） | ❌ | ✅（violation resolved） |

**Non-persistent requirement：**

```
[] → [.] → [\✓]  (永久完成，不退回)
```

**Persistent requirement：**

```
[] → [.] → [\✓]  (阶段性完成；下一轮次出现新的语义漂移时，可退回 [.] 重新验证)
```

- `[\✓]` 标记时机：至少一个 todo 完成 + 至少一轮次结束 + 验收检查通过
- 退回触发：下一轮次发现新的语义漂移，由 Verify Agent 或人主动提出

**Constraint：**

```
[] → [.] → [\✓]  (已解决)
          ↓
       [×]  (violated — 状态记录，Agent 继续)
```

- `[\✓]` = 约束已解决
- `[×]` = 约束违规中（状态记录，不 FAIL，不阻塞）
- 每轮次必须重新验证

**状态约束**：

| 状态 | marker | 可 amend？ |
|------|--------|-----------|
| 未确认 | `[]` / `()` / `{}` | ✅ |
| 确认 | `[.]` / `(.)` / `{.}` | ✅（执行前） |
| 已完成 | `[\✓]` / `(\✓)` / `{\✓}` | ❌ |
| Constraint 违规 | `[×]` | ✅（解决后转为 `[\✓]`） |

### /cap amend 命令

**amend 是唯一 mutation 原语。** create = amend(mode=initial)——新任务的创建是 amend 的首次调用；已有条目的修正是 amend 的后续调用。

在任意时刻发起对 VERIFY.md 的修正。

**交互流程**：

```
/cap amend
  → 仅展示未确认条目（[] / () / {}）
  → TUI 询问：「更新现有 marker」还是「新增 marker」
  → 用户指定要修正的条目
  → 用户提供新内容
  → 确认写入
  → session.md 记录此次 amend
```

**约束**：

- 仅未确认条目（`[]` / `()` / `{}`）可 amend
- 已确认条目（`[.]` / `(.)` / `{.}`）执行前可 amend，执行后不可
- 已完成条目（`[\✓]` / `(\✓)` / `{\✓}`）非持续性不可修改，持续性可退回 `[.]` 重新验证
- Constraint 的 `[×]`（违规中）可 amend（解决后转为 `[\✓]`）
- amend 记录追加到 session.md（可审计）
