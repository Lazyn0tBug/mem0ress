# mem0ress Protocol — 完整填写示例

> 以下是一个真实任务（OAuth 单点登录）在协议运行中产生的四个文件的完整内容。
> 任务已执行两个主轮次，经过一次 Judge 检验（失败），修正后再次检验（通过）。
>
> 这不是模板，是实例。所有占位符均已替换为真实内容。

---

## 任务背景

**任务：** 为企业内部工作台实现 OAuth 单点登录
**task_id：** `sso_login`
**执行过程：**
- Turn 1.1：搭建 OAuth 基础框架
- Turn 1.2：实现 Google / GitHub provider
- Turn 2.1：Judge 检验（FAILED — R-1 响应时间不达标）
- Turn 1.3（子轮次修正）：优化响应时间
- Turn 2.2：Judge 检验（PASSED）

---

## task.md

```markdown
```
task_id: sso_login
status: COMPLETED
created_at: 2025-01-15T08:00:00Z
```

# Task: 企业工作台 OAuth 单点登录

## 🎯 Picture（图景）

员工打开工作台时，无需输入任何密码，点击「使用企业账号登录」后
通过 Google 或 GitHub 账号完成授权，直接进入工作台主界面。
整个过程感知不到"登录"这个动作的存在，只感知到"进入了"。

---

## 📐 Requirements（需求）

- [x] R-1: 认证接口端到端响应时间 p99 < 300ms（测试命令：`pytest tests/perf/test_auth_latency.py`）
- [x] R-2: 支持 Google OAuth 2.0 和 GitHub OAuth 两种提供商（测试命令：`pytest tests/e2e/test_oauth_providers.py`）
- [x] R-3: 登录 session 有效期 7 天，过期后自动跳转登录页（测试命令：`pytest tests/e2e/test_session_expiry.py`）
- [x] R-4: 登录失败时展示错误原因，不暴露内部错误信息（测试命令：`pytest tests/e2e/test_auth_error_handling.py`）

---

## ⛔ Constraints（约束）

- ⛔ C-1: 不允许在任何日志（console、文件、监控系统）中输出用户的 Access Token 或 Refresh Token
- ⛔ C-2: 不允许在数据库中以明文存储任何用户凭证
- ⛔ C-3: 所有 OAuth callback URL 必须通过 HTTPS，不允许 HTTP 回调

---

## ✅ Todos（机械步）

- [x] T-1: 搭建 OAuth 基础框架（Provider 抽象接口、HTTPS 中间件、callback 路由）
- [x] T-2: 实现 Google OAuth 2.0 provider（授权流程、token exchange、用户信息获取）
- [x] T-3: 实现 GitHub OAuth provider（授权流程、token exchange、用户信息获取）
- [x] T-4: 实现 session 管理（JWT 签发、7 天过期、自动跳转）
- [x] T-5: 实现登录失败错误处理（友好错误信息、错误码映射）
- [x] T-6: 性能优化（响应时间 p99 < 300ms，针对 Judge Turn 2.1 的 FAILED 修正）
```

---

## session.md

