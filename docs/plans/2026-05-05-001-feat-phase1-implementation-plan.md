---
title: Phase 1 Implementation - Core Infrastructure
type: feat
status: active
date: 2026-05-05
origin: docs/brainstorms/005-phase1-requirements.md
---

# Phase 1 Implementation - Core Infrastructure

## Overview

Implementing the core infrastructure layer of mem0ress — the cognitive OS kernel that uses pure text files (Markdown + YAML frontmatter) to express cognitive state. Phase 1 establishes the architectural foundation: data models, storage layer with optimistic locking, TaskService with Protocol interface, and PlaneAssembler.

## Problem Frame

How to build a file-based cognitive state management system with:
- Pydantic models for strict schema validation
- Protocol-based interface segregation (Adapter-ready)
- Optimistic locking via SHA-256 for concurrent-write safety
- YAML frontmatter parsing for manifest files
- Directory structure as the sole source of truth for task relationships

## Requirements Trace

- R1-R7: Directory structure and association principles
- R8-R13: Core Models (TaskManifest, CognitiveTriad, TodoItem, Gotcha, TaskStatus)
- R14-R18: Storage Layer (SubstrateParser, fs.py with optimistic lock)
- R19-R22: TaskService (TaskServiceProtocol, TaskServiceImpl)
- R23-R25: Plane Assembler (compile_status_plane)

## Scope Boundaries

- No LLM integration (Phase 4)
- No Harness verification (Phase 5)
- No CLI adapters / slash commands (Phase 6+)
- No GotchaService (deferred)
- No GitOps (Phase 3)

## Context & Research

### Relevant Code and Patterns

- **spec.md Section 7.2.2** — Optimistic locking using state hash or mtime
- **spec.md Section 5.3** — YAML Frontmatter schema definition
- **phase1.md** — Implementation design with SubstrateParser, PlaneAssembler, schema
- **phase3.md** — SubstrateIO with safe_write and ConflictError (reference for fs.py design)

### External References

- Pydantic v2 with `frozen=True`, `extra="forbid"` for immutable models
- Python Protocol with `@runtime_checkable` for interface segregation
- SHA-256 via `hashlib.sha256()` for optimistic lock checksums
- Custom frontmatter parser using `re` + `yaml.safe_load()` (no python-frontmatter dependency)

### Technology Stack

- **Python**: 3.12+
- **Package manager**: uv (per project gitignore conventions)
- **Dependencies**: pydantic>=2.10, pyyaml>=6.0, pytest>=8.0, ruff>=0.8
- **No async in Phase 1** — synchronous file I/O for simplicity

## Key Technical Decisions

- **src-layout** — `src/mem0ress/` for package, `tests/` for tests
- **Immutable Pydantic models** — `frozen=True` for TaskManifest/Gotcha, matching optimistic locking design
- **SHA-256 checksum** — Used for optimistic lock verification (not mtime, as spec allows hash or mtime)
- **Custom frontmatter parser** — No python-frontmatter; simple regex剥离 YAML
- **Single file per concern** — Each module is single-purpose (parser.py, fs.py, etc.)
- **TaskServiceImpl delegates to storage layer** — fs.py handles file I/O, TaskServiceImpl orchestrates business logic

## Open Questions

### Resolved During Planning

- **Python version**: 3.12+ (modern typing, no legacy concerns)
- **Package manager**: uv (community standard, per gitignore patterns)
- **Project structure**: src-layout with `src/mem0ress/`, `tests/`
- **Hash algorithm**: SHA-256 for optimistic locking

### Deferred to Implementation

- Exact method naming conventions (TaskServiceImpl methods will follow protocol)
- Error message wording for ConflictError
- Todo list body section header format (`# Todos` vs `# Tasks`)

## Implementation Units

- [ ] **Unit 1: Project Scaffolding**

**Goal:** Establish the project structure, package configuration, and development tooling

**Requirements:** Dependencies (R0 - implicit), Python 3.12+

**Dependencies:** None

**Files:**
- Create: `pyproject.toml`
- Create: `src/mem0ress/__init__.py`
- Create: `src/mem0ress/core/__init__.py`
- Create: `src/mem0ress/core/schema.py`
- Create: `src/mem0ress/storage/__init__.py`
- Create: `src/mem0ress/storage/parser.py`
- Create: `src/mem0ress/storage/fs.py`
- Create: `src/mem0ress/service/__init__.py`
- Create: `src/mem0ress/service/protocol.py`
- Create: `src/mem0ress/service/impl/__init__.py`
- Create: `src/mem0ress/service/impl/task_service.py`
- Create: `src/mem0ress/plane.py`
- Create: `tests/__init__.py`
- Create: `.python-version`

