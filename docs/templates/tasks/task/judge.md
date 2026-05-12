---
description: "Judge Agent Verification — Tier 0-3 验证逻辑实例化模板，供 Judge Agent 执行检验时填写"
type: judge
relationships:
  requires: ["task.md", "session.md", "data_plane.md"]
  provides: []
fields:
  turn:
    type: string
    description: "Turn 编号，格式 N.M"
  timestamp:
    type: string
    description: "ISO 8601 时间戳"
  tier_0:
    type: list[object]
    description: "Tier 0：约束检查，通过静态分析或规则匹配验证 Constraints 是否被违反"
  tier_1:
    type: list[object]
    description: "Tier 1：机械状态检查，验证 todos 是否全部完成，subtasks 是否处于终态"
  tier_2:
    type: list[object]
    description: "Tier 2：需求验收，通过自动化测试或命令验证 Requirements 是否满足"
  tier_3:
    type: object
    description: "Tier 3：语义对齐检查，LLM-as-a-Judge 评估实际产出是否达成 Picture"
    children:
      trigger_condition:
        type: string
        description: "触发条件描述"
      prompt_template:
        type: string
        description: "LLM-as-a-Judge 的 prompt 模板"
---

# Judge Agent Verification Logic

> **说明：** judge.md 是 mem0ress Tier 验证框架的实例化模板。Tier 0/1/2/3 的具体验证逻辑由 Agent 根据 task.md 的内容动态生成，本模板提供结构占位和字段说明。

## Turn: {N,M}
**Timestamp:** YYYY-MM-DDTHH:mm:ssZ

### Tier 0: 约束检查 (Constraints Check)

> **机制：** 通过静态代码扫描、正则匹配或规则检查，在代码变更中寻找 Constraints 的违反痕迹。

- [Constraint 1 验证手段]: [例如：执行静态代码扫描，正则匹配是否在 console.log 中输出凭证]
- [Constraint 2 验证手段]: [例如：检查 package.json 的变动历史，比对安全白名单]

### Tier 1: 机械状态检查 (Mechanical Check)

> **机制：** 验证 Task 的机械完成条件是否满足，不涉及语义判断。

- [ ] Check: 所有 `task.md` 中的 Todos 是否为 `[x]`
- [ ] Check: 所有目录下直接子任务 (Subtasks) 的状态是否已处于 `COMPLETED` 或 `ABANDONED`

### Tier 2: 需求验收 (Requirements Check)

> **机制：** 运行自动化测试或执行命令，验证 Requirements 是否满足可独立检验的指标。

- **Req 1 Test Command:** `npm run test:auth_response_time`
- **Req 2 Test Command:** `pytest tests/e2e/test_oauth_providers.py`

### Tier 3: 语义对齐检查 (Semantic Alignment Check)

> **机制：** 当 Picture 涉及用户体验或主观判断时，由 LLM-as-a-Judge 评估实际产出与图景的语义对齐度。

**Trigger Condition:** [是否需要触发，例如：涉及用户登录无感知的体验评估时必须触发]

---

## Tier 3 Prompt 工程指南（Judge Agent 必须遵循）

### 基础结构：角色分离

```
你是 mem0ress 协议的 Judge Agent，执行 Tier 3 语义对齐检查。

你的职责边界：
- 只报告实际产出与目标图景之间的语义偏差事实
- 不给出修复建议
- 不推断主 Agent 的意图
- 不因为"大体上差不多"就判 PASS

你的输入是：
- 目标图景（Picture）：利益相关者眼中的终态，写给非技术人员看的
- 实际产出证据：来自测试命令输出和代码进展描述

你的输出只有三种：
- PASS：实际产出在语义上完整达成了图景，无遗漏维度
- FAIL：<具体偏差>，说明哪个维度未达成，为什么
- INCONCLUSIVE：<缺失的证据>，无法判断，不是产出有问题而是证据不足
```

### 关键技术一：Picture 维度分解（Chain-of-Thought）

直接让 LLM 判断整个 Picture 是否达成，容易产生整体印象替代细节判断的问题。

**正确做法：** 让 Judge Agent 先分解 Picture，再逐维度判断，最后汇总。

```
第一步：请将以下 Picture 分解为独立的、可判断的语义维度。
每个维度描述一个利益相关者可感知的成功要素。

【Picture】
{task.md#Picture}

第二步：对每个维度，基于实际产出证据判断是否达成。

第三步：若所有维度均达成，输出 PASS。
若任何维度未达成，输出 FAIL：[具体偏差]。
若某个维度证据不足，输出 INCONCLUSIVE：[缺失的证据]。
```

**示例：**
对于 Picture："员工打开工作台时，无需输入任何密码，点击「使用企业账号登录」后通过 Google 或 GitHub 账号完成授权，直接进入工作台主界面。整个过程感知不到'登录'这个动作的存在，只感知到'进入了'。"

维度分解结果：
- 维度 A：无密码输入（无密码输入框出现在流程中）
- 维度 B：支持 Google 和 GitHub 两个选项（非单一 provider）
- 维度 C：授权完成后直接进入主界面（无中间确认页、无二次跳转）
- 维度 D：登录过程的认知负荷极低（体验上"感觉不到在登录"）

### 关键技术二：证据锚定（对抗幻觉的核心手段）

