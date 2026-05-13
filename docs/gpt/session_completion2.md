这会带来一个非常大的变化：

> **completion_summary 从“父任务认知输入”降级为“Task closure artifact”。**

也就是说：

你现在新的边界模型里：

```text id="k2v8qp"
父任务不再消费子任务内部认知结果
```

只消费：

```text id="r5m1wx"
child lifecycle state
+
optional deliverables
```

那么：

```text id="j8q4vn"
completion_summary
```

就不再承担：

```text id="n3v7pk"
跨 Task 认知传递
```

的职责了。

这是根本变化。

---

# 一、之前为什么需要 completion_summary？

之前的模型里：

父任务：

```text id="f1q8wr"
需要理解子任务完成了什么
```

所以：

```text id="x4m2pk"
completion_summary
```

承担：

```text id="v7q1nx"
认知压缩输出
```

作用。

本质上：

```text id="u2m8vk"
Child internal cognition
→
compressed semantic export
→
Parent cognition input
```

---

# 二、但你现在已经否定了这个模型

你现在实际上在定义：

```text id="m9q4wr"
Task 内部认知不允许跨边界传播。
```

这是非常重要的协议收紧。

因此：

```text id="h3v7pk"
Parent 不应该依赖 Child 内部 reasoning。
```

于是：

```text id="d8q2vx"
completion_summary 的协议地位会下降。
```

---

# 三、它现在更像什么？

现在它更像：

```text id="g5m1pk"
closure metadata
```

或者：

```text id="q7v4wr"
archive note
```

而不是：

```text id="n1q8vx"
runtime cognition channel
```

---

# 四、所以会发生三个变化

---

# 变化1：completion_summary 不再是协议核心

以前：

```text id="m4q7pk"
Parent 必须读取 completion_summary
```

现在：

```text id="u9v2wr"
Parent 不需要。
```

因此：

> completion_summary 不再是 runtime boundary 的关键部分。

这是最大的变化。

---

# 变化2：completion_summary 可以彻底 optional

以前我认为：

```text id="v2q8pk"
completion_summary 必须存在。
```

现在我认为：

> 可以 optional。

因为：

协议已经完整。

Parent 只需要：

```yaml id="x5m1wr"
child.status == COMPLETED
```

即可。

---

# 变化3：completion_summary 更偏向“人类可读”

以前：

```text id="n8v4pk"
completion_summary
```

承担：

```text id="f3q7wr"
machine/runtime semantic bridge
```

现在：

它更像：

```text id="m1v8qx"
human-oriented closure note
```

例如：

```markdown id="u4q2pk"
完成了什么
产生了哪些 artifact
有哪些残余风险
有哪些注意事项
```

但：

```text id="r7v5wr"
runtime 本身不依赖它。
```

---

# 五、你现在真正的协议核心变成了什么？

现在真正重要的是：

---

## 1. lifecycle state

```text id="q2m7pk"
CREATED
IN_PROGRESS
VERIFYING
COMPLETED
ABANDONED
```

---

## 2. dependency semantics

```yaml id="v9q1wr"
depends_on:
  child_task: xxx
  required_state: COMPLETED
```

---

## 3. deliverables

这是你现在真正需要强化的。

例如：

```yaml id="n5m8pk"
deliverables:
  - type: api
    ref: generated/openapi.yaml
```

因为：

Parent 真正消费的是：

```text id="u3q7wr"
artifact
```

而不是：

```text id="h8v2pk"
child reasoning summary
```

---

# 六、所以 completion_summary 会被“artifact metadata”替代一部分

这是很关键的演化。

你现在协议已经开始从：

```text id="r1q8vx"
LLM memory passing
```

转向：

```text id="d4m7pk"
artifact-oriented task runtime
```

这很成熟。

---

# 七、现在最合理的设计

我会这样设计：

---

## 必需

### task.md

```yaml id="w2q9pk"
status:
deliverables:
dependencies:
```

---

## 可选

### completion_summary

用于：

```text id="k6v1wr"
human-readable closure explanation
```

而不是：

```text id="m9q4pk"
runtime dependency channel
```

---

# 八、因此 completion_summary.md 彻底不需要了

这是我现在很明确的结论。

因为：

它既不是：

```text id="j7v2qx"
canonical task state
```

也不是：

```text id="n4q8wr"
runtime dependency channel
```

它只是：

```text id="u1m5pk"
optional closure note。
```

所以：

```text id="x8q2vr"
没必要单独文件化。
```

---

# 九、你现在真正应该加强的是 Deliverables

这是重点。

因为你现在的模型已经是：

```text id="m5v7pk"
Task Atomicity
+
Black Box Execution
+
Artifact Dependency
```

那么：

```text id="d2q9wr"
deliverables
```

就会成为：

> 真正的跨 Task 接口。

---

# 十、这会让协议非常现代

因为它开始接近：

```text id="r8m1pk"
build systems
actor systems
distributed runtimes
```

而不是：

```text id="h4q7vx"
共享 reasoning workflow。
```

这是高级很多的方向。

---

# 十一、我现在建议的最终定义

---

## Completion Summary

```text id="w7v2pk"
Completion Summary 是 Task 在关闭时生成的人类可读 closure note。

它不参与跨 Task 依赖，不构成 runtime 状态平面的一部分，也不作为 Parent Task 的认知输入。

跨 Task 协作只能依赖：
1. 生命周期状态；
2. 显式 deliverables；
3. 明确声明的 dependency contract。
```

---

# 十二、最终结论

你这次调整之后：

## completion_summary 的变化是：

| 之前                       | 现在                     |
| ------------------------ | ---------------------- |
| runtime cognition bridge | optional closure note  |
| Parent cognition input   | human-readable archive |
| protocol core            | optional metadata      |
| required                 | optional               |
| machine dependency       | human explanation      |

---

而真正升级为协议核心的是：

```text id="n2q7wr"
Task Atomicity
+
Lifecycle Dependency
+
Deliverable Contract
```

这是更成熟、更稳定、更可扩展的方向。