**Approach:**
- Use uv to initialize project structure
- Define pyproject.toml with dependencies: pydantic, pyyaml, pytest, ruff
- Create all `__init__.py` files as package markers
- Use hatchling as build backend (per design.md)

**Patterns to follow:**
- pyproject.toml format from docs/design/design.md

**Test scenarios:**
- Test expectation: none — scaffolding has no behavioral logic to test

**Verification:**
- `python -c "from mem0ress import core"` imports without error
- `ruff check src/` reports no errors
- `pytest --collect-only tests/` discovers no test failures

---

- [ ] **Unit 2: Core Models (schema.py)**

**Goal:** Define Pydantic models for TaskManifest, CognitiveTriad, TodoItem, Gotcha, TaskStatus

**Requirements:** R8-R13

**Dependencies:** None

**Files:**
- Modify: `src/mem0ress/core/schema.py`

**Approach:**
- Define `TaskStatus` enum with `created`, `in-progress`, `completed`, `abandoned`
- Define `CognitiveTriad` with `picture: str`, `requirements: list[str]`, `constraints: list[str]`
- Define `TodoItem` with `text: str`, `done: bool = False`
- Define `TaskManifest` with `id`, `type`, `status`, `cognitive_triad`, `gotcha_refs`, `todos`
- Define `Gotcha` with `id`, `type`, `task_id`, `timestamp`, `content`
- Use `model_config = ConfigDict(frozen=True, extra="forbid")` for immutability

**Patterns to follow:**
- Pydantic v2 patterns: `BaseModel`, `Field`, `ConfigDict`
- Use `StrEnum` or plain `Enum` for `TaskStatus` (value is str)

**Test scenarios:**
- Happy path: TaskManifest.model_validate() with valid data succeeds
- Happy path: Gotcha.model_validate() with valid data succeeds
- Edge case: TaskManifest with missing optional fields uses defaults
- Edge case: TaskStatus enum accepts all four values
- Error path: TaskManifest with extra field raises ValidationError (extra="forbid")
- Error path: CognitiveTriad with non-list requirements raises ValidationError

**Files for testing:**
- Create: `tests/unit/test_schema.py`

**Verification:**
- All test cases pass
- `ruff check src/mem0ress/core/schema.py` passes

---

- [ ] **Unit 3: SubstrateParser (storage/parser.py)**

**Goal:** Bidirectional conversion between TaskManifest and YAML frontmatter + markdown body

**Requirements:** R14, R15, R16

**Dependencies:** Unit 2 (schema.py must exist)

**Files:**
- Modify: `src/mem0ress/storage/parser.py`

**Approach:**
- Implement `FRONTMATTER_PATTERN` regex to剥离 YAML frontmatter
- `parse_manifest(file_path: Path) -> TaskManifest`:
  - Read file content
  - Extract YAML frontmatter and markdown body
  - Parse YAML with `yaml.safe_load()`
  - Parse todo list from markdown body (pattern: `- [x] text` or `- [ ] text`)
  - Construct and return TaskManifest
  - id field is set to directory name (filesystem is source of truth)
- `serialize_manifest(manifest: TaskManifest) -> str`:
  - Build YAML dict from manifest fields
  - Serialize to YAML string
  - Build markdown body from todos (`- [x]` or `- [ ]`)
  - Return combined frontmatter + body string
  - id always set to directory name (ensures round-trip consistency)

**Patterns to follow:**
- Regex-based frontmatter parsing (no python-frontmatter dependency)
- `yaml.safe_load()` for YAML parsing (safe, no arbitrary code execution)

**Test scenarios:**
- Happy path: parse_manifest round-trips a complete TaskManifest
- Happy path: serialize_manifest produces valid frontmatter format
- Happy path: todo `- [x] Done` and `- [ ] Pending` parse correctly
- Edge case: `- [X]` (uppercase X) parses as done=True
- Edge case: `- [x]` with extra whitespace parses correctly
- Edge case: file with no frontmatter raises ValueError
- Error path: malformed YAML raises appropriate error
- Error path: todo line without brackets raises no error (silently skipped or raises — decide in implementation)

**Files for testing:**
- Create: `tests/unit/test_parser.py`
- Create: `tests/fixtures/sample_manifest.md` (test data)

**Verification:**
- All test cases pass
- parse_manifest and serialize_manifest are true inverses for valid input

---

- [ ] **Unit 4: Storage Layer with Optimistic Locking (storage/fs.py)**

