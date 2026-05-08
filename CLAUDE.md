# mem0ress - 认知对齐平面 SDK

## 项目概述

mem0ress 是一个面向 AI Agent 开发者的认知对齐平面（Cognitive Alignment Plane）SDK。它以轻量级生命周期钩子的形式注入 Agent 执行循环，提供任务状态管理与目标态势感知能力。

**技术栈**: Python 3.12+ + uv + ruff + ty + Pydantic

**核心模块**: Plane Assembler（状态平面组装器）/ Tool Interface（工具接口）/ Harness Engine（约束检验引擎）/ 任务完成度检查（Tier 1-3）

**文档依赖**:
- `docs/spec.md` — 接口语义规范（做什么）
- `docs/arch.md` — 实现架构文档（如何做）
- `docs/design.md` — 实施方案与开发日志

## 项目结构

```
mem0ress/
├── src/
│   └── mem0ress/
│       ├── cli.py           # CLI 入口，终端态势可视化
│       ├── core/
│       │   └── schema.py    # Pydantic 模型（PRC 三要素、Task、Session）
│       ├── gateway/         # 认知网关
│       │   ├── intercept.py  # CognitiveContext 上下文管理器
│       │   ├── plane.py     # Plane Assembler（状态平面组装）
│       │   └── actions.py   # Tool Interface（写入指令集）
│       ├── substrate/       # 认知基座操作
│       │   ├── fs.py        # Markdown/YAML ↔ Pydantic 双向解析
│       │   └── git_ops.py   # Git 固化、Data Plane commit ID 管理
│       └── harness/         # 检验引擎（Tier 0-3）
│           ├── runner.py    # Tier 1/2 机械检查
│           └── judge.py     # Tier 3 语义裁决器（LLM）
├── tests/                   # 测试文件
├── docs/
│   ├── spec.md              # 接口语义规范
│   ├── arch.md              # 实现架构
│   └── design.md            # 实施方案与开发日志
└── pyproject.toml
```

## 开发原则

### 核心开发流程

**每次完整改动都必须经过以下步骤，缺一不可：**

```bash
# 1. 类型检查（ty 严格模式）
ty check src/

# 2. Lint 检查
ruff check src/

# 3. 格式化
ruff format src/

# 4. 运行测试
pytest tests/ -v

# 5. 完整验证（推荐）
ty check src/ && ruff check src/ && pytest tests/
```

**原则说明：**

1. **类型安全优先** — 使用 `ty` 进行严格类型检查，所有公共函数必须有完整类型注解
2. **无私有格式** — 所有认知数据以纯文本（Markdown/YAML）存储，无二进制或隐藏状态
3. **零抽象层** — 直接操作文件系统，不引入额外的 ORM 或缓存层
4. **SSOT** — 运行时工作区内新认知直接覆写旧认知，不做合并

### Git 提交规范

```bash
# 提交前必须运行
ty check src/ && ruff check src/ && pytest tests/

# 约定式提交格式
git commit -m "type(scope): description"

# type 包括:
# - feat: 新功能
# - fix: Bug 修复
# - test: 测试相关
# - docs: 文档更新
# - chore: 构建/工具配置
# - refactor: 代码重构（不影响功能）
# - arch: 架构调整（对应 arch.md 变更）
```

## Python 最佳实践

### 类型注解

```python
from pydantic import BaseModel, Field
from pathlib import Path


class TaskManifest(BaseModel):
    """任务清单 Manifest 模型"""

    id: str = Field(..., description="任务唯一标识")
    status: Literal["CREATED", "IN_PROGRESS", "COMPLETED", "ABANDONED"]
    picture: str = Field(..., description="目标图景（语义成功状态）")
    requirements: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    todos: list[TodoItem] = Field(default_factory=list)
    data_plane: dict[str, str] = Field(default_factory=dict)
    gotcha_refs: list[str] = Field(default_factory=list)


def load_manifest(path: Path) -> TaskManifest:
    """从 Markdown 文件加载 Manifest"""
    ...
```

**原则：**

- ✅ 所有公共函数必须有类型注解（`ty check` 强制）
- ✅ 使用 Pydantic 进行运行时验证，Typer CLI 参数自动类型转换
- ✅ 优先使用 `Literal` 而非 `Enum` 表示有限状态集
- ✅ `Field` 必须提供 `description`，供文档和 LSP 使用

### Pydantic 模型

```python
from pydantic import BaseModel, Field, field_validator
import yaml


class CognitiveTriad(BaseModel):
    """认知三要素：Picture / Requirements / Constraints"""

    picture: str
    requirements: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)

    @field_validator("requirements", "constraints", mode="before")
    @classmethod
    def split_multiline(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [line.strip() for line in v.strip().splitlines() if line.strip()]
        return v


class TodoItem(BaseModel):
    """Todo 项"""

    text: str
    done: bool = False
```

### 文件操作

```python
from pathlib import Path
import yaml


def read_manifest(path: Path) -> TaskManifest:
    """读取 Manifest，支持 Frontmatter 格式"""
    content = path.read_text()
    if content.startswith("---"):
        _, frontmatter, body = content.split("---", 2)
        data = yaml.safe_load(frontmatter)
        # body 用于人类阅读，不做解析
        return TaskManifest(**data)
    return TaskManifest.model_validate_json(content)


def write_manifest(path: Path, manifest: TaskManifest) -> None:
    """写入 Manifest，保持 Frontmatter 格式"""
    frontmatter = yaml.dump(manifest.model_dump(exclude={"body"}), allow_unicode=True)
    path.write_text(f"---\n/frontmatter}\n---\n{manifest.body}")
```

