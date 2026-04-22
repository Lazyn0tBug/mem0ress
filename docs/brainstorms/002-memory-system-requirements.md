# Memory System Requirements: Plane-Based Goal-Anchored Memory

**Date:** 2026-04-22
**Status:** Draft for Discussion
**Scope:** mem0ress memory system design

---

## 1. Problem Statement

Existing memory systems treat memory as a flat pool of information. They fail because:

1. **Memory has no anchor** — same info is relevant to multiple goals, making it equally (un)useful to all
2. **No state awareness** — systems don't know "where you are" in a goal hierarchy
3. **Completion is ambiguous** — no clear criteria for when a goal is truly achieved
4. **Context is lost** — sessions are independent; no persistent "where am I"

**Core insight:** Memory is not a warehouse; it is a goal-anchored, state-aware network. Information gains meaning only when anchored to a goal with a picture of success.

---

## 2. Core Concepts

### 2.1 Task (Primary Anchor)

```
┌─────────────────────────────────────────────────────────────┐
│                            Task                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  picture     : "让用户觉得app流畅"                    │  │
│  │  status      : in-progress ◉                        │  │
│  │                                                     │  │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐    │  │
│  │  │Subtask A │───▶│Subtask B │    │Subtask C │    │  │
│  │  │ completed │    │ in-progress   │  pending │    │  │
│  │  └──────────┘    └──────────┘    └──────────┘    │  │
│  │                                                     │  │
│  │  info[]  : tagged memories linked via tags         │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Key properties:**
- Task is the fundamental unit of memory anchoring
- Every Task has a Picture (not just description)
- Subtasks are Tasks — the hierarchy is recursive
- Task-Info link is via tags, not ownership

### 2.2 Recursive Task Tree

```
                    ┌─────────────────────────────────────────┐
                    │           Task: 完成项目X                │
                    │           picture: "X上线运行"           │
                    │           status: in-progress            │
                    └──────────────────┬──────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
              ▼                        ▼                        ▼
    ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
    │ Task: 登录模块   │      │ Task: 支付模块   │      │ Task: 搜索模块   │
    │ picture: 流畅   │      │ picture: 安全   │      │ picture: 准确   │
    │ status: done ✓ │      │ status: active  │      │ status: pending │
    └────────┬────────┘      └────────┬────────┘      └─────────────────┘
             │                        │
             ▼                        ▼
    ┌─────────────────┐      ┌─────────────────┐
    │ Sub: OAuth配置  │      │ Sub: Stripe集成  │
    │ status: done ✓  │      │ status: active   │
    └─────────────────┘      └─────────────────┘

    NOTE: Every subtask IS a Task with its own picture/status/info
```

### 2.3 Info (Memory Body)

```
┌─────────────────────────────────────────────────────────────┐
│                          Info                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  content                                            │  │
│  │  "用户反馈:登录太慢,等了3秒才跳转"                    │  │
│  │                                                     │  │
│  │  tags: ["性能", "登录", "用户反馈", "P0"]            │  │
│  │                                                     │  │
│  │  cold/hot: ● hot                                    │  │
│  │                                                     │  │
│  │  linked to: Task[登录模块], Task[性能优化]           │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Properties:**
- Info = traditional memory (learned from MemPalace, Claude-Mem)
- Supports grep and vector search (learned from both systems)
- Tags are AI-generated, optionally user-confirmed
- No Task association is required; links are soft (tag-based)

### 2.4 Plane (Discovered State, Not Maintained)

```
┌─────────────────────────────────────────────────────────────┐
│                     Plane = Task at Moment T                │
│                                                              │
│    ┌───────────────────────────────────────────────────┐   │
│    │  Task: 登录模块                                     │   │
│    │  Picture: "登录<1秒, 成功率>99%"                    │   │
│    │  Status: in-progress ◉                             │   │
│    │                                                    │   │
│    │  Subtasks:                                         │   │
│    │    ├── [✓] OAuth配置完成                           │   │
│    │    ├── [○] 优化登录逻辑  ← 当前                    │   │
│    │    └── [ ] 性能测试                                │   │
│    │                                                    │   │
│    │  Linked Info (hot):                                │   │
│    │    ├── "用户反馈:登录3秒"  [性能,登录]              │   │
│    │    ├── "Session存储改为Redis"  [架构,性能]          │   │
│    │                                                    │   │
│    │  Progress: 50% toward Picture                      │   │
│    └───────────────────────────────────────────────────┘   │
│                                                              │
│    Plane是"被发现的"，不是"被维护的"                          │
│    下一秒可能状态变了，就是不同的Plane                         │
└─────────────────────────────────────────────────────────────┘
```

