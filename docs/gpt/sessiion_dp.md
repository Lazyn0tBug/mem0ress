我认真想了这个问题，我现在的结论是：

> **v0.1-alpha 不建议引入 data_plane.md。**

而且更进一步：

> 你现在这套协议，如果强行加入 data_plane.md，很容易开始“协议层抽象过度”。

这是我认真推演后的判断。

---

# 一、先问本质：Data Plane 到底想表达什么？

你之前提到 Data Plane，本质上是在表达：

```text id="q8m2vx"
Task 当前可被 Judge / Agent 消费的事实性证据集合。
```

例如：

```text id="u4q7pk"
生成文件
测试结果
日志
运行输出
artifact
验证结果
```

也就是说：

> Data Plane 其实是“事实层（evidence layer）”。

这个方向本身没错。

---

# 二、但问题是：你现在已经有别的层在承担这些职责了

现在你的协议已经有：

| 文件           | 职责                   |
| ------------ | -------------------- |
| task.md      | canonical task state |
| session.md   | execution evolution  |
| gotchas.md   | unresolved friction  |
| judge.md     | verification traces  |
| deliverables | explicit outputs     |

于是：

```text id="m1v8wr"
Data Plane 的边界会变得非常模糊。
```

---

# 三、最危险的问题：data_plane.md 很容易变成“垃圾桶”

这是最大风险。

因为你会开始往里面放：

```text id="r5q2pk"
test results
file refs
logs
runtime outputs
temporary evidence
metrics
execution artifacts
```

然后：

```text id="n9v4wx"
session.md 也有执行记录
judge.md 也有验证记录
deliverables 也有产出
```

最终：

```text id="k3m7pq"
边界重叠。
```

---

# 四、你现在其实不需要“Data Plane”

你真正需要的是：

> **Evidence References。**

这是两个完全不同的东西。

---

# 五、Judge 真正需要的不是“数据平面”

Judge 真正需要的是：

```text id="u8q1vx"
evidence mapping
```

例如：

```yaml id="m4v7pk"
requirement: oauth login works

evidence:
  - tests/oauth_login.test.ts
  - screenshot: artifacts/login_success.png
  - log: logs/oauth.log
```

这已经够了。

不需要：

```text id="x2q5wr"
data_plane.md
```

再包一层。

---

# 六、否则你会开始出现“三层事实系统”

这是危险的。

你会得到：

---

## session.md

记录：

```text id="d7v2pk"
做了什么
```

---

## judge.md

记录：

```text id="q1m8wr"
验证了什么
```

---

## data_plane.md

记录：

```text id="u5q4vx"
有哪些数据
```

---

然后：

```text id="h8v1pk"
谁才是真正 evidence source？
```

开始混乱。

---

# 七、你当前体系最强的地方是“少抽象层”

这是关键。

你现在其实已经非常漂亮：

```text id="m2q7wr"
Task
Session
Gotcha
Judge
Deliverable
```

每个都很清晰。

而：

```text id="u9v4pk"
Data Plane
```

开始变成：

```text id="r4q1vx"
meta abstraction。
```

---

# 八、我认为你之前提到 Data Plane，是因为 Judge Tier 3

这个很关键。

因为我们之前讨论：

```text id="w7m2pk"
Picture Claims
Evidence Mapping
Residual Gaps
```

于是自然会想到：

```text id="q3v8wr"
需要 Data Plane。
```

但后来你的协议发生了一个巨大变化：

---

# 你收紧了 Task Boundary

现在：

```text id="n6q1vx"
Task Atomicity
Black Box Execution
Artifact Dependency
```

成立了。

这意味着：

Judge 其实不再需要：

```text id="x5m4pk"
全局数据平面。
```

它只需要：

```text id="u1q7wr"
当前 Task 的局部 evidence。
```

---

# 九、因此更合理的是：

---

## 在 judge.md 中直接引用 evidence

例如：

```yaml id="m8v2pk"
picture_claim:
  claim: user can login with google

evidence:
  - type: test
    ref: tests/oauth_google.test.ts

  - type: screenshot
    ref: artifacts/google_login_success.png

judge_result:
  status: PASS
```

---

# 十、这已经够形成“局部 Data Plane”

注意：

你其实已经有：

```text id="v2q5wr"
implicit data plane。
```

只是：

```text id="r9m1pk"
不需要单独文件化。
```

这是成熟设计。

---

# 十一、什么时候才需要真正的 Data Plane？

只有未来：

---

## 1. 分布式 Runtime

例如：

```text id="u4v7pk"
remote agents
distributed workers
shared artifact store
```

