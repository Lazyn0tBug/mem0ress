## 1. 项目目录结构 (Project Structure)

我们将严格按照第 7 章的架构（L1 控制台、L2 存储层、LLM 接口、Harness 引擎）来划分模块：



```plaintext
mem0ress/
├── pyproject.toml         # 核心项目配置 (基于 uv)
├── .python-version        # uv 固定的 Python 版本 (如 3.12)
├── README.md
├── .mem0ress/             # [测试沙箱] 认知基座 (Cognitive Substrate)
│   ├── inbox.md
│   └── tasks/
└── src/
    └── mem0ress/
        ├── __init__.py
        ├── cli.py         # [入口] 终端交互，提供任务创建 (Task Creation) 等指令
        ├── gateway/       # [认知网关 L1] 替代原 core，连接大脑与基座的中枢
        │   ├── __init__.py
        │   ├── loop.py    # 事件驱动控制循环 (对齐循环)
        │   └── plane.py   # Plane Assembler (认知构建：组装状态/数据平面)
        ├── substrate/     # [认知基座 L2] 替代原 storage，物理客体与状态管理
        │   ├── __init__.py
        │   ├── parser.py  # Manifest 解析与 Schema 校验 (Pydantic)
        │   ├── fs.py      # 乐观锁写入、水化路由与冲突感知
        │   └── git_ops.py # 底层 Git 固化与回溯机制
        ├── llm/           # [大脑接口]
        │   ├── __init__.py
        │   ├── client.py  # LiteLLM 封装 (无状态推理算力)
        │   └── tools.py   # 暴露给 Agent 的 Tool Calls (如水化、状态突变)
        └── harness/       # [检验引擎] 任务检验 (Task Verification)
            ├── __init__.py
            ├── runner.py  # Tier 2: 客观规律验收 (沙箱脚本执行)
            └── judge.py   # Tier 3: 跨平面语义对齐 (LLM-as-a-Judge)
```

## 2. 核心配置文件 (pyproject.toml)

使用 uv 初始化，声明依赖。我们需要 typer 处理命令，pydantic 处理严格的文档 Schema，pyyaml 处理 Frontmatter，litellm 处理多模型接入，以及 GitPython 处理客体回溯。

```toml
[project]
name = "mem0ress"
version = "0.1.0"
description = "A text-based Cognitive Alignment Plane (CAP) and situational awareness framework for LLM Agents."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "typer>=0.12.3",       # 优雅的 CLI 框架
    "pydantic>=2.7.0",     # 强类型 Schema 与认知三要素校验
    "pyyaml>=6.0.1",       # Markdown Frontmatter 解析
    "litellm>=1.35.0",     # LLM 网关，支持多模型路由
    "gitpython>=3.1.43",   # 认知基座的 Git 版本控制
    "rich>=13.7.1",        # CLI 终端美观的态势投影展示
]

[project.scripts]
mem0 = "mem0ress.cli:app"  

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"] 
ignore = []
```

## 3. MVP 落地 Todo 清单 (Execution Todos)

为了避免陷入“一口吃成个胖子”的陷阱，我们将开发过程拆解为 5 个具有明确可交付成果的阶段（这本身就是一个标准的 mem0ress Task）：

* [ ] Phase 1: 基础设施与数据结构 (L2 Storage & Schema)

  * [ ] 初始化 uv 环境，配置 ruff 和 typer 脚手架。
  * [ ] 使用 Pydantic 定义 Manifest (Task) 和 Gotcha 的严格数据模型。
  * [ ] 实现 storage/parser.py：能够正确读取 .md 文件并分离 YAML 头部与 Markdown 正文。

* [ ] Phase 2: 态势平面组装 (Plane Assembler)

  * [ ] 实现目录树遍历逻辑，提取所有 Task.md 的核心字段。
  * [ ] 实现 Status Plane 编译器：将其压缩为极简的 System Prompt 文本。
  * [ ] 实现引用水化 (ref: 解析)：通过正则或字符串匹配，按需读取外部文档至 Data Plane。

* [ ] Phase 3: 动作网关与冲突控制 (Tools & Optimistic Locking)

  * [ ] 在 storage/fs.py 实现带乐观锁的 write_document，若哈希不一致抛出异常。
  * [ ] 封装基础的 Git 自动化操作（初始化仓库、自动 Commit 固化）。
  * [ ] 将读/写能力包装为标准的 JSON Tool 格式格式，供 LLM 调用。

* [ ] Phase 4: LLM 循环与推理介入 (LLM Event Loop)

  * [ ] 接入 LiteLLM，打通 API 通讯。
  * [ ] 编写核心 loop.py：投射平面 -> 发给 LLM -> 拦截并执行 Tool -> 更新状态。

* [ ] Phase 5: 约束检验台 (Harness Engine)

  * [ ] 捕获任务 Todo 状态变更的事件钩子。
  * [ ] 实现 harness/runner.py：读取并 subprocess.run() 外部验证脚本（Tier 2）。
  * [ ] 实现 harness/judge.py：调用另一个无状态 LLM 进行 Picture 语义比对（Tier 3），并生成 Failure Patch。
