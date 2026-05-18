const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "mem0ress";
pres.title = "CAP: 认知对齐平面架构规约";

// Color palette - Deep blue/navy theme for technical presentation
const C = {
  navy: "1A237E",
  blue: "1565C0",
  lightBlue: "E3F2FD",
  white: "FFFFFF",
  dark: "212121",
  gray: "616161",
  lightGray: "F5F5F5",
  accent: "FFC107",
  green: "2E7D32",
  orange: "FF8F00",
  red: "C62828",
  purple: "6A1B9A",
  teal: "00838F",
};

// ============================================================
// Slide 1: Title
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.navy };

  // Title
  slide.addText("CAP", {
    x: 0.5, y: 1.5, w: 9, h: 1.2,
    fontSize: 72, fontFace: "Arial", bold: true,
    color: C.white, align: "center", margin: 0
  });

  slide.addText("认知对齐平面", {
    x: 0.5, y: 2.7, w: 9, h: 0.7,
    fontSize: 36, fontFace: "Arial",
    color: C.accent, align: "center", margin: 0
  });

  slide.addText("Cognitive Alignment Plane", {
    x: 0.5, y: 3.4, w: 9, h: 0.5,
    fontSize: 20, fontFace: "Arial", italic: true,
    color: C.lightBlue, align: "center", margin: 0
  });

  // Subtitle
  slide.addText("架构规约 v0.6", {
    x: 0.5, y: 4.3, w: 9, h: 0.4,
    fontSize: 18, fontFace: "Arial",
    color: C.white, align: "center", margin: 0
  });

  // Bottom line
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 3, y: 5.0, w: 4, h: 0.04,
    fill: { color: C.accent }, line: { color: C.accent, width: 0 }
  });
}

// ============================================================
// Slide 2: 背景 - 问题
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.white };

  // Header bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("背景：当前 AI Agent 的四个结构性问题", {
    x: 0.5, y: 0.15, w: 9, h: 0.5,
    fontSize: 22, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });

  // Four problems in 2x2 grid
  const problems = [
    { title: "数据汤困境", desc: "历史对话、代码片段、废弃架构融合成没有边界的混沌数据，导致上下文污染和认知噪声", icon: "01" },
    { title: "意图迷失", desc: "记忆系统不感知目标，只能回答\"之前怎么处理\"，无法回答\"我当前目标是什么、该往哪走\"", icon: "02" },
    { title: "高频数据语义坍缩", desc: "高频迭代中反复操作产生的记忆在向量空间高度重叠，Top-K 检索召回语义等价但时序不同的冗余片段", icon: "03" },
    { title: "向量检索叠加向量检索", desc: "在 LLM 已有的向量检索基础上再对会话数据做一层向量检索，两层检索面临同样的根本困境", icon: "04" },
  ];

  const colors = [C.red, C.orange, C.purple, C.teal];
  problems.forEach((p, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.5 + col * 4.7;
    const y = 1.1 + row * 2.1;

    // Card background
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 4.3, h: 1.9,
      fill: { color: C.lightGray }, line: { color: "E0E0E0", width: 1 }
    });

    // Left accent bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.08, h: 1.9,
      fill: { color: colors[i] }, line: { color: colors[i], width: 0 }
    });

    // Number
    slide.addText(p.icon, {
      x: x + 0.2, y: y + 0.15, w: 0.5, h: 0.4,
      fontSize: 20, fontFace: "Arial", bold: true,
      color: colors[i], margin: 0
    });

    // Title
    slide.addText(p.title, {
      x: x + 0.7, y: y + 0.15, w: 3.4, h: 0.4,
      fontSize: 16, fontFace: "Arial", bold: true,
      color: C.dark, margin: 0
    });

    // Description
    slide.addText(p.desc, {
      x: x + 0.2, y: y + 0.6, w: 3.9, h: 1.2,
      fontSize: 11, fontFace: "Arial",
      color: C.gray, margin: 0
    });
  });

  // Bottom insight
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 5.2, w: 9, h: 0.35,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("核心矛盾：Agent 不缺信息，缺的是对\"当前自己在哪里、目标偏了没有、还差什么\"的持续感知", {
    x: 0.6, y: 5.22, w: 8.8, h: 0.3,
    fontSize: 11, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });
}

