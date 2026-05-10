const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'mem0ress';
pres.title = 'mem0ress 认知对齐平面';

// Color palette
const C = {
  primary: "028090",      // teal
  secondary: "00A896",    // seafoam
  accent: "02C39A",       // mint
  dark: "1E2761",         // navy
  light: "CADCFC",        // ice blue
  white: "FFFFFF",
  gray: "64748B",
  lightGray: "F1F5F9",
  darkText: "1E293B",
};

// Shadow factory
const makeShadow = () => ({ type: "outer", blur: 4, offset: 2, angle: 135, color: "000000", opacity: 0.12 });

// ============================================================
// Slide 1: Title
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.dark };

  // Accent bar left
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.15, h: 5.625,
    fill: { color: C.accent }
  });

  // Title
  slide.addText("mem0ress", {
    x: 0.6, y: 1.5, w: 8.8, h: 1.2,
    fontSize: 56, fontFace: "Georgia", color: C.white, bold: true,
    margin: 0
  });

  slide.addText("认知对齐平面", {
    x: 0.6, y: 2.6, w: 8.8, h: 0.8,
    fontSize: 36, fontFace: "Georgia", color: C.accent,
    margin: 0
  });

  slide.addText("Cognitive Alignment Plane", {
    x: 0.6, y: 3.3, w: 8.8, h: 0.5,
    fontSize: 18, fontFace: "Calibri", color: C.light,
    margin: 0
  });

  // Subtitle
  slide.addText("AI Agent 任务状态管理与目标态势感知框架", {
    x: 0.6, y: 4.5, w: 8.8, h: 0.4,
    fontSize: 14, fontFace: "Calibri", color: C.gray,
    margin: 0
  });
}

// ============================================================
// Slide 2: 1.1 背景 - 三大结构性问题
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.lightGray };

  // Header bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.9,
    fill: { color: C.dark }
  });
  slide.addText("1.1 背景", {
    x: 0.5, y: 0.2, w: 9, h: 0.5,
    fontSize: 24, fontFace: "Georgia", color: C.white, bold: true, margin: 0
  });

  // Three problem cards
  const problems = [
    { title: "数据汤困境", desc: "上下文污染（Context Collapse）和不可逆的熵增" },
    { title: "意图迷失", desc: "通过追溯历史来拼凑当下，无法匹配目标牵引" },
    { title: "大模型之上的大模型", desc: "算力消耗，未触及「自主管理状态」核心" },
  ];

  problems.forEach((p, i) => {
    const x = 0.5 + i * 3.1;

    // Card background
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.3, w: 2.9, h: 3.5,
      fill: { color: C.white },
      shadow: makeShadow()
    });

    // Top accent
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.3, w: 2.9, h: 0.08,
      fill: { color: C.primary }
    });

    // Number
    slide.addText(String(i + 1), {
      x: x + 0.2, y: 1.6, w: 0.6, h: 0.6,
      fontSize: 28, fontFace: "Georgia", color: C.primary, bold: true, margin: 0
    });

    // Title
    slide.addText(p.title, {
      x: x + 0.2, y: 2.3, w: 2.5, h: 0.6,
      fontSize: 16, fontFace: "Calibri", color: C.darkText, bold: true, margin: 0
    });

    // Description
    slide.addText(p.desc, {
      x: x + 0.2, y: 2.9, w: 2.5, h: 1.5,
      fontSize: 12, fontFace: "Calibri", color: C.gray, margin: 0
    });
  });

  // Bottom insight
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 5.0, w: 9, h: 0.45,
    fill: { color: C.dark }
  });
  slide.addText("我们需要的不是记忆，而是认知（Cognition）", {
    x: 0.7, y: 5.05, w: 8.6, h: 0.35,
    fontSize: 14, fontFace: "Calibri", color: C.accent, bold: true, margin: 0
  });
}

