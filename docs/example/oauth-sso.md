# 案例：OAuth 单点登录（软件交付）

> 任务：为企业内部工作台实现 OAuth 单点登录
>
> 类型：软件交付
>
> 特色：完整生命周期（失败 → 修正 → 通过）、Tier 2 `verify_cmd` 执行、gotchas 记录

---

## 执行时序

```
Day 1 08:00  mem0 create → task.md 创建（CREATED）
Day 1 09:15  /cap snapshot → session.md Turn 1.1（基础框架）
Day 1 11:42  /cap snapshot → session.md Turn 1.2（provider 实现完成）
Day 1 13:05  /cap verify → Verify Turn 2.1 → FAILED（R-1 p99=487ms 超标）
Day 1 13:10  gotchas.md → G-1 追加（性能优化教训）
Day 1 14:30  /cap snapshot → session.md Turn 1.3（连接池 + 缓存）
Day 1 15:10  /cap verify → Verify Turn 2.2 → PASSED
Day 1 15:12  mem0 done → COMPLETED
```

---

## task.md（最终状态）

```yaml
---
id: 7k3m9x
type: task
status: COMPLETED
created_at: 2025-01-15T08:00:00Z
completed_at: 2025-01-15T15:12:00Z
---

# Task: 企业工作台 OAuth 单点登录

## Picture

> 员工打开工作台时，无需输入任何密码，点击「使用企业账号登录」后
> 通过 Google 或 GitHub 账号完成授权，直接进入工作台主界面。
> 整个过程感知不到"登录"这个动作的存在，只感知到"进入了"。

---

## Requirements

- [x] R-1: 认证接口端到端响应时间 p99 < 300ms
      verify_cmd: pytest tests/perf/test_auth_latency.py
- [x] R-2: 支持 Google OAuth 2.0 和 GitHub OAuth 两种提供商
      verify_cmd: pytest tests/e2e/test_oauth_providers.py
- [x] R-3: 登录 session 有效期 7 天，过期后自动跳转登录页
      verify_cmd: pytest tests/e2e/test_session_expiry.py
- [x] R-4: 登录失败时展示错误原因，不暴露内部错误信息
      verify_cmd: pytest tests/e2e/test_auth_error_handling.py

---

## Constraints

- C-1: 不允许在任何日志（console、文件、监控系统）中输出用户的 Access Token 或 Refresh Token
- C-2: 不允许在数据库中以明文存储任何用户凭证
- C-3: 所有 OAuth callback URL 必须通过 HTTPS，不允许 HTTP 回调

**verify_cmd 推导说明：** Agent 从需求语义生成验证命令（如"p99 < 300ms" → `pytest tests/perf/test_auth_latency.py`）。用户只需表达业务意图，Agent 负责转化为可执行测试。

---

## Todos

### Phase 1 — 基础框架
- [x] T-1: 搭建 OAuth 基础框架（Provider 抽象接口、HTTPS 中间件、callback 路由）

### Phase 2 — Provider 实现
- [x] T-2: 实现 Google OAuth 2.0 provider（授权流程、token exchange、用户信息获取）
- [x] T-3: 实现 GitHub OAuth provider（授权流程、token exchange、用户信息获取）

### Phase 3 — Session 与错误处理
- [x] T-4: 实现 session 管理（JWT 签发、7 天过期、自动跳转）
- [x] T-5: 实现登录失败错误处理（友好错误信息、错误码映射）

### Phase 4 — 性能优化
- [x] T-6: 性能优化（连接池 + token 缓存，p99 实测 187ms）
```

---

## session.md（完整快照序列）

### Turn 1.1 — 基础框架搭建

```markdown
## Turn 1.1
**Timestamp:** 2025-01-15T09:15:00Z
**Status:** IN_PROGRESS

### Action Summary
搭建了 OAuth 基础框架，定义了 Provider 抽象接口，配置了 HTTPS 强制中间件，
建立了 callback 路由结构。

### Todos
- [x] T-1: 搭建 OAuth 基础框架
- [ ] T-2: 实现 Google OAuth 2.0 provider
- [ ] T-3: 实现 GitHub OAuth provider
- [ ] T-4: 实现 session 管理
- [ ] T-5: 实现登录失败错误处理
- [ ] T-6: 性能优化

### Code Progress
新增 `src/auth/base_provider.py`（抽象接口）、`src/auth/middleware.py`（HTTPS 强制）、
`src/auth/callback.py`（路由结构）。

### Data Plane
- Commit: `a1b2c3d4e5f67890`
- Active Refs:
  - `src/auth/base_provider.py`
  - `src/auth/middleware.py`
  - `src/auth/callback.py`

### Constraint Violations
—
```

