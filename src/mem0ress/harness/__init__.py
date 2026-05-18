"""Harness Engine - Task Verification System.

This module implements Tier 1/2/3 verification logic:

Tier 1: Mechanical state check (Todo + subtask closure)
Tier 2: Objective requirements check (reads verify.md entry state)
Tier 3: Semantic alignment (prepared for Agent, performed by Agent)

Tier 3 is NOT automated by mem0ress. Per spec.md 7.2:
- Tier 3 is triggered by Agent's 主动决策
- The semantic alignment judgment is performed BY the Agent
- prepare_judge_context() prepares the judgment briefing for the Agent

The Agent receives the briefing and performs the actual semantic judgment.
mem0ress does not call any LLM or external model.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from mem0ress.core.schema import TaskManifest, TaskStatus, VerifyPlane
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
        verify_plane: VerifyPlane | None = None,
    ) -> list[HarnessResult]:
        """Verify a task against three-tier validation.

        Args:
            manifest: Task manifest to verify
            subtasks: List of subtask manifests (empty if none)
            verify_plane: VerifyPlane read from verify.md (None = file not found)

        Returns:
            List of HarnessResult for each tier
        """
        results = []

        # Tier 1: Mechanical state check
        results.append(self._verify_tier1(manifest, subtasks or []))

        # Tier 2: Objective requirements check
        results.append(self._verify_tier2(manifest, verify_plane))

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

    def _verify_tier2(
        self, manifest: TaskManifest, verify_plane: VerifyPlane | None
    ) -> HarnessResult:
        """Tier 2: Objective requirements check using verify.md entry state.

        Reads the VerifyPlane (parsed from verify.md) and checks that all
        requirement entries have state != "unconfirmed". Unconfirmed entries
        mean the requirement has not yet been verified.
        """
        requirements = manifest.cognitive_triad.requirements

        if not requirements:
            return HarnessResult(
                tier=2,
                passed=True,
                message="Tier 2 通过: 无客观验收标准（跳过）",
            )

        # If no verify_plane, entries haven't been created yet
        if verify_plane is None:
            unverified = [
                f"{req.id}: {req.description or '(无描述)'}" for req in requirements
            ]
            msg_lines = "\n".join(f"  - {u}" for u in unverified)
            return HarnessResult(
                tier=2,
                passed=False,
                message=(
                    f"Tier 2: {len(unverified)} 项 requirement "
                    f"尚未在 verify.md 中创建\n{msg_lines}"
                ),
                deviation="verify.md entries not created",
            )

        # Build map of verified entries by id
        entry_map = {e.id: e for e in verify_plane.entries}
        unverified: list[str] = []

        for req in requirements:
            entry = entry_map.get(req.id)
            if entry is None:
                unverified.append(
                    f"{req.id}: {req.description or '(无描述)'} "
                    "(entry not in verify.md)"
                )
            elif entry.state == "unconfirmed":
                unverified.append(
                    f"{req.id}: {req.description or '(无描述)'} "
                    "(state=unconfirmed)"
                )

        if unverified:
            msg_lines = "\n".join(f"  - {u}" for u in unverified)
            return HarnessResult(
                tier=2,
                passed=False,
                message=f"Tier 2: {len(unverified)} 项 requirement 未验证\n{msg_lines}",
                deviation="unverified requirements",
            )

        return HarnessResult(
            tier=2,
            passed=True,
            message=f"Tier 2 通过: {len(requirements)} 项 requirement 全部验证",
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
