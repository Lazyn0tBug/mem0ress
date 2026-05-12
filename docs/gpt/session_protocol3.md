你这两个反驳是成立的。我要修正我前面的判断：我之前把你的两句话按“上下文裁剪风险”来理解了，但你实际强调的是 Task-local 条件下的状态忠实投影。在你这个前提下，“不相关性排序、不挑选、不截断”不是粗暴全量注入，而是为了避免状态平面被二次加工后失真。

我的建议如下。

一、关于“不相关性排序、不挑选、不截断”
你的原意应该保留，但需要换一种更精确的表达。

你不是说：

所有历史、所有任务、所有内容都不截断地塞给 Agent。

你真正说的是：

在当前绑定 Task 的认知边界内，状态平面不通过相关性排序、语义挑选或摘要截断来猜测“哪些状态重要”，而是如实投影当前 Task 的完整可判断状态。

这个逻辑是对的。

因为你的架构已经有三层天然边界：

Agent 对应 Task：不会默认读取整个 Project；

轮次和时间戳对应内容：Session 本身有时序结构；

Task 文件模型限定内容范围：task.md / session.md / gotchas.md / judge.md 只属于当前 Task。

所以在这个前提下，再引入相关性排序反而可能破坏状态平面的可信度。

也就是说，你要避免的是：

Agent 不是从一堆历史里“猜当前状态”，而是从当前 Task 的结构化状态中“读取当前状态”。

这个是 mem0ress 与 memory / RAG 系统的关键区别。

我建议你把 spec 里的表达改成这样
mem0ress 不以相关性排序、语义挑选或摘要截断来构建当前状态平面。

在 Task-local 边界内，状态平面应当如实投影当前 Task 的完整可判断状态，包括任务定义、Todo 进度、未解决 Gotchas、最近 Session 指针、Judge 结果和必要的数据平面引用。

这里的“不排序、不挑选、不截断”并不意味着把整个项目历史或完整任务树注入 Agent 上下文，而是指：在当前绑定 Task 的认知边界内，不通过相似度检索或模型摘要来重写当前状态。

状态平面的边界由 Task 确定，而不是由相关性算法确定。
这句话很关键：

状态平面的边界由 Task 确定，而不是由相关性算法确定。

这个比“全面覆盖，显示所有任务”更准确，也能避免别人误解。

二、你这个原则的本质：不是“全量”，而是“忠实”
我建议你把术语从：

不检索、不排序、不挑选、不截断

升级成：

Faithful Projection，忠实投影

它表达的是：

不是把所有东西都塞进去，
而是在已经确定的 Task 边界内，不歪曲、不猜测、不遗漏当前状态。
可以定义为：

Faithful Projection 指状态平面在当前 Task 边界内，对任务状态进行忠实投影。它不根据语义相似度决定哪些状态应被保留，也不通过 LLM 摘要替代结构化状态，而是直接从协议文件中读取当前可判断事实。
这能把你的设计讲得更高级，也更工程化。

三、关于 Judge Agent：你的判断是对的，但要把边界说清楚
你说：

Judge Agent 恰恰是试图用 LLM 判定来补全 Requirements 无法达到的部分。

这个观点我赞成。

我前面说“Judge Agent 的边界要收紧”，不是说不要 LLM Judge，而是担心它变成一个无边界的“再来一个模型主观判断一切”。

但按你的设计，Judge Agent 的价值正是在于：

Requirements 是可验证条件，但 Requirements 无法穷尽 Picture；因此需要 Judge Agent 在 Requirements 之外，对 Picture 是否真正达成进行语义补全判断。

这非常关键。

你的原始理论里已经说过：

Requirements 满足不等于 Picture 达成。

那么 Judge Agent 的 Tier 3 就不是多余的，它是为了处理这部分缺口。

所以，我现在建议不是削弱 Judge Agent，而是把它的职责定义得更准确。

四、Judge Agent 不应该判断一切，而应该判断 Requirements 与 Picture 之间的剩余差
我建议你给 Judge Agent 一个更严格的定义：

Judge Agent 不是替代 Requirements 的验证器，而是 Picture 与 Requirements 之间的语义差距检验器。

也就是说：

Tier 0 检查 Constraints；

Tier 1 检查 Todos / Subtasks；

Tier 2 检查 Requirements；