**Key properties:**
- Plane is a **state concept**, not a storage concept
- AI **discovers** the current Plane, does not build it
- Every session, every moment, discovers a (possibly new) Plane
- Plane change = Task state changed, not that Plane was "switched"
- Historical Plane has no meaning — only current state matters

### 2.5 Status Lifecycle

```
                    ┌──────────────┐
                    │   created    │
                    └──────┬───────┘
                           │ AI discovers via conversation
                           ▼
                    ┌──────────────┐
              ┌─────│ in-progress  │─────┐
              │     └──────────────┘     │
              │                          │
              ▼                          ▼
       ┌──────────────┐         ┌──────────────┐
       │  completed   │         │  abandoned   │
       │     ✓        │         │     ✗        │
       └──────────────┘         └──────────────┘

Completion criteria = Picture achieved
  (NOT = all subtasks marked done)
  (If Picture not achieved → add more subtasks, not abandon)
```

---

## 3. Design Principles

### 3.1 Memory Has Goal Attributes

> Same information, different goal → different relevance

This is the fundamental departure from MemPalace and Claude-Mem:

```
MemPalace Organization:          Claude-Mem Organization:      mem0ress Organization:

┌─────────────────┐              ┌─────────────────┐         ┌─────────────────┐
│  Wing: 项目A    │              │  Layer 0: Header │         │  Task: 登录模块  │
│  ├── Room: auth │              │  Layer 1: Recent │         │    └── Info...  │
│  ├── Room: api  │              │  Layer 2: Full   │         │  Task: 支付模块  │
│  └── Room: db   │              │  Layer 3: Deep  │         │    └── Info...  │
└─────────────────┘              └─────────────────┘         └─────────────────┘
     ↑                              ↑                           ↑
  Structure-first                  Time-first                 Goal-first
  (metadata filter)               (progressive disclosure)     (picture + status)
```

### 3.2 AI as Discoverer, Not Maintainer

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│   你走进办公室                                                │
│       │                                                     │
│       ▼                                                     │
│   ┌─────────────────────────────────────────────────────┐  │
│   │  你看到: 桌面上的文件、笔记、任务清单                  │  │
│   │  你没有"维护"这些状态                                  │  │
│   │  状态客观存在，你只是发现它                            │  │
│   └─────────────────────────────────────────────────────┘  │
│       │                                                     │
│       ▼                                                     │
│   AI = 那个帮你"看一眼桌面"的聪明助手                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Picture as Completion Standard

```
    ┌──────────────────────────────────────────────────────────┐
    │                      Picture                              │
    │              "让用户觉得app流畅"                          │
    └──────────────────────────┬───────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │  Requirements   │ │  Requirements   │ │  Requirements   │
    │  "登录 < 1秒"   │ │  "搜索 < 0.5秒" │ │  "错误率 < 0.1%"│
    └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
             │                   │                   │
             ▼                   ▼                   ▼
        [满足]              [满足]               [满足]
             │                   │                   │
             └───────────────────┴───────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────┐
                    │     Picture Achieved?       │
                    │                              │
                    │   可能仍NO!                  │
                    │   用户仍抱怨"卡"              │
                    │   → 需要新的Requirements     │
                    │   → Picture演化              │
                    └─────────────────────────────┘
```

### 3.4 Plane Is Always Current

```
Session 1, T1              Session 1, T2              Session 2, T3
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│ Plane: Task A   │        │ Plane: Task A   │        │ Plane: Task A   │
│ status: 30%     │   →    │ status: 60%     │   →    │ status: 80%     │
│                 │        │                 │        │                 │
│ Plane是瞬时快照  │        │ 下一秒状态变了    │        │ 新Session        │
│ 每次都是新的发现  │        │ 就是新的Plane     │        │ 发现新的Plane    │
└─────────────────┘        └─────────────────┘        │ 没有"恢复"概念   │
                                                       └─────────────────┘
```

