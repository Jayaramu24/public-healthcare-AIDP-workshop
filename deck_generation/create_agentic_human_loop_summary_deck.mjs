import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const NODE_MODULES = "/Users/jayarkri/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";
const pptxgen = require(path.join(NODE_MODULES, "pptxgenjs"));
const sharp = require(path.join(NODE_MODULES, "sharp"));

const OUT_DIR = path.resolve("outputs/public_healthcare_lakehouse_workshop/downloads");
const OUT_FILE = path.join(OUT_DIR, "public_healthcare_aidp_workshop_summary_deck.pptx");

const ASSETS = {
  oacDashboard: path.resolve("outputs/public_healthcare_lakehouse_workshop/assets/oac_dashboard_lab/oac_executive_overview_final.png"),
  oacAssistant: path.resolve("outputs/public_healthcare_lakehouse_workshop/assets/oac_dashboard_lab/screenshots/43_oac_live_consumer_assistant_denied_claims_expanded_clean.png"),
  agentFlow: path.resolve("outputs/public_healthcare_lakehouse_workshop/assets/aidp_agent_lab/screenshots/01_agent_flow_development_canvas.png"),
  mlMetrics: path.resolve("outputs/public_healthcare_lakehouse_workshop/assets/aidp_ml_lab/screenshots/04_ml_run_metrics_train_test.png"),
  healthContext: path.resolve("outputs/public_healthcare_lakehouse_workshop/assets/public_healthcare_context.png"),
};

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Oracle";
pptx.company = "Oracle";
pptx.subject = "Agentic AI with Human in Loop workshop factory";
pptx.title = "Agentic AI with Human in Loop for Repeatable Industry Use Cases";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US",
};
pptx.defineLayout({ name: "LAYOUT_WIDE", width: 13.333, height: 7.5 });

const SLIDE_W = 13.333;
const SLIDE_H = 7.5;
const COLORS = {
  bg: "FBF8F3",
  panel: "FFFFFF",
  panel2: "FFF2EA",
  ink: "2F2A26",
  muted: "6C625C",
  light: "EEE5DD",
  red: "C74634",
  redDark: "8F2B1D",
  blue: "315F79",
  green: "4F7C5B",
  teal: "2C7C73",
  amber: "D87B2A",
  gold: "B66D00",
  purple: "6E5A8D",
};

const FONT = {
  title: "Aptos Display",
  body: "Aptos",
};

function addBg(slide) {
  slide.background = { color: COLORS.bg };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: SLIDE_W,
    h: SLIDE_H,
    fill: { color: COLORS.bg },
    line: { color: COLORS.bg },
  });
}

function addFooter(slide, left = "PHIC example: Public Healthcare AIDP Workshop", right = "Agentic AI with Human in Loop") {
  slide.addShape(pptx.ShapeType.line, {
    x: 0.55,
    y: 7.08,
    w: 12.25,
    h: 0,
    line: { color: "E2D8D0", width: 0.6 },
  });
  addText(slide, left, 0.9, 7.22, 4.1, 0.16, { size: 6.8, color: "7B7069" });
  addText(slide, right, 8.55, 7.22, 3.9, 0.16, { size: 6.8, color: "7B7069" });
}

function addText(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x,
    y,
    w,
    h,
    fontFace: opts.fontFace ?? FONT.body,
    fontSize: opts.size ?? 14,
    color: opts.color ?? COLORS.ink,
    bold: opts.bold ?? false,
    italic: opts.italic ?? false,
    align: opts.align ?? "center",
    valign: opts.valign ?? "mid",
    margin: opts.margin ?? 0.04,
    fit: opts.fit ?? "shrink",
    breakLine: false,
  });
}

function addPill(slide, text, x, y, w, color, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h: opts.h ?? 0.28,
    rectRadius: 0.06,
    fill: { color, transparency: opts.transparency ?? 0 },
    line: { color, transparency: 100 },
  });
  addText(slide, text, x + 0.05, y + 0.03, w - 0.1, (opts.h ?? 0.28) - 0.06, {
    size: opts.size ?? 8.8,
    bold: true,
    color: opts.textColor ?? "FFFFFF",
  });
}

function addCard(slide, x, y, w, h, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: opts.radius ?? 0.12,
    fill: { color: opts.fill ?? COLORS.panel, transparency: opts.transparency ?? 0 },
    line: { color: opts.line ?? "E3D8D1", width: opts.lineWidth ?? 0.7 },
    shadow: opts.shadow === false ? undefined : { type: "outer", color: "CFC2BA", opacity: 0.17, blur: 1.2, angle: 45, distance: 1 },
  });
}

