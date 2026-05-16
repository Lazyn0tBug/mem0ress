"""Gateway Interceptor - CognitiveContext context manager.

Lifecycle hooks for host integration:

__enter__ (Before Turn):
    - Trigger Plane Assembler to build status plane snapshot
    - Return StatusPlane for host to inject into Agent context

__exit__ (After Turn):
    - Auto-trigger Tier 0 constraint check (Harness Engine)
    - Auto-trigger Session snapshot append (snapshot_session)

Tool Interface write operations (update_todo, complete_task, etc.)
are NOT handled here — those are Agent's主动决策, called explicitly
by the Agent during the turn.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from mem0ress.core.constants import DEFAULT_SUBSTRATE_ROOT
from mem0ress.gateway.plane import PlaneAssembler
from mem0ress.substrate.fs import get_file_hash, safe_write

if TYPE_CHECKING:
    from mem0ress.core.schema import StatusPlane


# Turn number pattern: ## Turn {N.M}
_TURN_PATTERN = re.compile(r"## Turn (\d+)\.(\d+)", re.MULTILINE)


def _next_turn(session_path: Path) -> tuple[int, int]:
    """Determine next turn number from existing session.md.

    Scans for all "## Turn N.M" entries and returns the next
    turn number as (parent, child). If no turns exist, returns (1, 1).
    """
    if not session_path.exists():
        return (1, 1)

    content = session_path.read_text(encoding="utf-8")
    turns = _TURN_PATTERN.findall(content)

    if not turns:
        return (1, 1)

    # Find highest parent turn
    parent = max(int(t[0]) for t in turns)
    # Find highest child turn under the highest parent
    child = max(int(t[1]) for t in turns if int(t[0]) == parent)
    return (parent, child + 1)


def snapshot_session(
    task_id: str,
    substrate_root: Path,
    code_progress: str,
    data_plane: dict[str, str] | None = None,
    todos: list[dict] | None = None,
    status: str = "in-progress",
) -> None:
    """Append a session snapshot to task's session.md.

    Appends a new "## Turn {N.M}" entry following the spec.md B.1 template.
    Turn number auto-increments based on existing entries in session.md.

    Args:
        task_id: Task identifier
        substrate_root: Root directory (.cap)
        code_progress: Description of this turn's code output
        data_plane: Repository → commit ID mapping (optional)
        todos: List of {text, done} dicts (optional, inferred from manifest if None)
        status: Task status string (optional, inferred from manifest if None)
    """
    from mem0ress.substrate.parser import SubstrateParser

    tasks_dir = substrate_root / "tasks"
    session_path = tasks_dir / task_id / "session.md"

    # Determine next turn number
    parent, child = _next_turn(session_path)
    turn_id = f"{parent}.{child}"

    # Build snapshot entry
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    todos_lines: list[str] = []
    if todos:
        for t in todos:
            todos_lines.append(f'  - text: "{t["text"]}", done: {t["done"]}')
    else:
        # Infer from manifest if not provided
        try:
            manifest_path = tasks_dir / task_id / "task.md"
            manifest = SubstrateParser.parse_manifest(manifest_path)
            for t in manifest.todos:
                todos_lines.append(f'  - text: "{t.text}", done: {t.done}')
            status = manifest.status.value
        except Exception:
            todos_lines = []

    data_plane_lines: list[str] = []
    if data_plane:
        for repo, commit in data_plane.items():
            data_plane_lines.append(f"  {repo}: {commit}")
    else:
        data_plane_lines = ["  (no data plane)"]

    snapshot = f"""## Turn {turn_id}
