# mem0ress Behavioral Protocol

> schema.md defines the canonical structural authority.
> SPEC.md defines the architectural semantics.
>本文档定义参与方行为规范与运行时配置。

---
schema_ref: ./schema.md
spec_ref: ./SPEC.md

# 运行时配置
# 本节为机器可读配置区，与下方行为协议语义完全一致。

version: "1.0"

## 状态机
states:
  - CREATED
  - IN_PROGRESS
  - VERIFYING
  - COMPLETED
  - ABANDONED

transitions:
  CREATED:
    - IN_PROGRESS
    - ABANDONED
  IN_PROGRESS:
    - VERIFYING
    - COMPLETED
    - ABANDONED
  VERIFYING:
    - COMPLETED
    - IN_PROGRESS
    - ABANDONED
  COMPLETED: []
  ABANDONED: []

## 验证层级
# Tier 1/2/3 为验证单路径的三个阶段
tiers:
  Tier 1:
    name: 约束验证
    check: constraint_validation
    description: Constraint 违规检查，参考信号（loop 或忽略）
    on_fail: RECORD_ONLY
  Tier 2:
    name: 需求验证
    check: requirement_validation
    description: deterministic 验证，评估参考，逐步满足
    on_fail: RECORD_ONLY
  Tier 3:
    name: 语义对齐验证
    check: semantic_alignment
    description: 唯一硬门槛，FAIL → amend 循环
    on_fail: PASS_FAIL_UNCERTAIN
    on_uncertain: HUMAN_DECISION

## 超时配置
timeouts:
  verifying_default: 180      # seconds
  tier3_default: 300          # seconds

## 协议约束
constraints:
  no_concurrent_session_writes: true
  no_multi_agent_same_task: true
  no_cross_workspace_dependencies: true
  verifying_is_transient: true    # 不可停留，必须转移

---

## 1. 参与方

| 参与方 | 职责 |
|--------|------|
| **主 Agent（Main Agent）** | 执行任务：创建任务、拆解 Todo、推进执行、写入 session 快照、触发 Verify Agent、读取 Verify 结论、自主决策 |
| **Verify Agent** | 检验任务：被动等待 `pending_verify` 触发、执行 Tier 1/2/3 检验、写入 VERIFY.md |
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
  1. 认知构建 → 2. 执行（可选追加 gotchas.md）→ 3. Session 写入
  4. tier0 进度检查 → 若有 Todo 本轮完成则设置 pending_verify
  5. 若 pending_verify 有值则触发 Verify（Tier 1/2/3）
  6. 决策
轮次结束
```

**pending_verify 机制**：每轮次结束时，tier0 检测本轮完成的 Todo，将其记录到 session 快照的 `pending_verify` 字段。Verify Agent 执行完成后清除该字段。

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

| Tier | 检查层 | 语义职责 | 性质 |
|------|--------|---------|------|
| Tier 1 | 约束验证 | Constraint 约束检查 — 是否触碰红线 | 参考信号（loop 或忽略） |
| Tier 2 | 需求验证 | VERIFY.md marker 执行 — requirements 条件是否满足 | 评估参考（逐步满足） |
| Tier 3 | 语义对齐验证 | 语义对齐 — Requirements 能否支撑 Picture | **唯一硬门槛**，无独立触发语义 |

**验证单路径模型：** 验证触发有三种方式（每 todo 完成 / 人主动 verify / 达到阈值），触发后统一执行完整验证路径：

```
Tier 1（约束验证）→ Tier 2（需求验证）→ Tier 3（语义对齐验证）
```

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
| task.md | 主 Agent | 认知三要素在创建时写入，可通过 amend 修正 |
| session.md | 主 Agent | 追加，不覆盖历史 |
| gotchas.md | 主 Agent | 追加，不删除历史 |
| VERIFY.md | 主 Agent / Verify Agent | 追加；`[.] / (.) / {.}` 条目可作为执行依据，`[] / () / {}` 仅作记录；已完成条目（`[✓]`）可退回 `[.]` 重新验证；Verify 执行完成后清除 `pending_verify` |

**写入权限语义**：
- **主 Agent** 对 task.md 只有一次写入权（创建时），认知三要素在创建时写入，可通过 amend 修正
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

### VERIFY.md — 验证条目格式

验证条目格式和 marker 语义详见 [SPEC.md §5.4.1](../SPEC.md#_541-验证定义工作流)。

**核心约束**：
- `[.]` / `(.)` / `{.}` 条目可作为执行依据，`[]` / `()` / `{}` 仅作记录
- 已完成条目可退回 `[.]` 重新验证
- Verify 执行完成后清除 `pending_verify`

详细状态转移规则、amend 协议见 [SPEC.md §5.4.2](../SPEC.md#_542-三状态与-amend-命令)。

### /cap amend 命令

详见 [SPEC.md §5.4.2](../SPEC.md#_542-三状态与-amend-命令)。
