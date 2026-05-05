Phase 4: 事件循环与推理介入 (The Heartbeat)
CognitiveLoop 是系统的脉搏。它不断重复着：投影平面 -> 思考 -> 行动 -> 固化 的循环。

`src/mem0ress/core/loop.py`

```python
import json
from mem0ress.core.plane import PlaneAssembler
from mem0ress.llm.tools import get_tool_schemas
from mem0ress.harness.engine import HarnessEngine
# 假设我们有一个封装好的 litellm client
from mem0ress.llm.client import AgentClient 

class CognitiveLoop:
    def __init__(self, substrate_root):
        self.assembler = PlaneAssembler(substrate_root)
        self.agent = AgentClient()
        self.harness = HarnessEngine(substrate_root)

    def tick(self):
        """执行一次完整的认知时钟滴答 (Event Loop)"""
        
        # 1. 投影当前态势 (获取最新的 Status Plane)
        status_plane_text = self.assembler.compile_status_plane()
        
        # 2. 注入上下文并请求 LLM 决策
        # 注意：这里我们将 Status Plane 作为 System Prompt，强制全量挂载
        response = self.agent.chat(
            system_prompt=status_plane_text,
            messages=[{"role": "user", "content": "请基于当前态势，推进任务。"}],
            tools=get_tool_schemas()
        )

        # 3. 拦截与执行动作
        if response.tool_calls:
            for tool_call in response.tool_calls:
                self._dispatch_tool(tool_call)
        else:
            print(f"[Agent 思考]: {response.content}")

    def _dispatch_tool(self, tool_call):
        """系统级路由与权限拦截"""
        func_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        if func_name == "resolve_reference":
            print(f"🌊 [水化触发] 正在挂载 Data Plane: {args['ref_path']}")
            # TODO: 读取外部文件并追加到历史上下文中
            
        elif func_name == "update_todo_status":
            print(f"📝 [态势突变] 更新 Task {args['task_id']} 进度...")
            # TODO: 调用 SubstrateIO.safe_write_manifest (带乐观锁)
            
            # 🔥 核心防线：如果试图勾选完成，或更新了关键状态，唤醒 Harness！
            if args.get('is_done'):
                self._trigger_harness(args['task_id'])

    def _trigger_harness(self, task_id: str):
        """挂起主进程，触发带外约束检验"""
        print(f"🛑 [主执行流挂起] 唤醒 Harness 约束检验引擎拦截 Task: {task_id}")
        passed, failure_patch = self.harness.verify_task(task_id)
        
        if not passed:
            print(f"❌ [约束检验失败] 生成高优先级补丁 (Failure Patch)，强制拉入下一次循环！")
            # 强制覆写基座，生成新的 Gotcha，让 Agent 在下一个 tick 吃到教训
            # SubstrateIO.write_gotcha(task_id, failure_patch)
        else:
            print(f"✅ [约束检验通过] 任务 {task_id} 准许推进，触发 Git 固化。")
```python
