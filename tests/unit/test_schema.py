"""Tests for core schema models."""

from mem0ress.core.schema import (
    CognitiveTriad,
    Gotcha,
    TaskManifest,
    TaskStatus,
    TodoItem,
)


class TestTaskStatus:
    """Test TaskStatus enum."""

    def test_all_values_present(self):
        assert TaskStatus.CREATED.value == "created"
        assert TaskStatus.IN_PROGRESS.value == "in-progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.ABANDONED.value == "abandoned"
        assert len(TaskStatus) == 4


class TestCognitiveTriad:
    """Test CognitiveTriad model."""

    def test_valid_model(self):
        triad = CognitiveTriad(
            picture="用户能顺畅登录",
            requirements=["响应 < 200ms"],
            constraints=["不可明文存储密码"],
        )
        assert triad.picture == "用户能顺畅登录"
        assert triad.requirements == ["响应 < 200ms"]
        assert triad.constraints == ["不可明文存储密码"]

    def test_empty_lists(self):
        triad = CognitiveTriad(picture="简单任务")
        assert triad.requirements == []
        assert triad.constraints == []


class TestTodoItem:
    """Test TodoItem model."""

    def test_default_not_done(self):
        item = TodoItem(text="实现登录 API")
        assert item.done is False

    def test_done_true(self):
        item = TodoItem(text="实现登录 API", done=True)
        assert item.done is True


class TestTaskManifest:
    """Test TaskManifest model."""

    def test_valid_manifest(self):
        manifest = TaskManifest(
            id="auth_module",
            cognitive_triad=CognitiveTriad(picture="用户顺畅登录"),
            todos=[TodoItem(text="实现 API", done=True)],
        )
        assert manifest.id == "auth_module"
        assert manifest.status == TaskStatus.CREATED

    def test_all_status_values(self):
        statuses = [
            (TaskStatus.CREATED, "created"),
            (TaskStatus.IN_PROGRESS, "in-progress"),
            (TaskStatus.COMPLETED, "completed"),
            (TaskStatus.ABANDONED, "abandoned"),
        ]
        for status, expected in statuses:
            manifest = TaskManifest(
                id="test",
                status=status,
                cognitive_triad=CognitiveTriad(picture="test"),
            )
            assert manifest.status.value == expected


class TestGotcha:
    """Test Gotcha model."""

    def test_valid_gotcha(self):
        gotcha = Gotcha(
            id="cors_decision",
            task_id="auth_module",
            timestamp="2026-05-05T10:00:00Z",
            content="不要在每个路由单独配跨域",
        )
        assert gotcha.id == "cors_decision"
        assert gotcha.task_id == "auth_module"
        assert gotcha.type == "gotcha"

    def test_related_task_optional(self):
        gotcha = Gotcha(
            id="test",
            task_id="auth",
            timestamp="2026-05-05",
            content="test content",
        )
        assert gotcha.related_task is None