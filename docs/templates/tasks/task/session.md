---
description: "Session History — 记录任务执行过程中每个 Turn 的状态快照，按条目追加不覆盖"
type: session
relationships:
  requires: ["task.md", "data_plane.md"]
  provides: []
fields:
  turn:
    type: string
    description: "Turn 编号，格式 N.M，N 为 todo 序列号，M 为子序号，如 1.1、1.2"
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
  data_plane:
    type: object
    description: "数据平面快照，见 data_plane.md"
    children:
      commit_id:
        type: string
        description: "Git commit hash"
      active_refs:
        type: list[string]
        description: "本轮涉及的文件路径列表"
      note:
        type: string
        description: "可选：本轮简要说明"
---

# Session History

## Turn: {N,M}
**Timestamp:** YYYY-MM-DDTHH:mm:ssZ
todos:
  - {id: "T-1", text: "...", done: true|false}
status: {CREATED|IN_PROGRESS}

---

**Action Summary:** [简述本轮次 Agent 执行的主要动作，例如：完成了 Google OAuth 路由的搭建。]

### 状态快照 (Status Snapshot)
- **Code Progress:** [简述代码层面的推进情况]
- **Docs Progress:** [简述文档层面的推进情况]
- **Todos Status:** [已完成 Todo 的标记状态，例如 1/2]
- **Task Status:** IN_PROGRESS

### 数据平面快照 (Data Plane)
- **Commit ID:** `[git_commit_hash]`
- **Active References:**
  - `ref:src/auth/google_router.ts`

---

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `todos` | list | `{id, text, done}` 结构，id 对应 task.md 中的 todos[].id |
| `status` | enum | CREATED / IN_PROGRESS / COMPLETED / ABANDONED（VERIFYING 为检验瞬态，不属于生命周期状态，不记录于 Session） |

**写入约定：**
- Turn 编号格式为 `{parent_turn}.{child_turn}`，N为todo的序列号， 如 1.1、1.2、2.1，体现嵌套关系
- 每轮次结束时**追加**写入，不覆盖历史快照（版本快照模型）
- **不记录 Picture / Requirements / Constraints**（这些从 task.md 获取，不重复记录）
- `data_plane` 字段记录本轮次操作时的 commit ID 快照，供回溯使用
- Data Plane 模板结构见 `data_plane.md`

**触发时机：** 每轮次结束时追加状态快照。