### Turn 1.2 — Provider 实现完成

```markdown
## Turn 1.2
**Timestamp:** 2025-01-15T11:42:00Z
**Status:** IN_PROGRESS

### Action Summary
实现了 Google 和 GitHub 两个 OAuth provider，完成了 session 管理和错误处理。
所有 Todo 已完成（T-6 暂标为完成，待 Verify 检验后确认性能达标）。

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

### Data Plane
- Commit: `b2c3d4e5f6789012`
- Active Refs:
  - `src/auth/google_provider.py`
  - `src/auth/github_provider.py`
  - `src/auth/session.py`
  - `src/auth/error_handler.py`

### Constraint Violations
—
```

### Turn 1.3 — 性能修正

```markdown
## Turn 1.3
**Timestamp:** 2025-01-15T14:30:00Z
**Status:** IN_PROGRESS

### Action Summary
针对 Verify Turn 2.1 的 FAILED 结论（R-1 响应时间不达标，p99=487ms）进行专项优化：
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

### Data Plane
- Commit: `c3d4e5f678901234`
- Active Refs:
  - `src/auth/connection_pool.py`
  - `src/auth/token_cache.py`
  - `src/auth/base_provider.py`

### Constraint Violations
—
```

---

## verification.md（完整检验记录）

### Verify Turn 2.1 — 首次检验（FAILED）

```markdown
## Verify Turn 2.1
**Timestamp:** 2025-01-15T13:05:00Z
**Verdict:** FAILED

---

### Tier 0 — Constraints 约束检查

| Constraint | 验证方式 | 结论 |
|-----------|---------|------|
| C-1: 不允许日志输出 Token | 扫描 `logs/` 目录，匹配 `access_token\|refresh_token` | ✅ PASS |
| C-2: 不允许明文存储凭证 | 扫描 `migrations/` 目录，`password\|token` 字段类型 | ✅ PASS |
| C-3: callback URL 必须 HTTPS | 检查 `src/auth/callback.py` 中的 URL 配置 | ✅ PASS |

**Findings:** —

---

### Tier 1 — Todo & Subtask 完成检查

- [x] 所有 Todo 已标记 `[x]`
- [x] 所有直接子任务已处于终态（无子任务）

**未完成项:** —

---

### Tier 2 — Requirements 验收检查

| Requirement | verify_cmd | 输出摘要 | 结论 |
|------------|-----------|---------|------|
| R-1: p99 < 300ms | `pytest tests/perf/test_auth_latency.py` | `FAILED: p99=487ms` | ❌ FAIL |
| R-2: Google + GitHub | `pytest tests/e2e/test_oauth_providers.py` | — | ⏭️ SKIPPED |
| R-3: session 7天 | `pytest tests/e2e/test_session_expiry.py` | — | ⏭️ SKIPPED |
| R-4: 错误处理 | `pytest tests/e2e/test_auth_error_handling.py` | — | ⏭️ SKIPPED |

**Findings:** R-1 未满足。p99=487ms，超出阈值 300ms 的 62%。
快速失败原则，后续 Requirement 未执行检验。

---

### Tier 3 — 语义对齐检查

**Trigger:** SKIPPED — Tier 2 FAILED，Tier 3 强制跳过。

---

**Overall Verdict:** FAILED

**Summary:** Tier 2 失败。R-1 性能未达标（p99=487ms，要求 < 300ms）。
主 Agent 需修正性能问题后重新触发检验。
```

### Verify Turn 2.2 — 复检（PASSED）

