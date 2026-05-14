---
title: "feat: Implement cog Skill and unified CLI naming"
type: feat
status: active
date: 2026-05-14
origin: docs/brainstorms/2026-05-13-001-mem0ress-skill-design.md
---

# cog Skill 实现 + CLI 统一命名

## Overview

统一产品命名为 `cog`，实现 Claude Code Skill 调用层，同时修复 CLI `create` 命令的底层实现问题。Skill 通过 shell 调用 CLI，CLI 是实际的执行者。

## Problem Frame

mem0ress MVP 的 CLI 已完整，但存在两个问题：

1. **CLI 命名不一致**：CLI 名称是 `mem0`，Skill 触发器是 `/mem0ress`（文档），实际应为 `/cog`
2. **CLI `create` 命令实现有缺陷**：直接写 `TEMPLATE_INDEX` 字符串，与 `SubstrateParser.serialize_manifest()` 格式不兼容，导致创建的任务无法被 `TaskServiceImpl.get_task()` 正确解析

同时，设计文档要求的 `.current_task` 指针管理、6 位 task_id 自动生成均未实现。

## Requirements Trace

- R1. Skill 文件名为 `cog.md`，放置于 `~/.claude/skills/cog.md`
- R2. Skill 使用 YAML frontmatter + Markdown 正文格式
- R3. Skill 触发器：`/cog create`、`/cog update`、`/cog judge`、`/cog close`
- R4. CLI 命令格式：`cog create`（子命令），与 Skill 命名对齐
- R5. `/cog create` 创建任务，自动生成 task_id，写入 `task.md` + 初始化辅助文件，更新 `.current_task`
- R8. `/cog close` 原子操作：先 judge，全部 PASS 才标记 COMPLETED
- R9. task_id 自动生成 6 位 ID（例如 `2k5m3x`）
- R10. 算法：`{base36_timestamp_low}{random_alphanumeric}` = 取时间戳低 4 位 base36 + 2 位随机
- R12. 每次 create 后写入 `.current_task`
- R15. close 后清空 `.current_task` 的 task_id
- R21. judge 输出纯文本（非 Rich ANSI）
- R24. `.current_task` 格式为 YAML，含 `task_id`（可选字串）和 `activated_at`（ISO8601 字串）

## Scope Boundaries

- 不实现：`skills/` 目录于 repo 内（Skill 文件属于用户级配置）
- 不实现：abandon/status/report 命令
- 不实现：Tier 2 verify_cmd 真实 shell 执行（MVP 为 stub）
- 不实现：PRC 迭代补全（R18-R20 由 Hermes 负责，Skill 接收完整参数）
- 不实现：PRC 更新（`update_cognitive_triad` CLI 命令暴露，纳入 v0.2）

## Key Technical Decisions

- **CLI 命名分两步迁移**：第一步实现 Skill（`/cog create/update/judge/close`），CLI 命令暂保持 `mem0`；第二步将 CLI 改名为 `cog`，彻底统一。分步降低破坏性，避免同时更新 Skill 和 CLI 导致调试困难
- **TaskServiceImpl 是真实执行者**：Skill 通过 `cog create --picture X --requirements Y --constraints Z` 调用 CLI，CLI 委托 TaskServiceImpl 执行
- **`.current_task` 是 CLI 的职责**：CLI create/update/close 命令负责维护 `.current_task`，Skill 不直接操作文件系统
- **task_id 生成算法**：取 Unix 时间戳低 4 位 base36 + monotonic counter 2 位 base36，合计 6 位（如 `2k5m3x`）。Counter 保证同一进程内连续创建不碰撞；时间戳提供跨进程区分
- **Tier 2 stub 返回 auto-PASS**：当 requirement 的 `verify_cmd` 为 `None` 或空时，该 tier 视为自动满足（PASS），不阻塞 close。简化 MVP 语义，Tier 2 真实执行纳入 v0.2

## Context & Research

### Relevant Code and Patterns

