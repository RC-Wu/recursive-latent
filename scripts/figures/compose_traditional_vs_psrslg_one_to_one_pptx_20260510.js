#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = "/Users/fanta/code/agent/Code/recursive_3d_generative_growth";
const TRAD = path.join(ROOT, "case_gallery_for_user_20260510_remote_matched_candidates/01_traditional_targets");
const OURS_V24 = path.join(ROOT, "visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510");
const OURS_V25 = path.join(ROOT, "visuals/strict_visual_matched_texture_V25_root_sc_refine_zoom_white_20260510");
const OUT_DIR = path.join(ROOT, "paper_siga/figures/traditional_vs_psrslg_one_to_one_pptx_20260510");
const MAIN_ONLY = process.env.MAIN_ONLY === "1";
const OUT_BASENAME = process.env.OUT_BASENAME || (MAIN_ONLY ? "traditional_vs_psrslg_one_to_one_main_20260510" : "traditional_vs_psrslg_one_to_one_20260510");
const OUT_PPTX = path.join(OUT_DIR, `${OUT_BASENAME}.pptx`);

const WHITE = "FFFFFF";
const INK = "1B1F23";
const MUTED = "5C6670";
const LINE = "D6DEE6";
const RED = "B94036";
const BLUE = "246EB9";
let SHAPES = null;

const ROWS = [
  {
    family: "DLA / frontier",
    target: "dla_coral_cluster_900",
    selected: "V24_dla_staghorn_frontier",
    tag: "cluster target -> staghorn frontier asset",
    traditional: path.join(TRAD, "strict_matched_traditional_targets_zoom_20260510__dla_coral_cluster_900__strict_matched_zoom_comparison.png"),
    ours: path.join(OURS_V24, "V24_dla_staghorn_frontier/strict_matched_zoom_comparison.png"),
    metric: "r0 comps 1, LCR 1.000; 3-seed stable",
    caveat: "asset-style frontier attachment; not a physical DLA/coral simulation",
  },
  {
    family: "IFS / lattice",
    target: "ifs_fractal_lattice_d4",
    selected: "V24_ifs_pyrite_lattice",
    tag: "fractal lattice -> pyrite copy bridges",
    traditional: path.join(TRAD, "strict_matched_traditional_targets_zoom_20260510__ifs_fractal_lattice_d4__strict_matched_zoom_comparison.png"),
    ours: path.join(OURS_V24, "V24_ifs_pyrite_lattice/strict_matched_zoom_comparison.png"),
    metric: "r1 connected; min r0 LCR 0.9997",
    caveat: "operator-admission evidence with tiny r0 islands; not strict equivariance",
  },
  {
    family: "L-system / root fan",
    target: "lsys_root_fan_d5",
    selected: "V25_root_smooth_D",
    tag: "branching root fan -> connected dense rootlets",
    traditional: path.join(TRAD, "strict_matched_traditional_targets_zoom_20260510__lsys_root_fan_d5__strict_matched_zoom_comparison.png"),
    ours: path.join(OURS_V25, "V25_root_smooth_D/strict_matched_zoom_comparison.png"),
    metric: "r0 comps 1, LCR 1.000",
    caveat: "post-GLB surface diagnostic; not watertight topology proof",
  },
  {
    family: "Space colonization / crown",
    target: "sc_tree_crown_260",
    selected: "V25_sc_tapered_B",
    tag: "attractor crown -> tapered textured crown asset",
    traditional: path.join(TRAD, "strict_matched_traditional_targets_zoom_20260510__sc_tree_crown_260__strict_matched_zoom_comparison.png"),
    ours: path.join(OURS_V25, "V25_sc_tapered_B/strict_matched_zoom_comparison.png"),
    metric: "r0 comps 1, LCR 1.000",
    caveat: "metric-stable candidate; visual natural-tree quality remains caveated",
  },
];

function assertInputs() {
  for (const row of ROWS) {
    for (const key of ["traditional", "ours"]) {
      if (!fs.existsSync(row[key])) {
        throw new Error(`Missing ${key} image for ${row.family}: ${row[key]}`);
      }
    }
  }
}

function addImageContain(slide, imagePath, x, y, w, h) {
  slide.addImage({
    path: imagePath,
    x,
    y,
    w,
    h,
    sizing: { type: "contain", x, y, w, h },
  });
  slide.addShape(SHAPES.rect, {
    x,
    y,
    w,
    h,
    fill: { color: WHITE, transparency: 100 },
    line: { color: LINE, width: 0.5 },
  });
}

function addHeader(slide) {
  slide.background = { color: WHITE };
  slide.addText("Strict traditional targets vs. PS-RSLG candidates", {
    x: 0.32,
    y: 0.18,
    w: 12.5,
    h: 0.32,
    fontFace: "Arial",
    fontSize: 18,
    bold: true,
    color: INK,
    margin: 0,
  });
  slide.addText("Each panel is a white-background camera-zoom strip: overview with callout, first zoom, second zoom.", {
    x: 0.32,
    y: 0.54,
    w: 12.0,
    h: 0.24,
    fontFace: "Arial",
    fontSize: 8.5,
    color: MUTED,
    margin: 0,
  });
  slide.addShape(SHAPES.line, {
    x: 0.32,
    y: 0.83,
    w: 12.65,
    h: 0,
    line: { color: LINE, width: 0.5 },
  });
}

