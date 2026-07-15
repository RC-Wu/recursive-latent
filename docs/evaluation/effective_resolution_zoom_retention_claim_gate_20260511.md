# Effective-Resolution / Zoom-Retention Claim Gate

Date: 2026-05-11 CST

## Current Status

This lane is not empty. It has a selected-final-only proxy table and several
matched zoom render packs, but it is not yet a strong quantitative proof.

Core metric script:

- `assets/effective_resolution_metrics_20260510.py`

Current metric outputs:

- `results/effective_resolution_metrics_20260510/effective_resolution_metrics.csv`
- `results/effective_resolution_metrics_20260510/effective_resolution_comparisons.csv`
- `paper_siga/drafts/effective_resolution_status_table_20260510.tex`
- `results/publication_ablation_metrics_20260510/effective_resolution_schema.csv`

Important zoom render packs already available:

- `visuals/gen3d_baseline_matched_white_renders_20260510_flatwhite/`
- `visuals/gen3d_baseline_texture_fair_matched_20260510_flatwhite/`
- `visuals/gen3d_baseline_geometry_control_20260510_flatwhite/`
- `visuals/publication_repair_20260510f_controlled_zoom_1200/`

## What The Current Numbers Say

The current comparison CSV contains two selected groups:

| Group | One-shot | Recursive | Local scale improvement | Terminal detail ratio | One faces | Recursive faces |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| crystal/coral | `dla_cluster_baseline` | `pyrite_lattice_depth_stage_04...` | 4.09x | 2.46x | 10,800 | 482,348 |
| tree/vine | `sc_tree_canopy_baseline` | `ours_vine_stage5` | 3.79x | 0.54x | 31,700 | 455,964 |

Definitions used by the current script:

- local feature scale proxy: `bbox_diag / sqrt(face_count)`;
- terminal detail count proxy: occupied voxels when available, otherwise
  vertices/faces;
- zoom retention proxy: `connectivity_lcr * (1 + box_count_dimension_proxy / 3)`;
- full-object high-resolution blow-up estimate: one-shot faces scaled by the
  local-scale improvement squared and lower-bounded by recursive faces.

## Why It Is Still A Proxy

The current evidence should be described as selected-case accounting plus
matched zoom visualization. It is not a formal effective-resolution proof for
the following reasons:

1. The local feature scale is a triangle-density estimate, not a measured
   semantic minimum feature size.
2. The zoom retention score combines connectivity and box-count complexity; it
   does not directly match the same physical/semantic patch before and after
   zooming.
3. Current comparisons are not strictly same-root, same-condition, same-budget
   rows.
4. The tree/vine row has finer local scale but lower terminal detail ratio
   (`0.54x`), so it cannot support a universal detail-superiority claim.
5. The rows are selected examples, not a multi-case/multi-seed distribution.
6. The high-resolution blow-up number is an estimate, not an actually generated
   full-object high-resolution baseline.

## Paper-Safe Wording

Allowed:

- "We report selected-case proxy metrics for local feature scale and terminal
  detail, alongside matched camera zoom panels."
- "The recursive assets allocate geometry locally and can expose finer local
  feature scale in selected cases."
- "The full-object high-resolution cost is estimated from the observed local
  feature-scale ratio."

Not allowed yet:

- "Our method proves higher effective resolution."
- "Zoom retention is quantitatively superior across cases."
- "The recursive method preserves more terminal detail universally."
- "The blow-up estimate is an actual full-resolution baseline result."

## Minimum Closure Plan

To upgrade this lane from proxy to stronger evidence:

1. Use the existing matched baseline zoom packs to build a selected matched
   panel: Trellis2 one-shot, Trellis2 latent-copy, mesh-space copy, ours.
2. For each case, record the exact same physical target/zoom camera where
   possible, or explicitly mark the target as method-specific if not possible.
3. Add an image/geometry patch metric for each zoom panel:
   foreground occupancy, edge/detail density, connected foreground components,
   and optional rendered silhouette entropy.
4. Pair these image metrics with mesh metrics:
   faces, vertices, GLB size, occupancy LCR, box-count proxy, and local feature
   scale.
5. Report a small table as "selected zoom accounting" unless a larger case pool
   and multi-seed distribution is produced.

This would be good enough for a cautious main-paper side table or appendix
figure. A full quantitative proof still requires same-budget generation and a
larger matched case pool.
