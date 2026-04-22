# Memory Systems Design Analysis: MemPalace vs Claude-Mem

**Date:** 2026-04-22
**Status:** Research Document
**Purpose:** Inform mem0ress architecture decisions

---

## Executive Summary

MemPalace and Claude-Mem represent two fundamentally different philosophies on AI memory:

| Dimension | MemPalace | Claude-Mem |
|-----------|-----------|------------|
| **Storage** | ChromaDB (vectors) + SQLite (KG) | SQLite + Chroma (vectors) |
| **Retrieval** | Passive: AI queries on demand | Active: context injected proactively |
| **Compression** | AAAK lossy abbreviations | LLM semantic summarization |
| **Capture** | `mine` command (batch/ingest) | Lifecycle hooks (continuous) |
| **Organization** | Palace metaphor (wing/room/hall) | Progressive disclosure layers |
| **Knowledge Graph** | Temporal entity triples | None (observations only) |
| **Benchmark** | 96.6% LongMemEval R@5 (raw) | Not disclosed |
| **License** | MIT | AGPL-3.0 |

**Core insight:** MemPalace bets on verbatim storage + structure; Claude-Mem bets on continuous capture + summarization. Neither approach is obviously superior — they optimize for different use cases.

---

## 1. System Architecture

### 1.1 MemPalace Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         MemPalace                                │
│                                                                  │
│  ┌──────────┐     ┌──────────┐     ┌────────────────────────┐  │
│  │  CLI     │────▶│  Miner   │────▶│  ChromaDB              │  │
│  │  (init, │     │  (batch) │     │  mempalace_drawers     │  │
│  │   mine,  │     └──────────┘     │  (verbatim chunks)     │  │
│  │   search)│                     └────────────────────────┘  │
│  └──────────┘                                                      │
│                                                                  │
│  ┌──────────┐     ┌──────────┐     ┌────────────────────────┐  │
│  │  MCP     │────▶│ Searcher │────▶│  SQLite               │  │
│  │  Server  │     │          │     │  knowledge_graph      │  │
│  │  (18 tools)    └──────────┘     │  (entity triples)      │  │
│  └──────────┘                     └────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  4-Layer Memory Stack (wake-up context)                  │  │
│  │  L0: identity.txt (~50 tokens)                          │  │
│  │  L1: essential drawers (~500-800 tokens AAAK)          │  │
│  │  L2: room-filtered search (~200-500 tokens on-demand)  │  │
│  │  L3: deep semantic search (unlimited, explicit query)   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Key architectural traits:**
- **Passive storage**: Drawers are stored, not pushed into context. AI must explicitly query.
- **Batch ingestion**: `mempalace mine` is a batch operation. Not real-time.
- **No hooks by default**: AI integration is via MCP tools, not automatic capture.
- **Dual storage**: ChromaDB for verbatim retrieval, SQLite for structured relationships.

### 1.2 Claude-Mem Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Claude-Mem                                 │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Claude Code Lifecycle Hooks                               │  │
│  │  SessionStart → UserPromptSubmit → PostToolUse            │  │
│  │  PreToolUse → Stop → SessionEnd                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Worker Service (port 37777, Bun runtime)                │  │
│  │                                                            │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │  │
│  │  │ Database   │  │  Session   │  │  SDK Agent         │  │  │
│  │  │ Manager    │  │  Manager   │  │  (Claude Code CLI) │  │  │
│  │  │ (SQLite)   │  │            │  │                    │  │  │
│  │  └────────────┘  └────────────┘  └────────────────────┘  │  │
│  │                       │                    │               │  │
│  │                       ▼                    ▼               │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │  Pending Message Queue (observations/summaries)     │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  │                                                            │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │  │
│  │  │  Search    │  │  SSE       │  │  Transcript        │  │  │
│  │  │  Manager   │  │  Broadcaster│  │  Watcher          │  │  │
│  │  └────────────┘  └────────────┘  └────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  MCP Search Tools (search, timeline, get_observations)    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Web Viewer UI (port 37777)                               │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Key architectural traits:**
- **Active capture**: Hooks fire on session events, continuously capturing.
- **Event-driven**: Pending message queue with event emitters — no polling.
- **LLM-in-the-loop**: SDK Agent uses Claude Code CLI itself to generate observations/summaries.
- **Single storage**: SQLite primary (observations, summaries, sessions), Chroma for vector search.