// ============================================================
// Slide 3: 1.2 系统定位
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.lightGray };

  // Header bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.9,
    fill: { color: C.dark }
  });
  slide.addText("1.2 系统定位", {
    x: 0.5, y: 0.2, w: 9, h: 0.5,
    fontSize: 24, fontFace: "Georgia", color: C.white, bold: true, margin: 0
  });

  // Left: Definition box
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.2, w: 4.3, h: 3.8,
    fill: { color: C.white },
    shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.2, w: 0.08, h: 3.8,
    fill: { color: C.primary }
  });

  slide.addText("认知对齐平面", {
    x: 0.8, y: 1.4, w: 3.8, h: 0.5,
    fontSize: 18, fontFace: "Georgia", color: C.primary, bold: true, margin: 0
  });
  slide.addText("Cognitive Alignment Plane", {
    x: 0.8, y: 1.85, w: 3.8, h: 0.35,
    fontSize: 11, fontFace: "Calibri", color: C.gray, italic: true, margin: 0
  });

  slide.addText([
    { text: "不是传统记忆检索数据库", options: { bullet: true, breakLine: true } },
    { text: "不以二进制或向量方式存储", options: { bullet: true, breakLine: true } },
    { text: "基于纯文本的逻辑框架", options: { bullet: true, breakLine: true } },
    { text: "持续检验执行偏差", options: { bullet: true } },
  ], {
    x: 0.8, y: 2.4, w: 3.8, h: 2.4,
    fontSize: 13, fontFace: "Calibri", color: C.darkText,
    paraSpaceAfter: 8
  });

  // Right: Core function
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.2, w: 4.4, h: 3.8,
    fill: { color: C.dark }
  });

  slide.addText("核心功能", {
    x: 5.4, y: 1.4, w: 3.8, h: 0.4,
    fontSize: 14, fontFace: "Calibri", color: C.accent, bold: true, margin: 0
  });

  slide.addText("在任务执行过程中，为 AI Agent 提供清晰的图景（Picture）与执行约束（Constraints），确保 Agent 的动作始终与既定需求对齐。", {
    x: 5.4, y: 1.9, w: 3.8, h: 1.5,
    fontSize: 13, fontFace: "Calibri", color: C.white, margin: 0
  });

  slide.addText("目标用户", {
    x: 5.4, y: 3.5, w: 3.8, h: 0.4,
    fontSize: 14, fontFace: "Calibri", color: C.accent, bold: true, margin: 0
  });
  slide.addText("AI/Agent 框架开发者", {
    x: 5.4, y: 3.9, w: 3.8, h: 0.4,
    fontSize: 13, fontFace: "Calibri", color: C.light, margin: 0
  });
}

// ============================================================
// Slide 4: 1.3 核心解法总览
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.lightGray };

  // Header bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.9,
    fill: { color: C.dark }
  });
  slide.addText("1.3 核心解法总览", {
    x: 0.5, y: 0.2, w: 9, h: 0.5,
    fontSize: 24, fontFace: "Georgia", color: C.white, bold: true, margin: 0
  });

  // Three columns: PRC, 双平面, Judge Agent
  const cols = [
    {
      title: "认知三要素",
      subtitle: "Picture / Requirements / Constraints",
      color: C.primary,
      items: ["Picture 图景", "Requirements 需求", "Constraints 约束"]
    },
    {
      title: "双平面正交",
      subtitle: "状态平面 + 数据平面",
      color: C.secondary,
      items: ["状态平面：做什么→做到哪", "数据平面：当前代码版本", "正交互斥，认知效率"]
    },
    {
      title: "四层检验",
      subtitle: "Judge Agent",
      color: "6D2E46",
      items: ["Tier 0: Constraints 检查", "Tier 1: Todo + 子任务", "Tier 2: Requirements", "Tier 3: 语义对齐"]
    }
  ];

  cols.forEach((col, i) => {
    const x = 0.5 + i * 3.15;

    // Card
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.15, w: 3.0, h: 4.1,
      fill: { color: C.white },
      shadow: makeShadow()
    });

    // Top bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.15, w: 3.0, h: 0.55,
      fill: { color: col.color }
    });

    // Title
    slide.addText(col.title, {
      x: x + 0.15, y: 1.2, w: 2.7, h: 0.35,
      fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, margin: 0
    });
    slide.addText(col.subtitle, {
      x: x + 0.15, y: 1.5, w: 2.7, h: 0.2,
      fontSize: 9, fontFace: "Calibri", color: C.light, margin: 0
    });

    // Items
    col.items.forEach((item, j) => {
      slide.addShape(pres.shapes.RECTANGLE, {
        x: x + 0.15, y: 1.9 + j * 0.95, w: 0.06, h: 0.06,
        fill: { color: col.color }
      });
      slide.addText(item, {
        x: x + 0.3, y: 1.85 + j * 0.95, w: 2.55, h: 0.8,
        fontSize: 11, fontFace: "Calibri", color: C.darkText, margin: 0
      });
    });
  });
}

