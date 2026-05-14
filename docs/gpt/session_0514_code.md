```plaintext
mem0ress/
├── pyproject.toml
├── src/
│   └── mem0ress/
│       ├── cli/
│       │   └── main.py
│       │
│       ├── protocol/
│       │   ├── parser.py
│       │   ├── models.py
│       │   └── snapshots.py
│       │
│       ├── runtime/
│       │   ├── filesystem.py
│       │   ├── renderer.py
│       │   ├── validator.py
│       │   └── judge.py
│       │
│       ├── skill/
│       │   ├── skill.py
│       │   ├── context.py
│       │   ├── models.py
│       │   └── commands/
│       │       ├── recover.py
│       │       ├── status.py
│       │       ├── snapshot.py
│       │       ├── gotcha.py
│       │       ├── verify.py
│       │       └── decide.py
│       │
│       └── workspace/
│           └── init.py
│
└── tests/
```

pyproject.toml

```toml
[project]
name = "mem0ress"
version = "0.1.0"
requires-python = ">=3.12"

dependencies = [
    "pydantic>=2.7.0",
    "typer>=0.12.0",
    "rich>=13.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.5.0",
    "ty>=0.0.1a8",
]

[project.scripts]
mem0ress = "mem0ress.cli.main:app"

[tool.ruff]
line-length = 88
```

`protocol/models.py`

```python
from enum import Enum

from pydantic import BaseModel


class TaskState(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SnapshotType(str, Enum):
    PROGRESS = "PROGRESS"
    DECISION = "DECISION"
    DISCOVERY = "DISCOVERY"


class Snapshot(BaseModel):
    type: SnapshotType
    summary: str
    impact: str | None = None


class Gotcha(BaseModel):
    summary: str


class JudgeVerdict(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    UNCERTAIN = "UNCERTAIN"
    TIMEOUT = "TIMEOUT"


class JudgeEntry(BaseModel):
    verdict: JudgeVerdict
    summary: str


class TaskProtocol(BaseModel):
    picture: str
    requirements: list[str]
    constraints: list[str]
    todos: list[str]
    state: TaskState


class StatusPlane(BaseModel):
    picture: str
    requirements: list[str]
    todos: list[str]
    gotchas: list[str]
    recent_snapshots: list[str]
    latest_verdict: str | None


class DataPlane(BaseModel):
    outputs: list[str]
    evidence: list[str]
    artifacts: list[str]
protocol/parser.py
from mem0ress.protocol.models import TaskProtocol, TaskState


class TaskParser:
    def parse(self, content: str) -> TaskProtocol:
        picture = self._section(content, "Picture")
        requirements = self._list(content, "Requirements")
        constraints = self._list(content, "Constraints")
        todos = self._todos(content)

        return TaskProtocol(
            picture=picture,
            requirements=requirements,
            constraints=constraints,
            todos=todos,
            state=TaskState.IN_PROGRESS,
        )

    def _section(
        self,
        content: str,
        section: str,
    ) -> str:
        lines = content.splitlines()

        capture = False
        collected = []

        for line in lines:
            if line.strip() == f"# {section}":
                capture = True
                continue

            if capture and line.startswith("# "):
                break

            if capture:
                collected.append(line)

        return "\n".join(collected).strip()

    def _list(
        self,
        content: str,
        section: str,
    ) -> list[str]:
        body = self._section(content, section)

        return [
            line.removeprefix("- ").strip()
            for line in body.splitlines()
            if line.startswith("- ")
        ]

    def _todos(self, content: str) -> list[str]:
        return [
            line.removeprefix("- [ ]").strip()
            for line in content.splitlines()
            if line.startswith("- [ ]")
        ]
```

`protocol/snapshots.py`

