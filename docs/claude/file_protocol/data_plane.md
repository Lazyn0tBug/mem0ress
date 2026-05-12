---
task_id: "{task_id}"
type: data_plane
---

# Data Plane — {task_id}

> data_plane 不是独立文件，而是嵌入在 session.md 每个 Turn 块中的结构化字段。
> 本文件定义该字段的格式规范，供实现方参考。
>
> **设计意图：** 数据平面记录"当前操作的是哪个版本的代码"。
> 它是状态平面的补充——状态平面回答"做到哪了"，数据平面回答"在什么版本上做的"。
> 数据平面可 revert，认知状态不可 revert，这是两者的根本差异。

---

## 单仓库格式

```markdown
### Data Plane
- **Commit ID:** `a1b2c3d4e5f6...`
- **Active Refs:**
  - `src/auth/google_provider.ts`
  - `src/auth/session.ts`
  - `tests/e2e/test_oauth.py`
```

## 多仓库格式

```markdown
### Data Plane
- **Repos:**
  - `api-service` → `a1b2c3d4` — 实现了 OAuth callback 端点
  - `frontend` → `b2c3d4e5` — 更新了登录页 UI
  - `infra` → `c3d4e5f6` — 添加了 HTTPS 证书配置
- **Active Refs:**
  - `api-service:src/auth/callback.py`
  - `frontend:src/pages/login.tsx`
```

---

## 字段定义

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| `Commit ID` | string | 单仓库时必填 | 完整 git commit hash（至少 8 位） |
| `Repos` | list | 多仓库时必填 | 格式：`{repo_name} → {commit_hash} — {本轮变更说明}` |
| `Active Refs` | list | ✅ | 本轮实际操作的文件路径，格式 `{repo:}path/to/file` |

---

## 约束

**Active Refs 只记录本轮实际操作的文件**，不记录所有相关文件。
"相关"和"操作"的边界：读取但未修改的文件不计入 Active Refs。

**Commit ID 必须是真实存在的 commit**，不允许记录"即将提交"或"本地未推送"的状态。
Judge Agent 在 Tier 3 会通过 Data Plane 定位实际产出，commit 必须可达。

**无 git 场景：** 若项目不使用 git，Commit ID 字段替换为任意可唯一标识版本的标识符
（构建号、文件 hash、时间戳均可），但必须填写，不允许省略。

---

## 与 session.md 的关系

data_plane 是 session.md 每个 Turn 块的内嵌字段，不单独存在为文件。
在 session.md 中的位置固定在 `Docs Progress` 之后，`Constraint Violations` 之前。

```
## Turn 1.1
...
### Docs Progress
...
### Data Plane          ← 固定位置
...
### Constraint Violations
...
---
```
