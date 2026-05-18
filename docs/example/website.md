# 案例：mem0ress 官方网站（软件交付）

> 任务：制作 mem0ress 官方网站，用户能够在数分钟内理解核心架构理念
>
> 类型：软件交付
>
> 特色：量化 Tier 2 验证（Lighthouse、CI/CD）；多类 Constraints；Tier 2 自动验证

---

## task.md

```yaml
---
id: 2v8p4q
type: task
status: COMPLETED
created_at: 2026-02-01T09:00:00Z
completed_at: 2026-02-15T17:00:00Z
---

# Task: mem0ress 官方网站

## Picture

> 用户访问网站后，能够在数分钟内理解：
> - mem0ress 是什么
> - 与传统 AI workflow 的区别
> - 核心架构理念
> - 为什么它强调 cognitive persistence
>
> 网站具备：清晰信息层级、快速加载、可移动端访问、一致视觉语言、可直接进入 GitHub / Docs

---

## Requirements

- [x] R-1: 首页必须完整表达核心概念（Cognitive Persistence / Runtime Separation /
         Persistent Artifacts / Judge Verification）
         verify_cmd: python scripts/check_homepage_concepts.py --path dist/index.html
- [x] R-2: 移动端适配（320px ~ 1440px）
         verify_cmd: playwright test tests/e2e/responsive.spec.ts
- [x] R-3: Lighthouse Performance ≥ 90, Accessibility ≥ 90
         verify_cmd: lighthouse https://mem0ress.dev --preset=desktop --quiet --output=json | jq '.categories.performance.score, .categories.accessibility.score'
- [x] R-4: Docs 可导航（spec.md / protocol.md / schema.md 在线阅读）
         verify_cmd: python scripts/check_routes.py https://mem0ress.dev --routes /docs/spec,/docs/protocol,/docs/schema
- [x] R-5: push main 后自动构建和部署
         verify_cmd: gh run list --workflow=ci.yml --limit=1 --jq '.[0].conclusion == "success"'
- [x] R-6: 视觉一致性（typography / spacing / button style / color tokens 统一）
         verify_cmd: python scripts/check_design_tokens.py --path dist/assets/tokens.json

---

## Constraints

- C-1: 绝不允许首页出现无法解释的 buzzword
- C-2: 绝不允许 docs 与实现版本不一致
- C-3: 绝不允许未压缩大图直接进入生产环境
- C-4: 绝不允许 runtime architecture 与网站描述矛盾
- C-5: 绝不允许将 agent 描述为"完全自治"
        （除非明确说明 deterministic boundary）

---

## Todos

### Phase 1 — Information Architecture
- [ ] T-1: 定义网站 sitemap
- [ ] T-2: 定义 landing page narrative
- [ ] T-3: 定义 docs navigation
- [ ] T-4: 定义 visual language

### Phase 2 — UI/UX Design
- [ ] T-5: 输出首页 wireframe
- [ ] T-6: 输出 responsive layout
- [ ] T-7: 定义 typography scale
- [ ] T-8: 定义 component tokens

### Phase 3 — Frontend Implementation
- [ ] T-9: 初始化 frontend project
- [ ] T-10: 实现 landing page
- [ ] T-11: 实现 docs viewer
- [ ] T-12: 实现 navigation system
- [ ] T-13: 实现 mobile responsive behavior

### Phase 4 — Infrastructure
- [ ] T-14: 配置 CI/CD（GitHub Actions）
- [ ] T-15: 配置 deployment environment
- [ ] T-16: 配置 analytics
- [ ] T-17: 配置 SEO metadata

### Phase 5 — Validation
- [ ] T-18: 执行 lighthouse test
- [ ] T-19: 执行 responsive test
- [ ] T-20: 检查 docs consistency
- [ ] T-21: 执行 semantic messaging review
```

---

## Judge 重点

### Tier 0 — Constraints 约束检查

