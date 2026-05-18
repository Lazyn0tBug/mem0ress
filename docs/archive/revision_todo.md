# CAP Spec Rev A2 → spec.md Revision TODO

> 来源：session_0514_2.md (CAP Specification Revision A2) vs docs/spec.md

## 对照表

| session 要点 | spec.md 对应章节 | 核对结论 |
|---|---|---|
| §2 Picture/Requirement/Constraints 三原语定义 | §4.1 PRC模型 | ✅ 已有（Picture/Requirements/Constraints 三要素） |
| §2.2 "Requirements are not implementation details"（需求不是实现细节） | §4.1 | ⚠️ 隐含但未明确声明 |
| §3 Plane Semantics: data_plane = "what happened" | §4.3 数据平面 | ⚠️ spec 定义为 commit ID，CAP 定义更抽象（执行记录） |
| §3 Plane Semantics: status_plane = "interpreted alignment state" | §4.3 状态平面 | ⚠️ spec 定义为任务树+Todo，CAP 定义为语义对齐标记 |
| §3.1 data_plane "does not own alignment truth" | 无对应章节 | ❌ 缺失 |
| §4 Judge = "semantic alignment constructor"（主动构造） | §5.4 Judge Agent | ⚠️ spec 描述为检验执行器，CAP 强调"构造"角色 |
| §4.2 "Alignment is not binary" | 无明确对应 | ❌ 缺失（漂移是渐进的） |
| §5 Cognition Ownership: Agent = cognition production, CAP = alignment authority | §3.2 认知归属模型 | ⚠️ spec 有 runtime vs Agent 的职责划分，但未用 Cognition Ownership 框架 |
| §6 Alignment Continuity: "semantic direction remains reconstructable" | 分散在 §5.2 | ⚠️ 隐含，未独立章节 |
| §7 Alignment Drift: 列举5种漂移形式 | 无专门章节 | ❌ 缺失 |
| §8 Reconstruction Semantics: "semantic rather than historical" | 无专门章节 | ❌ 缺失（spec §5.2 隐含） |
| §9 Alignment Invariants: 5个 Visibility/Interpretability 不变式 | 无对应章节 | ❌ 缺失 |
| §10 Failure Conditions: 7种失败条件 | 无对应章节 | ❌ 缺失 |
| §11 Final Principle: "semantic alignment surface, NOT execution framework" | §1 系统定位 | ✅ 已有（"认知对齐平面不是存储系统"） |

---

## 待处理项

### [x] 1. 新增 Alignment Drift 专章 ✅
**来源**：CAP Spec §7

**内容**：
- 漂移定义：执行活动逐渐偏离对齐语义
- 5种漂移形式：
  1. work no longer serving Picture
  2. implicit Requirement violations
  3. hidden Constraint erosion
  4. unstable semantic reinterpretation
  5. local optimization replacing task intent
- 漂移检测是持续语义责任
- 漂移通常是渐进的，难以通过原始执行活动检测

**建议位置**：§7（结语之前），新增 §7 Alignment Drift

---

### [ ] 2. 明确 "Requirements are not implementation details"
**来源**：CAP Spec §2.2

**内容**：在 §4.1 PRC 模型中增加一段，明确 Requirements 是正确性定义，不是实现细节。多种实现可以满足同一 Requirements集合。

**建议位置**：§4.1 内补充

---

### [x] 3. 新增 Alignment Invariants 专章 ✅
**来源**：CAP Spec §9

**内容**：5个必须保持的不变式：
1. Picture Visibility — 当前语义方向必须保持可重建
2. Requirement Visibility — 需求满足状态必须保持可观测
3. Constraint Visibility — 活动约束必须保持可见和可解释
4. Drift Visibility — 潜在语义漂移必须保持可检测
5. Alignment Interpretability — 当前对齐状态必须保持可语义解释

**建议位置**：§7 或作为独立附录

---

### [x] 4. 新增 Failure Conditions 专章 ✅
**来源**：CAP Spec §10

**内容**：spec 被认为降级（degraded）的条件：

| Failure | Meaning |
|---------|---------|
| Picture becomes ambiguous | semantic direction collapse |
| Requirements become unverifiable | correctness collapse |
| Constraints become hidden | boundary collapse |
| drift becomes undetectable | alignment collapse |
| status_plane becomes raw execution state | semantic interpretation collapse |
| alignment requires transcript replay | continuity collapse |
| Agent implicitly owns alignment truth | cognition ownership collapse |

**建议位置**：作为附录或 §10

---

### [x] 5. Cognition Ownership 框架明确化 ✅
**来源**：CAP Spec §5

**内容**：
- Agent = cognition production（执行推理、生成输出、产生认知）
- CAP = alignment authority（对齐语义由 Picture/Requirements/Constraints/Judge 解释构建）
- 核心不变式：Agent 不拥有对齐真理，执行活动本身无法决定对齐是否保持

**建议位置**：§3.2 补充，或新增 §5.1 Cognition Ownership

---

### [x] 6. data_plane "does not own alignment truth" ✅
**来源**：CAP Spec §3.1

**内容**：data_plane 包含可观察的执行记录，但不拥有对齐真理。原始执行证据本身不足以判定对齐是否保持。

**建议位置**：§4.3 数据平面章节补充

---

### [ ] 7. Judge = semantic alignment constructor
**来源**：CAP Spec §4

**内容**：Judge 是语义对齐的主动构造者，不是被动验证器。Judge 通过解释关系构造对齐状态，评估对齐连续性，检测语义漂移。

**建议位置**：§5.4 Judge Agent 章节补充

---

### [ ] 8. Alignment is not binary
**来源**：CAP Spec §4.2

**内容**：对齐不是二元的。语义漂移可能通过局部优化、隐藏假设、语义捷径、隐式约束侵蚀、目标重新解释逐渐发生。Judge 执行连续解释而非简单 pass/fail 验证。

**建议位置**：§5.4 内补充

---

### [ ] 9. Alignment Continuity 独立章节
**来源**：CAP Spec §6

**内容**：
- 对齐连续性定义：当前语义方向可重建、正确性状态可解释、活动约束可见、未解决风险可观测、语义连贯性可恢复
- 不需要：完整转录重放、全面对话历史、持久隐藏运行时内存

**建议位置**：新增 §6 Alignment Continuity 或合并到 §5.2

---

### [ ] 10. Reconstruction Semantics 专章
**来源**：CAP Spec §8

**内容**：
- 重建是语义的而非历史的
- 重建需要：当前对齐原语、当前语义解释、当前证据关系、未解决语义风险
- 重建不需要：完整转录重放、详尽推理历史、完整执行年表

**建议位置**：新增 §8 Reconstruction Semantics 或合并到 §5.2

---

### [ ] 11. Final Principle 补充
**来源**：CAP Spec §11

**内容**：CAP 定义的是语义对齐表面，不是执行框架。

**建议位置**：§1 或 §11 已有，可检查完整性

---

## 已完成

### ✅ spec vs CAP 定义层次差异待决策
- CAP Spec 是抽象语义层，定义"做什么"
- spec.md 是实现规约层，定义"怎么做"
- 部分章节（如 data_plane）两者抽象程度不同

**决策**：保持 spec.md 的具体化定义，还是向 CAP 的抽象层对齐？
