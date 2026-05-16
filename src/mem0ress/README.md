# mem0ress — 快速上手

## 安装

```bash
# 项目内直接运行（使用 uv）
uv run mem0 <command>

# 或将 mem0 安装为全局命令
uv pip install -e .
mem0 <command>
```

---

## 命令一览

| 命令 | 说明 |
|------|------|
| `mem0 init` | 初始化认知基座（`.cap/` 目录）|
| `mem0 create` | 创建任务，自动生成 6 位 task_id |
| `mem0 list` | 列出活跃任务，支持交互式选择当前任务 |
| `mem0 update -c "内容"` | 追加 turn 快照到 session.md |
| `mem0 judge` | 执行 T0/T1/T2 验证，结果写入 judge.md |
| `mem0 close` | 先 judge，全 PASS 才标记 COMPLETED（不可绕过）|
| `mem0 done` | `close` 的别名 |
| `mem0 status` | 展示当前状态平面（树形视图）|
| `mem0 report` | 展示最新 judge 验证报告 |
| `mem0 abandon` | 标记任务为 ABANDONED |

除 `init` / `status` / `list` 外，所有命令均从 `.task_info` 读取当前任务，`task_id` 参数可选。

所有命令支持 `--root / -r <path>` 指定基座路径（默认 `.cap`）。

---

## 最小闭环示例

```bash
# 1. 初始化
mem0 init

# 2. 创建任务（自动生成 task_id）
mem0 create

# 3. 查看任务列表（显示当前任务）
mem0 list

# 4. 每轮结束后记录快照
mem0 update -c "完成了用户登录流程，修复了 session 超时问题"

# 5. 验证任务是否就绪
mem0 judge

# 6. 关闭任务（必须 judge PASS 才成功）
mem0 close

# 7. 查看状态
mem0 status
```

---

## 任务文件结构

```
.cap/
└── tasks/
    └── {task_id}/
        ├── task.md     # PRC 定义（picture / requirements / constraints）+ todos
        ├── session.md  # turn 快照（每次 update 追加）
        ├── gotchas.md  # 偏差记录（预留）
        └── judge.md    # 验证报告（每次 judge 追加）
```

---

## requirements 与 verify_cmd

MVP 阶段 requirements 为结构化对象，T2 verify_cmd 存储但不执行：

```yaml
cognitive_triad:
  picture: "用户能安全登录系统"
  requirements:
    - id: req_01
      description: "登录响应 < 200ms"
      verify_cmd: "pytest tests/test_perf.py -k test_login_latency"
    - id: req_02
      description: "认证失败返回 401"
      verify_cmd: null
  constraints:
    - "不得明文存储密码"
```

verify_cmd 为 `null` 时表示纯描述性需求，不需要 shell 验证。

---

## Tier 验证说明

| Tier | 内容 | MVP 状态 |
|------|------|----------|
| Tier 0 | 约束一致性自动检查（在 verify() 链路内部） | ✅ 自动执行 |
| Tier 1 | Mechanical check（todo 完成率 + 子任务状态）| ✅ 执行 |
| Tier 2 | Objective verify（verify_cmd shell 执行）| ⏳ stub（v0.2+ 实现）|
| Tier 3 | Semantic alignment（LLM 推断 picture 对齐）| ⏳ 待实现 |

---

## 开发相关

```bash
# 类型检查
ty check src/

# Lint 检查
ruff check src/

# 运行测试
pytest tests/ -v

# 完整验证
ty check src/ && ruff check src/ && pytest tests/ -v
```

---

## 相关文档

- [spec.md](../../docs/spec.md) — 接口语义规范（协议定义）
- [design.md](./design.md) — 实施方案与实现细节