- **CLI 入口**：`src/mem0ress/cli.py` — typer app，当前 `name="mem0"`，包含 `create`/`update`/`judge`/`close`/`done`/`abandon`/`status`/`report` 命令
- **TaskServiceImpl**：`src/mem0ress/gateway/actions.py` — 包含 `create_task()`/`update_session()`/`judge_task()`/`close_task()` 等方法，所有写操作使用 `SubstrateParser.serialize_manifest()`
- **SubstrateParser**：`src/mem0ress/substrate/parser.py` — `parse_manifest()` 和 `serialize_manifest()` 实现 Markdown ↔ Pydantic 双向转换
- **Schema**：`src/mem0ress/core/schema.py` — `TaskManifest`/`TaskStatus`/`CognitiveTriad`/`Requirement` 等 Pydantic 模型
- **SafeWrite**：`src/mem0ress/substrate/fs.py` — `safe_write()` 实现乐观锁
- **HarnessRunner**：`src/mem0ress/harness/__init__.py` — Tier 0/1/2 验证执行器

### Existing Patterns

- CLI 命令通过 `typer` 定义，使用 `@app.command()` 装饰器
- 所有公共函数有完整类型注解，`ty check src/` 强制检查
- 异常命名使用 `{Domain}{Error}` 模式（如 `TaskExistsError`）
- 文件路径使用 `Path` 类型，编码始终为 `utf-8`
- 测试使用 `pytest`，临时目录用 `tmp_path` fixture

## Implementation Units

- [ ] **Unit 1: 创建 `cog.md` Skill 文件（CLI 暂保持 `mem0`）**

**Goal:** 创建 Claude Code Skill 文件，暴露 `/cog create/update/judge/close` 四个触发器。CLI 保持 `mem0` 命令不变，Skill 通过 shell 调用 `mem0 ...` CLI。此步不修改 CLI 命名。

**Requirements:** R1, R2, R3, R5, R6, R7, R8, R21, R22, R23

**Dependencies:** 无（Skill 调用现有 CLI，无需先改 CLI）

**Files:**
- Create: `skills/cog.md`（repo 内参考实现：`docs/skills/cog.md` 作为文档化；实际用户级安装文件为 `~/.claude/skills/cog.md`）

**Approach:**
- SKILL.md 格式：YAML frontmatter + Markdown 正文
- `name: cog`，`description: Cognitive alignment plane for AI agents`
- `triggers`：`/cog create`、`/cog update`、`/cog judge`、`/cog close`
- Skill 通过 shell 执行 CLI：`!cog create --picture ...`（Step 1 时仍调用 `mem0`）
- 各命令的 Skill 描述、参数格式、输出格式
- Skill 文件放在 `docs/skills/cog.md` 作为参考实现，真实安装到 `~/.claude/skills/cog.md`

**Skill 文件结构：**
```markdown
---
name: cog
description: Cognitive alignment plane for AI agents. Track tasks, verify progress, maintain cognitive context across turns.
triggers:
  - /cog create
  - /cog update
  - /cog judge
  - /cog close
---

# cog Skill
...
```

**Patterns to follow:**
- Claude Code SKILL.md 格式（参考 `~/.claude/skills/` 下其他 skill 文件的结构）
- YAML frontmatter：`name`、`description`、`triggers` 三个必需字段

**Test scenarios:**
- Skill file 的 YAML frontmatter 格式正确（可通过 Python `yaml.safe_load()` 验证）
- `triggers` 列表包含全部 4 个命令
- Skill 文件名和内部 `name` 一致（`cog`）

**Verification:**
- `python -c "import yaml; yaml.safe_load(open('docs/skills/cog.md'))"` 无报错

---

- [ ] **Unit 2: task_id 自动生成算法**

**Goal:** 实现 6 位 task_id 生成算法：时间戳低 4 位 base36 + monotonic counter 2 位 base36

**Requirements:** R9, R10, R11

**Dependencies:** 无（独立工具模块）

**Files:**
- Create: `src/mem0ress/core/id_gen.py`

**Approach:**
- 独立 `generate_task_id() -> str` 函数
- 取 `int(time.time() // 64)` 的低 4 位 base36 编码（64 秒粒度，覆盖约 12 天范围）
- 拼接 2 位 base36 monotonic counter（`itertools.count`，取模 36²）
- 同一进程内 counter 保证连续调用不碰撞；时间戳提供跨进程区分
- 文件格式：纯 6 位字串，无分隔符（如 `2k5m3x`）

