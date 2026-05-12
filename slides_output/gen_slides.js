const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'mem0ress';
pres.title = 'mem0ress: 认知对齐平面';
pres.subject = 'AI Agent 目标态势感知框架';

// Color palette: Midnight Executive
const C = {
  navy: "1E2761",
  iceBlue: "CADCFC",
  white: "FFFFFF",
  darkText: "1E2761",
  lightText: "CADCFC",
  accent: "3D5A80"
};

// Helper: create consistent shadow
const makeShadow = () => ({
  type: "outer",
  color: "000000",
  blur: 8,
  offset: 3,
  angle: 135,
  opacity: 0.2
});

// ============ Slide 1: Title ============
let slide1 = pres.addSlide();
slide1.background = { color: C.navy };

// Decorative shape - top accent bar
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.08,
  fill: { color: C.iceBlue }
});

// Main title
slide1.addText("mem0ress", {
  x: 0.5, y: 1.5, w: 9, h: 1.2,
  fontSize: 60, fontFace: "Arial Black", bold: true,
  color: C.white, align: "center", margin: 0
});

// Subtitle
slide1.addText("认知对齐平面 (Cognitive Alignment Plane)", {
  x: 0.5, y: 2.7, w: 9, h: 0.7,
  fontSize: 28, fontFace: "Arial",
  color: C.iceBlue, align: "center", margin: 0
});

// Tagline
slide1.addText("让 AI Agent 在任何时刻都能判断自己在哪里", {
  x: 0.5, y: 3.8, w: 9, h: 0.5,
  fontSize: 18, fontFace: "Arial", italic: true,
  color: C.iceBlue, align: "center", margin: 0
});

// Bottom accent line
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 3.5, y: 4.6, w: 3, h: 0.04,
  fill: { color: C.iceBlue }
});

// Footer
slide1.addText("AI Agent 框架开发者", {
  x: 0.5, y: 5.0, w: 9, h: 0.4,
  fontSize: 14, fontFace: "Arial",
  color: C.iceBlue, align: "center", margin: 0
});

// ============ Slide 2: Background - Four Problems ============
let slide2 = pres.addSlide();
slide2.background = { color: C.white };

// Title bar
slide2.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: C.navy }
});
slide2.addText("背景：四个结构性问题", {
  x: 0.5, y: 0.15, w: 9, h: 0.6,
  fontSize: 28, fontFace: "Arial", bold: true,
  color: C.white, margin: 0
});

// Four problem cards - 2x2 grid
const problems = [
  { title: "数据汤困境", desc: "历史对话、代码片段、废弃架构融合成没有边界的\"数据汤\"，导致上下文污染和不可逆的熵增" },
  { title: "意图迷失", desc: "记忆系统不感知目标，只能回答\"这个问题之前怎么处理的\"，无法回答\"我当前的目标是什么\"" },
  { title: "高频数据语义坍缩", desc: "高频迭代中，Top-K 检索容易召回一堆语义等价但时序不同的冗余片段，使 Agent 陷入信息茧房" },
  { title: "向量检索叠加向量检索", desc: "在 LLM 已有向量检索的基础上，再对会话数据做一层向量检索，两层检索面临同样的根本困境" }
];

const cardW = 4.3, cardH = 1.7;
const startX = 0.5, startY = 1.2;
const gapX = 0.4, gapY = 0.3;

problems.forEach((p, i) => {
  const col = i % 2;
  const row = Math.floor(i / 2);
  const x = startX + col * (cardW + gapX);
  const y = startY + row * (cardH + gapY);

  // Card background
  slide2.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: cardW, h: cardH,
    fill: { color: "F8F9FA" },
    shadow: makeShadow()
  });

  // Left accent bar
  slide2.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: 0.06, h: cardH,
    fill: { color: C.navy }
  });

  // Card title
  slide2.addText(p.title, {
    x: x + 0.2, y: y + 0.15, w: cardW - 0.3, h: 0.4,
    fontSize: 16, fontFace: "Arial", bold: true,
    color: C.navy, margin: 0
  });

  // Card description
  slide2.addText(p.desc, {
    x: x + 0.2, y: y + 0.55, w: cardW - 0.3, h: cardH - 0.7,
    fontSize: 11, fontFace: "Arial",
    color: "4A4A4A", margin: 0, valign: "top"
  });
});

