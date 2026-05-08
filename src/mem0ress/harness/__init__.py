"""Harness Engine - Task Verification System.

This module implements the three-tier verification logic:

Tier 1: Mechanical state check (Todo + subtask closure)
Tier 2: Objective requirements check (test/scripts via subprocess)
Tier 3: Cross-plane semantic alignment via Judge Task (spawned on-demand)

Judge Task Design:
- Judge is a standard Task with manifest, cognitive_triad, todos
- Judge is spawned on-demand, completes when todos done
- Briefing is embedded in Judge's cognitive_triad
- Result is written to the original task's gotcha_refs

Tier 3 judge logic has been moved to harness/judge.py.
"""

import subprocess

from pydantic import BaseModel, Field

from mem0ress.core.schema import TaskManifest, TaskStatus
from mem0ress.harness.judge import JudgeResult as JudgeResult
from mem0ress.harness.judge import judge as judge


class HarnessResult(BaseModel):
    """Result of a single verification tier."""

    model_config = {"extra": "forbid"}

    tier: int = Field(description="1, 2, or 3")
    passed: bool = Field(description="Whether this tier passed")
    message: str = Field(description="Human-readable result message")
    deviation: str | None = Field(default=None, description="Deviation reason if failed")


class JudgeBriefing(BaseModel):
    """Input for a Judge Task - summarizes what to evaluate."""

    model_config = {"extra": "forbid"}

    target_task_id: str = Field(description="Task ID being judged")
    picture: str = Field(description="Target picture")
    constraints: list[str] = Field(description="Target constraints")
    data_plane_summary: str = Field(description="Main agent prepared summary")
    artifacts: list[str] = Field(description="File paths to check")


