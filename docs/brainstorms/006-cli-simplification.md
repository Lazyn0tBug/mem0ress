---
date: 2026-05-16
topic: cli-commands-simplification
---

# CLI 命令简化与 .task_info 设计

## Context

当前 mem0ress CLI 存在命令设计不一致：部分命令（`update/judge/close/done`）已经从 `.current_task` 隐式读取 task_id，但 `abandon` 和 `report` 仍然强制要求显式传入。此外，缺少 `list` 命令供用户在 TUI 中通过编号选择任务。

本次改动解决三个问题：
1. 统一所有命令从 `.task_info` 读取 task_id，简化用户心智负担
2. 新增 `list` 命令，支持编号选择加载任务
3. 用 `.task_info` 替代 `.current_task`，集中管理所有任务状态

## Decisions

### D1. 所有命令统一从 `.task_info` 读取

**结论：** abandon 和 report 改为可选读取（与 update/judge/close/done 一致），CLI 不保留显式 task_id 参数能力。

**理由：**
- 统一交互模型：用户不需要区分"哪些命令可以用 task_id，哪些不行"
- 符合 Skill 语义：slash command 从 .task_info 读取，CLI 作为实现层也应保持一致
- 无实际 escape hatch 需求：Agent/Skill 层已可通过 Python 模块直接调用

**影响范围：**
- `abandon`: `task_id: str` → `task_id: str | None = None`
- `report`: `task_id: str` → `task_id: str | None = None`
- 其他命令（update/judge/close/done）已实现，无需修改

### D2. list 命令设计

**交互逻辑：**

| 状态 | 显示 | 行为 |
|------|------|------|
| 0 个任务 | "No tasks available. Run /cap create first." | 直接退出，exit code 1 |
| 1 个任务 | 显示任务（加粗标注为当前任务） | 自动选中（已是 current_task），退出 |
| N 个任务 (N>1) | 编号列表，current_task_id 对应项加粗标注 | 等待用户选择，输入后更新 current_task_id |

**显示格式（示例）：**

```
  1. ■ 2k5m3x  [in-progress] ← current (activated 2026-05-16)
  2. ■ a3x7br  [created]

Select task number:
```

**当前任务识别：**
- 从 `.task_info` frontmatter读取 `current_task_id`
- 列表中对应项加粗显示，激活时间标注
- list 只显示非 completed、非 abandoned 的任务

**非交互式支持：** 不在 MVP 中实现。

### D3. 放弃 slash command 级联设计

**结论：** 不做 `/cap close` → `/cog close {task_id}` 的级联调用。

**理由：**
- 当前 CLI 已实现完整闭环（隐式读取 + Judge 验证 + 状态更新）
- Skill 直接调用 CLI 模块即可，无需中间层 slash command
- 级联调用无实际价值，增加调试复杂度

### D4. .task_info 任务信息中心

**结论：** 用 `.task_info` 文件替代 `.current_task`，集中存储所有任务信息。

**文件格式（YAML）：**
```yaml
---
current_task_id: "2k5m3x"
---

tasks:
  - task_id: "2k5m3x"
    status: "in-progress"
    path: ".cap/tasks/2k5m3x"
    created_at: "2026-05-14T10:00:00+09:00"
    activated_at: "2026-05-16T10:00:00+09:00"
  - task_id: "a3x7br"
    status: "created"
    path: ".cap/tasks/a3x7br"
    created_at: "2026-05-15T08:00:00+09:00"
    activated_at: null
```

**文件头（frontmatter）：**
- `current_task_id`: 当前活动的任务 ID

**任务列表（tasks）：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 任务标识符 |
| `status` | string | 任务状态（created/in-progress/verifying/completed/abandoned） |
| `path` | string | 任务目录相对路径（支持子任务：`.cap/tasks/{parent_id}/{task_id}`） |
| `created_at` | string | 任务创建时间（ISO8601） |
| `activated_at` | string/null | 最后一次激活为当前任务的时间，null 表示从未激活 |

**更新时机（事务性保证）：**
- `create`: 添加新任务到 tasks 列表，current_task_id 更新
- `abandon/close/done`: 更新对应任务的 status，两处同时更新（task.md + .task_info）
- `update`: 不更新 .task_info（session 是瞬态数据）
- `list`: 仅读取 .task_info，快速过滤

