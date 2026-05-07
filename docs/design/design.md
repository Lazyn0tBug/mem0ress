## 1. 项目目录结构 (Project Structure)

## 1. 项目目录结构 (Project Structure)

本项目采用 **“认知拦截器 (Cognitive Interceptor)”** 模式设计。mem0ress 不再被视为一个独立的 OS，而是一个伴生式 SDK。它不接管业务编排逻辑，但通过生命周期钩子 (Lifecycle Hooks) 深度参与 Agent 的执行循环，实现态势自动投影与会话捕捉。

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
        ├── cli.py         # [终端入口] 提供基座初始化、态势可视化 (Rich) 与手工校验
        ├── core/          # [核心契约]
        │   ├── __init__.py
        │   └── schema.py  # 基于 Pydantic 的强类型模型 (PRC 三要素、Task、Session)
        ├── gateway/       # [认知网关] 认知对齐平面的逻辑中枢
        │   ├── __init__.py
        │   ├── intercept.py # 核心拦截器：CognitiveContext (Context Manager)
        │   ├── plane.py   # Plane Assembler (认知构建：态势投影逻辑)
        │   └── actions.py # Tool Interface (写入指令集：update_todo, complete_task)
        ├── substrate/     # [认知基座操作]
        │   ├── __init__.py
        │   ├── fs.py      # Markdown/YAML 双向解析器，带 Hash 乐观锁校验
        │   └── git_ops.py # Git 固化、Data Plane commit ID 映射管理
        └── harness/       # [检验引擎] 任务属性对齐验证 (Tiers 0-3)
            ├── __init__.py
            ├── runner.py  # Tier 1/2: 机械检查与沙箱脚本执行
            └── judge.py   # Tier 3: 语义裁决器 (调用独立 LLM 进行 Picture 对齐判断)

```

2. 工程栈与质量控制
项目采用 Astral 性能全家桶 (uv + ruff + ty)。

  * uv: 极速包管理与虚拟环境隔离。
  * ruff: 毫秒级 Linting 与代码格式化。
  * ty: Astral 推出的强类型检查器，确保认知模型在静态期即具备高度确定性

## 2. 核心配置文件 (pyproject.toml)

使用 uv 初始化，声明依赖。我们需要 typer 处理命令，pydantic 处理严格的文档 Schema，pyyaml 处理 Frontmatter，litellm 处理多模型接入，以及 GitPython 处理客体回溯。

```toml
[project]
name = "mem0ress"
version = "0.1.0"
description = "A Cognitive Alignment Plane (CAP) SDK with Lifecycle Hooking."
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

## 3. 核心机制设计

### 3.1 认知拦截器 (Gateway Interceptor)

gateway/intercept.py 提供 CognitiveContext 上下文管理器，作为 SDK 参与 Agent 循环的唯一入口：

* enter (Before Turn):
  * 启动 Plane Assembler 扫描物理基座。
  * 构建 Status Plane 快照，自动注入 Agent 的上下文环境变量。
* exit (After Turn):
  * 捕获 Agent 的 Output 和 Tool Calls。
  * 自动会话捕捉: 计算物理文件的 Delta，追加记录至 session.md。
  * 若检测到关键动作（如 update_todo），自动触发 substrate 层的文件写入。


### 3.2 任务检验逻辑 (Harness)

Harness 遵循“绝对阻断”原则：

* Tier 0: 检查 Constraints 是否被违背。违背即阻断，记录 Gotcha，交由 Agent 处理，绝不执行隐式自动修复。
* Tier 3: 仅在 Agent 显式请求或满足高危阈值时触发。通过 Data Plane 记录的 commit ID “水化”出代码产出，喂给独立 Judge LLM。

### 3.3 乐观锁机制 (Optimistic Locking)

`substrate/fs.py1在写入任何1index.md1前，必须比对内容 Hash。若基座在 Agent 思考期间被外部修改，抛出 409 Conflict，强制 Agent 重新投影平面。

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

* [ ] Phase 1: 物理契约与类型安全 (Substrate & Ty Check)
  * [ ] 配置 uv, ruff, ty 环境。
  * [ ] 实现 core/schema.py: 定义 PRC 三要素与分形 Task 模型。
  * [ ] 实现 substrate/fs.py: Markdown ↔ Pydantic 双向转换逻辑。
* [ ] Phase 2: 拦截器与态势投影 (Interception & Projection)
  * [ ] 实现 gateway/plane.py: 递归目录树生成带层级缩进的 Status Plane 文本。
  * [ ] 实现 gateway/intercept.py: 编写 CognitiveContext 上下文管理器。
  * [ ] 实现 ref: 引用的水化机制。
* [ ] Phase 3: 动作网关与版本锚定 (Tools & GitOps)
  * [ ] 实现 gateway/actions.py: 暴露 update_todo, create_task, complete_task 工具。
  * [ ] 封装 git_ops.py: 实现 Data Plane 的 commit ID 自动管理与关联。
* [ ] Phase 4: 属性对齐验证 (Verification Engine)
  * [ ] 实现 harness/runner.py: Tier 1 (Todo 检查) 与 Tier 2 (脚本执行)。
  * [ ] 实现 harness/judge.py: 调用裁判模型进行 Tier 3 语义对齐。
* [ ] Phase 5: CLI 可观测性 (CLI Observability)
  * [ ] 在 cli.py 中利用 Rich 实现 mem0 status：在终端展示高亮、分形的认知地图。
