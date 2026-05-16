"""mem0ress CLI - terminal entry point with Rich visualization.

Usage:
    mem0 status           # Show cognitive status plane
    mem0 status --root .  # Show status plane for custom root
    mem0 init             # Initialize cognitive substrate
    mem0 create [--picture TEXT] [--requirements TEXT] [--constraints TEXT]
    mem0 update [--content TEXT]   # Append turn snapshot to session.md
    mem0 judge <task_id>                      # Run T0/T1/T2 verification
    mem0 close <task_id>                      # Judge then mark COMPLETED (atomic)
    mem0 done <task_id>                       # Alias for close
    mem0 abandon <task_id>
    mem0 report <task_id>
"""

from __future__ import annotations

import re
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

from mem0ress.core.constants import DEFAULT_SUBSTRATE_ROOT
from mem0ress.core.id_gen import generate_task_id
from mem0ress.core.schema import TaskManifest, TaskStatus
from mem0ress.gateway import PlaneAssembler, TaskServiceImpl
from mem0ress.gateway.current_task import CurrentTaskManager
from mem0ress.gateway.task_info import TaskInfoManager
from mem0ress.substrate.fs import get_file_hash, safe_write
from mem0ress.substrate.parser import SubstrateParser

app = typer.Typer(
    name="mem0",
    help="mem0ress — Cognitive Alignment Plane SDK",
    invoke_without_command=True,
)
console = Console()

TEMPLATE_INDEX = """---
id: {task_id}
type: task
status: created
cognitive_triad:
  picture: ""
  requirements: []
  constraints: []
gotcha_refs: []
---

# Todos
"""

TEMPLATE_SESSION = """---
description: "Session History — 任务执行过程中每个 Turn 的状态快照，按条目追加不覆盖"
type: session
---

# Session History

"""

TEMPLATE_GOTCHA = """---
description: "Gotcha 记录 — 任务执行过程中的认知偏差与经验记录，按条目追加"
type: gotcha
---

# Gotchas (认知偏差与经验记录)

"""

TEMPLATE_JUDGE = (
    "---\n"
    'description: "Judge Agent Verification — Tier 0-3 验证逻辑实例化模板"\n'
    "type: judge\n"
    "---\n"
    "\n"
    "# Judge Agent Verification Logic\n"
    "\n"
    "> **说明：** judge.md 是 mem0ress Tier 验证框架的实例化模板。"
    "Tier 0/1/2/3 的具体验证逻辑由 Agent 根据 task.md 的内容动态生成，"
    "本模板提供结构占位和字段说明。\n"
    "\n"
)

JUDGE_TURN_PATTERN = re.compile(r"^## Turn:\s*(\S+)", re.MULTILINE)
VERIFIER_OUTPUT_PATTERN = re.compile(r"^-\s*`?(\w+)`?:\s*(.+)$", re.MULTILINE)


@app.command()
def status(
    root: str = typer.Option(
        DEFAULT_SUBSTRATE_ROOT,
        "--root",
        "-r",
        help="Path to cognitive substrate root directory",
    ),
) -> None:
    """Display the cognitive status plane with tree visualization."""
    substrate_root = Path(root)

    if not substrate_root.exists():
        console.print(f"[yellow]No cognitive substrate found at[/yellow] [bold]{root}[/bold]")
        console.print("[dim]Run 'mem0 init' first to initialize the substrate.[/dim]")
        raise typer.Exit(code=1)

    try:
        assembler = PlaneAssembler(substrate_root)
        plane = assembler.compile_status_plane()
        render_rich_status_plane(plane, console)
    except Exception as e:
        console.print(f"[red]Error reading status plane:[/red] {e}")
        raise typer.Exit(code=1) from e


@app.command()
def init(
    root: str = typer.Option(
        DEFAULT_SUBSTRATE_ROOT,
        "--root",
        "-r",
        help="Path where to initialize cognitive substrate",
    ),
) -> None:
    """Initialize a new cognitive substrate in the current project."""
    substrate_root = Path(root)

    if substrate_root.exists():
        console.print(f"[yellow]Cognitive substrate already exists at[/yellow] [bold]{root}[/bold]")
        raise typer.Exit(code=0)

    tasks_dir = substrate_root / "tasks"
    tasks_dir.mkdir(parents=True)
    console.print(f"[green]Initialized cognitive substrate at[/green] [bold]{root}[/bold]")


