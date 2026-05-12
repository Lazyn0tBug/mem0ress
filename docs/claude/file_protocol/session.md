---
task_id: "{task_id}"
type: session
---

# Session History — {task_id}

> 每轮次结束时追加写入，不覆盖历史快照。
> 不记录 Picture / Requirements / Constraints（从 task.md 获取）。
>
> **Turn 编号规则：** `{主轮次}.{子轮次}`
> 主轮次在主 Agent 开始一个新的独立执行阶段时递增；
> 子轮次在同一阶段内的迭代中递增（如重试、修正）。
> Turn 编号与 Todo 序号解耦，一个 Turn 可以推进多个 Todo。

---

## Turn {N.M}
**Timestamp:** YYYY-MM-DDTHH:mm:ssZ
**Status:** {CREATED | IN_PROGRESS | COMPLETED | ABANDONED}

**Action Summary:**
{简述本轮主 Agent 执行的主要动作。}

### Todos
- [x] T-1: {已完成的 Todo 描述}
- [ ] T-2: {未完成的 Todo 描述}

### Code Progress
{代码层面的推进情况。写发生了什么，不写计划。}

### Docs Progress
{文档层面的推进情况，无则写"—"。}

### Data Plane
- **Commit ID:** `{git_commit_hash}`
- **Active Refs:**
  - `{src/path/to/changed_file.ts}`
  - `{src/path/to/another_file.py}`

### Constraint Violations
{本轮是否检测到约束违反。无则写"—"。有则列出，自动触发 Gotcha 追加。}

---