**Technical design:**
```python
import time, itertools

_BASE36 = "0123456789abcdefghijklmnopqrstuvwxyz"
_COUNTER = itertools.count(start=0)

def _to_base36(value: int, width: int) -> str:
    """Convert integer to base36 string of given width."""
    return ''.join(_BASE36[(value // 36**i) % 36] for i in range(width - 1, -1, -1))

def generate_task_id() -> str:
    ts_low = int(time.time() // 64) % (36**4)  # 4 chars base36
    counter = next(_COUNTER) % (36**2)          # 2 chars base36, wraps
    return _to_base36(ts_low, 4) + _to_base36(counter, 2)
```

**Patterns to follow:**
- `itertools.count` 用于进程内单调递增（确保本地唯一性）
- `secrets` 模块不使用（counter 本身已保证唯一性，不需要随机）

**Test scenarios:**
- Happy path: 连续调用 10 次，生成的 ID 互不相同
- Happy path: 生成的 ID 长度为 6，仅含 base36 字符（`0-9a-z`）
- Edge case: counter 绕回（36² = 1296 次后）仍唯一（时间戳部分已变化）
- Format: 返回值不包含空格、换行或分隔符

**Verification:**
- `pytest tests/unit/test_id_gen.py -v` 全部通过

---

- [ ] **Unit 3: `.current_task` 文件管理**

**Goal:** 实现 `.current_task` 文件的读写管理，供 create/update/close 使用

**Requirements:** R12, R13, R14, R15, R24

**Dependencies:** Unit 2（依赖 id_gen 模块）

**Files:**
- Create: `src/mem0ress/gateway/current_task.py`
- Modify: `src/mem0ress/gateway/actions.py`（集成 CurrentTaskManager）
- Create: `tests/unit/test_current_task.py`

**Approach:**
- `CurrentTaskManager` 类，持有 `substrate_root: Path`
- `read() -> tuple[Optional[str], Optional[str]]`：返回 `(task_id, activated_at)`，文件不存在或格式错误时返回 `(None, None)`
- `write(task_id: str) -> None`：写入 YAML 格式 `task_id: <id>\nactivated_at: <ISO8601>`
- `clear() -> None`：将 `task_id` 置为空字串，`activated_at` 保留（不清空文件）
- `activate_on_create(task_id: str)`：create 命令成功后调用，写入当前时间戳
- `activate_on_close()`：close 命令成功后调用，清空 task_id，保留 activated_at
- 写入使用 `safe_write`（乐观锁）防止并发写冲突
- 文件路径：`.mem0ress/.current_task`

**Patterns to follow:**
- `safe_write` 来自 `substrate/fs.py` 的乐观锁模式
- YAML 格式参考现有 `SubstrateParser.serialize_manifest()` 的序列化风格
- Pydantic 模型不使用（文件格式足够简单，直接操作 dict）

**Test scenarios:**
- Happy path: write + read 返回相同 task_id 和 activated_at
- Edge case: 文件不存在时 read 返回 (None, None)
- Edge case: clear() 后 read 返回 (None, activated_at)
- Error path: 文件损坏时 read 返回 (None, None)，不抛异常
- Happy path: activate_on_create 写入非空 task_id + ISO8601 时间戳

**Verification:**
- `pytest tests/unit/test_current_task.py -v` 全部通过

---

- [ ] **Unit 4: 修复 CLI `create` 命令**

**Goal:** 修复 `create` 命令，使其通过 `TaskServiceImpl.create_task()` 正确创建任务，并初始化辅助文件

**Requirements:** R5（写入 task.md + 初始化辅助文件）

**Dependencies:** Unit 1, Unit 2, Unit 3

**Files:**
- Modify: `src/mem0ress/cli.py`（`create` 命令）
- Modify: `src/mem0ress/gateway/actions.py`（`create_task` 方法增强）