function addStep(slide, num, title, body, x, y, w, color) {
  slide.addShape(pptx.ShapeType.ellipse, {
    x,
    y,
    w: 0.45,
    h: 0.45,
    fill: { color },
    line: { color, transparency: 100 },
  });
  addText(slide, String(num), x, y + 0.02, 0.45, 0.36, { size: 11, bold: true, color: "FFFFFF" });
  addText(slide, title, x + 0.62, y - 0.02, w - 0.62, 0.23, { size: 12.5, bold: true });
  addText(slide, body, x + 0.62, y + 0.25, w - 0.62, 0.42, { size: 8.7, color: COLORS.muted });
}

function addArrow(slide, x1, y1, x2, y2, color = COLORS.red, width = 1.4) {
  slide.addShape(pptx.ShapeType.line, {
    x: x1,
    y: y1,
    w: x2 - x1,
    h: y2 - y1,
    line: { color, width, endArrowType: "triangle" },
  });
}

async function imageMeta(file) {
  const meta = await sharp(file).metadata();
  return { width: meta.width, height: meta.height };
}

async function addImageFit(slide, file, x, y, w, h, opts = {}) {
  const meta = await imageMeta(file);
  const imgAspect = meta.width / meta.height;
  const boxAspect = w / h;
  let iw = w;
  let ih = h;
  let ix = x;
  let iy = y;
  if (imgAspect > boxAspect) {
    iw = w;
    ih = w / imgAspect;
    iy = y + (h - ih) / 2;
  } else {
    ih = h;
    iw = h * imgAspect;
    ix = x + (w - iw) / 2;
  }
  if (opts.frame) addCard(slide, x, y, w, h, { fill: "FFFFFF", line: opts.line ?? "E2D8D0", radius: 0.08 });
  slide.addImage({ path: file, x: ix, y: iy, w: iw, h: ih });
}

function addTitle(slide, title, subtitle, opts = {}) {
  addText(slide, title, 0.72, opts.y ?? 0.45, 11.9, 0.55, {
    fontFace: FONT.title,
    size: opts.size ?? 25,
    color: COLORS.ink,
    bold: false,
  });
  if (subtitle) {
    addText(slide, subtitle, 1.15, (opts.y ?? 0.45) + 0.72, 11.0, 0.32, {
      size: opts.subSize ?? 10.6,
      color: COLORS.muted,
    });
  }
}

function addMiniMedallion(slide, x, y, w, h) {
  const boxW = 0.58;
  const boxH = 0.36;
  const gap = (w - boxW * 5) / 4;
  const top = y + 0.27;
  const labels = [
    { text: "Raw", color: "F2E8DF" },
    { text: "Bronze", color: "E7D0C4" },
    { text: "Silver", color: "E8EDF0" },
    { text: "Gold", color: "F5E0AF" },
    { text: "AI\nLakehouse", color: "DCE9F0" },
  ];

  addCard(slide, x + boxW + gap * 0.55, y + 0.05, boxW * 3 + gap * 2.05, h - 0.1, {
    fill: "F7FBFD",
    line: "D4E5ED",
    radius: 0.07,
    shadow: false,
  });
  addText(slide, "AIDP medallion architecture", x + boxW + gap * 0.55, y + 0.09, boxW * 3 + gap * 2.05, 0.14, {
    size: 5.8,
    bold: true,
    color: COLORS.blue,
  });

  labels.forEach((node, idx) => {
    const nx = x + idx * (boxW + gap);
    addCard(slide, nx, top, boxW, boxH, {
      fill: node.color,
      line: idx === 4 ? "AFC9D7" : "D6CBC3",
      radius: 0.05,
      shadow: false,
    });
    addText(slide, node.text, nx + 0.03, top + 0.07, boxW - 0.06, boxH - 0.12, {
      size: idx === 4 ? 5.5 : 6.2,
      bold: true,
      color: idx === 4 ? COLORS.blue : COLORS.ink,
    });
    if (idx < labels.length - 1) {
      addArrow(slide, nx + boxW + 0.02, top + boxH / 2, nx + boxW + gap - 0.04, top + boxH / 2, idx === 3 ? COLORS.red : COLORS.blue, 0.8);
    }
  });

  addText(slide, "Gold star schema push", x + 2.38, y + 0.72, 0.9, 0.12, {
    size: 5.3,
    color: COLORS.redDark,
    bold: true,
  });
}