```python
from datetime import UTC, datetime

from mem0ress.protocol.models import Snapshot


class SnapshotFormatter:
    def format(self, snapshot: Snapshot) -> str:
        timestamp = datetime.now(UTC).isoformat()

        result = [
            f"## Snapshot {timestamp}",
            "",
            f"Type: {snapshot.type}",
            f"Summary: {snapshot.summary}",
        ]

        if snapshot.impact:
            result.append(f"Impact: {snapshot.impact}")

        result.append("")

        return "\n".join(result)
runtime/filesystem.py
from pathlib import Path


class Workspace:
    def __init__(self, root: Path):
        self.root = root

    def task_dir(self, task_id: str) -> Path:
        return self.root / ".mem0ress" / "tasks" / task_id

    def protocol_file(
        self,
        task_id: str,
        filename: str,
    ) -> Path:
        return self.task_dir(task_id) / filename

    def data_dir(self, task_id: str) -> Path:
        return self.task_dir(task_id) / "data"
```

`runtime/renderer.py`

```python
from mem0ress.protocol.models import (
    DataPlane,
    StatusPlane,
)
from mem0ress.protocol.parser import TaskParser
from mem0ress.runtime.filesystem import Workspace


class Renderer:
    def __init__(
        self,
        workspace: Workspace,
    ):
        self.workspace = workspace
        self.parser = TaskParser()

    def render_status_plane(
        self,
        task_id: str,
    ) -> StatusPlane:
        task = self._read(task_id, "task.md")
        session = self._read(task_id, "session.md")
        gotchas = self._read(task_id, "gotchas.md")
        judge = self._read(task_id, "judge.md")

        protocol = self.parser.parse(task)

        return StatusPlane(
            picture=protocol.picture,
            requirements=protocol.requirements,
            todos=protocol.todos,
            gotchas=self._lines(gotchas),
            recent_snapshots=self._recent_snapshots(session),
            latest_verdict=self._latest_verdict(judge),
        )

    def render_data_plane(
        self,
        task_id: str,
    ) -> DataPlane:
        data_dir = self.workspace.data_dir(task_id)

        if not data_dir.exists():
            return DataPlane(
                outputs=[],
                evidence=[],
                artifacts=[],
            )

        files = [
            str(p.relative_to(data_dir))
            for p in data_dir.rglob("*")
            if p.is_file()
        ]

        return DataPlane(
            outputs=[
                f for f in files if f.startswith("outputs/")
            ],
            evidence=[
                f for f in files if f.startswith("evidence/")
            ],
            artifacts=[
                f for f in files if f.startswith("artifacts/")
            ],
        )

    def _read(
        self,
        task_id: str,
        filename: str,
    ) -> str:
        path = self.workspace.protocol_file(
            task_id,
            filename,
        )

        if not path.exists():
            return ""

        return path.read_text(encoding="utf-8")

    def _lines(self, content: str) -> list[str]:
        return [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

    def _recent_snapshots(
        self,
        content: str,
    ) -> list[str]:
        snapshots = []

        current = []

        for line in content.splitlines():
            if line.startswith("## Snapshot"):
                if current:
                    snapshots.append("\n".join(current))

                current = [line]
            else:
                current.append(line)

        if current:
            snapshots.append("\n".join(current))

        return snapshots[-5:]

    def _latest_verdict(
        self,
        content: str,
    ) -> str | None:
        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

        if not lines:
            return None

        return lines[-1]
```

`runtime/validator.py`

```python
from mem0ress.runtime.filesystem import Workspace


class ProtocolValidator:
    REQUIRED = [
        "task.md",
        "session.md",
        "gotchas.md",
        "judge.md",
    ]

    def __init__(
        self,
        workspace: Workspace,
    ):
        self.workspace = workspace

    def validate(
        self,
        task_id: str,
    ) -> list[str]:
        issues = []

        for filename in self.REQUIRED:
            path = self.workspace.protocol_file(
                task_id,
                filename,
            )

            if not path.exists():
                issues.append(
                    f"Missing protocol file: {filename}"
                )

        return issues

```

`runtime/judge.py`