// ============================================================
// Slide 3: 核心洞察 - 三个推导链
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("核心洞察：三个推导链", {
    x: 0.5, y: 0.15, w: 9, h: 0.5,
    fontSize: 22, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });

  const insights = [
    {
      num: "01",
      title: "上下文以目标为导向",
      quote: "上下文不是被维护的，而是被发现的",
      detail: "Agent 在每个任务开始时，根据当前目标动态构建相关的上下文视图。否定\"存储优先\"的记忆架构，转向\"目标导向的认知架构\""
    },
    {
      num: "02",
      title: "任务是信息的完整单元",
      quote: "任务天然封装目标、行动、结果和上下文",
      detail: "事件天然封装了目标、行动、结果和上下文——这些维度共同提供了认知的边界和检索线索。孤立的知识点或对话片段无法成为可靠的认知锚点"
    },
    {
      num: "03",
      title: "任务需要的是认知，而非记忆",
      quote: "一种能让自己随时判断\"我在哪、目标偏没偏、还差什么\"的能力",
      detail: "真正稀缺的不是更多信息，而是判断力。一个始终知道自己在做什么的 Agent，对任务的掌控力远强于一个存储了十年对话的 Agent"
    },
  ];

  insights.forEach((ins, i) => {
    const y = 1.0 + i * 1.5;

    // Number circle
    slide.addShape(pres.shapes.OVAL, {
      x: 0.5, y: y, w: 0.5, h: 0.5,
      fill: { color: C.navy }, line: { color: C.navy, width: 0 }
    });
    slide.addText(ins.num, {
      x: 0.5, y: y + 0.08, w: 0.5, h: 0.35,
      fontSize: 14, fontFace: "Arial", bold: true,
      color: C.white, align: "center", margin: 0
    });

    // Title
    slide.addText(ins.title, {
      x: 1.2, y: y, w: 4, h: 0.4,
      fontSize: 16, fontFace: "Arial", bold: true,
      color: C.dark, margin: 0
    });

    // Quote (italic)
    slide.addText(ins.quote, {
      x: 1.2, y: y + 0.4, w: 8, h: 0.35,
      fontSize: 12, fontFace: "Arial", italic: true,
      color: C.blue, margin: 0
    });

    // Detail
    slide.addText(ins.detail, {
      x: 1.2, y: y + 0.75, w: 8.3, h: 0.6,
      fontSize: 10, fontFace: "Arial",
      color: C.gray, margin: 0
    });

    // Arrow between
    if (i < 2) {
      slide.addShape(pres.shapes.LINE, {
        x: 0.75, y: y + 0.55, w: 0, h: 0.9,
        line: { color: C.navy, width: 1.5, dashType: "dash" }
      });
    }
  });
}

// ============================================================
// Slide 4: 核心解法概览
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("核心解法概览", {
    x: 0.5, y: 0.15, w: 9, h: 0.5,
    fontSize: 22, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });

  // Three boxes: PRC, Status Plane, Data Plane
  const boxes = [
    { title: "任务信息模型 (PRC)", color: C.green, items: ["Picture — 方向锚点", "Requirements — 可验证标准", "Constraints — 边界约束"] },
    { title: "状态平面 (Status Plane)", color: C.orange, items: ["\"我在哪、做到哪了\"", "任务树结构", "Todo 完成度", "Gotchas 指针"] },
    { title: "数据平面 (Data Plane)", color: C.blue, items: ["\"当前操作哪个版本\"", "各仓库 commit ID", "Git 底层可追溯"] },
  ];

  boxes.forEach((box, i) => {
    const x = 0.5 + i * 3.1;

    // Card
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.0, w: 2.9, h: 2.8,
      fill: { color: C.lightGray }, line: { color: box.color, width: 2 }
    });

    // Title bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.0, w: 2.9, h: 0.5,
      fill: { color: box.color }, line: { color: box.color, width: 0 }
    });
    slide.addText(box.title, {
      x, y: 1.05, w: 2.9, h: 0.4,
      fontSize: 11, fontFace: "Arial", bold: true,
      color: C.white, align: "center", margin: 0
    });

    // Items
    box.items.forEach((item, j) => {
      slide.addText(item, {
        x: x + 0.15, y: 1.6 + j * 0.5, w: 2.6, h: 0.45,
        fontSize: 11, fontFace: "Arial",
        color: C.dark, margin: 0
      });
    });
  });

  // Bottom: Judge Agent
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.0, w: 9, h: 0.06,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });

  slide.addText("任务检验：Judge Agent 执行四层检验", {
    x: 0.5, y: 4.15, w: 9, h: 0.35,
    fontSize: 14, fontFace: "Arial", bold: true,
    color: C.dark, margin: 0
  });

  const tiers = [
    { name: "Tier 0: 约束检查", desc: "Constraints 是否被逾越" },
    { name: "Tier 1: 进度检查", desc: "Todo 完成 + 子任务关闭" },
    { name: "Tier 2: 验收检查", desc: "Requirements 达标验证" },
    { name: "Tier 3: 语义对齐", desc: "Picture 剩余语义偏差" },
  ];
  tiers.forEach((t, i) => {
    const x = 0.5 + i * 2.3;
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y: 4.55, w: 2.15, h: 0.9,
      fill: { color: C.lightBlue }, line: { color: C.blue, width: 1 }
    });
    slide.addText(t.name, {
      x, y: 4.6, w: 2.15, h: 0.35,
      fontSize: 10, fontFace: "Arial", bold: true,
      color: C.navy, align: "center", margin: 0
    });
    slide.addText(t.desc, {
      x, y: 4.95, w: 2.15, h: 0.4,
      fontSize: 9, fontFace: "Arial",
      color: C.gray, align: "center", margin: 0
    });
  });
}

