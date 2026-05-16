---
title: "feat: CLI simplification — .task_info + optional task_id + list command"
type: feat
status: active
date: 2026-05-16
origin: docs/brainstorms/006-cli-simplification.md
---

# CLI Simplification: .task_info + Optional task_id + list Command

## Overview

统一所有 CLI 命令从 `.task_info` 读取 task_id，新增 `list` 命令支持交互式编号选择任务，并用 `.task_info` 文件替代 `.current_task` 集中管理所有任务状态。

## Problem Frame

当前 `abandon` 和 `report` 命令强制要求 `task_id` 参数，与 `update`/`judge`/`close`/`done` 的隐式读取行为不一致。

此外，缺少 `list` 命令，用户无法在 TUI 中通过编号选择任务，只能靠记忆 task_id。

当前 `.current_task` 只存储当前任务，list 需要扫描整个 filesystem。

## Requirements Trace

- **R1**: `mem0 abandon` 无参数时从 `.task_info` 读取，abandon 后更新 .task_info 中的 status
- **R2**: `mem0 report` 无参数时从 `.task_info` 读取
- **R3**: `mem0 list` 在 0 任务时提示并退出（exit code 1）
- **R4**: `mem0 list` 在 1 任务时显示并自动选中（已是 current），退出（exit code 0）
- **R5**: `mem0 list` 在 N>1 任务时显示编号列表，用户选择后更新 current_task_id
- **R6**: list 只显示非 completed、非 abandoned 的任务
- **R7**: 当前任务在 list 中加粗标注
- **R8**: .task_info 文件集中管理所有任务信息（task_id/status/path/created_at/activated_at）
- **R9**: abandon/close/done 操作时同时更新 task.md 和 .task_info（事务性保证）

## Scope Boundaries

- **不实现**: list 命令的 `--select` 非交互式选项
- **不实现**: 任务过滤/搜索功能
- **不实现**: CLI 保留显式 task_id 参数作为 escape hatch（遵循 brainstorm 决策）
- **不实现**: 旧 `.current_task` 文件迁移
- **不实现**: 旧 `.task_info` 格式迁移

## Context & Research

### .task_info 文件格式

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

### 关键设计点

1. **文件头**: 仅存 `current_task_id`（避免重复）
2. **任务列表**: YAML 格式，存储所有任务信息
3. **更新时机**:
   - `create`: 添加任务到 tasks，current_task_id 指向新任务
   - `abandon/close/done`: 更新 task status（两处同时更新）
   - `update`: 不更新 .task_info（session 是瞬态）
   - `list`: 仅读取 .task_info

### Existing Patterns

- **CurrentTaskManager**: 已有 read/write 方法，需迁移到 TaskInfoManager
- **TaskServiceImpl**: abandon_task/close_task 使用 SubstrateParser + safe_write
- **safe_write**: 乐观锁保护，用于事务性保证

## Key Technical Decisions

- **YAML 格式**: .task_info 使用纯 YAML（不是 Markdown），便于机器读写
- **集中管理**: 所有任务状态存在 .task_info，list 无需扫描 filesystem
- **事务性**: abandon/close/done 同时更新 task.md + .task_info，使用 safe_write 乐观锁

## Implementation Units

- [ ] **Unit 1: Create TaskInfoManager class**

**Goal:** 新建 `TaskInfoManager` 管理 `.task_info` 文件

**Requirements:** R8

**Dependencies:** 无

**Files:**
- Create: `src/mem0ress/gateway/task_info.py`

**Approach:**
1. `TaskInfoManager` 类管理 .task_info 文件读写
2. `read()`: 读取 YAML，返回 (current_task_id, tasks list)
3. `write()`: 写入 YAML（乐观锁保护）
4. `add_task(task_id, path, created_at)`: 添加新任务，current_task_id 指向它
5. `update_task_status(task_id, status)`: 更新任务状态
6. `set_current_task(task_id)`: 设置当前任务（更新 current_task_id + activated_at）
7. `get_current_task_id()`: 获取当前任务 ID
8. `get_active_tasks()`: 获取非 completed/abandoned 的任务列表

**Patterns to follow:**
- `CurrentTaskManager` 的 read/write 模式（safe_write + get_file_hash）

**Test scenarios:**
- Happy path: create -> read -> returns correct current_task_id
- Happy path: add_task -> tasks list contains new task
- Edge case: .task_info doesn't exist -> returns empty state
- Edge case: invalid YAML -> raises error

**Verification:**
- `ty check src/mem0ress/gateway/task_info.py` 通过
- `ruff check src/mem0ress/gateway/task_info.py` 通过

---

- [ ] **Unit 2: Update create command to use .task_info**

**Goal:** create 命令创建任务时同时更新 .task_info

**Requirements:** R8

**Dependencies:** Unit 1

**Files:**
- Modify: `src/mem0ress/cli.py`

**Approach:**
1. create 命令在创建 task.md 后，调用 `task_info.add_task(task_id, path, created_at)`
2. created_at 使用当前时间
3. path 计算为 `{substrate_root}/tasks/{task_id}`

**Verification:**
- `mem0 create` 后 .task_info 包含新任务
- current_task_id 指向新任务

---

- [ ] **Unit 3: Make abandon task_id optional + update .task_info**

**Goal:** `mem0 abandon` 无参数时从 .task_info 读取，abandon 后更新 task status

**Requirements:** R1, R9

**Dependencies:** Unit 1

**Files:**
- Modify: `src/mem0ress/cli.py`
- Modify: `src/mem0ress/gateway/actions.py`（更新事务性逻辑）