```markdown
---
task_id: sso_login
type: session
---

# Session History — sso_login

---

## Turn 1.1
**Timestamp:** 2025-01-15T09:15:00Z
**Status:** IN_PROGRESS

**Action Summary:**
搭建了 OAuth 基础框架，定义了 Provider 抽象接口，配置了 HTTPS 强制中间件，
建立了 callback 路由结构。

### Todos
- [x] T-1: 搭建 OAuth 基础框架（Provider 抽象接口、HTTPS 中间件、callback 路由）
- [ ] T-2: 实现 Google OAuth 2.0 provider
- [ ] T-3: 实现 GitHub OAuth provider
- [ ] T-4: 实现 session 管理
- [ ] T-5: 实现登录失败错误处理
- [ ] T-6: 性能优化

### Code Progress
新增 `src/auth/base_provider.py`（抽象接口）、`src/auth/middleware.py`（HTTPS 强制）、
`src/auth/callback.py`（路由结构）。Provider 具体实现暂为空实现，待下轮填充。

### Docs Progress
—

### Data Plane
- **Commit ID:** `a1b2c3d4e5f67890`
- **Active Refs:**
  - `src/auth/base_provider.py`
  - `src/auth/middleware.py`
  - `src/auth/callback.py`

### Constraint Violations
—

---

## Turn 1.2
**Timestamp:** 2025-01-15T11:42:00Z
**Status:** IN_PROGRESS

**Action Summary:**
实现了 Google 和 GitHub 两个 OAuth provider，完成了 session 管理和错误处理。
所有 Todo 已完成（T-6 暂标为完成，待 Judge 检验后确认性能达标）。

### Todos
- [x] T-1: 搭建 OAuth 基础框架
- [x] T-2: 实现 Google OAuth 2.0 provider
- [x] T-3: 实现 GitHub OAuth provider
- [x] T-4: 实现 session 管理
- [x] T-5: 实现登录失败错误处理
- [x] T-6: 性能优化（初版，未做专项优化）

### Code Progress
新增 `src/auth/google_provider.py`、`src/auth/github_provider.py`。
`src/auth/session.py` 实现了 JWT 签发（7 天过期）和自动跳转。
`src/auth/error_handler.py` 实现了错误码到友好信息的映射。

### Docs Progress
—

### Data Plane
- **Commit ID:** `b2c3d4e5f6789012`
- **Active Refs:**
  - `src/auth/google_provider.py`
  - `src/auth/github_provider.py`
  - `src/auth/session.py`
  - `src/auth/error_handler.py`

### Constraint Violations
—

---

## Turn 1.3
**Timestamp:** 2025-01-15T14:30:00Z
**Status:** IN_PROGRESS

**Action Summary:**
针对 Judge Turn 2.1 的 FAILED 结论（R-1 响应时间不达标，p99=487ms）进行专项优化：
引入了 provider 连接池、增加了 token 缓存层。

### Todos
- [x] T-1: 搭建 OAuth 基础框架
- [x] T-2: 实现 Google OAuth 2.0 provider
- [x] T-3: 实现 GitHub OAuth provider
- [x] T-4: 实现 session 管理
- [x] T-5: 实现登录失败错误处理
- [x] T-6: 性能优化（连接池 + token 缓存，p99 实测 187ms）

### Code Progress
新增 `src/auth/connection_pool.py`、`src/auth/token_cache.py`。
修改 `src/auth/base_provider.py` 接入连接池。
本地压测 p99 = 187ms，达标。

### Docs Progress
—

### Data Plane
- **Commit ID:** `c3d4e5f678901234`
- **Active Refs:**
  - `src/auth/connection_pool.py`
  - `src/auth/token_cache.py`
  - `src/auth/base_provider.py`

### Constraint Violations
—

---
```

---

## judge.md

```markdown
---
task_id: sso_login
type: judge
---

# Judge Verification — sso_login

---

## Turn 2.1
**Timestamp:** 2025-01-15T13:05:00Z
**Verdict:** FAILED

---

### Tier 0 — Constraints 约束检查

| Constraint | 验证手段 | 结论 |
|-----------|---------|------|
| C-1: 不允许在日志中输出 Token | 正则扫描 `logs/` 目录，匹配 `access_token\|refresh_token` | ✅ PASS |
| C-2: 不允许明文存储凭证 | 检查 `migrations/` 目录，扫描 `password\|token` 字段类型 | ✅ PASS |
| C-3: callback URL 必须 HTTPS | 检查 `src/auth/callback.py` 中的 URL 配置 | ✅ PASS |

**Findings:** —

---

### Tier 1 — Todo & Subtask 完成检查

- [x] 所有 `task.md` 中的 Todos 已标记 `[x]`
- [x] 所有直接子任务已处于终态（无子任务）

**未完成项：** —

---

### Tier 2 — Requirements 验收检查

| Requirement | 验证命令 | 输出摘要 | 结论 |
|------------|---------|---------|------|
| R-1: 认证接口 p99 < 300ms | `pytest tests/perf/test_auth_latency.py` | `FAILED: p99=487ms, threshold=300ms` | ❌ FAIL |
| R-2: 支持 Google + GitHub | 跳过（R-1 已 FAIL） | — | ⏭️ SKIPPED |
| R-3: session 7 天有效期 | 跳过（R-1 已 FAIL） | — | ⏭️ SKIPPED |
| R-4: 错误处理友好 | 跳过（R-1 已 FAIL） | — | ⏭️ SKIPPED |

**Findings:** R-1 未满足。测试命令输出 p99=487ms，超出阈值 300ms 的 62%。
快速失败原则，后续 Requirement 未执行检验。

---

### Tier 3 — 语义对齐检查

**Trigger Condition:** SKIPPED — Tier 2 FAILED，Tier 3 强制跳过。

---

**Overall Verdict:** FAILED
**Summary:** Tier 2 失败。R-1 性能未达标（p99=487ms，要求 < 300ms）。
Tier 0、Tier 1 均通过。主 Agent 需修正性能问题后重新触发检验。

---

## Turn 2.2
**Timestamp:** 2025-01-15T15:10:00Z
**Verdict:** PASSED

---

### Tier 0 — Constraints 约束检查

| Constraint | 验证手段 | 结论 |
|-----------|---------|------|
| C-1: 不允许在日志中输出 Token | 正则扫描 `logs/` 目录，含新增的 `connection_pool.py` 日志 | ✅ PASS |
| C-2: 不允许明文存储凭证 | 检查 migrations，token_cache 使用加密存储 | ✅ PASS |
| C-3: callback URL 必须 HTTPS | 检查 callback.py 配置，未变更 | ✅ PASS |

**Findings:** —

---

### Tier 1 — Todo & Subtask 完成检查

- [x] 所有 `task.md` 中的 Todos 已标记 `[x]`（含新增 T-6）
- [x] 所有直接子任务已处于终态（无子任务）

**未完成项：** —

---

### Tier 2 — Requirements 验收检查

| Requirement | 验证命令 | 输出摘要 | 结论 |
|------------|---------|---------|------|
| R-1: 认证接口 p99 < 300ms | `pytest tests/perf/test_auth_latency.py` | `PASSED: p99=187ms` | ✅ PASS |
| R-2: 支持 Google + GitHub | `pytest tests/e2e/test_oauth_providers.py` | `2 passed in 4.32s` | ✅ PASS |
| R-3: session 7 天有效期 | `pytest tests/e2e/test_session_expiry.py` | `1 passed in 0.91s` | ✅ PASS |
| R-4: 错误处理友好 | `pytest tests/e2e/test_auth_error_handling.py` | `3 passed in 2.17s` | ✅ PASS |

**Findings:** —

---

### Tier 3 — 语义对齐检查

**Trigger Condition:** 触发。Picture 包含"感知不到登录动作"这一主观体验描述，需语义对齐。

**Prompt 发送内容：**

```
【目标图景】
员工打开工作台时，无需输入任何密码，点击「使用企业账号登录」后
通过 Google 或 GitHub 账号完成授权，直接进入工作台主界面。
整个过程感知不到"登录"这个动作的存在，只感知到"进入了"。