async function slide1() {
  const slide = pptx.addSlide();
  addBg(slide);
  addPill(slide, "AGENTIC AI + HUMAN IN LOOP", 0.75, 0.28, 2.05, COLORS.red, { size: 7.4 });
  addTitle(
    slide,
    "A repeatable way to build industry use cases with PHIC as the proof",
    "Codex acts as the delivery agent; humans provide industry judgment, service access, validation, and final approval.",
    { y: 0.68, size: 24, subSize: 10.7 }
  );

  addCard(slide, 0.82, 1.7, 5.55, 4.95, { fill: "FFF8F3", line: "E9D9CF" });
  addText(slide, "Agentic build loop", 1.05, 1.92, 5.05, 0.28, { size: 16, bold: true, color: COLORS.redDark });
  const loop = [
    ["1", "Read the industry signal", "Use public research, business goals, and participant personas.", COLORS.blue],
    ["2", "Generate the workshop system", "Synthetic data, medallion notebooks, star schema, ML, agents, guide.", COLORS.red],
    ["3", "Human validates in real OCI", "Log in, test each step, correct product behavior, approve checkpoints.", COLORS.green],
    ["4", "Publish reusable assets", "GitHub Pages site, PDF guide, raw data bundle, notebooks, SQL, deck.", COLORS.gold],
  ];
  loop.forEach((item, idx) => {
    const yy = 2.45 + idx * 0.88;
    slide.addShape(pptx.ShapeType.ellipse, {
      x: 1.1,
      y: yy,
      w: 0.44,
      h: 0.44,
      fill: { color: item[3] },
      line: { color: item[3], transparency: 100 },
    });
    addText(slide, item[0], 1.1, yy + 0.02, 0.44, 0.34, { size: 10, bold: true, color: "FFFFFF" });
    addText(slide, item[1], 1.75, yy - 0.02, 3.95, 0.23, { size: 12.2, bold: true });
    addText(slide, item[2], 1.75, yy + 0.24, 3.95, 0.34, { size: 8.8, color: COLORS.muted });
    if (idx < loop.length - 1) addArrow(slide, 1.32, yy + 0.53, 1.32, yy + 0.78, COLORS.light, 1.0);
  });

  addCard(slide, 6.72, 1.7, 5.8, 4.95, { fill: "FFFFFF", line: "E8DED7" });
  addText(slide, "PHIC example output", 7.0, 1.94, 5.25, 0.28, { size: 15.5, bold: true, color: COLORS.blue });
  await addImageFit(slide, ASSETS.oacDashboard, 7.02, 2.35, 5.18, 3.05, { frame: true });
  addText(
    slide,
    "A working public healthcare claims command center, backed by generated data, AIDP pipelines, AI Lakehouse star schema, OAC analytics, ML, and an AI policy copilot.",
    7.08,
    5.58,
    5.05,
    0.62,
    { size: 10.5, color: COLORS.muted }
  );
  addFooter(slide);
}

function flowBlock(slide, x, y, w, h, title, label, color) {
  addCard(slide, x, y, w, h, { fill: "FFFFFF", line: "E7DDD5", radius: 0.09 });
  addPill(slide, label, x + 0.14, y + 0.14, 1.25, color, { size: 7.2, h: 0.24 });
  addText(slide, title, x + 0.18, y + 0.48, w - 0.36, 0.3, { size: 12.2, bold: true });
}

