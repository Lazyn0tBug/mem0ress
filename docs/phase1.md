# Phase 1: 系统骨架与核心数据契约实现

我们将使用 uv 初始化项目，并基于 Pydantic 定义最核心的认知属性模型。这是认知内核 (Cognitive Kernel) 能够理解世界的基础。

## 1.1 pyproject.toml 配置

```toml
[project]
name = "mem0ress"
version = "0.1.0"
description = "A text-based cognitive OS kernel based on situational awareness."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "typer>=0.12.3",
    "pydantic>=2.7.0",
    "pyyaml>=6.0.1",
    "litellm>=1.35.0",
    "gitpython>=3.1.43",
    "rich>=13.7.1",
]

[project.scripts]
mem0 = "mem0ress.cli:app"

[tool.ruff]
line-length = 100
target-version = "py312"
```

## 1.2 核心 Schema 设计 (src/mem0ress/core/schema.py)

我们将“认知三要素”和“任务属性”固化为强类型模型。

```python
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class CognitiveTriad(BaseModel):
    """认知三要素：系统对任务的最高级约束"""
    picture: str = Field(..., description="图景：任务完成后的终极语义描述")
    requirements: List[str] = Field(default_factory=list, description="需求：客观、可量化的指标或验证脚本")
    constraints: List[str] = Field(default_factory=list, description="约束：执行过程中不可逾越的红线")

class TodoItem(BaseModel):
    """执行步伐"""
    text: str
    done: bool = False

class TaskManifest(BaseModel):
    """任务声明式清单 (index.md 的内存映射)"""
    id: str
    type: str = "manifest"
    status: TaskStatus = TaskStatus.CREATED
    cognitive_triad: CognitiveTriad
    gotcha_refs: List[str] = Field(default_factory=list)
    todos: List[TodoItem] = Field(default_factory=list)

class Gotcha(BaseModel):
    """认知增量 (gotcha.md 的内存映射)"""
    id: str
    type: str = "gotcha"
    timestamp: str
    related_task: Optional[str] = None
    content: str # 认知增量的核心文本
```

## 1.3 实现认知基座解析器 (Substrate Parser)

我们现在开始编写代码。这个模块的任务是：将 认知基座 (Cognitive Substrate) 上的物理 Markdown 文件，“水化”成内存中的 Pydantic 模型。

我们将使用 python-frontmatter（或简单的正则）来处理 YAML 和 Markdown 的分离。

1. 核心解析逻辑 (src/mem0ress/storage/parser.py)

```python
import yaml
import re
from pathlib import Path
from typing import Tuple, Dict, Any
from mem0ress.core.schema import TaskManifest, TaskStatus, CognitiveTriad, TodoItem

class SubstrateParser:
    """
    认知基座解析器：负责 Manifest (index.md) 与内存模型的双向转换。
    """

    @staticmethod
    def parse_manifest(file_path: Path) -> TaskManifest:
        """读取 Markdown 文件并解析为 TaskManifest 模型"""
        content = file_path.read_text(encoding="utf-8")
        
        # 1. 分离 YAML Frontmatter 和正文
        # 匹配模式: --- (YAML) --- (Markdown Body)
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if not match:
            raise ValueError(f"文件 {file_path} 格式非法：未找到标准的 YAML Frontmatter")
        
        frontmatter_raw, body = match.groups()
        data = yaml.safe_load(frontmatter_raw)
        
        # 2. 解析正文中的 Todo (状态平面核心)
        # 匹配模式: - [x] text 或 - [ ] text
        todos = []
        todo_matches = re.finditer(r'-\s*\[([ xX])\]\s*(.*)', body)
        for m in todo_matches:
            is_done = m.group(1).lower() == 'x'
            todos.append(TodoItem(text=m.group(2).strip(), done=is_done))

        # 3. 构造 Pydantic 模型
        # 注意：此处处理了认知三要素的解构
        triad_data = data.get("cognitive_triad", {})
        
        return TaskManifest(
            id=data.get("id", file_path.parent.name),
            status=TaskStatus(data.get("status", "created")),
            cognitive_triad=CognitiveTriad(
                picture=triad_data.get("picture", ""),
                requirements=triad_data.get("requirements", []),
                constraints=triad_data.get("constraints", [])
            ),
            gotcha_refs=data.get("gotcha_refs", []),
            todos=todos
        )

    @staticmethod
    def serialize_manifest(manifest: TaskManifest) -> str:
        """将内存模型序列化回 Markdown 文本 (用于绝对覆写)"""
        # 1. 构建 YAML 部分
        frontmatter = {
            "id": manifest.id,
            "type": manifest.type,
            "status": manifest.status.value,
            "cognitive_triad": manifest.cognitive_triad.model_dump(),
            "gotcha_refs": manifest.gotcha_refs
        }
        
        yaml_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
        
        # 2. 构建 Body 部分 (Todo 列表)
        todo_lines = []
        for item in manifest.todos:
            mark = "x" if item.done else " "
            todo_lines.append(f"- [{mark}] {item.text}")
        
        body_str = "\n".join(todo_lines)
        
        return f"---\n{yaml_str}---\n\n# Todos\n{body_str}"
```