// ============================================================
// Slide 5: 设计决策
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("设计决策", {
    x: 0.5, y: 0.15, w: 9, h: 0.5,
    fontSize: 22, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });

  const decisions = [
    {
      num: "1",
      title: "选择任务作为认知单元",
      reason: "任务天然封装目标、可验证条件和执行边界，三位一体构成可判断的认知单元。所有认知单元同类同构，系统复杂性维持在常数级别"
    },
    {
      num: "2",
      title: "选择单任务 Agent 责任模型",
      reason: "Agent 在任意时刻只绑定一个活跃 Task，认知平面只围绕当前 Task 组装。认知边界是 Task，不是 Project"
    },
    {
      num: "3",
      title: "选择 PRC 作为任务信息模型",
      reason: "Picture 定方向，Requirements 提供可检验的验收条件，Constraints 划定不可逾越的边界，三者缺一不可"
    },
    {
      num: "4",
      title: "选择任务信息平面来呈现认知",
      reason: "状态平面回答\"做到了什么\"，数据平面回答\"当前操作哪个版本\"，两个维度认知性质不同，必须分开处理"
    },
    {
      num: "5",
      title: "选择状态变更驱动认知构建",
      reason: "只记录导致目标推进或路径修正的状态变更，不记录过程录像。认知以轮次为周期，感知→构建→挂载构成完整闭环"
    },
  ];

  decisions.forEach((d, i) => {
    const y = 0.95 + i * 0.9;

    // Number
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y, w: 0.4, h: 0.4,
      fill: { color: C.navy }, line: { color: C.navy, width: 0 }
    });
    slide.addText(d.num, {
      x: 0.5, y: y + 0.05, w: 0.4, h: 0.3,
      fontSize: 14, fontFace: "Arial", bold: true,
      color: C.white, align: "center", margin: 0
    });

    // Title
    slide.addText(d.title, {
      x: 1.05, y, w: 8.4, h: 0.35,
      fontSize: 14, fontFace: "Arial", bold: true,
      color: C.dark, margin: 0
    });

    // Reason
    slide.addText(d.reason, {
      x: 1.05, y: y + 0.35, w: 8.4, h: 0.5,
      fontSize: 10, fontFace: "Arial",
      color: C.gray, margin: 0
    });

    if (i < 4) {
      slide.addShape(pres.shapes.LINE, {
        x: 0.5, y: y + 0.82, w: 9, h: 0,
        line: { color: "E0E0E0", width: 0.5 }
      });
    }
  });
}

// ============================================================
// Slide 6: PRC 三要素
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("任务信息模型：PRC 三要素", {
    x: 0.5, y: 0.15, w: 9, h: 0.5,
    fontSize: 22, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });

  const prcItems = [
    {
      name: "Picture",
      subtitle: "图景",
      role: "方向锚点 · 任务完成的充分条件",
      desc: "任务完成后的宏观景象，以自然语言描绘。必须是利益相关者能想象的状态，而不是实现路径",
      example: "✓ \"用户不用输入密码就能登录\"\n✗ \"用 OAuth 2.0 实现登录\"（这是路径）",
      color: C.green
    },
    {
      name: "Requirements",
      subtitle: "需求",
      role: "可验证标准 · Picture 的必要条件",
      desc: "将 Picture 转化为具体的检验点。必须可独立验证（存在可运行的验证命令或明确的数值指标）",
      example: "✓ \"Google OAuth 登录成功\"\n✗ \"界面美观大方\"（无法客观验证）",
      color: C.blue
    },
    {
      name: "Constraints",
      subtitle: "约束",
      role: "边界约束 · 贯穿全程的约束线",
      desc: "任务的外部属性，定义过程和结果的边界条件。违反 Constraints 即使 Picture 看似达成，任务也不算完成",
      example: "✓ \"不存储用户明文密码\"\n✓ \"不超过 3 次重试\"",
      color: C.red
    },
  ];

  prcItems.forEach((item, i) => {
    const x = 0.5 + i * 3.1;

    // Card
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.0, w: 2.9, h: 4.4,
      fill: { color: C.lightGray }, line: { color: item.color, width: 2 }
    });

    // Top bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.0, w: 2.9, h: 0.7,
      fill: { color: item.color }, line: { color: item.color, width: 0 }
    });
    slide.addText(item.name, {
      x, y: 1.05, w: 2.9, h: 0.35,
      fontSize: 14, fontFace: "Arial", bold: true,
      color: C.white, align: "center", margin: 0
    });
    slide.addText(item.subtitle, {
      x, y: 1.35, w: 2.9, h: 0.3,
      fontSize: 11, fontFace: "Arial",
      color: C.white, align: "center", margin: 0
    });

    // Role
    slide.addText(item.role, {
      x: x + 0.15, y: 1.8, w: 2.6, h: 0.45,
      fontSize: 10, fontFace: "Arial", bold: true, italic: true,
      color: item.color, margin: 0
    });

    // Desc
    slide.addText(item.desc, {
      x: x + 0.15, y: 2.25, w: 2.6, h: 1.3,
      fontSize: 10, fontFace: "Arial",
      color: C.dark, margin: 0
    });

    // Divider
    slide.addShape(pres.shapes.LINE, {
      x: x + 0.15, y: 3.5, w: 2.6, h: 0,
      line: { color: "BDBDBD", width: 0.5 }
    });

    // Example label
    slide.addText("示例", {
      x: x + 0.15, y: 3.6, w: 2.6, h: 0.3,
      fontSize: 9, fontFace: "Arial", bold: true,
      color: C.gray, margin: 0
    });

    // Example
    slide.addText(item.example, {
      x: x + 0.15, y: 3.85, w: 2.6, h: 1.4,
      fontSize: 9, fontFace: "Arial",
      color: C.gray, margin: 0
    });
  });
}

