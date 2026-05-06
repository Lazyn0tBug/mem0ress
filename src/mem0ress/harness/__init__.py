"""Harness Engine - Task Verification System.

This module implements the three-tier verification logic:

Tier 1: Mechanical state check (Todo + subtask closure)
Tier 2: Objective requirements check (test/scripts via subprocess)
Tier 3: Cross-plane semantic alignment (LLM-as-a-Judge, placeholder)
"""

import subprocess
from typing import List, Optional, Dict
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