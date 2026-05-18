# task.md Protocol Schema
# Extracted from CAP Spec §4.4

## File Purpose

task.md is the **semantic authority surface** for a task. It contains:
- Cognitive Triad: Picture / Requirements / Constraints
- Task metadata: id, type, status
- Todos: actionable checklist

## Schema

```yaml
---
id: string
type: task
status: created | in-progress | verifying | completed | abandoned
cognitive_triad:
  picture: string
  requirements:
    - id: string
      description: string
  constraints:
    - string
gotcha_refs: []
todos:
  - text: string
    done: boolean
---
```

## Status Values

| Status | Meaning |
|--------|---------|
| created | Task defined, no todos completed |
| in-progress | At least one todo marked complete |
| verifying | Judge verification in progress (transient) |
| completed | All non-persistent requirements verified AND goal achieved; persistent requirements remain in confirmed state |
| abandoned | Task abandoned |

## Status Transition Rules

| From | To | Trigger |
|------|-----|---------|
| created | in-progress | Any todo marked done |
| created | abandoned | Task abandoned |
| in-progress | completed | Judge verification passes |
| in-progress | abandoned | Task abandoned |

## Write Permissions

| File | Writer | Mode |
|------|--------|------|
| task.md | 主 Agent | Overwrite (cognitive_triad cannot be modified after creation) |
| session.md | 主 Agent | Append only |
| gotchas.md | 主 Agent | Append only |
| judge.md | Judge Agent | Append only |

## Requirements Verification

Each Requirement is paired with a verify.md marker entry defined via interactive dialogue:

| marker | 含义 | 可 amend？ |
|--------|------|-----------|
| `[]` / `()` / `{}` | 未确认 | ✅ |
| `[.]` / `(.)` / `{.}` | 已确认（可执行） | ✅（执行前） |
| `[\✓]` / `(\✓)` / `{\✓}` | 已完成 | ❌ |

**状态转移**：未确认 → 确认 → 已完成（已完成后不可逆向）

## Example

```yaml
---
id: oauth_google
type: task
status: created
cognitive_triad:
  picture: "用户可以通过 Google 登录我们的应用，且 refresh token 存储在加密的数据库字段中"
  requirements:
    - id: req_01
      description: "用户点击 Google 登录按钮后，OAuth flow 完整执行并获得 access_token"
    - id: req_02
      description: "refresh_token 以加密形式存储，不以明文形式出现在日志或响应中"
  constraints:
    - "绝对不得在客户端存储 refresh_token"
    - "必须支持 token revoke"
gotcha_refs: []
todos:
  - text: "实现 Google OAuth flow"
    done: false
  - text: "添加 token 加密存储"
    done: false
  - text: "实现 token revoke"
    done: false
---
```

Corresponding verify.md:

```markdown
type: verify

## Requirements

[.] req_01 command curl -s /auth/google/callback?code=test | grep access_token
[.] req_02 checked 人确认日志中无明文 token
```

## session.md Format

Append-only cognitive delta stream:

```markdown
## Turn N @ {timestamp}

{compressed semantic delta — discoveries, decisions, progress}
```

Rules:
- No raw logs
- No chain-of-thought
- Only: discoveries, decisions, progress

## gotchas.md Format

Recovery-critical discoveries:

```markdown
## Gotcha N @ {timestamp}

{critical finding — ambiguity, drift risk, unstable assumption, blocker}
```

## judge.md Format

Judge verification surface:

```markdown
# Judge Report — {task_id}

**Generated**: {timestamp}
**Status**: PASS | FAIL

## Tier 0 — PASS | FAIL
{message}

## Tier 1 — PASS | FAIL
{message}

## Tier 2 — PASS | FAIL | SKIP
{message}

## Tier 3 — ALIGNED | MISALIGNED | UNCERTAIN
{reasoning}
```

## Tier Definitions

| Tier | Responsibility |
|------|----------------|
| Tier 0 | Constraint violations check |
| Tier 1 | Todo completion check |
| Tier 2 | verify.md marker execution |
| Tier 3 | Semantic alignment (Agent judgment) |
