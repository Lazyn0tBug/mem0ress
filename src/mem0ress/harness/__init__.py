"""Harness Engine - Task Verification System.

This module implements the three-tier verification logic:

Tier 1: Mechanical state check (Todo + subtask closure)
Tier 2: Objective requirements check (test/scripts)
Tier 3: Cross-plane semantic alignment (LLM-as-a-Judge, placeholder)
"""

from typing import List, Optional
from dataclasses import dataclass

from mem0ress.core.schema import TaskManifest, TaskStatus


@dataclass
class HarnessResult:
    """Result of a single verification tier."""

    tier: int  # 1, 2, or 3
    passed: bool
    message: str
    deviation: Optional[str] = None  # Deviation reason if failed


class HarnessRunner:
    """Task verification engine using three-tier validation."""

    def verify_task(
        self,
        manifest: TaskManifest,
        subtasks: Optional[List[TaskManifest]] = None,
    ) -> List[HarnessResult]:
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

        # Tier 3: Cross-plane semantic alignment (placeholder)
        results.append(self._verify_tier3(manifest))

        return results

    def _verify_tier1(
        self,
        manifest: TaskManifest,
        subtasks: List[TaskManifest],
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

        For now, this is a placeholder that always passes.
        In full implementation, this would run test scripts.
        """
        requirements = manifest.cognitive_triad.requirements

        if not requirements:
            return HarnessResult(
                tier=2,
                passed=True,
                message="Tier 2 通过: 无客观验收标准（跳过）",
            )

        # TODO: Run actual test scripts for each requirement
        return HarnessResult(
            tier=2,
            passed=True,
            message=f"Tier 2 通过: {len(requirements)} 项需求待验证（Placeholder）",
        )

    def _verify_tier3(self, manifest: TaskManifest) -> HarnessResult:
        """Tier 3: Cross-plane semantic alignment (LLM-as-a-Judge).

        This is a placeholder for the LLM-based semantic check.
        """
        picture = manifest.cognitive_triad.picture

        return HarnessResult(
            tier=3,
            passed=True,
            message="Tier 3 通过: 跨平面语义对齐（Placeholder）",
        )

    def is_complete(self, results: List[HarnessResult]) -> bool:
        """Check if all tiers passed."""
        return all(r.passed for r in results)