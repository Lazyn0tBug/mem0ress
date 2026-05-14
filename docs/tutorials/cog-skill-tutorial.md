---
title: cog Skill Tutorial
description: A practical guide to the cog cognitive alignment plane for AI agents.
---

# cog Skill Tutorial

This tutorial explains what `cog` does, how its parts fit together, and how to use it effectively.

## What Problem Does It Solve?

AI agents lose context when conversations end. An agent working on a 30-step task that spans 10 Claude Code sessions has no built-in way to remember what it did in session 1 when starting session 10. `cog` solves this by giving the agent a persistent memory layer: task state, progress history, and verification results that survive context windows.

## Core Concepts

### The Cognitive Triad (PRC)

Every task is defined by three elements:

- **Picture** — a one-sentence description of what success looks like
- **Requirements** — verifiable conditions (e.g., "response < 200ms")
- **Constraints** — non-negotiable boundaries (e.g., "never store passwords in plaintext")

```yaml
cognitive_triad:
  picture: "用户能顺畅登录"
  requirements:
    - id: req_01
      description: "登录 API 响应 < 200ms"
      verify_cmd: "pytest tests/test_perf.py -k test_login_latency"
  constraints:
    - "不可明文存储密码"
```

### The Task Lifecycle

```
CREATED → IN_PROGRESS → VERIFYING → COMPLETED
                        ↘ ABANDONED
```

- **CREATED**: Task exists but work hasn't started
- **IN_PROGRESS**: Agent is actively working on it
- **VERIFYING**: `judge` is running (transient state)
- **COMPLETED**: All tiers passed, task closed
- **ABANDONED**: Agent explicitly gave up

### Verification Tiers

Every task passes through three tiers of verification:

- **Tier 0** (Constraints): Scans session history for constraint violations — passive, runs every turn
- **Tier 1** (Todos): Checks that all todo items are marked done
- **Tier 2** (Requirements): Runs the `verify_cmd` for each requirement (MVP: auto-PASS stub)

The key rule: **a task cannot close without passing all three tiers**. This is the "no bypass" rule.

---

## How task_id Generation Works

Task IDs are 6-character base36 strings auto-generated on creation (e.g., `2k5m3x`). The algorithm encodes two pieces of information:

```
{4 chars: timestamp_low}{2 chars: counter}
```

**Timestamp portion** — takes the low 4 base36 digits of `floor(unix_time / 64)`. This gives a ~12-day window before wrapping (`36^4 = 1,679,616` values).

**Counter portion** — a per-process monotonic counter, low 2 base36 digits. This guarantees uniqueness across calls within the same 64-second window.

```python
ts_low = int(time.time() // 64) % (36**4)   # 4 chars
counter = next(_COUNTER) % (36**2)            # 2 chars
return _to_base36(ts_low, 4) + _to_base36(counter, 2)
```

The result: within a single Claude Code session, you will never get duplicate IDs. Across sessions, the timestamp prevents collisions for tasks created more than 64 seconds apart.

---

## The `.current_task` Pointer

The `.current_task` file (at `.mem0ress/.current_task`) is a single YAML pointer that tracks which task is "active":

```yaml
task_id: '2k5m3x'
activated_at: '2026-05-14T10:00:00+09:00'
```

**Why it exists**: Agents shouldn't need to remember and re-type task IDs across turns. After `/cog create`, all subsequent commands (`update`, `judge`, `close`) operate on that task by default.

**Lifecycle**:
- `create` → writes task_id + current timestamp to `.current_task`
- `update/judge/close` → reads `.current_task` if no explicit task_id given
- `close` (success) → clears task_id, preserves `activated_at` for audit trail
- If `task_id` is empty/null, the system requires an explicit task_id

**Corruption safety**: uses `safe_write` with SHA-256 hash comparison — if two processes try to write simultaneously, the second one gets a conflict error instead of silently corrupting the pointer.

---

## File Structure

```
.mem0ress/
├── .current_task              # Active task pointer
└── tasks/
    └── <task_id>/
        ├── task.md            # Manifest (PRC, todos, status)
        ├── session.md         # Turn-by-turn history
        ├── gotchas.md         # Cognitive偏差记录
        └── judge.md           # Last verification report
```

All files are plain Markdown + YAML frontmatter. No database, no server — just the filesystem.

---

## How the CLI Commands Work

### `mem0 create --picture "..."`

1. Generates a 6-char task_id via `generate_task_id()`
2. Calls `TaskServiceImpl.create_task()` which uses `SubstrateParser.serialize_manifest()` to write a proper `task.md` (not a raw template string)
3. Creates `session.md`, `gotchas.md`, `judge.md` auxiliary files
4. Calls `CurrentTaskManager.activate_on_create(task_id)` to set `.current_task`
5. Prints the generated task_id

