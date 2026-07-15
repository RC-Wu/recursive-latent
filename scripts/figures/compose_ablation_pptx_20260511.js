#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = "/Users/fanta/code/agent/Code/recursive_3d_generative_growth";
const FIG_DIR = path.join(ROOT, "paper_siga/figures/ablation_pptx_20260511");
const PROJECTION_MANIFEST = path.join(FIG_DIR, "projection_ablation_visual_manifest_20260511.json");
const NATURALIZATION_MANIFEST = path.join(FIG_DIR, "masked_naturalization_visual_manifest_20260511.json");

const WHITE = "FFFFFF";
const INK = "1D2329";
const MUTED = "58636F";
const LINE = "D8E0E8";
const ACCENT = "C43730";
let SHAPES = null;

const TASK_LABELS = {
  coral_frontier: "coral frontier",
  ifs_crystal: "IFS crystal",
  botanical_root: "botanical root",
  vine_trellis: "vine trellis",
};

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function assertFile(file) {
  if (!fs.existsSync(file)) throw new Error(`Missing input: ${file}`);
}

function manifestsFor(kind) {
  const data = readJson(kind === "projection" ? PROJECTION_MANIFEST : NATURALIZATION_MANIFEST);
  return Array.isArray(data) ? data : [data];
}

function groupPanels(manifest) {
  const grouped = {};
  for (const panel of manifest.panels) {
    assertFile(panel.path);
    grouped[panel.variant] = grouped[panel.variant] || {};
    grouped[panel.variant][panel.kind] = panel.path;
  }
  return grouped;
}

function addHeader(slide, title, subtitle) {
  slide.background = { color: WHITE };
  slide.addText(title, {
    x: 0.26, y: 0.11, w: 5.9, h: 0.16,
    fontFace: "Arial", fontSize: 7.8, bold: true, color: INK, margin: 0,
  });
  slide.addText(subtitle, {
    x: 4.25, y: 0.12, w: 8.78, h: 0.13,
    fontFace: "Arial", fontSize: 4.8, color: MUTED, margin: 0, align: "right",
  });
  slide.addShape(SHAPES.line, { x: 0.26, y: 0.35, w: 12.78, h: 0, line: { color: LINE, width: 0.30 } });
}

function addLabel(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x, y, w, h,
    fontFace: "Arial",
    fontSize: opts.fontSize || 5.8,
    bold: Boolean(opts.bold),
    color: opts.color || MUTED,
    align: opts.align || "center",
    valign: "mid",
    margin: 0,
    fit: "shrink",
  });
}

function addImageCell(slide, img, x, y, w, h) {
  slide.addImage({
    path: img,
    x, y, w, h,
    sizing: { type: "contain", x, y, w, h },
  });
}

function addAblationSlide(pres, kind, manifests) {
  const slide = pres.addSlide();
  if (kind === "projection") {
    addHeader(
      slide,
      "Experiment 2: projection inside the loop",
      "Two held-out visual cases; rows are different roots, columns are matched projection variants, and red boxes mark independent zoom renders."
    );
  } else {
    addHeader(
      slide,
      "Experiment 4: masked local naturalization",
      "Two visual cases not used in Experiment 2; rows cross case and zoom level, columns compare local-realization variants."
    );
  }

  const variants = manifests[0].variants;
  const labels = manifests[0].labels;
  const left = 0.64;
  const right = 0.20;
  const rowLabelW = 0.86;
  const gapX = 0.07;
  const gapY = 0.12;
  const headerY = 0.43;
  const cellY = 0.65;
  const footerH = 0.15;
  const availableW = 13.33 - left - right - rowLabelW;
  const cellW = (availableW - gapX * (variants.length - 1)) / variants.length;
  const cellH = kind === "projection" ? 1.48 : 1.34;
  const caseGap = kind === "projection" ? 0.15 : 0.11;

  for (let i = 0; i < labels.length; i += 1) {
    const x = left + rowLabelW + i * (cellW + gapX);
    addLabel(slide, labels[i], x, headerY, cellW, 0.16, { fontSize: 5.6, bold: true, color: INK });
  }

  manifests.forEach((manifest, caseIdx) => {
    const grouped = groupPanels(manifest);
    const caseTop = cellY + caseIdx * (2 * cellH + gapY + caseGap);
    const taskLabel = TASK_LABELS[manifest.task_id] || manifest.task_id;
    addLabel(slide, taskLabel, 0.23, caseTop + 0.08, rowLabelW, 0.18, {
      fontSize: 6.3,
      bold: true,
      color: INK,
      align: "left",
    });
    addLabel(slide, "overview", 0.23, caseTop + 0.40, rowLabelW, 0.15, { fontSize: 5.4, align: "left" });
    addLabel(slide, "zoom", 0.23, caseTop + cellH + gapY + 0.40, rowLabelW, 0.15, { fontSize: 5.4, align: "left" });
    slide.addShape(SHAPES.line, {
      x: 0.26,
      y: caseTop + 2 * cellH + gapY + caseGap * 0.52,
      w: 12.78,
      h: 0,
      line: { color: LINE, width: caseIdx === manifests.length - 1 ? 0 : 0.25 },
    });
    for (let i = 0; i < variants.length; i += 1) {
      const variant = variants[i];
      const x = left + rowLabelW + i * (cellW + gapX);
      addImageCell(slide, grouped[variant].overview, x, caseTop, cellW, cellH);
      addImageCell(slide, grouped[variant].zoom, x, caseTop + cellH + gapY, cellW, cellH);
    }
  });

  slide.addText("Overview panels use the same case-level camera; zoom panels are separately rendered from the red boxed footprint.", {
    x: 0.27, y: 7.22, w: 12.70, h: footerH,
    fontFace: "Arial", fontSize: 5.6, color: MUTED, margin: 0,
  });
  slide.addText("red box = zoom footprint", {
    x: 10.85, y: 7.22, w: 1.88, h: footerH,
    fontFace: "Arial", fontSize: 5.4, color: ACCENT, margin: 0, align: "right",
  });
}

async function buildDeck(kind) {
  const manifests = manifestsFor(kind);
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = "PS-RSLG";
  pres.subject = `${kind} ablation PPTX-first figure`;
  pres.title = `${kind} ablation`;
  SHAPES = pres.ShapeType;
  addAblationSlide(pres, kind, manifests);
  const basename = kind === "projection" ? "projection_ablation_pptx_20260511" : "masked_naturalization_ablation_pptx_20260511";
  const out = path.join(FIG_DIR, `${basename}.pptx`);
  await pres.writeFile({ fileName: out });
  return {
    kind,
    pptx: out,
    source_manifest: kind === "projection" ? PROJECTION_MANIFEST : NATURALIZATION_MANIFEST,
    task_ids: manifests.map((m) => m.task_id),
    page_count: 1,
  };
}

async function main() {
  fs.mkdirSync(FIG_DIR, { recursive: true });
  const projection = await buildDeck("projection");
  const naturalization = await buildDeck("naturalization");
  const summary = {
    schema: "ablation_pptx_20260511",
    projection,
    naturalization,
    workflow_contract: "PPTX-first single-page paper figures; export these PPTX files to PDF before LaTeX inclusion",
  };
  fs.writeFileSync(path.join(FIG_DIR, "ablation_pptx_summary_20260511.json"), JSON.stringify(summary, null, 2));
  console.log(JSON.stringify(summary, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
