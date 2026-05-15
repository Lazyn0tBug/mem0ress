---
name: mem0ress
description: |
  Use when starting a task (/cog create), checking state (/cog status),
  or verifying alignment (/cog verify). Provides semantic coordination
  for recoverable task cognition — NOT workflow orchestration.
version: 0.1.0
author: mem0ress
license: MIT
metadata:
  hermes:
    tags: [cognition, task-management, semantic-coordination]
    related_skills: []
---

# mem0ress — Semantic Coordination Layer

## 1. Overview

mem0ress is a **Semantic Coordination Layer** for AI agents, not a workflow orchestrator.

**Core responsibility**: Maintain task cognition alignment by dynamically routing the agent to the right cognitive mode based on current state.

**Key distinction**:
- Workflow orchestration = "do A, then B, then C" (procedural)
- Semantic coordination = "you need X right now, do X" (dynamic routing)

## 2. Participants

Only two participants exist:

| Agent | Role |
|-------|------|
| **主 Agent** | All semantic reasoning (clarification, analysis, decision) |
| **Judge Agent** | Isolated verification only (Tier 0-3) |

No sub-agents, no workflow engines, no orchestration frameworks.

## 3. Core Model

```
主 Agent + Judge Agent
        ↓
Skill assesses cognitive state
        ↓
What is missing?
  Picture unclear      → Clarification Mode
  Constraints conflict → Analysis Mode
  Requirements need validation → Judge Mode
        ↓
Cognitive state complete
        ↓
CLI persistence (create/update files)
```

## 4. Three Cognitive Modes

### 4.1 Clarification Mode

**Triggered when**: Picture (语义成功状态) is unclear or incomplete.

**Agent behavior**: Elicits and refines the semantic success definition through dialogue.

**Completion criteria**: Picture is specific, measurable, and agreed upon.

### 4.2 Analysis Mode

**Triggered when**: Constraints conflict with each other or with the Picture.

**Agent behavior**: Identifies contradictions, proposes resolutions, iterates until矛盾消除.

**Completion criteria**: All constraints are mutually consistent and consistent with Picture.

### 4.3 Judge Mode

**Triggered when**: Requirements need verification against current state.

**Agent behavior**: Invokes Judge Agent with isolated context (task_id + filesystem only).

**Judge isolation**: Judge receives NO runtime memory, NO hidden state, NO full history.

**Completion criteria**: Judge returns PASS/FAIL with evidence.

## 5. Slash Commands as Semantic Entrypoints

Each `/cog` command is a **semantic interaction entrypoint**, not a command binding.

| Command | Semantic Meaning |
|---------|-----------------|
| `/cog create` | Begin semantic initialization of a task |
| `/cog status` | Understand current cognitive state |
| `/cog snapshot` | Append cognitive delta to session |
| `/cog gotcha` | Record recovery-critical discovery |
| `/cog verify` | Request Judge Agent verification |
| `/cog decide` | Read Judge verdict, determine next action |

**CLI role**: Protocol persistence step — executes file operations AFTER semantic coordination completes.

## 6. /cog create Protocol

### 6.1 Flow Overview

```
Agent invokes /cog create <task_id>
        ↓
Skill assesses: Is Picture complete?
  No → Clarification Mode
        ↓
Skill assesses: Do Constraints conflict?
  Yes → Analysis Mode
        ↓
Skill assesses: Are Requirements verifiable?
  No → Refine with Agent
        ↓
All three elements complete
        ↓
Agent confirms completion
        ↓
CLI creates .CAP/tasks/<task_id>/task.md
```

### 6.2 Three Elements

Every task must have:

| Element | Question |
|---------|----------|
| **Picture** | What does "done" mean semantically? |
| **Requirements** | What must be verifiable? |
| **Constraints** | What must never be violated? |

**Definition order**: Picture first, then Requirements and Constraints derived from Picture.

**Consistency check**: After all three are defined, verify no contradictions exist.

### 6.3 Detailed Protocol

See `references/create-protocol.md`

## 7. File Protocol

### 7.1 File Overview

| File | Purpose | Authority |
|------|---------|-----------|
| `task.md` | Picture/Requirements/Constraints + Todos | 主 Agent writes |
| `session.md` | Append-only cognitive deltas | 主 Agent appends |
| `gotchas.md` | Recovery-critical discoveries | 主 Agent appends |
| `judge.md` | Judge verification records | Judge Agent writes |

### 7.2 Detailed Schema

See `references/protocol.yaml`

## 8. Cognitive Modes Detailed Reference

See `references/cognitive-modes.md`

## 9. Anti-Patterns

mem0ress is NOT:
- A workflow engine
- An orchestration framework
- A generalized memory system
- An autonomous planner

If you find yourself designing a procedural sequence (A→B→C), you're doing it wrong.

## 10. Failure Modes

| Failure | Meaning |
|---------|---------|
| session.md becomes transcript | Compression failure |
| Picture/Requirements/Constraints modified after creation | Protocol violation |
| Judge receives hidden state | Isolation failure |
| Skill owns execution flow | CAP has become orchestration |
