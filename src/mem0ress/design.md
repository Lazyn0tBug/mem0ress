# mem0ress Design — Phase 0 实现计划

> 本文档是 mem0ress 运行时的实现层规范，对应 spec.md（协议语义层）。
> spec.md 回答"是什么"，design.md 回答"怎么做"。

---

## 1. 核心定位

### 1.1 三层职责划分

| 层 | 名称 | 职责 |
|---|---|---|
| Skill | Semantic Coordination Layer | 定义语义协调协议（问什么问题、如何算补全） |
| Agent | Semantic Reasoning | 在 Skill 引导下执行对话，补全语义 |
| Stable Capability Runtime | Protocol Persistence Step | 根据会话结果执行协议持久化（创建/更新文件） |

### 1.2 Skill 的定义

Skill = Semantic Coordination Layer，不是 Workflow Coordinator。

**Skill 可以：**
- 请求补充 Picture
- 请求澄清 Constraints
- 请求验证 Requirement
- 请求 Judge 重新解释 alignment
- 请求 Agent 生成候选方案

**Skill 不得拥有：**
- workflow DAG
- execution pipeline
- state machine orchestration
- procedural execution graph

### 1.3 Slash Command 的定义

Slash Command = Semantic Interaction Entrypoint，不是 Command Binding。

```
/cog create
  ≠ create_task()
  = 一个认知操作开始

它可能触发：
  - 多轮交互
  - 语义澄清
  - 补全 Constraints
  - Agent 提案
  - Judge 检验 alignment
```

### 1.4 Stable Capability Runtime 的定义

Stable Capability Runtime = Protocol Persistence Step，不是主要交互界面。

交互的终点，最后才执行文件创建/更新。

### 1.5 Cognitive Focus Principle

**核心原则**：

> Probabilistic cognition should only be used where semantic ambiguity or strategic reasoning is required. Deterministic execution should be delegated to stable capability runtimes whenever possible.

**含义**：

| 资源 | 用途 |
|------|------|
| **Cognition（稀缺）** | semantic ambiguity、intent formation、strategic reasoning、prioritization |
| **Stable Capability Runtime（稳定）** | write_file、retry、path adaptation、encoding、transaction、rollback、backend migration |

**边界**：

```
Cognition 不应消耗在：
  - 文件写入路径
  - YAML/JSON 序列化
  - 重试逻辑
  - backend adaptation

这些是 Stable Capability Runtime 的职责。
```

**稳定性结论**：

- LLM 不稳定，runtime 稳定
- 加更多 Agent 不能解决 deterministic instability，复杂度上升比稳定性更快
- 原则：不要让 agent 做 runtime，不要让 runtime 做 cognition

**收益**：

1. **Stability** — LLM 不参与 deterministic mechanics，execution surface 收缩
2. **Cognitive purity** — Agent 不被 execution detail（mkdir/path/yaml/utf8）污染
3. **Backend portability** — 今天 task.md，明天 sqlite，后天 remote graph store，Agent 完全不用改
4. **Recovery** — runtime 天然支持 replay、rollback、recover、audit

---

## 2. CLI Design

CLI 是 Stable Capability Runtime 的第一种实现形态。

### 2.1 命令表面

| 命令 | 功能 | 类型 |
|------|------|------|
| `mem0 init` | 初始化认知基座 | setup |
| `mem0 status` | 渲染状态平面 | query |
| `mem0 create` | 创建任务（含 task_id 生成） | write |
| `mem0 abandon` | 标记任务废弃 | write |
| `mem0 update` | 追加认知增量到 session.md | write |
| `mem0 judge` | 触发 Tier 0/1/2 验证 | write |
| `mem0 close` | judge 通过后标记 COMPLETED | write |
| `mem0 done` | close 的别名 | write |
| `mem0 report` | 显示最新 judge 报告 | query |

### 2.2 create 命令

```bash
mem0 create \
  --picture "语义成功状态描述" \
  --requirements "req1; req2; ..." \
  --constraints "红线1; 红线2; ..."
```

**内部流程**：

1. 生成 6 位 base36 task_id：`{timestamp_low}{counter}`
2. 创建 `.mem0ress/tasks/<task_id>/`
3. 生成 task.md（via SubstrateParser）
4. 生成 session.md、gotchas.md、judge.md
5. 更新 `.current_task` 指针

### 2.3 close 命令