---

## 2. Data Models

### 2.1 MemPalace Drawer Model

```
Drawer ID:   drawer_{wing}_{room}_{MD5(content)[:16]}
Content:     Verbatim chunk text (800 chars, 100 overlap)
Metadata:
  wing          - Project/person name
  room          - Topic/aspect
  hall          - (optional) Thematic corridor
  source_file   - Absolute path
  source_mtime  - File modification time
  chunk_index   - Position in file sequence
  added_by      - "mempalace" | "mcp" | etc.
  filed_at      - ISO datetime
```

**Design rationale:**
- Content-based ID = idempotent re-mining (same content = same ID)
- No summaries ever stored — verbatim only
- File mtime for file-level dedup, not content-level

### 2.2 Claude-Mem Observation Model

```sql
CREATE TABLE observations (
  id              INTEGER PRIMARY KEY,
  memory_session_id TEXT NOT NULL,
  project         TEXT NOT NULL,
  text            TEXT NOT NULL,           -- The actual observation
  type            TEXT NOT NULL,           -- decision|bugfix|feature|refactor|discovery|change
  title           TEXT,                    -- Generated summary title
  subtitle        TEXT,                    -- Generated subtitle
  facts           TEXT,                    -- Extracted facts
  concepts        TEXT,                    -- Extracted concepts
  files_touched   TEXT,                   -- File paths mentioned
  created_at      TEXT NOT NULL,
  created_at_epoch INTEGER NOT NULL,
  discovery_tokens INTEGER DEFAULT 0,      -- ROI metric
  relevance_count  INTEGER DEFAULT 0,       -- Feedback metric
  generated_by_model TEXT,                  -- Which model generated
  agent_type       TEXT,                   -- Subagent attribution
  agent_id         TEXT,                   -- Subagent ID
  content_hash     TEXT                    -- Deduplication
);
```

**Design rationale:**
- Rich structured fields (title, facts, concepts) enable selective disclosure
- `discovery_tokens` tracks LLM cost efficiency
- `relevance_count` enables feedback-driven importance
- Subagent fields allow attribution to specific agents

### 2.3 Knowledge Graph Schema (MemPalace only)

```sql
CREATE TABLE entities (
  id         TEXT PRIMARY KEY,
  name       TEXT NOT NULL,
  type       TEXT,           -- person|project|concept|etc.
  properties TEXT,           -- JSON additional properties
  created_at TEXT
);

CREATE TABLE triples (
  id           TEXT PRIMARY KEY,
  subject      TEXT REFERENCES entities(id),
  predicate    TEXT NOT NULL,  -- works_on|assigned_to|decided|etc.
  object       TEXT REFERENCES entities(id),
  valid_from   TEXT,
  valid_to     TEXT,
  confidence   REAL DEFAULT 1.0,
  source_closet TEXT,
  source_file  TEXT,
  extracted_at TEXT
);
```

**Temporal validity design:**
- `valid_from` / `valid_to` enable time-travel queries
- `as_of="2026-01-15"` returns only facts true at that date
- `invalidate()` sets `valid_to` — never deletes (preserves history)

---

## 3. Capture Mechanisms

### 3.1 MemPalace: Batch Mining

**`mempalace mine` flow:**