// ============================================================
// Slide 5: 2.1-2.4 四个洞察
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.lightGray };

  // Header bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.9,
    fill: { color: C.dark }
  });
  slide.addText("2.1-2.4 四个洞察", {
    x: 0.5, y: 0.2, w: 9, h: 0.5,
    fontSize: 24, fontFace: "Georgia", color: C.white, bold: true, margin: 0
  });

  // Four insight cards in 2x2
  const insights = [
    { num: "1", title: "记忆的目标属性", desc: "上下文是被发现的，而非被维持的", derived: "" },
    { num: "2", title: "PRC 框架", desc: "目标需要一个可判断的完成标准", derived: "← 推导自洞察一" },
    { num: "3", title: "Task 锚点", desc: "任务是人类和 AI 共同的工作记忆单元", derived: "← 拆分自洞察二" },
    { num: "4", title: "双平面正交", desc: "做什么和做到哪是两个独立维度", derived: "← 拆分自洞察二" },
  ];

  insights.forEach((ins, i) => {
    const x = 0.5 + (i % 2) * 4.65;
    const y = 1.1 + Math.floor(i / 2) * 2.2;

    // Card
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: 4.4, h: 2.0,
      fill: { color: C.white },
      shadow: makeShadow()
    });

    // Number circle
    slide.addShape(pres.shapes.OVAL, {
      x: x + 0.15, y: y + 0.15, w: 0.5, h: 0.5,
      fill: { color: C.primary }
    });
    slide.addText(ins.num, {
      x: x + 0.15, y: y + 0.2, w: 0.5, h: 0.4,
      fontSize: 18, fontFace: "Georgia", color: C.white, bold: true, align: "center", margin: 0
    });

    // Title
    slide.addText(ins.title, {
      x: x + 0.75, y: y + 0.2, w: 3.4, h: 0.4,
      fontSize: 16, fontFace: "Calibri", color: C.darkText, bold: true, margin: 0
    });

    // Description
    slide.addText(ins.desc, {
      x: x + 0.15, y: y + 0.75, w: 4.1, h: 0.7,
      fontSize: 12, fontFace: "Calibri", color: C.gray, margin: 0
    });

    // Derived from
    if (ins.derived) {
      slide.addText(ins.derived, {
        x: x + 0.15, y: y + 1.5, w: 4.1, h: 0.35,
        fontSize: 10, fontFace: "Calibri", color: C.secondary, italic: true, margin: 0
      });
    }
  });
}

