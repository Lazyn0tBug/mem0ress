好，这次我直接给你一个明确、可落地、适合进入规范的 `Verification Contract` 设计。

不再泛谈 `/goal`。

你提到参考 Hermes/Codex `/goal`，
我认为真正值得吸收的是：

# “完成条件协议化”

而不是：

* autonomous loop
* 自动继续执行

所以：
你们规范里的 `Verification Contract`
本质上应该解决：

# “什么才算真正完成？”

并且：

* 可恢复
* 可审计
* 可 replay
* 支持 semantic verification
* 支持 deterministic verification

---

# 一、Verification Contract 的正式定义

我建议：

---

# Verification Contract

定义：

> A Verification Contract defines the required conditions, validation methods, semantic expectations, and stopping criteria that determine whether a task is considered complete.

---

它回答：

```text id="vc1"
What does it mean for this task to be true/completed?
```

而不是：

```text id="vc2"
How do we run tests?
```

---

# 二、Verification Contract 在协议中的位置

我建议：

```text id="vc3"
Task
├── PRC
├── Verification Contract
└── Execution State
```

即：

---

# PRC

定义：

```text id="vc4"
What should become true?
```

---

# Verification Contract

定义：

```text id="vc5"
How do we determine truth?
```

---

# Judge

定义：

```text id="vc6"
Was truth actually achieved?
```

---

这是三个不同层。

---

# 三、Verification Contract 的目标

必须同时支持：

| 类型                       | 示例                        |
| ------------------------ | ------------------------- |
| Deterministic Validation | build / lint / schema     |
| Structural Validation    | headings / files / routes |
| Behavioral Validation    | responsive / deployment   |
| Semantic Validation      | coherence / worldview     |
| Constraint Validation    | forbidden conditions      |
| Completion Validation    | todo coverage             |

---

因此：

# Verification Contract 必须是多层验证协议。

---

# 四、最终推荐结构（正式版）

我建议：

```yaml id="vc7"
verification_contract:
  philosophy:
  tiers:
  targets:
  methods:
  triggers:
  stop_conditions:
  failure_conditions:
  evidence_requirements:
```

下面我详细定义。

---

# 五、字段设计（规范建议）

---

# 1. philosophy

定义：

```text id="vc8"
本任务验证的核心哲学与优先级
```

例如：

```yaml id="vc9"
philosophy:
  prioritize_semantic_coherence: true
  prioritize_deterministic_validation: true
  tolerate_partial_visual_variance: true
```

作用：

* 指导 Judge
* 指导 reconciliation
* 指导 future continuation

---

# 2. tiers

定义：

# 验证层级定义

我建议正式固定：

---

## Tier 0 — Constraint Validation

检查：

# 不允许发生什么

例如：

* forbidden architecture
* undefined terminology
* security violation

---

## Tier 1 — Completion Validation

检查：

# 是否真正完成了所有 required work

例如：

* todos
* subtasks
* artifacts

---

## Tier 2 — Deterministic Validation

检查：

# 可稳定执行验证

例如：

* build
* lint
* tests
* schema validation
* route validation

---

## Tier 3 — Semantic Validation

检查：

# 语义与图景是否成立

例如：

* coherence
* architecture consistency
* narrative alignment
* worldview integrity

---

建议 schema：

```yaml id="vc10"
tiers:
  tier0:
    enabled: true

  tier1:
    enabled: true

  tier2:
    enabled: true

  tier3:
    enabled: true
```

---

# 3. targets

定义：

# 需要验证的对象

例如：

```yaml id="vc11"
targets:
  - requirement: R-1
    type: structural

  - requirement: R-2
    type: semantic

  - requirement: R-3
    type: deterministic
```

---

# 4. methods

定义：

# 如何验证

这是：

# verify_cmd 真正应该存在的位置。

例如：

```yaml id="vc12"
methods:
  - target: R-1
    tier: tier2
    method: command
    command: "python scripts/check_headings.py"

  - target: R-2
    tier: tier3
    method: judge_review

  - target: R-3
    tier: tier2
    method: command
    command: "npm run build"
```

---

# 五个关键点

这里我建议：

---

## method types

固定支持：

```yaml id="vc13"
method:
  - command
  - script
  - parser
  - diff
  - judge_review
  - human_review
```

---

## command 不直接写在 requirement

避免：

```markdown id="vc14"
R-1
verify_cmd: xxx
```

因为：

* semantics 和 execution 耦合过深

---

## Tier 3 不允许 command-only

例如：

```text id="vc15"
worldview coherence
```

不能：

```bash id="vc16"
grep coherent
```

---

## method 必须可 replay

不能：

* 即时 hallucinated verification

---

## dynamic generation allowed

但：

```text id="vc17"
generated
→ persisted
→ replayable
```

---

# 5. triggers

定义：

# 什么时候触发验证

例如：

```yaml id="vc18"
triggers:
  on_task_complete:
    - tier1
    - tier2

  on_major_architecture_change:
    - tier3

  on_requirement_change:
    - tier0
    - tier3
```

---

# 6. stop_conditions

定义：

# 什么才算真正完成

这是整个 contract 最关键部分。

例如：

```yaml id="vc19"
stop_conditions:
  require_all_tier0_pass: true
  require_all_tier1_pass: true
  require_all_tier2_pass: true
  require_tier3_alignment: true
```

---

这其实就是：

# `/goal` 真正值得学习的部分。

即：

# completion must be protocolized.

---

# 7. failure_conditions

定义：

# 什么必须立即失败

例如：

```yaml id="vc20"
failure_conditions:
  - undefined_terminology
  - architecture_contradiction
  - failed_build
  - forbidden_dependency
```

---

# 8. evidence_requirements

定义：

# 必须保留哪些验证证据

例如：

```yaml id="vc21"
evidence_requirements:
  retain_logs: true
  retain_judge_reviews: true
  retain_verification_reports: true
```

---

# 六、白皮书案例（推荐）

---

## Tier 0

* undefined terminology
* contradictory worldview

---

## Tier 1

* all sections exist

---

## Tier 2

* glossary scan
* heading validation
* word count

---

## Tier 3

* semantic coherence
* architecture integrity
* independent readability

---

# 七、网站案例（推荐）

---

## Tier 0

* forbidden architecture
* broken docs routing

---

## Tier 1

* all pages exist

---

## Tier 2

* lighthouse
* responsive test
* build

---

## Tier 3

* messaging coherence
* cognition/runtime distinction clarity

---

# 八、为什么这个结构是长期稳定的

因为它解决了：

---

## 1. 完成 ≠ Todo Done

---

## 2. Tests Pass ≠ Goal Achieved

---

## 3. Deterministic Validation ≠ Semantic Alignment

---

## 4. Verification ≠ Judge

---

## 5. Runtime Validation ≠ Cognitive Evaluation

---

# 九、最终建议（进入 schema）

我建议正式定义：

---

# Verification Contract

作为：

# Task 的一级协议对象

即：

```yaml id="vc22"
task:
  prc:
  verification_contract:
  execution_state:
```

---

而不是：

```yaml id="vc23"
verify_cmd:
```

这种单字段模型。

---

# 十、最后一句结论

我认为：

Codex/Hermes `/goal`
真正值得借鉴的，
不是：

* autonomous loop

而是：

# “completion condition must become protocol”

而你们现在应该进一步升级为：

# “semantic completion protocol”

这就是 `Verification Contract` 的真正意义。
