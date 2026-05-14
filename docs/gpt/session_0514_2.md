mem0ress Spec Revision
Agent-Native Cognition Runtime
Revision Draft
Section: Core Philosophy
1. Design Principle
mem0ress is a cognition protocol runtime.

The system exists to stabilize long-horizon task cognition
across agent execution.

mem0ress is NOT:

a workflow engine

an orchestration framework

a centralized memory system

a symbolic reasoning engine

an autonomous planner

The system prioritizes:

recoverable cognition continuity
over:

execution automation
2. Primary Goal
The primary purpose of mem0ress is:

preserving stable task cognition
through protocolized recovery surfaces
The system is designed to reduce:

semantic drift

context fragmentation

cognition loss

long-horizon instability

Section: Cognitive Ownership Model
1. Ownership Separation
mem0ress explicitly separates:

deterministic protocol execution

non-deterministic semantic cognition

This separation is a foundational architectural principle.

2. Runtime Responsibility
The runtime owns deterministic protocol behavior.

This includes:

persistence

protocol validation

markdown parsing

snapshot append

state transition

plane assembly

evidence collection

objective execution

The runtime MUST remain deterministic.

The runtime MUST NOT perform semantic reasoning.

3. Agent Responsibility
The agent owns semantic cognition.

This includes:

semantic interpretation

ambiguity resolution

picture alignment

task evolution

semantic drift correction

completion judgment

recovery planning

execution prioritization

Semantic authority always belongs to the agent.

4. Runtime Provides Evidence, Not Meaning
The runtime MAY provide structured evidence.

Example:

missing_requirements:
- oauth_session_persistence

constraint_violations:
- introduced_new_database
However, the runtime MUST NOT conclude:

- task is semantically complete
- implementation quality is sufficient
- explanation is conceptually aligned
- architecture is correct
Meaning belongs to the agent.

Section: Cognition Compression Model
1. Compression Philosophy
mem0ress does NOT preserve full execution history.

The system preserves:

stable cognition

semantic continuity

recovery-critical information

execution alignment

The system MUST avoid degenerating into conversation persistence.

2. Snapshot Philosophy
Snapshots are:

cognitive deltas
NOT:

execution transcripts
Snapshots SHOULD contain:

meaningful progress

important decisions

newly discovered constraints

semantic risks

recovery-critical discoveries

Snapshots SHOULD NOT contain:

verbose reasoning chains

full execution traces

low-signal exploration

discarded attempts

temporary chain-of-thought

3. Stable Cognition
Stable cognition represents information required for:

long-horizon continuity

semantic recovery

alignment preservation

Examples:

architectural decisions

clarified requirements

stable constraints

persistent gotchas

task direction updates

Stable cognition SHOULD persist.

4. Transient Cognition
Transient cognition represents short-lived execution state.

Examples:

temporary hypotheses

exploratory reasoning

local debugging attempts

ephemeral planning

intermediate chain-of-thought

Transient cognition SHOULD decay.

The runtime SHOULD NOT preserve transient cognition by default.

5. Compression Objective
The system continuously compresses:

execution history
  ↓
cognitive deltas
  ↓
stable cognition
The system optimizes for:

cognition density
NOT:

historical completeness
Section: Plane Model
1. Plane Philosophy
A plane is a cognition recovery surface.

A plane is NOT a raw aggregation of protocol artifacts.

The purpose of a plane is to:

recover task cognition

stabilize execution continuity

reduce context entropy

preserve semantic alignment

2. Plane Layering
Core Plane
Contains stable cognition.

Includes:

picture

active requirements

active constraints

unresolved blockers

persistent gotchas

current task direction

The Core Plane SHOULD always load.

Progress Plane
Contains recent execution evolution.

Includes:

recent snapshots

recent decisions

recently completed todos

newly discovered information

The Progress Plane MAY be windowed.

Evidence Plane
Contains deterministic evidence.

Includes:

test results

validation output

protocol violations

execution artifacts

The Evidence Plane SHOULD remain objective.

Recovery Plane
Contains cognition recovery guidance.

Includes:

known confusion points

recovery hints

semantic drift warnings

unresolved ambiguity

The Recovery Plane exists to accelerate cognition reconstruction.

3. Plane Optimization
Planes SHOULD optimize for:

recovery quality

token efficiency

semantic continuity

cognition stability

Planes SHOULD avoid:

historical reconstruction