// Bottom insight
slide2.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.8, w: 9, h: 0.6,
  fill: { color: C.navy, transparency: 10 }
});
slide2.addText("核心矛盾：Agent 不缺信息，缺的是对\"当前自己在哪里、目标偏了没有、还差什么\"的持续感知", {
  x: 0.6, y: 4.9, w: 8.8, h: 0.4,
  fontSize: 12, fontFace: "Arial", bold: true,
  color: C.navy, align: "center", margin: 0
});

// ============ Slide 3: Three Core Insights ============
let slide3 = pres.addSlide();
slide3.background = { color: C.white };

// Title bar
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: C.navy }
});
slide3.addText("核心洞察：三个洞察的推导链", {
  x: 0.5, y: 0.15, w: 9, h: 0.6,
  fontSize: 28, fontFace: "Arial", bold: true,
  color: C.white, margin: 0
});

// Three insight cards in a row
const insights = [
  {
    num: "01",
    title: "上下文以目标为导向",
    desc: "上下文不是被维护的，而是被发现的。人类记忆主动为当前目标服务，同一条信息在不同目标下重要性截然不同。",
    color: "2C5F2D"
  },
  {
    num: "02",
    title: "任务是信息的完整单元",
    desc: "事件天然封装目标、行动、结果和上下文。孤立的条件列表、进度记录、目标描述无法单独构成完整认知。",
    color: "065A82"
  },
  {
    num: "03",
    title: "任务需要认知而非记忆",
    desc: "真正稀缺的不是更多信息，而是随时判断\"我在哪、目标偏没偏、还差什么\"的能力。认知回答当下，记忆存储过去。",
    color: "B85042"
  }
];

const insightCardW = 2.9;
const insightStartX = 0.5;
const insightGap = 0.3;

insights.forEach((ins, i) => {
  const x = insightStartX + i * (insightCardW + insightGap);

  // Card
  slide3.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.2, w: insightCardW, h: 3.8,
    fill: { color: "FAFAFA" },
    shadow: makeShadow()
  });

  // Top color bar
  slide3.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.2, w: insightCardW, h: 0.6,
    fill: { color: ins.color }
  });

  // Number
  slide3.addText(ins.num, {
    x: x, y: 1.25, w: insightCardW, h: 0.5,
    fontSize: 24, fontFace: "Arial Black", bold: true,
    color: C.white, align: "center", margin: 0
  });

  // Title
  slide3.addText(ins.title, {
    x: x + 0.15, y: 2.0, w: insightCardW - 0.3, h: 0.7,
    fontSize: 14, fontFace: "Arial", bold: true,
    color: ins.color, align: "center", margin: 0
  });

  // Description
  slide3.addText(ins.desc, {
    x: x + 0.15, y: 2.7, w: insightCardW - 0.3, h: 2.2,
    fontSize: 10, fontFace: "Arial",
    color: "4A4A4A", margin: 0, valign: "top"
  });
});

// Arrow connecting insights
slide3.addText("→", {
  x: 3.4, y: 2.8, w: 0.3, h: 0.5,
  fontSize: 24, color: C.navy, align: "center", margin: 0
});
slide3.addText("→", {
  x: 6.6, y: 2.8, w: 0.3, h: 0.5,
  fontSize: 24, color: C.navy, align: "center", margin: 0
});

// Bottom note
slide3.addText("前一个洞察是后一个洞察的前提 —— 理解这条推导链，就能理解 mem0ress 为什么是这样设计", {
  x: 0.5, y: 5.15, w: 9, h: 0.35,
  fontSize: 11, fontFace: "Arial", italic: true,
  color: C.navy, align: "center", margin: 0
});