---

## 4. Data Model (Conceptual)

### 4.1 Entity Relationships

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   ┌─────────┐      parent_id       ┌─────────┐                     │
│   │  Task   │◀────────────────────│  Task   │                     │
│   │  (root) │                     │(subtask)│                     │
│   └────┬─────┘                     └────┬────┘                     │
│        │                                   │                         │
│        │          ┌───────────────────────┘                         │
│        │          │                                                  │
│        │          ▼                                                  │
│        │   ┌──────────────────────────────────────┐                 │
│        │   │         "Task is discovered"         │                 │
│        │   │                                      │                 │
│        │   │  picture: string                     │                 │
│        │   │  status: created|in-progress|completed|abandoned      │
│        │   │  created_at: timestamp               │                 │
│        │   │  updated_at: timestamp               │                 │
│        │   └──────────────────────────────────────┘                 │
│        │                                                           │
│        │          tagged by            discovered as                 │
│        │   ┌───────────────────┐    ┌──────────────────┐          │
│        │   │       Info        │    │      Plane       │          │
│        │   │                   │    │                  │          │
│        │   │  content: text    │    │  = Task at T     │          │
│        │   │  tags: string[]   │◀───│  = current state │          │
│        │   │  cold/hot: enum   │    │                  │          │
│        │   │  created_at: ts   │    │  NOT stored      │          │
│        │   └───────────────────┘    │  DISCOVERED       │          │
│        │            ▲                └──────────────────┘          │
│        └────────────┼──────────────────────────────────────────────┘
│                     │
│                     │ via tag matching
│                     │ (soft link, not foreign key)
└─────────────────────┘
```

### 4.2 Task Entity

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| parent_id | UUID? | Parent Task (null for root) |
| picture | string | Goal picture (what success looks like) |
| status | enum | completed \| in-progress \| abandoned |
| created_at | timestamp | When Task was discovered |
| updated_at | timestamp | Last state change |

### 4.3 Info Entity

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| content | text | The memory content |
| tags | string[] | AI-generated labels |
| cold/hot | enum | Activity level |
| created_at | timestamp | When captured |

### 4.4 Task-Info Link (Soft, via Tags)

```
Info A: tags = ["auth", "oauth", "clerk"]
Info B: tags = ["性能", "登录", "用户反馈"]
Info C: tags = ["oauth", "安全"]

Task X (登录模块): inferred tags from picture + context = ["auth", "oauth", "登录"]
Task Y (性能优化): inferred tags = ["性能", "优化", "用户反馈"]

Linking:
  Info A → Task X  (tag intersection: oauth)
  Info B → Task X, Task Y  (登录, 用户反馈)
  Info C → Task X  (oauth)

No foreign key. Link exists when tag intersection is non-empty.
```

---

## 5. AI Interaction Model

### 5.1 Session Flow

```
User arrives
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│  AI discovers via dialogue                                   │
│                                                              │
│  "你好，我看到你说要做X项目..."                                │
│  "能告诉我你现在想达成什么吗？"                                │
│  "这个目标完成时会是什么样子？"                               │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Plane Discovered                                            │
│                                                              │
│  Task: X项目                                                  │
│  Picture: "X上线,日活1万"                                    │
│  Status: in-progress                                         │
│  Subtasks: [登录模块(60%), 支付(30%), 通知(10%)]            │
│                                                              │
│  Related Info (hot):                                         │
│  - "用户调研: 最关心登录速度"  [hot, 优先级P0]              │
│  - "竞品A的登录方案"  [hot, 参考]                           │
│                                                              │
│  Progress: 33% toward Picture                                │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  AI presents:                                                │
│                                                              │
│  "你现在在X项目。Picture是'X上线,日活1万'。                  │
│   当前进度33%。登录模块60%, 支付30%。                         │
│   我看到有2条热门信息..."                                     │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 During Session

