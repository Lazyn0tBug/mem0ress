1. 物理层防御：带乐观锁的基座写入 (src/mem0ress/storage/fs.py)

首先，我们在 storage 层实现底层的物理保护。这里我们引入简单的文件内容 Hash 校验，防止并发或异步导致的文件覆盖（即乐观锁）。

```python
import hashlib
import json
from pathlib import Path
from mem0ress.core.schema import TaskManifest
from mem0ress.storage.parser import SubstrateParser

class ConflictError(Exception):
    """触发 409 Conflict 的自定义异常"""
    pass

class SubstrateIO:
    """
    基座 I/O 引擎：负责安全的物理读写与乐观锁控制
    """
    
    @staticmethod
    def get_file_hash(file_path: Path) -> str:
        """计算文件的当前客观状态 Hash"""
        if not file_path.exists():
            return ""
        content = file_path.read_bytes()
        return hashlib.md5(content).hexdigest()

    @staticmethod
    def safe_write_manifest(manifest: TaskManifest, file_path: Path, expected_hash: str, force_overwrite: bool = False):
        """
        带乐观锁的安全写入
        """
        current_hash = SubstrateIO.get_file_hash(file_path)
        
        # 乐观锁校验：如果物理客体已被外部修改，且没有开启强制覆写
        if current_hash != expected_hash and not force_overwrite:
            # 读取最新状态以便抛出给 Agent
            latest_manifest = SubstrateParser.parse_manifest(file_path)
            raise ConflictError(
                f"409 Conflict: 认知基座已被修改！\n"
                f"期望 Hash: {expected_hash}, 实际 Hash: {current_hash}。\n"
                f"当前底层最新状态为: \n{json.dumps(latest_manifest.model_dump(), ensure_ascii=False, indent=2)}\n"
                f"请更新你的状态平面后重新决断！"
            )

        # 校验通过，执行绝对覆写
        new_content = SubstrateParser.serialize_manifest(manifest)
        file_path.write_text(new_content, encoding="utf-8")
        
        # TODO: 这里预留 Git 固化钩子 (git_ops.commit)
        # GitOps.commit(file_path, message=f"Update manifest: {manifest.id}")
```

2. 认知网关：暴露给 LLM 的动作契约 (src/mem0ress/llm/tools.py)
接下来，我们利用 Python 的类型提示，将系统的能力封装为标准的 Tool Calls (函数调用)，供大模型在推理时使用。

这三个工具完美映射了系统的运转流：水化（探索）、修改状态（执行）、沉淀经验（记录）。

```python
from typing import List, Dict, Any

# 这些 Schema 将被转化为 OpenAI/LiteLLM 的 function calling 格式
def get_tool_schemas() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "resolve_reference",
                "description": "[水化工具] 当你在图景或经验中看到 ref: 前缀的指针时，调用此工具将外部长文档水化挂载到你的数据平面中。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ref_path": {
                            "type": "string",
                            "description": "例如: ref:docs/auth_vision.md"
                        }
                    },
                    "required": ["ref_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_todo_status",
                "description": "[态势突变] 修改指定任务的 Todo 进度。注意：若勾选完成，将触发底层的 Harness 约束检验。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "目标 Task 的 ID"},
                        "todo_index": {"type": "integer", "description": "要修改的 Todo 的索引 (从 0 开始)"},
                        "is_done": {"type": "boolean", "description": "是否完成 (true/false)"},
                        "expected_hash": {"type": "string", "description": "你当前上下文中的该任务状态 Hash，用于防冲突"}
                    },
                    "required": ["task_id", "todo_index", "is_done", "expected_hash"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "record_gotcha",
                "description": "[沉淀经验] 当你排查完 Bug 或做出重大架构妥协时，将认知增量(状态突变)固化为 Gotcha 补丁。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "该经验归属的父级 Task ID"},
                        "filename": {"type": "string", "description": "简短的英文文件名，如 jwt_decision.md"},
                        "content": {"type": "string", "description": "经验的正文内容，包含触发原因与最终决议"}
                    },
                    "required": ["task_id", "filename", "content"]
                }
            }
        }
    ]
```

阶段性复盘
通过这一层设计，大模型（大脑）的“手脚”被严格束缚在了一个极度安全的沙盒里：

它不能胡乱写文件，只能明确指定修改哪个 Task 的第几个 Todo。

即使它发疯或者遭遇并发，底层的 expected_hash (乐观锁) 也会像一面叹息之墙，直接把非法的写入弹回，并强制它“重新看看世界现在的样子”。

至此，我们的 Cognitive Kernel (认知内核) 已经具备了处理 I/O 的手眼能力。

下一个阶段，我们将进入 Phase 4 和 Phase 5 的高潮环节：

我们将编写最核心的 loop.py，把大模型接入进来，让它读到平面、调用工具；并在它调用 update_todo_status 试图完结任务时，用 Harness (约束检验引擎) 的三级短路机制，狠狠地“抽打”它！gg
