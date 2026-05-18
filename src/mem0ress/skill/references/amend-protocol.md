# /cap amend Protocol

## Purpose

Amend verify.md entries at any point during task execution. Enables iterative refinement of verification definitions without waiting for `/cap close`.

## Three-State Constraint

| State | marker | Can amend? |
|-------|--------|-----------|
| Unconfirmed | `[]` / `()` / `{}` | ✅ |
| Confirmed | `[.]` / `(.)` / `{.}` | ✅ (before execution) |
| Completed | `[\✓]` / `(\✓)` / `{\✓}` | ❌ |

**Rule**: Completed entries are immutable. Once a marker transitions to completed state, it cannot be reverted or modified.

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

1. Display only unconfirmed entries (`[]` / `()` / `{}`)
2. User selects entry by ID
3. User provides new content (marker state, command, or description)
4. Confirm write
5. Append amend record to session.md

### Step 3b: Add New

1. User provides new requirement ID and description
2. Interactive dialogue determines verification type:
   - `checked` — human confirms manually
   - `command` — automated command
   - `skip` — explicitly skip
3. Marker starts as unconfirmed (`[]` / `()` / `{}`)
4. Confirm write
5. Append to session.md

## Audit Trail

Every amend produces a session.md entry:

```markdown
## Amend @{timestamp}

- verify.md: R-2 [] → [.]
- reason: "确认验证方式"
```
