# mem0ress Specification

## rev-0.3

### Protocol-Native Recoverable Cognition System

---

# 1. Introduction

Most current agent systems are designed around one of two models:

* workflow orchestration
* persistent memory accumulation

These systems typically assume that continuity emerges from either:

* retaining enough execution state
* replaying enough history
* preserving enough conversational context

mem0ress takes a fundamentally different direction.

The core assumption of mem0ress is:

```text id="qj1kwe"
cognition continuity should emerge from protocol reconstruction,
not from historical replay.
```

This changes the role of:

* memory
* runtime
* skills
* tools
* execution history
* verification

Instead of treating cognition as an opaque runtime state, mem0ress treats cognition as something reconstructable through protocol surfaces.

The system therefore focuses on:

* recoverable cognition
* semantic continuity
* append-only cognition deltas
* isolated verification
* deterministic execution boundaries

---

# 2. System Definition

mem0ress is:

```text id="1m3fga"
a protocol-native recoverable cognition system
```

designed to preserve:

```text id="7v4uok"
recoverable task cognition continuity
```

through:

* protocol reconstruction
* deterministic runtime execution
* append-only cognition deltas
* isolated verification

mem0ress is NOT:

* an orchestration framework
* a generalized AI operating system
* a multi-agent coordination layer
* a persistent memory engine
* a capability routing framework

This distinction is important.

The system is intentionally constrained.

The protocol itself is the primary cognition substrate.

---

# 3. Foundational Principle

Traditional agent systems often operate under the assumption:

```text id="r7zvkt"
memory is the cognition substrate
```

Under this model:

* more memory means better continuity
* longer transcripts mean better recovery
* preserving history means preserving cognition

mem0ress rejects this assumption.

Instead:

```text id="i7l6mj"
protocol is the cognition substrate
```

This means cognition continuity should be achievable through:

* structured protocol artifacts
* semantic compression
* deterministic reconstruction
* recovery-oriented state surfaces

rather than through:

* transcript replay
* hidden runtime state
* persistent conversational accumulation

This principle drives the entire architecture.

---

# 4. System Goal

The purpose of mem0ress is not to preserve everything.

The purpose is:

```text id="9c0bqg"
recoverable cognition continuity
```

This distinction matters.

The system optimizes for:

* interruption recovery
* context reconstruction
* semantic continuity
* verification isolation
* recoverable execution

The system does NOT optimize for:

* historical completeness
* full execution replay
* exhaustive memory persistence
* transcript reconstruction

A recoverable system is not necessarily a historically complete system.

---

# 5. Architecture

The architecture is intentionally simple.

```text id="cnrj4m"
Hermes Agent
    ↓
mem0ress Skill
    ↓
Slash Commands
    ↓
Runtime
    ↓
Filesystem Protocol
    ↓
Judge Agent
```

Each layer has strict responsibility boundaries.

The architecture avoids:

* hidden orchestration
* dynamic routing
* opaque memory layers
* planner-centric execution

because these tend to blur cognition ownership.

---

# 6. Ownership Boundaries

One of the most important architectural constraints is:

```text id="wbh2zx"
semantic authority must remain explicit
```

The system therefore separates responsibility clearly.

| Layer          | Responsibility             |
| -------------- | -------------------------- |
| Hermes         | semantic cognition         |
| mem0ress Skill | protocol lifecycle surface |
| Runtime        | deterministic execution    |
| Judge Agent    | isolated verification      |

This separation prevents:

* runtime cognition leakage
* orchestration drift
* hidden planning layers
* semantic ambiguity

---

# 7. Semantic Authority

Semantic authority belongs ONLY to Hermes.

Hermes decides:

* what matters
* what progress means
* what should be verified
* what should be persisted

The runtime MUST remain deterministic.

The runtime MUST NOT:

* reinterpret semantics
* autonomously plan
* synthesize cognition
* become orchestration logic

This constraint exists to prevent the runtime from slowly becoming:

```text id="u5v1tw"
a hidden agent system
```

which is a common failure mode in many AI frameworks.

---

# 8. Skill Model

## 8.1 Unified Skill Constraint

mem0ress exposes:

```text id="5wy1jw"
ONE unified cognition skill
```

NOT:

```text id="k4qk6e"
multiple independent skills
```

For example:

```text id="rbclwq"
/cog.recover
/cog.snapshot
/cog.verify
```

are NOT separate skills.

They are:

* protocol operations
* lifecycle mutations
* cognition surface operators

This distinction is critical.

