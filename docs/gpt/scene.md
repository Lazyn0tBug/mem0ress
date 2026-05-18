# 基于 mem0ress 的 PRC 与 Task/Todo 设计示例

本文基于当前讨论后的协议结构，重新设计两个典型场景：

1. 白皮书（Whitepaper）
2. 网站制作（Website Development）

目标不是简单列 Todo，
而是体现：
- PRC（Picture / Requirements / Constraints）
- Cognitive Ownership
- Judge 可验证性
- 长周期认知恢复
- semantic / operational separation

---

# 一、场景一：AI Agent Framework 白皮书

---

## 1.1 Task 定义

```yaml
Task Name: AI Agent Framework Whitepaper
Type: cognitive-deliverable
Primary Artifact: docs/whitepaper.md
```

---

# 1.2 Picture（图景）

> 一份能够被技术团队、投资人和高级工程人员独立阅读并理解的 Agent Framework 白皮书。
>
> 阅读者能够：
> - 理解系统的核心认知模型
> - 理解与传统 workflow agent 的区别
> - 理解 runtime / cognition separation
> - 在不依赖作者解释的情况下复现整体架构
>
> 文档具备：
> - 完整结构
> - 一致术语
> - 清晰图景
> - 工程可信度

---

# 1.3 Requirements（需求）

## R-1：文档结构完整

必须包含：
- Executive Summary
- Problem Statement
- Architecture
- Cognitive Model
- Runtime Model
- Protocol Design
- Failure Recovery
- Future Work

验证方式：
- 自动检查 markdown heading

---

## R-2：术语一致

以下术语必须定义且全篇一致：
- Cognitive Ownership
- Semantic Intent
- Runtime
- Judge
- Cognitive Artifact
- PRC

验证方式：
- glossary scan
- duplicated-definition scan

---

## R-3：至少包含 3 个架构图

必须包括：
- 系统层级图
- 生命周期图
- Agent / Runtime 边界图

验证方式：
- markdown image reference count

---

## R-4：必须存在失败模型章节

必须明确：
- semantic drift
- ownership split
- runtime instability
- context contamination

验证方式：
- section existence check

---

## R-5：白皮书长度

正文不少于：
- 8000 字（中文）
或
- 5000 words（英文）

验证方式：
- word count

---

## R-6：可独立阅读

新读者无需额外口头解释，能够理解：
- 为什么使用 markdown artifact
- 为什么 runtime 不拥有 cognition
- 为什么需要 Judge

验证方式：
- Tier 3 semantic review

---

# 1.4 Constraints（约束）

## C-1

绝不允许：
- 使用未定义术语
- 在不同章节改变同一术语含义

---

## C-2

绝不允许：
- 将 deterministic runtime 与 cognitive reasoning 混写为同一层

---

## C-3

绝不允许：
- 用 marketing language 替代 architecture explanation

例如：
- “革命性”
- “下一代”
- “颠覆式”

除非给出明确技术依据。

---

## C-4

绝不允许：
- 引入无法验证的 Requirement

例如：
- “非常智能”
- “体验很好”

---

# 1.5 Todos（机械步拆解）

## Phase 1 — Research

- [ ] T-1: 收集现有 agent framework 架构
- [ ] T-2: 对比 workflow orchestration 与 cognitive persistence
- [ ] T-3: 建立核心术语表
- [ ] T-4: 输出核心 worldview 草稿

---

## Phase 2 — Architecture Design

- [ ] T-5: 设计 runtime / cognition separation
- [ ] T-6: 设计 protocol layering
- [ ] T-7: 设计 Judge lifecycle
- [ ] T-8: 设计 cognitive artifact model

---

## Phase 3 — Whitepaper Writing

- [ ] T-9: 编写 introduction
- [ ] T-10: 编写 architecture section
- [ ] T-11: 编写 protocol section
- [ ] T-12: 编写 failure model
- [ ] T-13: 编写 future work

---

## Phase 4 — Validation

- [ ] T-14: 检查术语一致性
- [ ] T-15: 检查章节完整性
- [ ] T-16: 执行 semantic review
- [ ] T-17: 输出最终 PDF

---

# 1.6 Judge 重点

## Tier 1

检查：
- 所有章节是否存在
- 所有图是否存在
- 所有 Todo 是否完成

---

## Tier 2

检查：
- 术语一致性
- heading 完整性
- word count
- glossary coverage

---

## Tier 3

判断：
- 文档是否真正解释了 cognition/runtime separation
- 是否存在 semantic contradiction
- 是否形成 coherent worldview

---



# 二、场景二：Website 制作

---

## 2.1 Task 定义

