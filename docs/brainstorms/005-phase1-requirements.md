---
date: 2026-05-05
topic: phase1-implementation
---

# Phase 1: 系统骨架与核心数据契约实现

## Problem Frame

Phase 1 是 mem0ress 的架构基础层——定义数据模型、核心服务接口、存储层和目录结构。所有后续阶段（Phase 2-6）都依赖于此。

核心问题：**如何在文件系统上用纯文本准确表达认知状态，并以可测试的方式解耦 Adapter？**

## Architecture Overview

```
Adapter Layer (Phase 6+)     Protocol 解耦
────────────────────────     ────────────
CLI Slash Commands    →       TaskServiceProtocol
Agent Skills         →       (Interface only)

───────────────────────────────────────────
Core Layer (Phase 1)
─────────────────────────
├── core/             数据模型（schema.py）
├── service/         核心业务逻辑
│   ├── protocol.py  TaskServiceProtocol（接口定义）
│   └── impl/        TaskServiceImpl（实现）
├── storage/         存储中间层
│   ├── parser.py    解析/序列化
│   └── fs.py        乐观锁写入、冲突检测
└── plane.py         状态平面组装
```

## Requirements

### 目录结构与关联原则

- R1. `.mem0ress/` 是认知基座根目录（Substrate Root）
- R2. `tasks/` 下每个子目录是一个 Task，目录名即 Task ID
- R3. 每个 Task 目录下有且只有一个 `index.md` 作为 Manifest 锚点
- R4. 每个 Task 目录下有且只有一个 `references/` 目录，存放单文件单用途的引用文件
- R5. `references/` 下每个文件有且只有一个，明确目的（如 `gotcha.md`、`tag.md`）
- R6. 子目录即是 Subtask，无需额外声明——目录结构即关联关系
- R7. 目录路径即关联关系，不需要额外的 `related_task` 等冗余字段（保留字段声明不用）

### Core Models (schema.py)

- R8. `TaskStatus` 枚举：`created`, `in-progress`, `completed`, `abandoned`
- R9. `TaskManifest` Pydantic 模型包含：`id`, `type`, `status`, `cognitive_triad`, `gotcha_refs`, `todos`
- R10. `TaskManifest.id` 为冗余字段，读取时与目录名校验，不一致以目录名为准；写入时始终设为目录名（文件系统是 source of truth）
- R11. `CognitiveTriad` 包含 `picture`, `requirements`, `constraints`
- R12. `TodoItem` 包含 `text`, `done`
- R13. `Gotcha` Pydantic 模型包含：`id`, `type`, `task_id`, `timestamp`, `content` — 文件路径即关联，`id` 和 `task_id` 均为冗余但方便字段（与 TaskManifest.id 一致），`related_task` 保留声明不用

### Storage Layer

- R14. `SubstrateParser.parse_manifest(file_path: Path) -> TaskManifest` 读取 YAML frontmatter 和 markdown body 中的 todo list。`id` 字段始终以目录名为准（文件系统是 source of truth），无需校验或警告
- R15. `SubstrateParser.serialize_manifest(manifest: TaskManifest) -> str` 将内存模型序列化回标准 markdown 格式，`id` 始终设为目录名
- R16. 支持 `- [x]` 和 `- [ ]` 两种 todo 格式，大小写不敏感
- R17. `fs.py` 实现带乐观锁的 `safe_write(index_path: Path, content: str, expected_hash: str)`：写入前校验 hash，不一致则抛出 `ConflictError`。使用 SHA-256 算法计算文件内容 hash
- R18. `fs.py` 实现 `get_file_hash(file_path: Path) -> str`，用于乐观锁校验

### TaskService (核心业务逻辑)