【实际产出】
- OAuth 流程：用户点击登录按钮 → 跳转到 Google/GitHub 授权页 → 用户点击授权 
  → callback → 自动跳转工作台主界面，全程无密码输入框
- session 有效期 7 天，过期自动跳转，不弹 session 过期提示
- 错误场景：OAuth 授权失败时展示"登录遇到问题，请重试"，不暴露错误码
- 性能：p99=187ms，用户感知为"瞬间完成"

【检验指令】
请判断实际产出是否在语义和最终体验上达成了目标图景。
如果达成，返回 PASS。
如果未达成，返回 FAIL，并指出具体偏差：哪个维度不符合图景，为什么。
不要给出修复建议，只报告事实。
```

**Verdict:** PASS
用户全程无密码输入，OAuth 流程对用户透明，session 管理无感知，符合图景描述。

---

**Overall Verdict:** PASSED
**Summary:** 全部四个 Tier 均通过。主 Agent 可调用 `complete_task`。
```

---

## gotchas.md

```markdown
---
task_id: sso_login
type: gotchas
---

# Gotchas — sso_login

---

## Gotcha G-1 — Turn 2.1 Judge FAILED：性能未达标
**Timestamp:** 2025-01-15T13:10:00Z
**Turn:** 2.1

### 触发背景
执行 T-6（性能优化）时未做专项压测，以为 OAuth 外部请求不会成为瓶颈，直接标记为完成触发检验。

### 实际发生了什么
Judge Turn 2.1 运行 `pytest tests/perf/test_auth_latency.py`，结果 p99=487ms，
超出 R-1 阈值（300ms）62%。根因是每次认证都对 OAuth provider 建立新的 HTTP 连接，
连接握手耗时占总延迟约 58%。

### 如何处理
追加了 T-6 作为专项性能优化 Todo（连接池 + token 缓存），修正后 p99=187ms 达标。
教训：包含外部网络请求的接口，在标记 Todo 完成前应先本地压测，不应等到 Judge 检验才发现。

---
```

---

## 文件系统布局（任务完成后）

```
.mem0ress/
└── tasks/
    └── sso_login/
        ├── task.md       # status: COMPLETED，所有 Todo [x]
        ├── session.md    # 3 个 Turn 块（1.1 / 1.2 / 1.3）
        ├── gotchas.md    # 1 条 Gotcha（G-1）
        └── judge.md      # 2 次检验（Turn 2.1 FAILED / Turn 2.2 PASSED）
```

---

## 关键时序

```
08:00  task.md 创建（status: CREATED）
09:15  Turn 1.1 → session.md 第一个快照，status: IN_PROGRESS
11:42  Turn 1.2 → session.md 第二个快照，所有 Todo 标记完成
13:05  Judge Turn 2.1 → judge.md 第一个检验块，Verdict: FAILED（R-1 不达标）
13:10  Gotcha G-1 追加 → gotchas.md
14:30  Turn 1.3 → session.md 第三个快照（性能修正）
15:10  Judge Turn 2.2 → judge.md 第二个检验块，Verdict: PASSED
15:12  主 Agent 调用 complete_task → task.md status: COMPLETED
```
