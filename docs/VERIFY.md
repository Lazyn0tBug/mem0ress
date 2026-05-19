# VERIFY.md

`VERIFY.md` 是验证协议的 Canonical 真源。每个 Task 创建时生成（空文件），随着任务执行逐步填充。

**与 task.md 的关系**：task.md 的 Constraints 和 Requirements 条目不在此重复。task.md 的验证结果字段是对 VERIFY.md 中对应条目的引用（Reference Record），VERIFY.md 才是 Canonical。

## 核心设计原则

1. **验证方式通过交互式对话确认，不追求预先全覆盖**
2. **marker 本身就是验证结论，无需独立 section**
3. **Agent 可写验证结论，执行所依据的程序由人预先验证**
4. **Picture 直接确认（公理），Constraints/Requirements 先确认验证方式再记录结论**

## 条目格式

```markdown
## Picture

[.] T3-1
   description: <引用 task.md 中的 Picture 描述>
   conclusion: <验证结论>

## Constraints

[.] C-1
   description: <引用 task.md 中的约束描述>
   verification_method: checked / command / skip
   conclusion: <验证结论>

(.) C-2
   description: <引用 task.md 中的约束描述>
   verification_method: checked / command / skip
   conclusion: <验证结论>

## Requirements

[.] R-1
   description: <引用 task.md 中的需求描述>
   verification_method: checked / command / skip
   conclusion: <验证结论>

(.) R-2
   description: <引用 task.md 中的需求描述>
   verification_method: checked / command / skip
   conclusion: <验证结论>
```

## marker 语义

| marker | 类型 | 说明 |
|--------|------|------|
| `[]` | 待确认 | 尚未通过对话确认验证方式 |
| `[.]` | checked 已确认 | 交互式验证方法已确认 |
| `(.)` | command 已确认 | 命令式验证方法已确认 |
| `{.}` | skip 已确认 | 跳过，记录理由 |
| `[×]` | 违规中 | Constraint 已被违反（参考信号，状态记录，不阻塞） |
| `{×}` | 跳过已确认 | Skip 已确认并执行 |

## 三要素验证逻辑

| 要素 | 对话确认什么 | 验证什么 |
|------|-------------|---------|
| Picture | Picture 条目本身是否成立 | 无需验证，直接确认 |
| Constraints | 验证方式（怎么算违规） | 验证结论 |
| Requirements | 验证方式（怎么算满足） | 验证结论 |

**Picture**：通过对话直接确认条目成立，作为公理。不需要 verification_method。

**Constraints / Requirements**：通过对话确认验证方式（checked/command/skip），然后执行验证并记录结论。

## 写入规则

1. **`[.]` / `(.)` / `{.}` 只能由人写入**：验证程序经人确认后，人将其标记为已确认
2. **Agent 可写验证结论 `(.)` / `{.} ` / `[×]`**：Agent 执行验证后写入结果
3. **`[]` 可以由 Agent 写入**：作为占位符，等待后续对话确认验证方式
4. **已确认的条目如需修改**：将 marker 改回 `[]` / `()` / `{}`，重新进入讨论状态，不直接删除历史记录