- R19. `TaskServiceProtocol` Protocol 接口定义，方法包括：
  - `create_task(task_id: str, picture: str) -> TaskManifest`
  - `get_task(task_id: str) -> TaskManifest`
  - `update_todo(task_id: str, index: int, done: bool) -> TaskManifest` — 若 index 越界则抛出 IndexError
  - `update_cognitive_triad(task_id: str, picture: str, requirements: list[str], constraints: list[str]) -> TaskManifest`
  - `get_all_tasks() -> list[TaskManifest]`
  - `delete_task(task_id: str) -> None` — 若 task_id 不存在则抛出 FileNotFoundError
  - `add_todo(task_id: str, text: str) -> TaskManifest`
  - `remove_todo(task_id: str, index: int) -> TaskManifest`
- R20. `TaskServiceImpl` 实现 `TaskServiceProtocol`，通过 `storage/fs.py` 进行文件读写
- R21. `create_task` 自动创建 `.mem0ress/tasks/<task_id>/index.md`，并创建 `references/` 目录。若 task_id 已存在则抛出 `TaskExistsError`
- R22. `update_todo` 和 `update_cognitive_triad` 调用 `fs.py` 的乐观锁写入，冲突时抛出 `ConflictError`

### Plane Assembler

- R23. `PlaneAssembler.compile_status_plane() -> str` 扫描 `tasks/` 目录树，生成带缩进和依赖关系的状态平面文本
- R24. 状态平面中 `picture` 字段若以 `ref:` 开头，标记为脱水指针而非直接展开
- R25. 系统法则固定追加到状态平面末尾。内容为：
  1. 你不可撤销状态，只能覆写向前。
  2. 任何父级 Task 的完成，必须以其所有子层级 Task 完成为绝对前提。

## Success Criteria

- 目录结构完整，物理符合 R1-R7
- 所有 Model 可通过 pydantic 校验
- `parse_manifest` 和 `serialize_manifest` 互为逆操作
- `compile_status_plane()` 输出格式示例：

```markdown
# Status Plane (当前态势感知)

■ Task ID: auth_module [IN-PROGRESS]
   目标图景: 实现完整的用户登录模块
   进度: 1/2 Todos 完成

  └─ Task ID: auth_middleware [CREATED]
     目标图景: 实现跨域与 Token 验签拦截器
     进度: 0/3 Todos 完成
     [约束]: 这是 auth_module 的子任务，必须优先完成。

---
系统法则：
1. 你不可撤销状态，只能覆写向前。
2. 任何父级 Task 的完成，必须以其所有子层级 Task 完成为绝对前提。
```
- `TaskServiceImpl` 实现可通过 `TaskServiceProtocol` 类型校验
- 乐观锁冲突时 `ConflictError` 可被正确抛出

## Scope Boundaries

- 不实现 CLI 入口（Slash Commands）— 延至 Phase 6+
- 不实现 Agent Skill 适配器 — 延至 Phase 6+
- 不实现 LLM 接入 — 延至 Phase 4
- 不实现 Harness 验证 — 延至 Phase 5
- 不实现 GotchaService — 附加服务，延至后续阶段

## Key Decisions

- **文件即身份**：Gotcha 文件路径即身份，不需要额外 UUID 生成
- **单文件单用途**：`references/` 下每个文件职责单一
- **目录即关联**：Subtask 无需在 index.md 中声明，目录结构天然表达父子关系
- **轻量 Protocol**：Adapter 只依赖 Protocol 类型提示，实现与接口分离
- **乐观锁**：使用文件内容 Hash 校验，写入前比对 expected_hash

## Dependencies / Assumptions

- Python 3.12+，uv 作为包管理工具
- `pyyaml` 用于 frontmatter 解析
- `pydantic >= 2.7` 用于 schema 校验
- 无额外依赖注入框架，使用 Python 原生 Protocol

## Outstanding Questions

### Deferred to Planning
- [Phase 2?] `ref:` 指针的水化机制（`resolve_reference` 工具）是 Phase 2 还是 Phase 3 的范围？
- [Phase 1?] 系统法则的具体措辞是否可以在 Phase 1 固化，还是留给后续阶段？

## Next Steps

-> /ce:plan for structured implementation planning