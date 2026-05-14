---
name: cog
description: Cognitive alignment plane for AI agents. Track tasks, verify progress, and maintain cognitive context across turns.
triggers:
  - /cog create
  - /cog update
  - /cog judge
  - /cog close
---

# cog Skill

`cog` provides a cognitive alignment plane for AI agents. It tracks task state, verifies progress against requirements, and maintains cognitive context across turns.

## Setup

The Skill calls the `mem0` CLI. Ensure `mem0` is available in PATH. The skill file is installed at `~/.claude/skills/cog.md`.

## Commands

### /cog create

Create a new task. Task ID is auto-generated (6 characters, e.g., `2k5m3x`).

**Parameters:**
- `--picture <text>`: Semantic goal description (required). The "picture" is what success looks like.
- `--requirements <text>`: YAML list of requirements (optional). Example: `- "响应 < 200ms"`
- `--constraints <text>`: YAML list of constraints (optional). Example: `- "不明文存储密码"`

**Usage:** `/cog create --picture "用户顺畅登录" --requirements "- 响应 < 200ms" --constraints "- 不明文存储密码"`

**Behavior:** Creates task directory under `.mem0ress/tasks/<task_id>/` with `task.md`, `session.md`, `gotchas.md`, `judge.md`. Updates `.current_task` pointer to the new task.

---

### /cog update

Append a turn snapshot to the session log of the active task.

**Parameters:**
- `--content <text>`: What happened this turn (required).
- `<task_id>`: Optional. Task ID to operate on (default: active task from `.current_task`).

**Usage:** `/cog update --content "完成了登录 API 实现，开始写测试"`

**Behavior:** Appends a turn snapshot to `session.md` under the target task's directory.

---

### /cog judge

Run Tier 0/1/2 verification on a task.

**Parameters:**
- `<task_id>`: Optional. Task ID to verify (default: active task from `.current_task`).

**Usage:** `/cog judge`

**Behavior:** Executes verification and prints results. Tier 0 checks constraints, Tier 1 checks todo completion, Tier 2 checks requirements (MVP: stub).

**Output format:**
```
Tier 0: PASS
Tier 1: PASS — 3/3 todos completed
Tier 2: PASS (MVP stub)
```

Exit code 1 if any tier fails.

---

### /cog close

Atomically close the active task: run judge first, mark COMPLETED only if all tiers pass.

**Parameters:**
- `<task_id>`: Optional. Task ID to close (default: active task from `.current_task`).

**Usage:** `/cog close`

**Behavior:**
1. Runs judge verification
2. If all tiers pass → marks task as COMPLETED, clears `.current_task`
3. If any tier fails → reports which tier failed, task remains in current state

**On success:**
```
Task closed: <task_id>
Status: COMPLETED
```

**On failure:**
```
Cannot close task '<task_id>': verification failed
Failed tiers: Tier 1
  - Tier 1: Todo "编写 Auth 守卫中间件" not completed
```