// ============ Slide 4: System Positioning ============
let slide4 = pres.addSlide();
slide4.background = { color: C.white };

// Title bar
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: C.navy }
});
slide4.addText("系统定位：mem0ress 是什么", {
  x: 0.5, y: 0.15, w: 9, h: 0.6,
  fontSize: 28, fontFace: "Arial", bold: true,
  color: C.white, margin: 0
});

// Left column - What it IS
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.2, w: 4.3, h: 3.6,
  fill: { color: "E8F5E9" },
  shadow: makeShadow()
});
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.2, w: 4.3, h: 0.5,
  fill: { color: "2C5F2D" }
});
slide4.addText("mem0ress 是", {
  x: 0.5, y: 1.25, w: 4.3, h: 0.4,
  fontSize: 16, fontFace: "Arial", bold: true,
  color: C.white, align: "center", margin: 0
});

const isItems = [
  "认知对齐平面 —— 持续让认知与任务状态保持一致",
  "状态窗口 —— 不做检索、排序、截断，完整呈现当前认知",
  "任务状态管理者 —— 提供可判断的当前状态坐标",
  "目标态势感知器 —— 确保 Agent 不偏离既定需求"
];
slide4.addText(
  isItems.map((item, idx) => ({
    text: item,
    options: { bullet: true, breakLine: idx < isItems.length - 1 }
  })),
  {
    x: 0.7, y: 1.85, w: 3.9, h: 2.8,
    fontSize: 11, fontFace: "Arial",
    color: "2C5F2D", margin: 0, valign: "top"
  }
);

// Right column - What it is NOT
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: 1.2, w: 4.3, h: 3.6,
  fill: { color: "FFEBEE" },
  shadow: makeShadow()
});
slide4.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: 1.2, w: 4.3, h: 0.5,
  fill: { color: "B85042" }
});
slide4.addText("mem0ress 不是", {
  x: 5.2, y: 1.25, w: 4.3, h: 0.4,
  fontSize: 16, fontFace: "Arial", bold: true,
  color: C.white, align: "center", margin: 0
});

const notItems = [
  "记忆检索数据库 —— 不存储历史对话",
  "向量数据库 —— 不做相似度检索",
  "LLM 总结系统 —— 不做 LLM 总结 LLM",
  "回答问题引擎 —— 不回答问题，只呈现状态"
];
slide4.addText(
  notItems.map((item, idx) => ({
    text: item,
    options: { bullet: true, breakLine: idx < notItems.length - 1 }
  })),
  {
    x: 5.4, y: 1.85, w: 3.9, h: 2.8,
    fontSize: 11, fontFace: "Arial",
    color: "B85042", margin: 0, valign: "top"
  }
);

// Bottom tagline
slide4.addText("我们需要的不是记忆，而是认知 (Cognition)", {
  x: 0.5, y: 5.0, w: 9, h: 0.4,
  fontSize: 16, fontFace: "Arial", bold: true,
  color: C.navy, align: "center", margin: 0
});

// ============ Slide 5: Core Solution Overview ============
let slide5 = pres.addSlide();
slide5.background = { color: C.navy };

// Title
slide5.addText("核心解法概览", {
  x: 0.5, y: 0.3, w: 9, h: 0.7,
  fontSize: 32, fontFace: "Arial", bold: true,
  color: C.white, align: "center", margin: 0
});

// Three pillars
const pillars = [
  {
    title: "PRC",
    subtitle: "任务信息模型",
    items: ["Picture 图景", "Requirements 需求", "Constraints 约束"],
    color: "2C5F2D",
    bgColor: "E8F5E9"
  },
  {
    title: "双平面",
    subtitle: "认知 + 数据",
    items: ["状态平面", "数据平面"],
    color: "065A82",
    bgColor: "E3F2FD"
  },
  {
    title: "Judge",
    subtitle: "任务检验",
    items: ["Tier 0 约束检查", "Tier 1 Todo 检查", "Tier 2 需求检查", "Tier 3 语义对齐"],
    color: "B85042",
    bgColor: "FCE4EC"
  }
];

