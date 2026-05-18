先纠正一个前提：两份文件里 verify_cmd 的**定义时机**存在隐患，这比格式问题更根本。

---

## 核心问题诊断

两个案例的 verify_cmd 都写在 `task.md` 里，看起来是"预定义"的。但注意这句话：

> `verify_cmd: python scripts/check_homepage_concepts.py --path dist/index.html`

这个脚本 `check_homepage_concepts.py` **由谁写、什么时候写？**

如果是主 Agent 在执行 T-9~T-13 期间顺手生成的，那就是**自己出卷自己阅卷**，verify_cmd 形式上预定义，实质上不可信。

---

## 两个案例的具体建议

### 案例一：网站（软件交付）

这个案例的 verify_cmd 分两类，处理方式不同：

**第一类：外部工具调用 → 天然可信，预定义即可**

```
R-3: lighthouse ... | jq ...       ✅ 工具由第三方维护，无法被主 Agent 篡改
R-5: gh run list ...               ✅ 读取 CI 系统状态，主 Agent 无法伪造
R-2: playwright test               ✅ 测试文件需提前写，见下
```

**第二类：自定义脚本 → 必须约定冻结时机**

```
R-1: check_homepage_concepts.py    ⚠️ 谁定义"核心概念出现"的判断逻辑？
R-4: check_routes.py               ✅ 逻辑简单（HTTP 200），可信
R-6: check_design_tokens.py        ⚠️ token 对比基准从哪来？
```

对 R-1 和 R-6，建议在 task.md 里补充冻结声明：

```markdown
- [ ] R-1: 首页完整表达核心概念
  verify_cmd: python scripts/check_homepage_concepts.py --path dist/index.html
  verify_frozen_at: 2026-02-01T09:00:00Z   # 与 created_at 同时写入
  concepts_ref: docs/core-concepts.yaml    # 判断基准文件，执行前锁定
```

`core-concepts.yaml` 在任务创建时就定义好四个核心词条，主 Agent 之后不得修改。Judge 验证时比对的是这个冻结文件，而不是脚本自己的判断。

---

### 案例二：白皮书（认知交付）

这个案例更值得细看，因为它暴露了 `manual` 的歧义问题。

**R-1 到 R-5：结构扫描类脚本**

这类脚本逻辑透明（数 heading、数词、找图片引用），可信度高。但要注意：

```markdown
R-1: verify_cmd: python scripts/check_headings.py docs/whitepaper.md
```

章节名称列表应该**硬编码在脚本里还是传参**？建议传参并在 task 创建时冻结：

```markdown
- [ ] R-1: 文档结构完整
  verify_cmd: python scripts/check_headings.py docs/whitepaper.md \
    --required "Executive Summary,Problem Statement,Architecture,\
    Cognitive Model,Runtime Model,Protocol Design,Failure Recovery,Future Work"
```

参数直接写在 task.md 的 verify_cmd 里，主 Agent 无法在执行中修改已写入的 task.md。

**R-6：manual 的问题**

```markdown
R-6: 可独立阅读
  verify_cmd: manual  # Tier 3 semantic review required
```

这里有两个问题：

1. `manual` 不是命令，Judge 的 Tier 2 无法执行，实际上跳过了 Tier 2
2. 把"可独立阅读"的验证全部推给 Tier 3，相当于这条 Requirement 没有任何机器可执行的验证锚点

建议拆分：

```markdown
- [ ] R-6a: 每个核心术语在首次出现时必须有明确定义句
  verify_cmd: python scripts/check_term_definitions.py docs/whitepaper.md \
    --terms "Cognitive Ownership,Semantic Intent,Runtime,Judge,Cognitive Artifact,PRC" \
    --require-definition-on-first-use

- [ ] R-6b: 可独立阅读（语义层）
  verify_cmd: manual
  tier2_result: UNCERTAIN   # 固定，不允许 Judge 对 manual 条目返回 PASS
```

R-6b 的 `tier2_result: UNCERTAIN` 直接写死在 task.md 里，Judge 读到 `manual` 时不执行、直接记录 UNCERTAIN，然后强制进入 Tier 3。这样 Tier 3 的触发是**结构性必然**，而不是"Agent 判断是否需要"。

---

## 一个通用的冻结检查清单

综合两个案例，建议在 SCHEMA 里加一条写入约束：

```
verify_cmd 合法性规则（task 创建时校验）：

1. 外部工具调用（lighthouse / gh / playwright）→ 直接合法
2. 自定义脚本 → 脚本路径 + 判断基准参数必须同时写入，
   基准参数不允许是运行时变量
3. manual → 必须声明 tier2_result: UNCERTAIN，
   且对应 Requirement 必须有至少一条姐妹 R-Xa 提供机器可验的代理指标
4. 禁止 verify_cmd 引用执行阶段才会生成的文件
   （如 dist/ 目录下的内容可以是验证目标，但判断逻辑本身不能依赖它）
```

这样两个案例都能在创建任务时完成合规性检查，Judge 收到的 verify_cmd 是完全可信的静态依据。