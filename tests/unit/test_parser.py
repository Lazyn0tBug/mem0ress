"""Tests for SubstrateParser."""


import pytest

from mem0ress.core.schema import CognitiveTriad, TaskStatus, TodoItem
from mem0ress.substrate.parser import SubstrateParser


class TestSubstrateParser:
    """Test SubstrateParser."""

    def test_parse_valid_manifest(self, tmp_path):
        # Create a test file
        task_dir = tmp_path / "auth_module"
        task_dir.mkdir()
        index_path = task_dir / "index.md"
        index_path.write_text(
            """---
id: auth_module
type: task
status: in-progress
cognitive_triad:
  picture: 用户顺畅登录
  requirements:
  - 响应 < 200ms
  constraints:
  - 不可明文存储密码
gotcha_refs: []
---

# Todos
- [x] 实现基础登录 API
- [ ] 编写 Auth 守卫中间件
""",
            encoding="utf-8",
        )

        manifest = SubstrateParser.parse_manifest(index_path)

        assert manifest.id == "auth_module"
        assert manifest.status == TaskStatus.IN_PROGRESS
        assert manifest.cognitive_triad.picture == "用户顺畅登录"
        assert len(manifest.todos) == 2
        assert manifest.todos[0].done is True
        assert manifest.todos[0].text == "实现基础登录 API"
        assert manifest.todos[1].done is False

    def test_parse_uppercase_x(self, tmp_path):
        task_dir = tmp_path / "test_task"
        task_dir.mkdir()
        index_path = task_dir / "index.md"
        index_path.write_text(
            """---
id: test_task
type: task
status: created
cognitive_triad:
  picture: test
  requirements: []
  constraints: []
gotcha_refs: []
---

# Todos
- [X] 完成这项任务
""",
            encoding="utf-8",
        )

        manifest = SubstrateParser.parse_manifest(index_path)
        assert manifest.todos[0].done is True

    def test_parse_whitespace_in_todo(self, tmp_path):
        task_dir = tmp_path / "test_task"
        task_dir.mkdir()
        index_path = task_dir / "index.md"
        index_path.write_text(
            """---
id: test_task
type: task
status: created
cognitive_triad:
  picture: test
  requirements: []
  constraints: []
gotcha_refs: []
---

# Todos
- [x]   带多余空格的任务
""",
            encoding="utf-8",
        )

        manifest = SubstrateParser.parse_manifest(index_path)
        assert manifest.todos[0].text == "带多余空格的任务"

    def test_parse_no_frontmatter_raises(self, tmp_path):
        index_path = tmp_path / "no_frontmatter.md"
        index_path.write_text("No frontmatter here", encoding="utf-8")

        with pytest.raises(ValueError, match="未找到标准的 YAML Frontmatter"):
            SubstrateParser.parse_manifest(index_path)

    def test_serialize_manifest_roundtrip(self, tmp_path):
        from mem0ress.core.schema import TaskManifest

        task_dir = tmp_path / "auth_module"
        task_dir.mkdir()
        index_path = task_dir / "index.md"

        manifest = TaskManifest(
            id="auth_module",
            status=TaskStatus.IN_PROGRESS,
            cognitive_triad=CognitiveTriad(
                picture="用户顺畅登录",
                requirements=["响应 < 200ms"],
                constraints=["不可明文存储密码"],
            ),
            gotcha_refs=[],
            todos=[
                TodoItem(text="实现基础登录 API", done=True),
                TodoItem(text="编写 Auth 守卫中间件", done=False),
            ],
        )

        serialized = SubstrateParser.serialize_manifest(manifest, index_path)

        # Verify it's valid frontmatter
        assert serialized.startswith("---\n")
        assert "id: auth_module" in serialized
        assert "status: in-progress" in serialized
        assert "- [x] 实现基础登录 API" in serialized
        assert "- [ ] 编写 Auth 守卫中间件" in serialized

        # Round-trip test
        index_path.write_text(serialized, encoding="utf-8")
        reparsed = SubstrateParser.parse_manifest(index_path)
        assert reparsed.id == manifest.id
        assert reparsed.status == manifest.status
        assert len(reparsed.todos) == len(manifest.todos)