const pillarW = 2.8;
const pillarStartX = 0.8;
const pillarGap = 0.5;

pillars.forEach((p, i) => {
  const x = pillarStartX + i * (pillarW + pillarGap);

  // Card
  slide5.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.2, w: pillarW, h: 3.8,
    fill: { color: p.bgColor },
    shadow: makeShadow()
  });

  // Title
  slide5.addText(p.title, {
    x: x, y: 1.4, w: pillarW, h: 0.6,
    fontSize: 28, fontFace: "Arial Black", bold: true,
    color: p.color, align: "center", margin: 0
  });

  // Subtitle
  slide5.addText(p.subtitle, {
    x: x, y: 2.0, w: pillarW, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: p.color, align: "center", margin: 0
  });

  // Divider
  slide5.addShape(pres.shapes.RECTANGLE, {
    x: x + 0.5, y: 2.5, w: pillarW - 1.0, h: 0.02,
    fill: { color: p.color, transparency: 50 }
  });

  // Items
  slide5.addText(
    p.items.map((item, idx) => ({
      text: item,
      options: { bullet: true, breakLine: idx < p.items.length - 1 }
    })),
    {
      x: x + 0.2, y: 2.7, w: pillarW - 0.4, h: 2.0,
      fontSize: 10, fontFace: "Arial",
      color: "333333", margin: 0, valign: "top"
    }
  );
});

// Bottom note
slide5.addText("三者组合，构成 Agent 在任意时刻对任务态势的完整感知", {
  x: 0.5, y: 5.1, w: 9, h: 0.35,
  fontSize: 13, fontFace: "Arial", italic: true,
  color: C.iceBlue, align: "center", margin: 0
});

// ============ Slide 6: PRC Model ============
let slide6 = pres.addSlide();
slide6.background = { color: C.white };

// Title bar
slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: C.navy }
});
slide6.addText("任务信息模型 (PRC)", {
  x: 0.5, y: 0.15, w: 9, h: 0.6,
  fontSize: 28, fontFace: "Arial", bold: true,
  color: C.white, margin: 0
});

// Three elements - horizontal layout
const prcElements = [
  {
    title: "Picture",
    subtitle: "图景",
    role: "方向锚点",
    desc: "任务完成后的宏观景象，以自然语言描绘。提供方向锚点，使 Agent 理解最终目标是什么。",
    formula: "任务完成的充分条件",
    color: "2C5F2D",
    bgColor: "E8F5E9"
  },
  {
    title: "Requirements",
    subtitle: "需求",
    role: "可验证标准",
    desc: "任务完成的可验证标准，将 Picture 转化为具体的检验点。是 Picture 满足的必要条件。",
    formula: "Picture 的必要条件",
    color: "065A82",
    bgColor: "E3F2FD"
  },
  {
    title: "Constraints",
    subtitle: "约束",
    role: "边界约束",
    desc: "任务的过程和结果定义边界条件。违反即使 Req 满足，Picture 看似达成，任务也不算完成。",
    formula: "贯穿全程的约束线",
    color: "B85042",
    bgColor: "FCE4EC"
  }
];

const prcW = 2.9;
const prcStartX = 0.5;
const prcGap = 0.3;

