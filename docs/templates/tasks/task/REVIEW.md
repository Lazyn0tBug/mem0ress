# Task 模板文档评审报告

**评审日期：** 2026-05-15
**评审框架：** scientific-critical-thinking（规范评审扩展）
**评审维度：** 内容、解构、逻辑、颗粒度、创新性、一致性

---

## 一、内容（Content）

### 优势

- task.md 的认知三要素结构（Picture/Requirements/Constraints）设计合理，语义清晰
- session.md 的版本快照模型（追加不覆盖）设计合理，符合认知记录的审计需求
- gotchas.md 的三段式结构（Context/Deviation/Resolution）对经验固化很有价值
- 整体使用 frontmatter + body 双格式，机器可解析性与人类可读性兼顾

### 缺口

1. **[P0] `data_plane` 在多个模板中被引用，但从未定义**
   - task.md 第19行 `data_plane:` 字段仅有注释占位，无实际内容
   - session.md 第18-22行依赖 `data_plane` 记录 commit ID 和 active references
   - 后果：模板间产生了隐性依赖，但定义缺失，Agent 无法判断具体操作什么

2. **[P1] `cognitive_triad` 字段在 task.md 模板中缺失**
   - task.md 第34行声明"frontmatter 中的 `cognitive_triad` 字段是机器可解析的标准格式"
   - 但实际的 frontmatter（第1-5行）中只有 `task_id`、`status`、`created_at`，没有 `cognitive_triad`
   - 后果：模板自述与实际不符，Agent 写入时缺少占位符指引

3. **[P1] Subtask 的定义和生命周期完全缺失**
   - task.md 第31-32行引用了 subtask，但：
     - subtask 目录结构是什么？
     - subtask 的状态如何与主任务同步？
     - subtask 被标记为 `ABANDONED` 时，主任务应如何响应？
   - 后果：subtask 机制不可用，多层任务分解无法落地

4. **[P1] Todo 格式在模板间不一致**
   - task.md 第27行使用 `- [ ] Todo 1:` 格式（无 id，无 done 字段）
   - session.md 第5行使用 `{text, done}` 结构（无 id，与 task.md 的 Todo 无法关联）
   - 后果：无法建立 Session todos 与 task.md Todos 的对应关系，追踪链路断裂

---

## 二、解构（Document Structure）

### 优势

- 四个模板各司其职，职责分离清晰（task/session/judge/gotchas）
- 文件之间有明确的引用关系（session 引用 task，judge 引用 task）

### 缺口

1. **[P1] 模板间引用关系不完整**
   - session.md 依赖 `data_plane`，但 `data_plane` 的定义在哪里？可能是 arch.md 或 design.md，但模板层面没有指向
   - judge.md 依赖"水化"操作，但"水化"的定义和工具链未在任何模板中说明

2. **[P2] judge.md 的 Tier 0/1/2/3 与 mem0ress 规范（harness 模块）的对应关系不明确**
   - judge.md 是独立模板还是 harness 模块的实例化？
   - Tier 验证失败后的状态转移路径未定义

---

## 三、逻辑（Logic）

### 优势

- task.md 的状态机定义（CREATED/IN_PROGRESS/VERIFYING/COMPLETED/ABANDONED）基本完整
- session.md 正确标注了 VERIFYING 为检验瞬态，不属于生命周期状态（与 spec 一致）

### 缺口

1. **[P1] task.md 的 `cognitive_triad` 自述与实际不符**
   - 第34行声称 frontmatter 中有 `cognitive_triad` 字段
   - 实际 frontmatter（第1-5行）只有 `task_id`、`status`、`created_at`
   - 这是一个自相矛盾：模板声称的格式与定义的格式不一致

2. **[P1] `ABANDONED` 状态的语义模糊**
   - 当 subtask 标记为 ABANDONED 时，主任务应该继续还是终止？
   - ABANDONED 与 COMPLETED 的本质区别是什么？subtask 可以 ABANDON，主任务可以吗？

3. **[P1] judge.md 的 Tier 3 触发条件和执行路径不明确**
   - "涉及用户登录无感知的体验评估时必须触发"——这个判断由谁来做？
   - LLM-as-a-Judge 的输出格式是什么？（PASS/FAIL + 偏差描述）
   - 判定结果如何影响 task status？

---

## 四、颗粒度（Granularity）

### 优势

- task.md 的 Constraints 有明确的"绝对不可逾越"的语义定义
- session.md 的字段说明表设计合理

### 缺口

1. **[P2] 过度描述的操作细节混入模板**
   - task.md 第34行关于"Agent 写入 body 后必须同步更新 frontmatter"的约定是实现层面的操作规程，更适合放在工具文档或 arch.md，而非模板说明

