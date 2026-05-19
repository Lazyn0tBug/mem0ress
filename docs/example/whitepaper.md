# 案例：AI Agent Framework 白皮书（认知交付）

> 任务：撰写一份能够被技术团队、投资人和高级工程人员独立阅读并理解的 Agent Framework 白皮书
>
> 类型：认知交付
>
> 特色：PRC 推导顺序；Phase 分组 Todo；Terminology 一致性；Tier 3 语义对齐

---

## task.md

```yaml
---
id: 9p2n5w
type: task
status: COMPLETED
created_at: 2026-01-10T09:00:00Z
completed_at: 2026-01-18T17:30:00Z
---

# Task: AI Agent Framework 白皮书

## Picture

> 一份能够被技术团队、投资人和高级工程人员独立阅读并理解的 Agent Framework 白皮书。
>
> 阅读者能够：
> - 理解系统的核心认知模型
> - 理解与传统 workflow agent 的区别
> - 理解 runtime / cognition separation
> - 在不依赖作者解释的情况下复现整体架构
>
> 文档具备：完整结构、一致术语、清晰图景、工程可信度

---

## Requirements

- [x] R-1: 文档结构完整（Executive Summary / Problem Statement / Architecture /
         Cognitive Model / Runtime Model / Protocol Design / Failure Recovery / Future Work）
         verify_cmd: python scripts/check_headings.py docs/whitepaper.md
- [x] R-2: 术语一致（定义并全篇一致使用： Cognitive Ownership / Semantic Intent /
         Runtime / Verify / Cognitive Artifact / PRC）
         verify_cmd: python scripts/check_glossary.py docs/whitepaper.md
- [x] R-3: 至少包含 3 个架构图（系统层级图 / 生命周期图 / Agent-Runtime 边界图）
         verify_cmd: python scripts/check_diagrams.py docs/whitepaper.md
- [x] R-4: 必须存在失败模型章节（semantic drift / ownership split /
         runtime instability / context contamination）
         verify_cmd: python scripts/check_section.py docs/whitepaper.md "Failure Recovery"
- [x] R-5: 白皮书长度不少于 8000 字（中文）或 5000 词（英文）
         verify_cmd: python scripts/check_wordcount.py docs/whitepaper.md --min 5000
- [x] R-6: 可独立阅读（新读者无需额外口头解释即能理解核心设计决策）
         verify_cmd: manual  # Tier 3 semantic review required

---

## Constraints

- C-1: 绝不允许使用未定义术语，或在不同章节改变同一术语含义
- C-2: 绝不允许将 deterministic runtime 与 cognitive reasoning 混写为同一层
- C-3: 绝不允许用 marketing language 替代 architecture explanation
        （如"革命性"、"下一代"、"颠覆式"，除非给出明确技术依据）
- C-4: 绝不允许引入无法验证的 Requirement
        （如"非常智能"、"体验很好"等主观描述）

---

## Todos

### Phase 1 — Research
- [ ] T-1: 收集现有 agent framework 架构
- [ ] T-2: 对比 workflow orchestration 与 cognitive persistence
- [ ] T-3: 建立核心术语表
- [ ] T-4: 输出核心 worldview 草稿

### Phase 2 — Architecture Design
- [ ] T-5: 设计 runtime / cognition separation
- [ ] T-6: 设计 protocol layering
- [ ] T-7: 设计 Verify lifecycle
- [ ] T-8: 设计 cognitive artifact model

### Phase 3 — Whitepaper Writing
- [ ] T-9: 编写 Introduction / Executive Summary
- [ ] T-10: 编写 Architecture section
- [ ] T-11: 编写 Protocol Design section
- [ ] T-12: 编写 Failure Recovery section
- [ ] T-13: 编写 Future Work section

### Phase 4 — Validation
- [ ] T-14: 执行术语一致性检查（glossary scan / duplicated-definition scan）
- [ ] T-15: 执行章节完整性检查
- [ ] T-16: 执行 word count 检查
- [ ] T-17: 执行 semantic review（Tier 3）
- [ ] T-18: 输出最终 PDF
```

---

## Verify 重点

### Tier 0 — Constraints 约束检查

检查所有 Constraints 是否有违反记录：

- C-1 验证：扫描全文，检查是否存在未在 glossary 定义的术语，或同一术语出现矛盾定义
- C-2 验证：扫描全文，检查是否存在将 runtime 和 cognition 描述为同层的段落
- C-3 验证：扫描全文，检查 marketing language 出现位置是否有技术依据支撑
- C-4 验证：检查所有 Requirements 是否具有可验证的 verify_cmd

### Tier 1 — Todo & Subtask 完成检查

所有 T-1 ~ T-18 必须标记为 `[x]`。

### Tier 2 — Requirements 验收检查

