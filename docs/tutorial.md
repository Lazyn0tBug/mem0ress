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

### 1. Initialize a task

```bash
/cog create
```

The Agent will engage in a multi-turn conversation to clarify:
- **Picture**: What does "done" mean semantically?
- **Requirements**: What must be verifiable?
- **Constraints**: What must never be violated?

Once all three elements are defined and consistent, the Agent calls:

```bash
mem0 create --picture "..." --requirements "..." --constraints "..."
```

### 2. Record progress

```bash
/cog snapshot <task_id>
```

Summarize what happened this turn — compressed, not a transcript.

### 3. Record recovery-critical discoveries

```bash
/cog gotcha <task_id>
```

Note ambiguity, drift risk, unstable assumptions, or blockers.

### 4. Verify alignment

```bash
/cog verify <task_id>
```

Triggers Judge Agent verification (Tier 0/1/2).

### 5. Close the task

```bash
/cog close <task_id>
```

Flow:
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

Each task lives in `.mem0ress/tasks/<task_id>/`:

| File | Purpose |
|------|---------|
| `task.md` | Picture + Requirements + Constraints + Todos |
| `session.md` | Append-only cognitive deltas |
| `gotchas.md` | Recovery-critical discoveries |
| `judge.md` | Judge verification records |

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

## Example Session

```
User: I need to write a whitepaper on AI safety.

Agent: /cog create whitepaper-001
  → Clarification Mode: What does "done" mean semantically?
  → Define: Picture, Requirements, Constraints
  → Agent: mem0 create --picture "..." --requirements "..." --constraints "..."

[Work on whitepaper sections]

Agent: /cog snapshot whitepaper-001
  → "Completed §2, identified ambiguity in §4 scope"

Agent: /cog gotcha whitepaper-001
  → "§4 scope undefined — may conflict with §2 assumptions"

[Continue work]

Agent: /cog verify whitepaper-001
  → Judge returns: Tier 0 PASS, Tier 1 PASS, Tier 2 PASS

Agent: /cog close whitepaper-001
  → Semantic alignment check: yes
  → Agent: mem0 close whitepaper-001
```