Tier 3 检查 Requirements 通过后，Picture 是否仍未被真正达成。

这就把 LLM Judge 的边界收紧了，但没有否定它。

建议写法
Judge Agent 的核心职责不是重复执行 Requirements 检查，而是补足 Requirements 无法穷尽 Picture 的部分。

Requirements 是 Picture 的必要条件，但不是充分条件。即使所有 Requirements 均已通过，实际产出仍可能无法满足利益相关者对 Picture 的语义预期。因此，Judge Agent 在 Tier 3 中执行语义对齐检查，用于判断 Requirements 与 Picture 之间是否仍存在剩余偏差。

Judge Agent 的判断对象不是任意历史内容，而是当前 Task 的 Picture、已通过的 Requirements、Constraints 状态、最新 Judge 结果、Data Plane 引用和实际产出证据。
五、Tier 3 应该触发在“Requirements 看似通过之后”
我建议把 Tier 3 的触发条件改得更清楚。

不是每轮都让 LLM Judge 介入，而是：

Tier 0 没有 hard violation；
Tier 1 Todos / Subtasks 已完成；
Tier 2 Requirements 已满足或大部分满足；
但 Picture 是否真正达成仍存在语义判断空间。
也就是说，Tier 3 是最后的“Picture alignment check”。

建议触发条件：

tier_3_trigger:
  enabled_when:
    - tier_0.result == passed
    - tier_1.result == passed
    - tier_2.result in [passed, mostly_passed]
  required_if:
    - picture_involves_user_experience
    - picture_involves_stakeholder_acceptance
    - requirements_are_proxy_metrics
    - output_is_document_or_design
    - user_explicitly_requests_semantic_review
这样它就不会滥用。

六、Judge Agent 的输出不应该是“主观意见”，而应该是“语义偏差报告”
我建议 Tier 3 的输出不要只写：

PASS / FAIL
而要写：

semantic_alignment:
  result: PASS | FAIL | UNCERTAIN
  residual_gap:
    exists: true | false
    description: ...
  picture_coverage:
    covered:
      - ...
    not_covered:
      - ...
  stakeholder_risk:
    level: low | medium | high
    reason: ...
  required_human_confirmation: true | false
这能让 LLM Judge 的判断更可审计。

尤其是 UNCERTAIN 很重要。
因为 LLM 不应该在证据不足时强行判定 PASS 或 FAIL。

七、Tier 3 Prompt 应该围绕“剩余偏差”设计
不要问：

是否完美达成 Picture？

这个太绝对。

建议问：

你是当前 Task 的 Judge Agent。你的任务不是重新验证 Requirements，而是在 Requirements 已经通过或接近通过的前提下，判断实际产出是否仍然存在会阻止 Picture 被利益相关者认可的语义偏差。

请只基于以下材料判断：
1. Picture
2. Requirements 及其验证结果
3. Constraints 及其状态
4. 最新 Data Plane 引用
5. 实际产出证据
6. 未解决 Gotchas

请回答：
- Requirements 是否只能证明局部达标？
- 是否存在 Picture 层面的剩余偏差？
- 该偏差是否足以阻止任务关闭？
- 是否需要人类确认？

输出必须使用 YAML。
输出：

tier_3:
  result: PASS
  residual_gap:
    exists: false
    description: null
  closure_recommendation:
    can_close_task: true
    reason: "Requirements 已通过，且未发现阻止 Picture 达成的语义偏差。"
  human_confirmation_required: false
失败时：

tier_3:
  result: FAIL
  residual_gap:
    exists: true
    description: "虽然 Google OAuth callback 测试通过，但实际登录流程仍显示本地密码输入框，违背 Picture 中‘无需输入本地密码’的用户感知目标。"
  closure_recommendation:
    can_close_task: false
    reason: "存在 Picture 层面的用户体验偏差。"
  human_confirmation_required: false
不确定时：

tier_3:
  result: UNCERTAIN
  residual_gap:
    exists: unknown
    description: "缺少实际 UI 截图或用户流程日志，无法判断用户是否真的没有看到本地密码输入环节。"
  closure_recommendation:
    can_close_task: false
    reason: "证据不足，不能关闭任务。"
  human_confirmation_required: true
八、你可以把 Judge Agent 定义为“语义验收器”，不是“裁判模型”
我建议你不要过多强调 LLM-as-a-Judge，因为这个词现在容易引发争议。