// ============================================================
// Slide 7: 状态平面 vs 数据平面
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("双平面分离：状态平面 vs 数据平面", {
    x: 0.5, y: 0.15, w: 9, h: 0.5,
    fontSize: 22, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });

  // Two columns
  // Status Plane
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.0, w: 4.3, h: 3.8,
    fill: { color: C.lightGray }, line: { color: C.orange, width: 2 }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.0, w: 4.3, h: 0.55,
    fill: { color: C.orange }, line: { color: C.orange, width: 0 }
  });
  slide.addText("状态平面 Status Plane", {
    x: 0.5, y: 1.05, w: 4.3, h: 0.45,
    fontSize: 13, fontFace: "Arial", bold: true,
    color: C.white, align: "center", margin: 0
  });

  const spItems = [
    { label: "回答", value: "\"我在哪、做到哪了、目标偏了没有\"" },
    { label: "挂载时机", value: "Agent 唤醒时强制挂载" },
    { label: "内容", value: "任务树结构、Todo 完成度、任务状态、Gotchas 指针" },
    { label: "组装来源", value: "task.md、Session 历史切片、Data Plane 版本指针" },
  ];
  spItems.forEach((it, i) => {
    slide.addText(it.label, {
      x: 0.65, y: 1.65 + i * 0.75, w: 1.1, h: 0.3,
      fontSize: 9, fontFace: "Arial", bold: true,
      color: C.orange, margin: 0
    });
    slide.addText(it.value, {
      x: 0.65, y: 1.9 + i * 0.75, w: 4.0, h: 0.45,
      fontSize: 10, fontFace: "Arial",
      color: C.dark, margin: 0
    });
  });

  // Data Plane
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.0, w: 4.3, h: 3.8,
    fill: { color: C.lightGray }, line: { color: C.blue, width: 2 }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.0, w: 4.3, h: 0.55,
    fill: { color: C.blue }, line: { color: C.blue, width: 0 }
  });
  slide.addText("数据平面 Data Plane", {
    x: 5.2, y: 1.05, w: 4.3, h: 0.45,
    fontSize: 13, fontFace: "Arial", bold: true,
    color: C.white, align: "center", margin: 0
  });

  const dpItems = [
    { label: "回答", value: "\"当前操作的是哪个版本的代码\"" },
    { label: "挂载时机", value: "按需展开，不默认加载" },
    { label: "内容", value: "各仓库当前 commit ID\n格式：{ repo_name: \"{ commit_id }\" }" },
    { label: "底层", value: "Git — 可追溯、可 revert" },
  ];
  dpItems.forEach((it, i) => {
    slide.addText(it.label, {
      x: 5.35, y: 1.65 + i * 0.75, w: 1.1, h: 0.3,
      fontSize: 9, fontFace: "Arial", bold: true,
      color: C.blue, margin: 0
    });
    slide.addText(it.value, {
      x: 5.35, y: 1.9 + i * 0.75, w: 4.0, h: 0.45,
      fontSize: 10, fontFace: "Arial",
      color: C.dark, margin: 0
    });
  });

  // Bottom note
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.95, w: 9, h: 0.55,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("关键设计：数据平面可 revert，外部状态不会因数据 revert 而回退，因此认知无法回退，只能基于当下向前构建", {
    x: 0.65, y: 5.02, w: 8.7, h: 0.4,
    fontSize: 11, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });
}