```
┌─────────────────────────────────────────────────────────────┐
│                    During Session                            │
│                                                              │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐ │
│  │ New Info    │ ───▶ │ AI tags it │ ───▶ │ Link to     │ │
│  │ produced    │      │ (auto)     │      │ relevant    │ │
│  │             │      │            │      │ Task(s)     │ │
│  └─────────────┘      └─────────────┘      └──────┬──────┘ │
│                                                     │       │
│      ┌──────────────────────────────────────────────┘       │
│      │                                                        │
│      ▼                                                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  AI monitors Picture progression                     │    │
│  │                                                      │    │
│  │  "当前状态接近Picture了?"                           │    │
│  │  "需要增加新的subtask?"                              │    │
│  └──────────────────┬──────────────────────────────────┘    │
│                     │                                         │
│           ┌─────────┴─────────┐                               │
│           ▼                   ▼                               │
│  ┌───────────────┐   ┌───────────────┐                       │
│  │ Picture       │   │ Picture       │                       │
│  │ achieved?     │   │ not achieved? │                       │
│  │               │   │               │                       │
│  │ AI: "建议     │   │ AI: "需要     │                       │
│  │ 完成这个Task" │   │ 增加subtask?" │                       │
│  └───────┬───────┘   └───────┬───────┘                       │
│          │                   │                                │
│          ▼                   ▼                                │
│   [User confirms]    [User + AI collaborate                    │
│    → completed]       → new subtasks]                         │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Session End

```
┌─────────────────────────────────────────────────────────────┐
│                      Session End                             │
│                                                              │
│  No explicit "save" needed.                                  │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  What persists:           What does NOT persist:    │    │
│  │  ┌─────────────────┐     ┌─────────────────────┐   │    │
│  │  │ Task entities   │     │ "Session state"     │   │    │
│  │  │ (with status)   │     │ (Plane is NOT stored│   │    │
│  │  │                 │     │  across sessions)   │   │    │
│  │  │ Info entities   │     │                     │   │    │
│  │  │ (with tags)     │     │                     │   │    │
│  │  │                 │     │                     │   │    │
│  │  │ Status changes  │     │                     │   │    │
│  │  │ (persisted)     │     │                     │   │    │
│  │  └─────────────────┘     └─────────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Next session: AI discovers Plane fresh                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Comparison with Existing Systems

### 6.1 Organization Models

```
MemPalace:                    Claude-Mem:                 mem0ress:

┌─────────────────┐          ┌─────────────────┐         ┌─────────────────┐
│  Palace         │          │  Layers         │         │  Task Forest    │
│                 │          │                 │         │                 │
│  ┌───────────┐  │          │  [0] Header    │         │    Task A ─┬─▶ Info
│  │ Wing: P1  │  │          │  [1] Timeline  │         │    Task B ─┬─▶ Info
│  │ ├─ Room 1 │  │          │  [2] Full      │         │    Task C ─┬─▶ Info
│  │ ├─ Room 2 │  │          │  [3] Deep      │         │      ↑                    │
│  │ └─ Room 3 │  │          │                 │         │   (recursive)              │
│  └───────────┘  │          └─────────────────┘         └─────────────────┘
│  ┌───────────┐  │          ┌─────────────────┐                 │
│  │ Wing: P2  │  │          │  Observations  │                 │
│  │ ├─ Room 1 │  │          │  (with types)  │                 │
│  │ └─ Room 4 │  │          └─────────────────┘                 │
│  └───────────┘  │                                                │
│       ↑         │                                                │
│    (structure)  │                                           (goal-anchored)
└─────────────────┘
```

### 6.2 Feature Comparison Table

| Dimension | MemPalace | Claude-Mem | mem0ress |
|-----------|-----------|------------|----------|
| **Organization** | Palace (wing/room) | Temporal layers | Task anchor |
| **State awareness** | None | Partial (session summary) | Full (Picture + Status) |
| **Completion criteria** | N/A | N/A | Picture matching |
| **Memory capture** | Batch mine | Hook-driven | Dialogue-discovered |
| **Retrieval** | Semantic + structure | Progressive disclosure | Tag + vector + Task context |
| **冷/热** | N/A (all equal) | N/A (all equal) | cold/hot lifecycle |
| **Session continuity** | None | Summary injection | Plane discovery |
| **LongMemEval** | 96.6% (raw) | N/A | TBD |

---

## 7. Open Questions & Proposed Solutions

### OQ-1: How does AI discover "which Task" is current?

**Problem:** When a user arrives, how does AI know which Task(s) are active?