date: {now}
code_progress: "{code_progress}"
data_plane:
{chr(10).join(data_plane_lines)}
todos:
{chr(10).join(todos_lines)}
status: {status}
"""
    # Append to session.md
    if session_path.exists():
        expected_hash = get_file_hash(session_path)
    else:
        expected_hash = ""

    existing = session_path.read_text(encoding="utf-8") if session_path.exists() else "# Session\n"
    new_content = existing.rstrip() + "\n" + snapshot + "\n"

    if session_path.exists():
        safe_write(session_path, new_content, expected_hash)
    else:
        session_path.parent.mkdir(parents=True, exist_ok=True)
        session_path.write_text(new_content, encoding="utf-8")


class CognitiveContext:
    """SDK entry point for host lifecycle hooks.

    Usage (host event loop):
        with CognitiveContext(DEFAULT_SUBSTRATE_ROOT) as ctx:
            status_plane = ctx.status_plane  # inject into Agent context
            # Agent executes turn...
            # (no explicit call needed on exit — hooks fire automatically)

    Before Turn (__enter__):
        - Trigger Plane Assembler to build status plane snapshot
        - Return StatusPlane for Agent context injection

    After Turn (__exit__):
        - Auto-trigger Tier 0 constraint check (Harness Engine)
        - Auto-trigger Session snapshot append

    Note: Tool Interface write operations (update_todo, complete_task,
    abandon_task, etc.) are NOT handled here — those are the Agent's
    active decisions called explicitly during the turn.
    """

    def __init__(self, substrate_root: str | Path = DEFAULT_SUBSTRATE_ROOT):
        """Initialize CognitiveContext.

        Args:
            substrate_root: Root directory for cognitive substrate
        """
        self.substrate_root = Path(substrate_root)
        self._plane_assembler = PlaneAssembler(self.substrate_root)
        self._status_plane: StatusPlane | None = None
        self._tier0_violation: str | None = None

    @property
    def status_plane(self) -> StatusPlane:
        """Get the compiled status plane snapshot.

        Available after __enter__ is called.
        """
        if self._status_plane is None:
            raise RuntimeError(
                "status_plane is only available inside the 'with' block. "
                "Did you forget to use 'with CognitiveContext(...)'?"
            )
        return self._status_plane

    def __enter__(self) -> CognitiveContext:
        """Before Turn hook — compile and return status plane."""
        self._status_plane = self._plane_assembler.compile_status_plane()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """After Turn hook — Tier 0 check + Session snapshot (auto-triggered)."""
        # Tier 0 constraint check — auto-triggered by system
        self._run_tier0_check()

        # Session snapshot — auto-triggered by system
        # Note: code_progress is empty here; host should call snapshot_session
        # explicitly with meaningful code_progress if needed. This hook ensures
        # the snapshot always happens even if host forgets to call explicitly.
        self._append_session_snapshot(code_progress="(auto snapshot)")

    def _run_tier0_check(self) -> None:
        """Run Tier 0 constraint check.

        Tier 0 is auto-triggered at the end of each turn. If constraints
        are violated:
        1. Attempt auto-repair if repairable
        2. If unrepairable, record the violation (Gotcha) — the Agent
           decides whether/how to handle it on the next turn.

        This implementation is a placeholder — the actual auto-repair
        logic depends on what constraints are defined and which are
        repairable by the system.
        """
        # TODO: Implement Tier 0 constraint check
        # - Read all task manifests
        # - For each task, check Constraints against actual state
        # - If violated and repairable: attempt auto-repair
        # - If violated and unrepairable: record Gotcha for Agent to handle
        self._tier0_violation = None

    def _append_session_snapshot(self, code_progress: str) -> None:
        """Append session snapshot for all active tasks.

        Auto-triggered by __exit__. Records a snapshot for each task
        that has been touched. The turn number auto-increments.
        """
        if not self._status_plane:
            return

        for entry in self._status_plane.entries:
            snapshot_session(
                task_id=entry.task_id,
                substrate_root=self.substrate_root,
                code_progress=code_progress,
                todos=[{"text": f"progress [{entry.todo_progress[0]}/{entry.todo_progress[1]}]"}],
                status=entry.status.value,
            )