@app.command()
def create(
    picture: str = typer.Option(
        "",
        "--picture",
        "-p",
        help="Semantic goal description — what success looks like",
    ),
    requirements: str = typer.Option(
        "",
        "--requirements",
        "-r",
        help="YAML list of requirements",
    ),
    constraints: str = typer.Option(
        "",
        "--constraints",
        "-c",
        help="YAML list of constraints",
    ),
    root: str = typer.Option(
        DEFAULT_SUBSTRATE_ROOT,
        "--root",
        "-r",
        help="Path to cognitive substrate root directory",
    ),
) -> None:
    """Create a new task with auto-generated 6-char task_id.

    Creates task directory with task.md, session.md, gotchas.md, judge.md.
    Updates .current_task to point to the new task.
    """

    substrate_root = Path(root)
    tasks_dir = substrate_root / "tasks"

    if not tasks_dir.exists():
        console.print(f"[red]No cognitive substrate found at[/red] [bold]{root}[/bold]")
        console.print("[dim]Run 'mem0 init' first to initialize the substrate.[/dim]")
        raise typer.Exit(code=1)

    # Auto-generate task_id
    task_id = generate_task_id()

    # Check for existing active task — warn if non-empty
    ctm = CurrentTaskManager(substrate_root=substrate_root)
    existing_task_id, existing_activated_at = ctm.read()
    if existing_task_id:
        console.print(
            f"[yellow]Warning: overwriting non-empty .current_task "
            f"(was {existing_task_id!r} since {existing_activated_at})[/yellow]"
        )

    # Determine target directory
    target_dir = tasks_dir / task_id

    if target_dir.exists():
        console.print(f"[yellow]Task already exists:[/yellow] [bold]{task_id}[/bold]")
        raise typer.Exit(code=1)

    # Create directories
    target_dir.mkdir(parents=True)

    # Write task.md via TaskServiceImpl for SubstrateParser compatibility
    service = TaskServiceImpl(substrate_root=substrate_root)
    try:
        service.create_task(task_id=task_id, picture=picture)
    except Exception as e:
        # Clean up directory on failure
        import shutil

        shutil.rmtree(target_dir, ignore_errors=True)
        console.print(f"[red]Failed to create task:[/red] {e}")
        raise typer.Exit(code=1) from e

    # Write session.md
    session_path = target_dir / "session.md"
    session_path.write_text(TEMPLATE_SESSION, encoding="utf-8")

    # Write gotchas.md
    gotcha_path = target_dir / "gotchas.md"
    gotcha_path.write_text(TEMPLATE_GOTCHA, encoding="utf-8")

    # Write judge.md
    judge_path = target_dir / "judge.md"
    judge_path.write_text(TEMPLATE_JUDGE, encoding="utf-8")

    # Update .current_task pointer
    ctm.activate_on_create(task_id)

    # Register in .task_info
    task_info = TaskInfoManager(substrate_root=substrate_root)
    task_info.add_task(task_id=task_id, path=f"tasks/{task_id}")

    console.print(f"[green]Created task[/green] [bold]{task_id}[/bold]")

    # If picture was provided, show what was set
    if picture:
        console.print(f"  Picture: {picture}")


@app.command()
def abandon(
    task_id: str | None = None,
    root: str = typer.Option(
        DEFAULT_SUBSTRATE_ROOT,
        "--root",
        "-r",
        help="Path to cognitive substrate root directory",
    ),
) -> None:
    """Mark a task as abandoned. Uses current task if not specified."""
    substrate_root = Path(root)

    # Resolve task_id from .task_info if not provided
    if task_id is None:
        task_info = TaskInfoManager(substrate_root=substrate_root)
        task_id = task_info.get_current_task_id()
        if task_id is None:
            console.print("[red]No active task.[/red] Create or select a task first.")
            raise typer.Exit(code=1)

    # Update task.md (existing helper)
    _update_status(task_id, root, TaskStatus.ABANDONED, "Abandoned")

    # Sync .task_info
    task_info = TaskInfoManager(substrate_root=substrate_root)
    task_info.update_task_status(task_id, TaskStatus.ABANDONED)


