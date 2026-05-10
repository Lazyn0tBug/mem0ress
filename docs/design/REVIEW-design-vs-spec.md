# design.md 评审意见

## 总体评价

design.md 的方向正确，抓住了几个核心要素（拦截器模式、Tier 0-3、文件树结构），但**遗漏了大量 spec.md 的关键设计决策**。

---

## 一、design.md 正确反映的内容 ✓

1. **拦截器模式**：CognitiveContext 作为唯一入口，before turn 挂载状态平面，after turn 快照——符合 spec 第 8.1 节"生命周期挂钩"
2. **Tier 0-3 四层验证**：harness/runner.py + judge.py 的分离架构，符合 spec 第 7.2 节
3. **文件树结构**：`.mem0ress/tasks/{id}/{index.md, session.md, data-plane/, gotchas/}` 与 spec 第 6 章一致
4. **工具接口封装**：`update_todo`、`create_task`、`complete_task` 等，符合 spec 附录 A 的动作表
5. **Data Plane + Status Plane 分离**：plane.py 和 fs.py 的职责划分符合双平面正交原则

---

## 二、遗漏的关键设计决策

### 1. 缺少"认知三要素"的地位说明

spec 第 2.2 节专门论证了 PRC 框架的认知科学来源（目标导向行为理论 + 约束满足网络），第 5.1 节给出了完整的定义者/参与者/填写顺序规则。

design.md 只在 `core/schema.py` 的注释里一笔带过"PRC 三要素"，但没有说明：
- 为什么必须先定义 Requirements，再定义 Constraints，最后推导出 Picture
- 冲突检测机制（Req ∩ Cst 矛盾 → 标记「不可行」）
- Picture 的质量判断标准（"是否可感知"而非"是否可测试"）

### 2. 状态平面的"纯展示"约束丢失

spec 第 7.3 节明确：状态平面**纯展示，不做诊断**，只呈现任务树/TODO 进度/状态/Gotchas/Session 指针，**不展开 Picture/Requirements/Constraints**。

design.md 的 `gateway/plane.py` 只说了"递归目录树生成带层级缩进的 Status Plane 文本"，没有说明"纯展示不做诊断"这条核心约束。

### 3. 三个工程准则完全缺失

spec 第 4 章定义了三条工程准则：
- **SSOT + 绝对覆写**：新认知直接覆写旧认知，运行时工作区内不合并
- **系统级卸责**：不接管大模型沙箱、并发控制等底层复杂性
- **反黑盒 + 绝对可观测性**：零中介，目录树+纯文本，无私有格式

design.md 只在 substrate/fs.py 提到"Hash 乐观锁"，但对 SSOT 和反黑盒原则没有任何体现。

### 4. Tier 0 的前置处理器定位模糊

~~spec 明确 Tier 0 是**独立于 Harness Engine 之外的前置处理器**，与 Tier 1/2/3 性质不同（Tier 0 可能涉及数据修复，Tier 1/2/3 纯检验）。~~

**已修正（spec v3.6+）：** spec 现已明确 Tier 0 与 Tier 1/2/3 均为纯检验——只读数据，报告结果，不修改任何状态。Tier 0 与其他 Tier 的区别仅在于触发方式（每轮次自动触发 vs 主 Agent 按需调用），而非性质。

design.md 在 3.2 节和 3.3 节两处提到 Tier 0，位置和定性都不清晰：
```
# 3.2 节：
Tier 0: 检查 Constraints 是否被违背。违背即阻断，记录 Gotcha

# 3.3 节（运行逻辑）：
Tier 0 前置处理（独立于 Harness 之外）
```

这两处描述互相矛盾——3.2 说"阻断"，3.3 说"前置处理"。spec 的实际逻辑是：**Tier 0 自动触发（不归 Agent 决策），Tier 1/2/3 由 Agent 按需调用**。

### 5. Session 快照的触发规则缺失

spec 第 7.3 节明确：
- 系统每轮次结束时**自动触发**，无需 Agent 调用
- 快照内容是 code_progress/docs_progress/todos/status，**不含 Picture/Requirements/Constraints**（这些从 Manifest 获取）

design.md 3.1 节的 `__exit__` 里写了"自动会话捕捉"，但没有说明触发时机和内容边界。

### 6. 四个洞察的推导链没有体现

spec 第 2 章给出了完整的认知科学基础推导链。design.md 直接跳到工程实现，没有建立从洞察到架构的映射。这不是说 design.md 要重写第二章，而是说每个模块的设计选择需要能追溯到对应的洞察。

### 7. 乐观锁的冲突处理流程缺失

spec 8.2 节说：执行写操作时比对文件哈希，若遭外部修改，抛出 409 Conflict，**强制 Agent 重新进行认知构建后再决策**。

design.md 3.3 节只说了"抛出 409 Conflict"，但没说后续流程。

### 8. 决策权归属缺失

spec 第 7.4 节明确：Agent 是所有决策的起点与终点，`complete_task()` 的调用权属于决策权，可由 Agent 自主行使或按权限分级让度给人。

design.md 没有说明决策权归属，导致工具接口缺少权限校验逻辑的设计依据。

---

## 三、建议

### 建议 1：在 design.md 开头加"设计决策溯源"一节

建立 spec → design 的映射：

```
4 洞察 → gateway 层设计选择（为什么是拦截器而非独立服务）
PRC 框架 → core/schema.py 的类型强制
双平面正交 → gateway/plane.py（只读展示）vs gateway/actions.py（写入口）
四层检验 → harness/ 模块职责边界
```

### 建议 2：明确 Tier 0 的触发模式

spec 的 Tier 0 是**自动前置处理**（不等 Agent 调用），Tier 1/2/3 是**按需触发**。design.md 需要在 3.2 节说清楚这个分层。

### 建议 3：在 gateway/actions.py 或 intercept.py 加上决策权说明

"Agent 是决策终点"是一条架构约束，需要落在工具接口的语义层面。

### 建议 4：补充冲突处理的 Agent 行为协议

乐观锁冲突后 Agent 应该重新 get_status_plane 再决策，这条协议对多 Agent 协作时的正确性很重要。