| Requirement | verify_cmd | 结论条件 |
|------------|-----------|---------|
| R-1: 结构完整 | `check_headings.py` | 8 个章节全部存在 |
| R-2: 术语一致 | `check_glossary.py` | 6 个术语定义存在且无重复定义 |
| R-3: 至少 3 个图 | `check_diagrams.py` | image reference ≥ 3 |
| R-4: 失败模型章节 | `check_section.py` | 4 个子议题全部存在 |
| R-5: 长度 | `check_wordcount.py` | ≥ 5000 词 |
| R-6: 可独立阅读 | `manual` | Tier 3 触发 |

### Tier 3 — 语义对齐检查

**Trigger:** R-6 标记为 `manual`，必须触发 Tier 3。

**Verify Prompt:**

```
【目标图景】
一份能够被技术团队、投资人和高级工程人员独立阅读并理解的 Agent Framework 白皮书。
阅读者能够：
- 理解系统的核心认知模型
- 理解与传统 workflow agent 的区别
- 理解 runtime / cognition separation
- 在不依赖作者解释的情况下复现整体架构

【实际产出】
- [实际产出的完整内容摘要]
- 核心架构图：[数量]
- 术语表：[术语列表]

【检验指令】
请判断：
1. 新读者是否能仅凭白皮书内容复现整体架构（无需口头解释）？
2. cognitive model 和 runtime model 的 separation 是否在全文中保持一致？
3. 是否存在 semantic drift 或逻辑矛盾？
4. 文档是否真正传达了与传统 workflow agent 的本质区别？

如果达成，返回 PASS。
如果未达成，返回 FAIL，并指出具体偏差维度。
如果证据不足，返回 UNCERTAIN。
```

---

## PRC 推导过程

### Step 1: 定义 Picture

与利益相关者（技术团队 + 投资人）沟通后，确认白皮书的受众是"能独立理解架构的高级工程人员"，
核心价值是传达 **runtime / cognition separation**。

### Step 2: 推导 Requirements

从 Picture 推导出 6 个 Requirements：

| 从 Picture 推导 | 对应 Requirement |
|----------------|----------------|
| "独立阅读并理解" → 结构完整 | R-1: 8 个章节 |
| "一致术语" | R-2: 术语一致性 |
| "工程可信度" → 架构图佐证 | R-3: ≥ 3 个图 |
| "Failure Recovery" | R-4: 失败模型章节 |
| "独立阅读" → 长度支撑 | R-5: ≥ 5000 词 |
| "不依赖作者解释" | R-6: 可独立阅读（Tier 3） |

### Step 3: 推导 Constraints

从领域知识推导 Constraints：

- C-1: 术语漂移是白皮书最常见的失效模式
- C-2: runtime/cognition 混层是最常见的架构混淆
- C-3: marketing language 破坏技术文档可信度
- C-4: 无法验证的 Requirement 违反 CAP 协议原则

### Step 4: 冲突检测

R-1（结构完整）与 C-2（不混层）存在潜在矛盾：
若 Architecture 章节同时描述 runtime 和 cognition，容易混层。
→ 决议：在 Protocol Design 章节明确分离两节，分别描述。

### Step 5: 推导 verify_cmd（Agent 辅助）

每条 Requirement 生成后，Agent 负责推导对应的 `verify_cmd`：

| Requirement | verify_cmd 推导 | 说明 |
|------------|----------------|------|
| R-1: 结构完整 | `python scripts/check_headings.py` | Agent 生成：检查 8 个章节 heading 是否存在 |
| R-2: 术语一致 | `python scripts/check_glossary.py` | Agent 生成：扫描术语出现位置，检测重复定义 |
| R-3: ≥3 个图 | `python scripts/check_diagrams.py` | Agent 生成：统计 markdown image reference 数量 |
| R-4: 失败模型章节 | `python scripts/check_section.py` | Agent 生成：检查章节存在及 4 个子议题 |
| R-5: ≥5000 词 | `python scripts/check_wordcount.py --min 5000` | Agent 生成：字数统计 |
| R-6: 可独立阅读 | `manual` | Agent 判断：需 Tier 3 语义推断，无法自动验证 |

**注意：** `verify_cmd` 命令由 Agent 生成，用户只需表达语义意图（如"白皮书需要至少3个架构图"），Agent 负责转化为可执行验证命令。

---

## 与软件交付案例的关键差异

| 维度 | 认知交付（白皮书） | 软件交付（OAuth） |
|------|-----------------|-----------------|
| 产出性质 | cognition artifact | software artifact |
| Tier 3 权重 | 极高（必须触发） | 高（Picture 含主观体验） |
| Tier 2 验证 | 结构扫描、术语检查、字数统计 | pytest 自动化测试 |
| 失败风险 | semantic incoherence | implementation bug |
| Todo 分组 | Phase 分组（Research/Architecture/Writing/Validation） | 扁平 T-1~T-N |
| Constraints 重点 | 内容约束（术语、表述方式） | 技术约束（安全、性能） |