```
File/Directory Input
    │
    ▼
┌─────────────────────────────────────────┐
│  Chunking (miner.py)                    │
│  - 800 char chunks, 100 char overlap   │
│  - Paragraph boundary detection         │
│  - Skip chunks < 50 chars              │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Room Detection                         │
│  1. Folder path matches room name      │
│  2. Filename matches room name         │
│  3. Content keyword scoring            │
│  4. Fallback: "general"               │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Wing Assignment                        │
│  - CLI --wing flag                     │
│  - Keyword matching from wing_config   │
│  - Entity detection (person vs project) │
└─────────────────────────────────────────┘
    │
    ▼
ChromaDB Insert (upsert by drawer_id)
```

**Conversation mining (`mempalace mine --mode convos`):**

```
Chat Export (Claude.ai JSON, ChatGPT JSON, Slack, Codex JSONL)
    │
    ▼
┌─────────────────────────────────────────┐
│  Normalize (normalize.py)               │
│  - Convert 5 formats → standard format │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Chunking (convo_miner.py)              │
│  - Exchange-pair mode: user+AI = 1 chunk│
│  - General mode: extract 5 memory types │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Room Detection                         │
│  - Topic keyword scoring                │
│  - Memory type as room (general mode)  │
└─────────────────────────────────────────┘
    │
    ▼
ChromaDB Insert
```

**General extraction (no LLM):**

```python
# 5-type classifier with keyword matching
TYPE_MARKERS = {
    "decision": ["decided", "instead of", "because", "architecture", "trade-off"],
    "preference": ["I prefer", "always use", "never do", "my rule is"],
    "milestone": ["it works", "fixed", "finally", "first time", "breakthrough"],
    "problem": ["bug", "doesn't work", "root cause", "the fix"],
    "emotional": ["love", "scared", "proud", "I feel", "I wish"]
}

# Disambiguation: resolved problem + positive = milestone
# Prose-only scoring (code lines filtered out)
```

### 3.2 Claude-Mem: Hook-Driven Capture

**Hook sequence per session:**

```
SessionStart
  ├─ smart-install.js     (dependency check)
  ├─ worker start         (spawn daemon)
  └─ context inject       (L0+L1 from prior sessions)

UserPromptSubmit
  └─ session-init         (create/fetch session record, start SDK Agent)

PostToolUse
  └─ observation         (queue tool data → SDK Agent → LLM extract)

Stop
  └─ summarize           (queue summary request → SDK Agent → LLM extract)

SessionEnd
  └─ session-complete    (cleanup, 1.5s cap)
```

**SDK Agent observation extraction:**

```typescript
// SDK Agent uses Claude Code CLI itself as the LLM
for await (const message of queryResult) {
  if (message.type === 'assistant') {
    // Parse <observation>...</observation> XML blocks
    // Store to SQLite observations table
  }
}
```

**Prompt template pattern:**

```typescript
// buildInitPrompt: Sets up observer role
// buildObservationPrompt: Each tool use becomes observed content
// buildSummaryPrompt: Session end → <summary> XML
// buildContinuationPrompt: Maintain context across SDK prompts
```

**Key insight:** The SDK Agent doesn't call an API directly — it spawns Claude Code CLI processes. This means Claude-Mem uses Claude to observe Claude, which is clever but architecturally unusual.

---

## 4. Retrieval Patterns

### 4.1 MemPalace: Palace-Native Search

**Layer 1 — Semantic search with wing/room filtering:**

```python
# searcher.py
def search_memories(query, wing=None, room=None, n_results=10):
    where_filter = {}
    if wing:  where_filter["wing"] = wing
    if room:  where_filter["room"] = room

    results = chroma_db.query(
        query_texts=[query],
        n_results=n_results,
        where=where_filter  # Metadata filtering BEFORE vector search
    )
    # Returns: ids, documents, distances, metadata
```

**Layer 2 — Palace graph traversal:**