可以叫：

Semantic Acceptance Agent

或者：

Picture Alignment Judge

中文叫：

图景对齐检验器

它的核心职责是：

在机械条件和可验证需求之外，判断任务产出是否真正满足 Picture。
这样比“LLM 判定一切”稳得多。

九、对你原设计的最终建议
1. “不排序、不挑选、不截断”保留
但改名为：

Task-local Faithful Projection

强调：

不是项目全量注入；
不是历史全量注入；
而是当前 Task 边界内的完整状态忠实投影。
建议加入一句：

mem0ress 不用相关性算法决定当前状态边界，当前状态边界由 active Task 决定。

2. Judge Agent 保留，而且应该成为核心
但边界定义为：

Judge Agent 补足 Requirements 无法穷尽 Picture 的语义验收缺口。

3. Tier 3 不应滥用
建议只在：

Requirements 已满足或接近满足；
Picture 仍可能存在语义偏差；
任务准备关闭前；
用户或 Agent 明确请求；
时触发。

4. Tier 3 必须允许 UNCERTAIN
这是非常重要的工程安全阀。

LLM Judge 不能只有 PASS / FAIL。
必须允许：

证据不足，不能关闭，需要人类确认。
5. Judge Agent 不直接关闭任务
Judge 只能输出：

can_close_task: true|false
recommended_status: ...
semantic_gap: ...
human_confirmation_required: true|false
最终关闭由主 Agent 或 Worker 执行。

十、我建议你在 spec 里这样改
可以新增两个小节。

1. Faithful Projection
### Faithful Projection：状态平面的忠实投影原则

mem0ress 的状态平面不通过相关性排序、语义挑选或摘要截断来构建当前认知。状态平面的边界由当前绑定 Task 决定，而不是由相似度算法决定。

在 Task-local 边界内，状态平面应当如实投影当前 Task 的完整可判断状态，包括任务声明、Todo 进度、未解决 Gotchas、最近 Session 指针、Judge 结果、直接子任务摘要和必要的数据平面引用。

这里的“不排序、不挑选、不截断”并不意味着把整个项目历史注入 Agent，而是指在当前 Task 边界内不对状态事实进行相关性重排或语义删减。mem0ress 通过 Task、Turn、Timestamp 和协议文件天然限定状态范围，从而获得当前完整状态。
2. Picture Alignment Judge
### Picture Alignment Judge：补足 Requirements 无法穷尽的语义验收

Requirements 是 Picture 的必要条件，但不是充分条件。即使所有 Requirements 均已满足，实际产出仍可能无法达成 Picture 所描述的利益相关者可感知成功状态。

Judge Agent 的 Tier 3 并不是重复验证 Requirements，而是检验 Requirements 与 Picture 之间是否仍存在剩余语义偏差。它只在任务接近关闭、Requirements 已满足或接近满足、且 Picture 存在语义验收空间时触发。

Tier 3 的输出不是任意主观评价，而是结构化的语义偏差报告，包括 residual_gap、stakeholder_risk、can_close_task 和 human_confirmation_required。若证据不足，Tier 3 必须返回 UNCERTAIN，而不是强行 PASS 或 FAIL。
结论
你这两个点都应该保留。

我的修正意见是：

“不排序、不挑选、不截断”是对的，但要明确它发生在 Task-local 边界内，核心是 Faithful Projection。

Judge Agent 用 LLM 判断也是对的，但它判断的不是一切，而是 Requirements 无法穷尽 Picture 的剩余语义差。

这样写之后，你的 spec 会更强：
既不会退回到传统 memory / RAG 的相关性拼接，也不会让 Judge Agent 变成无边界的主观裁判。



是的，Judge Agent 用 LLM 判断 Picture 这一块，确实是整套 spec 里最薄弱、但也最有价值的部分。

因为 Picture 本质上不是一个简单测试条件，而是一个利益相关者可感知的成功状态。它通常包含体验、意图、语义、完整性、可接受性、上下文一致性这些东西。传统 Requirements 很难完全覆盖它，所以才需要 Judge Agent。

但问题也在这里：
如果设计得太松，Judge Agent 会变成“另一个模型发表主观意见”；
如果设计得太硬，它又会退化成 Requirements 检查，失去判断 Picture 的意义。

所以关键不是“要不要 LLM Judge”，而是：