@app.command()
def update(
    task_id: str | None = None,
    content: str = typer.Option(
        "",
        "--content",
        "-c",
        help="Turn snapshot content describing what happened this turn",
    ),
    root: str = typer.Option(
        DEFAULT_SUBSTRATE_ROOT,
        "--root",
        "-r",
        help="Path to cognitive substrate root directory",
    ),
) -> None:
    """Append a turn snapshot to session.md.

    Records what happened in the current turn so the Agent can resume
    after context switch without losing state.

    If task_id is not provided, uses the active task from .current_task.
    """
    substrate_root = Path(root)
    service = TaskServiceImpl(substrate_root=substrate_root)

    # Resolve task_id: explicit or from .current_task
    if task_id is None:
        ctm = CurrentTaskManager(substrate_root=substrate_root)
        task_id, _ = ctm.read()
        if task_id is None:
            console.print("[red]No active task.[/red] Provide task_id or create a task first.")
            raise typer.Exit(code=1)
    elif not (substrate_root / "tasks" / task_id).exists():
        console.print(f"[red]Task not found:[/red] [bold]{task_id}[/bold]")
        raise typer.Exit(code=1)

    # Non-interactive: content is required
    if not content:
        console.print("[red]Error:[/red] --content is required when running non-interactively.")
        console.print("Hint: mem0 update --content 'what happened this turn'")
        raise typer.Exit(code=1)

    service.update_session(task_id, content)
    console.print(f"[green]Turn snapshot appended for:[/green] [bold]{task_id}[/bold]")


@app.command()
def judge(
    task_id: str | None = None,
    root: str = typer.Option(
        DEFAULT_SUBSTRATE_ROOT,
        "--root",
        "-r",
        help="Path to cognitive substrate root directory",
    ),
) -> None:
    """Run Tier 0/1/2 verification and write results to judge.md.

    If task_id is not provided, uses the active task from .current_task.
    Output is plain text (no ANSI markup) for agent consumption.
    """
    substrate_root = Path(root)
    service = TaskServiceImpl(substrate_root=substrate_root)

    # Resolve task_id: explicit or from .current_task
    if task_id is None:
        ctm = CurrentTaskManager(substrate_root=substrate_root)
        task_id, _ = ctm.read()
        if task_id is None:
            console.print("[red]No active task.[/red] Provide task_id or create a task first.")
            raise typer.Exit(code=1)
    elif not (substrate_root / "tasks" / task_id).exists():
        console.print(f"[red]Task not found:[/red] [bold]{task_id}[/bold]")
        raise typer.Exit(code=1)

    try:
        results = service.judge_task(task_id)
    except FileNotFoundError:
        console.print(f"[red]Task not found:[/red] [bold]{task_id}[/bold]")
        raise typer.Exit(code=1)

    # Print results to console (plain text, no ANSI markup)
    all_passed = True
    for result in results:
        tier_label = f"Tier {result.tier}"
        status_str = "PASS" if result.passed else "FAIL"
        print(f"  {tier_label}: {status_str}", end="")
        if result.message:
            print(f" — {result.message}", end="")
        if result.deviation:
            print(f" — {result.deviation}", end="")
        print()
        if not result.passed:
            all_passed = False

    # Exit non-zero if any tier failed
    if not all_passed:
        raise typer.Exit(code=1)


@app.command()
def close(
    task_id: str | None = None,
    root: str = typer.Option(
        DEFAULT_SUBSTRATE_ROOT,
        "--root",
        "-r",
        help="Path to cognitive substrate root directory",
    ),
) -> None:
    """Atomically close a task: judge first, then mark COMPLETED.

    This is the MVP's "no bypass" rule — a task cannot be closed
    without passing all verification tiers.

    If task_id is not provided, uses the active task from .current_task.
    On success, clears the .current_task pointer.
    """
    substrate_root = Path(root)
    service = TaskServiceImpl(substrate_root=substrate_root)

    # Resolve task_id: explicit or from .current_task
    if task_id is None:
        ctm = CurrentTaskManager(substrate_root=substrate_root)
        task_id, _ = ctm.read()
        if task_id is None:
            console.print("[red]No active task.[/red] Provide task_id or create a task first.")
            raise typer.Exit(code=1)
    elif not (substrate_root / "tasks" / task_id).exists():
        console.print(f"[red]Task not found:[/red] [bold]{task_id}[/bold]")
        raise typer.Exit(code=1)

    try:
        service.close_task(task_id)
    except RuntimeError as e:
        console.print(f"[red]Close failed:[/red] {e}")
        raise typer.Exit(code=1)
    except FileNotFoundError:
        console.print(f"[red]Task not found:[/red] [bold]{task_id}[/bold]")
        raise typer.Exit(code=1)

    # Clear .current_task on successful close
    ctm = CurrentTaskManager(substrate_root=substrate_root)
    ctm.activate_on_close()

    # Sync .task_info
    task_info = TaskInfoManager(substrate_root=substrate_root)
    task_info.update_task_status(task_id, TaskStatus.COMPLETED)

    console.print(f"[green]Task closed:[/green] [bold]{task_id}[/bold]")
    console.print("Status: COMPLETED")