**Approach:**
- 重写 `cli.py` 的 `create` 命令：
  1. 解析 `--picture`/`--requirements`/`--constraints` 参数（YAML 格式传入）
  2. 调用 `TaskServiceImpl.create_task(task_id=generate_task_id(), picture=picture)` 创建任务
  3. 若传入 requirements/constraints，调用 `update_cognitive_triad()` 补充 PRC
  4. 创建辅助文件：`session.md`（空模板）、`gotchas.md`（空模板）、`judge.md`（空模板）
  5. 调用 `CurrentTaskManager.activate_on_create(task_id)` 更新 `.current_task`
- 移除当前的 `TEMPLATE_INDEX` 硬编码字符串
- **关键**：`TaskServiceImpl.create_task()` 通过 `SubstrateParser.serialize_manifest()` 写入，确保与 `parse_manifest()` 双向兼容

**Patterns to follow:**
- `TaskServiceImpl.create_task()` 现有模式：创建目录，写入 manifest，返回 `TaskManifest`
- `SubstrateParser.serialize_manifest()` 的输出格式（YAML frontmatter + markdown body）

**Test scenarios:**
- Happy path: `cog create --picture "用户登录"` 创建任务目录和文件
- Happy path: 创建的任务可通过 `TaskServiceImpl.get_task()` 正确解析
- Edge case: `picture` 包含特殊字符（中文、emoji）正常处理
- Happy path: 辅助文件 session.md/gotchas.md/judge.md 在 create 时初始化
- Error path: task_id 已存在时 `create` 报错（由 TaskServiceImpl 抛出 `TaskExistsError`）

**Verification:**
- `pytest tests/unit/test_task_service.py::TestTaskServiceImpl::test_create_task` 通过
- `pytest tests/unit/test_cli.py`（新增或更新）

---

- [ ] **Unit 5: CLI `update`/`judge`/`close` 集成 `.current_task`**

**Goal:** 让 update/judge/close 命令默认操作 `.current_task` 指定的 active task，支持显式 task_id 覆盖

**Requirements:** R13, R14, R17

**Dependencies:** Unit 3, Unit 4

**Files:**
- Modify: `src/mem0ress/cli.py`（`update`/`judge`/`close` 命令）

**Approach:**
- `update` 命令：若无显式 `<task_id>`，从 `CurrentTaskManager.read()` 获取当前 active task；调用 `TaskServiceImpl.update_session()` 追加 session.md
- `judge` 命令：若无显式 `<task_id>`，从 `.current_task` 读取；调用 `TaskServiceImpl.judge_task()`，输出纯文本结果
- `close` 命令：若无显式 `<task_id>`，从 `.current_task` 读取；调用 `TaskServiceImpl.close_task()`（内含 judge + complete 原子操作）；成功后调用 `CurrentTaskManager.activate_on_close()` 清空 task_id
- judge 输出改为纯文本（移除 Rich ANSI markup）
- Tier 2 stub 行为：HarnessRunner 对无 verify_cmd 的 requirement 返回 PASS（不阻塞 close）

**Patterns to follow:**
- CLI 参数解析参考现有 `--content`/`--root` 选项模式
- `CurrentTaskManager` 作为单一数据源

**Test scenarios:**
- Happy path: `cog update --content "完成了登录"` 操作当前 active task
- Happy path: `cog update <task_id>` 操作指定任务（覆盖）
- Edge case: `.current_task` 为空时 update 报错，要求显式提供 task_id
- Happy path: `cog judge` 对当前 active task 执行 T0/T1/T2
- Happy path: `cog close` 全部 PASS 时任务标记 COMPLETED，`.current_task` 清空
- Error path: Tier 1 FAIL 时 `cog close` 抛出 RuntimeError，`.current_task` 保持不变

**Verification:**
- `pytest tests/unit/test_cli.py` 相关测试通过
- 手动：`cog create && cog judge && cog close` 端到端成功

---

- [ ] **Unit 6: 创建 `cog.md` Skill 文件**

**Goal:** 创建用户级 Skill 文件 `~/.claude/skills/cog.md`，暴露 4 个 slash commands

**Requirements:** R1, R2, R3, R5, R6, R7, R8, R21, R22, R23

**Dependencies:** Unit 4, Unit 5（Skill 调用 CLI，CLI 必须先正常工作）