The system intentionally avoids:

* capability graphs
* planner-driven tool routing
* multi-skill orchestration
* dynamic agent composition

because those patterns tend to evolve toward:

```text id="c9z4hy"
workflow-centric agent systems
```

instead of:

```text id="x4q8dr"
protocol-native cognition systems
```

---

## 8.2 Skill Philosophy

The skill exists ONLY to expose:

```text id="8hplrt"
protocol lifecycle operations
```

The skill is NOT:

* a utility collection
* a workflow engine
* a planner surface
* a routing layer

The skill should remain extremely thin.

Its purpose is protocol exposure, not cognition ownership.

---

# 9. Slash Command Model

Slash commands are defined as:

```text id="s8t2pa"
protocol lifecycle operators
```

Each command maps directly to a protocol phase.

Commands are NOT:

* tools
* autonomous workers
* planners
* subsystems

This is important because command inflation often leads to:

* orchestration layers
* hidden routing
* capability composition
* planner dependency

The MVP intentionally avoids this direction.

---

# 10. MVP Command Surface

| Slash Command | Protocol Role               |
| ------------- | --------------------------- |
| /cog.recover  | cognition reconstruction    |
| /cog.status   | recoverable state rendering |
| /cog.snapshot | cognition delta append      |
| /cog.gotcha   | recovery mutation           |
| /cog.verify   | Judge trigger               |
| /cog.decide   | post-verification decision  |

These commands collectively expose the recoverable cognition lifecycle.

---

# 11. Lifecycle Model

## 11.1 Execution Lifecycle

```text id="1rj82m"
1. Recover Cognition
2. Execute Work
3. Append Snapshot
4. Trigger Verification
5. Read Judge Verdict
6. Decide Next Action
```

This lifecycle is intentionally minimal.

The MVP does not attempt to model:

* autonomous decomposition
* planning graphs
* recursive orchestration
* distributed coordination

The goal is validating cognition recovery.

---

## 11.2 Lifecycle Authority

| Phase        | Authority |
| ------------ | --------- |
| cognition    | Hermes    |
| execution    | runtime   |
| verification | Judge     |
| decision     | Hermes    |

This separation ensures:

* recoverability
* isolation
* deterministic execution boundaries

---

# 12. Protocol Surface

The protocol is the core system surface.

Not memory.

Not orchestration.

Not runtime state.

The protocol is the reconstructable cognition substrate.

---

## 12.1 Core Protocol Files

```text id="d3a1vu"
task.md
session.md
gotchas.md
judge.md
```

These files collectively form the recoverable cognition surface.

---

## 12.2 task.md

task.md is the:

```text id="jlwm06c"
semantic authority surface
```

It defines:

* picture
* requirements
* constraints
* todos

task.md should remain stable and high-signal.

It represents the intended cognition target.

---

## 12.3 session.md

session.md is:

```text id="jlwm06d"
append-only cognition delta stream
```

NOT:

```text id="’wini06q"
execution transcript
```

This is one of the most important constraints in the system.

session.md exists to preserve:

* semantic progress
* meaningful discoveries
* architectural decisions
* cognition mutations

NOT:

* raw execution
* verbose reasoning
* transcript history
* chain-of-thought

---

## 12.4 gotchas.md

gotchas.md stores:

```text id="jlwm06e"
recovery-critical discoveries
```

Examples include:

* ambiguity
* unstable assumptions
* semantic drift risks
* unresolved blockers
* architectural traps

gotchas improve future recovery quality.

---

## 12.5 judge.md

judge.md is the:

```text id="’wini06r"
isolated verification surface
```

It stores:

* verification triggers
* verdicts
* evidence summaries

Judge outputs should remain concise and recoverable.

---

# 13. Snapshot Semantics

## 13.1 Snapshot Definition

A snapshot represents:

```text id="’wini06s"
recoverable cognition delta
```

NOT:

```text id="’wini06t"
historical replay
```

This distinction changes how snapshots are written.

---

## 13.2 Snapshots MUST Preserve

* semantic progress
* stable discoveries
* architectural decisions
* recovery-critical changes

---

## 13.3 Snapshots MUST Discard

* raw logs
* chain-of-thought
* transcript replay
* verbose execution history
* transient reasoning

---

## 13.4 Snapshot Success Condition

Recovery SHOULD succeed using ONLY:

```text id="’wini06u"
task.md
recent snapshots
gotchas.md
latest judge verdict
```

without requiring:

* transcript replay
* runtime continuation
* hidden memory state

