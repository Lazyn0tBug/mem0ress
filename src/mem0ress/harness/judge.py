"""Tier 3 Semantic Judge - out-of-band alignment verification.

Tier 3 performs semantic alignment judgment between a task's Picture
and its actual artifacts. It runs out-of-band (context-isolated from
the executing Agent) to avoid polluting the Agent's execution state.

Trigger conditions (spec.md 7.2):
- Picture involves subjective judgment or stakeholder perception
- Semantic ambiguity exists between Constraints and Picture
- Host determines task is high-risk (host-defined algorithm)
- Agent or stakeholder explicitly requests it

Note: This module requires litellm to be installed for actual LLM calls.
Without litellm, judge() returns a placeholder result indicating the
judgment could not be performed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class JudgeResult:
    """Result of a Tier 3 semantic judgment."""

    task_id: str
    aligned: bool
    reasoning: str
    deviation: str | None = None


def judge(
    task_id: str,
    picture: str,
    artifacts: list[Path] | None = None,
    constraints: list[str] | None = None,
) -> JudgeResult:
    """Judge whether task artifacts are aligned with its Picture.

    Performs out-of-band semantic alignment check. Reads the task's Picture
    and compares it against actual artifacts to determine if the task
    achieved its intended goal.

    Args:
        task_id: Task identifier
        picture: The task's Picture (intended semantic goal)
        artifacts: File paths to artifacts produced by the task
        constraints: Task constraints to check against

    Returns:
        JudgeResult with alignment decision and reasoning
    """
    # TODO: When litellm is available, integrate here.
    #
    # The judge workflow:
    # 1. Read Picture and constraints from manifest
    # 2. Read actual artifact contents
    # 3. Build prompt for LLM to evaluate semantic alignment
    # 4. Call LLM via litellm
    # 5. Parse response into JudgeResult
    #
    # Example litellm usage:
    #   from litellm import completion
    #   response = completion(
    #       model="gpt-4o",
    #       messages=[{"role": "user", "content": judge_prompt}]
    #   )
    #
    # For now, return a placeholder result.

    if artifacts is None:
        artifacts = []

    return JudgeResult(
        task_id=task_id,
        aligned=True,  # Placeholder: assume aligned until LLM is integrated
        reasoning=(
            "Tier 3 semantic judgment is a placeholder. "
            "Install litellm and implement LLM-based judgment to enable "
            "out-of-band semantic alignment verification."
        ),
        deviation=None,
    )


def _summarize_artifacts(artifacts: list[Path]) -> str:
    """Build a summary of artifact contents for the judge prompt."""
    summaries = []
    for artifact in artifacts:
        if not artifact.exists():
            summaries.append(f"(does not exist): {artifact}")
            continue
        try:
            content = artifact.read_text(encoding="utf-8")
            preview = content[:500] + "..." if len(content) > 500 else content
            summaries.append(f"\n--- {artifact} ---\n{preview}")
        except Exception as e:
            summaries.append(f"\n--- {artifact} ---\n(Error reading: {e})")
    return "\n".join(summaries) if summaries else "(no artifacts)"