prcElements.forEach((el, i) => {
  const x = prcStartX + i * (prcW + prcGap);

  // Card
  slide6.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.1, w: prcW, h: 2.6,
    fill: { color: el.bgColor },
    shadow: makeShadow()
  });

  // Top accent
  slide6.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.1, w: prcW, h: 0.06,
    fill: { color: el.color }
  });

  // Title
  slide6.addText(el.title, {
    x: x, y: 1.25, w: prcW, h: 0.4,
    fontSize: 16, fontFace: "Arial", bold: true,
    color: el.color, align: "center", margin: 0
  });

  // Subtitle
  slide6.addText(el.subtitle, {
    x: x, y: 1.6, w: prcW, h: 0.3,
    fontSize: 12, fontFace: "Arial",
    color: el.color, align: "center", margin: 0
  });

  // Description
  slide6.addText(el.desc, {
    x: x + 0.1, y: 2.0, w: prcW - 0.2, h: 1.0,
    fontSize: 9, fontFace: "Arial",
    color: "4A4A4A", margin: 0, valign: "top"
  });

  // Formula badge
  slide6.addShape(pres.shapes.RECTANGLE, {
    x: x + 0.2, y: 3.1, w: prcW - 0.4, h: 0.45,
    fill: { color: el.color }
  });
  slide6.addText(el.formula, {
    x: x + 0.2, y: 3.15, w: prcW - 0.4, h: 0.35,
    fontSize: 8, fontFace: "Arial", bold: true,
    color: C.white, align: "center", margin: 0
  });
});

// Definition order section
slide6.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 3.9, w: 9, h: 1.5,
  fill: { color: "F5F5F5" },
  shadow: makeShadow()
});
slide6.addText("定义顺序", {
  x: 0.7, y: 4.0, w: 2, h: 0.35,
  fontSize: 12, fontFace: "Arial", bold: true,
  color: C.navy, margin: 0
});

const steps = [
  "1. 定义 Picture（任务完成后的宏观景象）",
  "2. 从 Picture 推导 Requirements（可验证的检验点）",
  "3. 从 Picture + 上下文推导 Constraints（贯穿全程的约束线）",
  "→ 检查 Req ∩ Cst 是否有矛盾 → 如有矛盾，沟通修正"
];
slide6.addText(
  steps.map((s, idx) => ({
    text: s,
    options: { bullet: idx < steps.length - 1, breakLine: idx < steps.length - 1 }
  })),
  {
    x: 0.7, y: 4.35, w: 8.5, h: 1.0,
    fontSize: 10, fontFace: "Arial",
    color: "4A4A4A", margin: 0
  }
);

// ============ Slide 7: Dual Plane ============
let slide7 = pres.addSlide();
slide7.background = { color: C.white };

// Title bar
slide7.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: C.navy }
});
slide7.addText("双重平面", {
  x: 0.5, y: 0.15, w: 9, h: 0.6,
  fontSize: 28, fontFace: "Arial", bold: true,
  color: C.white, margin: 0
});

// Two planes side by side
const planes = [
  {
    title: "状态平面",
    subtitle: "Status Plane",
    question: "\"我在哪、做到哪了、目标偏了没有\"",
    mount: "Agent 唤醒时强制挂载",
    content: "任务树结构 / Todo 完成度 / 任务状态 / Gotchas 指针 / Session 最近变化指针",
    color: "065A82",
    bgColor: "E3F2FD"
  },
  {
    title: "数据平面",
    subtitle: "Data Plane",
    question: "\"当前操作的是哪个版本的代码\"",
    mount: "按需展开，不默认加载",
    content: "各仓库当前 commit ID\n格式：{ repo_name }: \"{ commit_id }\"\n底层是 Git，可追溯、可 revert",
    color: "2C5F2D",
    bgColor: "E8F5E9"
  }
];

const planeW = 4.3;
planes.forEach((pl, i) => {
  const x = 0.5 + i * (planeW + 0.4);

  // Card
  slide7.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.1, w: planeW, h: 3.0,
    fill: { color: pl.bgColor },
    shadow: makeShadow()
  });

  // Title
  slide7.addText(pl.title, {
    x: x, y: 1.2, w: planeW, h: 0.45,
    fontSize: 20, fontFace: "Arial", bold: true,
    color: pl.color, align: "center", margin: 0
  });
  slide7.addText(pl.subtitle, {
    x: x, y: 1.6, w: planeW, h: 0.3,
    fontSize: 11, fontFace: "Arial", italic: true,
    color: pl.color, align: "center", margin: 0
  });

  // Divider
  slide7.addShape(pres.shapes.RECTANGLE, {
    x: x + 0.3, y: 2.0, w: planeW - 0.6, h: 0.02,
    fill: { color: pl.color, transparency: 50 }
  });

  // Question
  slide7.addText(pl.question, {
    x: x + 0.15, y: 2.1, w: planeW - 0.3, h: 0.45,
    fontSize: 11, fontFace: "Arial", bold: true,
    color: pl.color, margin: 0
  });

  // Mount info
  slide7.addText("挂载时机：" + pl.mount, {
    x: x + 0.15, y: 2.55, w: planeW - 0.3, h: 0.3,
    fontSize: 10, fontFace: "Arial",
    color: "4A4A4A", margin: 0
  });

  // Content
  slide7.addText(pl.content, {
    x: x + 0.15, y: 2.9, w: planeW - 0.3, h: 1.1,
    fontSize: 9, fontFace: "Arial",
    color: "4A4A4A", margin: 0, valign: "top"
  });
});

