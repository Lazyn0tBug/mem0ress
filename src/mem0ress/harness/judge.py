"""Tier 3 Semantic Judge - judgment context preparation.

Tier 3 is NOT automated by mem0ress. Per spec.md 7.2:

- Tier 3 is triggered by Agent's 主动决策 (active decision)
- The semantic alignment judgment is performed BY the Agent
  (or by a separate Judge Agent spawned by the host framework)
- This module only prepares the judgment context for the Agent

Trigger conditions (spec.md 7.2):
- Picture involves subjective judgment or stakeholder perception
- Semantic ambiguity between Constraints and Picture
- Host determines task is high-risk (host-defined algorithm)
- Agent or stakeholder explicitly requests Tier 3

The Agent receives the judgment context and performs the actual
semantic alignment check. mem0ress does not call any LLM.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class JudgeResult:
    """Result of a Tier 3 semantic judgment.

    The judgment itself is performed by the Agent (or Judge Agent).
    This dataclass structures the result for consistent handling.
    """

    task_id: str
    aligned: bool
    reasoning: str
    deviation: str | None = None


def prepare_judge_context(
    task_id: str,
    picture: str,
    artifacts: list[Path] | None = None,
    constraints: list[str] | None = None,
    data_plane_summary: str | None = None,
) -> JudgeResult:
    """Prepare judgment context for Agent to perform Tier 3 semantic alignment.

    This function does NOT perform the judgment — it prepares the context
    that the Agent (or a host-spawned Judge Agent) uses to make the call.

    Args:
        task_id: Task identifier
        picture: The task's Picture (intended semantic goal)
        artifacts: File paths to artifacts produced by the task
        constraints: Task constraints to check against
        data_plane_summary: Optional summary of data plane state

    Returns:
        JudgeResult with aligned=True as default — Agent must perform
        the actual semantic judgment and update accordingly
    """
    if artifacts is None:
        artifacts = []

    artifact_summary = _summarize_artifacts(artifacts)
    constraints_str = ", ".join(constraints) if constraints else "无"

    # Build a judgment briefing the Agent can use directly
    briefing = _build_briefing(
        task_id, picture, constraints_str, artifact_summary, data_plane_summary
    )

    return JudgeResult(
        task_id=task_id,
        aligned=True,  # Agent performs judgment and updates this
        reasoning=briefing,
        deviation=None,
    )


def _summarize_artifacts(artifacts: list[Path]) -> str:
    """Build a summary of artifact contents for the Agent's judgment."""
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


def _build_briefing(
    task_id: str,
    picture: str,
    constraints: str,
    artifact_summary: str,
    data_plane_summary: str | None,
) -> str:
    """Build the judgment briefing text for Agent consumption."""
    lines = [
        "Tier 3 语义对齐判断",
        "",
        f"任务: {task_id}",
        f"目标图景: {picture}",
        f"执行约束: {constraints}",
    ]
    if data_plane_summary:
        lines.append(f"\nData Plane 摘要:\n{data_plane_summary}")
    lines.extend(
        [
            "",
            "产出摘要:",
            artifact_summary,
            "",
            "请执行跨平面语义对齐判断：",
            "1. 对比 picture 与实际产出是否语义对齐",
            "2. 检查 constraints 是否被违背",
            "3. 判断是否偏离目标",
            "",
            "判断结果由 Agent 自主决策，mem0ress 不调用任何外部模型。",
        ]
    )
    return "\n".join(lines)