```python
from datetime import UTC, datetime

from mem0ress.runtime.filesystem import Workspace


class JudgeRuntime:
    def __init__(
        self,
        workspace: Workspace,
    ):
        self.workspace = workspace

    def trigger_verify(
        self,
        task_id: str,
    ) -> None:
        path = self.workspace.protocol_file(
            task_id,
            "judge.md",
        )

        timestamp = datetime.now(UTC).isoformat()

        entry = (
            f"\n## Verify Trigger {timestamp}\n\n"
            "Status: VERIFYING\n"
        )

        with path.open("a", encoding="utf-8") as f:
            f.write(entry)
```

`skill/context.py`

```python
from pathlib import Path

from mem0ress.runtime.filesystem import Workspace
from mem0ress.runtime.judge import JudgeRuntime
from mem0ress.runtime.renderer import Renderer
from mem0ress.runtime.validator import ProtocolValidator


class SkillContext:
    def __init__(
        self,
        root: Path,
    ):
        workspace = Workspace(root)

        self.renderer = Renderer(workspace)
        self.validator = ProtocolValidator(workspace)
        self.judge = JudgeRuntime(workspace)
        self.workspace = workspace
skill/models.py
from pydantic import BaseModel


class SkillResult(BaseModel):
    success: bool
    message: str
    data: dict | None = None

```

`skill/skill.py`

```python
from mem0ress.skill.commands.decide import decide
from mem0ress.skill.commands.gotcha import gotcha
from mem0ress.skill.commands.recover import recover
from mem0ress.skill.commands.snapshot import snapshot
from mem0ress.skill.commands.status import status
from mem0ress.skill.commands.verify import verify


class Mem0ressSkill:
    commands = {
        "/mem0ress.recover": recover,
        "/mem0ress.status": status,
        "/mem0ress.snapshot": snapshot,
        "/mem0ress.gotcha": gotcha,
        "/mem0ress.verify": verify,
        "/mem0ress.decide": decide,
    }
skill/commands/recover.py
from mem0ress.skill.context import SkillContext
from mem0ress.skill.models import SkillResult


def recover(
    context: SkillContext,
    task_id: str,
) -> SkillResult:
    plane = context.renderer.render_status_plane(
        task_id,
    )

    return SkillResult(
        success=True,
        message="Recovered task cognition",
        data=plane.model_dump(),
    )
```

`skill/commands/status.py`

```python
from mem0ress.skill.context import SkillContext
from mem0ress.skill.models import SkillResult


def status(
    context: SkillContext,
    task_id: str,
) -> SkillResult:
    status_plane = (
        context.renderer.render_status_plane(
            task_id,
        )
    )

    data_plane = (
        context.renderer.render_data_plane(
            task_id,
        )
    )

    return SkillResult(
        success=True,
        message="Rendered task status",
        data={
            "status_plane": status_plane.model_dump(),
            "data_plane": data_plane.model_dump(),
        },
    )

```

`skill/commands/snapshot.py`

```python
from mem0ress.protocol.models import (
    Snapshot,
    SnapshotType,
)
from mem0ress.protocol.snapshots import (
    SnapshotFormatter,
)
from mem0ress.skill.context import SkillContext
from mem0ress.skill.models import SkillResult


def snapshot(
    context: SkillContext,
    task_id: str,
    summary: str,
    impact: str | None = None,
) -> SkillResult:
    snapshot = Snapshot(
        type=SnapshotType.PROGRESS,
        summary=summary,
        impact=impact,
    )

    formatted = SnapshotFormatter().format(
        snapshot,
    )

    path = context.workspace.protocol_file(
        task_id,
        "session.md",
    )

    with path.open("a", encoding="utf-8") as f:
        f.write(formatted)

    return SkillResult(
        success=True,
        message="Snapshot appended",
    )
skill/commands/gotcha.py
from datetime import UTC, datetime

from mem0ress.skill.context import SkillContext
from mem0ress.skill.models import SkillResult


def gotcha(
    context: SkillContext,
    task_id: str,
    summary: str,
) -> SkillResult:
    path = context.workspace.protocol_file(
        task_id,
        "gotchas.md",
    )

    timestamp = datetime.now(UTC).isoformat()

    entry = (
        f"\n## Gotcha {timestamp}\n\n"
        f"{summary}\n"
    )

    with path.open("a", encoding="utf-8") as f:
        f.write(entry)

    return SkillResult(
        success=True,
        message="Gotcha recorded",
    )
```
    