```python
# palace_graph.py
def traverse_graph(start_room, wing, max_hops=3):
    """BFS from start room, following halls within wing"""
    visited = {start_room}
    queue = [(start_room, 0)]
    while queue:
        room, depth = queue.pop(0)
        if depth >= max_hops:
            continue
        for hall in get_halls(room, wing):
            for adjacent_room in get_rooms_via_hall(hall, wing):
                if adjacent_room not in visited:
                    visited.add(adjacent_room)
                    queue.append((adjacent_room, depth + 1))
    return visited

def find_tunnels(wing_a, wing_b):
    """Find rooms that appear in BOTH wings = tunnels between them"""
    rooms_a = set(get_rooms(wing_a))
    rooms_b = set(get_rooms(wing_b))
    return rooms_a & rooms_b  # Intersection = tunnels
```

**Layer 3 — 4-layer wake-up stack:**

```python
# layers.py
def wake_up(wing=None):
    # L0: Always loaded (~50 tokens)
    l0 = open(identity_path).read()

    # L1: Essential story (~500-800 tokens AAAK compressed)
    l1_zettels = get_top_drawers(wing=wing, limit=15, sort="importance")
    l1 = compress_aaak(l1_zettels)

    # L2: On-demand room recall (when topic mentioned)
    # L3: Deep search (explicit query only)

    return f"{l0}\n\n{l1}"
```

### 4.2 Claude-Mem: 3-Layer Progressive Disclosure

**Layer 1 — Compact index (search tool):**

```typescript
// SearchManager.ts
async search(query, options): Promise<SearchResult[]> {
  // Returns ~50-100 tokens per result
  // Just IDs, titles, dates — no full content
  const results = await this.queryChroma(query, 100, whereFilter);
  return results.map(r => ({
    id: r.id,
    title: r.title,
    type: r.type,
    date: r.created_at,
    score: r.distance
  }));
}
```

**Layer 2 — Timeline context (timeline tool):**

```typescript
// Returns chronological context around anchor
// Groups observations by date
// Shows what was happening in a time window
// ~200-300 tokens per result
```

**Layer 3 — Full observation (get_observations tool):**

```typescript
// Fetches ONLY for filtered IDs (~500-1000 tokens per result)
// Batch multiple IDs to amortize cost
get_observations(ids: number[])
```

**Token efficiency analysis:**

| Tool | Tokens/result | Purpose |
|------|--------------|---------|
| `search` | ~50-100 | Index browsing |
| `timeline` | ~200-300 | Temporal context |
| `get_observations` | ~500-1000 | Deep dive |

**Progressive disclosure configuration:**

```json
// ~/.claude-mem/settings.json
{
  "CLAUDE_MEM_CONTEXT_OBSERVATIONS": 10,
  "CLAUDE_MEM_CONTEXT_FULL_COUNT": 3,
  "CLAUDE_MEM_CONTEXT_SESSION_COUNT": 5,
  "CLAUDE_MEM_CONTEXT_SHOW_LAST_SUMMARY": true,
  "CLAUDE_MEM_CONTEXT_SHOW_LAST_MESSAGE": true
}
```

---

## 5. Memory Stack Design

### 5.1 MemPalace: L0–L3 Progressive Disclosure

```
┌─────────────────────────────────────────────────────────────┐
│  Context Window (~200K tokens for Claude)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  L0: Identity (~50 tokens)                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Who am I? Plain text user wrote.                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  L1: Critical Facts (~500-800 tokens AAAK)                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 15 most important drawers, room-grouped, AAAK comp.  │   │
│  │ Wing|Poom|Date|Zettel content...                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  L2: Room Recall (~200-500 tokens, on-demand)              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ChromaDB search within wing+room                    │   │
│  │ Triggered when topic mentioned                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  L3: Deep Search (~unlimited, explicit query)              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Full palace semantic search                         │   │
│  │ Triggered by explicit /search command               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Wake-up cost: ~600-900 tokens total                       │
│  Leaves 95%+ of context for actual work                    │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Claude-Mem: Context Injection Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Context Window                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer: Header                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Token economics summary                              │   │
│  │ "N observations, M sessions, ~X tokens"             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Layer: Timeline                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Recent observations grouped by date                  │   │
│  │ "Yesterday: 3 observations..."                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Layer: Full Observations (N most recent)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Complete narrative + facts for top N                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Layer: Session Summary                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Last session: request/completed/learned/next_steps   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Layer: Prior Message                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Last assistant message from prior session           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Injection triggered: SessionStart hook                    │
│  Amount controlled by CLAUDE_MEM_CONTEXT_* settings       │
└─────────────────────────────────────────────────────────────┘
```