@app.command()
def done(
    task_id: str | None = None,
    root: str = typer.Option(
        DEFAULT_SUBSTRATE_ROOT,
        "--root",
        "-r",
        help="Path to cognitive substrate root directory",
    ),
) -> None:
    """Mark a task as completed. Alias for 'close' (runs verification first).

    If task_id is not provided, uses the active task from .current_task.
    """
    substrate_root = Path(root)
    service = TaskServiceImpl(substrate_root=substrate_root)

    # Resolve task_id: explicit or from .current_task
    if task_id is None:
        ctm = CurrentTaskManager(substrate_root=substrate_root)
        task_id, _ = ctm.read()
        if task_id is None:
            console.print("[red]No active task.[/red] Provide task_id or create a task first.")
            raise typer.Exit(code=1)
    elif not (substrate_root / "tasks" / task_id).exists():
        console.print(f"[red]Task not found:[/red] [bold]{task_id}[/bold]")
        raise typer.Exit(code=1)

    try:
        service.close_task(task_id)
    except RuntimeError as e:
        console.print(f"[red]Close failed:[/red] {e}")
        raise typer.Exit(code=1)
    except FileNotFoundError:
        console.print(f"[red]Task not found:[/red] [bold]{task_id}[/bold]")
        raise typer.Exit(code=1)

    # Clear .current_task on successful close
    ctm = CurrentTaskManager(substrate_root=substrate_root)
    ctm.activate_on_close()

    # Sync .task_info
    task_info = TaskInfoManager(substrate_root=substrate_root)
    task_info.update_task_status(task_id, TaskStatus.COMPLETED)

    console.print(f"[green]Task closed:[/green] [bold]{task_id}[/bold]")


def _update_status(task_id: str, root: str, new_status: TaskStatus, label: str) -> None:
    """Update task status in task.md frontmatter."""
    substrate_root = Path(root)
    task_path = substrate_root / "tasks" / task_id / "task.md"

    if not task_path.exists():
        console.print(f"[red]Task not found:[/red] [bold]{task_id}[/bold]")
        raise typer.Exit(code=1)

    manifest = SubstrateParser.parse_manifest(task_path)
    expected_hash = get_file_hash(task_path)

    # Create new manifest with updated status (manifest is frozen, must construct new instance)
    updated = TaskManifest(
        id=manifest.id,
        type=manifest.type,
        status=new_status,
        cognitive_triad=manifest.cognitive_triad,
        gotcha_refs=manifest.gotcha_refs,
        todos=manifest.todos,
    )

    content = SubstrateParser.serialize_manifest(updated, task_path)
    safe_write(task_path, content, expected_hash)

    console.print(f"[green]{label}:[/green] [bold]{task_id}[/bold]")


@app.command()
def report(
    task_id: str | None = None,
    root: str = typer.Option(
        DEFAULT_SUBSTRATE_ROOT,
        "--root",
        "-r",
        help="Path to cognitive substrate root directory",
    ),
) -> None:
    """Show the latest judge verification report. Uses current task if not specified."""
    substrate_root = Path(root)

    # Resolve task_id from .task_info if not provided
    if task_id is None:
        task_info = TaskInfoManager(substrate_root=substrate_root)
        task_id = task_info.get_current_task_id()
        if task_id is None:
            console.print("[red]No active task.[/red] Create or select a task first.")
            raise typer.Exit(code=1)

    judge_path = substrate_root / "tasks" / task_id / "judge.md"

    if not judge_path.exists():
        console.print(f"[red]Judge report not found for:[/red] [bold]{task_id}[/bold]")
        raise typer.Exit(code=1)

    content = judge_path.read_text(encoding="utf-8")

    # Find all Turn sections
    turns = list(JUDGE_TURN_PATTERN.finditer(content))
    if not turns:
        console.print(f"[yellow]No verification runs found for:[/yellow] [bold]{task_id}[/bold]")
        raise typer.Exit(code=0)

    # Get the last turn
    last_turn = turns[-1]
    turn_id = last_turn.group(1)
    turn_start = last_turn.start()

    # Find the next turn or end of file
    if len(turns) > 1:
        next_turn = turns[-2]
        turn_content = content[turn_start : next_turn.start()]
    else:
        turn_content = content[turn_start:]

    console.print(f"\n[bold]Judge Report — Turn {turn_id}[/bold]\n")

    # Parse verifier outputs (lines like: - `PASS`: or - FAIL: or - `Tier 0`:)
    current_tier = None
    tier_outputs: dict[str, list[str]] = {}
    current_lines: list[str] = []

    for line in turn_content.split("\n"):
        tier_match = re.match(r"^### Tier (\d+):", line)
        if tier_match:
            if current_tier is not None:
                tier_outputs[current_tier] = current_lines
            current_tier = f"Tier {tier_match.group(1)}"
            current_lines = []
            continue

        vmatch = VERIFIER_OUTPUT_PATTERN.match(line)
        if vmatch:
            key, val = vmatch.groups()
            current_lines.append(f"  {key}: {val}")

    if current_tier is not None:
        tier_outputs[current_tier] = current_lines

    # Render
    for tier, lines in tier_outputs.items():
        console.print(f"[cyan]{tier}[/cyan]")
        if lines:
            for line in lines:
                console.print(line)
        else:
            console.print("  [dim](no output)[/dim]")
        console.print()