```bash
mem0 close <task_id>
```

**内部流程**：

1. 解析 task_id
2. 调用 `HarnessRunner.verify_task()` 执行 Tier 0/1/2
3. 任何 Tier FAIL → 打印失败项，exit 1
4. 全部 PASS → `TaskServiceImpl.complete_task()` → status=COMPLETED
5. 清理 `.current_task` 指针

**No bypass rule**：不经过 Judge 验证的任务不得 close。

### 2.4 其他命令

**status**：`mem0 status [--root .mem0ress]`
渲染 Rich tree 状态平面。

**update**：`mem0 update [--content "..."]`
追加 Turn snapshot 到 session.md，压缩记录，不含 chain-of-thought。

**judge**：`mem0 judge [--root .mem0ress]`
执行 Tier 0/1/2，输出纯文本 PASS/FAIL（无 ANSI markup）。

**abandon**：`mem0 abandon <task_id>`
标记 task.md status=ABANDONED。

**done**：close 的别名，内部调用同一逻辑。

**report**：`mem0 report <task_id>`
读取 judge.md，打印最新验证报告。

### 2.5 文件协议落地

| 文件 | CLI 职责 |
|------|---------|
| `task.md` | TaskServiceImpl.create_task() 生成，SubstrateParser 序列化 |
| `session.md` | TaskServiceImpl.update_session() 追加 Turn 块 |
| `gotchas.md` | TaskServiceImpl.append_gotcha() 追加 Gotcha 块 |
| `judge.md` | HarnessRunner.verify_task() 写入验证报告 |

所有文件格式见 spec.md §5.4 文档数据模型。

### 2.6 目录结构

```
.mem0ress/
├── .current_task              # 当前激活任务指针
└── tasks/
    └── {task_id}/
        ├── task.md           # 任务清单
        ├── session.md        # 认知增量流
        ├── gotchas.md        # 关键发现
        ├── judge.md          # 验证报告
        │
        └── data/             # data plane
            ├── outputs/
            ├── evidence/
            └── artifacts/
```

### 2.7 .current_task 指针

```yaml
task_id: '2k5m3x'
activated_at: '2026-05-14T10:00:00+09:00'
```

- `create` → 写入 task_id + timestamp
- `update/judge/close` → 无 task_id 时读取此指针
- `close` 成功 → 清除 task_id，保留 activated_at

**安全机制**：`safe_write` + SHA-256 hash comparison，并发写入触发 ConflictError。

### 2.8 task_id 生成算法

6 位 base36 字符串：

```
{4 chars: timestamp_low}{2 chars: counter}
```

- **timestamp_low**：`floor(unix_time / 64) % 36^4`，约 12 天循环
- **counter**：进程内单调计数器，保证同窗口内唯一

---

## 3. 技术栈

| 层级 | 技术 |
|------|------|
| Runtime | Python 3.12 |
| 依赖管理 | uv |
| 项目管理 | pyproject.toml |
| CLI | Typer |
| 验证模型 | Pydantic |
| Lint | Ruff |
| 类型检查 | ty |
| 可视化 | Rich |

---

## 4. 验证场景

### Scenario A — 白皮书写作

```
/cog recover
    ↓
write section
    ↓
/cog snapshot
    ↓
identify ambiguity
    ↓
/cog gotcha
    ↓
/cog verify
```

成功标准：白皮书存活于中断；认知从协议重建；gotchas 改善连续性。

### Scenario B — 软件开发

```
/cog recover
    ↓
implement feature
    ↓
/cog snapshot
    ↓
run tests
    ↓
/cog verify
    ↓
/cog decide
```

成功标准：实现存活于 context reset；snapshots 保持压缩；Judge 验证保持隔离；runtime 保持确定性。

---

## 5. 失败条件

| 失败 | 含义 |
|------|------|
| session.md 变成 transcript | 压缩失败 |
| recovery 需要完整回放 | 认知失败 |
| runtime 吸收 reasoning | 架构失败 |
| Judge 收到 hidden state | 隔离失败 |
| slash commands 变成 workflows | 协议失败 |
| Skill 变成 workflow coordinator | CAP 回归 orchestration 框架 |

---

## 6. 实现步骤

### Step 1: 验证

- [ ] 运行 `ty check src/`
- [ ] 运行 `ruff check src/`
- [ ] 运行 `pytest tests/`
- [ ] 提交

---

*其余内容待补充。*