# Brainstorming Framework: Applying mem0ress Specs

## 背景

mem0ress 的四个核心概念——**记忆**、**任务**、**PRC**、**冲突**——原本是为 AI Agent 的认知对齐设计的。本文档探索将这些概念反过来应用于人类 brainstorming 的可行性与设计方向。

**目标：** 设计一个结构化的 brainstorming 框架，让想法的生成、筛选、沉淀和决策都遵循可验证的认知逻辑。

**适用范围：** 早期研究规划、开放性探索、多假设推演

**不适范围：** 已有明确结论的验证任务、已确定的执行计划

---

## 核心映射

mem0ress 的每个概念都可以对应到 brainstorming 过程的一个维度：

### 记忆 (Memory) → 上下文锚定

mem0ress 的"记忆"是以**目标为锚**的主动提取，而非被动检索。

对应到 brainstorming：
- 每次 brainstorming 开始前，明确当前正在解决的**核心问题**是什么
- 所有新想法必须与这个锚点建立明确关系
- 偏离锚点的想法不是"错误"，而是"需要新的锚点"

**设计问题：** 如何在 brainstorming 过程中实时检测想法是否偏离锚点？

### 任务 (Task) → 结构化产出

mem0ress 的任务是将模糊意图转化为**可判断状态**的认知单元。

对应到 brainstorming：
- brainstorming 之后不应该只有聊天记录，应该有**可验证的任务节点**
- 每个任务节点必须有明确的 **Picture / Requirements / Constraints**
- 任务之间通过依赖关系形成树结构

**设计问题：** brainstorming 过程中的"子想法"是否都应建模为任务节点？

### PRC (Picture/Requirements/Constraints) → 质量过滤

PRC 构成判断**未来动作是否偏离**的绝对标准。

对应到 brainstorming：
- **Picture**：这个想法指向的最终成功状态是什么？
- **Requirements**：如何验证这个想法的可行性？需要什么数据/实验？
- **Constraints**：这个想法绝对不能违反的底线是什么？

**设计问题：** 是不是每个"新想法"都必须经过 PRC 过滤才能进入下一轮发散？

### 冲突 (Conflict) → 动力机制

mem0ress 中的冲突检测用于发现 Requirements 与 Constraints 之间的矛盾。

对应到 brainstorming：
- 冲突不是"争吵"，而是**假设之间的张力**
- 识别"A 和 B 不能同时为真"是 brainstorming 的核心产出
- 冲突的存在本身就是一个有价值的研究发现

**设计问题：** brainstorming 框架是否应该主动诱发冲突（而非回避冲突）？

---

## Proposed Workflow

### Phase 0: 锚定 (Anchor)

在发散之前，明确：

```
Picture: [当前正在解决的模糊问题]
Requirements: [这个问题被解决后应该有什么可观测的变化]
Constraints: [ brainstorming 过程中绝对不能做的事]
```

这一步的目的是确保后续所有想法都有明确的上下文，而不是漫无目的的联想。

### Phase 1: 发散 (Divergent)

自由生成想法，不做判断。

每个想法记录为：
```
想法 ID: [自动编号]
内容: [描述]
与 Picture 的关系: [直接关联 / 间接关联 / 偏离锚点]
冲突标记: [是否有已知的冲突]
```

**规则：** 数量优先于质量；任何想法都可以提出，包括"明显荒谬的"。

### Phase 2: PRC 过滤 (Filter)

对 Phase 1 的每个想法应用 PRC 检查：

```
Picture Check: 这个想法是否指向某个可感知的目标？
Requirements Check: 这个想法是否可以被验证/推翻？验证手段是什么？
Constraints Check: 这个想法是否违反了任何底线约束？
```

通过检查的进入 Phase 3；未通过的标记为"待定"或"已放弃"。

### Phase 3: 冲突识别 (Conflict Detection)

在通过 PRC 过滤的想法之间识别冲突：

```
冲突类型 A: [两个想法互相排斥，不能同时为真]
冲突类型 B: [想法 A 蕴含想法 B，但 B 未被显式接受]
冲突类型 C: [想法 A 和 B 都指向同一个 Picture，但路径互斥]
```

冲突本身是重要产出——它们揭示了问题的深层结构。

### Phase 4: 收敛与任务化 (Converge & Taskify)