async function slide2() {
  const slide = pptx.addSlide();
  addBg(slide);
  addTitle(
    slide,
    "The pattern has three distinct flows, all validated through the same loop",
    "Data-to-insights, ML/MLOps, and Agentic AI are related, but each has its own build path and checkpoint rhythm.",
    { y: 0.42, size: 22.5 }
  );

  const rows = [
    {
      y: 1.55,
      color: COLORS.red,
      label: "FLOW 1",
      name: "Core data-to-insights",
      nodes: ["Object Storage\nraw data", "AIDP\nBronze/Silver/Gold", "AI Lakehouse\nclaims star schema", "OAC\nexecutive insights"],
      note: "Business users consume governed analytics and Assistant-ready dashboards.",
    },
    {
      y: 3.22,
      color: COLORS.green,
      label: "FLOW 2",
      name: "ML and MLOps",
      nodes: ["AI Lakehouse\nfeature data", "AIDP ML\ntrain/test/eval", "Experiment run\nmetrics + model", "Scored output\nfor action"],
      note: "Model work is grounded in the same gold-layer facts and dimensions.",
    },
    {
      y: 4.89,
      color: COLORS.blue,
      label: "FLOW 3",
      name: "AI Agent flow",
      nodes: ["AI Lakehouse\nSQL source", "Knowledge base\npolicy documents", "SQL + RAG\ntools", "Supervisor agent\nanswers + actions"],
      note: "The agent combines structured claims data with policy context.",
    },
  ];

  rows.forEach((row) => {
    addPill(slide, row.label, 0.75, row.y + 0.2, 0.88, row.color, { size: 6.9, h: 0.24 });
    addText(slide, row.name, 1.78, row.y + 0.1, 1.75, 0.42, { size: 11.6, bold: true });
    addText(slide, row.note, 1.75, row.y + 0.52, 1.9, 0.38, { size: 7.8, color: COLORS.muted });
    row.nodes.forEach((node, idx) => {
      const x = 3.95 + idx * 2.12;
      flowBlock(slide, x, row.y, 1.55, 0.96, node, idx === 0 ? "SOURCE" : idx === 3 ? "USE" : "BUILD", row.color);
      if (idx < row.nodes.length - 1) addArrow(slide, x + 1.6, row.y + 0.48, x + 2.03, row.y + 0.48, row.color, 1.4);
    });
  });

  addCard(slide, 0.9, 6.36, 11.52, 0.52, { fill: "FFF4EC", line: "F1CDBB", radius: 0.08, shadow: false });
  addText(
    slide,
    "Human checkpoints sit between every major transition: data realism, product setup, successful notebook runs, model metrics, agent test answers, and published GitHub Pages.",
    1.0,
    6.47,
    11.32,
    0.22,
    { size: 9.4, color: COLORS.redDark, bold: true }
  );
  addFooter(slide);
}

async function slide3() {
  const slide = pptx.addSlide();
  addBg(slide);
  addTitle(
    slide,
    "Human-in-loop turns Codex from a content generator into a delivery partner",
    "The method is intentionally interactive: Codex proposes and builds; humans approve, log in, test, and correct product-specific steps.",
    { y: 0.42, size: 22 }
  );

  addCard(slide, 0.86, 1.48, 5.65, 4.92, { fill: "FFFFFF", line: "E9DDD4" });
  addText(slide, "Agentic AI responsibilities", 1.18, 1.75, 5.0, 0.33, { size: 15.5, bold: true, color: COLORS.redDark });
  const aiItems = [
    ["Discover", "Research current industry challenges and propose use cases."],
    ["Synthesize", "Create raw data with depth, geographic spread, hierarchy, and useful noise."],
    ["Build", "Generate notebooks, SQL, star schema, ML flow, agent prompts, guide, and deck."],
    ["Validate Artifacts", "Run local checks for links, downloads, PDF/deck quality, and layout."],
  ];
  aiItems.forEach((item, idx) => {
    const y = 2.28 + idx * 0.82;
    addCard(slide, 1.15, y, 4.95, 0.55, { fill: "FFF7F2", line: "F0D6C7", radius: 0.05, shadow: false });
    addText(slide, item[0], 1.32, y + 0.09, 1.1, 0.22, { size: 9.7, bold: true, color: COLORS.redDark });
    addText(slide, item[1], 2.45, y + 0.07, 3.42, 0.27, { size: 8.6, color: COLORS.muted });
  });

  addCard(slide, 6.82, 1.48, 5.65, 4.92, { fill: "FFFFFF", line: "E9DDD4" });
  addText(slide, "Human validation responsibilities", 7.14, 1.75, 5.0, 0.33, { size: 15.5, bold: true, color: COLORS.blue });
  const humanItems = [
    ["Approve", "Confirm business story, personas, lab sequence, and data realism."],
    ["Access", "Log in to OCI, AIDP, AI Lakehouse, and OAC where live validation is needed."],
    ["Observe", "Capture true product screens and correct wrong assumptions immediately."],
    ["Sign off", "Verify the final workshop can be executed by new participants."],
  ];
  humanItems.forEach((item, idx) => {
    const y = 2.28 + idx * 0.82;
    addCard(slide, 7.11, y, 4.95, 0.55, { fill: "F6FAFC", line: "D7E4EC", radius: 0.05, shadow: false });
    addText(slide, item[0], 7.28, y + 0.09, 1.1, 0.22, { size: 9.7, bold: true, color: COLORS.blue });
    addText(slide, item[1], 8.41, y + 0.07, 3.42, 0.27, { size: 8.6, color: COLORS.muted });
  });

  addArrow(slide, 6.38, 3.78, 6.78, 3.78, COLORS.red, 1.8);
  slide.addShape(pptx.ShapeType.ellipse, {
    x: 5.92,
    y: 3.33,
    w: 1.0,
    h: 1.0,
    fill: { color: COLORS.ink },
    line: { color: COLORS.ink },
  });
  addText(slide, "HIL\nloop", 6.0, 3.5, 0.84, 0.42, { size: 11, bold: true, color: "FFFFFF" });

  addText(
    slide,
    "Result: repeatable industry-specific workshops that are generated fast, but still grounded in real product behavior and human domain judgment.",
    1.36,
    6.55,
    10.6,
    0.35,
    { size: 11.8, color: COLORS.redDark, bold: true }
  );
  addFooter(slide);
}