如何把 LLM 对 Picture 的判断，从主观评价，约束成可审计、可复核、可追责的语义验收过程。

一、Picture 为什么不能完全由 Requirements 覆盖
你的 PRC 模型里，Picture / Requirements / Constraints 三者的关系非常重要。

我建议你这样定义：

Picture 是成功状态。
Requirements 是可验证条件。
Constraints 是不可逾越边界。

问题在于：Requirements 只能捕捉 Picture 中可以被明确列举、测试、度量的部分。

但 Picture 往往还包含：

用户是否真的觉得流程顺畅；
投资人是否能理解方案的确定性与风险；
一份 spec 是否真的让开发者知道下一步怎么实现；
一个登录功能是否真的达到“无需输入密码”的体验；
一份投资说明是否既有保障感又没有违法承诺；
一个 Agent 是否真的没有偏离用户最初想要的东西。
这些东西不容易被简单测试项覆盖。

例如：

Picture:
用户无需输入密码即可通过企业 SSO 无缝进入工作台。

Requirements:
- 支持 Google OAuth
- 支持 GitHub OAuth
- callback 返回 200
- session 创建成功
即使 Requirements 都通过，也可能出现：

页面仍显示“请输入本地密码”的输入框；
用户第一次登录后还要绑定本地账号密码；
登录成功后跳到错误页面；
错误提示让用户以为登录失败；
流程技术上通过，但体验上不是“无缝进入”。
这就是 Requirements 和 Picture 之间的剩余差。

Judge Agent 的存在价值就在这里：

它不是检查 Requirements 是否通过，而是检查 Requirements 通过之后，Picture 是否仍然存在语义缺口。

二、Judge Agent 判断 Picture 的本质：不是“打分”，而是“寻找剩余偏差”
我建议你不要把 Tier 3 定义为：

LLM 判断 Picture 是否达成。

这个说法太宽。

更准确地说：

Tier 3 是 Residual Gap Detection。

中文可以叫：

剩余语义偏差检测。

它的任务不是泛泛地评价“好不好”，而是回答一个非常具体的问题：

在 Requirements 已经通过或接近通过的情况下，实际产出是否仍存在足以阻止 Picture 被认可的偏差？

这个定义非常关键。

它把 Judge Agent 的角色从“主观裁判”变成了“缺口检查器”。

三、建议把 Tier 3 拆成五个判断层
我建议你不要让 Judge Agent 直接输出 PASS / FAIL。
它应该按五层结构判断 Picture。

1. Picture Parsing：解析 Picture 的成功状态
第一步，Judge Agent 要先拆解 Picture。

不是拆成 Requirements，而是拆成几个语义维度：

picture_claims:
  - id: P-1
    claim: 用户可以通过 Google OAuth 登录
    dimension: function
  - id: P-2
    claim: 用户不需要输入本地密码
    dimension: user_experience
  - id: P-3
    claim: 登录成功后进入系统首页
    dimension: outcome
这一步很重要。

因为如果不先解析 Picture，LLM 很容易凭整体印象判断。

你需要让它明确：

Picture 里到底包含哪些可感知承诺？

这不是 Requirements，而是 Picture 的语义声明。

2. Evidence Mapping：把证据映射到 Picture
第二步，Judge Agent 不能凭空判断。它必须把已有证据映射到每个 Picture claim。

例如：

evidence_mapping:
  - picture_claim_id: P-1
    evidence:
      - R-1 passed: Google login button exists
      - R-2 passed: OAuth callback integration test passed
    evidence_strength: strong

  - picture_claim_id: P-2
    evidence:
      - C-1 passed: no local password prompt detected
    evidence_strength: medium

  - picture_claim_id: P-3
    evidence:
      - R-3 passed: session created
    evidence_strength: weak
    concern: session created does not prove redirect to homepage
这一步能防止 LLM 乱判。

3. Residual Gap Detection：寻找剩余偏差
第三步才是核心。

Judge Agent 要问：

有没有哪个 Picture claim 没有被 Requirements 或证据充分覆盖？
有没有 Requirements 全通过但 Picture 仍可能失败的地方？
有没有用户可感知层面的偏差？
有没有利益相关者会认为“这不是我要的”的风险？
输出：

