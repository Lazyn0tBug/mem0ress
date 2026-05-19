# mem0ress Tutorial

mem0ress is a **Semantic Coordination Layer** for AI agents — not a workflow orchestrator.

## Core Concept

mem0ress maintains task cognition alignment through a simple protocol:

```
Picture (语义成功状态)
    +
Requirements (可验证条件)
    +
Constraints (不可逾越的红线)
    ↓
Judge verification
    ↓
Task close
```

## Quick Start

### 1. Start a task

```bash
/cap create
```

The Agent engages in multi-turn clarification:
- **Picture**: What does "done" mean semantically?
- **Requirements**: What must be verifiable?
- **Constraints**: What must never be violated?

Once the triad is defined and consistent:

```bash
mem0 create --picture "..." --requirements "..." --constraints "..."
```

### 2. Record progress

```bash
/cap snapshot
```

Compressed delta — not a transcript.

### 3. Record recovery-critical discoveries

```bash
/cap gotcha
```

Ambiguity, drift risk, unstable assumptions, blockers.

### 4. Verify alignment

```bash
/cap verify
```

Judge Agent runs Tier 0/1/2 verification.

### 5. Close the task

```bash
/cap close
```

1. Agent checks: Does current state semantically match Picture?
2. Judge verifies: Tier 0/1/2 → PASS/FAIL
3. Agent decides: Ready → `mem0 close`; Not ready → continue work

**No bypass**: Judge verification is always required.

## Three Cognitive Modes

| Mode | Trigger | Agent Focus |
|------|---------|-------------|
| Clarification Mode | Picture unclear | Refine semantic success definition |
| Analysis Mode | Constraints conflict | Resolve contradictions |
| Judge Mode | Requirements need validation | Invoke isolated verification |

## File Protocol

Each task lives in `.cap/tasks/<task_id>/`:

| File | Purpose |
|------|---------|
| `task.md` | Picture + Requirements + Constraints + Todos |
| `session.md` | Append-only cognitive deltas |
| `gotchas.md` | Recovery-critical discoveries |
| `VERIFY.md` | Verify Agent verification records |

## Tier Verification

Every task passes through three tiers:

| Tier | Name | What it checks |
|------|------|----------------|
| Tier 0 | Constraints | Scans session history for constraint violations — passive, runs every turn |
| Tier 1 | Todos | Every todo item must be marked `done: true` |
| Tier 2 | Requirements | Runs VERIFY.md marker execution for each requirement (MVP: auto-PASS stub) |

**No bypass rule**: A task cannot close without passing all three tiers.

## task_id Generation

Task IDs are 6-character base36 strings auto-generated on creation (e.g., `2k5m3x`):

```
{4 chars: timestamp_low}{2 chars: counter}
```

- **Timestamp portion**: low 4 base36 digits of `floor(unix_time / 64)` — gives a ~12-day window before wrapping
- **Counter portion**: per-process monotonic counter, low 2 base36 digits — guarantees uniqueness within the same 64-second window

```python
ts_low = int(time.time() // 64) % (36**4)   # 4 chars
counter = next(_COUNTER) % (36**2)            # 2 chars
return _to_base36(ts_low, 4) + _to_base36(counter, 2)
```

Within a single session: no duplicate IDs. Across sessions: timestamp prevents collisions for tasks created >64 seconds apart.

## The `.current_task` Pointer

`.cap/.current_task` tracks the active task:

```yaml
task_id: '2k5m3x'
activated_at: '2026-05-14T10:00:00+09:00'
```

**Why it exists**: Agents don't need to remember and re-type task IDs across turns.

**Lifecycle**:
- `create` → writes task_id + timestamp to `.current_task`
- `update/judge/close` → reads `.current_task` if no explicit task_id given
- `close` (success) → clears task_id, preserves `activated_at` for audit trail

**Corruption safety**: uses `safe_write` with SHA-256 hash comparison — simultaneous writes cause a conflict error instead of silent corruption.

## Anti-Patterns

mem0ress is NOT:
- A workflow engine (no A→B→C sequences)
- An orchestration framework
- A generalized memory system
- An autonomous planner

## Key Constraints

| Rule | Meaning |
|------|---------|
| No bypass | Judge verification required for close |
| Judge isolation | Judge receives NO runtime memory |
| Agent authority | Decision to close is always Agent's |
| Semantic purity | session.md is compressed deltas, not transcripts |

## Skill Layer Design

The Skill bridges slash commands to the CLI:

```
/cap create  →  Skill  →  mem0 create
```

The Skill is a thin glue layer: it translates slash commands into CLI invocations, knows nothing about task state, and stays minimal.

**Two-layer design**: CLI core (Python, testable, typed) + Skill shell (Claude-Code-specific conventions).

## Example Session

```
User: I need to write a whitepaper on AI safety.

Agent: /cap create
  → Clarification Mode: What does "done" mean semantically?
  → Define: Picture, Requirements, Constraints
  → Agent: mem0 create --picture "..." --requirements "..." --constraints "..."

[Work on whitepaper sections]

Agent: /cap snapshot
  → "Completed §2, identified ambiguity in §4 scope"

Agent: /cap gotcha
  → "§4 scope undefined — may conflict with §2 assumptions"

[Continue work]

Agent: /cap verify
  → Judge returns: Tier 0 PASS, Tier 1 PASS, Tier 2 PASS

Agent: /cap close
  → Semantic alignment check: yes
  → Agent: mem0 close <task_id>
```

## Design Decisions

**Why auto-generated task IDs?** Eliminates a manual step and prevents user errors (duplicate IDs, special characters). The 6-char base36 format is short enough to type but large enough to be unique within a session.

**Why does `activated_at` survive `close()`?** Preserved for future tooling to detect "there was a task that ran from X to Y" without looking inside the task directory.

**Why optimistic locking on `.current_task`?** Two agents could call `create` simultaneously. Without hash-checking, the second writer would silently corrupt the first's pointer. With `safe_write`, the second writer gets a conflict error.

**Why plain-text judge output?** Agents consume tool output programmatically. ANSI markup is not machine-parseable without a Rich console. Plain text (`PASS`) is unambiguous.