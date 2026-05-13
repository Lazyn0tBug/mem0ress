---
description: "Session History — 记录任务执行过程中每个 Turn 的状态快照，按条目追加不覆盖"
type: session
fields:
  turn:
    type: string
    description: "Turn 编号，格式 {N}.{M}，N 为主 Agent 开始新的独立执行阶段时的阶段号，M 为当前 Todo 的会话轮次序号"
  timestamp:
    type: string
    description: "ISO 8601 时间戳"
  todos:
    type: list[object]
    description: "Todo 状态列表"
    children:
      id:
        type: string
        description: "Todo ID，与 task.md 中的 todos[].id 对应"
      text:
        type: string
        description: "动作描述"
      done:
        type: boolean
        description: "完成状态"
  status:
    type: enum
    description: "任务生命周期状态"
    values: [CREATED, IN_PROGRESS, COMPLETED, ABANDONED]
    note: "VERIFYING 为检验瞬态，不属于生命周期状态，不记录于 Session"
  outcome:
    type: object
    description: "本轮执行的实际结果"
    children:
      status:
        type: enum
        description: "结果状态：success | partial | failed"
        values: [success, partial, failed]
      note:
        type: string
        description: "结果说明，例如 partial 时说明哪些部分未完成"
  evidence:
    type: list[object]
    description: "本轮涉及的事实性证据，支持 Judge 检验时定位具体证据"
    children:
      type:
        type: enum
        description: "证据类型"
        values: [code, test, screenshot, log, artifact, config, other]
      ref:
        type: string
        description: "证据引用路径或标识符"
      purpose:
        type: string
        description: "该证据证明了什么（例如：verify_google_login、implement_oauth_callback）"
  workspace_snapshot:
    type: object
    description: "工作区快照，用于回溯"
    children:
      commit_id:
        type: string
        description: "Git commit hash"
      note:
        type: string
        description: "可选：本轮简要说明"
---

# Session History

## Turn: {N,M}
**Timestamp:** YYYY-MM-DDTHH:mm:ssZ

todos:
  - {id: "T-1", text: "...", done: true|false}

status: {CREATED|IN_PROGRESS|COMPLETED|ABANDONED}

---

**Action Summary:** [简述本轮次 Agent 执行的主要动作]

### Outcome
```
outcome:
  status: success | partial | failed
  note: [说明]
```

### Evidence（结构化证据）
```
evidence:
  - type: code
    ref: "src/auth/google_router.ts"
    purpose: "implement_google_oauth"
  - type: test
    ref: "tests/google_oauth.test.ts"
    purpose: "verify_google_login"
  - type: screenshot
    ref: "artifacts/google_login_success.png"
    purpose: "verify_ui_flow"
```

### Workspace Snapshot
```
workspace_snapshot:
  commit_id: "[git_commit_hash]"
  note: "[可选：本轮简要说明]"
```

---

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `todos` | list | `{id, text, done}` 结构，id 对应 task.md 中的 todos[].id |
| `status` | enum | CREATED / IN_PROGRESS / COMPLETED / ABANDONED（VERIFYING 为检验瞬态，不属于生命周期状态，不记录于 Session） |
| `outcome` | object | 描述本轮执行的实际结果，Judge 语义的关键字段 |
| `evidence` | list | 结构化证据列表，替代原有的 `active_refs`；每个证据含 type/ref/purpose，purpose 绑定到 Picture Claim |
| `workspace_snapshot` | object | 工作区快照，记录 commit_id 供回溯 |

**写入约定：**
- Turn 编号格式为 `{N}.{M}`：N = 阶段号（主 Agent 开始新的独立执行阶段时递增），M = 当前 Todo 的会话轮次序号（从 1 开始，同一 Todo 内的重试/修正累加）
- 每轮次结束时**追加**写入，不覆盖历史快照（版本快照模型）
- **不记录 Picture / Requirements / Constraints**（这些从 task.md 获取，不重复记录）
- `evidence[].purpose` 必须与 Picture 维度对应，供 Judge 建立 Picture Claim → Evidence 映射

**触发时机：** 每轮次结束时追加状态快照。