raw execution persistence

conversation replay

Section: Recovery Stability Model
1. Recovery Philosophy
Recovery does NOT mean reconstructing exact reasoning history.

Recovery means:

restoring stable task cognition
The system prioritizes:

semantic continuity

execution alignment

recoverable direction

NOT:

exact thought reconstruction

2. Recovery Failure
Recovery failure occurs when the agent can no longer:

identify task direction

align with the picture

understand active constraints

determine meaningful next actions

Recovery failure is a cognition failure,
not a storage failure.

3. Recovery Degradation
Recovery quality MAY degrade when:

snapshots become noisy

planes become oversized

cognition becomes fragmented

semantic drift accumulates

stable cognition is not compressed

4. Recovery Priority
The system SHOULD optimize for:

recoverable cognition
rather than:

perfect historical reconstruction
Section: Task Evolution Rules
1. Task Evolution Philosophy
Tasks MAY evolve during execution.

However:

task evolution MUST preserve:

semantic continuity

picture alignment

recoverability

2. Allowed Evolution
Allowed evolution includes:

requirement clarification

todo refinement

implementation restructuring

recovery-driven adjustment

subtask extraction

3. Forbidden Evolution
Forbidden evolution includes:

silent scope expansion

picture replacement

unrelated architecture redesign

hidden semantic mutation

uncontrolled requirement growth

4. Scope Mutation Rule
Semantic scope expansion SHOULD:

create explicit subtasks

record cognition deltas

preserve original task identity

The runtime MUST NOT silently mutate task semantics.

Section: Skill Philosophy
1. Skill Definition
Skills are cognitive operators.

Skills exist between:

agent cognition
    ↕
skill layer
    ↕
deterministic runtime
Skills are NOT command wrappers.

2. Skill Purpose
Skills exist to:

recover cognition

stabilize semantic continuity

compress execution into stable cognition

expose recoverable task state

assist cognition alignment

3. Skill Constraints
Skills SHOULD NOT:

expose raw runtime mechanics

centralize semantic authority

become workflow orchestrators

become hidden planners

reconstruct full conversation history

4. Skill Lifecycle
Skills participate in cognition continuity.

A skill lifecycle follows:

recover cognition
  ↓
assess semantic state
  ↓
perform operation
  ↓
collect evidence
  ↓
record cognition delta
  ↓
propose next recovery state
Section: Runtime Boundary
1. Runtime Philosophy
The runtime is a deterministic protocol executor.

The runtime is NOT a semantic cognition system.

2. Runtime Responsibilities
The runtime is responsible for:

protocol persistence

deterministic validation

state transition

plane assembly

evidence collection

objective execution

3. Runtime Constraints
The runtime MUST NOT:

autonomously plan

autonomously reprioritize

reinterpret requirements

rewrite task direction

expand semantic scope

perform semantic completion judgment

Section: Autonomy Boundary
1. Design Principle
mem0ress stabilizes cognition.

mem0ress does NOT replace agent reasoning.

2. Runtime Autonomy
The runtime MUST remain deterministic.

The runtime MUST NOT become:

an autonomous planner

a workflow controller

a semantic orchestrator

a centralized cognition authority

3. Skill Autonomy
Skills MAY assist cognition recovery.

Skills MUST NOT:

replace semantic reasoning

centralize cognition ownership

hide autonomous orchestration

override agent interpretation

4. Semantic Authority
The agent always retains authority over:

semantic interpretation

ambiguity resolution

completion judgment

task direction

semantic alignment

Section: Failure Conditions
1. Architectural Failure
The system SHOULD be considered architecturally degraded if:

session artifacts become conversation history

planes continuously expand without compression

cognition recovery requires full chat replay

runtime accumulates semantic authority

skills become orchestration systems

protocol artifacts become execution transcripts

2. Recovery Failure
The system SHOULD be considered operationally degraded if:

long-horizon cognition becomes unrecoverable

semantic drift accumulates across execution

task direction cannot be reconstructed

recovery planes lose alignment value

stable cognition becomes fragmented

Section: Explicit Non-Goals
mem0ress is NOT:

a workflow engine

an orchestration framework

a centralized memory database

an autonomous agent runtime

a generalized planning system

a symbolic reasoning framework

a hidden orchestration layer

a chain-of-thought persistence system

The system exists to stabilize:

recoverable task cognition
NOT to maximize:

execution automation