// Key insight box
slide7.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.3, w: 9, h: 1.1,
  fill: { color: C.navy },
  shadow: makeShadow()
});
slide7.addText("组装关系", {
  x: 0.7, y: 4.4, w: 2, h: 0.3,
  fontSize: 12, fontFace: "Arial", bold: true,
  color: C.white, margin: 0
});
slide7.addText("Session 是每个 Task 的私有历史，记录每个轮次的状态快照。版本快照模型，只追加不覆盖。\nSession 是状态平面的数据来源之一，但不等于平面本身——平面是某一时刻的聚合快照，Session 是快照的时间序列。", {
  x: 0.7, y: 4.7, w: 8.5, h: 0.65,
  fontSize: 10, fontFace: "Arial",
  color: C.iceBlue, margin: 0
});

// ============ Slide 8: Task Lifecycle ============
let slide8 = pres.addSlide();
slide8.background = { color: C.white };

// Title bar
slide8.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: C.navy }
});
slide8.addText("任务生命周期", {
  x: 0.5, y: 0.15, w: 9, h: 0.6,
  fontSize: 28, fontFace: "Arial", bold: true,
  color: C.white, margin: 0
});

// State diagram - horizontal flow
const states = [
  { name: "CREATED", desc: "模型已定义\n所有 Todo 未开始", color: "90A4AE" },
  { name: "IN_PROGRESS", desc: "至少一个 Todo\n已完成", color: "065A82" },
  { name: "VERIFYING", desc: "任务检验进行中\n（瞬态）", color: "FF8F00" },
  { name: "COMPLETED", desc: "目标达成\n认知生命周期结束", color: "2C5F2D" },
  { name: "ABANDONED", desc: "目标放弃\n记录 Gotcha", color: "B85042" }
];

const stateW = 1.6;
const stateStartX = 0.7;
const stateGap = 0.35;
const stateY = 1.5;

states.forEach((st, i) => {
  const x = stateStartX + i * (stateW + stateGap);

  // State circle
  slide8.addShape(pres.shapes.OVAL, {
    x: x + (stateW - 1.0) / 2, y: stateY, w: 1.0, h: 1.0,
    fill: { color: st.color },
    shadow: makeShadow()
  });

  // State name
  slide8.addText(st.name, {
    x: x, y: stateY + 0.25, w: stateW, h: 0.5,
    fontSize: 8, fontFace: "Arial", bold: true,
    color: C.white, align: "center", margin: 0
  });

  // Description
  slide8.addText(st.desc, {
    x: x, y: stateY + 1.1, w: stateW, h: 0.6,
    fontSize: 9, fontFace: "Arial",
    color: "4A4A4A", align: "center", margin: 0
  });

  // Arrow to next state
  if (i < states.length - 1 && i !== 1) {  // Skip after IN_PROGRESS (VERIFYING is different path)
    slide8.addText("→", {
      x: x + stateW - 0.1, y: stateY + 0.25, w: 0.5, h: 0.5,
      fontSize: 20, color: "9E9E9E", align: "center", margin: 0
    });
  }
});

