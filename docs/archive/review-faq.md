# Review FAQ: 常见误报问题

本文档记录历次审查中曾被提出但经核实为误报的问题，避免重复讨论。

---

## 2026-05-07 审查 (spec.md v3.5)

### 已核实为误报的问题

| 问题 | 误报原因 | 规范已有说明 |
|------|----------|--------------|
| **CPU-RAM-Disk 与 L1/L2 架构矛盾** | CPU 在规范中已明确 = AI Agent | Section 2.4: "CPU（处理枢纽）：AI Agent" |
| **Judge spawn 机制未定义** | Judge Task 已是标准任务，无需额外机制 | Section 6.2: "Judge Task 是一个标准的、一次性的 Task" |
| **Cognitive Substrate 与 Data Plane 关系未定义** | 两者同义，不是包含关系 | Section 1.3: "认知基座 (Cognitive Substrate - 数据)" = Data Plane |
| **Session 模板未展示追加行为** | Session 按轮次追加是明确的设计，无需模板展示 | Section 4.2: "每个轮次的状态快照，版本快照模型，只追加不覆盖" |
| **Gotchas 存储位置不明确** | gotcha_refs 是 Manifest 中的引用字段，已明确定义 | Section 5 模板: `gotcha_refs: []` |
| **"被检验任务摘要"由谁生成** | Judge Agent 自己读取任务信息 | Section 6.2: "Judge Agent 读取被检验任务的 manifest、picture、constraints" |

### 已解决的真实问题（基于用户澄清）

| 问题 | 解决方案 |
|------|---------|
| Session 数据模型矛盾 | Session = 历史追加记录，认知数据 = 覆写 |
| Picture 完成标准无法验证 | Picture = 语义判断，Judge 是可选的，无绝对验证 |
| Judge 递归问题 | 不需要绝对验证，无递归 |
| Cognitive Triad 冲突 | 任务构建时先 Requirements 后 Constraints，保证无冲突 |
| 目标用户缺失 | 已添加：AI/Agent 框架开发者 |
| Data Plane mermaid 标签错误 | 已修改：Data Plane = "commit ID 映射表" |
| Cognitive Triad 构建顺序缺失 | 已在 FAQ 说明：先 Requirements 后 Constraints |

### 审查结论

- **Coherence 问题**: 6/6 为误报，spec 已有明确说明
- **Feasibility 问题**: 均为实现相关，不影响规范本身
- **Product 问题**: 修辞问题，用户接受当前表述
- **Adversarial 问题**: 设计选择问题，用户确认无需修改

---

## 审查原则

1. **先读规范，再提问题** — 规范已明确的内容不是问题
2. **认知 = 虚拟概念** — 构建认知是汇聚数据，不修改数据
3. **Status Plane = 当下** — 不提供历史，历史由 Session 追踪
4. **Session = 任务相关** — 按对话轮次记录，不会无限增长
5. **Judge = 可选验证** — 无绝对验证，不存在递归问题
