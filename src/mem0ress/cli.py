"""mem0ress CLI - terminal entry point with Rich visualization.

Usage:
    mem0 status           # Show cognitive status plane
    mem0 status --root .  # Show status plane for custom root
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

from mem0ress.gateway import PlaneAssembler

app = typer.Typer(
    name="mem0",
    help="mem0ress — Cognitive Alignment Plane SDK",
    invoke_without_command=True,
)
console = Console()


@app.command()
def status(
    root: str = typer.Option(
        ".mem0ress",
        "--root",
        "-r",
        help="Path to cognitive substrate root directory",
    ),
) -> None:
    """Display the cognitive status plane with tree visualization."""
    substrate_root = Path(root)

    if not substrate_root.exists():
        console.print(f"[yellow]No cognitive substrate found at[/yellow] [bold]{root}[/bold]")
        console.print(
            "[dim]Run mem0ress from a project initialized with cognitive substrate.[/dim]"
        )
        raise typer.Exit(code=0)

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
        ".mem0ress",
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
    laws = "\n".join(f"  {i+1}. {law}" for i, law in enumerate(plane.system_laws))
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
        f"■ [bold]{entry.task_id}[/bold] {progress} "
        f"[{status_color}]{status_label}[/{status_color}]"
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