async function slide4() {
  const slide = pptx.addSlide();
  addBg(slide);
  addTitle(
    slide,
    "PHIC demonstrates the approach end to end",
    "The proof sequence follows the actual build order: data story, AIDP medallion to AI Lakehouse, OAC, ML, and Agent.",
    { y: 0.42, size: 23 }
  );

  const proofs = [
    {
      title: "1. Business context and data story",
      caption: "PHIC business problems are translated into synthetic claims, membership, provider, disbursement, JSON event, spatial, and policy-document data.",
      image: ASSETS.healthContext,
      color: COLORS.redDark,
      x: 0.62,
      y: 1.42,
    },
    {
      title: "2. AIDP medallion to AI Lakehouse",
      caption: "AIDP prepares Bronze, Silver, and Gold data, then writes the Claims star schema into AI Lakehouse for consumption.",
      diagram: "medallion",
      color: COLORS.blue,
      x: 4.75,
      y: 1.42,
    },
    {
      title: "3. OAC executive insight layer",
      caption: "The AI Lakehouse Claims star schema powers KPI tiles, denial analysis, geography, detailed tables, trends, and Assistant responses.",
      image: ASSETS.oacDashboard,
      color: COLORS.green,
      x: 8.88,
      y: 1.42,
    },
    {
      title: "4. ML train-test-evaluate flow",
      caption: "AIDP ML uses gold-layer claims features, splits train and test data, logs metrics, and registers the model for reuse.",
      image: ASSETS.mlMetrics,
      color: COLORS.teal,
      x: 2.67,
      y: 4.04,
    },
    {
      title: "5. Agentic claims copilot",
      caption: "The AIDP Agent Flow combines SQL over the claims star schema with RAG over policy documents through a supervised agent experience.",
      image: ASSETS.agentFlow,
      color: COLORS.gold,
      x: 6.8,
      y: 4.04,
    },
  ];

  for (const proof of proofs) {
    const w = 3.83;
    const h = 2.22;
    addCard(slide, proof.x, proof.y, w, h, { fill: "FFFFFF", line: "E8DAD2", radius: 0.1 });
    addText(slide, proof.title, proof.x + 0.14, proof.y + 0.13, w - 0.28, 0.24, {
      size: 10.7,
      bold: true,
      color: proof.color,
    });
    if (proof.diagram === "medallion") {
      addMiniMedallion(slide, proof.x + 0.23, proof.y + 0.55, w - 0.46, 0.88);
    } else {
      await addImageFit(slide, proof.image, proof.x + 0.42, proof.y + 0.52, w - 0.84, 0.92, { frame: true, line: "EFE5DD" });
    }
    addText(slide, proof.caption, proof.x + 0.25, proof.y + 1.56, w - 0.5, 0.42, {
      size: 7.35,
      color: COLORS.muted,
    });
  }

  addText(
    slide,
    "The same proof pattern can be reused for banking, manufacturing, insurance, public sector, telecom, or any business function with similar human validation checkpoints.",
    1.25,
    6.55,
    10.85,
    0.25,
    { size: 10.2, color: COLORS.redDark, bold: true }
  );

  addFooter(slide);
}