---

## 2. 独立 Evidence Indexing

例如：

```text id="q8m2wr"
cross-task evidence retrieval
global semantic evidence graph
```

---

## 3. 自动化 Judge Pipeline

例如：

```text id="h1v5pk"
Judge 自动消费统一 evidence bus
```

---

这已经是：

```text id="n7q4vx"
v0.3+
```

了。

不是 v0.1-alpha。

---

# 十二、你现在真正需要加强的不是 Data Plane

而是：

---

# Evidence Contract

例如：

```yaml id="m3v8pk"
evidence:
  type:
  ref:
  generated_by:
  verified_at:
```

---

# Deliverable Contract

例如：

```yaml id="u9q1wr"
deliverables:
  - type: api_schema
    ref: artifacts/openapi.yaml
```

---

# Judge Evidence Mapping

例如：

```yaml id="r5m2pk"
picture_claim:
evidence:
residual_gap:
```

---

# 十三、这是比 data_plane.md 更高级的方向

因为：

你避免了：

```text id="k7v4wr"
再引入一个“万能层”。
```

而是：

```text id="d1q8pk"
让 evidence 自然附着在语义上下文中。
```

这非常重要。

---

# 十四、我现在建议的最终结论

## v0.1-alpha

### 不建议：

```text id="w6m2vx"
data_plane.md
```

---

### 推荐：

在：

```text id="q4v7pk"
judge.md
task.md
session.md
```

中：

```text id="u8q1wr"
直接引用 evidence。
```

---

# 十五、真正成熟的结构应该是：

| 层             | 内容                              |
| ------------- | ------------------------------- |
| task.md       | canonical state                 |
| session.md    | evolution                       |
| gotchas.md    | unresolved friction             |
| judge.md      | verification + evidence mapping |
| deliverables  | outputs                         |
| evidence refs | factual grounding               |

而不是：

```text id="h3m5pk"
再单独做 data_plane.md。
```

---

# 十六、最终一句话

我现在认为：

> **Data Plane 应该是协议中的“隐式语义层”，而不是 v0.1 的显式文件。**

否则：

```text id="q9v2wr"
协议会开始从“极简认知 runtime”
滑向
“过度抽象的 orchestration framework”。
```

而你现在最强的地方，恰恰是：

```text id="m1q7pk"
少而稳定的协议核心。
```

我认真看了你这个 `session.md`，我认为：

> 你现在这个方向其实已经非常接近“正确形态”了。

而且有一个很重要的变化：

> 你已经不是在做独立的 `data_plane.md`，
> 而是在做：

```text id="x7m2pk"
session-scoped evidence snapshot
```

这比独立 Data Plane 文件更成熟。

---

# 一、我认为你现在的方向是对的

尤其这一点：

```yaml id="n4q8wr"
data_plane:
  commit_id:
  active_refs:
```

这是非常合理的。

因为它本质上不是：

```text id="u1v5pk"
全局数据平面
```

而是：

```text id="m8q2vx"
当前 Turn 的 evidence context。
```

这是关键区别。

---

# 二、你实际上做对了什么？

你避免了：

```text id="h3v7pk"
global mutable data plane
```

而选择：

```text id="r6m1wr"
append-only local snapshot
```

这非常符合你的协议哲学：

```text id="d9q4pk"
Task-local
Turn-local
Append-only
Faithful projection
```

这是很一致的。

---

# 三、但我认为还有几个关键调整

现在最重要的问题是：

> 你当前的 `data_plane` 仍然偏“文件引用层”。

而 Judge 真正需要的是：

```text id="u5m8vx"
Evidence Semantics
```

也就是：

```text id="k2q7wr"
这些 ref 为什么存在？
它们证明了什么？
```

否则：

```yaml id="j8v1pk"
active_refs:
  - src/auth/google.ts
```

其实信息量很低。

---

# 四、我认为你应该把 data_plane 改名

这是我第一个建议。

因为：

```text id="n7q4vx"
data_plane
```

这个词太“大”。

它天然会让协议滑向：

```text id="u3m8pk"
global runtime abstraction
```

而你实际上做的是：

```text id="w1q5wr"
turn evidence snapshot。
```

---

# 五、我建议改成：

## 推荐名称

### 方案1（我最推荐）

```yaml id="m9v2pk"
evidence:
```

---

### 方案2

```yaml id="x4q7wr"
artifacts:
```

---

### 方案3

```yaml id="r8m1vx"
workspace_snapshot:
```

---

我最推荐：

```text id="u2q9pk"
evidence
```

因为它最符合 Judge 语义。