### 1.4 实现态势平面组装器 (Plane Assembler)

基于你的洞见，我们现在来实现 认知内核 (Cognitive Kernel) 的大脑投影仪：PlaneAssembler。

它的工作是遍历 Cognitive Substrate（认知基座，即目录树），利用刚才写的 SubstrateParser 读取内存模型，并编译出一份带有“依赖缩进”的 状态平面 (Status Plane) 纯文本，喂给大模型。

核心代码 (src/mem0ress/core/plane.py)

```python
from pathlib import Path
from typing import List, Dict
from mem0ress.storage.parser import SubstrateParser
from mem0ress.core.schema import TaskStatus

class PlaneAssembler:
    """
    平面组装器：负责将物理拓扑结构投影为 Agent 的态势感知。
    """
    def __init__(self, substrate_root: Path):
        self.substrate_root = substrate_root
        # 例如: .mem0ress/tasks/
        self.tasks_dir = self.substrate_root / "tasks"

    def compile_status_plane(self) -> str:
        """
        编译状态平面：扫描基座，生成带有物理深度（依赖关系）的全局视野。
        """
        if not self.tasks_dir.exists():
            return "[Status Plane] 当前基座为空，没有活跃的认知任务。"

        lines = ["# Status Plane (当前态势感知)", ""]
        
        # 1. 获取所有 index.md (Manifest) 并按路径排序 (利用路径排序天然形成树状)
        manifest_files = sorted(self.tasks_dir.rglob("index.md"))
        
        # 2. 遍历并投影
        for file_path in manifest_files:
            # 计算深度：通过计算相对于 tasks_dir 的相对路径层级
            rel_path = file_path.relative_to(self.tasks_dir)
            # 目录深度，减 1 是因为最后是 index.md
            depth = len(rel_path.parts) - 1 
            
            # 解析基座文件为内存模型
            manifest = SubstrateParser.parse_manifest(file_path)
            
            # 生成缩进
            indent = "  " * depth
            prefix = "└─ " if depth > 0 else "■ "
            
            # 处理图景 (判断是否脱水/水化)
            pic_summary = manifest.cognitive_triad.picture
            if pic_summary.startswith("ref:"):
                pic_summary = f"[脱水指针] 需调用 resolve_reference('{pic_summary}') 水化读取"
            else:
                # 截断长文本，保持状态平面轻量
                pic_summary = pic_summary[:50] + ("..." if len(pic_summary) > 50 else "")

            # 组装 Task 摘要
            lines.append(f"{indent}{prefix}Task ID: {manifest.id} [{manifest.status.value.upper()}]")
            lines.append(f"{indent}   目标图景: {pic_summary}")
            
            # 组装 Todo 进度 (机械步)
            done_count = sum(1 for t in manifest.todos if t.done)
            total_count = len(manifest.todos)
            lines.append(f"{indent}   进度: {done_count}/{total_count} Todos 完成")
            
            # 明确告知大模型依赖规则
            if depth > 0:
                parent_dir_name = rel_path.parts[-3] if len(rel_path.parts) >= 3 else rel_path.parts[0]
                lines.append(f"{indent}   [约束]: 这是 {parent_dir_name} 的子任务，必须优先完成。")
            
            lines.append("") # 空行分隔

        # 增加全局系统级提示
        lines.append("---")
        lines.append("系统法则：")
        lines.append("1. 你不可撤销状态，只能覆写向前。")
        lines.append("2. 任何父级 Task 的完成，必须以其所有子层级 Task 完成为绝对前提。")

        return "\n".join(lines)
```

运行结果演示
如果 Agent 此时醒来，`compile_status_plane()`会给它投射这样一份极度清晰的状态平面：

````markdown
# Status Plane (当前态势感知)

■ Task ID: auth_module [IN-PROGRESS]
   目标图景: [脱水指针] 需调用 resolve_reference('ref:docs/auth_vision.md') 水化读取
   进度: 1/2 Todos 完成

  └─ Task ID: auth_middleware [CREATED]
     目标图景: 实现跨域与 Token 验签拦截器
     进度: 0/3 Todos 完成
     [约束]: 这是 auth_module 的子任务，必须优先完成。

---
系统法则：
1. 你不可撤销状态，只能覆写向前。
2. 任何父级 Task 的完成，必须以其所有子层级 Task 完成为绝对前提。
````