// ============================================================
// Slide 8: 目录任务拓扑
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("目录任务拓扑：拓扑即协议", {
    x: 0.5, y: 0.15, w: 9, h: 0.5,
    fontSize: 22, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });

  // Tree structure visualization
  const treeX = 1.5;
  const treeY = 1.2;

  // Root
  slide.addShape(pres.shapes.RECTANGLE, {
    x: treeX, y: treeY, w: 2.2, h: 0.45,
    fill: { color: C.green }, line: { color: C.green, width: 0 }
  });
  slide.addText(".CAP/tasks/", {
    x: treeX, y: treeY + 0.07, w: 2.2, h: 0.3,
    fontSize: 11, fontFace: "Courier New", bold: true,
    color: C.white, align: "center", margin: 0
  });

  // Vertical line from root
  slide.addShape(pres.shapes.LINE, {
    x: treeX + 1.1, y: treeY + 0.45, w: 0, h: 0.35,
    line: { color: C.gray, width: 1 }
  });

  // Parent task
  slide.addShape(pres.shapes.RECTANGLE, {
    x: treeX, y: treeY + 0.8, w: 2.2, h: 0.45,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("build_auth/", {
    x: treeX, y: treeY + 0.87, w: 2.2, h: 0.3,
    fontSize: 11, fontFace: "Courier New", bold: true,
    color: C.white, align: "center", margin: 0
  });

  // Vertical from parent
  slide.addShape(pres.shapes.LINE, {
    x: treeX + 1.1, y: treeY + 1.25, w: 0, h: 0.35,
    line: { color: C.gray, width: 1 }
  });

  // Horizontal for children
  slide.addShape(pres.shapes.LINE, {
    x: treeX - 0.3, y: treeY + 1.25, w: 2.8, h: 0,
    line: { color: C.gray, width: 1 }
  });

  // Child 1
  slide.addShape(pres.shapes.LINE, {
    x: treeX - 0.3, y: treeY + 1.25, w: 0, h: 0.35,
    line: { color: C.gray, width: 1 }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: treeX - 0.3, y: treeY + 1.6, w: 2.2, h: 0.45,
    fill: { color: C.blue }, line: { color: C.blue, width: 0 }
  });
  slide.addText("oauth_google/", {
    x: treeX - 0.3, y: treeY + 1.67, w: 2.2, h: 0.3,
    fontSize: 11, fontFace: "Courier New", bold: true,
    color: C.white, align: "center", margin: 0
  });

  // Child 2
  slide.addShape(pres.shapes.LINE, {
    x: treeX + 2.5, y: treeY + 1.25, w: 0, h: 0.35,
    line: { color: C.gray, width: 1 }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: treeX + 2.5, y: treeY + 1.6, w: 2.2, h: 0.45,
    fill: { color: C.blue }, line: { color: C.blue, width: 0 }
  });
  slide.addText("oauth_github/", {
    x: treeX + 2.5, y: treeY + 1.67, w: 2.2, h: 0.3,
    fontSize: 11, fontFace: "Courier New", bold: true,
    color: C.white, align: "center", margin: 0
  });

  // Key points on right
  const keyPoints = [
    {
      title: "拓扑即协议",
      desc: "父子关系由目录拓扑天然表达，不需 parent_id 字段重复声明。避免双重真相"
    },
    {
      title: "task_id 作为稳定身份",
      desc: "目录名可能因 rename / move / archive 变化，task_id 是稳定的 identity"
    },
    {
      title: "协作边界",
      desc: "父任务只依赖子任务 lifecycle state（COMPLETED / ABANDONED）和 deliverables，不依赖子任务内部执行过程"
    },
  ];

  keyPoints.forEach((kp, i) => {
    const y = 1.2 + i * 1.35;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 6.2, y, w: 3.3, h: 1.2,
      fill: { color: C.lightGray }, line: { color: "BDBDBD", width: 1 }
    });
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 6.2, y, w: 0.06, h: 1.2,
      fill: { color: C.navy }, line: { color: C.navy, width: 0 }
    });
    slide.addText(kp.title, {
      x: 6.4, y: y + 0.1, w: 3.0, h: 0.35,
      fontSize: 12, fontFace: "Arial", bold: true,
      color: C.dark, margin: 0
    });
    slide.addText(kp.desc, {
      x: 6.4, y: y + 0.45, w: 3.0, h: 0.7,
      fontSize: 10, fontFace: "Arial",
      color: C.gray, margin: 0
    });
  });
}

// ============================================================
// Slide 9: 文档数据模型
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("文档数据模型：四个核心文档", {
    x: 0.5, y: 0.15, w: 9, h: 0.5,
    fontSize: 22, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });

  const docs = [
    {
      name: "task.md",
      role: "任务声明",
      desc: "Picture / Requirements / Constraints 的唯一真源。任务创建时写入，运行时以它为准",
      write: "主 Agent（覆盖写）",
      color: C.green
    },
    {
      name: "session.md",
      role: "轮次快照序列",
      desc: "每轮次结束后的状态快照，含 data_plane 快照。每轮次结束后按时间追加",
      write: "主 Agent（追加写）",
      color: C.blue
    },
    {
      name: "gotchas.md",
      role: "偏差记录",
      desc: "带外追加，不阻塞主流程。偏差确认后追加",
      write: "主 Agent（追加写）",
      color: C.orange
    },
    {
      name: "judge.md",
      role: "Judge 检验记录",
      desc: "Judge Agent 检验记录，与 Task 生命周期同步。任务创建时生成空文件，检验后追加",
      write: "Judge Agent（追加写）",
      color: C.purple
    },
  ];

  docs.forEach((doc, i) => {
    const y = 0.95 + i * 1.05;

    // File icon box
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y, w: 1.8, h: 0.9,
      fill: { color: doc.color }, line: { color: doc.color, width: 0 }
    });
    slide.addText(doc.name, {
      x: 0.5, y: y + 0.25, w: 1.8, h: 0.4,
      fontSize: 13, fontFace: "Courier New", bold: true,
      color: C.white, align: "center", margin: 0
    });

    // Role
    slide.addText(doc.role, {
      x: 2.5, y, w: 2, h: 0.35,
      fontSize: 12, fontFace: "Arial", bold: true,
      color: doc.color, margin: 0
    });

    // Desc
    slide.addText(doc.desc, {
      x: 2.5, y: y + 0.35, w: 5.0, h: 0.55,
      fontSize: 10, fontFace: "Arial",
      color: C.dark, margin: 0
    });

    // Write owner
    slide.addText("写入方：" + doc.write, {
      x: 7.5, y: y + 0.25, w: 2.0, h: 0.4,
      fontSize: 9, fontFace: "Arial",
      color: C.gray, margin: 0
    });

    if (i < 3) {
      slide.addShape(pres.shapes.LINE, {
        x: 0.5, y: y + 0.97, w: 9, h: 0,
        line: { color: "E0E0E0", width: 0.5 }
      });
    }
  });

  // Design rationale
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 5.15, w: 9, h: 0.4,
    fill: { color: C.lightBlue }, line: { color: C.blue, width: 1 }
  });
  slide.addText("设计理由：消除隐藏状态 | 时间切片而非可变状态 | 与 Agent 工具生态无缝衔接", {
    x: 0.6, y: 5.2, w: 8.8, h: 0.3,
    fontSize: 10, fontFace: "Arial",
    color: C.navy, margin: 0
  });
}

