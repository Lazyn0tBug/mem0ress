# mem0ress Protocol Schema

> 本文件是协议所有字段的权威定义。
> 当模板文件与本文件冲突时，以本文件为准。

---

## 1. 通用规范

### 1.1 时间戳

所有时间戳字段均采用 **ISO 8601 UTC** 格式：

```
YYYY-MM-DDTHH:mm:ssZ
示例：2025-01-15T09:23:41Z
```

不允许使用本地时间或省略时区。

### 1.2 task_id

```
格式：[a-z0-9_]{1,64}
示例：oauth_login、data_pipeline_v2、fix_auth_timeout
```

规则：
- 小写字母、数字、下划线
- 最长 64 字符
- 在同一 workspace 内全局唯一
- 创建后不可修改

### 1.3 Turn 编号

```
格式：{N}.{M}
N：主轮次，正整数，从 1 开始
M：子轮次，正整数，从 1 开始
示例：1.1、1.2、2.1、3.4
```

规则：
- N 在主 Agent 开始一个新的独立执行阶段时递增
- M 在同一阶段内的迭代中递增（重试、局部修正）
- Turn 编号与 Todo 序号解耦：一个 Turn 可以推进多个 Todo，多个 Turn 可以推进同一个 Todo
- 同一 task 内 Turn 编号单调递增，不允许回退

### 1.4 编号 ID 体系

所有编号 ID 在**任务内唯一**，不要求全局唯一。

| ID 前缀 | 含义 | 示例 |
|--------|------|------|
| `T-N` | Todo | T-1, T-2 |
| `R-N` | Requirement | R-1, R-2 |
| `C-N` | Constraint | C-1, C-2 |
| `G-N` | Gotcha | G-1, G-2 |

N 从 1 开始，在对应文件内单调递增，不允许复用。

---

## 2. task.md 字段

### Frontmatter

|| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
|| `status` | enum | ✅ | 见 §2.1 |
|| `created_at` | timestamp | ✅ | 见 §1.1 |

**task_id 由目录拓扑表达，不由 frontmatter 字段定义。**

### 2.1 status 枚举

| 值 | 含义 | 可转入的下一状态 |
|----|------|----------------|
| `CREATED` | 已创建，所有 Todo 未开始 | IN_PROGRESS, ABANDONED |
| `IN_PROGRESS` | 执行中，至少一个 Todo 已完成 | COMPLETED, ABANDONED |
| `VERIFYING` | 检验瞬态，Judge Agent 正在执行 | IN_PROGRESS, ABANDONED |
| `COMPLETED` | 终态：目标达成 | — |
| `ABANDONED` | 终态：目标放弃 | — |

**VERIFYING 的约束：**
- VERIFYING 是瞬态，不允许持久停留
- Judge Agent 调用结束后必须立即退出 VERIFYING
- VERIFYING **不记录**在 session.md 的 status 字段中（session 只记录生命周期状态）
- 宿主框架负责 VERIFYING 的超时保护（见 PROTOCOL.md §3.3）

### 2.2 Picture

- 类型：自由文本，无长度限制
- 写给人看，不要求可验证，要求真实反映利益相关者预期
- 不允许为空

### 2.3 Requirements

- 格式：`- [ ] R-N: {描述}`
- 每条 Requirement 必须可独立验证（存在对应的自动化命令或明确指标）
- "界面美观"、"用户体验好"等无验收标准的描述不是合法 Requirement
- 不允许为空列表

### 2.4 Constraints

- 格式：`- ⛔ C-N: {描述}`
- 描述约束的**违反条件**，而非期望行为。写"不允许 X"，不写"应当 Y"
- 允许为空列表（无约束任务）

### 2.5 Todos

- 格式：`- [ ] T-N: {描述}` / `- [x] T-N: {描述}`
- 描述具体可执行动作，不允许写抽象目标
- 不允许为空列表

---

## 3. session.md 字段

### Frontmatter

|| 字段 | 类型 | 必填 |
|-----|------|------|
|| `task_id` | string | ✅ |
|| `type` | `"session"` | ✅ |

