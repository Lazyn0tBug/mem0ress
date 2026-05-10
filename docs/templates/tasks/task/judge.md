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

**LLM-as-a-Judge Prompt Template:**
```text
请作为独立的裁判，比对以下目标图景 (Picture) 与基于最新 Data Plane commit 提取的实际代码产出。

【目标图景】: "{task.md#Picture}"
【实际产出】: [水化的代码切片/测试日志]

请评估当前产出是否在语义和最终体验上完美达成了图景描述。如果不符合，请指出具体的偏差原因。如果符合，请返回 PASS
```

**输出格式：**
- `PASS`: 实际产出在语义上完美达成 Picture
- `FAIL: <具体偏差描述>`: 存在语义偏差，需指出具体原因
