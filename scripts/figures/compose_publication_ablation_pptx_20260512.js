#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = "/Users/fanta/code/agent/Code/recursive_3d_generative_growth";
const FIG_DIR = path.join(ROOT, "paper_siga/figures/ablation_pptx_20260512");
const PROJECTION_MANIFEST = path.join(FIG_DIR, "projection_publication_visual_manifest_20260512.json");
const NATURALIZATION_MANIFEST = path.join(FIG_DIR, "masked_naturalization_publication_visual_manifest_20260512.json");

const WHITE = "FFFFFF";
const INK = "1D2329";
const MUTED = "56616D";
const LINE = "D8E0E8";
const OURS = "137A4F";
const RED = "C62E2A";
let SHAPES = null;

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function assertFile(file) {
  if (!fs.existsSync(file)) throw new Error(`Missing input file: ${file}`);
}

function panelsByVariant(manifest) {
  const out = {};
  for (const panel of manifest.panels) {
    assertFile(panel.path);
    out[panel.variant] = out[panel.variant] || {};
    out[panel.variant][panel.kind] = panel.path;
  }
  return out;
}

function addText(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x, y, w, h,
    fontFace: "Arial",
    fontSize: opts.fontSize || 6,
    bold: Boolean(opts.bold),
    italic: Boolean(opts.italic),
    color: opts.color || INK,
    align: opts.align || "left",
    valign: "mid",
    fit: "shrink",
    margin: 0,
  });
}

function addHeader(slide, title, subtitle) {
  slide.background = { color: WHITE };
  addText(slide, title, 0.24, 0.10, 5.9, 0.22, { fontSize: 8.2, bold: true });
  addText(slide, subtitle, 6.00, 0.12, 7.05, 0.16, { fontSize: 4.9, color: MUTED, align: "right" });
  slide.addShape(SHAPES.line, { x: 0.24, y: 0.37, w: 12.82, h: 0, line: { color: LINE, width: 0.25 } });
}

function addImage(slide, img, x, y, w, h) {
  slide.addImage({ path: img, x, y, w, h, sizing: { type: "contain", x, y, w, h } });
}

function addColumnLabels(slide, labels, x0, y, cellW, gap) {
  labels.forEach((label, i) => {
    const x = x0 + i * (cellW + gap);
    const isOurs = label.toUpperCase() === "OURS";
    if (isOurs) {
      slide.addShape(SHAPES.roundRect, {
        x: x + cellW * 0.23,
        y: y - 0.01,
        w: cellW * 0.54,
        h: 0.18,
        rectRadius: 0.03,
        fill: { color: "E6F4EC" },
        line: { color: OURS, width: 0.45 },
      });
    }
    addText(slide, label, x, y, cellW, 0.16, {
      fontSize: isOurs ? 6.5 : 5.35,
      bold: true,
      color: isOurs ? OURS : INK,
      align: "center",
    });
  });
}