function addFullFigureSlide(pres) {
  const slide = pres.addSlide();
  addHeader(slide);
  slide.addText("Traditional target", {
    x: 2.20,
    y: 0.95,
    w: 4.8,
    h: 0.24,
    fontFace: "Arial",
    fontSize: 10,
    bold: true,
    color: MUTED,
    align: "center",
    margin: 0,
  });
  slide.addText("Selected PS-RSLG candidate", {
    x: 7.45,
    y: 0.95,
    w: 4.8,
    h: 0.24,
    fontFace: "Arial",
    fontSize: 10,
    bold: true,
    color: MUTED,
    align: "center",
    margin: 0,
  });
  const labelX = 0.32;
  const tradX = 2.05;
  const oursX = 7.36;
  const imgW = 5.05;
  const imgH = 1.06;
  const startY = 1.26;
  const rowGap = 0.38;
  for (let i = 0; i < ROWS.length; i += 1) {
    const row = ROWS[i];
    const y = startY + i * (imgH + rowGap);
    slide.addText(row.family, {
      x: labelX,
      y: y + 0.05,
      w: 1.52,
      h: 0.22,
      fontFace: "Arial",
      fontSize: 9.0,
      bold: true,
      color: INK,
      margin: 0,
      fit: "shrink",
    });
    slide.addText(row.tag, {
      x: labelX,
      y: y + 0.32,
      w: 1.48,
      h: 0.24,
      fontFace: "Arial",
      fontSize: 6.4,
      color: MUTED,
      margin: 0,
      fit: "shrink",
    });
    slide.addText(row.metric, {
      x: labelX,
      y: y + 0.77,
      w: 1.48,
      h: 0.22,
      fontFace: "Arial",
      fontSize: 6.0,
      color: MUTED,
      margin: 0,
      fit: "shrink",
    });
    addImageContain(slide, row.traditional, tradX, y, imgW, imgH);
    addImageContain(slide, row.ours, oursX, y, imgW, imgH);
    slide.addShape(SHAPES.line, {
      x: 7.22,
      y,
      w: 0,
      h: imgH,
      line: { color: RED, width: 0.8 },
    });
    if (i < ROWS.length - 1) {
      slide.addShape(SHAPES.line, {
        x: 0.32,
        y: y + imgH + rowGap * 0.52,
        w: 12.65,
        h: 0,
        line: { color: LINE, width: 0.35 },
      });
    }
  }
}

function addPerFamilySlides(pres) {
  for (const row of ROWS) {
    const slide = pres.addSlide();
    slide.background = { color: WHITE };
    slide.addText(row.family, {
      x: 0.40,
      y: 0.24,
      w: 5.4,
      h: 0.35,
      fontFace: "Arial",
      fontSize: 19,
      bold: true,
      color: INK,
      margin: 0,
    });
    slide.addText(row.tag, {
      x: 0.42,
      y: 0.63,
      w: 6.6,
      h: 0.24,
      fontFace: "Arial",
      fontSize: 8.5,
      color: MUTED,
      margin: 0,
    });
    slide.addShape(SHAPES.line, {
      x: 0.40,
      y: 0.95,
      w: 12.5,
      h: 0,
      line: { color: LINE, width: 0.5 },
    });
    slide.addText("Traditional target", {
      x: 0.58,
      y: 1.08,
      w: 5.8,
      h: 0.24,
      fontFace: "Arial",
      fontSize: 10,
      bold: true,
      color: MUTED,
      align: "center",
      margin: 0,
    });
    slide.addText("Selected PS-RSLG", {
      x: 6.95,
      y: 1.08,
      w: 5.8,
      h: 0.24,
      fontFace: "Arial",
      fontSize: 10,
      bold: true,
      color: MUTED,
      align: "center",
      margin: 0,
    });
    addImageContain(slide, row.traditional, 0.58, 1.42, 5.8, 2.05);
    addImageContain(slide, row.ours, 6.95, 1.42, 5.8, 2.05);
    slide.addShape(SHAPES.line, {
      x: 6.66,
      y: 1.36,
      w: 0,
      h: 2.20,
      line: { color: RED, width: 1.0 },
    });
    slide.addText(row.metric, {
      x: 0.58,
      y: 3.84,
      w: 5.8,
      h: 0.26,
      fontFace: "Arial",
      fontSize: 8.5,
      bold: true,
      color: BLUE,
      margin: 0,
    });
    slide.addText(row.caveat, {
      x: 6.95,
      y: 3.84,
      w: 5.8,
      h: 0.34,
      fontFace: "Arial",
      fontSize: 8.0,
      color: MUTED,
      margin: 0,
      fit: "shrink",
    });
    slide.addText(`target: ${row.target}   selected: ${row.selected}`, {
      x: 0.58,
      y: 4.28,
      w: 12.2,
      h: 0.22,
      fontFace: "Arial",
      fontSize: 7.0,
      color: MUTED,
      margin: 0,
    });
  }
}

async function main() {
  assertInputs();
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const pres = new pptxgen();
  SHAPES = pres.ShapeType;
  pres.layout = "LAYOUT_WIDE";
  pres.author = "PS-RSLG";
  pres.subject = "Traditional baseline versus PS-RSLG one-to-one visual evidence";
  pres.title = "Traditional vs PS-RSLG one-to-one";
  pres.company = "Recursive 3D Generative Growth";
  pres.lang = "en-US";
  addFullFigureSlide(pres);
  if (!MAIN_ONLY) {
    addPerFamilySlides(pres);
  }
  await pres.writeFile({ fileName: OUT_PPTX });
  console.log(OUT_PPTX);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