**Goal:** File I/O with SHA-256-based optimistic lock to prevent concurrent overwrites

**Requirements:** R17, R18

**Dependencies:** Unit 3 (parser.py should exist for write verification)

**Files:**
- Modify: `src/mem0ress/storage/fs.py`

**Approach:**
- Define `ConflictError(Exception)` for optimistic lock failures
- `get_file_hash(file_path: Path) -> str`:
  - Read file bytes
  - Compute SHA-256 hash
  - Return hex string
- `safe_write(file_path: Path, content: str, expected_hash: str)`:
  - If file exists, compute current hash
  - Compare with expected_hash using constant-time comparison (hmac.compare_digest)
  - If mismatch, raise ConflictError with message showing expected vs actual
  - If match, write content to file
  - Return None (or new hash if needed)

**Patterns to follow:**
- `hashlib.sha256()` for hash computation
- `hmac.compare_digest()` for constant-time comparison (prevents timing attacks)
- No async — synchronous file operations for Phase 1

**Test scenarios:**
- Happy path: safe_write with matching hash succeeds
- Happy path: safe_write to new file (no existing hash check) succeeds
- Edge case: first write (file doesn't exist) succeeds without hash check
- Error path: safe_write with mismatched hash raises ConflictError with details
- Error path: safe_write to non-existent directory raises FileNotFoundError

**Files for testing:**
- Create: `tests/unit/test_fs.py`
- Create: `tests/fixtures/` directory for test files

**Verification:**
- ConflictError is raised and contains expected vs actual hash info
- Successful write leaves file with correct content
- No race condition between hash check and write (single process, no threading in Phase 1)

---

- [ ] **Unit 5: TaskService Protocol and Impl**

**Goal:** Define TaskServiceProtocol interface and implement TaskServiceImpl

**Requirements:** R19, R20, R21, R22

**Dependencies:** Units 2, 3, 4

**Files:**
- Modify: `src/mem0ress/service/protocol.py`
- Create: `src/mem0ress/service/impl/task_service.py`
- Modify: `src/mem0ress/service/impl/__init__.py`

**Approach:**

**protocol.py:**
```python
from typing import Protocol
from mem0ress.core.schema import TaskManifest

class TaskServiceProtocol(Protocol):
    def create_task(self, task_id: str, picture: str) -> TaskManifest: ...
    def get_task(self, task_id: str) -> TaskManifest: ...
    def update_todo(self, task_id: str, index: int, done: bool) -> TaskManifest: ...
    def update_cognitive_triad(self, task_id: str, picture: str, requirements: list[str], constraints: list[str]) -> TaskManifest: ...
    def get_all_tasks(self) -> list[TaskManifest]: ...
    def delete_task(self, task_id: str) -> None: ...
    def add_todo(self, task_id: str, text: str) -> TaskManifest: ...
    def remove_todo(self, task_id: str, index: int) -> TaskManifest: ...
```

**task_service.py:**
- `TaskServiceImpl` implements `TaskServiceProtocol`
- Init takes `substrate_root: Path` (default: `.mem0ress`)
- `create_task`: Create directory, references/ dir, index.md with default cognitive_triad (picture only, requirements/constraints empty)
- `get_task`: Use parser.parse_manifest on `substrate_root/tasks/<task_id>/index.md`
- `update_todo`: Read manifest, modify todos[index].done, serialize + safe_write with expected_hash
- `update_cognitive_triad`: Read manifest, update cognitive_triad fields, serialize + safe_write
- `get_all_tasks`: Scan `substrate_root/tasks/` for directories, parse each index.md, return list
- `delete_task`: Remove task directory (shutil.rmtree)
- `add_todo`: Append TodoItem to todos list, serialize + safe_write
- `remove_todo`: Remove todos[index], serialize + safe_write
- All mutation methods use `safe_write` with expected_hash for optimistic locking
- On ConflictError from safe_write, let it propagate to caller

**Patterns to follow:**
- Task directory layout: `substrate_root/tasks/<task_id>/index.md`
- `TaskExistsError` for duplicate create_task (custom exception class)
- FileNotFoundError for get_task on non-existent task

**Test scenarios:**
- Happy path: create_task creates directory structure and index.md
- Happy path: get_task returns correct TaskManifest
- Happy path: update_todo marks correct todo as done
- Happy path: get_all_tasks returns all task manifests
- Edge case: create_task with duplicate task_id raises TaskExistsError
- Edge case: get_task with non-existent task_id raises FileNotFoundError
- Edge case: update_todo with out-of-range index raises IndexError
- Edge case: get_all_tasks on empty substrate returns empty list
- Error path: update_todo with wrong expected_hash raises ConflictError
- Error path: concurrent modification detection via optimistic lock

**Files for testing:**
- Create: `tests/unit/test_task_service.py`
- Create: `tests/fixtures/` with sample index.md files

**Verification:**
- All TaskServiceProtocol methods are implemented
- Type checker confirms TaskServiceImpl satisfies TaskServiceProtocol
- Optimistic lock ConflictError propagates correctly

---

- [ ] **Unit 6: Plane Assembler**

**Goal:** Compile Status Plane — scan task tree and generate human-readable overview

**Requirements:** R23, R24, R25

**Dependencies:** Units 2, 3 (parser needed for scanning)

**Files:**
- Modify: `src/mem0ress/plane.py`
- Modify: `src/mem0ress/__init__.py` (export PlaneAssembler)

**Approach:**
- `PlaneAssembler.__init__(substrate_root: Path)` — store substrate root
- `compile_status_plane() -> str`:
  - Scan `substrate_root/tasks/` recursively for `index.md` files
  - Sort by path (natural tree order)
  - For each manifest, compute depth from relative path
  - Format: `■` for root tasks, `└─` for subtasks (depth > 0)
  - Show: task_id, status, picture (truncated to 50 chars if > 50), progress (done/total)
  - For subtasks, show parent constraint line
  - Append fixed system laws at end
- Handle `ref:` picture: if picture starts with `ref:`, show dehydration pointer text instead of content

**Patterns to follow:**
- Output format exactly as specified in Success Criteria R88
- Prefix characters: `■` for root, `└─` for subtasks
- Indent: 2 spaces per depth level

**Test scenarios:**
- Happy path: compile_status_plane produces correct format for single task
- Happy path: compile_status_plane shows tree structure with parent-child relationships
- Happy path: ref: picture shows dehydration pointer
- Edge case: empty substrate produces "当前基座为空" message
- Edge case: long picture text truncated to 50 chars
- Edge case: deeply nested subtasks show correct indentation

**Files for testing:**
- Create: `tests/unit/test_plane.py`
- Create: `tests/fixtures/plane/` with nested task structures

**Verification:**
- Output matches exactly the format in Success Criteria R88

---

- [ ] **Unit 7: Integration Tests**

**Goal:** Verify end-to-end behavior of TaskService + Storage + Parser

**Requirements:** All Success Criteria

**Dependencies:** Units 1-6 complete

**Files:**
- Create: `tests/integration/test_task_lifecycle.py`

**Approach:**
- Use temporary directory as substrate root
- Test complete task lifecycle: create -> get -> update_todo -> update_cognitive_triad -> delete
- Test optimistic locking: concurrent update scenarios
- Test plane assembly after multiple tasks

**Test scenarios:**
- Happy path: full task lifecycle works correctly
- Happy path: plane shows multiple tasks with correct tree structure
- Error path: optimistic lock prevents lost updates
- Error path: TaskExistsError on duplicate create

**Verification:**
- All integration tests pass
- No file handles left open
- Temporary directories cleaned up

---

## System-Wide Impact

- **Task directory structure is the only truth** — no database, no metadata store
- **Concurrent modification protection** — SHA-256 optimistic lock on every write
- **Adapter interface is Protocol-based** — CLI and Agent will depend on TaskServiceProtocol only
- **No global state** — TaskServiceImpl is instantiated with substrate_root, no singletons

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| Greenfield project — no existing patterns to follow | Research phase established best practices; design docs provide direction |
| Optimistic lock race condition (multi-process) | Phase 1 is single-process; multi-process race handling deferred |
| YAML parsing edge cases | Use safe_load, handle exceptions explicitly |
| Subtask parent resolution complexity | Simple path-based parent derivation (depth > 0 → parent is grandparent) |

## Documentation / Operational Notes

- **Dependencies** (pyproject.toml): pydantic>=2.10, pyyaml>=6.0, pytest>=8.0, ruff>=0.8
- **CLI not implemented yet** — test via direct TaskServiceImpl instantiation
- **No GitOps in Phase 1** — file system is sole storage; git versioning deferred

## Sources & References

- **Origin document:** [docs/brainstorms/005-phase1-requirements.md](../brainstorms/005-phase1-requirements.md)
- **Design reference:** [docs/design/phase1.md](../design/phase1.md)
- **Spec reference:** [docs/spec.md](../spec.md)
- **Architecture:** [docs/design/design.md](../design/design.md)