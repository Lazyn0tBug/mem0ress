# Cognitive Modes

Three modes exist. Mode selection is based on current cognitive state assessment, not a fixed sequence.

## Mode Selection Logic

```
Assess cognitive state:
  - Picture incomplete? → Clarification Mode
  - Constraints conflict with Picture or each other? → Analysis Mode
  - Requirements need verification? → Judge Mode
  - All three elements complete? → CLI persistence
```

## Clarification Mode

### Trigger Condition

Picture is:
- Vague or ambiguous
- Not specific enough to determine success
- Missing measurable criteria

### Agent Behavior

Ask probing questions:
- "What does 'done' look like specifically?"
- "How would you measure success?"
- "What is the opposite of the goal?"

### Completion Criteria

Picture is:
- Specific and concrete
- Measurable (has success criteria)
- Agreed upon by all stakeholders

### Example

```
Bad: "Improve the login flow"
Good: "Reduce login time from 3s to under 1s, with success rate > 99%"
```

## Analysis Mode

### Trigger Condition

Constraints exhibit one of:
- Internal conflict: two constraints contradict each other
- External conflict: constraint contradicts Picture or Requirements
- Unclear boundary: constraint is too vague to enforce

### Agent Behavior

1. List all constraints explicitly
2. Identify conflicts pairwise
3. For each conflict, propose resolution options
4. Iterate until contradiction eliminated

### Completion Criteria

- All constraints listed explicitly
- No internal contradictions
- All constraints consistent with Picture and Requirements
- Resolutions documented

### Example Conflict

```
Constraint A: "Must work offline"
Constraint B: "Must sync data in real-time"

Conflict: Real-time sync requires network connection.

Resolution options:
  - Accept offline-first with eventual consistency
  - Define clear online/offline transition behavior
  - Narrow scope: "sync when network available"
```

## Judge Mode

### Trigger Condition

User or agent requests verification of:
- Whether current state satisfies Requirements
- Whether any Constraints are violated
- Semantic alignment with Picture

### Agent Behavior

1. Invoke Judge Agent with isolated context
2. Judge receives ONLY: task_id + filesystem protocol
3. Judge returns: Tier 0/1/2/3 assessment
4. Present Judge verdict to main Agent

### Judge Isolation Guarantee

Judge MUST NOT receive:
- Runtime memory
- Hidden state
- Full execution history
- Agent's internal reasoning

### Completion Criteria

Judge returns structured verdict:
- Tier 0: PASS | FAIL (constraint violations)
- Tier 1: PASS | FAIL (todo completion)
- Tier 2: PASS | FAIL | SKIP (verify.md marker results)
- Tier 3: ALIGNED | MISALIGNED | UNCERTAIN (semantic judgment)

### Post-Judge Decision

Decision always belongs to main Agent. Judge verdict is input to Agent's decision process, not a command.

## Mode Transitions

Modes are NOT sequential. Transitions are based on state assessment:

```
Current state determines next mode, not a fixed sequence.

Example path:
  Start → Clarification → Analysis → Judge → Clarification → Done
```

## When Multiple Modes Apply

If multiple issues exist simultaneously, prioritize:
1. Constraint conflicts (Analysis Mode) — must resolve before anything else
2. Missing Picture (Clarification Mode) — Picture drives everything
3. Verification needed (Judge Mode) — only after Picture and Constraints are solid