2. **[P1] 核心机制缺失占位符**
   - `data_plane`（P0 级依赖）无占位符
   - `cognitive_triad`（第34行声明）无实际占位符
   - subtask 目录结构（多层任务分解的核心）完全缺失

---

## 五、创新性（Innovation）

- 认知三要素（Picture/Requirements/Constraints）是对传统需求文档的有意义的改进
- 版本快照模型的追加设计合理
- 三层验证（机械检查/需求验收/语义对齐）的分层思路清晰

### 缺口

- judge.md 的 Tier 3 的 LLM-as-a-Judge 框架是合理的，但依赖"水化"操作（将代码切片转换为可读摘要），这个关键操作在任何模板中都没有定义

---

## 六、一致性（Consistency）

### 优势

- status 枚举值在各模板中保持一致
- Turn 编号格式在 session.md 和 gotchas.md 中保持一致（`{N,M}` 格式）

### 缺口

1. **[P0] `data_plane` 引用不一致**
   - 被 session.md、task.md 引用，但从未定义
   - 需要在 templates 目录新增 `data_plane.md` 或在 arch.md 中明确定义

2. **[P1] Todo 格式不一致**
   - task.md: `- [ ] Req 1:` / `- [ ] Todo 1:`（带复选框，无 id）
   - session.md: `{text, done}`（无复选框，无 id）
   - 两者无法建立关联

3. **[P1] `cognitive_triad` 字段声明与实际不符**
   - 第34行说 frontmatter 有 `cognitive_triad`
   - 实际 frontmatter 没有这个字段

---

## 七、补足优先级

### P0（规范不可运行的缺口）

| # | 问题 | 建议 |
|---|------|------|
| P0-1 | `data_plane` 被引用但从未定义 | 在 `docs/templates/` 目录下新增 `data_plane.md` 模板，定义其结构和用途 |

### P1（影响规范可信度的缺口）

| # | 问题 | 建议 |
|---|------|------|
| P1-1 | `cognitive_triad` 字段声明与实际 frontmatter 不符 | 在 task.md frontmatter 中添加 `cognitive_triad` 占位字段结构 |
| P1-2 | Subtask 的定义和生命周期完全缺失 | 新增 `docs/templates/tasks/task/subtask.md` 模板，或在 task.md 中补充 subtask 定义 |
| P1-3 | Todo 格式在 task.md 和 session.md 中不一致，无法关联 | 统一 Todo 格式，建议都带 `{id, text, done}` 结构 |
| P1-4 | Tier 3 的"水化"操作未定义 | 在 judge.md 或新增的 `docs/templates/tasks/task/hydration.md` 中定义水化操作 |

### P2（降低规范可用性的缺口）

| # | 问题 | 建议 |
|---|------|------|
| P2-1 | task.md 第34行操作约定混入模板说明 | 移除该行或将其移至模板的使用说明文档 |
| P2-2 | `ABANDONED` 状态的语义模糊 | 在 task.md 中为 `ABANDONED` 添加语义说明（与 COMPLETED 的区别） |
| P2-3 | judge.md 与 mem0ress harness Tier 0/1/2/3 的对应关系不明确 | 在 judge.md 开头添加说明：judge.md 是 mem0ress Tier 验证的实例化模板 |

---

## 八、评审者问题记录

| # | 问题 | 答案 | 来源 |
|---|------|------|------|
| Q1 | `data_plane` 的正确定义在哪里？是在 arch.md 还是需要新增模板？ | 待确认 | — |
| Q2 | `cognitive_triad` 字段是否应该添加到 task.md frontmatter？ | 待确认 | — |
| Q3 | Subtask 的生命周期由哪个模块管理？主任务如何感知 subtask 的 ABANDONED？ | 待确认 | — |
| Q4 | "水化"操作的工具链是什么？ | 待确认 | — |

---

## 总结评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 内容 | 6/10 | 核心框架清晰，但 `data_plane` 缺失是 P0 级缺口 |
| 解构 | 7/10 | 模板间引用关系基本合理，但引用目标未定义 |
| 逻辑 | 5/10 | `cognitive_triad` 自述矛盾，P0/P1 问题较多 |
| 颗粒度 | 6/10 | 核心机制占位符缺失，实现层细节混入模板 |
| 创新性 | 8/10 | 认知三要素和分层验证设计有价值 |
| 一致性 | 5/10 | `data_plane` 和 `cognitive_triad` 存在严重不一致 |

**核心结论：** 四个模板的设计思路（认知三要素、版本快照、分层验证）总体合理，但存在一个 P0 级缺口（`data_plane` 未定义）和多个 P1 级缺口（`cognitive_triad` 矛盾、subtask 缺失、Todo 格式不统一）。建议优先补足 P0 和 P1 缺口后再进行实现。

---

*评审框架：scientific-critical-thinking（规范评审扩展），2026-05-15*
