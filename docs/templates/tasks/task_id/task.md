---
description: "Task Manifest — 定义任务的认知目标、验收标准和执行计划"
type: task
status: CREATED
fields:
  cognitive_triad:
    type: object
    description: "认知三要素，语义层面的任务定义"
    children:
      picture:
        type: string
        description: "图景：终极成功状态，利益相关者眼中可感知的结果"
      requirements:
        type: list[string]
        description: "需求：达成目标需要满足的条件，必须可独立验证"
      constraints:
        type: list[string]
        description: "约束：绝对不可逾越的物理红线，一旦违反系统必须阻断"
  todos:
    type: list[object]
    description: "机械步拆解，Agent 执行的具体动作列表"
    children:
      id:
        type: string
        description: "Todo 唯一标识，格式 T-N，用于跨模板关联"
      text:
        type: string
        description: "动作描述，具体可执行的动作"
      done:
        type: boolean
        description: "完成状态"
---

# Task: {任务直观名称}

## 1. 认知三要素 (The Triad)

### 1.1 🎯 图景 (Picture)

> **语义层面的终极成功状态。利益相关者眼中可感知的结果，回答"做成什么样"。**

[在此描述图景。例如：用户无需手动输入密码，即可通过企业单点登录无缝进入工作台。]

### 1.2 📐 需求 (Requirements)

> **达成目标需要满足的条件。必须可独立验证（自动化检验或明确指标）。**

- [ ] Req 1: [例如：认证接口的响应时间必须小于 200ms]
- [ ] Req 2: [例如：必须支持 Google 和 GitHub 两种 OAuth 提供商]

### 1.3 ⛔ 约束 (Constraints)

> **任务实施到完成期间，绝对不可逾越的物理红线。一旦违反系统必须阻断。**

- ⛔ Constraint 1: [例如：绝不允许在任何日志中打印用户的 Access Token]
- ⛔ Constraint 2: [例如：外部依赖包的引入必须经过安全白名单校验]

---

## 2. 机械步拆解 (Todos)

- [ ] T-1: [具体动作描述]
- [ ] T-2: [具体动作描述]

## 3. 子任务依赖 (Subtasks)

- [ ] `{subtask_1_id}/`
- [ ] `{subtask_2_id}/`
