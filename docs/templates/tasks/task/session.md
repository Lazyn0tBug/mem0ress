# Session: {task_id}

## Turn {N.M}
date: {YYYY-MM-DDTHH:MM:SS}
code_progress: "{本轮代码产出摘要}"
data_plane:
  {repository}: {commit_id}
todos:
  - {text: "...", done: true|false}
status: {CREATED|IN_PROGRESS}

---

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `code_progress` | string | 本轮次代码产出摘要，描述性文本 |
| `data_plane` | map | 仓库名 → commit ID 映射（每个 Turn 的快照，用于回溯） |
| `todos` | list | `{text, done}` 结构，done 为 boolean |
| `status` | enum | CREATED / IN_PROGRESS / COMPLETED / ABANDONED（VERIFYING 为检验瞬态，不属于生命周期状态，不记录于 Session） |

**写入约定：**
- Turn 编号格式为 `{parent_turn}.{child_turn}`，如 1.1、1.2、2.1，体现嵌套关系
- 每轮次结束时**追加**写入，不覆盖历史快照（版本快照模型）
- **不记录 Picture / Requirements / Constraints**（这些从 task.md 获取，不重复记录）
- `data_plane` 字段记录本轮次操作时的 commit ID 快照，供回溯使用

**触发时机：** 每轮次结束时追加状态快照。