residual_gaps:
  - id: RG-1
    picture_claim_id: P-3
    description: "session 创建成功不等于用户已经进入系统首页。缺少 redirect 行为或 UI 流程证据。"
    severity: medium
    closure_blocking: true
这就是 Tier 3 的核心价值。

4. Stakeholder Acceptance Risk：判断利益相关者接受风险
Picture 是利益相关者可感知的成功状态，所以 Judge Agent 必须判断：

即使 Requirements 通过，利益相关者是否仍可能不接受？

例如：

stakeholder_acceptance:
  risk_level: medium
  reason: >
    当前证据能证明 OAuth 技术流程基本可用，
    但不能证明用户登录后直接进入首页。
    如果用户仍停留在登录页或绑定页，Picture 不成立。
这比简单的“语义是否对齐”更有用。

5. Closure Recommendation：给出是否可关闭建议
最后才输出是否可以关闭任务：

closure_recommendation:
  can_close_task: false
  reason: "P-3 缺少足够证据，存在 closure-blocking residual gap。"
  required_actions:
    - "补充登录后 redirect 到首页的测试"
    - "提供端到端流程截图或测试日志"
注意：

Judge Agent 不是直接关闭任务，而是建议关闭或不关闭。

四、建议 Tier 3 输出结构
我建议你把 Tier 3 的标准输出固定成这样：

tier_3:
  name: picture_alignment_check
  result: PASS | FAIL | UNCERTAIN | SKIPPED

  picture_claims:
    - id: P-1
      claim: ...
      dimension: function | experience | outcome | policy | document_quality | stakeholder_acceptance

  evidence_mapping:
    - picture_claim_id: P-1
      evidence:
        - source: requirement
          id: R-1
          result: passed
          note: ...
        - source: test
          ref: ...
          result: passed
      evidence_strength: strong | medium | weak | none

  residual_gaps:
    - id: RG-1
      picture_claim_id: P-3
      description: ...
      severity: low | medium | high | critical
      closure_blocking: true | false
      suggested_fix: ...

  stakeholder_acceptance:
    risk_level: low | medium | high
    reason: ...

  human_confirmation:
    required: true | false
    reason: ...

  closure_recommendation:
    can_close_task: true | false
    reason: ...
    required_actions: []
这个结构非常重要。
它把 LLM 判断变成了一个有步骤、有证据、有缺口、有结论的过程。

五、Tier 3 的输入必须被严格限制
Judge Agent 最容易出问题的地方是输入太乱。

我建议 Tier 3 只能读取这些内容：

1. 当前 Task 的 Picture
2. 当前 Task 的 Requirements 及验证结果
3. 当前 Task 的 Constraints 状态
4. 当前 Task 的 Todos / Subtasks 完成状态
5. 最新 Judge Tier 0/1/2 结果
6. 未解决 Gotchas
7. Data Plane 引用的实际产出证据
8. 必要的父任务摘要
不能读取：

完整历史对话；
完整项目任务树；
无关兄弟任务；
过期需求；
未经引用的外部文档；
模型自己回忆的内容。
这和你的 Faithful Projection 是一致的。

Judge Agent 的判断必须在当前 Task-local 平面内完成。

六、Tier 3 应该什么时候触发？
我建议分成三种触发模式。

1. Closure Gate：任务关闭前强制触发
当任务准备从 IN_PROGRESS 进入 COMPLETED 时，如果 Picture 包含语义体验、文档质量、用户接受、业务意图，就触发 Tier 3。

trigger:
  event: before_task_close
  required: true
这是最重要的触发。

2. Uncertainty Gate：Requirements 通过但仍不确定时触发
例如：

Requirements 全绿；
Constraints 没问题；
Todos 全完成；
但 Agent 仍不确定 Picture 是否达成。
触发：

trigger:
  event: requirements_passed_picture_uncertain
  required: true
3. Stakeholder Gate：用户或父任务要求时触发
例如父任务 Agent 觉得子任务 summary 不足，要求子任务重新进行 Picture alignment。

trigger:
  event: stakeholder_requested
  required: true
七、Tier 3 不应该频繁触发
我建议你明确写：

Tier 3 不是每轮执行检查，而是任务接近关闭时的语义验收关卡。

否则成本高，而且会扰乱执行。

Tier 0/1/2 可以每轮跑；Tier 3 应该更克制。