### `mem0 update [--content "..."]`

1. Resolves task_id: explicit argument → `.current_task` → error
2. Calls `TaskServiceImpl.update_session(task_id, content)` to append a turn snapshot
3. Turn counter increments automatically (parsed from existing `## Turn N` markers)

### `mem0 judge`

1. Resolves task_id (same as above)
2. Calls `TaskServiceImpl.judge_task()` → `HarnessRunner.verify_task()`
3. Each tier runs and produces a `HarnessResult { tier, passed, message, deviation }`
4. Results written to `judge.md` as a Markdown report
5. **Output is plain text** (no ANSI markup) so Claude Code agents can parse it programmatically
6. Exit code 1 if any tier fails — agents detect failure via exit code

### `mem0 close`

1. Resolves task_id (same as above)
2. Runs `judge_task()` internally
3. If any tier fails → prints which tier failed and exits with code 1 (task stays open)
4. If all pass → calls `TaskServiceImpl.complete_task()` → marks `task.md` status as `COMPLETED`
5. Calls `CurrentTaskManager.activate_on_close()` to clear `.current_task`

---

## The Skill Layer (`cog.md`)

The Skill bridges Claude Code slash commands to the CLI. It lives at `~/.claude/skills/cog.md` (user-level install, not in the repo).

The Skill format uses YAML frontmatter + Markdown body:

```yaml
---
name: cog
description: Cognitive alignment plane for AI agents...
triggers:
  - /cog create
  - /cog update
  - /cog judge
  - /cog close
---

# cog Skill
[detailed command docs]
```

When you run `/cog create`, Claude Code's Skill system invokes the shell command(s) defined in the Skill. The Skill calls `mem0 create ...` — the same CLI you'd use from a terminal. This is a thin glue layer: the Skill knows nothing about task state, it just translates slash commands into CLI invocations.

This two-layer design (CLI core + Skill shell) keeps the business logic in Python (testable, typed) while the Skill layer stays minimal and Claude-Code-specific.

---

## Tier Verification Deep Dive

### Tier 0 — Constraint Check

Scans the session history for any recorded constraint violations. This is a text scan, not a command execution — it looks for entries that indicate a constraint was violated. It does NOT block progress; it just reports.

### Tier 1 — Todo Completion

Reads the `todos` list from `task.md`. Every item must have `done: true`. If any are `done: false`, Tier 1 fails.

### Tier 2 — Requirement Verification (MVP Stub)

In the MVP, this always returns `PASS`. The `verify_cmd` field exists in the schema so requirements like:

```yaml
requirements:
  - id: req_01
    description: "API 响应 < 200ms"
    verify_cmd: "pytest tests/test_perf.py -k test_api_latency"
```

...are structured for future execution, but the actual shell run is not yet wired up.

---

## Common Workflows

### Starting a New Task

```
/cog create --picture "实现用户登录功能"
```
Agent receives the task_id (e.g., `2k5m3x`). `.current_task` is now set.

### During Development

After each meaningful chunk of work:
```
/cog update --content "完成了登录 API 实现，开始写测试"
```

### Checking Progress

```
/cog judge
```
→ Plain text output: which tiers passed/failed, and why.

### Closing a Task

```
/cog close
```
→ If all tiers pass: status → COMPLETED, `.current_task` cleared.
→ If any tier fails: task stays open, specific failure reported.

---

## Design Decisions Worth Knowing

**Why auto-generated task IDs?** Eliminates a manual step and prevents user errors (duplicate IDs, special characters). The 6-char base36 format is short enough to type but large enough to be unique within a session.

**Why does `activated_at` survive `close()`?** The field is preserved in `.current_task` even after task_id is cleared. This allows future tooling to detect "there was a task that ran from X to Y" without needing to look inside the task directory.

**Why optimistic locking on `.current_task`?** Two agents could theoretically call `create` at the same time. Without hash-checking on writes, the second writer would silently corrupt the first's pointer. With `safe_write`, the second writer gets a conflict error.

**Why plain-text judge output?** Agents consume tool output programmatically. ANSI markup (e.g., `[green]PASS[/green]`) is not machine-parseable without a Rich console. Plain text (`PASS`) is unambiguous.

**Why a separate Skill file instead of built-in commands?** The Skill layer is Claude-Code-specific. The CLI works for humans in a terminal and for any tool that speaks shell. Splitting them means the core is reusable; only the Skill layer knows about slash command conventions.
