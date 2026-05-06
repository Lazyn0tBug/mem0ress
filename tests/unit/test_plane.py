"""Tests for PlaneAssembler."""

from mem0ress.plane import PlaneAssembler
from mem0ress.service.impl.task_service import TaskServiceImpl


class TestPlaneAssembler:
    """Test PlaneAssembler."""

    def test_compile_status_plane_empty(self, tmp_path):
        """Test compile_status_plane with no tasks."""
        assembler = PlaneAssembler(substrate_root=tmp_path)

        result = assembler.compile_status_plane()

        assert "# Status Plane (当前态势感知)" in result
        assert "(无活动任务)" in result
        assert "系统法则：" in result
        assert "你不可撤销状态，只能覆写向前。" in result

    def test_compile_status_plane_single_task(self, tmp_path):
        """Test compile_status_plane with a single task."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        assembler = PlaneAssembler(substrate_root=tmp_path)
        result = assembler.compile_status_plane()

        assert "# Status Plane (当前态势感知)" in result
        assert "■ Task ID: auth_module [CREATED]" in result
        assert "目标图景: 用户顺畅登录" in result

    def test_compile_status_plane_with_todos(self, tmp_path):
        """Test compile_status_plane shows todo progress."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")
        service.update_todo("auth_module", 0, True)

        assembler = PlaneAssembler(substrate_root=tmp_path)
        result = assembler.compile_status_plane()

        assert "1/1 Todos 完成" in result

    def test_compile_status_plane_ref_pointer(self, tmp_path):
        """Test compile_status_plane handles ref: prefix in picture."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        # Update cognitive triad with ref: prefix
        service.update_cognitive_triad(
            "auth_module",
            "ref:parent_task#picture",
            requirements=[],
            constraints=[],
        )

        assembler = PlaneAssembler(substrate_root=tmp_path)
        result = assembler.compile_status_plane()

        assert "[脱水指针: parent_task#picture]" in result

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

        # The subtask should appear indented under auth_module
        assert "■ Task ID: auth_module [CREATED]" in result
        assert "■ Task ID: auth_middleware [CREATED]" in result

    def test_system_laws_appended(self, tmp_path):
        """Test system laws are always appended."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        assembler = PlaneAssembler(substrate_root=tmp_path)
        result = assembler.compile_status_plane()

        assert "系统法则：" in result
        assert "你不可撤销状态，只能覆写向前。" in result
        assert "任何父级 Task 的完成，必须以其所有子层级 Task 完成为绝对前提。" in result