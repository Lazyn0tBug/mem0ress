"""SubstrateParser - YAML frontmatter and markdown parsing."""

import re
from pathlib import Path

import yaml

from mem0ress.core.schema import (
    CognitiveTriad,
    TaskManifest,
    TaskStatus,
    TodoItem,
)

FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TODO_PATTERN = re.compile(r"^-\s*\[([ xX])\]\s*(.*)$", re.MULTILINE)


class SubstrateParser:
    """认知基座解析器：负责 Manifest (index.md) 与内存模型的双向转换."""

    @staticmethod
    def parse_manifest(file_path: Path) -> TaskManifest:
        """读取 Markdown 文件并解析为 TaskManifest 模型.

        id 字段始终以目录名为准（文件系统是 source of truth）。
        """
        content = file_path.read_text(encoding="utf-8")

        # 1. 分离 YAML Frontmatter 和正文
        match = FRONTMATTER_PATTERN.match(content)
        if not match:
            raise ValueError(f"文件 {file_path} 格式非法：未找到标准的 YAML Frontmatter")

        frontmatter_raw = match.group(1)
        body = content[match.end() :]

        data = yaml.safe_load(frontmatter_raw)
        if not isinstance(data, dict):
            raise ValueError(f"文件 {file_path} 的 YAML Frontmatter 必须是字典")

        # 2. 解析正文中的 Todo
        todos = []
        for line in body.split("\n"):
            todo_match = TODO_PATTERN.match(line.strip())
            if todo_match:
                is_done = todo_match.group(1).lower() == "x"
                todos.append(TodoItem(text=todo_match.group(2).strip(), done=is_done))

        # 3. 构造 Pydantic 模型
        triad_data = data.get("cognitive_triad", {})
        task_id = file_path.parent.name  # filesystem is source of truth

        return TaskManifest(
            id=task_id,
            type=data.get("type", "task"),
            status=TaskStatus(data.get("status", "created")),
            cognitive_triad=CognitiveTriad(
                picture=triad_data.get("picture", ""),
                requirements=triad_data.get("requirements", []),
                constraints=triad_data.get("constraints", []),
            ),
            gotcha_refs=data.get("gotcha_refs", []),
            todos=todos,
        )

    @staticmethod
    def serialize_manifest(manifest: TaskManifest, file_path: Path) -> str:
        """将内存模型序列化回 Markdown 文本 (用于绝对覆写).

        id 始终设为目录名（filesystem is source of truth）。
        """
        # 1. 构建 YAML 部分
        frontmatter = {
            "id": file_path.parent.name,  # filesystem is source of truth
            "type": manifest.type,
            "status": manifest.status.value,
            "cognitive_triad": manifest.cognitive_triad.model_dump(),
            "gotcha_refs": manifest.gotcha_refs,
        }

        yaml_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)

        # 2. 构建 Body 部分 (Todo 列表)
        todo_lines = []
        for item in manifest.todos:
            mark = "x" if item.done else " "
            todo_lines.append(f"- [{mark}] {item.text}")

        body_str = "\n".join(todo_lines)

        return f"---\n{yaml_str}---\n\n# Todos\n{body_str}\n"

    @staticmethod
    def parse_todos_from_body(body: str) -> list[TodoItem]:
        """从 markdown body 中解析 todo 列表."""
        todos = []
        for line in body.split("\n"):
            todo_match = TODO_PATTERN.match(line.strip())
            if todo_match:
                is_done = todo_match.group(1).lower() == "x"
                todos.append(TodoItem(text=todo_match.group(2).strip(), done=is_done))
        return todos
