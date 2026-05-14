“Hermes Skill 如何参与执行循环”
而这其实是 MVP 最重要的部分之一。

因为：

Skill 才是认知协议进入 Agent Runtime 的入口。
所以现在应该补的是：

“Skill-Level Workflow Design”
而不是 Task 本身。

我认为你的 MVP 应该是：

Hermes
  ↓
mem0ress skills
  ↓
CLI
  ↓
filesystem protocol
并且：

Agent 不直接操作协议文件
而是：

只能通过 skills
这会极大增强协议一致性。

我建议的 Skill 模型
我会把 skill 分成：



类型	作用
Cognitive Skills	管理认知状态
Runtime Skills	推进执行
Judge Skills	触发验证
MVP 只需要：

6 个 skill
MVP Skill Set


Skill	用途
create_task	创建 PRC
load_plane	注入认知
append_snapshot	写 session
update_todo	更新状态
run_judge	执行 Judge
close_task	关闭任务
这已经足够。

场景一（白皮书）Skill Workflow
这是重点。

白皮书场景的真实执行流
Step 1：创建任务
Hermes 调用：

create_task
Skill 输入
{
  "task_id": "whitepaper_ai_runtime",
  "picture": "...",
  "requirements": [...],
  "constraints": [...]
}
Skill 实际动作
底层：

mem0ress task create
生成：

.mem0ress/tasks/whitepaper_ai_runtime/
Step 2：加载认知平面
每轮开始：

Hermes 强制：

load_plane
返回：
Current Task:
whitepaper_ai_runtime

Picture:
...

Progress:
2/6 sections completed

Open Gotchas:
- terminology drift detected

Recent Snapshot:
- rewrote architecture section
关键点
这里：

Hermes 实际拿到的是 Status Plane
而不是 conversation history。

这是 MVP 核心。

Step 3：执行章节写作
Hermes：

Write architecture section
Step 4：追加 Snapshot
写完后：

Hermes 调用：

append_snapshot
Snapshot 内容
{
  "docs_progress": [
    "architecture section completed"
  ],
  "todos_completed": [
    "write_architecture"
  ],
  "state": "IN_PROGRESS"
}
Step 5：Judge Trigger
完成章节后：

Hermes 可调用：

run_judge
Judge 检查
例如：

Constraint:
not workflow engine
但新章节出现：

distributed orchestration scheduler
Judge：

FAIL:
semantic drift detected
Step 6：Hermes 自主决策
这是重点。

mem0ress：

不负责修复
Hermes：

自主决定下一步
例如：

rewrite architecture section
软件开发场景 Skill Workflow
这里更重要。

因为：

这是 executable cognition
Step 1：create_task
创建：

oauth_login
Step 2：load_plane
Hermes 获得：

Picture:
实现 Google OAuth 登录

Todos:
- callback handler
- session persistence
- auth middleware integration

Recent Progress:
- OAuth redirect completed

Open Gotchas:
- session expiration unclear
Step 3：Hermes 编码
例如：

Implement callback handler
Step 4：append_snapshot
{
  "code_progress": [
    "implemented oauth callback route"
  ],
  "todos_completed": [
    "oauth_callback"
  ]
}
Step 5：run_judge
这里：

真正执行 Tier0-2
Tier0
Constraint violation

例如：

introduced sqlite dependency
直接 FAIL。

Tier1
Todo completion。

Tier2
执行：

pytest tests/auth
Step 6：Hermes Decision
Judge：

FAIL:
session persistence broken
Hermes：

continue implementation
最关键的东西来了
你真正应该验证的是：

Skill 是否强制形成认知闭环
即：

load_plane
  ↓
execute
  ↓
append_snapshot
  ↓
judge
  ↓
decision
是否：

稳定

可恢复

抗漂移

我认为 MVP 最关键的一点
是：

load_plane 必须是强制前置 skill
这是整个系统的灵魂。

为什么？
因为：

传统 Agent：

conversation history
  ↓
继续生成
而 mem0ress：

status plane
  ↓
恢复认知
  ↓
继续执行
这就是根本差异。

我甚至建议：
Hermes 禁止直接读取 protocol files
只能：

load_plane()
append_snapshot()
run_judge()
这样：

认知入口会被严格控制。
这是非常重要的。

我建议的 MVP Skill API（最终版）
Cognitive
create_task()
load_plane()
append_snapshot()
Execution
update_todo()
close_task()
Validation
run_judge()
结束。

真的不要再加了。

你现在真正的 MVP 已经开始成型了
因为现在：

你已经形成了：



层	已明确
Protocol	spec
Persistence	filesystem
Runtime Boundary	CLI
Agent Integration	skill
Cognition Injection	load_plane
Validation Loop	judge
Recovery Mechanism	snapshot
这已经不是一个 idea 了。

而是：

一个真实可实现的认知协议系统。


# src/mem0ress_skill/skill.py

