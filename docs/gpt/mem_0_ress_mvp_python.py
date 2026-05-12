#!/usr/bin/env python3
"""
mem0ress MVP
A lightweight task-state harness for long-running AI agents.

Single-file Python implementation.

Core features:
- .mem0ress workspace initialization
- task creation with Picture / Requirements / Constraints / Todos
- task listing and display
- session snapshot append
- gotcha add / resolve
- status plane generation
- simple judge flow
- Git commit data plane capture

Usage examples:

  python mem0ress.py init

  python mem0ress.py task create oauth_login \
    --picture "Users can login with Google or GitHub without breaking email login" \
    --requirement "Google OAuth works" \
    --requirement "GitHub OAuth works" \
    --constraint "hard:Do not modify public API signatures" \
    --constraint "hard:Do not break existing email/password login" \
    --todo "Inspect existing auth architecture" \
    --todo "Add Google OAuth provider" \
    --todo "Add GitHub OAuth provider" \
    --todo "Run regression tests"

  python mem0ress.py plane build oauth_login
  python mem0ress.py gotcha add oauth_login "Directly changing auth middleware broke session tests" --severity high
  python mem0ress.py task todo oauth_login T1 done
  python mem0ress.py task req oauth_login R1 satisfied --evidence "tests/auth_google.spec.ts passed"
  python mem0ress.py judge run oauth_login

Design note:
This MVP intentionally uses JSON stored in .yaml files when PyYAML is unavailable.
JSON is valid YAML 1.2, so this remains compatible with YAML parsers.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


MEM_DIR = ".mem0ress"
TASKS_DIR = "tasks"
DEFAULT_CONFIG = {
    "version": "0.1",
    "active_task": None,
    "status_plane_mode": "active_context",
}

VALID_STATES = {
    "CREATED",
    "IN_PROGRESS",
    "BLOCKED",
    "NEEDS_USER",
    "VERIFYING",
    "COMPLETED",
    "FAILED",
    "ABANDONED",
    "SUPERSEDED",
}

CLOSED_STATES = {"COMPLETED", "ABANDONED", "SUPERSEDED"}
REQ_STATUSES = {"pending", "satisfied", "failed", "unknown"}
TODO_STATUSES = {"pending", "doing", "done", "skipped"}
CONSTRAINT_STATUSES = {"clear", "warning", "violated", "unknown"}
GOTCHA_STATUSES = {"open", "resolved"}
SEVERITIES = {"low", "medium", "high", "critical"}


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------


def now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def info(message: str) -> None:
    print(message)


def root_dir() -> Path:
    return Path.cwd()


def mem_dir() -> Path:
    return root_dir() / MEM_DIR


def tasks_dir() -> Path:
    return mem_dir() / TASKS_DIR


def config_path() -> Path:
    return mem_dir() / "config.yaml"


def ensure_workspace() -> None:
    if not mem_dir().exists():
        die("No .mem0ress workspace found. Run `mem0ress init` first.")


def ensure_task_id(task_id: str) -> None:
    if not task_id or not task_id.strip():
        die("task_id cannot be empty")
    bad_chars = {"/", "\\", ":", "*", "?", '"', "<", ">", "|", " "}
    if any(c in task_id for c in bad_chars):
        die("task_id must not contain spaces or path separators. Use snake_case, e.g. oauth_login.")


def task_dir(task_id: str) -> Path:
    return tasks_dir() / task_id


def task_file(task_id: str) -> Path:
    return task_dir(task_id) / "task.yaml"


def gotchas_file(task_id: str) -> Path:
    return task_dir(task_id) / "gotchas.yaml"


def session_file(task_id: str) -> Path:
    return task_dir(task_id) / "session.md"


def judge_file(task_id: str) -> Path:
    return task_dir(task_id) / "judge.md"


def read_text(path: Path, default: str = "") -> str:
    if not path.exists():
        return default
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_data(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return default
    if yaml is not None:
        data = yaml.safe_load(raw)
        return data if data is not None else default
    return json.loads(raw)


def dump_data(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is not None:
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    else:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_config() -> Dict[str, Any]:
    return load_data(config_path(), DEFAULT_CONFIG.copy())


def save_config(config: Dict[str, Any]) -> None:
    dump_data(config_path(), config)


def load_task(task_id: str) -> Dict[str, Any]:
    ensure_workspace()
    path = task_file(task_id)
    if not path.exists():
        die(f"Task not found: {task_id}")
    return load_data(path, {})


def save_task(task: Dict[str, Any]) -> None:
    task_id = task.get("id")
    if not task_id:
        die("Task has no id")
    task["updated_at"] = now_iso()
    dump_data(task_file(task_id), task)


def load_gotchas(task_id: str) -> Dict[str, Any]:
    return load_data(gotchas_file(task_id), {"gotchas": []})


def save_gotchas(task_id: str, data: Dict[str, Any]) -> None:
    dump_data(gotchas_file(task_id), data)


def next_id(items: List[Dict[str, Any]], prefix: str) -> str:
    nums = []
    for item in items:
        item_id = str(item.get("id", ""))
        if item_id.startswith(prefix):
            suffix = item_id[len(prefix):]
            if suffix.isdigit():
                nums.append(int(suffix))
    return f"{prefix}{max(nums, default=0) + 1}"


def git_commit() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root_dir(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def git_dirty() -> Optional[bool]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root_dir(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return bool(result.stdout.strip())
    except Exception:
        pass
    return None


def current_data_plane() -> Dict[str, Any]:
    commit = git_commit()
    dirty = git_dirty()
    return {
        "repos": {
            root_dir().name: {
                "commit": commit,
                "dirty": dirty,
            }
        }
    }


def print_data(data: Any) -> None:
    if yaml is not None:
        print(yaml.safe_dump(data, allow_unicode=True, sort_keys=False).strip())
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def parse_constraint(raw: str, idx: int) -> Dict[str, Any]:
    """Parse constraint strings like hard:Do not modify public API."""
    ctype = "soft"
    text = raw
    if ":" in raw:
        head, tail = raw.split(":", 1)
        if head.lower().strip() in {"hard", "soft"}:
            ctype = head.lower().strip()
            text = tail.strip()
    return {
        "id": f"C{idx}",
        "type": ctype,
        "text": text.strip(),
        "detection": "manual_or_agent_check",
        "status": "clear",
    }


def format_table(rows: List[Tuple[str, str]], width: int = 18) -> str:
    return "\n".join(f"{k:<{width}} {v}" for k, v in rows)


def summarize_text(text: str, max_len: int = 120) -> str:
    text = " ".join(text.split())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


# -----------------------------------------------------------------------------
# Workspace
# -----------------------------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> None:
    md = mem_dir()
    if md.exists() and not args.force:
        info(".mem0ress already exists. Use --force to overwrite config only.")
    md.mkdir(exist_ok=True)
    tasks_dir().mkdir(exist_ok=True)

    if not config_path().exists() or args.force:
        save_config(DEFAULT_CONFIG.copy())

    readme = mem_dir() / "README.md"
    if not readme.exists():
        write_text(
            readme,
            textwrap.dedent(
                """
                # .mem0ress

                Local task-state workspace for long-running AI agents.

                Core files:
                - config.yaml
                - tasks/{task_id}/task.yaml
                - tasks/{task_id}/session.md
                - tasks/{task_id}/gotchas.yaml
                - tasks/{task_id}/judge.md
                """
            ).strip()
            + "\n",
        )

    info("Initialized .mem0ress workspace.")


# -----------------------------------------------------------------------------
# Task commands
# -----------------------------------------------------------------------------


def cmd_task_create(args: argparse.Namespace) -> None:
    ensure_workspace()
    ensure_task_id(args.task_id)

    td = task_dir(args.task_id)
    if td.exists() and not args.force:
        die(f"Task already exists: {args.task_id}. Use --force to overwrite.")
    td.mkdir(parents=True, exist_ok=True)

    requirements = []
    for i, req in enumerate(args.requirement or [], start=1):
        requirements.append(
            {
                "id": f"R{i}",
                "text": req.strip(),
                "verification": "manual_or_agent_check",
                "status": "pending",
                "evidence": None,
            }
        )

    constraints = []
    for i, constraint in enumerate(args.constraint or [], start=1):
        constraints.append(parse_constraint(constraint, i))

    todos = []
    for i, todo in enumerate(args.todo or [], start=1):
        todos.append({"id": f"T{i}", "text": todo.strip(), "status": "pending"})

    task = {
        "id": args.task_id,
        "parent_id": args.parent,
        "status": "CREATED",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "picture": args.picture.strip(),
        "requirements": requirements,
        "constraints": constraints,
        "todos": todos,
        "data_plane": current_data_plane(),
        "next_actions": [todos[0]["text"]] if todos else [],
    }

    dump_data(task_file(args.task_id), task)
    dump_data(gotchas_file(args.task_id), {"gotchas": []})
    write_text(session_file(args.task_id), f"# Session — {args.task_id}\n\n")
    write_text(judge_file(args.task_id), f"# Judge Report — {args.task_id}\n\nNo judge run yet.\n")

    config = load_config()
    if args.activate or not config.get("active_task"):
        config["active_task"] = args.task_id
        save_config(config)

    append_session(
        args.task_id,
        summary="Task created.",
        state_changes=["Task initialized with PRC and todos."],
        evidence=[],
        next_action=task["next_actions"][0] if task["next_actions"] else None,
        data_plane=task["data_plane"],
    )

    info(f"Created task: {args.task_id}")


def cmd_task_list(args: argparse.Namespace) -> None:
    ensure_workspace()
    if not tasks_dir().exists():
        info("No tasks.")
        return

    rows = []
    for path in sorted(tasks_dir().iterdir()):
        if not path.is_dir():
            continue
        task_path = path / "task.yaml"
        if not task_path.exists():
            continue
        task = load_data(task_path, {})
        todos = task.get("todos", [])
        done = sum(1 for t in todos if t.get("status") in {"done", "skipped"})
        rows.append(
            (
                task.get("id", path.name),
                task.get("status", "UNKNOWN"),
                f"{done}/{len(todos)} todos",
                summarize_text(task.get("picture", ""), 80),
            )
        )

    if not rows:
        info("No tasks.")
        return

    print(f"{'ID':<24} {'STATUS':<14} {'PROGRESS':<14} PICTURE")
    print("-" * 90)
    for task_id, status, progress, picture in rows:
        print(f"{task_id:<24} {status:<14} {progress:<14} {picture}")


def cmd_task_show(args: argparse.Namespace) -> None:
    task = load_task(args.task_id)
    print_data(task)


def cmd_task_activate(args: argparse.Namespace) -> None:
    load_task(args.task_id)
    config = load_config()
    config["active_task"] = args.task_id
    save_config(config)
    info(f"Active task set to: {args.task_id}")


def cmd_task_state(args: argparse.Namespace) -> None:
    task = load_task(args.task_id)
    state = args.state.upper()
    if state not in VALID_STATES:
        die(f"Invalid state: {state}. Valid states: {', '.join(sorted(VALID_STATES))}")
    old = task.get("status")
    task["status"] = state
    save_task(task)
    append_session(
        args.task_id,
        summary=f"Task state changed from {old} to {state}.",
        state_changes=[f"status: {old} -> {state}"],
        evidence=[],
        next_action=None,
        data_plane=current_data_plane(),
    )
    info(f"Task {args.task_id} state: {old} -> {state}")


def cmd_task_todo(args: argparse.Namespace) -> None:
    task = load_task(args.task_id)
    status = args.status.lower()
    if status not in TODO_STATUSES:
        die(f"Invalid todo status: {status}. Valid: {', '.join(sorted(TODO_STATUSES))}")

    found = False
    for todo in task.get("todos", []):
        if todo.get("id") == args.todo_id:
            old = todo.get("status")
            todo["status"] = status
            found = True
            break
    if not found:
        die(f"Todo not found: {args.todo_id}")

    if task.get("status") == "CREATED" and status in {"doing", "done"}:
        task["status"] = "IN_PROGRESS"

    save_task(task)
    append_session(
        args.task_id,
        summary=f"Todo {args.todo_id} changed to {status}.",
        state_changes=[f"{args.todo_id}: {old} -> {status}"],
        evidence=[],
        next_action=None,
        data_plane=current_data_plane(),
    )
    info(f"Updated {args.todo_id}: {old} -> {status}")


def cmd_task_req(args: argparse.Namespace) -> None:
    task = load_task(args.task_id)
    status = args.status.lower()
    if status not in REQ_STATUSES:
        die(f"Invalid requirement status: {status}. Valid: {', '.join(sorted(REQ_STATUSES))}")

    found = False
    for req in task.get("requirements", []):
        if req.get("id") == args.req_id:
            old = req.get("status")
            req["status"] = status
            if args.evidence:
                req["evidence"] = args.evidence
            found = True
            break
    if not found:
        die(f"Requirement not found: {args.req_id}")

    if task.get("status") == "CREATED" and status == "satisfied":
        task["status"] = "IN_PROGRESS"

    save_task(task)
    append_session(
        args.task_id,
        summary=f"Requirement {args.req_id} changed to {status}.",
        state_changes=[f"{args.req_id}: {old} -> {status}"],
        evidence=[args.evidence] if args.evidence else [],
        next_action=None,
        data_plane=current_data_plane(),
    )
    info(f"Updated {args.req_id}: {old} -> {status}")


def cmd_task_constraint(args: argparse.Namespace) -> None:
    task = load_task(args.task_id)
    status = args.status.lower()
    if status not in CONSTRAINT_STATUSES:
        die(f"Invalid constraint status: {status}. Valid: {', '.join(sorted(CONSTRAINT_STATUSES))}")

    found = False
    for c in task.get("constraints", []):
        if c.get("id") == args.constraint_id:
            old = c.get("status")
            c["status"] = status
            if args.evidence:
                c["evidence"] = args.evidence
            found = True
            break
    if not found:
        die(f"Constraint not found: {args.constraint_id}")

    save_task(task)
    append_session(
        args.task_id,
        summary=f"Constraint {args.constraint_id} changed to {status}.",
        state_changes=[f"{args.constraint_id}: {old} -> {status}"],
        evidence=[args.evidence] if args.evidence else [],
        next_action=None,
        data_plane=current_data_plane(),
    )
    info(f"Updated {args.constraint_id}: {old} -> {status}")


# -----------------------------------------------------------------------------
# Session commands
# -----------------------------------------------------------------------------


def append_session(
    task_id: str,
    summary: str,
    state_changes: Optional[List[str]] = None,
    evidence: Optional[List[str]] = None,
    next_action: Optional[str] = None,
    data_plane: Optional[Dict[str, Any]] = None,
) -> None:
    path = session_file(task_id)
    turn_no = count_turns(path) + 1
    state_changes = state_changes or []
    evidence = evidence or []
    data_plane = data_plane or current_data_plane()

    lines = []
    lines.append(f"## Turn {turn_no} — {now_iso()}")
    lines.append("")
    lines.append("### Summary")
    lines.append(summary.strip() or "No summary.")
    lines.append("")
    lines.append("### State Changes")
    if state_changes:
        lines.extend(f"- {x}" for x in state_changes)
    else:
        lines.append("- No explicit state changes.")
    lines.append("")
    lines.append("### Data Plane")
    lines.append("```json")
    lines.append(json.dumps(data_plane, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("### Evidence")
    if evidence:
        lines.extend(f"- {x}" for x in evidence)
    else:
        lines.append("- None")
    lines.append("")
    lines.append("### Next Suggested Action")
    lines.append(next_action or "None")
    lines.append("")

    existing = read_text(path, default=f"# Session — {task_id}\n\n")
    write_text(path, existing.rstrip() + "\n\n" + "\n".join(lines))


def count_turns(path: Path) -> int:
    text = read_text(path, "")
    return sum(1 for line in text.splitlines() if line.startswith("## Turn "))


def cmd_session_append(args: argparse.Namespace) -> None:
    load_task(args.task_id)
    changes = args.change or []
    evidence = args.evidence or []
    append_session(
        args.task_id,
        summary=args.summary,
        state_changes=changes,
        evidence=evidence,
        next_action=args.next,
        data_plane=current_data_plane(),
    )
    info(f"Appended session snapshot to task: {args.task_id}")


# -----------------------------------------------------------------------------
# Gotcha commands
# -----------------------------------------------------------------------------


def cmd_gotcha_add(args: argparse.Namespace) -> None:
    load_task(args.task_id)
    severity = args.severity.lower()
    if severity not in SEVERITIES:
        die(f"Invalid severity: {severity}. Valid: {', '.join(sorted(SEVERITIES))}")

    data = load_gotchas(args.task_id)
    gotchas = data.setdefault("gotchas", [])
    gid = next_id(gotchas, "G")
    gotcha = {
        "id": gid,
        "status": "open",
        "severity": severity,
        "linked_task": args.task_id,
        "text": args.text.strip(),
        "evidence": args.evidence,
        "created_at": now_iso(),
        "resolved_at": None,
    }
    gotchas.append(gotcha)
    save_gotchas(args.task_id, data)
    append_session(
        args.task_id,
        summary=f"Gotcha added: {gid}.",
        state_changes=[f"{gid} opened: {args.text.strip()}"],
        evidence=[args.evidence] if args.evidence else [],
        next_action=None,
        data_plane=current_data_plane(),
    )
    info(f"Added gotcha {gid} to {args.task_id}")


def cmd_gotcha_resolve(args: argparse.Namespace) -> None:
    load_task(args.task_id)
    data = load_gotchas(args.task_id)
    found = False
    for g in data.get("gotchas", []):
        if g.get("id") == args.gotcha_id:
            old = g.get("status")
            g["status"] = "resolved"
            g["resolved_at"] = now_iso()
            if args.note:
                g["resolution_note"] = args.note
            found = True
            break
    if not found:
        die(f"Gotcha not found: {args.gotcha_id}")

    save_gotchas(args.task_id, data)
    append_session(
        args.task_id,
        summary=f"Gotcha {args.gotcha_id} resolved.",
        state_changes=[f"{args.gotcha_id}: {old} -> resolved"],
        evidence=[args.note] if args.note else [],
        next_action=None,
        data_plane=current_data_plane(),
    )
    info(f"Resolved gotcha {args.gotcha_id}")


def cmd_gotcha_list(args: argparse.Namespace) -> None:
    load_task(args.task_id)
    data = load_gotchas(args.task_id)
    items = data.get("gotchas", [])
    if args.open_only:
        items = [g for g in items if g.get("status") == "open"]
    if not items:
        info("No gotchas.")
        return
    print_data({"gotchas": items})


# -----------------------------------------------------------------------------
# Status Plane
# -----------------------------------------------------------------------------


def build_status_plane(task_id: str) -> Dict[str, Any]:
    task = load_task(task_id)
    gotchas_data = load_gotchas(task_id)
    open_gotchas = [g for g in gotchas_data.get("gotchas", []) if g.get("status") == "open"]

    todos = task.get("todos", [])
    reqs = task.get("requirements", [])
    constraints = task.get("constraints", [])

    done_todos = [t for t in todos if t.get("status") in {"done", "skipped"}]
    open_requirements = [r for r in reqs if r.get("status") != "satisfied"]
    hard_violations = [c for c in constraints if c.get("type") == "hard" and c.get("status") == "violated"]
    warnings = [c for c in constraints if c.get("status") in {"warning", "violated"} and c not in hard_violations]

    recent_changes = extract_recent_session_changes(task_id, max_items=8)
    next_actions = task.get("next_actions") or infer_next_actions(task, open_gotchas, hard_violations, warnings)

    plane = {
        "status_plane": {
            "active_task": {
                "id": task.get("id"),
                "status": task.get("status"),
                "picture_summary": summarize_text(task.get("picture", ""), 160),
                "progress": f"{len(done_todos)}/{len(todos)} todos done, {len(reqs) - len(open_requirements)}/{len(reqs)} requirements satisfied",
            },
            "parent_chain": build_parent_chain(task),
            "direct_subtasks": list_direct_subtasks(task_id),
            "open_requirements": [
                {"id": r.get("id"), "text": r.get("text"), "status": r.get("status")} for r in open_requirements
            ],
            "constraints": {
                "hard_violations": [
                    {"id": c.get("id"), "text": c.get("text"), "status": c.get("status")} for c in hard_violations
                ],
                "warnings": [
                    {"id": c.get("id"), "text": c.get("text"), "status": c.get("status")} for c in warnings
                ],
            },
            "unresolved_gotchas": [
                {"id": g.get("id"), "severity": g.get("severity"), "text": g.get("text")} for g in open_gotchas
            ],
            "recent_changes": recent_changes,
            "data_plane": task.get("data_plane") or current_data_plane(),
            "next_actions": next_actions,
        }
    }
    return plane


def build_parent_chain(task: Dict[str, Any]) -> List[str]:
    chain = []
    parent_id = task.get("parent_id")
    seen = set()
    while parent_id and parent_id not in seen:
        seen.add(parent_id)
        chain.append(parent_id)
        path = task_file(parent_id)
        if not path.exists():
            break
        parent = load_data(path, {})
        parent_id = parent.get("parent_id")
    return list(reversed(chain))


def list_direct_subtasks(task_id: str) -> List[Dict[str, Any]]:
    results = []
    if not tasks_dir().exists():
        return results
    for path in sorted(tasks_dir().iterdir()):
        tf = path / "task.yaml"
        if not tf.exists():
            continue
        task = load_data(tf, {})
        if task.get("parent_id") == task_id:
            results.append({"id": task.get("id"), "status": task.get("status"), "picture_summary": summarize_text(task.get("picture", ""), 80)})
    return results


def extract_recent_session_changes(task_id: str, max_items: int = 8) -> List[str]:
    text = read_text(session_file(task_id), "")
    lines = text.splitlines()
    changes = []
    capture = False
    for line in reversed(lines):
        if line.startswith("### State Changes"):
            capture = True
            continue
        if capture and line.startswith("### "):
            capture = False
            continue
        if capture and line.strip().startswith("- "):
            item = line.strip()[2:].strip()
            if item and item not in changes:
                changes.append(item)
        if len(changes) >= max_items:
            break
    return list(reversed(changes))


def infer_next_actions(task: Dict[str, Any], open_gotchas: List[Dict[str, Any]], hard_violations: List[Dict[str, Any]], warnings: List[Dict[str, Any]]) -> List[str]:
    if hard_violations:
        return [f"Fix hard constraint violation: {c.get('id')} {c.get('text')}" for c in hard_violations]
    for todo in task.get("todos", []):
        if todo.get("status") not in {"done", "skipped"}:
            return [f"Continue todo {todo.get('id')}: {todo.get('text')}"]
    for req in task.get("requirements", []):
        if req.get("status") != "satisfied":
            return [f"Provide evidence for requirement {req.get('id')}: {req.get('text')}"]
    if warnings:
        return [f"Review warning constraint {c.get('id')}: {c.get('text')}" for c in warnings]
    if open_gotchas:
        return [f"Resolve or acknowledge gotcha {g.get('id')}: {g.get('text')}" for g in open_gotchas]
    return ["Run judge before marking task completed."]


def cmd_plane_build(args: argparse.Namespace) -> None:
    task_id = args.task_id or load_config().get("active_task")
    if not task_id:
        die("No task_id provided and no active_task set.")
    plane = build_status_plane(task_id)
    if args.out:
        dump_data(Path(args.out), plane)
        info(f"Wrote status plane to {args.out}")
    else:
        print_data(plane)


# -----------------------------------------------------------------------------
# Judge
# -----------------------------------------------------------------------------


def run_judge(task_id: str, semantic: bool = False) -> Dict[str, Any]:
    task = load_task(task_id)
    gotchas = load_gotchas(task_id).get("gotchas", [])

    hard_violations = [c for c in task.get("constraints", []) if c.get("type") == "hard" and c.get("status") == "violated"]
    constraint_warnings = [c for c in task.get("constraints", []) if c.get("status") == "warning"]

    todos_pending = [t for t in task.get("todos", []) if t.get("status") not in {"done", "skipped"}]
    subtasks_open = [s for s in list_direct_subtasks(task_id) if s.get("status") not in CLOSED_STATES]
    reqs_pending = [r for r in task.get("requirements", []) if r.get("status") != "satisfied"]
    reqs_without_evidence = [r for r in task.get("requirements", []) if r.get("status") == "satisfied" and not r.get("evidence")]
    open_gotchas = [g for g in gotchas if g.get("status") == "open" and g.get("severity") in {"high", "critical"}]

    result = "READY_TO_COMPLETE"
    reasons = []

    if hard_violations:
        result = "NOT_READY"
        reasons.append("Hard constraints have been violated.")
    if todos_pending:
        result = "NOT_READY"
        reasons.append("Some todos are not closed.")
    if subtasks_open:
        result = "NOT_READY"
        reasons.append("Some direct subtasks are not closed.")
    if reqs_pending:
        result = "NOT_READY"
        reasons.append("Some requirements are not satisfied.")
    if reqs_without_evidence:
        result = "NOT_READY"
        reasons.append("Some satisfied requirements have no evidence.")
    if open_gotchas:
        result = "NOT_READY"
        reasons.append("High or critical gotchas are still open.")

    if task.get("status") in {"BLOCKED", "NEEDS_USER", "FAILED", "ABANDONED", "SUPERSEDED"}:
        result = task.get("status")
        reasons.append(f"Task is currently {task.get('status')}.")

    if semantic:
        semantic_result = "MANUAL_REVIEW_REQUIRED"
        if result == "READY_TO_COMPLETE":
            reasons.append("Tier 3 semantic Picture alignment requested; manual or LLM review is required before completion.")
            result = "NEEDS_USER"
    else:
        semantic_result = "SKIPPED"

    report = {
        "task_id": task_id,
        "generated_at": now_iso(),
        "result": result,
        "reasons": reasons or ["All structural checks passed."],
        "tiers": {
            "tier_0_constraints": {
                "hard_violations": hard_violations,
                "warnings": constraint_warnings,
            },
            "tier_1_todos_and_subtasks": {
                "pending_todos": todos_pending,
                "open_subtasks": subtasks_open,
            },
            "tier_2_requirements": {
                "pending_requirements": reqs_pending,
                "satisfied_without_evidence": reqs_without_evidence,
            },
            "tier_3_picture_alignment": semantic_result,
        },
        "recommendation": judge_recommendation(result),
    }
    return report


def judge_recommendation(result: str) -> str:
    if result == "READY_TO_COMPLETE":
        return "Task can be marked COMPLETED after human or main-agent confirmation."
    if result == "NEEDS_USER":
        return "Ask the user for missing information or semantic confirmation."
    if result == "BLOCKED":
        return "Resolve external dependency or unblock condition before continuing."
    if result == "FAILED":
        return "Review failure, record gotcha if needed, then retry or abandon."
    if result == "ABANDONED":
        return "Task is abandoned; do not continue unless reopened manually."
    if result == "SUPERSEDED":
        return "Follow the replacement task instead."
    return "Continue implementation. Do not mark task completed."


def write_judge_report(task_id: str, report: Dict[str, Any]) -> None:
    lines = []
    lines.append(f"# Judge Report — {task_id}")
    lines.append("")
    lines.append(f"Generated at: {report['generated_at']}")
    lines.append("")
    lines.append("## Result")
    lines.append(str(report["result"]))
    lines.append("")
    lines.append("## Reasons")
    for reason in report.get("reasons", []):
        lines.append(f"- {reason}")
    lines.append("")
    lines.append("## Tier 0: Constraints")
    t0 = report["tiers"]["tier_0_constraints"]
    if not t0["hard_violations"] and not t0["warnings"]:
        lines.append("- Clear")
    for item in t0["hard_violations"]:
        lines.append(f"- HARD VIOLATION {item.get('id')}: {item.get('text')}")
    for item in t0["warnings"]:
        lines.append(f"- WARNING {item.get('id')}: {item.get('text')}")
    lines.append("")
    lines.append("## Tier 1: Todos and Subtasks")
    t1 = report["tiers"]["tier_1_todos_and_subtasks"]
    if not t1["pending_todos"] and not t1["open_subtasks"]:
        lines.append("- Clear")
    for item in t1["pending_todos"]:
        lines.append(f"- Pending todo {item.get('id')}: {item.get('text')}")
    for item in t1["open_subtasks"]:
        lines.append(f"- Open subtask {item.get('id')}: {item.get('status')}")
    lines.append("")
    lines.append("## Tier 2: Requirements")
    t2 = report["tiers"]["tier_2_requirements"]
    if not t2["pending_requirements"] and not t2["satisfied_without_evidence"]:
        lines.append("- Clear")
    for item in t2["pending_requirements"]:
        lines.append(f"- Pending requirement {item.get('id')}: {item.get('text')}")
    for item in t2["satisfied_without_evidence"]:
        lines.append(f"- Missing evidence {item.get('id')}: {item.get('text')}")
    lines.append("")
    lines.append("## Tier 3: Picture Alignment")
    lines.append(f"- {report['tiers']['tier_3_picture_alignment']}")
    lines.append("")
    lines.append("## Recommendation")
    lines.append(report["recommendation"])
    lines.append("")
    lines.append("## Raw JSON")
    lines.append("```json")
    lines.append(json.dumps(report, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    write_text(judge_file(task_id), "\n".join(lines))


def cmd_judge_run(args: argparse.Namespace) -> None:
    report = run_judge(args.task_id, semantic=args.semantic)
    write_judge_report(args.task_id, report)
    append_session(
        args.task_id,
        summary=f"Judge run: {report['result']}.",
        state_changes=[f"judge result: {report['result']}"],
        evidence=[judge_file(args.task_id).as_posix()],
        next_action=report["recommendation"],
        data_plane=current_data_plane(),
    )
    if args.complete and report["result"] == "READY_TO_COMPLETE":
        task = load_task(args.task_id)
        old = task.get("status")
        task["status"] = "COMPLETED"
        save_task(task)
        append_session(
            args.task_id,
            summary="Task marked COMPLETED after judge passed.",
            state_changes=[f"status: {old} -> COMPLETED"],
            evidence=[judge_file(args.task_id).as_posix()],
            next_action=None,
            data_plane=current_data_plane(),
        )
        info("Judge result: READY_TO_COMPLETE. Task marked COMPLETED.")
    else:
        info(f"Judge result: {report['result']}")
        info(report["recommendation"])
        info(f"Report written to: {judge_file(args.task_id)}")


# -----------------------------------------------------------------------------
# Handoff
# -----------------------------------------------------------------------------


def cmd_handoff(args: argparse.Namespace) -> None:
    task_id = args.task_id or load_config().get("active_task")
    if not task_id:
        die("No task_id provided and no active_task set.")
    task = load_task(task_id)
    plane = build_status_plane(task_id)["status_plane"]
    gotchas = load_gotchas(task_id).get("gotchas", [])
    judge = read_text(judge_file(task_id), "No judge report.")

    lines = []
    lines.append(f"# Handoff — {task_id}")
    lines.append("")
    lines.append("## Goal / Picture")
    lines.append(task.get("picture", ""))
    lines.append("")
    lines.append("## Current State")
    lines.append(f"- Status: {task.get('status')}")
    lines.append(f"- Progress: {plane['active_task']['progress']}")
    lines.append("")
    lines.append("## Requirements")
    for r in task.get("requirements", []):
        lines.append(f"- [{r.get('status')}] {r.get('id')}: {r.get('text')} | evidence: {r.get('evidence')}")
    lines.append("")
    lines.append("## Constraints")
    for c in task.get("constraints", []):
        lines.append(f"- [{c.get('status')}] {c.get('type')} {c.get('id')}: {c.get('text')}")
    lines.append("")
    lines.append("## Todos")
    for t in task.get("todos", []):
        lines.append(f"- [{t.get('status')}] {t.get('id')}: {t.get('text')}")
    lines.append("")
    lines.append("## Open Gotchas")
    open_g = [g for g in gotchas if g.get("status") == "open"]
    if open_g:
        for g in open_g:
            lines.append(f"- [{g.get('severity')}] {g.get('id')}: {g.get('text')}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Data Plane")
    lines.append("```json")
    lines.append(json.dumps(plane.get("data_plane"), ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## Next Actions")
    for action in plane.get("next_actions", []):
        lines.append(f"- {action}")
    lines.append("")
    lines.append("## Latest Judge Summary")
    lines.append(summarize_text(judge, 1000))
    lines.append("")

    content = "\n".join(lines)
    if args.out:
        write_text(Path(args.out), content)
        info(f"Wrote handoff to {args.out}")
    else:
        print(content)


# -----------------------------------------------------------------------------
# Parser
# -----------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mem0ress",
        description="Lightweight task-state harness for long-running AI agents.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="Initialize .mem0ress workspace")
    p.add_argument("--force", action="store_true", help="Overwrite config if present")
    p.set_defaults(func=cmd_init)

    task = sub.add_parser("task", help="Task commands")
    task_sub = task.add_subparsers(dest="task_command", required=True)

    p = task_sub.add_parser("create", help="Create a task")
    p.add_argument("task_id")
    p.add_argument("--picture", required=True)
    p.add_argument("--requirement", action="append", default=[])
    p.add_argument("--constraint", action="append", default=[])
    p.add_argument("--todo", action="append", default=[])
    p.add_argument("--parent")
    p.add_argument("--activate", action="store_true")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_task_create)

    p = task_sub.add_parser("list", help="List tasks")
    p.set_defaults(func=cmd_task_list)

    p = task_sub.add_parser("show", help="Show task YAML")
    p.add_argument("task_id")
    p.set_defaults(func=cmd_task_show)

    p = task_sub.add_parser("activate", help="Set active task")
    p.add_argument("task_id")
    p.set_defaults(func=cmd_task_activate)

    p = task_sub.add_parser("state", help="Set task state")
    p.add_argument("task_id")
    p.add_argument("state")
    p.set_defaults(func=cmd_task_state)

    p = task_sub.add_parser("todo", help="Update todo status")
    p.add_argument("task_id")
    p.add_argument("todo_id")
    p.add_argument("status")
    p.set_defaults(func=cmd_task_todo)

    p = task_sub.add_parser("req", help="Update requirement status")
    p.add_argument("task_id")
    p.add_argument("req_id")
    p.add_argument("status")
    p.add_argument("--evidence")
    p.set_defaults(func=cmd_task_req)

    p = task_sub.add_parser("constraint", help="Update constraint status")
    p.add_argument("task_id")
    p.add_argument("constraint_id")
    p.add_argument("status")
    p.add_argument("--evidence")
    p.set_defaults(func=cmd_task_constraint)

    session = sub.add_parser("session", help="Session commands")
    session_sub = session.add_subparsers(dest="session_command", required=True)

    p = session_sub.add_parser("append", help="Append session snapshot")
    p.add_argument("task_id")
    p.add_argument("--summary", required=True)
    p.add_argument("--change", action="append", default=[])
    p.add_argument("--evidence", action="append", default=[])
    p.add_argument("--next")
    p.set_defaults(func=cmd_session_append)

    gotcha = sub.add_parser("gotcha", help="Gotcha commands")
    gotcha_sub = gotcha.add_subparsers(dest="gotcha_command", required=True)

    p = gotcha_sub.add_parser("add", help="Add gotcha")
    p.add_argument("task_id")
    p.add_argument("text")
    p.add_argument("--severity", default="medium")
    p.add_argument("--evidence")
    p.set_defaults(func=cmd_gotcha_add)

    p = gotcha_sub.add_parser("resolve", help="Resolve gotcha")
    p.add_argument("task_id")
    p.add_argument("gotcha_id")
    p.add_argument("--note")
    p.set_defaults(func=cmd_gotcha_resolve)

    p = gotcha_sub.add_parser("list", help="List gotchas")
    p.add_argument("task_id")
    p.add_argument("--open-only", action="store_true")
    p.set_defaults(func=cmd_gotcha_list)

    plane = sub.add_parser("plane", help="Status plane commands")
    plane_sub = plane.add_subparsers(dest="plane_command", required=True)

    p = plane_sub.add_parser("build", help="Build status plane")
    p.add_argument("task_id", nargs="?")
    p.add_argument("--out")
    p.set_defaults(func=cmd_plane_build)

    judge = sub.add_parser("judge", help="Judge commands")
    judge_sub = judge.add_subparsers(dest="judge_command", required=True)

    p = judge_sub.add_parser("run", help="Run judge")
    p.add_argument("task_id")
    p.add_argument("--semantic", action="store_true", help="Request Tier 3 semantic review")
    p.add_argument("--complete", action="store_true", help="Mark COMPLETED if READY_TO_COMPLETE")
    p.set_defaults(func=cmd_judge_run)

    p = sub.add_parser("handoff", help="Generate handoff summary")
    p.add_argument("task_id", nargs="?")
    p.add_argument("--out")
    p.set_defaults(func=cmd_handoff)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