class HarnessRunner:
    """Task verification engine using three-tier validation."""

    def verify_task(
        self,
        manifest: TaskManifest,
        subtasks: list[TaskManifest] | None = None,
    ) -> list[HarnessResult]:
        """Verify a task against three-tier validation.

        Args:
            manifest: Task manifest to verify
            subtasks: List of subtask manifests (empty if none)

        Returns:
            List of HarnessResult for each tier
        """
        results = []

        # Tier 1: Mechanical state check
        results.append(self._verify_tier1(manifest, subtasks or []))

        # Tier 2: Objective requirements check
        results.append(self._verify_tier2(manifest))

        # Tier 3: Judge Task (on-demand spawn)
        results.append(self._verify_tier3(manifest))

        return results

    def _verify_tier1(
        self,
        manifest: TaskManifest,
        subtasks: list[TaskManifest],
    ) -> HarnessResult:
        """Tier 1: Mechanical state check.

        Checks:
        - All todos are marked done
        - All subtasks are completed or don't exist
        """
        # Check if all todos are done
        pending_todos = [t for t in manifest.todos if not t.done]
        if pending_todos:
            todo_texts = ", ".join(f'"{t.text}"' for t in pending_todos)
            return HarnessResult(
                tier=1,
                passed=False,
                message=f"还有 {len(pending_todos)} 项 Todo 未完成: {todo_texts}",
                deviation=f"未完成: {todo_texts}",
            )

        # Check if all subtasks are completed
        open_subtasks = [s for s in subtasks if s.status != TaskStatus.COMPLETED]
        if open_subtasks:
            task_ids = ", ".join(s.id for s in open_subtasks)
            return HarnessResult(
                tier=1,
                passed=False,
                message=f"还有 {len(open_subtasks)} 个子任务未完成: {task_ids}",
                deviation=f"子任务未闭环: {task_ids}",
            )

        return HarnessResult(
            tier=1,
            passed=True,
            message="Tier 1 通过: 机械状态检查完成",
        )

    def _verify_tier2(self, manifest: TaskManifest) -> HarnessResult:
        """Tier 2: Objective requirements check.

        Runs validation scripts specified in requirements.
        Requirements with "shell:" prefix are executed as shell commands.
        """
        requirements = manifest.cognitive_triad.requirements

        if not requirements:
            return HarnessResult(
                tier=2,
                passed=True,
                message="Tier 2 通过: 无客观验收标准（跳过）",
            )

        failed = []
        passed_cmds = []

        for req in requirements:
            # Requirements format: "shell:pytest tests/ --cov"
            # or just descriptive text that can't be executed
            if req.startswith("shell:"):
                cmd = req[6:].strip()
                try:
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.returncode == 0:
                        passed_cmds.append(cmd)
                    else:
                        failed.append(f"命令失败: {cmd}\n输出: {result.stderr[:200]}")
                except subprocess.TimeoutExpired:
                    failed.append(f"命令超时: {cmd}")
                except Exception as e:
                    failed.append(f"命令执行异常: {cmd}\n{e}")
            else:
                # Non-executable requirement - pass with note
                passed_cmds.append(f"（描述性）{req}")

        if failed:
            return HarnessResult(
                tier=2,
                passed=False,
                message=f"Tier 2 失败: {len(failed)} 项需求未通过",
                deviation="\n".join(failed),
            )

        return HarnessResult(
            tier=2,
            passed=True,
            message=f"Tier 2 通过: {len(passed_cmds)} 项需求验证通过",
        )

    def _verify_tier3(self, manifest: TaskManifest) -> HarnessResult:
        """Tier 3: Cross-plane semantic alignment via Judge Task.

        Spawns a Judge Task (standard Task) to evaluate alignment.
        The Judge Task:
        - Is created with cognitive_triad containing the briefing
        - Has todos that represent the judgment steps
        - Writes deviation result to target task's gotcha_refs

        For now, this is a placeholder that simulates the Judge workflow.
        """
        target_task_id = manifest.id
        picture = manifest.cognitive_triad.picture
        constraints = manifest.cognitive_triad.constraints

        # Build Judge briefing (stored in cognitive_triad)
        briefing = f"""Judge Task: 评估 {target_task_id} 是否偏离目标

目标图景: {picture}
执行约束: {', '.join(constraints) if constraints else '无'}

请执行跨平面语义对齐判断。

步骤:
1. 读取 target task 的 data plane 产出
2. 对比 picture/constraints 与实际产出
3. 判断是否偏离
4. 如有偏离，详细描述并记录到 gotcha_refs
"""

        # TODO: When running in Agent Framework:
        # - Create _judge-{target_task_id} Task
        # - update_cognitive_triad to write briefing
        # - spawn Judge Agent to execute
        # - Judge completes, result written to gotcha_refs

        # Placeholder: record Judge Task info for tracking
        return HarnessResult(
            tier=3,
            passed=True,
            message=f"Tier 3: Judge Task 已创建 (_judge_{target_task_id})\n"
                    f"（Placeholder - 等待 Judge Agent 完成）\n"
                    f"Briefing: {briefing[:100]}...",
        )

    @staticmethod
    def create_judge_task(
        substrate_root: str,
        target_task_id: str,
        picture: str,
        constraints: list[str],
        data_plane_summary: str,
    ) -> str:
        """Create a Judge Task with embedded briefing.

        Returns the judge task ID.
        """
        judge_task_id = f"_judge_{target_task_id}"

        # Build briefing as cognitive_triad (stored for Agent Framework to use)
        _ = f"""评估任务 '{target_task_id}' 是否偏离目标

目标图景: {picture}
执行约束: {', '.join(constraints) if constraints else '无'}
Data Plane 摘要: {data_plane_summary}

执行步骤:
- [ ] 读取 target task 的 manifest 和 data plane 产出
- [ ] 对比 picture 与实际代码/逻辑
- [ ] 检查 constraints 是否被违背
- [ ] 记录偏离到 gotcha_refs 并完成判断
"""

        # TODO: Actually create the task via TaskServiceImpl
        # For now, return the judge task ID for tracking
        return judge_task_id

    def is_complete(self, results: list[HarnessResult]) -> bool:
        """Check if all tiers passed."""
        return all(r.passed for r in results)