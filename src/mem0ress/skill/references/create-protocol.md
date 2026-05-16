# /cap create Protocol

Detailed protocol for semantic initialization of a task via `/cap create`.

## Command Semantic

`/cap create` is a **semantic interaction entrypoint**, not a command binding.

- Invocation: `/cap create`
- Meaning: "Begin semantic initialization of a new task"
- Outcome: task.md created in `.CAP/tasks/<task_id>/`

## Session Flow

```
Agent: /cap create
        ↓
Skill assesses: Is Picture complete?
        ↓
  Picture incomplete
  → Clarification Mode
        ↓
Skill assesses: Do Constraints conflict?
        ↓
  Constraints conflict detected
  → Analysis Mode
        ↓
Skill assesses: Are Requirements verifiable?
        ↓
  Requirements unclear or not verifiable
  → Refine with Agent
        ↓
All three elements (Picture + Requirements + Constraints) complete
        ↓
Agent confirms completion
        ↓
CLI creates task.md
```

## Three Elements

All three must be present and internally consistent:

### Picture

Answer: "What does 'done' mean semantically?"

Good Picture criteria:
- Specific and concrete
- Measurable (has success criteria)
- Describes end state, not process
- Agreed upon

### Requirements

Answer: "What must be verifiable?"

Requirements criteria:
- Each has a verify_cmd (or null for manual)
- Derived from Picture
- Collectively sufficient to achieve Picture
- No circular dependencies

### Constraints

Answer: "What must never be violated?"

Constraints criteria:
- No internal contradictions
- No contradictions with Picture or Requirements
- Enforceable
- Categorical (no "try to" language)

## Consistency Check

After all three elements are drafted:

1. Check: Does each Requirement support the Picture?
2. Check: Does each Constraint not contradict the Picture?
3. Check: Do Requirements and Constraints together form a achievable solution?
4. If any check fails → return to appropriate mode (Clarification or Analysis)

## Definition Order

1. Picture first — defines the goal
2. Requirements derived from Picture — what conditions must be met
3. Constraints added — what boundaries must be respected
4. Consistency check — any contradictions must be resolved

## Multiple Iteration Cycles

The flow is NOT a single pass. Multiple cycles may be needed:

```
Draft Picture
    ↓
Check: Is it clear?
  No → Clarification Mode
    ↓
Draft Requirements
    ↓
Check: Do they support Picture?
  No → Refine Picture or Requirements
    ↓
Draft Constraints
    ↓
Check: Any conflicts?
  Yes → Analysis Mode
    ↓
All consistent
    ↓
Done
```

## CLI Persistence

After semantic coordination completes, CLI executes:

```bash
/cap create \
  --picture "语义成功状态描述" \
  --requirements "req1; req2; ..." \
  --constraints "红线1; 红线2; ..."
```

This creates:
```
.CAP/tasks/<task_id>/
├── task.md       # Full task manifest
├── session.md    # Empty (created)
├── gotchas.md    # Empty (created)
└── judge.md      # Empty (created)
```

## Skipping Semantic Coordination (MVP)

For MVP simplicity, if all three elements are provided upfront:

```bash
/cap create \
  --picture "..." \
  --requirements "..." \
  --constraints "..."
```

CLI creates task.md directly. Semantic coordination still applies — Agent should validate consistency before invoking CLI.

## Anti-Patterns

- Defining Requirements before Picture (requirements serve the goal)
- Adding Constraints that contradict Picture
- Writing verify_cmd that requires LLM inference (must be executable)
- Using vague language in Picture ("improve", "better", "nice")
- Skipping consistency check
