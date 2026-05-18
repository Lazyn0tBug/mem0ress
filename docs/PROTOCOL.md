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
| **主 Agent（Main Agent）** | 执行任务：创建任务、拆解 Todo、推进执行、写入 session 快照、触发 Judge、读取 Judge 结论、自主决策 |
| **Judge Agent（Judge Agent）** | 检验任务：被动等待触发、执行四层检验（Tier 0/1/2/3）、写入 judge.md |
| **宿主框架（Host Framework）** | 基础设施：管理文件系统布局、隔离上下文、注入 task_id、处理 VERIFYING 超时（默认 180s） |

---

## 2. 文件读写权限

| 文件 | 主 Agent | Judge Agent |
|------|---------|------------|
| task.md | 读 + 写（覆盖写） | 只读 |
| session.md | 追加写 | 只读 |
| gotchas.md | 追加写 | 只读 |
| judge.md | 只读 | 追加写 |
| verify.md | 追加写 | 只读 |

---

## 3. 执行轮次

```
轮次开始
  1. 认知构建 → 2. 执行（可选追加 gotchas.md）→ 3. Session 写入 → 4. 检验触发（条件）→ 5. 决策
轮次结束
```

**检验触发条件**（满足其一即触发）：所有 Todo 已完成；主 Agent 主动请求；利益相关者显式请求。

---

## 4. 状态语义

| 状态 | 语义 |
|------|------|
| CREATED | 任务已声明，Picture 尚未开始执行 |
| IN_PROGRESS | 任务正在执行，认知演化中 |
| VERIFYING | 瞬态，Judge 检验中（不可停留） |
| COMPLETED | 达到 Picture 描述的语义成功状态 |
| ABANDONED | 任务终止（未达 Picture） |

### 状态转换

| From | To | 触发 |
|------|----|------|
| CREATED | IN_PROGRESS | 任意 todo 标记完成 |
| IN_PROGRESS | VERIFYING | Agent 请求 Judge 验证 |
| VERIFYING | COMPLETED | Judge 返回 PASS |
| VERIFYING | IN_PROGRESS | Judge 返回 FAIL |
| CREATED / IN_PROGRESS | ABANDONED | 任务终止 |

---

## 5. Judge Tier 语义

| Tier | 语义职责 | 失败行为 |
|------|---------|---------|
| **Tier 0** | Constraint 约束检查 — 是否触碰红线 | 立即 FAIL |
| **Tier 1** | Todo 完成检查 — 是否完成所有计划项 | 立即 FAIL |
| **Tier 2** | verify.md marker 执行 — requirements 条件是否满足 | 立即 FAIL |
| **Tier 3**（条件） | 语义对齐 — Requirements 能否支撑 Picture | PASS / FAIL / UNCERTAIN |

**Tier 3 语义约束**：证据不足时必须返回 **UNCERTAIN**，不得强行 PASS。

---

## 6. Judge Agent 调用约定

- 上下文仅含：`task_id` + 系统提示（不含主 Agent 执行历史）
- 从文件系统读取依据，不接收运行时信息
- 只追加写 judge.md，不修改其他文件

---

## 7. VERIFYING 超时

- 默认：180 秒
- 超时处理：强制结束 Judge、写入 `Verdict: TIMEOUT`、恢复为 IN_PROGRESS

---

## 8. 主 Agent 决策速查

| Judge 结论 | 可选决策 |
|-----------|---------|
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
| judge.md | Judge Agent | 追加，不修改历史 |
| verify.md | 主 Agent | 追加；`[.] / (.) / {.}` 条目可作为执行依据，`[] / () / {}` 仅作记录；已完成条目（`[\✓]` / `(\✓)` / `{\✓}`）不可 amend |

**写入权限语义**：
- **主 Agent** 对 task.md 只有一次写入权（创建时），之后不可修改认知三要素
- **Judge Agent** 对 judge.md 追加，不读取 runtime 内存状态（隔离验证）

---

## 11. 文件语义（详述）

### task.md — 任务声明

语义权威表面。包含：

- **id**：任务标识符（目录名为 source of truth）
- **status**：当前生命周期阶段
- **cognitive_triad**：认知三要素
  - **picture**：语义成功状态（任务完成时看起来是什么样的）
  - **requirements**：可验证条件列表（验证方式定义在 verify.md）
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

### judge.md — 检验报告

Judge Agent 追加的验证表面。

### verify.md — 验证定义

主 Agent 追加写的验证条目集合。包含所有 Requirement 和 Constraint 的验证方式定义。

**三状态转移规则**：

```
未确认 → 确认：人机对话确认验证方式 → [.] / (.) / {.}
确认 → 已完成：验证执行（pass/skip/fail）→ [\✓] / (\✓) / {\✓}
已完成后不可逆向转移
```

**状态约束**：

| 状态 | marker | 可 amend？ |
|------|--------|-----------|
| 未确认 | `[]` / `()` / `{}` | ✅ |
| 确认 | `[.]` / `(.)` / `{.}` | ✅（执行前） |
| 已完成 | `[\✓]` / `(\✓)` / `{\✓}` | ❌ |

### /cap amend 命令

在任意时刻发起对 verify.md 的修正。

**交互流程**：

```
/cap amend
  → 展示当前 verify.md 状态（未确认 + 确认 + 已完成）
  → TUI 询问：「更新现有 marker」还是「新增 marker」
  → 用户指定要修正的条目（仅限未确认 + 确认）
  → 用户提供新内容
  → 确认写入
  → session.md 记录此次 amend
```

**约束**：

- 已完成条目（`[\✓]` / `(\✓)` / `{\✓}`）不可 amend，提示「已完成」
- amend 记录追加到 session.md（可审计）
