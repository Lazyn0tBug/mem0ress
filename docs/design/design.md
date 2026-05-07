## 1. 项目目录结构 (Project Structure)


本项目采用 **“认知拦截器 (Cognitive Interceptor)”** 模式。mem0ress 不编排业务逻辑，但通过挂钩 (Hook) 任务执行的生命周期，实现自动化的态势投影与会话捕捉。

```plaintext
mem0ress/
├── pyproject.toml         # 核心项目配置 (基于 uv)
├── .python-version        # uv 固定的 Python 版本 (3.12+)
├── README.md
├── .mem0ress/             # [认知基座 Substrate] 物理承载层
│   └── tasks/             # 分形任务树 (包含 index.md, session.md, gotchas/)
└── src/
    └── mem0ress/
        ├── __init__.py
        ├── cli.py         # [终端入口] 用于初始化基座、查看态势图、调试校验
        ├── core/          # [核心契约] 基于 Pydantic 的强类型定义
        │   ├── __init__.py
        │   └── schema.py  # 定义认知三要素、TaskManifest、Session、Gotcha 模型
        ├── gateway/       # [认知网关] 负责读写交互与生命周期拦截
        │   ├── __init__.py
        │   ├── intercept.py # 核心拦截器：CognitiveContext (上下文管理器)
        │   ├── plane.py   # Plane Assembler (认知构建：态势投影)
        │   └── actions.py # Tool Interface (写入操作：update_todo, create_task)
        ├── substrate/     # [基座操作] 底层物理 I/O
        │   ├── __init__.py
        │   ├── fs.py      # Markdown/YAML 双向解析、乐观锁校验
        │   └── git_ops.py # Git 固化、管理数据平面 (Data Plane) commit ID 映射
        └── harness/       # [检验引擎] 任务检验逻辑
            ├── __init__.py
            ├── runner.py  # Tier 1/2: 机械检查与沙箱脚本执行
            └── judge.py   # Tier 3: 语义对齐裁决 (独立运行的 Judge LLM)
```

## 2. 核心配置文件 (pyproject.toml)

使用 uv 初始化，声明依赖。我们需要 typer 处理命令，pydantic 处理严格的文档 Schema，pyyaml 处理 Frontmatter，litellm 处理多模型接入，以及 GitPython 处理客体回溯。

```toml
[project]
name = "mem0ress"
version = "0.1.0"
description = "A text-based Cognitive Alignment Plane (CAP) and situational awareness SDK for LLM Agents."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "typer>=0.12.3",       # 用于构建 CLI 外壳
    "pydantic>=2.7.0",     # 强类型 Schema，完美配合 ty 进行类型推断
    "pytest>=8.0",
    "ruff>=0.9.0",
    "ty>=0.0.32",
    "pyyaml>=6.0.1",       # Markdown Frontmatter 解析
    "litellm>=1.35.0",     # 仅用于 Harness Engine 的 Judge 语义裁决
    "gitpython>=3.1.43",   # 数据平面的 commit ID 管理
    "rich>=13.7.1",        # 终端可视化的态势投影展示
]

[project.scripts]
mem0 = "mem0ress.cli:app"  

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# Astral 工具链配置 (Ruff + Ty)
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"] 
ignore = []

[tool.ty]
# 开启 ty 的严格类型检查模式，保证内核代码的确定性
strict = true
```

## 3. 核心机制：认知拦截器 (Gateway Interceptor)
为了解决“自动捕捉会话”的需求，gateway/intercept.py 提供 CognitiveContext 上下文管理器。这是 mem0ress 参与 Event Loop 的唯一优雅方式。

### 3.1 运行逻辑

  1. 进入上下文 (__enter__)：
  
    * 调用 Plane Assembler 扫描物理基座。
    * 自动投影生成最新的 Status Plane 文本块。
    * 将投影注入到 Agent 的当前上下文变量中。
  
  2. 退出上下文 (__exit__)：
  
    * 拦截并捕获本轮 Agent 的输出以及产生的 Tool Calls 动作。
    * 自动触发 Session 快照：计算代码与文档的 Delta，记录到 session.md。
    * 若检测到 complete_task 等关键状态变更，自动执行基座的 Git 固化。

## 4. MVP 落地 Todo 清单 (基于生命周期重构)

开发过程被严格重塑为 5 个具有明确架构边界的阶段：

* [ ] Phase 1: 基座契约与强类型闸门 (Substrate & Type Safety)

  * [ ] 初始化 uv 项目，配置 ruff 和 ty 守护进程。
  * [ ] 在 core/schema.py 中定义任务三要素模型，确保字段符合 spec.md 语义。
  * [ ] 实现 substrate/fs.py：支持 Markdown 与 Pydantic 的转换，并在写入时执行内容 Hash 的乐观锁校验。
  
* [ ] Phase 2: 认知构建与生命周期拦截 (Cognition Building & Hooking)

  * [ ] 实现 gateway/plane.py：递归扫描 .mem0ress/tasks，生成带有层级依赖关系的态势文本。
  * [ ] 实现 gateway/intercept.py：编写 CognitiveContext 拦截器。
  * [ ] 实现 Data Plane 的“引用水化”逻辑：按需展开 ref: 指针指向的外部长文档。
  
* [ ] Phase 3: 任务创建引擎与动作网关 (Task Creation & Actions)

  * [ ] 在 cli.py 实现 mem0 task create 指令，强制交互式录入图景与约束。
  * [ ] 在 gateway/actions.py 实现工具集：update_todo, add_gotcha, link_data_plane。
  * [ ] 封装 git_ops.py，实现每次动作后的 commit ID 自动关联。
  
* [ ] Phase 4: 任务检验引擎 (Task Verification - Harness)

  * [ ] Tier 1 (机械)：扫描当前任务树，验证所有子任务是否已闭环。
  * [ ] Tier 2 (客观)：利用 subprocess 在隔离沙箱运行校验脚本，验证 Requirements。
  * [ ] Tier 3 (语义)：水化物理代码产出，调用独立裁判模型比对 Picture 和 Constraints。
  
* [ ] Phase 5: 绝对可观测性与 CI/CD

  * [ ] 利用 Rich 实现终端态势图（Status Plane Tree）。
  * [ ] 配置 GitHub Actions：在 CI 流程中强制运行 ruff check 和 ty check。