// ============================================================
// Slide 10: 任务生命周期状态机
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("任务生命周期状态机", {
    x: 0.5, y: 0.15, w: 9, h: 0.5,
    fontSize: 22, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });

  // State boxes
  const states = [
    { name: "CREATED", desc: "模型已定义\n所有 Todo 未开始", color: C.gray, x: 0.5 },
    { name: "IN_PROGRESS", desc: "至少有一个\nTodo 已完成", color: C.blue, x: 2.7 },
    { name: "VERIFYING", desc: "任务检验进行中\n（瞬态）", color: C.orange, x: 4.9 },
    { name: "COMPLETED", desc: "目标达成", color: C.green, x: 7.1 },
  ];

  states.forEach((s, i) => {
    // Box
    slide.addShape(pres.shapes.RECTANGLE, {
      x: s.x, y: 1.2, w: 2.0, h: 1.1,
      fill: { color: s.color }, line: { color: s.color, width: 0 }
    });
    slide.addText(s.name, {
      x: s.x, y: 1.25, w: 2.0, h: 0.35,
      fontSize: 11, fontFace: "Arial", bold: true,
      color: C.white, align: "center", margin: 0
    });
    slide.addText(s.desc, {
      x: s.x + 0.05, y: 1.6, w: 1.9, h: 0.65,
      fontSize: 9, fontFace: "Arial",
      color: C.white, align: "center", margin: 0
    });

    // Arrow
    if (i < 3) {
      slide.addShape(pres.shapes.LINE, {
        x: s.x + 2.0, y: 1.75, w: 0.7, h: 0,
        line: { color: C.dark, width: 2 }
      });
      // Arrow head
      slide.addText("→", {
        x: s.x + 2.4, y: 1.55, w: 0.4, h: 0.4,
        fontSize: 18, fontFace: "Arial", bold: true,
        color: C.dark, align: "center", margin: 0
      });
    }
  });

  // ABANDONED state (below)
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 2.7, y: 2.6, w: 2.0, h: 0.9,
    fill: { color: C.red }, line: { color: C.red, width: 0 }
  });
  slide.addText("ABANDONED", {
    x: 2.7, y: 2.65, w: 2.0, h: 0.35,
    fontSize: 11, fontFace: "Arial", bold: true,
    color: C.white, align: "center", margin: 0
  });
  slide.addText("目标放弃", {
    x: 2.7, y: 3.0, w: 2.0, h: 0.4,
    fontSize: 9, fontFace: "Arial",
    color: C.white, align: "center", margin: 0
  });

  // Dashed arrows to ABANDONED
  slide.addShape(pres.shapes.LINE, {
    x: 1.5, y: 2.3, w: 0, h: 0.3,
    line: { color: C.gray, width: 1.5, dashType: "dash" }
  });
  slide.addShape(pres.shapes.LINE, {
    x: 4.7, y: 2.3, w: 0, h: 0.3,
    line: { color: C.gray, width: 1.5, dashType: "dash" }
  });
  slide.addText("↱", {
    x: 2.2, y: 2.2, w: 0.5, h: 0.4,
    fontSize: 16, fontFace: "Arial",
    color: C.gray, margin: 0
  });
  slide.addText("↰", {
    x: 4.7, y: 2.2, w: 0.5, h: 0.4,
    fontSize: 16, fontFace: "Arial",
    color: C.gray, margin: 0
  });

  // State transition rules
  const rules = [
    "CREATED → IN_PROGRESS：任意 Todo 被标记为完成",
    "CREATED → ABANDONED：任务废弃",
    "IN_PROGRESS → COMPLETED：检验通过",
    "IN_PROGRESS → ABANDONED：任务废弃",
    "VERIFYING：是瞬态，检验完成后立即转换到 COMPLETED 或 ABANDONED",
  ];
  rules.forEach((rule, i) => {
    slide.addText(rule, {
      x: 0.5, y: 3.65 + i * 0.35, w: 9, h: 0.3,
      fontSize: 10, fontFace: "Arial",
      color: C.dark, margin: 0
    });
  });
}