// ============================================================
// Slide 6: 2.2 PRC 框架
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.lightGray };

  // Header bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.9,
    fill: { color: C.dark }
  });
  slide.addText("2.2 PRC 框架", {
    x: 0.5, y: 0.2, w: 9, h: 0.5,
    fontSize: 24, fontFace: "Georgia", color: C.white, bold: true, margin: 0
  });

  // Three PRC cards
  const prc = [
    {
      title: "Picture 图景",
      who: "利益相关者定义",
      desc: "语义层面的终极成功状态，回答「做成什么样」。即使所有代码写完、测试通过，用户感知到「还是不能登录」，Picture 即未达成。",
      color: C.primary
    },
    {
      title: "Requirements 需求",
      who: "Agent 推导，利益相关者确认",
      desc: "从 Picture 推导出的具体条件，必须可独立验证——要么通过，要么不通过，没有灰色地带。",
      color: C.secondary
    },
    {
      title: "Constraints 约束",
      who: "Agent + 领域知识，利益相关者确认",
      desc: "一旦违反系统必须阻断。如「不许存储明文密码」、「Access Token 有效期不得超过 1 小时」。",
      color: "6D2E46"
    }
  ];

  prc.forEach((p, i) => {
    const x = 0.5 + i * 3.15;

    // Card
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.15, w: 3.0, h: 3.6,
      fill: { color: C.white },
      shadow: makeShadow()
    });

    // Top bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.15, w: 3.0, h: 0.55,
      fill: { color: p.color }
    });

    slide.addText(p.title, {
      x: x + 0.15, y: 1.2, w: 2.7, h: 0.35,
      fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, margin: 0
    });

    // Who
    slide.addText(p.who, {
      x: x + 0.15, y: 1.85, w: 2.7, h: 0.3,
      fontSize: 10, fontFace: "Calibri", color: p.color, italic: true, margin: 0
    });

    // Description
    slide.addText(p.desc, {
      x: x + 0.15, y: 2.2, w: 2.7, h: 2.4,
      fontSize: 11, fontFace: "Calibri", color: C.darkText, margin: 0
    });
  });

  // Bottom note
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.9, w: 9, h: 0.5,
    fill: { color: C.dark }
  });
  slide.addText("Picture 是绝对的锚 —— 目标的核心语义锚", {
    x: 0.7, y: 4.95, w: 8.6, h: 0.4,
    fontSize: 13, fontFace: "Calibri", color: C.accent, bold: true, margin: 0
  });
}

// ============================================================
// Slide 7: 2.3 Task 锚点
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.lightGray };

  // Header bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.9,
    fill: { color: C.dark }
  });
  slide.addText("2.3 Task 锚点", {
    x: 0.5, y: 0.2, w: 9, h: 0.5,
    fontSize: 24, fontFace: "Georgia", color: C.white, bold: true, margin: 0
  });

  // Left: description
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.15, w: 4.4, h: 3.6,
    fill: { color: C.white },
    shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.15, w: 0.08, h: 3.6,
    fill: { color: C.primary }
  });

  slide.addText("任务作为认知单元", {
    x: 0.8, y: 1.35, w: 3.9, h: 0.4,
    fontSize: 16, fontFace: "Georgia", color: C.primary, bold: true, margin: 0
  });

  slide.addText([
    { text: "同构性：所有 Task 拥有相同结构", options: { bullet: true, breakLine: true } },
    { text: "可分解性：分形树状结构", options: { bullet: true, breakLine: true } },
    { text: "可验证性：每个 Task 有明确 Picture", options: { bullet: true, breakLine: true } },
    { text: "无冲突：父任务完成以所有子任务完成为前提", options: { bullet: true } },
  ], {
    x: 0.8, y: 1.85, w: 3.9, h: 2.8,
    fontSize: 12, fontFace: "Calibri", color: C.darkText,
    paraSpaceAfter: 10
  });

  // Right: tree structure visualization
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.15, w: 4.3, h: 3.6,
    fill: { color: C.white },
    shadow: makeShadow()
  });

  slide.addText("分形树状结构", {
    x: 5.4, y: 1.3, w: 3.9, h: 0.35,
    fontSize: 14, fontFace: "Calibri", color: C.darkText, bold: true, margin: 0
  });

  // Tree nodes (simplified)
  const nodes = [
    { label: "/tasks", x: 7.0, y: 1.8, w: 1.0, isRoot: true },
    { label: "auth_module/", x: 5.8, y: 2.6, w: 1.4, isTask: true },
    { label: "oauth_google/", x: 5.3, y: 3.4, w: 1.3, isTask: true },
    { label: "oauth_github/", x: 6.6, y: 3.4, w: 1.3, isTask: true },
    { label: "session_store/", x: 7.9, y: 3.4, w: 1.4, isTask: true },
  ];

  nodes.forEach(n => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: n.x, y: n.y, w: n.w, h: 0.45,
      fill: { color: n.isRoot ? C.dark : n.isTask ? C.primary : C.secondary },
      line: { color: n.isRoot ? C.dark : n.isTask ? C.primary : C.secondary, width: 1 }
    });
    slide.addText(n.label, {
      x: n.x, y: n.y + 0.05, w: n.w, h: 0.35,
      fontSize: 9, fontFace: "Calibri", color: C.white, align: "center", margin: 0
    });
  });

  // Connection lines (approximate)
  slide.addShape(pres.shapes.LINE, {
    x: 7.5, y: 2.25, w: 0, h: 0.35,
    line: { color: C.gray, width: 1 }
  });
  slide.addShape(pres.shapes.LINE, {
    x: 6.5, y: 2.6, w: 1.5, h: 0,
    line: { color: C.gray, width: 1 }
  });
}