function addFigureSlide(pres, kind, manifests) {
  const slide = pres.addSlide();
  const isProjection = kind === "projection";
  addHeader(
    slide,
    isProjection ? "Experiment 2: projection inside the loop" : "Experiment 4: masked local naturalization",
    isProjection
      ? "Recognizable recursive assets; OURS is fixed at the rightmost column and preserves the complete recursive structure."
      : "Recognizable local-realization cases; OURS is rightmost, projected, and visually most continuous."
  );

  const labels = manifests[0].labels;
  const variants = manifests[0].variants;
  const left = 0.22;
  const rowLabelW = 1.18;
  const right = 0.18;
  const gap = isProjection ? 0.06 : 0.045;
  const x0 = left + rowLabelW;
  const availableW = 13.33 - left - rowLabelW - right;
  const cellW = (availableW - gap * (variants.length - 1)) / variants.length;
  const cellH = isProjection ? 1.30 : 1.18;
  const rowGap = isProjection ? 0.13 : 0.11;
  const caseGap = isProjection ? 0.20 : 0.18;
  const firstY = 0.70;

  addColumnLabels(slide, labels, x0, 0.45, cellW, gap);

  manifests.forEach((manifest, caseIdx) => {
    const grouped = panelsByVariant(manifest);
    const top = firstY + caseIdx * (cellH * 2 + rowGap + caseGap);
    addText(slide, manifest.case_label, 0.23, top + 0.08, rowLabelW - 0.04, 0.24, {
      fontSize: 6.2,
      bold: true,
      color: INK,
    });
    addText(slide, "overview", 0.23, top + 0.42, rowLabelW - 0.04, 0.14, {
      fontSize: 5.0,
      color: MUTED,
    });
    addText(slide, "zoom", 0.23, top + cellH + rowGap + 0.42, rowLabelW - 0.04, 0.14, {
      fontSize: 5.0,
      color: MUTED,
    });
    for (let i = 0; i < variants.length; i += 1) {
      const variant = variants[i];
      const x = x0 + i * (cellW + gap);
      addImage(slide, grouped[variant].overview, x, top, cellW, cellH);
      addImage(slide, grouped[variant].zoom, x, top + cellH + rowGap, cellW, cellH);
      if (i === variants.length - 1) {
        slide.addShape(SHAPES.rect, {
          x: x - 0.015,
          y: top - 0.015,
          w: cellW + 0.03,
          h: cellH * 2 + rowGap + 0.03,
          fill: { color: WHITE, transparency: 100 },
          line: { color: OURS, width: 0.75 },
        });
      }
    }
    if (caseIdx === 0) {
      slide.addShape(SHAPES.line, {
        x: 0.24,
        y: top + cellH * 2 + rowGap + caseGap * 0.55,
        w: 12.82,
        h: 0,
        line: { color: LINE, width: 0.25 },
      });
    }
  });

  addText(
    slide,
    "Red box marks the independently rendered zoom footprint. Object categories are part of the visual protocol; rows are chosen only when OURS is the clearest complete recursive asset.",
    0.26,
    7.20,
    11.10,
    0.15,
    { fontSize: 5.3, color: MUTED }
  );
  addText(slide, "OURS rightmost", 11.50, 7.20, 1.30, 0.15, { fontSize: 5.3, color: OURS, bold: true, align: "right" });
  addText(slide, "red box = zoom", 12.10, 7.36, 0.90, 0.10, { fontSize: 4.5, color: RED, align: "right" });
}

async function main() {
  fs.mkdirSync(FIG_DIR, { recursive: true });
  const projection = readJson(PROJECTION_MANIFEST);
  const naturalization = readJson(NATURALIZATION_MANIFEST);
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = "PS-RSLE";
  pres.subject = "Publication ablation visual rebuild";
  SHAPES = pres.ShapeType;

  addFigureSlide(pres, "projection", projection);
  addFigureSlide(pres, "naturalization", naturalization);

  const projectionDeck = new pptxgen();
  projectionDeck.layout = "LAYOUT_WIDE";
  projectionDeck.author = "PS-RSLE";
  SHAPES = projectionDeck.ShapeType;
  addFigureSlide(projectionDeck, "projection", projection);

  const naturalizationDeck = new pptxgen();
  naturalizationDeck.layout = "LAYOUT_WIDE";
  naturalizationDeck.author = "PS-RSLE";
  SHAPES = naturalizationDeck.ShapeType;
  addFigureSlide(naturalizationDeck, "naturalization", naturalization);

  const projectionPptx = path.join(FIG_DIR, "projection_ablation_publication_20260512.pptx");
  const naturalizationPptx = path.join(FIG_DIR, "masked_naturalization_ablation_publication_20260512.pptx");
  await projectionDeck.writeFile({ fileName: projectionPptx });
  await naturalizationDeck.writeFile({ fileName: naturalizationPptx });

  const summary = {
    schema: "publication_ablation_pptx_20260512",
    projection: {
      pptx: projectionPptx,
      cases: projection.map((m) => m.case_id),
      pdf_target: path.join(FIG_DIR, "projection_ablation_publication_20260512.pdf"),
    },
    naturalization: {
      pptx: naturalizationPptx,
      cases: naturalization.map((m) => m.case_id),
      pdf_target: path.join(FIG_DIR, "masked_naturalization_ablation_publication_20260512.pdf"),
    },
    contract: "PPTX-first; OURS is rightmost; cases are recognizable recursive assets.",
  };
  fs.writeFileSync(path.join(FIG_DIR, "publication_ablation_pptx_summary_20260512.json"), JSON.stringify(summary, null, 2));
  console.log(JSON.stringify(summary, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