This is one of the primary invariants of the system.

---

# 14. Recoverability

Recoverability is defined as:

```text id="’wini06v"
protocol-reconstructable cognition continuity
```

NOT:

```text id="’wini06w"
persistent memory retention
```

This is a major architectural distinction.

Recoverability means:

* cognition can resume
* semantic continuity survives
* interruptions are tolerable
* reconstruction remains possible

without preserving every detail.

---

# 15. Plane Model

The MVP supports ONLY:

| Plane        | Responsibility                |
| ------------ | ----------------------------- |
| status_plane | recoverable cognition surface |
| data_plane   | execution artifact surface    |

The MVP intentionally avoids excessive plane abstraction.

---

# 16. status_plane

The status plane exists for:

```text id="’wini06x"
cognition recovery
```

NOT:

```text id="’wini06y"
execution monitoring
```

It includes:

* picture
* active requirements
* active todos
* recent meaningful deltas
* unresolved gotchas
* latest Judge state

The status plane is the primary recovery surface.

---

# 17. data_plane

The data plane stores:

* outputs
* artifacts
* evidence references
* generated assets

The data plane is NOT:

* runtime memory
* generalized persistence
* transcript storage

Its role is execution artifact continuity.

---

# 18. Judge Model

Judge is defined as:

```text id="’wini06z"
isolated verification authority
```

Judge exists to validate outcomes independently from execution runtime.

---

## 18.1 Judge Isolation Constraint

Judge receives ONLY:

```text id="’wini070"
task_id + filesystem protocol
```

Judge MUST NOT receive:

* runtime memory
* hidden cognition state
* chain-of-thought
* execution replay

This isolation is critical.

Without isolation:

* verification becomes contaminated
* semantic leakage occurs
* runtime state biases evaluation

---

## 18.2 Judge Verification Tiers

| Tier   | Responsibility        |
| ------ | --------------------- |
| Tier 0 | constraint violations |
| Tier 1 | todo completion       |
| Tier 2 | automated validation  |
| Tier 3 | semantic alignment    |

The MVP may only partially implement these tiers.

---

# 19. Runtime Model

The runtime is deterministic.

This is one of the most important constraints.

---

## 19.1 Runtime Responsibilities

* markdown parsing
* filesystem persistence
* protocol validation
* snapshot append
* Judge triggering
* plane rendering

---

## 19.2 Runtime MUST NOT

* own cognition authority
* reinterpret semantics
* autonomously plan
* absorb orchestration
* become hidden workflow logic

This prevents runtime drift.

---

# 20. Filesystem Layout

```text id="’wini071"
.mem0ress/
└── tasks/
    └── task_x/
        ├── task.md
        ├── session.md
        ├── gotchas.md
        ├── judge.md
        │
        └── data/
            ├── outputs/
            ├── evidence/
            └── artifacts/
```

The filesystem protocol is intentionally human-readable.

---

# 21. Technology Constraints

| Layer      | Technology     |
| ---------- | -------------- |
| Runtime    | Python 3.12    |
| Package    | pyproject.toml |
| Dependency | uv             |
| CLI        | Typer          |
| Validation | Pydantic       |
| Lint       | Ruff           |
| Type Check | ty             |

The MVP intentionally uses a lightweight stack.

---

# 22. MVP Constraints

The MVP MUST remain intentionally minimal.

---

## 22.1 MVP MUST NOT Introduce

* orchestration engines
* autonomous planning
* generalized memory systems
* hidden cognition layers
* distributed runtimes
* capability routing
* multi-agent coordination
* planner-driven composition

---

## 22.2 MVP Purpose

The MVP exists ONLY to validate:

```text id="’wini072"
recoverable cognition through protocol-native execution
```

NOT:

```text id="’wini073"
fully autonomous agent systems
```

---

# 23. Failure Conditions

The system SHOULD be considered degraded if:

| Failure                         | Meaning                   |
| ------------------------------- | ------------------------- |
| session.md becomes transcript   | compression failure       |
| recovery requires replay        | cognition failure         |
| runtime absorbs reasoning       | architecture failure      |
| Judge receives hidden state     | isolation failure         |
| slash commands become workflows | protocol failure          |
| skill becomes toolbox           | cognition surface failure |

These failures represent architectural drift.

---

# 24. Final Principle

mem0ress is fundamentally:

```text id="’wini074"
a cognition continuity protocol
```

NOT:

```text id="’wini075"
an AI workflow framework
```

This distinction defines the entire system direction.
