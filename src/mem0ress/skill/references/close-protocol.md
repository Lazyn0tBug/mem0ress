# /cap close Protocol

Detailed protocol for semantic task closure via `/cap close`.

## Command Semantic

`/cap close` is a **semantic verification entrypoint**, not a state machine transition.

- Invocation: `/cap close`
- Meaning: "Begin semantic closure verification"
- Precondition: Agent believes task may be ready to close
- Postcondition: Either task marked COMPLETED, or gaps identified

## Session Flow

```
Agent: /cap close
        ↓
Skill retrieves Picture from task.md
        ↓
Skill retrieves current state (todos, recent snapshots)
        ↓
Skill assesses: Does current state semantically match Picture?
        ↓
  Gap detected → Clarification Mode (what's missing to align with Picture?)
        ↓
Skill triggers Judge verification
        ↓
Judge reviews filesystem protocol (NO runtime memory)
        ↓
Judge returns: Tier 0/1/2 results → PASS/FAIL
        ↓
Agent evaluates:
  Judge PASS + no semantic gaps → mem0 close <task_id>
  Judge FAIL → Address specific failures, re-verify
  Semantic misalignment → Clarification Mode first
        ↓
CLI closes task (judge + mark COMPLETED atomically)
```

## Two-Level Verification

### Level 1: Semantic Alignment Check

Before triggering Judge, Agent checks:

1. **Picture completeness**: Does current work semantically match Picture?
2. **Requirements coverage**: Are all Requirements satisfied (or explicitly deferred)?
3. **Constraint compliance**: Were any Constraints violated?

If semantic misalignment exists → Clarification Mode first.

### Level 2: Judge Verification

Then Judge Agent evaluates:

| Tier | What Judge Checks |
|------|-------------------|
| Tier 0 | Constraint violations — hard failures |
| Tier 1 | Todo completion — Checklist verification |
| Tier 2 | Automated validation — verify.md marker execution |

Judge does NOT check semantic alignment — that's Agent's responsibility.

## Judge Isolation Invariant

Judge receives ONLY:
- `task_id`
- Filesystem protocol files (task.md, session.md, gotchas.md, judge.md)

Judge does NOT receive:
- Runtime memory
- Hidden state
- Full execution history
- Agent's internal reasoning

## Agent Decision Authority

The decision to close is **always Agent's**, not Judge's:

- Judge PASS + Agent semantic alignment → Agent calls `mem0 close`
- Judge FAIL → Agent addresses failures, re-triggers `/cap close`
- Judge PASS + semantic misalignment → Agent continues work
- Agent may abandon instead if Picture is unachievable

## No Bypass Rule

The MVP enforces: **No task may be closed without Judge verification.**

```
mem0 close
    ↓
service.close_task()
    ↓
  1. service.judge_task() — runs Tier 0/1/2
    ↓
  2. If any FAIL → RuntimeError, no status change
    ↓
  3. If all PASS → mark COMPLETED
```

This is the "no bypass" rule from the MVP design.

## Anti-Patterns

- Calling `mem0 close` without `/cap close` verification first
- Bypassing Judge (always runs, cannot be disabled in MVP)
- Judge checking semantic alignment (that's Agent's job)
- Agent closing without semantic alignment check
- Closing when semantic state doesn't match Picture

## CLI Commands

```bash
# Verify and close (atomic — Judge runs first)
mem0 close [task_id]

# Just run Judge verification (no close)
mem0 judge [task_id]

# Read Judge report
mem0 report [task_id]
```

## Relationship with /cap create

| Phase | Command | Agent Focus | CLI Action |
|-------|---------|-------------|------------|
| Opening | `/cap create` | Define goal (Picture + Requirements + Constraints) | Create task.md |
| Working | `/cap snapshot` | Record progress deltas | Append to session.md |
| Working | `/cap gotcha` | Record recovery-critical discoveries | Append to gotchas.md |
| Verification | `/cap verify` | Trigger Judge | Write to judge.md |
| Closure | `/cap close` | Semantic alignment + Judge PASS | Update task.md status |