// ============================================================
// Slide 11: 执行循环
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("执行循环：感知 → 判断 → 更新", {
    x: 0.5, y: 0.15, w: 9, h: 0.5,
    fontSize: 22, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });

  const steps = [
    { num: "1", title: "认知构建", desc: "主 Agent 读取状态平面（PlaneAssembler 实时组装）", color: C.green },
    { num: "2", title: "执行", desc: "主 Agent 执行 Todo；可选：带外追加 gotchas.md", color: C.blue },
    { num: "3", title: "Session 写入", desc: "主 Agent 追加 session.md 快照；更新 task.md Todo 状态", color: C.orange },
    { num: "4", title: "检验触发", desc: "主 Agent 设 status → VERIFYING\n宿主框架启动 Judge Agent\nJudge Agent 执行四层检验\nJudge Agent 写入 judge.md\n主 Agent 读取 judge.md 结论\n主 Agent 退出 VERIFYING 状态", color: C.purple },
    { num: "5", title: "决策", desc: "主 Agent 自主决策下一步（修正 / 完成 / 废弃）", color: C.teal },
  ];

  steps.forEach((s, i) => {
    const x = 0.5 + (i % 3) * 3.1;
    const y = i < 3 ? 1.0 : 3.2;

    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 2.9, h: i === 3 ? 1.95 : 1.9,
      fill: { color: C.lightGray }, line: { color: s.color, width: 2 }
    });
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 2.9, h: 0.5,
      fill: { color: s.color }, line: { color: s.color, width: 0 }
    });
    slide.addText(s.num + ". " + s.title, {
      x, y: y + 0.08, w: 2.9, h: 0.35,
      fontSize: 12, fontFace: "Arial", bold: true,
      color: C.white, align: "center", margin: 0
    });
    slide.addText(s.desc, {
      x: x + 0.1, y: y + 0.55, w: 2.7, h: i === 3 ? 1.35 : 1.3,
      fontSize: 9, fontFace: "Arial",
      color: C.dark, margin: 0
    });
  });

  // Three participants
  slide.addShape(pres.shapes.LINE, {
    x: 0.5, y: 5.2, w: 9, h: 0,
    line: { color: C.navy, width: 1 }
  });
  slide.addText("三个参与方：", {
    x: 0.5, y: 5.25, w: 1.3, h: 0.3,
    fontSize: 10, fontFace: "Arial", bold: true,
    color: C.dark, margin: 0
  });
  slide.addText("主 Agent（执行）| Judge Agent（检验）| 宿主框架（基础设施保障）", {
    x: 1.8, y: 5.25, w: 7.5, h: 0.3,
    fontSize: 10, fontFace: "Arial",
    color: C.gray, margin: 0
  });
}

// ============================================================
// Slide 12: 四层检验关卡
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("任务检验：四层检验关卡", {
    x: 0.5, y: 0.15, w: 9, h: 0.5,
    fontSize: 22, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });

  const tiers = [
    {
      tier: "Tier 0",
      name: "约束检查",
      exec: "纯逻辑",
      dep: "task.md, session.md, gotchas.md",
      rule: "检查 Constraints 是否被逾越"
    },
    {
      tier: "Tier 1",
      name: "进度检查",
      exec: "纯逻辑",
      dep: "task.md",
      rule: "所有 Todo 步是否完成、所有直接子任务是否已关闭"
    },
    {
      tier: "Tier 2",
      name: "验收检查",
      exec: "运行测试命令",
      dep: "task.md, session.md",
      rule: "验证每个 Requirement 是否达标"
    },
    {
      tier: "Tier 3",
      name: "语义对齐",
      exec: "LLM 推断",
      dep: "task.md, session.md",
      rule: "检查 Requirements 无法穷尽的 Picture 剩余语义偏差"
    },
  ];

  // Header row
  const headers = ["关卡", "名称", "执行方式", "依赖文件", "规则"];
  const colXs = [0.5, 1.5, 3.5, 5.8, 7.5];
  const colWs = [0.9, 1.9, 2.2, 1.6, 2.2];
  headers.forEach((h, i) => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: colXs[i], y: 1.0, w: colWs[i], h: 0.4,
      fill: { color: C.navy }, line: { color: C.navy, width: 0 }
    });
    slide.addText(h, {
      x: colXs[i], y: 1.05, w: colWs[i], h: 0.3,
      fontSize: 10, fontFace: "Arial", bold: true,
      color: C.white, align: "center", margin: 0
    });
  });

  const rowColors = [C.red, C.orange, C.blue, C.purple];
  tiers.forEach((t, i) => {
    const y = 1.45 + i * 0.75;
    const vals = [t.tier, t.name, t.exec, t.dep, t.rule];
    vals.forEach((v, j) => {
      slide.addShape(pres.shapes.RECTANGLE, {
        x: colXs[j], y, w: colWs[j], h: 0.7,
        fill: { color: j === 0 ? rowColors[i] : C.lightGray },
        line: { color: "E0E0E0", width: 0.5 }
      });
      slide.addText(v, {
        x: colXs[j] + 0.05, y: y + 0.1, w: colWs[j] - 0.1, h: 0.5,
        fontSize: j === 0 ? 10 : 9, fontFace: "Arial", bold: j === 0,
        color: j === 0 ? C.white : C.dark, margin: 0
      });
    });
  });

  // Execution rules
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.55, w: 9, h: 1.0,
    fill: { color: C.lightBlue }, line: { color: C.blue, width: 1 }
  });
  slide.addText("执行规则", {
    x: 0.65, y: 4.6, w: 1.5, h: 0.3,
    fontSize: 11, fontFace: "Arial", bold: true,
    color: C.navy, margin: 0
  });
  slide.addText([
    { text: "快速失败：", options: { bold: true } },
    { text: "某层检验 FAIL → 立即停止 → 输出 FAILED", options: { breakLine: true } },
    { text: "全部 PASS + 语义对齐 PASS/SKIPPED → 输出 PASSED", options: { breakLine: true } },
    { text: "语义对齐必须返回 UNCERTAIN（若证据不足），不能强行 PASS 或 FAIL", options: {} }
  ], {
    x: 0.65, y: 4.9, w: 8.7, h: 0.6,
    fontSize: 10, fontFace: "Arial",
    color: C.dark, margin: 0
  });
}