**设计优势：**
- list 命令只需读一个文件，无需扫描 filesystem
- 所有任务状态集中管理
- list 自动过滤 completed/abandoned 任务
- activated_at 非空的任务标注为当前任务

**向后兼容：** 不需要

## Requirements

### R1. abandon 命令改为可选 task_id，同时清空 current_task_id

**文件：** `src/mem0ress/cli.py`

**修改：**
```python
def abandon(
    task_id: str | None = None,  # 原: task_id: str
    root: str = typer.Option(DEFAULT_SUBSTRATE_ROOT, ...),
) -> None:
    # 解析逻辑：从 .task_info 读取 current_task_id
    task_info = TaskInfoManager(substrate_root=substrate_root)
    if task_id is None:
        task_id = task_info.get_current_task_id()
        if task_id is None:
            console.print("[red]No active task.[/red] Create a task first.")
            raise typer.Exit(code=1)
    # ... 执行 abandon ...
    # abandon 后更新 .task_info：current_task_id 设为空（或下一个激活的任务）
    task_info.update_task_status(task_id, "abandoned")
```

### R2. report 命令改为可选 task_id

**文件：** `src/mem0ress/cli.py`

**修改逻辑同 R1。**

### R3. 新增 list 命令

**文件：** `src/mem0ress/cli.py`

**功能：**
- 读取 `.task_info` 获取所有任务
- 过滤 completed/abandoned 任务
- 显示编号列表，current_task_id 对应项加粗标注
- 支持交互式编号选择（1/2/3/...）
- 输入后更新 `current_task_id` 为选中任务

**退出码：**
- 成功选择：0
- 无任务（0 个）：1
- 用户中断（Ctrl+C）：0

### R4. .task_info 文件管理

**文件：** `src/mem0ress/gateway/task_info.py`（新建）

**功能：**
- `TaskInfoManager` 类管理 `.task_info` 文件
- `read()`: 读取整个 .task_info 文件，返回结构化数据
- `write()`: 写入 .task_info 文件（乐观锁保护）
- `add_task()`: 添加新任务
- `update_task_status()`: 更新任务状态
- `set_current_task()`: 设置当前任务（更新 current_task_id + activated_at）
- `get_current_task_id()`: 获取当前任务 ID

### R5. 事务性保证

**文件：** `src/mem0ress/gateway/actions.py`

**修改：**
- abandon/close/done 操作时，同时更新 task.md 和 .task_info
- 使用文件系统乐观锁保证一致性

## Scope Boundaries

- **不实现:** list 命令的非交互式 `--select` 选项
- **不实现:** slash command 级联调用设计
- **不实现:** 任务过滤/搜索功能
- **不实现:** 旧 `.current_task` 文件迁移

## Success Criteria

- [ ] `mem0 abandon` 无参数时从 `.task_info` 读取，行为与 `mem0 update` 一致
- [ ] `mem0 report` 无参数时从 `.task_info` 读取，行为与 `mem0 judge` 一致
- [ ] `mem0 list` 在 0 任务时提示并退出
- [ ] `mem0 list` 在 1 任务时显示并自动选中（已是 current）
- [ ] `mem0 list` 在 N>1 任务时显示编号列表，用户选择后更新 current_task_id
- [ ] `mem0 list` 自动过滤 completed/abandoned 任务
- [ ] 当前任务在 list 中加粗标注
- [ ] 所有命令通过 `ty check` 和 `ruff check`

## Files to Modify

| File | Change |
|------|--------|
| `src/mem0ress/cli.py` | abandon/report 改为可选；新增 list 命令 |
| `src/mem0ress/gateway/task_info.py` | NEW — TaskInfoManager 管理 .task_info |
| `src/mem0ress/gateway/actions.py` | 事务性保证：abandon/close/done 同时更新 task.md + .task_info |
| `src/mem0ress/gateway/current_task.py` | DEPRECATED — 保留但不使用（未来删除）|

## Dependencies

- `PlaneAssembler`: 用于 status 命令
- `TaskServiceImpl`: 用于任务操作
- `safe_write`: 乐观锁文件系统操作

## Related Documents

- `docs/spec.md` — 接口语义规范
- `src/mem0ress/design.md` — 实施方案
- `docs/brainstorms/2026-05-13-001-mem0ress-skill-design.md` — Skill 设计

## Next Steps

→ `/ce:plan` for structured implementation planning