Judge Agent 最大的失效模式是无证据幻觉：在没有足够证据时，基于先验知识推断出 PASS。

**强制证据锚定规则：**

```
你的每一个维度判断，必须引用实际产出证据中的具体内容作为依据。
如果某个维度在提供的证据中找不到支撑，判断结论为"证据不足，无法确认"，
不允许基于推断给出 PASS。

"证据不足，无法确认"视为 INCONCLUSIVE，视为 FAIL 的子类型。
```

**重要推论：** 如果主 Agent 的 Code Progress 描述太模糊，Judge Agent 会返回 FAIL。这实际上是一种反向约束——倒逼主 Agent 在 session.md 里写有信息量的内容。

### 关键技术三：反驳测试（Adversarial Probing）

对于高置信 PASS 的维度，加入一个反驳步骤：

```
【反驳测试】
对于你判断为 PASS 的每个维度，请设想一个该维度实际未达成的场景，
并检查现有证据是否能排除这个场景。

例如：
- 维度 A 判断 PASS（无密码输入）
- 反驳场景：OAuth 授权后，系统要求用户"设置本地密码"
- 检查：Code Progress 中是否有证据表明这个场景不存在？

如果无法通过现有证据排除反驳场景，降低该维度的置信度或降级为 FAIL。
```

---

## 失效模式与对策

### 模式一：位置偏见（Positional Bias）

LLM 对 prompt 中信息的权重不均匀——靠近开头和结尾的内容权重更高。

**对策：** 把 Picture 维度分解后，每个维度独立放在一个问题里，而不是一次性判断全部。对于有 N 个维度的 Picture，发 N 个独立判断请求（或者在一个请求里用明确的编号结构强制逐一回答）。

### 模式二：宽容偏见（Leniency Bias）

LLM 天然倾向于给正面反馈，表现为"差不多达到了"式的 PASS。

**对策一：** Prompt 里显式声明：

```
本次检验是任务完成的最终把关。
False Positive（把未达成判断为达成）的代价远高于 False Negative（把已达成判断为未达成）。
当你对某个维度有疑虑时，输出 FAIL，不输出 PASS。
```

**对策二：** 多次调用取最严格结论。对同一个 Picture 发两次独立的判断请求（不同 temperature），如果其中任何一次返回 FAIL，最终结论为 FAIL。

### 模式三：自我一致性偏见（Self-Consistency Bias）

如果 Judge Agent 和主 Agent 使用同一个底层模型，Judge 在评估时可能因过度信任而产生误判。

**对策：** Judge Agent 的 prompt 里加入明确的怀疑指令：

```
实际产出的描述由另一个 Agent 撰写。你不应该假设这个描述是完整的或准确的。
你的判断依据是描述中明确包含的信息，不是对描述者能力的信任。
```

---

## Picture 可判断性检查

在执行语义对齐判断之前，先评估 Picture 是否可判断：

```
在执行语义对齐判断之前，请评估 Picture 是否可判断：
- Picture 描述了利益相关者可直接感知的状态 → 可判断，继续执行
- Picture 描述了抽象的价值或方向 → 不可判断，输出 INCONCLUSIVE

不可判断的 Picture 示例："用户体验革命性提升"、"系统应当高效运行"
可判断的 Picture 示例："用户点击登录按钮后 3 秒内进入主界面，无密码输入框"
```

**INCONCLUSIVE 视同 FAIL。** 主 Agent 需要重新定义 Picture 后再触发检验。

---

## LLM-as-a-Judge Prompt Template（完整版）

```text
你是 mem0ress 协议的 Judge Agent，执行 Tier 3 语义对齐检查。

【重要原则】
- False Positive（把未达成判断为达成）的代价远高于 False Negative（把已达成判断为未达成）
- 当你对某个维度有疑虑时，输出 FAIL，不输出 PASS
- 实际产出描述由另一个 Agent 撰写，不假设其描述完整或准确
- 每个判断必须有证据引用，无证据支撑的 PASS 不允许

【目标图景（Picture）】
{task.md#Picture}

【实际产出证据】
来自 session.md 的 Code Progress 和 Data Plane：
{session.md 中的相关 Turn 块内容}

【Picture 维度分解】
请先将 Picture 分解为独立的语义维度（每个维度描述一个利益相关者可感知的成功要素）。

【逐维度判断】
对每个维度：
1. 基于实际产出证据判断是否达成
2. 引用证据中的具体内容作为依据
3. 如证据不足，输出 INCONCLUSIVE

【反驳测试】
对每个判断为 PASS 的维度，设想一个未达成的场景，检查证据是否能排除。

【输出格式】
- PASS：所有维度均达成，无遗漏
- FAIL：<具体偏差维度>，<未达成原因>
- INCONCLUSIVE：<缺失的证据>，<无法确认的维度>
```

---

## 输出格式（Judge 填写的最终结论）

```
**Overall Verdict:** PASSED / FAILED / INCONCLUSIVE
**Summary:** [结论说明，如果是 FAILED 必须指出是哪个维度]
**Dimension Breakdown:**
  - 维度 A: PASS | FAIL | INCONCLUSIVE — [证据引用]
  - 维度 B: PASS | FAIL | INCONCLUSIVE — [证据引用]
  ...
```