### Turn 块字段

|| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
|| `Turn {N.M}` | string | ✅ | 见 §1.3 |
|| `Timestamp` | timestamp | ✅ | 见 §1.1 |
|| `Status` | enum | ✅ | CREATED / IN_PROGRESS / COMPLETED / ABANDONED，不含 VERIFYING |
|| `Action Summary` | string | ✅ | 本轮主要动作，一两句话 |
|| `Todos` | list | ✅ | 全量 Todo 列表当前状态，不只记录本轮变化 |
|| `Outcome` | object | ✅ | 执行结果：status（success/partial/failed）+ note |
|| `Evidence` | list[object] | ✅ | 结构化证据：type/ref/purpose，purpose 绑定 Picture Claim |
|| `Workspace Snapshot` | object | ✅ | 工作区快照：commit_id + note |

**Evidence 的 purpose 字段意义：** purpose 描述"该证据证明了什么"，与 Picture 维度对应，供 Judge 建立 Picture Claim → Evidence 映射。

**Todos 写法约定：**
session.md 的 Todos 字段记录**全量状态**（所有 Todo 的当前完成情况），不只记录本轮新完成的项。这样每个 Turn 块是独立可读的，不需要回溯历史才能知道当前进度。

---

## 4. judge.md 字段

### Frontmatter

|| 字段 | 类型 | 必填 |
|-----|------|------|
|| `task_id` | string | ✅ |
|| `type` | `"judge"` | ✅ |

### Turn 块字段

|| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
|| `Turn {N.M}` | string | ✅ | 与触发时的 session Turn 一致 |
|| `Timestamp` | timestamp | ✅ | Judge Agent 开始检验的时间 |
|| `Verdict` | enum | ✅ | PASSED / FAILED |
|| `Tier 0` | table | ✅ | 每条 Constraint 一行 |
|| `Tier 1` | checklist | ✅ | Todo + 子任务检查 |
|| `Tier 2` | table | ✅ | 每条 Requirement 一行 |
|| `Tier 3` | block | 条件 | 见 §4.1 |
|| `Overall Verdict` | enum | ✅ | PASSED / FAILED |
|| `Summary` | string | ✅ | FAILED 时必须说明是哪个 Tier 失败 |

### 4.1 Tier 3 触发条件

Tier 3 仅在以下条件之一成立时执行，其余情况标记为 SKIPPED：

1. Picture 包含主观判断词汇（"无感知"、"流畅"、"友好"等）
2. Constraints 与 Picture 之间存在语义歧义，需要语义裁定
3. 主 Agent 或利益相关者在触发检验时显式设置 `tier3_requested: true`

Tier 0/1/2 任一 FAIL 时，Tier 3 强制 SKIPPED。

---

## 5. gotchas.md 字段

### Frontmatter

|| 字段 | 类型 | 必填 |
|-----|------|------|
|| `task_id` | string | ✅ |
|| `type` | `"gotchas"` | ✅ |

### Gotcha 块字段

|| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
|| `Gotcha {G-N}` | string | ✅ | 见 §1.4 |
|| `Timestamp` | timestamp | ✅ | 见 §1.1 |
|| `Turn` | string | ✅ | 关联的 session Turn |
|| `触发背景` | string | ✅ | 在执行哪个 Todo 时发生 |
|| `实际发生了什么` | string | ✅ | 不允许写"发现了问题"，必须写具体事实 |
|| `如何处理` | string | ✅ | 结论，不写过程 |

---

## 6. 文件系统布局

```
{workspace}/
└── tasks/
    └── {task_id}/
        ├── task.md        # 读写方：主 Agent（创建）/ 主 Agent（更新 Todo）
        ├── session.md     # 读写方：主 Agent（追加）/ Judge Agent（只读）
        ├── gotchas.md     # 读写方：主 Agent（追加）/ Judge Agent（只读）
        ├── judge.md       # 读写方：Judge Agent（追加）/ 主 Agent（只读）
        └── {subtask_id}/ # 子任务目录，结构同上
```

父子关系由目录树表达，task.md 内不重复列子任务。