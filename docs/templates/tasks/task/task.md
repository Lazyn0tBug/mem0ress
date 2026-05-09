---
task_id: "{unique_task_id}"
status: "CREATED" # 可选值: CREATED | IN_PROGRESS | VERIFYING | COMPLETED | ABANDONED
created_at: "YYYY-MM-DDTHH:mm:ssZ"
---

# Task: {任务直观名称}

## 1. 认知三要素 (The Triad)
### 1.1 🎯 图景 (Picture)
> **语义层面的终极成功状态。利益相关者眼中可感知的结果，回答“做成什么样”。**
[在此描述图景。例如：用户无需手动输入密码，即可通过企业单点登录无缝进入工作台。]

### 1.2 📐 需求 (Requirements)
> **达成目标需要满足的条件。必须可独立验证（自动化检验或明确指标）。**
- [ ] Req 1: [例如：认证接口的响应时间必须小于 200ms]
- [ ] Req 2: [例如：必须支持 Google 和 GitHub 两种 OAuth 提供商]

### 1.3 ⛔ 约束 (Constraints)
> **任务实施到完成期间，绝对不可逾越的物理红线和禁则。一旦违反系统必须阻断。**
- ⛔ Constraint 1: [例如：绝不允许在任何日志中打印用户的 Access Token]
- ⛔ Constraint 2: [例如：外部依赖包的引入必须经过安全白名单校验]

---

## 2. 机械步拆解 (Todos)
- [ ] Todo 1: [具体动作描述]
- [ ] Todo 2: [具体动作描述]

## 3. 子任务依赖 (Subtasks)
- [ ] `{subtask_1_id}/`
- [ ] `{subtask_2_id}/`

> **双重格式说明：** task.md 存在两种等价的语义表达方式。Frontmatter 中的 `cognitive_triad` 字段（YAML 格式）是机器可解析的标准格式，供 mem0ress 内部 API 读取；Body 中的 `## Picture / ## Requirements / ## Constraints` 是人类可读的展示格式，供 Agent 和利益相关者直接查阅。两者内容必须完全一致——Agent 写入 body 后必须同步更新 frontmatter，或由工具自动维护一致性。
