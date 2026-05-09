# Data Plane

记录任务的代码产出快照，供回溯和检验使用。

---

## 结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `commit_id` | string | 当前 HEAD 的 Git commit hash |
| `active_refs` | list[string] | 本轮涉及的文件路径列表（相对路径） |
| `note` | string | 可选：本轮的简要说明 |

## 示例

```yaml
commit_id: "a1b2c3d"
active_refs:
  - "src/auth/google_router.ts"
  - "src/auth/github_router.ts"
  - "tests/e2e/test_oauth_providers.py"
note: "完成 Google OAuth 路由搭建"
```

---

## 用途

1. **Session 快照**：每轮次结束时记录当时的 commit ID，Judge Agent 检验时按 commit 定位代码
2. **回溯定位**：给定某一轮的 Session 快照，可通过 commit_id 还原当时的代码状态
3. **审计记录**：不是任务清单，是**代码层面的审计轨迹**

---

## 与 Task 的关系

- Data Plane 由 Session 写入，不属于 Task 的 frontmatter 或 body
- Task 的 frontmatter `status` 反映任务生命周期，不记录代码快照
- 两者通过 Turn 编号关联：Session Turn 引用对应的 Task + Data Plane 快照

---

## 与 Judge 的关系

Judge Agent 执行 Tier 1/2 检验时：
- 读取 Session 中记录的 `commit_id`
- 在该 commit 下运行测试或静态检查
- 将结果写入 `report.md`

不依赖 Data Plane 的实时状态，只读快照。
