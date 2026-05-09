---
id: {task_id}
type: task
status: created
cognitive_triad:
  picture: {描述任务完成后的终极成功状态}
  requirements: []
  constraints: []
todos:
  - [ ] {第一步}
---
# {task_id}

## Picture
{picture}

## Requirements
- ...

## Constraints
- ...

## Todos
- [ ] ...

> **模板参考：** Session 模板见 `docs/templates/tasks/task/session.md`，Gotcha 模板见 `docs/templates/tasks/task/gotchas.md`。
>
> **双重格式说明：** task.md 存在两种等价的语义表达方式。Frontmatter 中的 `cognitive_triad` 字段（YAML 格式）是机器可解析的标准格式，供 mem0ress 内部 API 读取；Body 中的 `## Picture / ## Requirements / ## Constraints` 是人类可读的展示格式，供 Agent 和利益相关者直接查阅。两者内容必须完全一致——Agent 写入 body 后必须同步更新 frontmatter，或由工具自动维护一致性。