将最终的想法转化为**任务节点**：

```
Task Picture: [这个任务完成后的成功状态]
Task Requirements: [可验证的完成标准]
Task Constraints: [执行边界]
依赖关系: [父任务 / 子任务]
```

每个任务都是可独立推进的最小单元。

---

### Tier 验证结构（四层关卡）

```
Tier 0 ──→ Tier 1 ──→ Tier 2 ──→ Tier 3
  │          │          │          │
  ↓          ↓          ↓          ↓
检查      检查 Todo   检查      检查
Constraints  是否完成   Requirements  Picture
是否满足                是否满足   是否对齐
```

**Tier 0：约束检查（可能有数据变更）**
- 检查当前 Task 的所有 Constraints 是否满足
- 若有违反，尝试自动修复
  - 修复成功 → 重跑 Tier 0 确认 → Tier 1
  - 修复失败 → Agent 按权限决定：
    - L1/L2：立即让度给人（TODO 标记"待人确认"，spawn 协作任务）
    - L3/L4：再尝试一次，失败则让度给人

**Tier 1/2/3：纯检验，不做数据变更**

|| 层级 | 检查内容 | 通过标准 | 是否有数据变更 |
||------|---------|---------|--------------|
| **Tier 0** | Constraints 是否满足 | 全部 Constraint 无违反 | 可能修复（自动或手动） |
| **Tier 1** | Todo 完成 + 直接子任务完成 | (1) 所有 Todo 步标记完成；(2) 所有直接子任务状态为 COMPLETED | 无 |
| **Tier 2** | Requirements 是否满足 | 可自动化脚本/测试验证每个 Requirement | 无 |
| **Tier 3** | Picture 是否对齐 | Judge Agent 语义判断（主观感知类 Picture 专用） | 无 |

**通过关系：** Tier 1 失败不阻断 Tier 2（Todo 完成与 Requirements 满足可能不同步）；Tier 2 失败阻断 Tier 3。Tier 1 + Tier 2 全部通过才进入 Tier 3。

**Tier 2 验证模式：** Tier 2 根据 Tier 1 的状态决定验证范围：若 Tier 1 未完成，则只检查所有未通过的 Requirements（效率优先）；若 Tier 1 完成，则重新全部检查所有 Requirements（最终确认）。Tier 1 与 Tier 2 之间不存在 Todo 与 Requirements 的映射关系。

---

## Open Questions

 1. **谁来定义锚点？** 人类主导还是 AI 辅助？如果是 AI 辅助，AI 如何理解模糊的研究意图？

 2. **Phase 2 (PRC 过滤) 的严格程度？** 过于严格会扼杀创新；过于宽松则失去过滤价值。是否存在"最小过滤"标准？

 3. **冲突应该被解决还是被保留？** mem0ress 中冲突是待解决的问题。但 brainstorming 中，某些冲突可能本身就是核心发现——"A 和 B 互相排斥，但两者都有证据支持"是一个有价值的结论。

 4. **记忆的粒度？** brainstorming 过程中的"记忆"应该记录哪些内容？每个想法的上下文？还是只记录最终决策？

 5. **如何与现有工具集成？** 这个框架是否需要独立的工具链，还是可以叠加在现有工具（笔记软件、飞书文档）之上？

 6. **Constraints 的检查位置？** → ✅ **已解决：作为 Tier 0，在 Tier 1 之前检查**
   - Tier 0 = 约束检查，可能有数据变更
   - Tier 1/2/3 = 纯检验，不做数据变更
   - 无法修复时按权限让度给人（L1/L2 立即让度，L3/L4 失败后让度）

---

## 关联文档

- [spec.md](./spec.md) — mem0ress 完整规范
- [SPEC.md (MetaDev)](https://github.com/NousResearch/mem0ress/blob/semantic-refactor/SPEC.md) — 理论层（洞察一~四）

---

## Status

**状态：** 概念设计阶段

尚未进行实际用例验证。下一步需要选择一个具体场景（如"如何让 AI Agent 的上下文管理更可靠"），完整走一遍上述流程，验证每个 phase 的可操作性。

**待办：**
- [ ] 确定第一个试点场景
- [ ] 设计 Phase 0~4 的具体执行步骤
- [ ] 设计 Phase 2 PRC 过滤的最小标准
- [ ] 实现或采购对应的工具支持
