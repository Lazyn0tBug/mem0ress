---
task_id: "{task_id}"
type: judge
---

# Judge Verification — {task_id}

> Judge Agent 专属文件，主 Agent 只读不写。
> 每次检验触发后追加一个 Turn 块，不覆盖历史。
> Tier 0/1 由 Judge Agent 用纯逻辑执行；Tier 2 运行测试命令；Tier 3 按需触发。
> 任何 Tier 失败立即停止，输出 FAILED，不继续执行后续 Tier。

---

## Turn {N.M}
**Timestamp:** YYYY-MM-DDTHH:mm:ssZ
**Verdict:** {PASSED | FAILED}

---

### Tier 0 — Constraints 约束检查

> 逐条比对 Constraints，在 session.md 和 gotchas.md 中寻找违反记录。
> 结论客观，不做修复建议。

| Constraint | 验证手段 | 结论 |
|-----------|---------|------|
| C-1: {约束描述} | {静态扫描 / 正则匹配 / 日志检查} | ✅ PASS / ❌ FAIL |
| C-2: {约束描述} | {验证手段} | ✅ PASS / ❌ FAIL |

**Findings:** {如有违反，描述违反事实：哪条 Constraint、在哪个 Turn 被逾越。无则写"—"。}

---

### Tier 1 — Todo & Subtask 完成检查

> 机械状态检查，不涉及语义判断。

- [ ] 所有 `task.md` 中的 Todos 已标记 `[x]`
- [ ] 所有直接子任务已处于终态（COMPLETED 或 ABANDONED）

**未完成项：** {列出未完成的 Todo id 和子任务 id，或写"—"。}

---

### Tier 2 — Requirements 验收检查

> 运行测试命令或执行可验证动作，不依赖 LLM 推断。
> 每条 Requirement 必须有对应的可运行验证手段。

| Requirement | 验证命令 | 输出摘要 | 结论 |
|------------|---------|---------|------|
| R-1: {需求描述} | `{npm run test:xxx 或 pytest tests/xxx.py}` | {命令输出关键行} | ✅ PASS / ❌ FAIL |
| R-2: {需求描述} | `{验证命令}` | {输出摘要} | ✅ PASS / ❌ FAIL |

**Findings:** {未满足的 Requirement 及原因，或写"—"。}

---

### Tier 3 — 语义对齐检查（按需触发）

> 仅在以下情况触发：Picture 涉及主观判断或用户体验；Constraints 与 Picture 存在语义歧义；
> 主 Agent 或利益相关者显式请求。
> Tier 0/1/2 任一失败时跳过。

**Trigger Condition:** {是否触发及原因。不触发则写"SKIPPED"。}

**Prompt（发送给 Judge LLM 的完整上下文）：**
```
【目标图景】
{task.md#Picture 的实际内容}

【实际产出】
{来自 session.md 最新 Code Progress + Data Plane 的实际代码描述或测试日志}

【检验指令】
请判断实际产出是否在语义和最终体验上达成了目标图景。
如果达成，返回 PASS。
如果未达成，返回 FAIL，并指出具体偏差：哪个维度不符合图景，为什么。
不要给出修复建议，只报告事实。
```

**Verdict:** {PASS / FAIL: {具体偏差描述}}

---

**Overall Verdict:** {PASSED | FAILED}
**Summary:** {Judge Agent 的整体说明，FAILED 时说明是哪个 Tier 失败及原因。}