`skill/commands/verify.py`

```python
from mem0ress.skill.context import SkillContext
from mem0ress.skill.models import SkillResult


def verify(
    context: SkillContext,
    task_id: str,
) -> SkillResult:
    issues = context.validator.validate(
        task_id,
    )

    if issues:
        return SkillResult(
            success=False,
            message="Protocol validation failed",
            data={"issues": issues},
        )

    context.judge.trigger_verify(task_id)

    return SkillResult(
        success=True,
        message="Judge verification triggered",
    )
```

`skill/commands/decide.py`

```python
from mem0ress.skill.context import SkillContext
from mem0ress.skill.models import SkillResult


def decide(
    context: SkillContext,
    task_id: str,
) -> SkillResult:
    plane = context.renderer.render_status_plane(
        task_id,
    )

    verdict = plane.latest_verdict

    return SkillResult(
        success=True,
        message="Judge verdict loaded",
        data={
            "latest_verdict": verdict,
        },
    )

```

`workspace/init.py`

```python
from pathlib import Path


def init_workspace(
    root: Path,
    task_id: str,
) -> None:
    task_dir = (
        root / ".mem0ress" / "tasks" / task_id
    )

    task_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    files = {
        "task.md": (
            "# Picture\n\n"
            "\n"
            "# Requirements\n\n"
            "\n"
            "# Constraints\n\n"
            "\n"
            "# Todos\n\n"
        ),
        "session.md": "",
        "gotchas.md": "",
        "judge.md": "",
    }

    for filename, content in files.items():
        path = task_dir / filename

        if not path.exists():
            path.write_text(
                content,
                encoding="utf-8",
            )

    data = task_dir / "data"

    (data / "outputs").mkdir(
        parents=True,
        exist_ok=True,
    )

    (data / "evidence").mkdir(
        parents=True,
        exist_ok=True,
    )

    (data / "artifacts").mkdir(
        parents=True,
        exist_ok=True,
    )
```

`cli/main.py`

```python
from pathlib import Path

import typer
from rich import print

from mem0ress.skill.context import SkillContext
from mem0ress.skill.skill import Mem0ressSkill
from mem0ress.workspace.init import (
    init_workspace,
)

app = typer.Typer()

root = Path.cwd()

context = SkillContext(root)

skill = Mem0ressSkill()


@app.command()
def init(task_id: str):
    init_workspace(root, task_id)

    print("Workspace initialized")


@app.command()
def recover(task_id: str):
    result = skill.commands[
        "/mem0ress.recover"
    ](
        context,
        task_id,
    )

    print(result.model_dump())


@app.command()
def status(task_id: str):
    result = skill.commands[
        "/mem0ress.status"
    ](
        context,
        task_id,
    )

    print(result.model_dump())


@app.command()
def snapshot(
    task_id: str,
    summary: str,
    impact: str | None = None,
):
    result = skill.commands[
        "/mem0ress.snapshot"
    ](
        context,
        task_id,
        summary,
        impact,
    )

    print(result.model_dump())


@app.command()
def gotcha(
    task_id: str,
    summary: str,
):
    result = skill.commands[
        "/mem0ress.gotcha"
    ](
        context,
        task_id,
        summary,
    )

    print(result.model_dump())


@app.command()
def verify(task_id: str):
    result = skill.commands[
        "/mem0ress.verify"
    ](
        context,
        task_id,
    )

    print(result.model_dump())


@app.command()
def decide(task_id: str):
    result = skill.commands[
        "/mem0ress.decide"
    ](
        context,
        task_id,
    )

    print(result.model_dump())


if __name__ == "__main__":
    app()
```