Tier 0：每轮可跑
Tier 1：每轮可跑
Tier 2：关键节点跑
Tier 3：关闭前或不确定时跑
八、Picture 类型不同，Judge 方法也不同
这是你 spec 现在还没有展开的关键点。

不是所有 Picture 都一样。不同 Picture 需要不同的 Tier 3 判断方式。

我建议你给 Picture 增加 picture_type 或 dimensions。

1. Functional Picture
例如：

用户可以通过 Google OAuth 登录。
判断重点：

功能是否闭环；
路径是否完整；
是否有测试证据；
是否有边界异常。
2. Experience Picture
例如：

用户无需感知复杂配置即可完成登录。
判断重点：

用户流程；
提示语；
交互摩擦；
是否有反直觉步骤。
3. Document Picture
例如：

开发者读完 spec 后可以直接实现 MVP。
判断重点：

是否有结构；
是否有字段；
是否有示例；
是否有边界；
是否有歧义；
是否能落地。
4. Business Picture
例如：

投资人读完说明后能理解投资结构、产权对应和风险边界。
判断重点：

是否清楚；
是否稳健；
是否过度承诺；
是否遗漏风险；
是否符合利益相关者关切。
5. Safety / Compliance Picture
例如：

方案不能产生保本承诺或医疗诊断误导。
判断重点：

合规风险；
越界表达；
不可承诺内容；
责任边界。
你可以这样定义：

picture:
  text: >
    投资人读完说明后，可以理解投资结构、产权对应和风险边界。
  dimensions:
    - business_understanding
    - legal_safety
    - stakeholder_acceptance
Judge Agent 根据 dimensions 使用不同 rubric。

九、需要为 Tier 3 设计 Rubric，而不是只给 Prompt
这是最关键的增强。

Prompt 只是指令，Rubric 才是标准。

建议每个 Picture dimension 有一个 rubric。

例如针对 document_quality：

rubric:
  dimension: document_quality
  checks:
    - id: DQ-1
      question: 文档是否明确说明目标读者？
    - id: DQ-2
      question: 文档是否给出可执行步骤？
    - id: DQ-3
      question: 文档是否区分必须项和可选项？
    - id: DQ-4
      question: 文档是否有足够示例？
    - id: DQ-5
      question: 是否存在会阻碍实现的关键歧义？
针对 user_experience：

rubric:
  dimension: user_experience
  checks:
    - id: UX-1
      question: 用户是否需要执行 Picture 中没有暗示的额外步骤？
    - id: UX-2
      question: 是否存在会让用户误以为失败的提示？
    - id: UX-3
      question: 是否存在与 Picture 相反的界面元素？
针对 stakeholder_acceptance：

rubric:
  dimension: stakeholder_acceptance
  checks:
    - id: SA-1
      question: 利益相关者的核心关切是否被回应？
    - id: SA-2
      question: 是否存在表面满足 Requirements 但实际偏离意图的地方？
    - id: SA-3
      question: 是否需要人工确认偏好或风险接受？
这样 Judge Agent 就不是“随便判断”，而是“按 rubric 评估”。

十、Tier 3 的结果不应该覆盖 Requirements
很重要。

如果 Tier 3 发现 Picture 没达成，它不应该直接篡改 Requirements。

它应该输出：

suggested_requirement_updates:
  - proposed_id: R-4
    text: 登录成功后必须自动跳转到系统首页。
    reason: "当前 Picture 包含进入首页的成功状态，但 Requirements 没有覆盖该行为。"
这样做的好处是：

不破坏原始 Requirements；

暴露 Requirements 的缺口；

让主 Agent 或人类决定是否接受新 Requirement；

让 Picture 的语义判断反哺 PRC。

这很漂亮。

Tier 3 不只是验收工具，还是 Requirements 完备性反馈机制。

十一、建议增加一个新概念：Picture Claims
我认为这是解决 Judge Agent 薄弱问题的关键。

不要让 Picture 只是一整段自然语言。
在任务创建时，可以让 Agent 从 Picture 中提取 picture_claims。

例如：

picture:
  text: >
    用户可以通过 Google OAuth 完成登录，
    整个过程中不需要输入本地密码，
    登录成功后进入系统首页。

picture_claims:
  - id: P-1
    text: 用户可以通过 Google OAuth 完成登录
    dimension: function
  - id: P-2
    text: 整个过程中不需要输入本地密码
    dimension: user_experience
  - id: P-3
    text: 登录成功后进入系统首页
    dimension: outcome