**Files:**
- Create: `skills/cog.md`（注意：此文件属于用户级配置，不是 repo 内文件；文档化时放在 `docs/skills/` 作为参考实现）

**Approach:**
- SKILL.md 格式：YAML frontmatter + Markdown 正文
- `name: cog`，`description: Cognitive alignment plane for AI agents`
- `triggers`：`/cog create`、`/cog update`、`/cog judge`、`/cog close`
- Skill 描述部分说明各命令的用途和参数格式
- Skill 通过 shell 调用 CLI（`!` 或 backtick 执行），将结果返回给 Agent

**Skill 文件结构：**
```markdown
---
name: cog
description: Cognitive alignment plane for AI agents. Track tasks, verify progress, maintain cognitive context across turns.
triggers:
  - /cog create
  - /cog update
  - /cog judge
  - /cog close
---

# cog Skill

`cog` provides a cognitive alignment plane for AI agents. It tracks task state, verifies progress against requirements, and maintains cognitive context across turns.

## Commands

### /cog create

Create a new task. Task ID is auto-generated (6 chars).

Parameters:
- `--picture <text>`: Semantic goal description (required)
- `--requirements <yaml>`: List of requirements (optional, can be updated later)
- `--constraints <yaml>`: List of constraints (optional)

Example: `/cog create --picture "用户顺畅登录" --requirements "- 响应 < 200ms" --constraints "- 不明文存储密码"`

### /cog update

Append a turn snapshot to the session log of the active task.

Parameters:
- `--content <text>`: What happened this turn (required)
- `<task_id>`: Optional task ID override (default: active task from .current_task)

### /cog judge

Run Tier 0/1/2 verification on the active task.

Parameters:
- `<task_id>`: Optional task ID override (default: active task)

Output: Pure text, one line per tier with PASS/FAIL and deviation reason.

### /cog close

Atomically close the active task: run judge first, mark COMPLETED only if all tiers pass.

Parameters:
- `<task_id>`: Optional task ID override (default: active task)

On failure: Reports which tier failed and why.
```

**Patterns to follow:**
- Claude Code SKILL.md 格式（参考 `~/.claude/skills/` 下其他 skill 文件的结构）
- YAML frontmatter：`name`、`description`、`triggers` 三个必需字段

**Test scenarios:**
- Skill file 的 YAML frontmatter 格式正确（可通过 Python `yaml.safe_load()` 验证）
- `triggers` 列表包含全部 4 个命令
- Skill 文件名和内部 `name` 一致（`cog`）

**Verification:**
- `python -c "import yaml; yaml.safe_load(open('docs/skills/cog.md'))"` 无报错
- Claude Code 中 `/cog help` 识别 Skill

---

- [ ] **Unit 7: CLI 命名统一 — `mem0` → `cog`（第二步）**

**Goal:** 将 CLI app 名称从 `mem0` 改为 `cog`，与 Skill 触发器彻底对齐。Skill 已存在且调用 `cog` CLI，此步修改 CLI 名称后 Skill 直接生效。

**Requirements:** R4（CLI 命令格式与 Skill 命名对齐）

**Dependencies:** Unit 1, Unit 4, Unit 5（Skill 已就位，CLI 改名后 Skill 无需修改）

**Files:**
- Modify: `src/mem0ress/cli.py`（`app = typer.Typer(name="mem0")` → `app = typer.Typer(name="cog")`）
- Modify: `src/mem0ress/README.md`（所有 `mem0` 命令引用更新为 `cog`）
- Modify: `src/mem0ress/design.md`（命令参考表格更新）
- Modify: `pyproject.toml`（console_scripts 或 entry points 更新为 `cog`）
- Modify: `docs/skills/cog.md`（Skill 中 CLI 调用从 `mem0` 改为 `cog`）

**Approach:**
- 将 `cli.py:32` 的 `name="mem0"` 改为 `name="cog"`
- 更新所有 `mem0` 字符串引用：docstring、error hints、help text
- 更新 README.md 和 design.md 中的命令引用
- 更新 pyproject.toml console_scripts（如有 `mem0` 入口）
- Skill 文件 `docs/skills/cog.md` 中 CLI 调用改为 `cog create ...` 等
- 告知用户：所有脚本、别名、CI/CD 中的 `mem0` 命令需更新为 `cog`