@app.command(name="list")
def _list(
    root: str = typer.Option(
        DEFAULT_SUBSTRATE_ROOT,
        "--root",
        "-r",
        help="Path to cognitive substrate root directory",
    ),
) -> None:
    """Show active tasks and optionally select one as current."""
    substrate_root = Path(root)

    task_info = TaskInfoManager(substrate_root=substrate_root)
    active_tasks = task_info.get_active_tasks()
    current_task_id = task_info.get_current_task_id()

    # R3: 0 tasks
    if len(active_tasks) == 0:
        console.print("[yellow]No tasks available. Run 'mem0 create' first.[/yellow]")
        raise typer.Exit(code=1)

    # Print numbered list
    for i, task in enumerate(active_tasks, start=1):
        is_current = task.task_id == current_task_id
        status_label = task.status.value
        activated = ""
        if is_current and task.activated_at:
            date_part = task.activated_at[:10]
            activated = f" ← current (activated {date_part})"
        current_marker = "[bold]" if is_current else ""
        current_end = "[/bold]" if is_current else ""
        console.print(
            f"  {i}. {current_marker}■ {task.task_id}  [{status_label}]{activated}{current_end}"
        )

    # R4: 1 task that is current — exit immediately
    if len(active_tasks) == 1:
        if active_tasks[0].task_id == current_task_id:
            raise typer.Exit(code=0)
        # Auto-select the only task
        task_info.set_current_task(active_tasks[0].task_id)
        raise typer.Exit(code=0)

    # R5: N>1 tasks — interactive selection
    while True:
        user_input = console.input("\nSelect task number: ").strip()
        if user_input == "":
            console.print("[yellow]Invalid input. Enter a number.[/yellow]")
            continue
        try:
            idx = int(user_input) - 1
            if 0 <= idx < len(active_tasks):
                task_info.set_current_task(active_tasks[idx].task_id)
                break
            else:
                max_num = len(active_tasks)
                console.print(
                    f"[yellow]Invalid selection. Enter a number between 1 and {max_num}.[/yellow]"
                )
        except ValueError:
            console.print("[yellow]Invalid input. Enter a number.[/yellow]")

    raise typer.Exit(code=0)


def render_rich_status_plane(plane, console: Console) -> None:
    """Render StatusPlane using Rich with tree formatting.

    Display format:
        ■ {task_id} [{done}/{total}] {STATUS}
           ! {gotcha}
           └─ {subtask}
    """
    tree = Tree("[bold blue]Status Plane[/bold blue]", guide_style="dim")

    if not plane.entries:
        tree.add("[dim](no active tasks)[/dim]")
        console.print(tree)
        return

    for entry in plane.entries:
        entry_tree = _build_entry_tree(entry)
        tree.add(entry_tree)

    console.print(tree)

    # System laws
    laws = "\n".join(f"  {i + 1}. {law}" for i, law in enumerate(plane.system_laws))
    console.print(Panel(laws, title="[bold]System Laws[/bold]", border_style="dim"))


def _build_entry_tree(entry) -> Tree:
    """Build a Rich Tree for a single StatusPlaneEntry."""
    completed, total = entry.todo_progress
    status_label = entry.status.value.upper()

    # Color coding by status
    status_color = {
        "CREATED": "cyan",
        "IN-PROGRESS": "yellow",
        "COMPLETED": "green",
        "ABANDONED": "red",
    }.get(status_label, "white")

    progress = f"[{completed}/{total}]" if total > 0 else "[-]"
    header = (
        f"■ [bold]{entry.task_id}[/bold] {progress} [{status_color}]{status_label}[/{status_color}]"
    )
    entry_tree = Tree(header, guide_style="dim")

    # Gotchas
    for gotcha in entry.gotchas:
        entry_tree.add(f"[red]![/red] [dim]{gotcha}[/dim]")

    # Subtasks
    for subtask in entry.subtasks:
        subtask_tree = _build_entry_tree(subtask)
        entry_tree.add(subtask_tree)

    return entry_tree


if __name__ == "__main__":
    app()