```
┌─────────────────────────────────────────────────────────────┐
│                    OQ-1: Task Discovery                     │
│                                                              │
│   Option A: Pointer          Option B: Inference             │
│   ┌─────────────┐           ┌─────────────┐                 │
│   │ current_    │           │ Scan all    │                 │
│   │ task_id     │           │ Tasks +     │                 │
│   │ (system)    │           │ context     │                 │
│   └──────┬──────┘           │ inference   │                 │
│          │                   └──────┬──────┘                 │
│          │                          │                        │
│          ▼                          ▼                        │
│   Simple, fast            Flexible, AI-driven               │
│   Risk: drift              Risk: ambiguous                  │
│                                                              │
│   Option C: Multi-Task                                       │
│   ┌─────────────┐                                            │
│   │ active_set: │                                            │
│   │ [A, B, C]   │                                            │
│   └─────────────┘                                            │
│   Most flexible                                              │
│                                                              │
│   RECOMMENDATION: A + B hybrid                               │
└─────────────────────────────────────────────────────────────┘
```

### OQ-2: How are tags structured and managed?

**Problem:** Info-Task linking is via tags. How are tags designed?

```
Option A: Flat           Option B: Hierarchical       Option D: Hybrid (REC)
┌─────────────┐        ┌─────────────┐            ┌─────────────┐
│ auth        │        │ auth/oauth  │            │ auth        │ ◀── explicit
│ oauth       │        │ auth/clerk  │            │ oauth       │
│ clerk       │        │ project/X  │            │ clerk       │
│ migration   │        │             │            │             │
└─────────────┘        └─────────────┘            ├─────────────┤
 Simple, grep-friendly  Structured           ───▶  │ [vector]    │ ◀── semantic
 Risk: explosion       Risk: upfront tax    similarity for rest
```

### OQ-3: What determines cold/hot?

**Problem:** When does Info become "cold"?

```
┌─────────────────────────────────────────────────────────────┐
│                    OQ-3: Cold/Hot Lifecycle                 │
│                                                              │
│   Info hot when:                          Info cold when:   │
│   ┌─────────────────────┐                ┌──────────────┐  │
│   │ 1. Linked to        │                │ 1. Created   │  │
│   │    in-progress Task │                │    > 7 days  │  │
│   │                     │                │              │  │
│   │ 2. Created/modified │                │ 2. ALL linked│  │
│   │    < 7 days         │                │    Tasks    │  │
│   └─────────────────────┘                │    completed│  │
│                                          │    or       │  │
│   Option C (RECOMMENDED):                │    abandoned│  │
│   Recency + Task Status                  └──────────────┘  │
│   Default window: 7 days                                       │
│                                                              │
│   Cold info still searchable, just lower priority             │
└─────────────────────────────────────────────────────────────┘
```

### OQ-4: How does AI confirm Picture achievement?

**Problem:** Who determines that current state matches the Picture?

```
┌─────────────────────────────────────────────────────────────┐
│                 OQ-4: Picture Completion                    │
│                                                              │
│   Option A (RECOMMENDED): AI Self-Assessment                │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  AI: "Based on current state, Picture appears      │   │
│   │      achieved. Should we mark this Task completed?" │   │
│   │                                                      │   │
│   │  User: [Confirms] or [Rejects with feedback]       │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   Option B: Evidence-Based (if Picture has verifiable criteria│
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Picture: "Tests pass"                              │   │
│   │  Evidence: CI result = pass  ✓                      │   │
│   │  System auto-completes                              │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### OQ-5: Can multiple Tasks be in-progress simultaneously?

**Problem:** Is there one "current" Task, or can multiple be active?

```
┌─────────────────────────────────────────────────────────────┐
│              OQ-5: Multiple Active Tasks                    │
│                                                              │
│   Option C (RECOMMENDED): Task Forest                        │
│                                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Root Tasks (all in-progress):                       │   │
│   │                                                      │   │
│   │    Task A ──▶ [subtasks]                           │   │
│   │    Task B ──▶ [subtasks]                           │   │
│   │    Task C ──▶ [subtasks]                           │   │
│   │                                                      │   │
│   │  AI presents all at session start                    │   │
│   │  User/AI selects which to focus on                   │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   NOT Option A (single focus) — artificial constraint        │
│   NOT Option B (stack LIFO) — what if A and C both needed?  │
└─────────────────────────────────────────────────────────────┘
```

### OQ-6: How does the system handle context switching?

**Problem:** When user shifts context, how is the new situation recognized?

```
┌─────────────────────────────────────────────────────────────┐
│              OQ-6: Context Switching                         │
│                                                              │
│   Scenario:                                                  │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Task A: in-progress                                │   │
│   │  User: "Actually, let's work on Y instead"         │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
│   Option C (RECOMMENDED): Task Tree handles naturally        │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                      │   │
│   │  "Working on Y"                                     │   │
│   │    ├── Creates new Task Y  (or finds existing Y)   │   │
│   │    └── A remains in tree                           │   │
│   │          ├── completed?  → no action needed          │   │
│   │          ├── abandoned? → no action needed          │   │
│   │          └── in-progress → simply not current      │   │
│   │                                                      │   │
│   │  Can return to A later without state confusion      │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Picture Interaction Design (Heavy)

