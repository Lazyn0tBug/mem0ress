"""Tests for TaskServiceImpl."""


import pytest

from mem0ress.core.schema import TaskManifest, TaskStatus, TodoItem
from mem0ress.service.impl.task_service import TaskExistsError, TaskServiceImpl
from mem0ress.storage.fs import ConflictError, get_file_hash, safe_write
from mem0ress.storage.parser import SubstrateParser


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
        assert (tmp_path / "tasks" / "auth_module" / "index.md").exists()
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

        index_path = tmp_path / "tasks" / "auth_module" / "index.md"
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
            requirements=["响应 < 100ms"],
            constraints=["不可明文存储密码"],
        )

        assert updated.cognitive_triad.picture == "用户安全登录"
        assert updated.cognitive_triad.requirements == ["响应 < 100ms"]
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