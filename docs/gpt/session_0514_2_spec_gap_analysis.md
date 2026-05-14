# session_0514_2.md → spec.md 差异分析（rev-0.4）

**分析日期**：2026-05-14（更新）  
**源文件**：docs/gpt/session_0514_2.md（rev-0.4）  
**目标文件**：docs/spec.md  

---

## 一、session rev-0.4 vs rev-0.3 变化摘要

| 变化类型 | 内容 |
|---------|------|
| **移除** | §10 MVP Command Surface（/cog 命令列表） |
| **移除** | §21 Technology Constraints |
| **新增章节** | §9 Slash Command Model |
| **新增章节** | §12 Snapshot Semantics（4 个子节） |
| **章节重组** | Failure Conditions 从 §23 调整为 §20 |
| **合并** | 原 §8 Skill Model 拆分为 8.1 + 8.2 |

---

## 二、缺失内容（session 有，spec 无）

### 1. Snapshot Semantics（§12）
| 项目 | 内容 |
|------|------|
| session 位置 | §12（含 12.1 Snapshot Definition、12.2 MUST Preserve、12.3 MUST Discard、12.4 Snapshot Success Condition） |
| 核心断言 | 快照 = recoverable cognition delta，NOT historical replay |
| 成功恢复条件 | 仅使用 task.md + recent snapshots + gotchas.md + latest judge verdict，无需 transcript replay |
| spec 现状 | §5.2 认知构建有 session.md 描述，但无专门的 Snapshot Semantics 章节；无明确的"成功恢复条件"断言 |

**归类**：新增章节（快照语义是协议核心，需独立章节）

---

### 2. Slash Command Model（§9）
| 项目 | 内容 |
|------|------|
| session 位置 | §9 |
| 核心定义 | Slash commands = protocol lifecycle operators（不是 autonomous tools / subsystems / planners / workflow abstractions） |
| 约束 | Each command maps directly to a protocol phase |
| 理由 | Command inflation often leads to orchestration logic |
| spec 现状 | 无专门章节；§5 执行循环描述了轮次，但未定义命令级约束 |

**归类**：新增小节（在 §5 执行循环或 §3 设计原则中补充）

---

### 3. Failure Conditions（§20）
| 项目 | 内容 |
|------|------|
| session 位置 | §20 |
| 6 种降级条件 | session.md becomes transcript（compression failure）、recovery requires replay（cognition failure）、runtime absorbs reasoning（architecture failure）、Judge receives hidden state（isolation failure）、slash commands become workflows（protocol failure）、skill becomes toolbox（cognition surface failure） |
| spec 现状 | 无专门章节，仅在 FAQ 零散提及 |

**归类**：新增章节（协议完整性重要组成）

---

## 三、表述差异（同一概念，精炼程度不同）

### 1. 核心断言：`protocol is the cognition substrate`
| 项目 | 内容 |
|------|------|
| session 位置 | §3 Foundational Principle |
| session 表述 | `protocol is the cognition substrate`，与 `memory is the cognition substrate` 对比 |
| spec 现状 | 分散在 §1.3（认知对齐平面）、§2 核心洞察、§3.5（运行时模型），无单一明确断言 |
| 差异 | session 是一句话核心断言；spec 用多章节分散表述 |

**归类**：表述强化（将分散的表述汇聚为明确的核心断言，放在 §2 或 §3）

---

### 2. Architecture 层级图（§5）
| 项目 | 内容 |
|------|------|
| session 位置 | §5 |
| session 表述 | Hermes Agent → mem0ress Skill → Slash Commands → Runtime → Filesystem Protocol → Judge Agent |
| spec 现状 | §3.1 设计原则有相关描述，但无层级图；§5.1.2 参与方与职责边界有职责表 |
| 差异 | session 有清晰的 6 层垂直流向图；spec 用职责表替代 |

**归类**：可补充层级图到 §3.1 或 §5

---

