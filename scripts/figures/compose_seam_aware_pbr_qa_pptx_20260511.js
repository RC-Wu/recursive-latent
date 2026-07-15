#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = "/Users/fanta/code/agent/Code/recursive_3d_generative_growth";
const OUT_DIR = path.join(ROOT, "paper_siga/figures/seam_aware_pbr_qa_pptx_20260511");
const OUT = path.join(OUT_DIR, "seam_aware_pbr_qa_20260511.pptx");

const V1 = path.join(ROOT, "visuals/seam_aware_texturing_batch_20260510_zoom_white");
const V2 = path.join(ROOT, "visuals/seam_aware_texturing_batch_v2_20260510_zoom_white_fast");
const PROC = path.join(ROOT, "visuals/seam_aware_procedural_pbr_20260511_zoom_white");

const WHITE = "FFFFFF";
const INK = "202428";
const MUTED = "65717C";
const LINE = "D8E0E8";
const RED = "BD3F34";
const BLUE = "2E6FAE";
let SHAPES = null;

const ROWS = [
  {
    family: "Root junction",
    claim: "v2 removes strong painted rings; object-space material removes UV island seams but is visually neutral.",
    v1: path.join(V1, "S01_root_seam_aware/strict_matched_zoom_comparison.png"),
    v2: path.join(V2, "S01a_root_continuous_bark_grain_lowcontrast/strict_matched_zoom_comparison.png"),
    proc: path.join(PROC, "S01a_root_procedural_bark_pbr/strict_matched_zoom_comparison.png"),
  },
  {
    family: "Coral frontier",
    claim: "Trellis texture remains blotchy; object-space ivory PBR is the cleanest seam-continuity candidate.",
    v1: path.join(V1, "S02_coral_seam_aware/strict_matched_zoom_comparison.png"),
    v2: path.join(V2, "S02c_coral_bone_ridge_plain/strict_matched_zoom_comparison.png"),
    proc: path.join(PROC, "S02c_coral_procedural_ivory_pbr/strict_matched_zoom_comparison.png"),
  },
  {
    family: "Pyrite / lattice",
    claim: "Low-contrast Trellis v2 is smooth but weak; procedural metallic facets better support transform-copy visuals.",
    v1: path.join(V1, "S03_ifs_seam_aware/strict_matched_zoom_comparison.png"),
    v2: path.join(V2, "S03a_pyrite_brushed_facets_lowcontrast/strict_matched_zoom_comparison.png"),
    proc: path.join(PROC, "S03a_pyrite_procedural_facets_pbr/strict_matched_zoom_comparison.png"),
  },
];

function assertInputs() {
  for (const row of ROWS) {
    for (const key of ["v1", "v2", "proc"]) {
      if (!fs.existsSync(row[key])) {
        throw new Error(`Missing ${row.family} ${key}: ${row[key]}`);
      }
    }
  }
}

function addImage(slide, imagePath, x, y, w, h) {
  slide.addImage({ path: imagePath, x, y, w, h, sizing: { type: "contain", x, y, w, h } });
  slide.addShape(SHAPES.rect, {
    x, y, w, h,
    fill: { color: WHITE, transparency: 100 },
    line: { color: LINE, width: 0.45 },
  });
}

function addTitle(slide, title, subtitle) {
  slide.background = { color: WHITE };
  slide.addText(title, {
    x: 0.34, y: 0.22, w: 12.2, h: 0.34,
    fontFace: "Arial", fontSize: 18, bold: true, color: INK, margin: 0,
  });
  slide.addText(subtitle, {
    x: 0.34, y: 0.58, w: 12.4, h: 0.24,
    fontFace: "Arial", fontSize: 8.4, color: MUTED, margin: 0,
  });
  slide.addShape(SHAPES.line, { x: 0.34, y: 0.88, w: 12.6, h: 0, line: { color: LINE, width: 0.5 } });
}

