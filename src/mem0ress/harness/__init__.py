"""Harness Engine - Task Verification System.

This module implements Tier 1/2/3 verification logic:

Tier 1: Mechanical state check (Todo + subtask closure)
Tier 2: Objective requirements check (test/scripts via subprocess)
Tier 3: Semantic alignment (prepared for Agent, performed by Agent)

Tier 3 is NOT automated by mem0ress. Per spec.md 7.2:
- Tier 3 is triggered by Agent's 主动决策
- The semantic alignment judgment is performed BY the Agent
- prepare_judge_context() prepares the judgment briefing for the Agent

The Agent receives the briefing and performs the actual semantic judgment.
mem0ress does not call any LLM or external model.
"""

from __future__ import annotations

import shlex
import subprocess

from pydantic import BaseModel, Field

from mem0ress.core.schema import TaskManifest, TaskStatus
from mem0ress.harness.judge import JudgeResult as JudgeResult
from mem0ress.harness.judge import prepare_judge_context as prepare_judge_context


class HarnessResult(BaseModel):
    """Result of a single verification tier."""

    model_config = {"extra": "forbid"}

    tier: int = Field(description="1, 2, or 3")
    passed: bool = Field(description="Whether this tier passed")
    message: str = Field(description="Human-readable result message")
    deviation: str | None = Field(default=None, description="Deviation reason if failed")


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

        # Tier 3: Semantic alignment context preparation
        # Actual judgment is performed by the Agent
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
        pending_todos = [t for t in manifest.todos if not t.done]
        if pending_todos:
            todo_texts = ", ".join(f'"{t.text}"' for t in pending_todos)
            return HarnessResult(
                tier=1,
                passed=False,
                message=f"还有 {len(pending_todos)} 项 Todo 未完成: {todo_texts}",
                deviation=f"未完成: {todo_texts}",
            )

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
            if req.startswith("shell:"):
                cmd = req[6:].strip()
                try:
                    # Use shell=False + shlex.split to prevent shell injection.
                    # Commands are user-authored via Requirements, so we sanitize
                    # by splitting into argv — prevents embedded pipes, redirects,
                    # and subshells from being interpreted.
                    args = shlex.split(cmd)
                    if not args:
                        failed.append(f"命令为空: {cmd}")
                        continue
                    result = subprocess.run(
                        args,
                        shell=False,
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
        """Tier 3: Prepare semantic alignment context for Agent.

        Per spec.md 7.2, Tier 3 is triggered by Agent's 主动决策.
        mem0ress prepares the judgment context via prepare_judge_context(),
        but the actual semantic alignment judgment is performed BY the Agent.

        Returns a HarnessResult containing the Agent-facing judgment briefing.
        """
        ctx = prepare_judge_context(
            task_id=manifest.id,
            picture=manifest.cognitive_triad.picture,
            constraints=manifest.cognitive_triad.constraints,
        )

        return HarnessResult(
            tier=3,
            passed=True,
            message=f"Tier 3: 请根据以下上下文自主判断是否对齐\n{ctx.reasoning}",
            deviation=ctx.deviation,
        )

    def is_complete(self, results: list[HarnessResult]) -> bool:
        """Check if all tiers passed."""
        return all(r.passed for r in results)
