"""Tests for HarnessRunner with mock data."""

from mem0ress.core.schema import (
    CognitiveTriad,
    Requirement,
    TaskManifest,
    TaskStatus,
    TodoItem,
)
from mem0ress.harness import HarnessRunner


class TestHarnessRunnerWithMockData:
    """Test harness verification with mock data."""

    def test_tier1_all_todos_done_no_subtasks(self):
        """Tier 1 passes when all todos done and no subtasks."""
        runner = HarnessRunner()
        manifest = TaskManifest(
            id="test_task",
            status=TaskStatus.IN_PROGRESS,
            cognitive_triad=CognitiveTriad(
                picture="完成测试",
                requirements=[],
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[
                TodoItem(text="写代码", done=True),
                TodoItem(text="写测试", done=True),
            ],
        )

        results = runner.verify_task(manifest, subtasks=[])

        assert runner.is_complete(results) is True
        tier1 = results[0]
        assert tier1.tier == 1
        assert tier1.passed is True

    def test_tier1_fails_with_pending_todos(self):
        """Tier 1 fails when some todos are not done."""
        runner = HarnessRunner()
        manifest = TaskManifest(
            id="test_task",
            status=TaskStatus.IN_PROGRESS,
            cognitive_triad=CognitiveTriad(
                picture="完成测试",
                requirements=[],
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[
                TodoItem(text="写代码", done=True),
                TodoItem(text="写测试", done=False),
            ],
        )

        results = runner.verify_task(manifest, subtasks=[])

        tier1 = results[0]
        assert tier1.passed is False
        assert "还有 1 项 Todo 未完成" in tier1.message
        assert tier1.deviation is not None

    def test_tier1_fails_with_open_subtasks(self):
        """Tier 1 fails when subtasks are not completed."""
        runner = HarnessRunner()
        parent = TaskManifest(
            id="parent_task",
            status=TaskStatus.IN_PROGRESS,
            cognitive_triad=CognitiveTriad(
                picture="父任务",
                requirements=[],
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[TodoItem(text="完成子任务", done=True)],
        )
        subtask = TaskManifest(
            id="subtask_1",
            status=TaskStatus.CREATED,  # Not completed
            cognitive_triad=CognitiveTriad(
                picture="子任务",
                requirements=[],
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[],
        )

        results = runner.verify_task(parent, subtasks=[subtask])

        tier1 = results[0]
        assert tier1.passed is False
        assert "还有 1 个子任务未完成" in tier1.message

    def test_tier1_passes_with_completed_subtasks(self):
        """Tier 1 passes when all subtasks are completed."""
        runner = HarnessRunner()
        parent = TaskManifest(
            id="parent_task",
            status=TaskStatus.IN_PROGRESS,
            cognitive_triad=CognitiveTriad(
                picture="父任务",
                requirements=[],
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[TodoItem(text="全部完成", done=True)],
        )
        subtask = TaskManifest(
            id="subtask_1",
            status=TaskStatus.COMPLETED,
            cognitive_triad=CognitiveTriad(
                picture="子任务",
                requirements=[],
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[TodoItem(text="已完成", done=True)],
        )

        results = runner.verify_task(parent, subtasks=[subtask])

        tier1 = results[0]
        assert tier1.passed is True

    def test_tier2_no_requirements_skips(self):
        """Tier 2 passes when no requirements defined."""
        runner = HarnessRunner()
        manifest = TaskManifest(
            id="test_task",
            status=TaskStatus.COMPLETED,
            cognitive_triad=CognitiveTriad(
                picture="简单任务",
                requirements=[],  # No requirements
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[TodoItem(text="done", done=True)],
        )

        results = runner.verify_task(manifest)

        tier2 = results[1]
        assert tier2.tier == 2
        assert tier2.passed is True
        assert "跳过" in tier2.message

    def test_tier2_descriptive_requirements_pass(self):
        """Tier 2 (MVP stub) returns passed=True with requirements listing."""
        runner = HarnessRunner()
        manifest = TaskManifest(
            id="test_task",
            status=TaskStatus.COMPLETED,
            cognitive_triad=CognitiveTriad(
                picture="测试任务",
                requirements=[
                    Requirement(id="req_01", description="测试覆盖率 > 80%", verify_cmd=None),
                    Requirement(id="req_02", description="响应时间 < 100ms", verify_cmd=None),
                ],
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[TodoItem(text="done", done=True)],
        )

        results = runner.verify_task(manifest)

        tier2 = results[1]
        assert tier2.tier == 2
        assert tier2.passed is True
        assert "2 项 requirements" in tier2.message

    def test_tier2_shell_command_success(self):
        """Tier 2 (MVP stub) with verify_cmd — returns passed=True listing stub."""
        runner = HarnessRunner()
        manifest = TaskManifest(
            id="test_task",
            status=TaskStatus.COMPLETED,
            cognitive_triad=CognitiveTriad(
                picture="测试任务",
                requirements=[
                    Requirement(id="req_01", description="shell test", verify_cmd="echo 'hello'"),
                ],
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[TodoItem(text="done", done=True)],
        )

        results = runner.verify_task(manifest)

        tier2 = results[1]
        assert tier2.tier == 2
        assert tier2.passed is True
        assert "stub" in tier2.message

    def test_tier2_shell_command_failure(self):
        """Tier 2 (MVP stub) — verify_cmd not executed, returns passed=True listing stub."""
        runner = HarnessRunner()
        manifest = TaskManifest(
            id="test_task",
            status=TaskStatus.COMPLETED,
            cognitive_triad=CognitiveTriad(
                picture="测试任务",
                requirements=[
                    Requirement(id="req_01", description="failing cmd", verify_cmd="exit 1"),
                ],
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[TodoItem(text="done", done=True)],
        )

        results = runner.verify_task(manifest)

        tier2 = results[1]
        assert tier2.tier == 2
        assert tier2.passed is True  # MVP stub: not executed, so not FAIL

    def test_tier2_mixed_requirements(self):
        """Tier 2 (MVP stub) lists all requirements with their stub status."""
        runner = HarnessRunner()
        manifest = TaskManifest(
            id="test_task",
            status=TaskStatus.COMPLETED,
            cognitive_triad=CognitiveTriad(
                picture="测试任务",
                requirements=[
                    Requirement(id="req_01", description="shell test", verify_cmd="echo 'test'"),
                    Requirement(id="req_02", description="描述性需求", verify_cmd=None),
                ],
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[TodoItem(text="done", done=True)],
        )

        results = runner.verify_task(manifest)

        tier2 = results[1]
        assert tier2.tier == 2
        assert tier2.passed is True

    def test_tier3_prepares_context_for_agent(self):
        """Tier 3 prepares judgment context for Agent to perform alignment."""
        runner = HarnessRunner()
        manifest = TaskManifest(
            id="auth_module",
            status=TaskStatus.COMPLETED,
            cognitive_triad=CognitiveTriad(
                picture="用户安全登录系统",
                requirements=[],
                constraints=["不可明文存储密码", "必须加密传输"],
            ),
            gotcha_refs=[],
            todos=[TodoItem(text="done", done=True)],
        )

        results = runner.verify_task(manifest)

        tier3 = results[2]
        assert tier3.tier == 3
        assert tier3.passed is True
        assert "请根据以下上下文自主判断是否对齐" in tier3.message
        assert "用户安全登录系统" in tier3.message
        assert "不可明文存储密码" in tier3.message

    def test_prepare_judge_context_returns_briefing(self):
        """prepare_judge_context returns structured judgment briefing."""
        from mem0ress.harness.judge import prepare_judge_context

        ctx = prepare_judge_context(
            task_id="auth_module",
            picture="用户安全登录",
            constraints=["不可明文存储密码"],
            data_plane_summary="实现了登录 API",
        )

        assert ctx.task_id == "auth_module"
        assert "用户安全登录" in ctx.reasoning
        assert "不可明文存储密码" in ctx.reasoning
        assert "实现了登录 API" in ctx.reasoning
        assert ctx.aligned is True

    def test_full_verification_all_pass(self):
        """Full verification passes when all tiers pass."""
        runner = HarnessRunner()
        manifest = TaskManifest(
            id="complete_task",
            status=TaskStatus.COMPLETED,
            cognitive_triad=CognitiveTriad(
                picture="完全完成的任务",
                requirements=[
                    Requirement(id="req_01", description="可量化指标", verify_cmd=None),
                ],
                constraints=["不可逾越的红线"],
            ),
            gotcha_refs=[],
            todos=[TodoItem(text="全部完成", done=True)],
        )

        results = runner.verify_task(manifest)

        assert runner.is_complete(results) is True
        assert all(r.passed for r in results)
        assert len(results) == 3

    def test_full_verification_fails_at_tier1(self):
        """Full verification fails if Tier 1 fails."""
        runner = HarnessRunner()
        manifest = TaskManifest(
            id="incomplete_task",
            status=TaskStatus.IN_PROGRESS,
            cognitive_triad=CognitiveTriad(
                picture="未完成任务",
                requirements=[],
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[TodoItem(text="未完成项", done=False)],
        )

        results = runner.verify_task(manifest)

        assert runner.is_complete(results) is False
        tier1 = results[0]
        assert tier1.passed is False

    def test_multi_subtask_scenario(self):
        """Test with multiple subtasks in various states."""
        runner = HarnessRunner()
        parent = TaskManifest(
            id="auth_module",
            status=TaskStatus.IN_PROGRESS,
            cognitive_triad=CognitiveTriad(
                picture="用户认证模块",
                requirements=[
                    Requirement(id="req_01", description="支持 OAuth", verify_cmd=None),
                ],
                constraints=[],
            ),
            gotcha_refs=[],
            todos=[TodoItem(text="协调子任务", done=True)],
        )
        subtasks = [
            TaskManifest(
                id="auth_api",
                status=TaskStatus.COMPLETED,
                cognitive_triad=CognitiveTriad(picture="", requirements=[], constraints=[]),
                gotcha_refs=[],
                todos=[TodoItem(text="done", done=True)],
            ),
            TaskManifest(
                id="auth_middleware",
                status=TaskStatus.IN_PROGRESS,
                cognitive_triad=CognitiveTriad(picture="", requirements=[], constraints=[]),
                gotcha_refs=[],
                todos=[TodoItem(text="not done", done=False)],
            ),
        ]

        results = runner.verify_task(parent, subtasks=subtasks)

        # Should fail at tier 1 because auth_middleware is not completed
        assert runner.is_complete(results) is False
        tier1 = results[0]
        assert tier1.passed is False
        assert "auth_middleware" in tier1.message