// ============================================================
// Slide 13: 关键设计原则
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.white };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.8,
    fill: { color: C.navy }, line: { color: C.navy, width: 0 }
  });
  slide.addText("关键设计原则", {
    x: 0.5, y: 0.15, w: 9, h: 0.5,
    fontSize: 22, fontFace: "Arial", bold: true,
    color: C.white, margin: 0
  });

  const principles = [
    {
      title: "拓扑即协议",
      desc: "父子关系由目录拓扑天然表达，不依赖 parent_id 字段，避免双重真相",
      color: C.green
    },
    {
      title: "同构认知单元",
      desc: "父任务是 Task，子任务也是 Task，没有里程碑、没有史诗、没有故事点，只有 Task",
      color: C.blue
    },
    {
      title: "单写入方原则",
      desc: "每个文件只有一个写入方，session.md / gotchas.md / judge.md 只追加不修改历史",
      color: C.orange
    },
    {
      title: "认知唯一性",
      desc: "对于一个任务，没有两份认知同时存在的状态，不讨论新旧与变更，只维护一份认知",
      color: C.purple
    },
    {
      title: "状态平面的当下性",
      desc: "实时扫描，每次调用直接读文件系统，不缓存。在当前 Task 边界内不做相关性排序、不挑选、不截断",
      color: C.teal
    },
    {
      title: "冲突避免优于协调",
      desc: "物理隔离（不同任务不同目录）+ 顺序保障（父任务等待所有子任务）+ 继续拆分原则",
      color: C.red
    },
  ];

  principles.forEach((p, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.5 + col * 4.7;
    const y = 1.0 + row * 1.4;

    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 4.4, h: 1.2,
      fill: { color: C.lightGray }, line: { color: p.color, width: 2 }
    });
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.08, h: 1.2,
      fill: { color: p.color }, line: { color: p.color, width: 0 }
    });
    slide.addText(p.title, {
      x: x + 0.2, y: y + 0.1, w: 4.0, h: 0.35,
      fontSize: 13, fontFace: "Arial", bold: true,
      color: p.color, margin: 0
    });
    slide.addText(p.desc, {
      x: x + 0.2, y: y + 0.45, w: 4.0, h: 0.7,
      fontSize: 10, fontFace: "Arial",
      color: C.dark, margin: 0
    });
  });
}

// ============================================================
// Slide 14: 结语
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.navy };

  slide.addText("结语", {
    x: 0.5, y: 0.8, w: 9, h: 0.6,
    fontSize: 28, fontFace: "Arial", bold: true,
    color: C.accent, align: "center", margin: 0
  });

  slide.addShape(pres.shapes.LINE, {
    x: 3.5, y: 1.5, w: 3, h: 0,
    line: { color: C.accent, width: 2 }
  });

  slide.addText("Agent 在执行一个需要数百轮交互的长路径任务时，\n最终可能无法回答一个看似简单的问题：", {
    x: 0.5, y: 1.7, w: 9, h: 0.7,
    fontSize: 14, fontFace: "Arial",
    color: C.lightBlue, align: "center", margin: 0
  });

  slide.addText("我现在在哪里？", {
    x: 0.5, y: 2.4, w: 9, h: 0.6,
    fontSize: 24, fontFace: "Arial", bold: true,
    color: C.white, align: "center", margin: 0
  });

  slide.addText("CAP 的全部设计，都在试图让这个问题变得可回答。", {
    x: 0.5, y: 3.1, w: 9, h: 0.4,
    fontSize: 14, fontFace: "Arial",
    color: C.lightBlue, align: "center", margin: 0
  });

  const takeaways = [
    "任务模型将目标、进度和边界封装为可判断的整体",
    "任务信息平面将认知状态和数据状态分开处理",
    "快照协议确保每轮结束时的状态变更可以被追踪",
  ];
  takeaways.forEach((t, i) => {
    slide.addText("•  " + t, {
      x: 2, y: 3.6 + i * 0.45, w: 6, h: 0.4,
      fontSize: 12, fontFace: "Arial",
      color: C.white, margin: 0
    });
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 1.5, y: 5.0, w: 7, h: 0.04,
    fill: { color: C.accent }, line: { color: C.accent, width: 0 }
  });

  slide.addText("当这套机制就位之后，Agent 只需要问自己一个问题：\n我的目标是什么，我现在距离它还有多远？", {
    x: 0.5, y: 5.1, w: 9, h: 0.5,
    fontSize: 11, fontFace: "Arial", italic: true,
    color: C.lightBlue, align: "center", margin: 0
  });
}

// ============================================================
// Write the file
// ============================================================
pres.writeFile({ fileName: "/Users/gpdi/code/ai/mem0ress/docs/CAP_spec.pptx" })
  .then(() => {
    console.log("PPT generated: /Users/gpdi/code/ai/mem0ress/docs/CAP_spec.pptx");
  })
  .catch(err => {
    console.error("Error:", err);
  });
