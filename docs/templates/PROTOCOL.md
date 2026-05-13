# mem0ress Protocol

> 本文件是协议实现者的快速参考手册。
> 所有语义定义均以 spec.md 为准。

---

## 参与方速查

| 参与方 | 职责 |
|--------|------|
| 主 Agent（Main Agent） | 执行任务：创建任务、拆解 Todo、推进执行、写入 session 快照、触发 Judge、读取 Judge 结论、自主决策 |
| Judge Agent（Judge Agent） | 检验任务：被动等待触发、执行四层检验（Tier 0/1/2/3）、写入 judge.md |
| 宿主框架（Host Framework） | 基础设施：管理文件系统布局、隔离上下文、注入 task_id、处理 VERIFYING 超时（默认 180s） |

## 文件读写权限速查

| 文件 | 主 Agent | Judge Agent |
|------|---------|------------|
| task.md | 读 + 写（覆盖写） | 只读 |
| session.md | 追加写 | 只读 |
| gotchas.md | 追加写 | 只读 |
| judge.md | 只读 | 追加写 |

## 执行轮次速查

```
轮次开始
  1. 认知构建 → 2. 执行（可选追加 gotchas.md）→ 3. Session 写入 → 4. 检验触发（条件）→ 5. 决策
轮次结束
```

检验触发条件（满足其一即触发）：所有 Todo 已完成；主 Agent 主动请求；利益相关者显式请求。

## Tier 速查

| Tier | 检查内容 | 失败行为 |
|------|---------|---------|
| Tier 0 | Constraints 违反记录 | 立即 FAIL |
| Tier 1 | Todo 完成 + 子任务关闭 | 立即 FAIL |
| Tier 2 | Requirements 自动化验证 | 立即 FAIL |
| Tier 3（条件） | Picture 语义对齐 | PASS / FAIL / UNCERTAIN |

## Judge Agent 调用约定

- 上下文仅含：`task_id` + 系统提示（不含主 Agent 执行历史）
- 从文件系统读取依据，不接收运行时信息
- 只追加写 judge.md，不修改其他文件

## VERIFYING 超时

- 默认：180 秒
- 超时处理：强制结束 Judge、写入 `Verdict: TIMEOUT`、恢复为 IN_PROGRESS

## 主 Agent 决策速查

| Judge 结论 | 可选决策 |
|-----------|---------|
| PASSED | complete_task / 继续执行 |
| FAILED | 修正重试 / 拆解子任务 / abandon_task |
| TIMEOUT | 重试 / abandon_task |

## 协议边界速查（不支持的场景）

- 并发子任务写入同一 session.md
- 多 Agent 并行执行同一任务
- 跨 workspace 任务依赖
- 事务性多步写入（无恢复协议）

遇到上述场景时，让度给人。
