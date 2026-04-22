# Memory System Design Dialogue Record

**Date:** 2026-04-22
**Participants:** User, AI (Claude Code)
**Topic:** Design a new memory system with goal-anchored Plane concept

---

## 1. Initial Proposal

User proposed a new memory system with these core ideas:

1. Memory is divided into **session** and **knowledge**
2. At any moment, memory exists on a **plane**: session plane + knowledge plane
3. On the plane: goal (with picture) and 3 states (completed, in-progress, abandoned)
4. Task marks all tasks as completed, in-progress, or abandoned; status describes current progress; everything else is information
5. At any time, we have a valid memory plane showing current goals, sessions, tasks, progress — "不会跑偏" (won't stray)
6. Multiple goals can exist simultaneously; each goal can have multiple sessions; each session can have multiple tasks; information has multiple tags
7. Information can be retrieved via tags and vector search to form a goal-specific knowledge base
8. Every goal has a **picture** — meaning we can verify if we completed correctly and know the actual distance to the goal
9. But actually, **every task is also a goal**

**Core insight:** Memory has goal attributes. For different scenarios/tasks, memory is different — not a single memory pool that we search through every time. We fundamentally solve the memory failure problem: at any time, we know who we are, what we're doing, where we are, where we're going, and what that destination looks like.

---

## 2. Clarification: Task vs Goal

User clarified:

> "I now tend to merge the two concepts — call them both Task or Goal. A goal is just a Task's picture attribute."

**Final design:**
```
Task
├── picture     ← Goal picture (what success looks like)
├── status      ← completed | in-progress | abandoned
├── subtasks[]  ← Recursive (every subtask is also a Task)
└── info[]      ← Related knowledge, tagged, searchable
```

---

## 3. Clarification: How AI Discovers Plane

**Q:** How does AI maintain Plane?

**A:** "AI does NOT maintain Plane. AI discovers Plane. Plane is a state cluster. Got it?"

This is a fundamental distinction:
- **Previous understanding (wrong):** AI maintains Plane
- **Correct understanding:** AI discovers Plane
- Plane = the current state of a Task
- AI = the discoverer, like walking into an office and seeing what's on the desk

---

## 4. Clarification: Info Management

**Q:** Where does Info come from? Who tags it?

**A:**
- Info sources: dialogue-generated, actively extracted, user-provided, mixed
- Tags: AI automatically tags, can consult user for confirmation

User further clarified:
- **Picture > Requirements** — even if all requirements are met, the goal may not be achieved. Goals are dynamic, requirements are variable.
- **Info = traditional memory** — supports tags, grep, and vector search

---

## 5. Clarification: Cold/Hot Info

User said info can be managed by tags and cold/hot, but hadn't fully figured out the boundaries.

**AI's interpretation:**
- Plane is the core asset
- When a task is completed/abandoned/orphaned for too long/is irrelevant to current task — could all trigger cold status
- Historical Plane has little meaning — every Plane is current

---

## 6. Clarification: Plane is Task-Anchored

User clarified key points:

1. **Plane is task-anchored** — each task has its own Plane
2. **Historical Plane has no meaning** — since sessions can be restored and relevant info may change, every Plane is current
3. **Info belongs to tasks** — the relationship is via tags, not mandatory
4. **Plane is not storage, it's state** — the core asset
5. **Task-Info relationship is tagging, not mandatory — it's inevitable**

**Key quotes:**
- "Plane is task's state, you asked about current active plane"
- "Plane is essentially a cluster of tagged information"
- "Task and info association is tagged, not required, it's inevitable"

---

## 7. Clarification: Session Continuity

**Q:** Is there continuity between sessions?

**A:** "Every session, every moment, is a Plane."

No "restore Plane" concept:
- Task/Info persists in storage
- Plane is rediscovered fresh each time
- Next time you return, not "restoring" but "discovering" the current state

---

## 8. Design Decisions Confirmed

### 8.1 Task = Primary Anchor
- Every Task has a Picture (not just description)
- Picture is the completion standard
- Subtasks are Tasks — the hierarchy is recursive

### 8.2 Picture vs Requirements
```
Picture: "让用户觉得app流畅"
  ├── Requirements: "登录<2s, 搜索<1s, 错误率<0.1%"
  └── Even if all requirements met → Picture may not be achieved
      (user still complains about slowness → new requirements needed)
```

### 8.3 Completion = Picture Achieved
- NOT = all subtasks marked done
- If Picture not achieved → add more subtasks (not abandon)
- Subtasks are paths to Picture, not the goal itself

### 8.4 AI as Discoverer
- AI discovers Plane through dialogue (like navigating a workspace)
- AI does not "maintain" state — it observes and reports
- This mirrors how humans work: you don't "maintain" your desk; you discover its state

### 8.5 Plane Is Always Current
- No freeze, no archive
- Every Plane is current by definition
- Plane change = Task state changed (not that Plane was "switched")

---

## 9. AI Interaction Model Confirmed

### 9.1 How AI Discovers Current Task
User: "AI discovers through communicating with users, just like what you're doing with me now."

This means the system's core interaction mode is:
- **AI + User dialogue → Task discovery + Picture confirmation + State maintenance**
- Like our current conversation — user describes intent, AI helps structure it

### 9.2 Session Flow
```
1. Session starts
2. AI discovers current Task (through dialogue)
3. AI establishes Task tree (root + subtasks)
4. During dialogue:
   - AI tags relevant information for the Task
   - AI updates Task status
   - AI judges whether Picture is achieved
5. Session ends/pauses
6. Next session: AI re-discovers current Task (may have changed)
```

---

## 10. Key Insight: Every Task Is Also a Goal

User said: "But actually, every task is also a goal."

This means the entire structure is **recursive Task-Goal**:
- There's no top-level "goal" separate from tasks
- A Task's Picture IS its goal
- The recursive structure handles context switching naturally

**Context switching example:**
- User was on Task A, now wants to work on Y
- Y creates a new Task (or finds existing Y)
- A remains in the tree — completed, abandoned, or simply not current
- No forced state transition needed

---

## 11. Open Questions & Proposed Solutions

See: `docs/brainstorms/002-memory-system-requirements.md` Section 7

| # | Question | Recommended Approach |
|---|----------|---------------------|
| OQ-1 | Task discovery mechanism | Hybrid: pointer hint + AI inference |
| OQ-2 | Tag structure | Hybrid: explicit tags + vector similarity |
| OQ-3 | Cold/hot determination | Recency + Task status hybrid, 7-day default |
| OQ-4 | Picture completion check | AI judgment + user confirmation |
| OQ-5 | Multiple active Tasks | Yes, task forest model |
| OQ-6 | Context switching | Task tree handles naturally |
| OQ-7 | What persists | Task + Info + Status only |

---

## 12. Additional Discussion: Interaction Design

User raised an important concern: "memory系统的一个关键特征是静默运行，我的设计可能过多交互了"

**The tension:**
| Approach | Description | User Burden |
|----------|-------------|-------------|
| Fully Silent | System runs in background | Zero |
| Hook-Driven | Automatic, silent unless anomaly | Minimal |
| Dialogue-Heavy | AI asks questions | High |

**Goal:** 99% silent, 1% minimal interaction when uncertain.

### Claude-Mem's Hook-Driven Model

Claude-Mem uses 6 lifecycle hooks that fire silently:
- SessionStart → context injection
- UserPromptSubmit → initialize SDK agent
- PostToolUse → capture observations
- Stop → queue summaries
- SessionEnd → cleanup

**Key insight:** User never waits for memory processing. Everything is async.

### Proposed: Uncertainty Triggers

Only 4 situations trigger interaction:
1. **Which Task?** — ambiguous context
2. **New Task?** — new project mentioned
3. **Picture achieved?** — completion evidence found
4. **Conflict?** — new info contradicts old

Each trigger: one question, one-tap response, optional to ignore.

### Comparison

| System | Silent? | User Burden |
|--------|---------|------------|
| MemPalace | Yes (but manual) | High |
| Claude-Mem | Yes | Zero |
| Original mem0ress | No | High |
| **Target mem0ress** | **Yes** | **Minimal** |

### Core Principle

> System should feel like a background service that "just knows."
> Interaction: rare (<1%), light (one question), optional.

---

## 13. Files Created

| File | Description |
|------|-------------|
| `docs/brainstorms/001-memory-systems-design-analysis.md` | Deep analysis of MemPalace and Claude-Mem |
| `docs/brainstorms/002-memory-system-requirements.md` | mem0ress requirements document |
| `docs/brainstorms/002-memory-system-conversation.md` | This dialogue record |
| `docs/brainstorms/002-memory-system-diagrams.html` | SVG architecture diagrams (4 slides) |
| `docs/brainstorms/003-interaction-design-analysis.md` | Interaction design deep-dive |
| `docs/brainstorms/003-interaction-design-diagrams.html` | Interaction design diagrams (3 slides) |

---

## 14. Core Principles Summary

1. **Memory has goal attributes** — same info, different goal = different relevance
2. **Task is the primary anchor** — everything is organized around Tasks, not a flat pool
3. **Picture is completion standard** — not subtasks done, but Picture achieved
4. **AI is discoverer, not maintainer** — AI discovers Plane, does not build it
5. **Plane is always current** — no freeze/archive, every Plane is discovered fresh
6. **Recursive Task structure** — every subtask is also a Task with its own Picture
7. **Soft links via tags** — Info-Task association is tag-based, not foreign key
8. **Silent by default** — 99% silent, only uncertainty triggers interaction

---

**Key quote from User:**

> "核心思想是记忆是有目标属性的，对每个场景，每个任务，记忆是不同的，而不是一个记忆库，每次工作都要从里面找有效的信息。根本上解决记忆的失效问题，任何时候，都知道我是谁，我在干什么，我在哪儿，我要去哪儿，那儿长什么样子。"

Translation: "The core idea is that memory has goal attributes — for each scenario, each task, memory is different, rather than a single memory pool where we have to find useful information every time. We fundamentally solve the memory failure problem — at any time, we know who we are, what we're doing, where we are, where we're going, and what that destination looks like."