---

# 六、你现在缺少的不是更多字段

而是：

> “Evidence 与 Action 的语义绑定”。

这是关键。

---

# 七、你现在的结构：

```yaml id="v5q1wr"
Action Summary
+
data_plane.active_refs
```

还是：

```text id="k8v4pk"
松散并列关系。
```

Judge 很难知道：

```text id="r3q7vx"
哪个 ref 对应哪个行为。
```

---

# 八、我建议升级成：

```yaml id="m1v8pk"
evidence:
  - type: code
    ref: src/auth/google_router.ts
    purpose: implement_google_oauth

  - type: test
    ref: tests/google_oauth.test.ts
    purpose: verify_google_login
```

这里：

```text id="h7q2wr"
purpose
```

非常关键。

因为：

> 它开始形成“Picture Claim → Evidence”映射。

---

# 九、这是比 data_plane 更高级的东西

因为：

你现在开始得到：

```text id="u9m4pk"
semantic evidence graph
```

而不是：

```text id="q2v7wr"
file list。
```

---

# 十、commit_id 是非常好的

这个我认为应该保留。

因为：

```text id="m5q1vx"
commit_id
```

实际上承担：

```text id="n8v4pk"
workspace immutability anchor
```

这是非常强的设计。

我甚至认为：

> 这是你现在 session.md 里最有价值的字段之一。

---

# 十一、但 active_refs 需要升级

当前：

```yaml id="d4q7wr"
active_refs:
```

太弱。

我建议升级成：

---

## 推荐结构

```yaml id="u1m8pk"
evidence:
  - type: code
    ref: src/auth/google_router.ts
    purpose: implement_google_oauth

  - type: test
    ref: tests/oauth_google.test.ts
    purpose: verify_google_login

  - type: screenshot
    ref: artifacts/google_login_success.png
    purpose: verify_ui_flow
```

---

# 十二、你还缺一个东西：Outcome

这是我认为你现在真正缺少的。

现在：

```text id="v7q2wr"
Action Summary
```

偏：

```text id="m3v8pk"
行为描述。
```

但缺：

```text id="u5q1vx"
结果状态。
```

---

# 十三、建议增加：

```yaml id="r9m4pk"
outcome:
  status: success|partial|failed
  note:
```

例如：

```yaml id="j2q7wr"
outcome:
  status: partial
  note: OAuth route implemented but token refresh still failing
```

这会极大提升：

```text id="k6v1pk"
Judge 可解释性。
```

---

# 十四、所以我现在建议你：

---

# 保留：

## append-only snapshot

正确。

---

## commit_id

非常正确。

---

## turn-local evidence

正确。

---

# 修改：

## data_plane → evidence

避免过度抽象。

---

## active_refs → structured evidence

增强语义。

---

# 增加：

## outcome

增强执行结果表达。

---

# 十五、我现在认为最成熟的 session 结构应该是：

```yaml id="m8q2wr"
turn:
timestamp:
status:

action_summary:

outcome:
  status:
  note:

evidence:
  - type:
    ref:
    purpose:

workspace:
  commit_id:
```

---

# 十六、然后删掉这些

我建议删除：

```yaml id="x5v7pk"
relationships:
  requires: ["data_plane.md"]
```

因为：

> 你已经不需要独立 Data Plane 文件了。

---

同时：

```text id="u4q1wr"
Data Plane 模板结构见 data_plane.md
```

这句也应该删。

否则：

```text id="n7m8pk"
协议仍然残留“全局 Data Plane”幻觉。
```

---

# 十七、一个非常关键的问题

你现在其实正在形成：

```text id="r2q5vx"
event-sourced cognitive runtime
```

所以：

Session 的本质应该是：

```text id="m1v9pk"
事实事件 + 证据快照
```

而不是：

```text id="k4q7wr"
运行时镜像。
```

这是重要区别。

---

# 十八、最终结论

我认为：

## 你当前把 data_plane 放进 session

这个方向是对的。

而且：

> 比独立 data_plane.md 更成熟。

---

但我建议：

| 当前            | 建议                  |
| ------------- | ------------------- |
| data_plane    | evidence            |
| active_refs   | structured evidence |
| file list     | semantic evidence   |
| 无 outcome     | 增加 outcome          |
| data_plane.md | 删除                  |

---

因为你现在真正需要的不是：

```text id="u8m2pk"
Data Plane
```

而是：

```text id="w3q7vx"
Evidence Semantics
+
Workspace Snapshot
+
Outcome Trace
```

这是更稳定、更轻、更符合你协议哲学的方向。
