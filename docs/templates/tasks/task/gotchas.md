---
description: "Gotcha 记录 — 任务执行过程中的认知偏差与经验记录，按条目追加"
type: gotcha
relationships:
  requires: ["task.md", "session.md"]
  provides: []
fields:
  title:
    type: string
    description: "偏差或经验的简短标题"
  timestamp:
    type: string
    description: "ISO 8601 时间戳"
  turn_reference:
    type: string
    description: "关联的 Session Turn，如 1.2"
  context:
    type: string
    description: "触发背景：执行哪个 Todo 或验证哪个 Requirement 时发生的问题"
  deviation:
    type: string
    description: "偏差与冲突事实：实际发生的问题描述"
  resolution:
    type: string
    description: "认知修正与妥协：最终的决定、执行路径变更或 Requirements 修改"
---

# Gotchas (认知偏差与经验记录)

## 💡 Gotcha: [偏差或经验的简短标题]
**Timestamp:** YYYY-MM-DDTHH:mm:ssZ
**Turn Reference:** [关联的 Session 轮次，如 Turn 1.2]

### 1. 触发背景 (Context)
[描述是在执行哪个 Todo 或验证哪个 Requirement 时发生的问题。]

### 2. 偏差与冲突事实 (Deviation/Issue)
[描述实际发生的问题。例如：发现由于跨域策略限制，原定的前后端分离 Auth 方案无法在当前基础设施下直接工作。]

### 3. 认知修正与妥协 (Resolution/Compromise)
[描述最终的决定。是修改了执行路径？还是让度给人？或是修改了 Requirements？例如：决定引入 Nginx 代理层解决 CORS 问题，并追加了相应的子任务。]