### 3. Snapshot Success Condition（§12.4）
| 项目 | 内容 |
|------|------|
| session 位置 | §12.4 |
| session 表述 | Recovery SHOULD succeed using ONLY: task.md + recent snapshots + gotchas.md + latest judge verdict. Without requiring: transcript replay / runtime continuation / hidden memory state. |
| spec 现状 | §5.2 认知构建描述了 session 快照是数据来源，但无明确的"成功恢复条件"断言 |
| 差异 | session 明确断言恢复成功的充要条件；spec 无此断言 |

**归类**：补充到 §5.2 或新增 §12.4

---

## 四、一致内容（无需修改）

| session 章节 | spec 对应 | 核对结论 |
|-------------|-----------|---------|
| §2 System Definition | §1.2 系统定位 | ✅ 语义一致，表述方式不同 |
| §4 System Goal | §1.4 核心解法概览、§2 核心洞察 | ✅ 一致 |
| §6 Ownership Boundaries | §3.2 认知归属模型 | ✅ 一致（四层分离） |
| §7 Semantic Authority | §3.2-3.3 | ✅ 一致 |
| §8.1 Unified Skill Constraint | §3.4 Skill 作为认知操作符 | ✅ 一致 |
| §8.2 Skill Philosophy | §3.4 | ✅ 一致 |
| §10.1 Execution Lifecycle | §5.1 执行循环 | ✅ 一致 |
| §10.2 Lifecycle Authority | §5.1.2 参与方与职责边界 | ✅ 一致 |
| §11 Protocol Surface（文件定义） | §4.5 文档数据模型 | ✅ 一致 |
| §11.2 task.md | §4.5 | ✅ 一致 |
| §11.3 session.md | §4.5、§5.2 | ✅ 一致（append-only delta stream） |
| §11.4 gotchas.md | §4.5 | ✅ 一致 |
| §11.5 judge.md | §4.5 | ✅ 一致 |
| §13 Recoverability | §1.3、§2 核心洞察 | ✅ 一致 |
| §14 Plane Model | §4.3 双重平面 | ✅ 一致 |
| §15 status_plane | §4.3 | ✅ 一致 |
| §16 data_plane | §4.3 | ✅ 一致 |
| §17 Judge Model | §5.4 任务检验 | ✅ 一致 |
| §17.1 Judge Isolation | §5.4、§5.1.2 | ✅ 一致 |
| §18.1 Runtime Responsibilities | §3.3、§3.5 | ✅ 一致 |
| §18.2 Runtime MUST NOT | §3.3、§3.5 | ✅ 一致 |
| §19 Filesystem Layout | §4.5 | ✅ 一致 |
| §21 Final Principle | §1.2、§6 结语 | ✅ 一致 |

---

## 五、归类汇总

| 类别 | 数量 | 建议 |
|------|------|------|
| 缺失（spec 无，session 有） | 3 | 新增 |
| 表述差异（同一概念，精炼程度不同） | 3 | 强化/补充 |
| 一致（无需修改） | 23 | 忽略 |

---

## 六、建议优先级

| 优先级 | 项目 | 理由 |
|--------|------|------|
| **P1** | **Snapshot Semantics**（新增 §12） | 快照语义是协议核心，spec 缺少独立章节定义 |
| **P1** | **Failure Conditions**（新增 §20） | 协议完整性重要组成，6 种降级条件是 mem0ress 特色防御性描述 |
| **P2** | **核心断言强化**（§3） | `protocol is the cognition substrate` 应作为明确陈述而非分散隐含 |
| **P2** | **Slash Command Model**（补充到 §5） | 命令级约束是协议表面的一部分 |
| **P3** | Architecture 层级图（补充到 §3） | 锦上添花 |
| **P3** | Snapshot Success Condition（补充到 §5.2） | 若新增 §12 则包含，否则补充到认知构建章节 |

---

## 七、rev-0.4 相对 rev-0.3 的变化处理

| rev-0.3 原建议 | rev-0.4 变化 | 建议 |
|---------------|-------------|------|
| Technology Constraints（新增） | **已移除** | 不再建议加入 spec |
| MVP Command Surface（新增） | **已移除** | 不再建议加入 spec |
