# mem0ress 教程

mem0ress 是面向 AI Agent 的认知对齐平面（Cognitive Alignment Plane）协议实现。它通过文件系统协议和 Judge 验证机制，帮助 Agent 在长程任务中保持认知稳定、 Survive 上下文压缩和中断恢复。

---

## §1 快速开始

### 1.1 初始化

```bash
mem0 init
```

这会在当前目录创建 `.cap/` 目录（CAP 的认知基座）。

### 1.2 创建任务

```bash
mem0 create my-task --picture "完成一份白皮书"
```

这会创建 `.cap/tasks/my-task/`，包含：

- `task.md` — 任务定义（picture、requirements、constraints）
- `session.md` — 认知增量流（append-only）
- `gotchas.md` — 关键发现（模糊点、风险、假设）
- `judge.md` — Judge 验证记录

### 1.3 工作循环

```
/cog.recover        → 恢复任务认知
write/edit          → 执行工作
/cog.snapshot       → 追加认知增量
/cog.gotcha         → 记录关键发现
/cog.verify         → 请求 Judge 验证
/cog.decide         → 根据 Judge 判决决定下一步
```

### 1.4 完成任务

```bash
mem0 done my-task
```

要求 Judge 通过（Tier 0 约束无违规 + Tier 1 Todo 完成 + Tier 2 可选自动验证）。

---

## §2 文件协议

### 2.1 目录结构

```
.cap/
├── tasks/
│   └── <task_id>/
│       ├── task.md       # 任务定义（语义权威）
│       ├── session.md    # 认知增量（append-only）
│       ├── gotchas.md    # 关键发现
│       ├── judge.md      # Judge 验证记录
│       └── data/         # 执行产物（可选）
│           ├── outputs/
│           ├── evidence/
│           └── artifacts/
```

### 2.2 task.md — 任务定义

```markdown
---
id: my-task
picture: "完成一份白皮书"
status: in-progress
todos:
  - [ ] 完成第一章
  - [ ] 完成第二章
constraints:
  - 不超过 10 页
  - 必须有数据支撑
---
```

**picture**：语义成功状态——"任务完成时，世界是什么样的"

**requirements**：可验证条件清单

**constraints**：不可逾越的红线

### 2.3 session.md — 认知增量

append-only 的增量流。只记录有意义的认知变化：

```
## 2026-06-08 14:00
- 第一章结构确定：背景 → 问题 → 方案
- 数据来源：参考 A 报告的 2024 年数据

## 2026-06-08 15:30
- 发现：第二章核心论点与第一章有冲突 → 需要重构
```

**禁止写入**：原始日志、chain-of-thought、verbose 过程记录。

### 2.4 gotchas.md — 关键发现

记录影响任务方向的关键发现：

```
## 语义模糊
- "用户价值"的定义在第一节和第三节不一致

## 风险假设
- 假设市场数据可以从公开渠道获取（尚未验证）

## 进展阻滞
- 需要与业务方确认目标受众定位
```

### 2.5 judge.md — Judge 验证记录

Judge Agent 的验证结果：

```markdown
## Tier 0 — 约束验证
PASS | 无约束违规

## Tier 1 — Todo 验证
PASS | 7/10 items completed

## Tier 2 — 自动验证
PASS | 数据来源标注完整

## 判决
VERIFIED | 语义对齐，可以继续
```

---

## §3 CLI 命令

mem0 是确定性能力层。语义推理在 Agent 层，持久化在 CLI 层。

### 3.1 初始化

```bash
mem0 init [--root .cap]
```

初始化认知基座。默认创建 `.cap/` 目录。

### 3.2 创建任务

```bash
mem0 create <task_id> --picture "<语义目标>"
```

创建任务目录和 `task.md`。picture 是必需的语义描述。

### 3.3 状态展示

```bash
mem0 status [--root .cap]
```

展示当前状态平面：所有任务、进度、阻塞点。

### 3.4 更新 Todo

```bash
mem0 update <task_id> --todo "完成第一章" --done
mem0 update <task_id> --todo "完成第一章"
```

标记 Todo 完成或添加新项。

### 3.5 完成任务

```bash
mem0 done <task_id>
```

触发完整 Judge 验证。必须通过才能完成。

### 3.6 废弃任务

```bash
mem0 abandon <task_id>
```

标记任务为废弃状态，并记录废弃原因。

### 3.7 查看 Judge 报告

```bash
mem0 report <task_id>
```

显示最近一次 Judge 验证的完整报告。

---

## §4 Skill 命令

`/cog *` 是语义交互入口。每个命令对应一个认知操作，不是命令绑定。

### 4.1 /cog.recover

恢复任务认知。加载 `task.md`、`session.md`、最近增量、gotchas、Judge 状态。

**返回**：
- 当前 picture
- 活跃的 requirements 和 todos
- 未解决的 gotchas
- 最近有意义的工作增量
- 最新 Judge 判决

**使用场景**：上下文压缩后、中断后回到任务、切换任务前。

### 4.2 /cog.status

渲染当前状态平面。包含认知表面和数据平面。

- **认知表面**：picture、todos、活跃 requirements、gotchas、最新 Judge 判决
- **数据平面**：outputs、evidence、artifacts

**使用场景**：快速了解任务全貌、给用户展示进度。

### 4.3 /cog.snapshot

追加认知增量到 `session.md`。

**规则**：
- 必须有语义意义（不是流水账）
- 必须可恢复（压缩但不丢失关键信息）
- 禁止写入：原始日志、chain-of-thought、verbose 过程