// ============================================================
// Slide 8: 2.4 双平面正交
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.lightGray };

  // Header bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.9,
    fill: { color: C.dark }
  });
  slide.addText("2.4 双平面正交", {
    x: 0.5, y: 0.2, w: 9, h: 0.5,
    fontSize: 24, fontFace: "Georgia", color: C.white, bold: true, margin: 0
  });

  // Two planes side by side
  const planes = [
    {
      title: "状态平面",
      subtitle: "Status Plane",
      color: C.primary,
      items: ["任务树结构", "Todo 完成度", "任务状态", "Gotchas 记录"],
      behavior: "Agent 唤醒时强制挂载",
      what: "回答：我在哪？"
    },
    {
      title: "数据平面",
      subtitle: "Data Plane",
      color: C.secondary,
      items: ["各仓库 commit ID", "长篇文档版本指针", "版本快照"],
      behavior: "Agent 需要时按需展开",
      what: "回答：我在操作什么代码？"
    }
  ];

  planes.forEach((p, i) => {
    const x = 0.5 + i * 4.7;

    // Card
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.15, w: 4.5, h: 4.1,
      fill: { color: C.white },
      shadow: makeShadow()
    });

    // Top bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.15, w: 4.5, h: 0.65,
      fill: { color: p.color }
    });

    slide.addText(p.title, {
      x: x + 0.2, y: 1.2, w: 2.5, h: 0.35,
      fontSize: 16, fontFace: "Georgia", color: C.white, bold: true, margin: 0
    });
    slide.addText(p.subtitle, {
      x: x + 0.2, y: 1.52, w: 2.5, h: 0.25,
      fontSize: 10, fontFace: "Calibri", color: C.light, margin: 0
    });

    // What question
    slide.addText(p.what, {
      x: x + 0.2, y: 2.0, w: 4.1, h: 0.35,
      fontSize: 13, fontFace: "Calibri", color: p.color, bold: true, margin: 0
    });

    // Items
    slide.addText("包含：", {
      x: x + 0.2, y: 2.45, w: 4.1, h: 0.25,
      fontSize: 10, fontFace: "Calibri", color: C.gray, margin: 0
    });

    p.items.forEach((item, j) => {
      slide.addShape(pres.shapes.RECTANGLE, {
        x: x + 0.2, y: 2.75 + j * 0.45, w: 0.05, h: 0.05,
        fill: { color: p.color }
      });
      slide.addText(item, {
        x: x + 0.35, y: 2.7 + j * 0.45, w: 3.9, h: 0.35,
        fontSize: 11, fontFace: "Calibri", color: C.darkText, margin: 0
      });
    });

    // Behavior
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.2, y: 4.6, w: 4.1, h: 0.45,
      fill: { color: p.color, transparency: 15 }
    });
    slide.addText(p.behavior, {
      x: x + 0.35, y: 4.65, w: 3.8, h: 0.35,
      fontSize: 11, fontFace: "Calibri", color: p.color, bold: true, margin: 0
    });
  });
}

