# /cap amend Protocol

## Purpose

Amend verify.md entries at any point during task execution. Enables iterative refinement of verification definitions without waiting for `/cap close`.

## Three-State Constraint

|| State | marker | Can amend? |
|-------|--------|-----------|
| Unconfirmed | `[]` / `()` / `{}` | ✅ |
| Confirmed | `[.]` / `(.)` / `{.}` | ✅ |
| Completed (non-persistent) | `[\✓]` / `(\✓)` / `{\✓}` | ❌ |
| Completed (persistent) | `[\✓]` / `(\✓)` / `{\✓}` | ✅ (can revert to `[.]` for re-verification) |

**Rule**: Non-persistent `[\✓]` / `(\✓)` / `{\✓}` are permanent — immutable. Persistent `[\✓]` means only "this check passed" — can revert to `[.]` / `(.)` / `{.}` on new semantic drift.

## State Transitions

```
Unconfirmed → Confirmed: interactive dialogue confirms verification method
Confirmed → Completed: verification execution (pass/skip/fail)
Completed → immutably locked
```

## Interaction Flow

### Step 1: Entry Point

User or Agent invokes `/cap amend`.

### Step 2: TUI Choice

```
"Update existing marker" or "Add new marker"?
```

### Step 3a: Update Existing

1. Display only: unconfirmed entries (`[]` / `()` / `{}`) AND confirmed entries (`[.]` / `(.)` / `{.}`) AND completed persistent entries (`[\✓]` / `(\✓)` / `{\✓}` with `persistent: true`)
2. Exclude: completed non-persistent entries (`[\✓]` / `(\✓)` / `{\✓}` with `persistent: false`) — these are permanent
3. User selects entry by ID
4. User provides new content (marker state, command, or description)
5. Confirm write
6. Append amend record to session.md

### Step 3b: Add New

1. User provides new requirement ID and description
2. Interactive dialogue determines verification type:
   - `checked` — human confirms manually
   - `command` — automated command
   - `skip` — explicitly skip
3. **Dialogue must conclude explicitly**: The verification method must be confirmed by the user, transitioning the marker from `[]` / `()` / `{}` (unconfirmed) to `[.]` / `(.)` / `{.}` (confirmed). Until the user explicitly confirms, the entry remains unconfirmed and cannot be executed.

   **Note for persistent requirements**: If this is a persistent requirement (e.g., terminology consistency), the marker transitions to `[\✓]` when at least one todo is completed and one session round ends with Tier 2 pass. New semantic drift in subsequent rounds can revert it to `[.]` / `(.)` / `{.}` for re-verification.
4. Confirm write
5. Append to session.md

## Audit Trail

Every amend produces a session.md entry:

```markdown
## Amend @{timestamp}

- verify.md: R-2 [] → [.]
- reason: "确认验证方式"
```