**Key difference:** MemPalace's L0-L3 is a pull model (AI queries when needed); Claude-Mem's layers are a push model (injected at session start).

---

## 6. Key Design Decisions

### 6.1 Verbatim vs. Summary

**MemPalace: Never summarize**

```python
# miner.py comment
# "No summaries. Ever."
# Philosophy: verbatim can always be re-summarized later,
# but a summary cannot recover the original
```

**Claude-Mem: Always summarize**

```typescript
// ResponseProcessor.ts
// Parse <observation>...</observation> blocks
// Extract: type, title, subtitle, facts, narrative, concepts
// Store structured summary fields, NOT raw transcript
```

**Trade-off analysis:**

| | MemPalace | Claude-Mem |
|--|-----------|------------|
| **Pros** | Fidelity preserved; no loss from summarization errors | Compact; fits more in context |
| **Cons** | Larger storage; retrieval returns full chunks | Irreversible information loss |
| **Recall** | 96.6% (LongMemEval, raw mode) | Not disclosed |
| **Best for** | Technical accuracy; audit trails | Quick context; limited windows |

### 6.2 Palace Metaphor vs. Progressive Disclosure

**MemPalace: Spatial organization (wing/room/hall/tunnel)**

```
Wing: Person or project
  └── Room: Topic within wing
        └── Hall: Connections between rooms within wing
        └── Tunnel: Connections BETWEEN wings
        └── Closet: Summary pointing to drawer
        └── Drawer: Verbatim content
```

**Claude-Mem: Temporal organization (layers by recency/importance)**

```
Session Start
  └── Header: Token economics
  └── Timeline: Recent observations by date
  └── Full: N most recent complete observations
  └── Summary: Last session's outcome
  └── Prior: Last assistant message
```

**Trade-off analysis:**

| | Palace Metaphor | Progressive Disclosure |
|--|-----------------|----------------------|
| **Strength** | Structural recall (+34% R@10 with wing+room filter) | Token efficiency |
| **Weakness** | Requires pre-defined taxonomy | Loses structural relationships |
| **Best for** | Cross-session continuity; navigating by topic | Quick context loading |
| **Query model** | Pull (AI asks) | Push (injected at start) |

### 6.3 Hook-Driven vs. Batch Mining

**Claude-Mem: Continuous hook capture**

```typescript
// Hook fires on PostToolUse
// Queues observation request
// SDK Agent processes asynchronously
// Zero latency to AI session
```

**MemPalace: Batch mining**

```bash
# User runs manually or via cron
mempalace mine ~/projects/myapp
# Or via hooks (optional)
mempalace mine $MEMPAL_DIR
```

**Trade-off analysis:**

| | Hook-Driven | Batch Mining |
|--|-------------|-------------|
| **Pros** | Always current; no manual steps | User controls when; can audit before ingest |
| **Cons** | Complex; tied to specific tools; potential overhead | Stale; requires discipline |
| **Complexity** | High (6 hooks, worker daemon, event queue) | Low (single command) |

### 6.4 Knowledge Graph: Temporal vs. None

**MemPalace: Full temporal KG**

```python
# Temporal validity windows
kg.add_triple("Kai", "works_on", "Orion", valid_from="2025-06-01")
kg.invalidate("Kai", "works_on", "Orion", ended="2026-03-01")

# Query as of a date
kg.query_entity("Kai", as_of="2026-01-15")
# → [Kai → assigned_to → auth-migration (active in Jan)]
# → NOT [Kai → works_on → Orion (ended March)]
```