```markdown
## Verify Turn 2.2
**Timestamp:** 2025-01-15T15:10:00Z
**Verdict:** PASSED

---

### Tier 0 — Constraints 约束检查

| Constraint | 验证方式 | 结论 |
|-----------|---------|------|
| C-1: 不允许日志输出 Token | 扫描含新增 `connection_pool.py` 的日志 | ✅ PASS |
| C-2: 不允许明文存储凭证 | `token_cache.py` 使用加密存储 | ✅ PASS |
| C-3: callback URL 必须 HTTPS | 检查 `callback.py` 配置，未变更 | ✅ PASS |

**Findings:** —

---

### Tier 1 — Todo & Subtask 完成检查

- [x] 所有 Todo 已标记 `[x]`（含新增 T-6）
- [x] 所有直接子任务已处于终态（无子任务）

**未完成项:** —

---

### Tier 2 — Requirements 验收检查

| Requirement | verify_cmd | 输出摘要 | 结论 |
|------------|-----------|---------|------|
| R-1: p99 < 300ms | `pytest tests/perf/test_auth_latency.py` | `PASSED: p99=187ms` | ✅ PASS |
| R-2: Google + GitHub | `pytest tests/e2e/test_oauth_providers.py` | `2 passed in 4.32s` | ✅ PASS |
| R-3: session 7天 | `pytest tests/e2e/test_session_expiry.py` | `1 passed in 0.91s` | ✅ PASS |
| R-4: 错误处理 | `pytest tests/e2e/test_auth_error_handling.py` | `3 passed in 2.17s` | ✅ PASS |

**Findings:** —

---

### Tier 3 — 语义对齐检查

**Trigger:** 触发。Picture 包含"感知不到登录动作"这一主观体验描述，需语义对齐。

**Verify Prompt:**

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
如果未达成，返回 FAIL，并指出具体偏差。
不要给出修复建议，只报告事实。
```

**Verdict:** PASS

用户全程无密码输入，OAuth 流程对用户透明，session 管理无感知，符合图景描述。

---

**Overall Verdict:** PASSED

**Summary:** 全部四个 Tier 均通过。主 Agent 可调用 `mem0 done`。
```

---

## gotchas.md

```markdown
## Gotcha G-1 — Verify Turn 2.1 FAILED：性能未达标
**Timestamp:** 2025-01-15T13:10:00Z
**Turn:** 2.1

### 触发背景
执行 T-6（性能优化）时未做专项压测，以为 OAuth 外部请求不会成为瓶颈，
直接标记为完成触发检验。

### 实际发生了什么
Verify Turn 2.1 运行 `pytest tests/perf/test_auth_latency.py`，结果 p99=487ms，
超出 R-1 阈值（300ms）62%。根因是每次认证都对 OAuth provider 建立新的 HTTP 连接，
连接握手耗时占总延迟约 58%。

### 如何处理
追加了 T-6 作为专项性能优化 Todo（连接池 + token 缓存），修正后 p99=187ms 达标。

### 教训
包含外部网络请求的接口，在标记 Todo 完成前应先本地压测，
不应等到 Verify 检验才发现。
```

---

## 文件系统布局

```
.cap/
└── tasks/
    └── 7k3m9x/
        ├── task.md       # status: COMPLETED，所有 Todo [x]
        ├── session.md    # 3 个 Turn 快照（1.1 / 1.2 / 1.3）
        ├── gotchas.md    # 1 条 Gotcha（G-1）
        └── verification.md  # 2 次检验（Turn 2.1 FAILED / Turn 2.2 PASSED）
```

---

## 关键协议行为

### 1. Tier 2 verify_cmd 执行

R-1 的 `verify_cmd: pytest tests/perf/test_auth_latency.py` 是 Verify Tier 2 的执行依据。
第一次检验时此命令输出 `FAILED: p99=487ms`，触发 Tier 2 快速失败。
修正后同命令输出 `PASSED: p99=187ms`，Tier 2 通过。

### 2. 快速失败原则

Verify 在 Tier 2 第一项（R-1）失败后，跳过 R-2/R-3/R-4 的验证执行。
理由：后续 Requirement 的验证在前置失败结论已知的情况下不可信。
这避免了无效的检验资源消耗。

### 3. Tier 3 触发模型

本案例中，Tier 3 作为路径末端自动触发——当 Todo 完成触发路径一时（Tier 0 → Tier 2 → Tier 3），或在人的主动 verify 下触发路径二时（Tier 0 → Tier 1 → Tier 2 → Tier 3），Tier 3 在 Tier 0 无 violation + Tier 2 满足后自动进入。Tier 3 无独立触发语义。

### 4. Gotcha 追加时机

G-1 在 Verify FAILED 结论出具后立即追加，不等到任务结束。
偏差发现后立即记录，避免跨轮次遗忘。