async function slide5() {
  const slide = pptx.addSlide();
  addBg(slide);
  addTitle(
    slide,
    "Scaling the method: one factory package, many industry workshops",
    "Teams can reuse the prompt package, folder structure, quality checklist, GitHub publishing flow, and service-specific patterns.",
    { y: 0.42, size: 23 }
  );

  const steps = [
    ["1", "Name industry", "Codex researches current public business challenges first.", COLORS.blue],
    ["2", "Approve design", "Human reviews use case, personas, labs, data, ML, and agent plan.", COLORS.green],
    ["3", "Build and test", "Codex creates assets; human validates in OCI services screen by screen.", COLORS.red],
    ["4", "Publish", "Git commands push the workshop to GitHub Pages for a stable URL.", COLORS.gold],
  ];

  steps.forEach((s, idx) => {
    const x = 0.86 + idx * 3.1;
    addCard(slide, x, 1.64, 2.58, 1.35, { fill: "FFFFFF", line: "E8DAD2", radius: 0.1 });
    slide.addShape(pptx.ShapeType.ellipse, {
      x: x + 1.06,
      y: 1.36,
      w: 0.46,
      h: 0.46,
      fill: { color: s[3] },
      line: { color: s[3], transparency: 100 },
    });
    addText(slide, s[0], x + 1.06, 1.39, 0.46, 0.32, { size: 10.5, bold: true, color: "FFFFFF" });
    addText(slide, s[1], x + 0.18, 1.85, 2.22, 0.22, { size: 11.2, bold: true });
    addText(slide, s[2], x + 0.2, 2.16, 2.18, 0.42, { size: 7.8, color: COLORS.muted });
    if (idx < steps.length - 1) addArrow(slide, x + 2.62, 2.28, x + 3.0, 2.28, COLORS.red, 1.2);
  });

  addCard(slide, 0.95, 3.55, 3.7, 1.62, { fill: "FFF7F2", line: "F0D0C2", radius: 0.1 });
  addText(slide, "Reusable data design standard", 1.18, 3.78, 3.22, 0.26, { size: 13, bold: true, color: COLORS.redDark });
  addText(
    slide,
    "Target raw volumes should create 100K-200K rows in the primary fact table, with trend depth, hierarchy, geography, segments, and controlled noise.",
    1.18,
    4.14,
    3.22,
    0.55,
    { size: 8.7, color: COLORS.muted }
  );

  addCard(slide, 4.88, 3.55, 3.7, 1.62, { fill: "F5FAFC", line: "D5E3EA", radius: 0.1 });
  addText(slide, "Codex service skill memory", 5.1, 3.78, 3.25, 0.26, { size: 13, bold: true, color: COLORS.blue });
  addText(
    slide,
    "The reusable package tells Codex to apply learned OCI, AIDP, AI Lakehouse, OAC, ML/MLOps, and Agent Flow patterns before producing new workshops.",
    5.1,
    4.14,
    3.25,
    0.55,
    { size: 8.5, color: COLORS.muted }
  );

  addCard(slide, 8.8, 3.55, 3.7, 1.62, { fill: "FFFFFF", line: "E8DAD2", radius: 0.1 });
  addText(slide, "Global delivery governance", 9.02, 3.78, 3.25, 0.26, { size: 13, bold: true, color: COLORS.green });
  addText(
    slide,
    "Quality checks cover step-screen alignment, executable notebooks, clean downloads, working GitHub Pages, and participant-safe wording.",
    9.02,
    4.14,
    3.25,
    0.55,
    { size: 8.6, color: COLORS.muted }
  );

  addCard(slide, 1.35, 5.78, 10.62, 0.68, { fill: "FFF2EA", line: "F0BFAF", radius: 0.1, shadow: false });
  addText(
    slide,
    "Takeaway: this is an Agentic AI with Human in Loop factory for repeatable, industry-specific Oracle data and AI use cases.",
    1.62,
    5.96,
    10.08,
    0.25,
    { size: 12.8, color: COLORS.redDark, bold: true }
  );
  addFooter(slide);
}

async function build() {
  for (const asset of Object.values(ASSETS)) {
    if (!fs.existsSync(asset)) throw new Error(`Missing asset: ${asset}`);
  }
  fs.mkdirSync(OUT_DIR, { recursive: true });
  await slide1();
  await slide2();
  await slide3();
  await slide4();
  await slide5();
  await pptx.writeFile({ fileName: OUT_FILE });
  console.log(`Wrote ${OUT_FILE}`);
}

build().catch((err) => {
  console.error(err);
  process.exit(1);
});