**Approach:**
1. 将 `task_id: str` 改为 `task_id: str | None = None`
2. 从 `task_info.get_current_task_id()` 获取当前任务
3. abandon 后调用 `task_info.update_task_status(task_id, "abandoned")`
4. 同时更新 task.md（原有逻辑）

**Patterns to follow:**
- abandon_task 内部使用 SubstrateParser + safe_write

**Test scenarios:**
- Happy path: abandon with no active task -> error
- Happy path: abandon with active task -> task.md updated + .task_info updated
- Edge case: task_id doesn't exist in .task_info -> error

**Verification:**
- `ty check src/mem0ress/cli.py` 通过
- `ruff check src/mem0ress/cli.py` 通过

---

- [ ] **Unit 4: Make report task_id optional**

**Goal:** `mem0 report` 无参数时从 .task_info 读取

**Requirements:** R2

**Dependencies:** Unit 1

**Files:**
- Modify: `src/mem0ress/cli.py`

**Approach:**
1. 将 `task_id: str` 改为 `task_id: str | None = None`
2. 从 `task_info.get_current_task_id()` 获取当前任务
3. 其余逻辑保持不变

**Test scenarios:**
- Happy path: report with no active task -> error
- Happy path: report with active task -> shows report

**Verification:**
- `ty check src/mem0ress/cli.py` 通过
- `ruff check src/mem0ress/cli.py` 通过

---

- [ ] **Unit 5: Add list command**

**Goal:** `mem0 list` 显示任务列表，支持交互式编号选择并更新 current_task_id

**Requirements:** R3, R4, R5, R6, R7

**Dependencies:** Unit 1

**Files:**
- Modify: `src/mem0ress/cli.py`

**Approach:**
1. 调用 `task_info.get_active_tasks()` 获取非 completed/abandoned 任务
2. 从 `task_info.get_current_task_id()` 获取当前任务
3. 显示格式：
   ```
     1. ■ 2k5m3x  [in-progress] ← current (activated 2026-05-16)
     2. ■ a3x7br  [created]

   Select task number:
   ```
4. 交互逻辑：
   - 0 个任务：打印 "No tasks available. Run 'mem0 create' first."，exit code 1
   - 1 个任务：打印任务，如果是 current 直接退出，否则调用 `set_current_task()` 并退出（exit code 0）
   - N>1 个任务：打印列表，提示 "Select task number:"，读取输入，调用 `set_current_task()`（exit code 0）
5. 输入验证：非数字输入提示重试，范围外输入提示重试，Ctrl+C 干净退出

**Patterns to follow:**
- `Console.input()` 用于交互式输入

**Test scenarios:**
- Edge case: 0 active tasks -> "No tasks available" message, exit code 1
- Happy path: 1 task that is current -> displays, exits immediately
- Happy path: 1 task that is not current -> displays, selects it, exits
- Happy path: N>1 tasks -> displays numbered list, accepts valid selection, updates current_task_id
- Edge case: Invalid input (non-numeric) -> "Invalid input" message, retries
- Edge case: Out-of-range selection -> "Invalid selection" message, retries
- Edge case: Ctrl+C -> exits cleanly

**Verification:**
- `ty check src/mem0ress/cli.py` 通过
- `ruff check src/mem0ress/cli.py` 通过

---

- [ ] **Unit 6: Update close/done to use .task_info**

**Goal:** close/done 命令也更新 .task_info，保持一致性

**Requirements:** R9

**Dependencies:** Unit 1

**Files:**
- Modify: `src/mem0ress/gateway/actions.py`

**Approach:**
1. close_task / done 执行成功后，调用 `task_info.update_task_status(task_id, "completed")`
2. 同时更新 current_task_id 为空（或下一个激活的任务）

**Verification:**
- close/done 后 .task_info 中对应任务 status 为 completed

---

- [ ] **Unit 7: Add unit tests for TaskInfoManager**

**Goal:** 确保 TaskInfoManager 有完整的测试覆盖

**Requirements:** R8

**Dependencies:** Unit 1

**Files:**
- Create: `tests/unit/test_task_info.py`

**Test scenarios:**
- Happy path: add_task -> read returns correct data
- Happy path: update_task_status -> status changes
- Happy path: set_current_task -> current_task_id + activated_at updated
- Happy path: get_active_tasks -> filters completed/abandoned
- Edge case: empty file -> returns default state
- Edge case: missing task -> update returns error
- Edge case: concurrent write -> ConflictError

**Verification:**
- `pytest tests/unit/test_task_info.py -v` 通过

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| .task_info 与 task.md 状态不一致 | 使用 safe_write 乐观锁，操作失败时回滚 |
| list 命令过滤逻辑遗漏 | Unit 7 测试覆盖 |
| 向后兼容（旧 .current_task） | 不支持，明确在 scope 外 |

## Documentation / Operational Notes

- `docs/spec.md` 和 `src/mem0ress/design.md` 中关于 .current_task 的描述需更新为 .task_info
- CLI help text (`docstring`) 需同步更新

## Sources & References

- **Origin document:** [docs/brainstorms/006-cli-simplification.md](docs/brainstorms/006-cli-simplification.md)
- Related code: `src/mem0ress/cli.py`, `src/mem0ress/gateway/current_task.py`
- Related plan: [docs/plans/2026-05-14-001-feat-cog-skill-implementation-plan.md](docs/plans/2026-05-14-001-feat-cog-skill-implementation-plan.md)