| Constraint | 验证方式 |
|-----------|---------|
| C-1: 无 buzzword | 扫描首页文本，检查是否包含无法解释的技术词汇 |
| C-2: docs 与实现一致 | 比对 `docs/` 目录与 `src/` 的版本号标签 |
| C-3: 无未压缩大图 | 扫描 `dist/` 目录，检查图片格式和文件大小 |
| C-4: architecture 与描述一致 | 对比 `docs/ARCHITECTURE.md` 与网站 Architecture 页面内容 |
| C-5: 无"完全自治"描述 | 扫描全文，检查"autonomous"等词汇出现位置是否有 boundary 说明 |

### Tier 1 — Todo & Subtask 完成检查

所有 T-1 ~ T-21 必须标记为 `[x]`。

### Tier 2 — Requirements 验收检查

| Requirement | verify_cmd | 通过条件 |
|------------|-----------|---------|
| R-1: 首页核心概念 | `check_homepage_concepts.py` | 4 个核心概念全部出现 |
| R-2: 移动端适配 | `playwright responsive.spec.ts` | 320px / 768px / 1440px 全部通过 |
| R-3: Lighthouse | `lighthouse ... \| jq` | performance ≥ 0.90 AND accessibility ≥ 0.90 |
| R-4: Docs 路由 | `check_routes.py` | 3 个路由全部返回 200 |
| R-5: CI/CD | `gh run list ...` | 最近一次 run 状态为 success |
| R-6: Design tokens | `check_design_tokens.py` | 所有 token 值与定义文件一致 |

### Tier 3 — 语义对齐检查

**Trigger:** 可选 — 当 Tier 1/2 全部通过后，由 Agent 判断是否需要。

**Judge Prompt:**

```
【目标图景】
用户访问网站后，能够在数分钟内理解 mem0ress 与传统 AI workflow 的区别，
以及为什么它强调 cognitive persistence。

【实际产出】
- [首页实际文案摘要]
- [核心概念传达方式]

【检验指令】
请判断：
1. 用户是否能理解 cognitive persistence 的核心价值主张？
2. 是否存在 marketing-heavy / architecture-light 的问题？
3. narrative flow 是否 coherent？
如果达成，返回 PASS。
如果未达成，返回 FAIL 并指出具体偏差。
```

---

## Tier 2 verify_cmd 详解

### R-3 Lighthouse

```bash
lighthouse https://mem0ress.dev \
  --preset=desktop \
  --quiet \
  --output=json \
  --chrome-flags="--headless" \
  | jq '.categories.performance.score, .categories.accessibility.score'
```

**为什么 Lighthouse 是 Tier 2 而非 Tier 3：**
Lighthouse 是自动化工具，输出客观数值（0.0~1.0），不涉及语义推断。
这正是 Tier 2 和 Tier 3 的本质区别：Tier 2 = 机器可判断，Tier 3 = 需要语义推断。

### R-5 CI/CD 验证

```bash
gh run list --workflow=ci.yml --limit=1
```

**为什么 CI/CD 是 Tier 2：**
CI/CD 是确定性系统，返回 PASS/FAIL，不涉及主观判断。
push main 触发自动构建和部署是客观可验证的工程行为。

---

## Constraints 与软件安全的关系

| Constraint | 性质 | 验证方式 |
|-----------|------|---------|
| C-1: 无 buzzword | 内容约束 | 文本扫描 |
| C-2: docs 一致性 | 技术约束 | 版本号比对 |
| C-3: 图片压缩 | 性能约束 | 文件扫描 |
| C-4: architecture 一致性 | 语义约束 | 文档比对 |
| C-5: agent 描述准确性 | 语义约束 | 全文扫描 |

---

## 与 OAuth SSO 案例的对比

| 维度 | 网站 | OAuth SSO |
|------|------|----------|
| Tier 2 验证类型 | Lighthouse / CI / responsive test | pytest 自动化测试 |
| Tier 2 工具 | lighthouse CLI / playwright / gh | pytest |
| Constraints 数量 | 5 个（内容/技术/部署） | 3 个（安全） |
| Tier 3 触发 | 可选 | 必需（Picture 含主观体验） |
| Todo 分组 | 5 个 Phase | 4 个 Phase |
| 主要失败风险 | performance / responsive | 安全/性能 |
