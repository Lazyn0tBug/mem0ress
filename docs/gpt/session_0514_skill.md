> SKILL.md
mem0ress Hermes Skill

MVP Version: v0.2-alpha
1. Overview
mem0ress is implemented as:

```plaintext
ONE Hermes Skill
    ↓
MULTIPLE Slash Commands
    ↓
Protocol Lifecycle Operations
```

The skill is NOT a toolbox.

The skill is:

the protocol-native cognition surface
between Hermes and the mem0ress runtime.

2. Core Philosophy
The mem0ress skill exists to support:

recoverable task cognition
through:

protocol-native cognition recovery

append-only cognition deltas

isolated verification

recoverable execution continuity

The skill MUST preserve the separation between:



Domain	Ownership
semantic reasoning	Hermes
deterministic execution	Runtime
verification authority	Judge Agent

3. Architecture Position

```plaintext
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

The skill bridges:

cognition

protocol

runtime execution

The skill MUST NOT:

become a workflow engine

absorb semantic authority

perform hidden planning

centralize cognition ownership

4. Protocol-Native Design

The skill is designed around:

protocol lifecycle phases
NOT:

utility categories
Every slash command maps directly to a protocol operation.

5. MVP Protocol Surface

The MVP skill operates ONLY on the defined protocol.

Protocol Files
task.md
session.md
gotchas.md
judge.md
Plane Surface
The MVP supports ONLY:

status_plane
data_plane
The skill MUST NOT introduce additional plane abstractions.

6. Lifecycle Mapping
The mem0ress skill maps directly to protocol lifecycle phases.

Lifecycle
1. Recover Cognition
2. Execute Work
3. Append Session Snapshot
4. Trigger Verification
5. Read Judge Verdict
6. Decide Next Action
The skill surface MUST reflect this lifecycle directly.

7. Slash Commands
7.1 /mem0ress.recover
Lifecycle Role
Recover Cognition
Purpose
Recover stable task cognition from protocol artifacts.

Responsibilities
load task.md

load recent session snapshots

load unresolved gotchas

load latest judge verdict

reconstruct recoverable task state

Returns
picture

requirements

constraints

active todos

unresolved blockers

recent cognition deltas

latest verification state

Notes
Recovery optimizes for:

recoverable cognition continuity
NOT:

historical replay
7.2 /mem0ress.status
Lifecycle Role
Recoverable State Rendering
Purpose
Render the current recoverable task state.

Includes
status_plane
task state

active todos

unresolved gotchas

recent meaningful progress

verification summary

data_plane
outputs

artifacts

evidence references

generated assets

Notes
The status plane is the primary cognition recovery surface.

The data plane is the primary execution artifact surface.

7.3 /mem0ress.snapshot
Lifecycle Role
Append Session Snapshot
Purpose
Append a recoverable cognition delta into session.md.

Responsibilities
persist meaningful execution progress

persist stable semantic discoveries

compress execution into cognition deltas

MUST NOT persist
raw execution logs

full reasoning traces

chain-of-thought

conversation history

verbose transcripts

Snapshot Semantics
Snapshots MUST represent:

meaningful cognition deltas
NOT:

execution history
7.4 /mem0ress.gotcha
Lifecycle Role
Recovery Mutation
Purpose
Persist recovery-critical discoveries into gotchas.md.

Examples
ambiguity

unstable assumptions

semantic drift risk

unresolved blockers

architectural traps

Notes
Gotchas exist to improve future cognition recovery.

They are NOT execution logs.

7.5 /mem0ress.verify
Lifecycle Role
Trigger Verification
Purpose
Trigger isolated Judge verification.

Trigger Conditions
Verification MAY trigger when:

all todos completed

Hermes explicitly requests verification

stakeholders request validation

Verification Model
Judge Agent operates with:

task_id + filesystem protocol only
Judge Agent MUST NOT receive:

runtime memory

hidden execution state

full agent history

Verification Responsibilities
Judge performs:



Tier	Responsibility
Tier 0	constraint violations
Tier 1	todo completion
Tier 2	automated requirement validation
Tier 3	semantic picture alignment
7.6 /mem0ress.decide
Lifecycle Role
Post-Verification Decision
Purpose
Read latest judge verdict and determine next action.

Possible Actions


Judge Result	Decision
PASSED	complete / continue
FAILED	retry / decompose / abandon
TIMEOUT	retry / abandon
Notes
Decision authority always belongs to Hermes.

The skill MUST NOT autonomously decide.

8. Snapshot Rules
session.md is append-only.

Snapshots MUST remain:

compressed

recoverable

semantically meaningful

Snapshots MUST NOT become:

chat history

execution replay

reasoning transcript

verbose logs

9. Recovery Guarantees
The skill SHOULD guarantee that recovery can occur using ONLY:

task.md
recent session snapshots
gotchas.md
latest judge verdict
Recovery MUST NOT require:

full conversation replay

hidden runtime state

external memory systems

10. Runtime Boundary
The runtime is deterministic.

The runtime handles:

markdown parsing

filesystem persistence

protocol validation

snapshot append

judge trigger

plane rendering

The runtime MUST NOT:

reinterpret semantics

autonomously plan

own cognition authority

11. Failure Conditions
The skill SHOULD be considered degraded if:

session.md becomes chat history

recovery requires full transcript replay

snapshots become verbose execution logs

Judge receives hidden runtime state

slash commands become orchestration workflows

runtime absorbs semantic authority

12. MVP Constraints
The MVP skill MUST remain intentionally minimal.

The MVP MUST NOT introduce:

orchestration engines

autonomous planning

hidden cognition layers

distributed memory systems

generalized workflow abstractions

multi-agent coordination

The MVP exists ONLY to validate:

recoverable cognition through protocol-native execution
NOT:

fully autonomous agent systems