```python
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MEM0RESS_BIN = "mem0ress"


# =========================================================
# Base
# =========================================================


class SkillError(RuntimeError):
    pass


@dataclass(slots=True)
class SkillResult:
    ok: bool
    data: dict[str, Any] | None = None
    error: str | None = None


class Mem0ressSkill:
    """
    Hermes Skill Adapter

    Hermes
      ↓
    Skill
      ↓
    mem0ress CLI
      ↓
    filesystem protocol
    """

    def __init__(
        self,
        workspace: str | Path,
        binary: str = MEM0RESS_BIN,
    ) -> None:
        self.workspace = Path(workspace).resolve()
        self.binary = binary

    # =====================================================
    # Internal
    # =====================================================

    def _run(
        self,
        args: list[str],
        *,
        expect_json: bool = True,
    ) -> SkillResult:
        cmd = [
            self.binary,
            *args,
            "--workspace",
            str(self.workspace),
        ]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        if proc.returncode != 0:
            return SkillResult(
                ok=False,
                error=proc.stderr.strip(),
            )

        stdout = proc.stdout.strip()

        if not expect_json:
            return SkillResult(
                ok=True,
                data={"raw": stdout},
            )

        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as exc:
            return SkillResult(
                ok=False,
                error=f"invalid json response: {exc}",
            )

        return SkillResult(
            ok=True,
            data=payload,
        )

    # =====================================================
    # Cognitive Skills
    # =====================================================

    def create_task(
        self,
        *,
        task_id: str,
        picture: str,
        requirements: list[str],
        constraints: list[str],
        todos: list[str],
    ) -> SkillResult:
        """
        Create PRC task.
        """

        payload = {
            "task_id": task_id,
            "picture": picture,
            "requirements": requirements,
            "constraints": constraints,
            "todos": todos,
        }

        return self._run(
            [
                "task",
                "create",
                "--json",
                json.dumps(payload),
            ]
        )

    def load_plane(
        self,
        *,
        task_id: str,
    ) -> SkillResult:
        """
        Load current status plane.

        This is the MOST IMPORTANT skill.
        """

        return self._run(
            [
                "plane",
                "render",
                task_id,
            ]
        )

    def append_snapshot(
        self,
        *,
        task_id: str,
        code_progress: list[str] | None = None,
        docs_progress: list[str] | None = None,
        todos_completed: list[str] | None = None,
        constraint_violations: list[str] | None = None,
        notes: str | None = None,
    ) -> SkillResult:
        """
        Append session snapshot.
        """

        payload = {
            "code_progress": code_progress or [],
            "docs_progress": docs_progress or [],
            "todos_completed": todos_completed or [],
            "constraint_violations": constraint_violations or [],
            "notes": notes,
        }

        return self._run(
            [
                "snapshot",
                "append",
                task_id,
                "--json",
                json.dumps(payload),
            ]
        )

    # =====================================================
    # Execution Skills
    # =====================================================

    def update_todo(
        self,
        *,
        task_id: str,
        todo: str,
        completed: bool,
    ) -> SkillResult:
        """
        Update todo state.
        """

        return self._run(
            [
                "todo",
                "update",
                task_id,
                "--todo",
                todo,
                "--completed",
                str(completed).lower(),
            ]
        )

    def close_task(
        self,
        *,
        task_id: str,
        status: str,
        reason: str | None = None,
    ) -> SkillResult:
        """
        Close task.

        status:
            COMPLETED
            ABANDONED
        """

        args = [
            "task",
            "close",
            task_id,
            "--status",
            status,
        ]

        if reason:
            args.extend(
                [
                    "--reason",
                    reason,
                ]
            )

        return self._run(args)

    # =====================================================
    # Judge Skills
    # =====================================================

    def run_judge(
        self,
        *,
        task_id: str,
        tier3: bool = False,
    ) -> SkillResult:
        """
        Execute judge tiers.
        """

        args = [
            "judge",
            "run",
            task_id,
        ]

        if tier3:
            args.append("--tier3")

        return self._run(args)


# =========================================================
# Hermes Integration Example
# =========================================================


class HermesRuntimeExample:
    """
    Example:
        Hermes Runtime using mem0ress skill.
    """

    def __init__(self, workspace: str) -> None:
        self.skill = Mem0ressSkill(workspace)

    def execute_turn(
        self,
        *,
        task_id: str,
        user_goal: str,
    ) -> None:
        # ---------------------------------------------
        # 1. Load cognition
        # ---------------------------------------------

        plane = self.skill.load_plane(
            task_id=task_id,
        )

        if not plane.ok:
            raise SkillError(plane.error)

        cognition = plane.data

        # ---------------------------------------------
        # 2. Inject cognition into Hermes context
        # ---------------------------------------------

        system_context = {
            "task_plane": cognition,
            "user_goal": user_goal,
        }

        # ---------------------------------------------
        # 3. Hermes executes actual work
        # ---------------------------------------------

        result = self._execute_with_llm(
            system_context
        )

        # ---------------------------------------------
        # 4. Append snapshot
        # ---------------------------------------------

        snapshot = self.skill.append_snapshot(
            task_id=task_id,
            code_progress=result["code_progress"],
            docs_progress=result["docs_progress"],
            todos_completed=result["todos_completed"],
            notes=result["notes"],
        )

        if not snapshot.ok:
            raise SkillError(snapshot.error)

        # ---------------------------------------------
        # 5. Optional judge
        # ---------------------------------------------

        if result["trigger_judge"]:
            judge = self.skill.run_judge(
                task_id=task_id,
            )

            if not judge.ok:
                raise SkillError(judge.error)

            print(judge.data)

    def _execute_with_llm(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Placeholder for Hermes execution.
        """

        return {
            "code_progress": [],
            "docs_progress": [
                "drafted architecture section"
            ],
            "todos_completed": [
                "write_architecture"
            ],
            "notes": "architecture draft completed",
            "trigger_judge": False,
        }
```
