"""Tests for TaskServiceImpl."""


import pytest

from mem0ress.core.schema import Requirement, TaskManifest, TaskStatus, TodoItem
from mem0ress.gateway.actions import TaskExistsError, TaskServiceImpl
from mem0ress.substrate.fs import ConflictError, get_file_hash, safe_write
from mem0ress.substrate.parser import SubstrateParser


class TestTaskServiceImpl:
    """Test TaskServiceImpl."""

    def test_create_task(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)
        manifest = service.create_task("auth_module", "用户顺畅登录")

        assert manifest.id == "auth_module"
        assert manifest.cognitive_triad.picture == "用户顺畅登录"
        assert manifest.status == TaskStatus.CREATED
        assert len(manifest.todos) == 1

        # Verify directory structure
        assert (tmp_path / "tasks" / "auth_module" / "task.md").exists()
        assert (tmp_path / "tasks" / "auth_module" / "references").is_dir()

    def test_create_task_duplicate_raises(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        with pytest.raises(TaskExistsError):
            service.create_task("auth_module", "另一个图景")

    def test_get_task(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)
        created = service.create_task("auth_module", "用户顺畅登录")
        retrieved = service.get_task("auth_module")

        assert retrieved.id == created.id
        assert retrieved.cognitive_triad.picture == created.cognitive_triad.picture

    def test_get_task_not_exists_raises(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)

        with pytest.raises(FileNotFoundError):
            service.get_task("nonexistent")

    def test_update_todo(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        updated = service.update_todo("auth_module", 0, True)

        assert updated.todos[0].done is True

    def test_update_todo_index_out_of_range_raises(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        with pytest.raises(IndexError):
            service.update_todo("auth_module", 99, True)

    def test_update_todo_nonexistent_task_raises(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)

        with pytest.raises(FileNotFoundError):
            service.update_todo("nonexistent", 0, True)

    def test_update_todo_optimistic_lock(self, tmp_path):
        """Test that file modification between reads is detected.

        This tests the scenario where the file changes after we read it but before
        we write. We simulate by manually modifying the file after the initial read.
        """
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        index_path = tmp_path / "tasks" / "auth_module" / "task.md"
        original_hash = get_file_hash(index_path)

        # Simulate external modification - write a different version with a todo
        # Note: todos are parsed from markdown body, not from YAML frontmatter
        index_path.write_text(
            "---\nid: auth_module\ntype: task\nstatus: completed\n"
            "cognitive_triad:\n  picture: 用户顺畅登录\n  requirements: []\n  constraints: []\n"
            "gotcha_refs: []\ntodos: []\n---\n\n- [ ] 已被外部修改",
            encoding="utf-8",
        )

        # Now try to update with the old hash - should fail
        manifest = SubstrateParser.parse_manifest(index_path)
        new_todos = [TodoItem(text=manifest.todos[0].text, done=True)]

        updated_manifest = TaskManifest(
            id=manifest.id,
            type=manifest.type,
            status=manifest.status,
            cognitive_triad=manifest.cognitive_triad,
            gotcha_refs=manifest.gotcha_refs,
            todos=new_todos,
        )

        content = SubstrateParser.serialize_manifest(updated_manifest, index_path)
        with pytest.raises(ConflictError):
            safe_write(index_path, content, original_hash)

    def test_update_cognitive_triad(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        updated = service.update_cognitive_triad(
            "auth_module",
            "用户安全登录",
            requirements=[
                Requirement(id="req_01", description="响应 < 100ms", verify_cmd=None),
            ],
            constraints=["不可明文存储密码"],
        )

        assert updated.cognitive_triad.picture == "用户安全登录"
        assert updated.cognitive_triad.requirements[0].id == "req_01"
        assert updated.cognitive_triad.requirements[0].description == "响应 < 100ms"
        assert updated.cognitive_triad.constraints == ["不可明文存储密码"]

    def test_get_all_tasks(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("task1", "图景1")
        service.create_task("task2", "图景2")

        tasks = service.get_all_tasks()

        assert len(tasks) == 2

    def test_get_all_tasks_empty(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)

        tasks = service.get_all_tasks()

        assert tasks == []

    def test_delete_task(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        service.delete_task("auth_module")

        assert not (tmp_path / "tasks" / "auth_module").exists()

    def test_delete_task_not_exists_raises(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)

        with pytest.raises(FileNotFoundError):
            service.delete_task("nonexistent")

    def test_add_todo(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        updated = service.add_todo("auth_module", "新任务")

        assert len(updated.todos) == 2
        assert updated.todos[1].text == "新任务"
        assert updated.todos[1].done is False

    def test_add_todo_nonexistent_raises(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)

        with pytest.raises(FileNotFoundError):
            service.add_todo("nonexistent", "新任务")

    def test_remove_todo(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        updated = service.remove_todo("auth_module", 0)

        assert len(updated.todos) == 0

    def test_remove_todo_index_out_of_range_raises(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        with pytest.raises(IndexError):
            service.remove_todo("auth_module", 99)

    def test_remove_todo_nonexistent_raises(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)

        with pytest.raises(FileNotFoundError):
            service.remove_todo("nonexistent", 0)

    def test_complete_task(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        updated = service.complete_task("auth_module")

        assert updated.status == TaskStatus.COMPLETED
        # Verify persistence
        retrieved = service.get_task("auth_module")
        assert retrieved.status == TaskStatus.COMPLETED

    def test_complete_task_nonexistent_raises(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)

        with pytest.raises(FileNotFoundError):
            service.complete_task("nonexistent")

    def test_abandon_task(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        updated = service.abandon_task("auth_module")

        assert updated.status == TaskStatus.ABANDONED
        # Verify persistence
        retrieved = service.get_task("auth_module")
        assert retrieved.status == TaskStatus.ABANDONED

    def test_abandon_task_nonexistent_raises(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)

        with pytest.raises(FileNotFoundError):
            service.abandon_task("nonexistent")

    def test_update_session(self, tmp_path):
        """update_session appends a turn marker to session.md with correct format."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        service.update_session("auth_module", "完成了登录流程")

        session_path = tmp_path / "tasks" / "auth_module" / "session.md"
        assert session_path.exists()
        content = session_path.read_text(encoding="utf-8")
        assert "## Turn 1 @" in content
        assert "完成了登录流程" in content

    def test_update_session_increments_turn_counter(self, tmp_path):
        """Multiple calls increment the turn counter."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        service.update_session("auth_module", "turn 1")
        service.update_session("auth_module", "turn 2")

        session_path = tmp_path / "tasks" / "auth_module" / "session.md"
        content = session_path.read_text(encoding="utf-8")
        assert "## Turn 1 @" in content
        assert "## Turn 2 @" in content

    def test_update_session_nonexistent_raises(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)

        with pytest.raises(FileNotFoundError):
            service.update_session("nonexistent", "content")

    def test_judge_task_writes_judge_report(self, tmp_path):
        """judge_task runs verification and writes results to judge.md."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        results = service.judge_task("auth_module")

        assert len(results) == 3  # Tier 1, 2, 3
        judge_path = tmp_path / "tasks" / "auth_module" / "judge.md"
        assert judge_path.exists()
        content = judge_path.read_text(encoding="utf-8")
        assert "# Judge Report — auth_module" in content

    def test_judge_task_nonexistent_raises(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)

        with pytest.raises(FileNotFoundError):
            service.judge_task("nonexistent")

    def test_close_task_succeeds_when_all_tiers_pass(self, tmp_path):
        """close_task marks COMPLETED when all tiers pass."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        # Complete the default todo so Tier 1 passes
        service.update_todo("auth_module", 0, True)

        manifest = service.close_task("auth_module")
        assert manifest.status == TaskStatus.COMPLETED

    def test_close_task_raises_when_tier1_fails(self, tmp_path):
        """close_task raises RuntimeError when Tier 1 (todo) check fails."""
        service = TaskServiceImpl(substrate_root=tmp_path)
        service.create_task("auth_module", "用户顺畅登录")

        # Leave the default todo incomplete — Tier 1 must fail
        with pytest.raises(RuntimeError) as exc_info:
            service.close_task("auth_module")
        assert "Tier 1" in str(exc_info.value)

    def test_close_task_nonexistent_raises(self, tmp_path):
        service = TaskServiceImpl(substrate_root=tmp_path)

        with pytest.raises(FileNotFoundError):
            service.close_task("nonexistent")