// ============================================================
// Slide 9: 3.1-3.4 + 4.1-4.3 设计理念与工程准则
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.lightGray };

  // Header bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.9,
    fill: { color: C.dark }
  });
  slide.addText("设计理念 & 工程准则", {
    x: 0.5, y: 0.2, w: 9, h: 0.5,
    fontSize: 24, fontFace: "Georgia", color: C.white, bold: true, margin: 0
  });

  // Two columns: Design principles (left) and Engineering rules (right)
  // Left: Design principles
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.1, w: 4.4, h: 4.2,
    fill: { color: C.white },
    shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.1, w: 4.4, h: 0.5,
    fill: { color: C.primary }
  });
  slide.addText("第三章：设计理念", {
    x: 0.7, y: 1.15, w: 4.0, h: 0.4,
    fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, margin: 0
  });

  const principles = [
    { title: "目标锚定", from: "洞察一", desc: "目的论认知，任何信息必须有明确目的" },
    { title: "认知而非记忆", from: "洞察一", desc: "只记录与目标相关的状态变化" },
    { title: "同构认知单元", from: "洞察三", desc: "分形树状结构，统一解析逻辑" },
    { title: "认知平面数据流", from: "洞察四", desc: "状态平面与数据平面正交互斥" },
  ];

  principles.forEach((p, i) => {
    slide.addText(p.title, {
      x: 0.7, y: 1.75 + i * 0.85, w: 4.0, h: 0.3,
      fontSize: 12, fontFace: "Calibri", color: C.primary, bold: true, margin: 0
    });
    slide.addText(p.desc, {
      x: 0.7, y: 2.0 + i * 0.85, w: 4.0, h: 0.5,
      fontSize: 10, fontFace: "Calibri", color: C.gray, margin: 0
    });
  });

  // Right: Engineering rules
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.1, w: 4.4, h: 4.2,
    fill: { color: C.white },
    shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.1, w: 4.4, h: 0.5,
    fill: { color: C.secondary }
  });
  slide.addText("第四章：工程准则", {
    x: 5.3, y: 1.15, w: 4.0, h: 0.4,
    fontSize: 14, fontFace: "Calibri", color: C.white, bold: true, margin: 0
  });

  const rules = [
    { title: "SSOT + 绝对覆写", abbr: "SSOT", desc: "拒绝模糊认知合并，运行时直接覆写旧认知" },
    { title: "系统级卸责", abbr: "", desc: "mem0ress 只专注认知生命周期管理" },
    { title: "反黑盒 + 绝对可观测性", abbr: "", desc: "零中介：目录树 + 纯文本，无隐藏状态" },
  ];

  rules.forEach((r, i) => {
    slide.addText(r.title, {
      x: 5.3, y: 1.75 + i * 1.1, w: 4.0, h: 0.3,
      fontSize: 12, fontFace: "Calibri", color: C.secondary, bold: true, margin: 0
    });
    slide.addText(r.desc, {
      x: 5.3, y: 2.0 + i * 1.1, w: 4.0, h: 0.7,
      fontSize: 10, fontFace: "Calibri", color: C.gray, margin: 0
    });
  });
}