**Claude-Mem: No KG**

```typescript
// Only observations with created_at timestamps
// No entity resolution
// No temporal validity
// No relationship triples
```

**Trade-off analysis:**

| | Temporal KG | No KG |
|--|-------------|-------|
| **Pros** | Historical queries; fact expiration; entity tracking | Simpler; less storage |
| **Cons** | More complex; entity extraction is hard | No cross-reference; stale facts remain |
| **Use case** | Long-term projects; team memory | Short sessions; personal use |

---

## 7. AAAK Dialect Analysis

### 7.1 What AAAK Is

**NOT lossless compression.** A lossy structured summary format:

```
Header: wing|room|date|source_file_stem
Zettel: entity_codes|topic_keywords|"key_sentence"|emotion_codes|+FLAGS
```

**Example:**
```
WING_CODE|auth-migration|2026-01-15|clerk_migration
KAI→MGR,PRI→APRV|clerk,oauth,migrate|"Team chose Clerk over Auth0 for DX"|joy|ORIGIN,DECISION
```

**Entity codes:** 3-letter uppercase (KAI, PRI, MGR = Manager, APRV = Approved)
**Emotion codes:** vul, joy, fear, trust (Plutchik's 8 emotions)
**Flags:** ORIGIN, CORE, SENSITIVE, PIVOT, GENESIS, DECISION, TECHNICAL

### 7.2 AAAK Properties

1. **Human-readable without decoding** — Any LLM can understand it
2. **Readable by Claude, GPT, Gemini, Llama, Mistral** — No decoder needed
3. **Designed for repeated entities at scale** — Entity codes amortize over many mentions
4. **Lossy** — Original verbatim not recoverable

### 7.3 AAAK Benchmark Reality

| Mode | LongMemEval R@5 | Notes |
|------|----------------|-------|
| Raw (verbatim) | **96.6%** | This is the headline number |
| AAAK | 84.2% | 12.4 point regression |
| Hybrid + Haiku rerank | **100%** | With LLM reranking |

**Honest status (April 2026):**
- AAAK overhead (codes, separators) costs more than it saves at small scales
- AAAK saves tokens at scale (repeated entities across thousands of sessions)
- Raw verbatim is the storage default — AAAK is a separate compression layer

---

## 8. Retrieval Benchmark Insights

### 8.1 MemPalace LongMemEval Results

```
LongMemEval R@5: 96.6% (raw, zero API calls)
LoCoMo R@10: 60.3% (raw, session level)
Personal palace R@10: 85% (heuristic bench)
Palace structure impact: +34% R@10 (wing+room filtering)
```

### 8.2 What the +34% Palace Boost Means

```
Search all closets:          60.9%  R@10
Search within wing:          73.1%  (+12%)
Search wing + hall:          84.8%  (+24%)
Search wing + room:          94.8%  (+34%)
```

**Key insight:** Metadata filtering (wing+room) is a standard ChromaDB feature. The +34% comes from using it, not from a novel retrieval mechanism. The palace metaphor provides the taxonomy that makes filtering effective.

### 8.3 Recall vs. Latency

MemPalace benchmark `test_search_latency_vs_size.py`:
- Tests at 500/1000/2500/5000 drawers
- Measures p50, p95 latency
- Tests concurrent search (30 simultaneous queries, 4 threads)

**Implication:** ChromaDB PersistentClient thread safety is tested. At scale, concurrent access matters.

---

## 9. Architectural Patterns

### 9.1 Claude-Mem: Event-Driven Message Queue

```typescript
// SessionManager.queueObservation():
// 1. Persist to database FIRST (crash-safe)
// 2. Emit 'message' event on in-memory emitter

const messageId = this.getPendingStore().enqueue(sessionDbId, ...); // FIRST
emitter?.emit('message');  // SECOND

// SDK Agent iterator awaits emitter events — no polling
// Generator exit invariant: every exit must either restart or terminate
```

**Why persist before emit?**
- If worker crashes after emit but before persist, data is lost
- Persisting first ensures observations survive crashes
- The cost: slight latency increase

### 9.2 MemPalace: Content-Based ID Generation

```python
drawer_id = f"drawer_{wing}_{room}_{hashlib.md5(content.encode()).hexdigest()[:16]}"
```

**Properties:**
- Idempotent re-mining: same content = same ID = upsert is no-op
- Content deduplication across files (but source_file differs in metadata)
- No update mechanism: changed content = new ID, old drawer persists

### 9.3 Claude-Mem: Fallback Chain Pattern

```
SDK Agent (Claude Code CLI)
    ↓ (fails)
Gemini Agent
    ↓ (fails)
OpenRouter Agent
    ↓ (fails)
Mark abandoned, terminate session
```

**Restart guard:**
```typescript
// Windowed rate limiter prevents runaway loops
const restartAllowed = session.restartGuard.recordRestart();
if (!restartAllowed) {
  this.terminateSession(sessionDbId, 'max_restarts_exceeded');
}
```

---

## 10. Limitations and Known Issues

### MemPalace Limitations

| Issue | Description | Severity |
|-------|-------------|----------|
| No content update | File changes → new chunks, old persist | Medium |
| No stale cleanup | Only manual delete exists | Low |
| Hall metadata unused | Stored but no active query path | Low |
| Entity detection requires prose | Code files excluded | Medium |
| Single embedding model | No domain-specific embeddings | Low |
| Hooks tied to Claude Code/Codex | Not tool-agnostic | High |

### Claude-Mem Limitations

| Issue | Description | Severity |
|-------|-------------|----------|
| SDK Agent uses Claude to observe Claude | Architectural oddity | Medium |
| No knowledge graph | Can't do entity relationship queries | High |
| No temporal validity | Facts never expire | Medium |
| Schema repair needs Python | Some recovery requires python script | Low |
| Mode taxonomy is opaque | code.json structure not obvious | Low |

---

## 11. Synthesis: What Both Systems Get Right

### 11.1 MemPalace Strengths

1. **Verbatim storage preserves fidelity** — 96.6% recall证明 raw > summary for retrieval
2. **Palace metaphor provides structure** — +34% from metadata filtering alone
3. **Temporal KG is powerful** — Historical queries are essential for long-term projects
4. **No LLM dependency** — Works offline, no API costs
5. **Idempotent storage** — Safe to re-mine

### 11.2 Claude-Mem Strengths

1. **Continuous capture** — Hooks ensure memories are always current
2. **Progressive disclosure** — Token-efficient context loading
3. **Event-driven architecture** — Zero latency, no polling
4. **Rich observation schema** — title, facts, concepts enable selective use
5. **Web viewer** — Real-time memory stream is genuinely useful

---

## 12. Open Questions for mem0ress

1. **Pull vs. Push:** Should mem0ress be passive (query on demand) or active (inject at session start)?
2. **Verbatim vs. Summary:** Is 96.6% recall proof that summaries are always worse?
3. **KG necessity:** Is temporal entity tracking worth the complexity?
4. **Hook dependency:** Should capture be tied to specific tools (Claude Code) or tool-agnostic?
5. **AAAK viability:** Is lossy compression worth it for context loading, or should raw verbatim be the only mode?
6. **Single embedding:** Should mem0ress support custom embedding models for domain-specific terminology?

---

## References

- MemPalace README: `~/code/ai/mempalace/README.md`
- MemPalace Core: `~/code/ai/mempalace/mempalace/`
- Claude-Mem README: `~/code/ai/claude-mem/README.md`
- Claude-Mem Source: `~/code/ai/claude-mem/src/`, `~/code/ai/claude-mem/plugin/`