**使用场景**：完成一个工作单元后、有意义的认知变化发生时。

### 4.4 /cog.gotcha

记录关键发现到 `gotchas.md`。

**发现类型**：
- **语义模糊**：概念定义不一致、存在歧义
- **风险假设**：未验证的假设、潜在问题
- **进展阻滞**：等待外部输入、方向不确定

**使用场景**：遇到模糊点、风险假设、阻塞时立即记录。

### 4.5 /cog.verify

请求 Judge Agent 验证。

**Judge 隔离原则**：Judge 只接收 `task_id + 文件系统协议`，不接收运行时内存或隐藏状态。

**验证层级**：

| Tier | 内容 | 说明 |
|------|------|------|
| Tier 0 | 约束验证 | 检查 constraints 是否被违反 |
| Tier 1 | Todo 验证 | 检查 requirements 完成度 |
| Tier 2 | 自动验证 | 结构化检查（可选） |

**使用场景**：完成一个阶段后、提交前、遇到方向问题时。

### 4.6 /cog.decide

读取 Judge 判决，决定下一步。

**决策权永远在 Agent**：Skill 只提供信息，不做决策。

**可能的判决结果**：
- `VERIFIED` — 通过，继续下一阶段
- `INCOMPLETE` — 未通过，继续当前工作
- `REVISION_REQUIRED` — 需要修订某个部分

**使用场景**：`/cog.verify` 之后、`/cog.recover` 之后、遇到重大决策时。

---

## §5 Judge 验证

### 5.1 Tier 0 — 约束验证（必须通过）

检查 constraints 是否被违反。任何违规都会导致验证失败。

**示例 constraints**：
- "不超过 10 页" → 检查实际页数
- "必须引用数据来源" → 检查是否有标注
- "不能使用未授权内容" → 检查版权状态

### 5.2 Tier 1 — Todo 验证

检查 requirements 完成度。每个 requirement 对应一个或多个 Todo。

**示例**：
```
requirements:
  - 包含市场分析（Todo: 完成市场分析章节）
  - 有竞品对比（Todo: 完成竞品对比）
  - 结论有数据支撑（Todo: 引用数据来源）
```

### 5.3 Tier 2 — 自动验证（可选）

结构化检查：文件格式、引用完整性、命名规范、逻辑一致性。

**不是语义验证**，是结构验证。

### 5.4 验证失败处理

验证失败时：

1. 查看 `judge.md` 中的失败原因
2. 使用 `/cog.gotcha` 记录发现的模糊点
3. 修复问题
4. 再次执行 `/cog.verify`

---

## §6 典型场景

### 场景 A：白皮书写作

```
1. mem0 create whitepaper --picture "完成一份 10 页白皮书"

2. /cog.recover
   → 加载任务定义

3. 开始写作，完成第一章
   /cog.snapshot
   → "完成第一章：背景与问题定义"

4. 发现数据来源不确定
   /cog.gotcha
   → "市场数据来源尚未验证"

5. 继续写作
   /cog.snapshot
   → "第二章核心论点：AI 提升效率 30%"

6. /cog.verify
   → Judge 检查 constraints（10 页限制、数据来源标注）

7. /cog.decide
   → 如果 PASS，继续；如果 FAIL，修复

8. mem0 done whitepaper
   → 完整 Judge 验证 + 持久化关闭
```

### 场景 B：软件功能开发

```
1. mem0 create feature-login --picture "实现基于 OAuth2 的第三方登录"

2. /cog.recover

3. 实现核心逻辑
   /cog.snapshot
   → "完成 OAuth2 授权码流程"

4. 写测试
   /cog.snapshot
   → "完成单元测试：覆盖率 85%"

5. /cog.verify
   → Judge 检查 constraints（无硬编码密钥、必须处理 refresh token 过期）

6. 发现边界条件未处理
   /cog.gotcha
   → "未处理用户撤回授权的情况"

7. 修复后再次验证

8. mem0 done feature-login
```

---

## §7 概念速查

| 概念 | 说明 |
|------|------|
| **picture** | 语义成功状态——"完成后世界是什么样的" |
| **requirements** | 可验证条件清单 |
| **constraints** | 不可逾越的红线 |
| **session.md** | append-only 认知增量流 |
| **gotchas.md** | 关键发现（模糊点、风险、阻塞） |
| **judge.md** | Judge 验证记录 |
| **Tier 0** | 约束验证（必须通过） |
| **Tier 1** | Todo 验证 |
| **Tier 2** | 自动验证（可选） |

---

## §8 常见问题

**Q：session.md 可以手动编辑吗？**
可以，但不建议。session.md 应该是 `/cog.snapshot` 自动追加的。手动编辑会破坏增量流的语义一致性。

**Q：验证失败后可以强行完成任务吗？**
不可以。`mem0 done` 要求 Judge 通过。强制完成会破坏协议完整性。

**Q：gotchas 会被自动处理吗？**
不会。gotchas 是给 Agent 和人类看的记录，不触发自动行为。Agent 应该在 `/cog.recover` 时看到活跃的 gotchas，并主动处理。

**Q：可以同时处理多个任务吗？**
可以。每个任务有独立目录。但上下文压缩会丢失任务切换的记忆，所以建议用 `/cog.recover` 恢复后再切换。

**Q：中断后如何恢复？**
使用 `/cog.recover` 恢复任务认知。mem0ress 通过文件系统协议保证了中断恢复的能力——即使完整上下文丢失，只要文件系统存在，就能恢复到一致状态。