这不是把 Picture 降级成 Requirements，而是为 Tier 3 提供语义锚点。

区别是：

Requirement 是验收条件。
Picture Claim 是成功图景的语义组成。
Requirement 可以验证，Picture Claim 用于语义覆盖检查。

十二、Tier 3 最终判断逻辑
建议你把 Tier 3 的结论规则写死：

如果存在 high/critical 且 closure_blocking 的 residual_gap → FAIL
如果存在 evidence_strength = none 的核心 Picture Claim → UNCERTAIN
如果 stakeholder_acceptance risk = high → FAIL 或 NEEDS_USER
如果全部 Picture Claims 有 medium 以上证据覆盖，且无 blocking residual_gap → PASS
如果证据不足但无法判断是否失败 → UNCERTAIN
这样它就不是任意判断。

十三、建议的 Judge Agent 完整流程
可以写成：

Step 1: 读取当前 Task-local 状态平面
Step 2: 解析 Picture Claims
Step 3: 读取 Requirements 验证结果
Step 4: 将 evidence 映射到 Picture Claims
Step 5: 识别 Requirements 未覆盖的 Picture Claims
Step 6: 识别 residual gaps
Step 7: 判断 stakeholder acceptance risk
Step 8: 输出 PASS / FAIL / UNCERTAIN
Step 9: 给出 can_close_task 和 required_actions
Step 10: 可选提出 suggested_requirement_updates
这就是一个完整的 Picture Alignment Judge。

十四、可以写进 spec 的正式段落
你可以直接用下面这段。

### Tier 3: Picture Alignment Check

Tier 3 的职责不是重复验证 Requirements，而是检验 Requirements 无法穷尽的 Picture 语义缺口。

在 mem0ress 中，Picture 表示利益相关者可感知的成功状态；Requirements 表示可独立验证的条件。Requirements 是 Picture 的必要条件，但不是充分条件。因此，即使所有 Requirements 均已通过，任务仍可能因为用户体验、语义完整性、业务意图或利益相关者接受度不足而未真正达成 Picture。

Tier 3 通过 Picture Alignment Judge 执行剩余语义偏差检测。Judge Agent 首先将 Picture 解析为若干 Picture Claims，然后将 Requirements 结果、Constraints 状态、Data Plane 证据、未解决 Gotchas 和实际产出映射到这些 Claims 上。若某个核心 Picture Claim 缺少证据覆盖，或存在足以阻止利益相关者认可任务完成的 residual gap，则任务不得关闭。

Tier 3 的输出不是主观评价，而是结构化的语义偏差报告，包括 picture_claims、evidence_mapping、residual_gaps、stakeholder_acceptance、human_confirmation 和 closure_recommendation。

当证据不足时，Tier 3 必须返回 UNCERTAIN，而不是强行 PASS 或 FAIL。
十五、我对你系统的更深判断
你这个设计里，Judge Agent 其实不只是“验收器”。

它还有三个更深的作用：

1. 防止勾选心态
Agent 很容易完成所有 Todo，然后以为任务完成。
Judge Agent 通过 Picture 检查防止这种问题。

2. 发现 Requirements 不完备
如果 Picture 有语义成分没有被 Requirements 覆盖，Judge Agent 会暴露这个缺口。

这能反过来提高任务定义质量。

3. 保护利益相关者意图
Requirements 是工程语言，Picture 是利益相关者语言。
Judge Agent 是两者之间的桥。

这一点非常有价值。

你的系统真正高级的地方不是“有 Judge”，而是：

它承认可验证条件永远无法完全覆盖人的意图，因此需要一个受约束的语义验收层。

最终建议
我建议你把 Judge Agent 的 Tier 3 从简单的：

LLM-as-a-Judge 判断 Picture 是否达成

升级为：

Picture Alignment Judge：在 Requirements 通过后，对 Picture Claims 进行证据映射、剩余偏差检测和利益相关者接受风险判断。

核心结构就是：

Picture
  ↓
Picture Claims
  ↓
Evidence Mapping
  ↓
Residual Gap Detection
  ↓
Stakeholder Acceptance Risk
  ↓
Closure Recommendation
这套设计会让 Tier 3 从“薄弱的 LLM 判断”变成真正有协议价值的语义验收机制。