### CLI 命令（Typer）

```python
import typer
from typing import Annotated

cli = typer.Typer(pretty_exceptions_enable=False)


@cli.command()
def status(
    task_id: Annotated[str, typer.Argument(help="任务 ID")] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
) -> None:
    """展示当前认知态势"""
    ...
```

**原则：**

- ✅ 使用 `Annotated` 提供 CLI 参数的完整类型信息和帮助文档
- ✅ `typer.Option` 参数放在 `typer.Argument` 之前
- ✅ 禁用 `pretty_exceptions_enable=False` 以便调试

### 异常处理

```python
class ManifestNotFoundError(Exception):
    """Manifest 文件不存在"""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Manifest not found: {path}")


class ConstraintViolationError(Exception):
    """约束违反错误"""

    def __init__(self, constraint: str, detail: str) -> None:
        self.constraint = constraint
        self.detail = detail
        super().__init__(f"Constraint violated: {constraint} — {detail}")


def load_manifest_safe(path: Path) -> TaskManifest | None:
    """加载失败返回 None，不抛出异常"""
    try:
        return read_manifest(path)
    except (ManifestNotFoundError, ValidationError):
        return None
```

**原则：**

- ✅ 使用自定义异常类，不直接抛出 `ValueError` 或 `RuntimeError`
- ✅ 异常应有足够的上下文字段，供调用方诊断
- ✅ 库函数在边界处转换异常，避免泄露实现细节

## 调试规范

### 日志级别

| 方法 | 场景 | 生产环境 |
|------|------|----------|
| `logging.debug` | 详细排查 | ❌ 禁止 |
| `logging.info` | 重要操作 | ✅ 允许 |
| `logging.warning` | 潜在问题 | ✅ 允许 |
| `logging.error` | 错误追踪 | ✅ 允许 |

### 开发调试

```python
import logging
import os

logger = logging.getLogger(__name__)

# 开发环境启用 DEBUG
if os.environ.get("DEBUG"):
    logging.basicConfig(level=logging.DEBUG)
    logger.debug("[Substrate] Loading manifest: %s", path)
```

### 提交前检查

```bash
# 检查遗留的 debug 日志
grep -r "logger.debug" src/
grep -r "print(" src/

# 检查硬编码路径
grep -r "/Users/" src/
grep -r "C:\\\\" src/
```

## 测试策略

**测试覆盖要求：**

- 新功能必须添加对应测试
- 测试文件位于 `tests/` 目录
- 命名格式：`test_{module}.py`
- 使用 `pytest` 框架

**测试结构：**

```python
# tests/test_schema.py
import pytest
from mem0ress.core.schema import TaskManifest, CognitiveTriad


class TestTaskManifest:
    def test_create_minimal_manifest(self) -> None:
        manifest = TaskManifest(
            id="test-001",
            status="CREATED",
            picture="用户无需输入密码即可登录",
            requirements=["支持 Google OAuth", "支持 GitHub OAuth"],
            constraints=["不许存储明文密码", "Access Token 有效期不得超过 1 小时"],
        )
        assert manifest.status == "CREATED"
        assert len(manifest.requirements) == 2

    def test_frontmatter_roundtrip(self, tmp_path: Path) -> None:
        manifest = TaskManifest(id="test-002", status="CREATED", picture="Test")
        path = tmp_path / "index.md"
        write_manifest(path, manifest)
        loaded = read_manifest(path)
        assert loaded.id == manifest.id

    def test_invalid_status_raises(self) -> None:
        with pytest.raises(ValidationError):
            TaskManifest(id="test", status="INVALID")
```

## 依赖管理（uv）

```bash
# 添加依赖
uv add pydantic typer

# 添加开发依赖
uv add --dev pytest ruff ty

# 同步环境
uv sync

# 锁文件更新
uv lock
```

## 项目命令

```bash
# 类型检查
ty check src/

# Lint 检查
ruff check src/

# 格式化
ruff format src/

# 运行测试
pytest tests/ -v

# 完整验证
ty check src/ && ruff check src/ && pytest tests/

# CLI 帮助
python -m mem0ress.cli --help
```

## 相关文档

- [docs/spec.md](./docs/spec.md) — 接口语义规范
- [docs/arch.md](./docs/arch.md) — 实现架构
- [docs/design.md](./docs/design.md) — 实施方案与开发日志

## 注意事项

1. **使用 uv 管理依赖** — 不使用 pip 或 conda，锁文件 `uv.lock` 必须提交
2. **ty 严格模式** — 所有公共接口必须有完整类型注解，禁用 `Any`
3. **零隐藏状态** — 所有认知数据以 Markdown/YAML 存储，不使用数据库或缓存
4. **测试必须** — 任何功能改动必须更新测试并验证通过
5. **审查优先** — 提交前必须运行 `ty check && ruff && pytest`
6. **禁止硬编码** — 不在代码中硬编码路径、密钥或环境特定配置
7. **异常类命名** — 使用 `{Domain}{Error}` 模式，如 `ConstraintViolationError`