**String inventory（cli.py 中所有 `mem0` 字符串）：**
- `cli.py:1-14` docstring 中的 usage 示例
- `cli.py:32` `name="mem0"`
- `cli.py:33` `help="mem0ress — ..."`
- `cli.py:102` `'mem0 init'` error hint
- `cli.py:161` `'mem0 init'` error hint
- `cli.py:247` `'mem0 update <task_id>'` hint

**Patterns to follow:**
- CLI 重命名时的字符串替换模式

**Test scenarios:**
- Happy path: `cog --help` 输出包含 `cog` 作为 app name
- Happy path: `cog create --help` 正常工作
- Edge case: 旧 `mem0 create` 调用报错 "command not found"（预期行为）

**Verification:**
- `python -m mem0ress.cli --help` 显示 `cog` 作为 app name
- `grep -r "mem0 " src/` 无残留（除非要保留的 deprecated alias）
- 所有现有测试通过（测试使用 `mem0` 的地方需更新）

## System-Wide Impact

- **Step 1（Skill 先）**：Skill 文件 `cog.md` 调用 CLI `mem0 ...`（此时 CLI 仍为 `mem0`）。这一步 Skill 可独立完成，无需修改 CLI
- **Step 2（CLI 改名）**：`mem0` → `cog`。所有调用 `mem0 ...` 的脚本、文档、别名、CI/CD 需要更新。提供迁移文档：`sed -i 's/mem0 /cog /g'` 一键替换
- **`.current_task` 文件**：所有任务创建和关闭命令现在会读写 `.mem0ress/.current_task`。旧的任务（无此文件）依然可用，但操作时会创建该文件
- **Skill 文件**：新增 `~/.claude/skills/cog.md`。用户需要手动安装或使用安装脚本
- **README.md / design.md**：命令参考表格中所有 `mem0` 引用需更新为 `cog`

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| CLI 命名改为 `cog` 是破坏性变更 | 提前在文档中说明，提供别名或迁移指南 |
| `.current_task` 并发写入冲突 | 使用 `safe_write` 乐观锁；MVP 阶段单 Agent 操作可接受 |
| Skill 文件安装需要用户手动操作 | 在 README 中提供安装命令和验证步骤 |
| `update_cognitive_triad` CLI 命令缺失（R20 deferred） | PRC 无法通过 CLI 更新，Agent 如需更新需重新 create |
| `create` 命令重写后与现有 e2e 测试兼容 | 运行完整的 e2e 测试验证 |

## Documentation / Operational Notes

- **README 更新**：添加 `skills/cog.md` 安装步骤：`cp docs/skills/cog.md ~/.claude/skills/cog.md`
- **CLI 帮助**：所有 `cog` 命令的 `--help` 输出需验证正确
- **破坏性变更告知**：CLI 从 `mem0` 改为 `cog`，提醒用户更新任何自动化脚本或别名

## Deferred Implementation Notes

- **R20 PRC 更新**：暂不实现，纳入 v0.2 重构。当前 workaround：Agent 重新 `/cog create` 新任务
- **Tier 2 verify_cmd 真实执行**：MVP 阶段为 stub，不阻塞 close
- **abandon/status/report 命令**：纳入 v0.2+

## Sources & References

- **Origin document:** [docs/brainstorms/2026-05-13-001-mem0ress-skill-design.md](docs/brainstorms/2026-05-13-001-mem0ress-skill-design.md)
- **CLI entry:** [src/mem0ress/cli.py](src/mem0ress/cli.py)
- **TaskServiceImpl:** [src/mem0ress/gateway/actions.py](src/mem0ress/gateway/actions.py)
- **SubstrateParser:** [src/mem0ress/substrate/parser.py](src/mem0ress/substrate/parser.py)
- **Schema:** [src/mem0ress/core/schema.py](src/mem0ress/core/schema.py)
- **HarnessRunner:** [src/mem0ress/harness/__init__.py](src/mem0ress/harness/__init__.py)