// ============================================================
// Slide 10: 5.1 PRC 三要素使用指南
// ============================================================
{
  let slide = pres.addSlide();
  slide.background = { color: C.lightGray };

  // Header bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.9,
    fill: { color: C.dark }
  });
  slide.addText("5.1 PRC 三要素使用指南", {
    x: 0.5, y: 0.2, w: 9, h: 0.5,
    fontSize: 24, fontFace: "Georgia", color: C.white, bold: true, margin: 0
  });

  // Three sections: who defines, when to define, quality criteria
  // Section 1: Who defines
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.1, w: 2.9, h: 2.5,
    fill: { color: C.white },
    shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.1, w: 2.9, h: 0.45,
    fill: { color: C.primary }
  });
  slide.addText("谁来定义", {
    x: 0.65, y: 1.15, w: 2.6, h: 0.35,
    fontSize: 13, fontFace: "Calibri", color: C.white, bold: true, margin: 0
  });

  const who = [
    { elem: "Picture", who: "利益相关者" },
    { elem: "Requirements", who: "Agent 推导" },
    { elem: "Constraints", who: "Agent + 领域" },
  ];
  who.forEach((w, i) => {
    slide.addText(w.elem, {
      x: 0.65, y: 1.7 + i * 0.55, w: 2.6, h: 0.25,
      fontSize: 11, fontFace: "Calibri", color: C.primary, bold: true, margin: 0
    });
    slide.addText(w.who, {
      x: 0.65, y: 1.92 + i * 0.55, w: 2.6, h: 0.25,
      fontSize: 10, fontFace: "Calibri", color: C.gray, margin: 0
    });
  });

  // Section 2: When to define
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 3.55, y: 1.1, w: 2.9, h: 2.5,
    fill: { color: C.white },
    shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 3.55, y: 1.1, w: 2.9, h: 0.45,
    fill: { color: C.secondary }
  });
  slide.addText("什么时候定义", {
    x: 3.7, y: 1.15, w: 2.6, h: 0.35,
    fontSize: 13, fontFace: "Calibri", color: C.white, bold: true, margin: 0
  });

  slide.addText([
    { text: "1. 定义 Picture", options: { bullet: true, breakLine: true } },
    { text: "2. 推导 Requirements", options: { bullet: true, breakLine: true } },
    { text: "3. 推导 Constraints", options: { bullet: true, breakLine: true } },
    { text: "4. 冲突检测", options: { bullet: true, breakLine: true } },
    { text: "   → 矛盾则标记「不可行」", options: { breakLine: true } },
  ], {
    x: 3.7, y: 1.65, w: 2.6, h: 1.9,
    fontSize: 10, fontFace: "Calibri", color: C.darkText,
    paraSpaceAfter: 4
  });

  // Section 3: Quality criteria
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.6, y: 1.1, w: 2.9, h: 2.5,
    fill: { color: C.white },
    shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.6, y: 1.1, w: 2.9, h: 0.45,
    fill: { color: "6D2E46" }
  });
  slide.addText("质量判断标准", {
    x: 6.75, y: 1.15, w: 2.6, h: 0.35,
    fontSize: 13, fontFace: "Calibri", color: C.white, bold: true, margin: 0
  });

  slide.addText([
    { text: "Picture: 是否可感知？", options: { bold: true, breakLine: true } },
    { text: "描述成功状态，而非实现路径", options: { breakLine: true, color: C.gray } },
    { text: "Requirements: 是否可自动化检验？", options: { bold: true, breakLine: true } },
    { text: "必须有明确的通过/失败判定", options: { breakLine: true, color: C.gray } },
    { text: "Constraints: 是否可阻断？", options: { bold: true, breakLine: true } },
    { text: "违反时系统必须能检测并阻止", options: { color: C.gray } },
  ], {
    x: 6.75, y: 1.6, w: 2.6, h: 1.95,
    fontSize: 9, fontFace: "Calibri", color: C.darkText,
    paraSpaceAfter: 2
  });

  // Bottom: key insight
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 3.8, w: 9, h: 1.5,
    fill: { color: C.dark }
  });

  slide.addText("关键原则", {
    x: 0.7, y: 3.95, w: 8.6, h: 0.35,
    fontSize: 14, fontFace: "Calibri", color: C.accent, bold: true, margin: 0
  });

  slide.addText([
    { text: "Picture / Requirements / Constraints 从 Manifest 获取，不重复记录。", options: { breakLine: true } },
    { text: "清单文件中统一存放，状态平面仅展示其摘要，不展开全文。", options: {} },
  ], {
    x: 0.7, y: 4.35, w: 8.6, h: 0.85,
    fontSize: 12, fontFace: "Calibri", color: C.white,
    paraSpaceAfter: 6
  });
}

// Save
pres.writeFile({ fileName: "/Users/gpdi/code/ai/mem0ress/docs/mem0ress_overview.pptx" })
  .then(() => console.log("Created: mem0ress_overview.pptx"))
  .catch(err => console.error(err));