```yaml
Task Name: mem0ress Official Website
Type: software-deliverable
Primary Artifact: apps/web
```

---

# 2.2 Picture（图景）

> 用户访问网站后，能够在数分钟内理解：
> - mem0ress 是什么
> - 与传统 AI workflow 的区别
> - 核心架构理念
> - 为什么它强调 cognitive persistence
>
> 网站具备：
> - 清晰信息层级
> - 快速加载
> - 可移动端访问
> - 一致视觉语言
> - 可直接进入 GitHub / Docs

---

# 2.3 Requirements（需求）

## R-1：首页必须完整表达核心概念

必须明确说明：
- Cognitive Persistence
- Runtime Separation
- Persistent Artifacts
- Judge Verification

验证方式：
- homepage semantic scan

---

## R-2：移动端适配

页面宽度：
- 320px ~ 1440px

验证方式：
- responsive test

---

## R-3：页面加载性能

Lighthouse：
- Performance ≥ 90
- Accessibility ≥ 90

验证方式：
- lighthouse CI

---

## R-4：Docs 可导航

必须支持：
- spec.md
- protocol.md
- schema.md

在线阅读。

验证方式：
- route existence check

---

## R-5：部署自动化

push main 后：
- 自动构建
- 自动部署

验证方式：
- CI pipeline test

---

## R-6：视觉一致性

必须统一：
- typography
- spacing
- button style
- color tokens

验证方式：
- design token audit

---

# 2.4 Constraints（约束）

## C-1

绝不允许：
- 首页出现无法解释的 buzzword

---

## C-2

绝不允许：
- docs 与实现版本不一致

---

## C-3

绝不允许：
- 未压缩大图直接进入生产环境

---

## C-4

绝不允许：
- runtime architecture 与网站描述矛盾

---

## C-5

绝不允许：
- 将 agent 描述为“完全自治”

除非明确说明 deterministic boundary。

---

# 2.5 Todos（机械步拆解）

## Phase 1 — Information Architecture

- [ ] T-1: 定义网站 sitemap
- [ ] T-2: 定义 landing page narrative
- [ ] T-3: 定义 docs navigation
- [ ] T-4: 定义 visual language

---

## Phase 2 — UI/UX Design

- [ ] T-5: 输出首页 wireframe
- [ ] T-6: 输出 responsive layout
- [ ] T-7: 定义 typography scale
- [ ] T-8: 定义 component tokens

---

## Phase 3 — Frontend Implementation

- [ ] T-9: 初始化 frontend project
- [ ] T-10: 实现 landing page
- [ ] T-11: 实现 docs viewer
- [ ] T-12: 实现 navigation system
- [ ] T-13: 实现 mobile responsive behavior

---

## Phase 4 — Infrastructure

- [ ] T-14: 配置 CI/CD
- [ ] T-15: 配置 deployment environment
- [ ] T-16: 配置 analytics
- [ ] T-17: 配置 SEO metadata

---

## Phase 5 — Validation

- [ ] T-18: 执行 lighthouse test
- [ ] T-19: 执行 responsive test
- [ ] T-20: 检查 docs consistency
- [ ] T-21: 执行 semantic messaging review

---

# 2.6 Judge 重点

## Tier 1

检查：
- 所有页面是否存在
- 所有 route 是否可访问
- deployment 是否成功

---

## Tier 2

检查：
- lighthouse score
- responsive layout
- broken links
- CI status

---

## Tier 3

判断：
- 网站是否真正传达 cognitive persistence worldview
- narrative 是否 coherent
- 是否存在 marketing-heavy / architecture-light 问题
- 用户是否能够理解 runtime/cognition separation

---

# 三、两个场景的核心差异

| 维度 | Whitepaper | Website |
|---|---|---|
| 核心交付物 | cognition artifact | software artifact |
| Tier 3 权重 | 极高 | 中高 |
| Tier 2 权重 | 中 | 极高 |
| Failure 风险 | semantic incoherence | implementation inconsistency |
| Todo 类型 | reasoning-heavy | execution-heavy |
| Judge 重点 | worldview consistency | user-facing coherence |
| PRC 重点 | semantic clarity | operational usability |

---

# 四、PRC 的最终理解

PRC 不是：
- 普通需求文档
- 用户故事
- checklist

而是：

## Picture
定义：
- 目标图景
- 语义终态
- stakeholder 可感知结果

---

## Requirements
定义：
- 可验证条件
- deterministic success checks

---

## Constraints
定义：
- 不允许突破的边界
- violation = hard stop

---

PRC 本质上是在做：

```text
semantic target
+
verifiable success
+
hard safety boundary
```

这是整个 cognitive protocol 的核心。