See detailed design in: `docs/brainstorms/004-picture-interaction-design.md`

### 8.1 The Heaviest Interaction

Picture is the **completion standard** — if it's wrong, the entire goal-tracking system fails.

| Interaction Type | Weight | Example | Trigger |
|-----------------|--------|---------|---------|
| **Heavy** | ~10-30 min | Picture construction | New task, skill invoke |
| **Medium** | ~5 min | Achievement check | Evidence threshold |
| **Light** | <1 min | Task confirmation | Uncertainty |
| **Zero** | 0 | Silent capture | 99% of ops |

### 8.2 Picture Construction Triggers

```
T1: New Task Detected    → /skill, new project mentioned
T2: Task has no Picture  → First access
T3: Picture obsolete     → Context shift
T4: Progress stalled     → 7+ days no progress
```

### 8.3 Picture Scaffold (Phased Questions)

```
Phase 1 (必答): Outcome
  Q: "Done是什么样？"
  Q: "你怎么知道达成了？"

Phase 2 (建议): Boundaries
  Q: "什么明确不在范围？"

Phase 3 (可选): Metrics
  Q: "怎么衡量成功？"
```

### 8.4 Achievement vs. Completion

```
COMPLETION: All subtasks done (mechanical)
ACHIEVEMENT: Picture criteria met (evidence-based)

Example:
  ✓ All subtasks done
  ✓ Tests pass
  ✗ But user says "still slow" → NOT achieved
```

### 8.5 Event/Skill Triggers

```
/ce:brainstorm → explore intent → trigger Picture scaffold
/ce:plan      → build intent  → trigger Picture scaffold
/debug        → fix intent    → usually subtask
/research     → learn intent  → trigger Picture
```

---

## 9. Non-Goals (Out of Scope)

These are explicitly NOT part of this system:

1. **Complete memory capture** — Not trying to store everything
2. **Universal search** — Search is Task-contextual, not global
3. **Human-readable memory dumps** — Memory is for AI consumption
4. **Multi-user sync** — Single-agent focus for now
5. **Automatic picture generation** — AI proposes, user confirms

---

## 10. Success Criteria

A mem0ress session should answer:

```
┌─────────────────────────────────────────────────────────────┐
│              At Any Moment, System Answers:                  │
│                                                              │
│   1. "Who am I?"                                           │
│      → Current Task identity and Picture                     │
│                                                              │
│   2. "Where am I?"                                          │
│      → Status, subtasks, progress toward Picture            │
│                                                              │
│   3. "What do I know?"                                     │
│      → Relevant Info (hot, tagged)                         │
│                                                              │
│   4. "Where am I going?"                                    │
│      → Subtasks breakdown, Picture criteria                  │
│                                                              │
│   If these 4 questions are answerable → system is working  │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. Open Questions Summary

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

## 12. Next Steps

1. **Validate core concepts** with user
2. **Resolve open questions** marked above
3. **Define data schema** for Task, Info, Link
4. **Design Plane discovery algorithm**
5. **Prototype AI dialogue flow**

---

## References

- Previous analysis: `docs/brainstorms/001-memory-systems-design-analysis.md`
- MemPalace source: `~/code/ai/mempalace/`
- Claude-Mem source: `~/code/ai/claude-mem/`