// Transitions section
slide8.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 3.2, w: 9, h: 2.2,
  fill: { color: "F5F5F5" },
  shadow: makeShadow()
});
slide8.addText("状态转换规则", {
  x: 0.7, y: 3.3, w: 3, h: 0.35,
  fontSize: 14, fontFace: "Arial", bold: true,
  color: C.navy, margin: 0
});

const transitions = [
  "CREATED → IN_PROGRESS：任意 Todo 被标记为完成",
  "CREATED → ABANDONED：任务废弃",
  "IN_PROGRESS → COMPLETED：检验通过",
  "IN_PROGRESS → ABANDONED：任务废弃"
];

transitions.forEach((tr, i) => {
  slide8.addText(tr, {
    x: 0.9, y: 3.7 + i * 0.35, w: 8, h: 0.3,
    fontSize: 11, fontFace: "Arial",
    color: "4A4A4A", margin: 0
  });
});

// Note about VERIFYING
slide8.addShape(pres.shapes.RECTANGLE, {
  x: 0.7, y: 4.85, w: 8.5, h: 0.4,
  fill: { color: "FF8F00", transparency: 20 }
});
slide8.addText("注：VERIFYING 是瞬态，存在于检验执行期间，检验完成后立即转换到 COMPLETED 或 ABANDONED", {
  x: 0.8, y: 4.9, w: 8.3, h: 0.3,
  fontSize: 10, fontFace: "Arial", italic: true,
  color: "5D4037", margin: 0
});

// ============ Slide 9: Execution Flow ============
let slide9 = pres.addSlide();
slide9.background = { color: C.white };

// Title bar
slide9.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.9,
  fill: { color: C.navy }
});
slide9.addText("执行流程：三个核心动作", {
  x: 0.5, y: 0.15, w: 9, h: 0.6,
  fontSize: 28, fontFace: "Arial", bold: true,
  color: C.white, margin: 0
});

// Three steps
const steps9 = [
  {
    num: "1",
    title: "认知构建",
    desc: "轮次结束后生成状态平面快照。实时扫描，每次调用直接读文件系统，不缓存。",
    details: ["只输出当前状态，不做偏差判断", "全面覆盖，不隐藏任何节点", "非侵入，只读不写"]
  },
  {
    num: "2",
    title: "任务检验",
    desc: "判断当前状态是否满足 Picture。四层关卡（Tier 0-3），前两层客观，后一层按需。",
    details: ["Tier 0: Constraints 约束检查", "Tier 1: Todo 完成检查", "Tier 2: Requirements 满足检查", "Tier 3: 语义对齐检查（按需）"]
  },
  {
    num: "3",
    title: "状态更新",
    desc: "将检验结果反映到 Task 状态，并处理决策执行。Agent 自主决策下一步。",
    details: ["检验通过 → 标记完成", "检验未通过 → 决定下一步", "ABANDONED 由 Agent 主动标记"]
  }
];

const stepW = 2.9;
const stepStartX = 0.5;
const stepGap = 0.3;

steps9.forEach((st, i) => {
  const x = stepStartX + i * (stepW + stepGap);

  // Card
  slide9.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.1, w: stepW, h: 3.7,
    fill: { color: "FAFAFA" },
    shadow: makeShadow()
  });

  // Number circle
  slide9.addShape(pres.shapes.OVAL, {
    x: x + (stepW - 0.6) / 2, y: 1.2, w: 0.6, h: 0.6,
    fill: { color: C.navy }
  });
  slide9.addText(st.num, {
    x: x + (stepW - 0.6) / 2, y: 1.28, w: 0.6, h: 0.45,
    fontSize: 18, fontFace: "Arial Black", bold: true,
    color: C.white, align: "center", margin: 0
  });

  // Title
  slide9.addText(st.title, {
    x: x, y: 1.9, w: stepW, h: 0.4,
    fontSize: 16, fontFace: "Arial", bold: true,
    color: C.navy, align: "center", margin: 0
  });

  // Description
  slide9.addText(st.desc, {
    x: x + 0.1, y: 2.3, w: stepW - 0.2, h: 0.9,
    fontSize: 9, fontFace: "Arial",
    color: "4A4A4A", margin: 0, valign: "top"
  });

  // Divider
  slide9.addShape(pres.shapes.RECTANGLE, {
    x: x + 0.2, y: 3.2, w: stepW - 0.4, h: 0.02,
    fill: { color: C.navy, transparency: 70 }
  });

  // Details
  slide9.addText(
    st.details.map((d, idx) => ({
      text: d,
      options: { bullet: true, breakLine: idx < st.details.length - 1 }
    })),
    {
      x: x + 0.1, y: 3.3, w: stepW - 0.2, h: 1.4,
      fontSize: 8, fontFace: "Arial",
      color: "4A4A4A", margin: 0, valign: "top"
    }
  );
});

