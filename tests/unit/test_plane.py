"""Tests for PlaneAssembler."""

from mem0ress.plane import PlaneAssembler
from mem0ress.service.impl.task_service import TaskServiceImpl


class TestPlaneAssembler:
    """Test PlaneAssembler - status plane showing current state only."""

    def test_compile_status_plane_empty(self, tmp_path):
        """Test compile_status_plane with no tasks."""
        assembler = PlaneAssembler(substrate_root=tmp_path)

        result = assembler.compile_status_plane()
        rendered = result.render()

        assert "# Status Plane" in rendered
        assert "(no active tasks)" in rendered
        assert "系统法则" in rendered

    def test_compile_status_plane_single_task(self, tmp_path):
        """Test compile_status_plane shows task ID, todos progress, and status."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        assembler = PlaneAssembler(substrate_root=tmp_path)
        result = assembler.compile_status_plane()
        rendered = result.render()

        assert "# Status Plane" in rendered
        assert "■ auth_module [0/1] CREATED" in rendered

    def test_compile_status_plane_with_todos(self, tmp_path):
        """Test compile_status_plane shows todo progress."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")
        service.update_todo("auth_module", 0, True)

        assembler = PlaneAssembler(substrate_root=tmp_path)
        result = assembler.compile_status_plane()
        rendered = result.render()

        assert "■ auth_module [1/1] CREATED" in rendered

    def test_compile_status_plane_with_gotcha(self, tmp_path):
        """Test compile_status_plane shows gotcha_refs."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        # Simulate adding a gotcha - use proper YAML format matching serialize_manifest
        # Note: todos go in body, NOT in frontmatter
        index_path = tmp_path / "tasks" / "auth_module" / "index.md"
        index_path.write_text(
            "---\n"
            "id: auth_module\n"
            "type: task\n"
            "status: in-progress\n"
            "cognitive_triad:\n"
            "  picture: 用户顺畅登录\n"
            "  requirements: []\n"
            "  constraints: []\n"
            "gotcha_refs:\n"
            "- 偏离：密码使用 MD5\n"
            "---\n\n"
            "- [x] 步骤1\n",
            encoding="utf-8",
        )

        assembler = PlaneAssembler(substrate_root=tmp_path)
        result = assembler.compile_status_plane()
        rendered = result.render()

        assert "■ auth_module [1/1] IN-PROGRESS" in rendered
        assert "! 偏离：密码使用 MD5" in rendered

    def test_compile_status_plane_no_picture(self, tmp_path):
        """Test compile_status_plane does NOT show picture (it's a goal, not state)."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        assembler = PlaneAssembler(substrate_root=tmp_path)
        result = assembler.compile_status_plane()
        rendered = result.render()

        # Picture should NOT appear in status plane
        assert "目标图景" not in rendered
        assert "用户顺畅登录" not in rendered
        # But task ID should appear
        assert "auth_module" in rendered

    def test_compile_status_plane_with_subtasks(self, tmp_path):
        """Test compile_status_plane shows subtasks indented."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")
        service.create_task("auth_middleware", "实现拦截器")

        # Create subtask under auth_module
        subtask_dir = tmp_path / "tasks" / "auth_module" / "auth_middleware"
        subtask_dir.mkdir(parents=True, exist_ok=True)
        (subtask_dir / "references").mkdir(exist_ok=True)
        index_path = subtask_dir / "index.md"
        index_path.write_text(
            "---\n"
            "id: auth_middleware\n"
            "type: task\n"
            "status: created\n"
            "cognitive_triad:\n"
            "  picture: 实现跨域拦截器\n"
            "  requirements: []\n"
            "  constraints: []\n"
            "gotcha_refs: []\n"
            "todos: []\n"
            "---\n\n"
            "- [ ] 子任务步骤",
            encoding="utf-8",
        )

        assembler = PlaneAssembler(substrate_root=tmp_path)
        result = assembler.compile_status_plane()
        rendered = result.render()

        # Both tasks should appear
        assert "■ auth_module" in rendered
        assert "■ auth_middleware" in rendered
        # Subtask should be indented under parent
        assert "  ■ auth_middleware" in rendered

    def test_system_laws_appended(self, tmp_path):
        """Test system laws are always appended."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        assembler = PlaneAssembler(substrate_root=tmp_path)
        result = assembler.compile_status_plane()
        rendered = result.render()

        assert "系统法则" in rendered
        assert "你不可撤销状态，只能覆写向前" in rendered
        assert "任何父级 Task 的完成" in rendered