function addOverviewSlide(pres) {
  const slide = pres.addSlide();
  addTitle(
    slide,
    "Seam-aware material QA candidates",
    "All rows use the same junction-collar geometry family; panels are PPTX-arranged white-background zoom strips."
  );
  slide.addText("v1 Trellis guide", { x: 2.02, y: 1.02, w: 3.0, h: 0.22, fontFace: "Arial", fontSize: 9, bold: true, color: MUTED, align: "center", margin: 0 });
  slide.addText("v2 low-contrast guide", { x: 5.62, y: 1.02, w: 3.0, h: 0.22, fontFace: "Arial", fontSize: 9, bold: true, color: MUTED, align: "center", margin: 0 });
  slide.addText("object-space PBR", { x: 9.22, y: 1.02, w: 3.0, h: 0.22, fontFace: "Arial", fontSize: 9, bold: true, color: MUTED, align: "center", margin: 0 });
  const startY = 1.32;
  const rowH = 1.58;
  const gapY = 0.22;
  for (let i = 0; i < ROWS.length; i += 1) {
    const row = ROWS[i];
    const y = startY + i * (rowH + gapY);
    slide.addText(row.family, { x: 0.34, y: y + 0.05, w: 1.35, h: 0.22, fontFace: "Arial", fontSize: 8.6, bold: true, color: INK, margin: 0, fit: "shrink" });
    slide.addText(row.claim, { x: 0.34, y: y + 0.35, w: 1.34, h: 0.82, fontFace: "Arial", fontSize: 5.9, color: MUTED, margin: 0.01, fit: "shrink" });
    addImage(slide, row.v1, 1.86, y, 3.35, rowH);
    addImage(slide, row.v2, 5.46, y, 3.35, rowH);
    addImage(slide, row.proc, 9.06, y, 3.35, rowH);
    slide.addShape(SHAPES.line, { x: 8.9, y, w: 0, h: rowH, line: { color: RED, width: 0.75 } });
  }
  slide.addText("Use as QA evidence first; paper inclusion requires manual/Keynote PDF export from this PPTX.", {
    x: 0.34, y: 6.96, w: 12.4, h: 0.22,
    fontFace: "Arial", fontSize: 7.5, color: MUTED, margin: 0,
  });
}

function addFamilySlides(pres) {
  for (const row of ROWS) {
    const slide = pres.addSlide();
    addTitle(slide, row.family, row.claim);
    slide.addText("v1 Trellis guide", { x: 0.55, y: 1.10, w: 3.7, h: 0.24, fontFace: "Arial", fontSize: 10, bold: true, color: MUTED, align: "center", margin: 0 });
    slide.addText("v2 low-contrast guide", { x: 4.82, y: 1.10, w: 3.7, h: 0.24, fontFace: "Arial", fontSize: 10, bold: true, color: MUTED, align: "center", margin: 0 });
    slide.addText("object-space procedural PBR", { x: 9.08, y: 1.10, w: 3.7, h: 0.24, fontFace: "Arial", fontSize: 10, bold: true, color: MUTED, align: "center", margin: 0 });
    addImage(slide, row.v1, 0.50, 1.44, 3.86, 4.56);
    addImage(slide, row.v2, 4.76, 1.44, 3.86, 4.56);
    addImage(slide, row.proc, 9.02, 1.44, 3.86, 4.56);
    slide.addText("Object-space material is a controlled rendering/materialization candidate, not a claim that Trellis UV texture export itself has no seam.", {
      x: 0.52, y: 6.25, w: 12.2, h: 0.26, fontFace: "Arial", fontSize: 8, color: MUTED, margin: 0,
    });
  }
}

async function main() {
  assertInputs();
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = "PS-RSLG";
  pres.subject = "PPTX-first seam-aware material QA";
  pres.title = "Seam-aware material QA candidates";
  SHAPES = pres.ShapeType;
  addOverviewSlide(pres);
  addFamilySlides(pres);
  await pres.writeFile({ fileName: OUT });
  const summary = {
    schema: "seam_aware_pbr_qa_pptx_20260511",
    pptx: OUT,
    pdf: "",
    rows: ROWS,
    workflow_contract: "PPTX-first figure candidate; export PDF from this deck before paper inclusion",
  };
  fs.writeFileSync(path.join(OUT_DIR, "summary.json"), JSON.stringify(summary, null, 2));
  console.log(JSON.stringify(summary, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