// Arrow between steps
slide9.addText("→", {
  x: 3.4, y: 2.5, w: 0.4, h: 0.5,
  fontSize: 24, color: C.navy, align: "center", margin: 0
});
slide9.addText("→", {
  x: 6.6, y: 2.5, w: 0.4, h: 0.5,
  fontSize: 24, color: C.navy, align: "center", margin: 0
});

// Bottom note
slide9.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 4.95, w: 9, h: 0.5,
  fill: { color: C.navy, transparency: 10 }
});
slide9.addText("三个动作在每个轮次结束后依次执行，构成完整的感知-判断-更新闭环", {
  x: 0.5, y: 5.05, w: 9, h: 0.3,
  fontSize: 12, fontFace: "Arial", bold: true,
  color: C.navy, align: "center", margin: 0
});

// ============ Slide 10: Conclusion ============
let slide10 = pres.addSlide();
slide10.background = { color: C.navy };

// Title
slide10.addText("结语", {
  x: 0.5, y: 0.8, w: 9, h: 0.7,
  fontSize: 36, fontFace: "Arial", bold: true,
  color: C.white, align: "center", margin: 0
});

// Central quote
slide10.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1.8, w: 8, h: 2.0,
  fill: { color: C.iceBlue, transparency: 15 }
});

slide10.addText("Agent 在执行一个需要数百轮交互的长路径任务时，\n最终可能无法回答一个看似简单的问题：\n我现在在哪里？", {
  x: 1.2, y: 1.9, w: 7.6, h: 1.2,
  fontSize: 16, fontFace: "Arial",
  color: C.white, align: "center", margin: 0
});

slide10.addText("mem0ress 的全部设计，\n都在试图让这个问题变得可回答。", {
  x: 1.2, y: 3.1, w: 7.6, h: 0.6,
  fontSize: 14, fontFace: "Arial", bold: true,
  color: C.iceBlue, align: "center", margin: 0
});

// Three design pillars
const conclusions = [
  "任务模型将目标、进度和边界封装为可判断的整体",
  "双重平面将认知状态和数据状态分开处理",
  "快照协议确保每轮结束时的状态变更可被追踪"
];

slide10.addText(
  conclusions.map((c, idx) => ({
    text: c,
    options: { bullet: true, breakLine: idx < conclusions.length - 1 }
  })),
  {
    x: 2, y: 4.0, w: 6, h: 1.0,
    fontSize: 12, fontFace: "Arial",
    color: C.iceBlue, margin: 0, valign: "top"
  }
);

// Final question
slide10.addShape(pres.shapes.RECTANGLE, {
  x: 2, y: 5.0, w: 6, h: 0.5,
  fill: { color: C.iceBlue }
});
slide10.addText("我的目标是什么，我现在距离它还有多远？", {
  x: 2, y: 5.05, w: 6, h: 0.4,
  fontSize: 13, fontFace: "Arial", bold: true, italic: true,
  color: C.navy, align: "center", margin: 0
});

// Save
pres.writeFile({ fileName: "/Users/gpdi/code/ai/mem0ress/slides_output/mem0ress_spec.pptx" })
  .then(() => console.log("PPTX created: mem0ress_spec.pptx"))
  .catch(err => console.error(err));
