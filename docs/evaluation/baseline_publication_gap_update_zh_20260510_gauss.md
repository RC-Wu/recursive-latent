# Baseline Publication Gap Update - Gauss - 2026-05-10

范围：baseline/evaluation 侧窄任务。本文只检查本地已有计划、候选文档、V23 两个 seed metrics、selected-8 manifest/render 状态，以及传统 baseline 目录 `case_gallery_for_user_20260509/06_baselines_metrics_ablation`。未启动远端任务，未修改 `paper_siga/main.tex`，未改已有脚本。

## 1. 输入材料状态

已读材料：

- `docs/plans/recursive_3d_growth_publication_ralph_loop_zh_20260510.md`
- `docs/evaluation/baseline_candidate_selection_zh_20260510.md`
- V23 first seed metrics: `results/strict_visual_matched_texture_V23_all_family_20260510_remote/surface_metrics_occ64.csv`
- V23 second seed metrics: `results/strict_visual_matched_texture_V23_all_family_seed20260511_20260510_remote/surface_metrics_occ64.csv`
- first-seed selected-8 manifest: `results/strict_visual_matched_texture_V23_all_family_20260510_remote/V23_zoom_manifest_selected8_glb_localplan.json`
- second-seed selected-8 manifest: `results/strict_visual_matched_texture_V23_all_family_seed20260511_20260510_remote/V23_zoom_manifest_selected8_glb_localplan.json`
- rendered selected-8 plan: `visuals/strict_visual_matched_texture_V23_all_family_selected8_zoom_20260510/matched_camera_zoom_plan.json`
- traditional baseline directory requested by user: `case_gallery_for_user_20260509/06_baselines_metrics_ablation`

Important directory finding:

- `case_gallery_for_user_20260509/06_baselines_metrics_ablation` exists but currently contains 0 files. It cannot be used as completed baseline/ablation evidence.
- `visuals/strict_visual_matched_texture_V23_all_family_selected8_zoom_20260510` currently has only two rendered case folders with `overview_raw.png`, `zoom_01.png`, `zoom_02.png`: `V23_lsys_pine...` and `V23_lsys_root_fan_dense...`.
- The selected-8 render manifest lists 8 cases, but 6 of them currently have missing PNG renders in that output directory. No `strict_matched_zoom_comparison.png` was found for any of the 8 manifest entries.

## 2. V23 two-seed metric status

V23 has two post-GLB surface metrics seeds and is currently the strongest baseline candidate pool. Connectivity is strong across all four families, but publication readiness still depends on visual QA and family-specific metrics.

| candidate | seed1 comp/LCR | seed2 comp/LCR | min LCR | mean occupied | current status |
|---|---:|---:|---:|---:|---|
| `V23_lsys_pine_canopy_d5_multi_root_smooth_needles` | 2 / 0.999703 | 1 / 1.000000 | 0.999703 | 3464.0 | main-text candidate, rendered PNG exists |
| `V23_lsys_root_fan_d5_multi_root_smooth_rootlets` | 2 / 0.999654 | 3 / 0.998854 | 0.998854 | 2755.0 | candidate, no selected-8 render in current selected manifest |
| `V23_lsys_root_fan_d5_dense_rootlets_variant` | 1 / 1.000000 | 5 / 0.997882 | 0.997882 | 2963.0 | appendix/control candidate, rendered PNG exists |
| `V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils` | 2 / 0.999245 | 3 / 0.998551 | 0.998551 | 1352.5 | appendix only until visual QA |
| `V23_sc_tree_crown_260_attractor_leaf_shell` | 1 / 1.000000 | 7 / 0.999372 | 0.999372 | 12734.5 | main-text candidate, selected-8 PNG missing |
| `V23_sc_root_network_260_attractor_rootlets` | 6 / 0.999549 | 8 / 0.999319 | 0.999319 | 15838.5 | main/appendix candidate, needs rootlet orphan QA |
| `V23_sc_tree_crown_260_sparse_kill_variant` | 3 / 0.999841 | 3 / 0.999848 | 0.999841 | 12855.5 | parameter-control candidate |
| `V23_sc_bush_shell_220_attractor_leaf_shell` | 3 / 0.999801 | 1 / 1.000000 | 0.999801 | 15546.5 | appendix unless shell-vs-blob visual strong |
| `V23_dla_coral_cluster_900_staghorn_frontier` | 1 / 1.000000 | 1 / 1.000000 | 1.000000 | 5610.0 | main-text candidate, selected-8 PNG missing |
| `V23_dla_frontier_sheet_700_open_boundary` | 1 / 1.000000 | 1 / 1.000000 | 1.000000 | 1948.0 | secondary main/appendix candidate, selected-8 PNG missing |
| `V23_dla_crystal_cluster_520_faceted_frontier` | 1 / 1.000000 | 1 / 1.000000 | 1.000000 | 2939.0 | appendix candidate, selected-8 PNG missing |
| `V23_dla_coral_cluster_900_lace_porosity_variant` | 6 / 0.999305 | 3 / 0.999630 | 0.999305 | 6296.0 | backup, needs porosity visual QA |
| `V23_ifs_radial_ornament_o8_d4_orbit_spokes` | 1 / 1.000000 | 2 / 0.999888 | 0.999888 | 8941.5 | main-text candidate, selected-8 PNG missing |
| `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges` | 4 / 0.999739 | 4 / 0.999739 | 0.999739 | 11480.5 | main/appendix candidate, selected-8 PNG missing |
| `V23_ifs_fractal_tree_d5_branch_copy` | 4 / 0.999228 | 2 / 0.999734 | 0.999228 | 3820.5 | appendix/needs copy hierarchy QA |
| `V23_ifs_branch_ornament_d5_contact_facets` | 2 / 0.999733 | 2 / 0.999739 | 0.999733 | 3787.5 | appendix backup |

## 3. Selected-8 manifest/render gap

First-seed selected-8 manifest includes:

1. `V23_lsys_pine_canopy_d5_multi_root_smooth_needles`
2. `V23_lsys_root_fan_d5_dense_rootlets_variant`
3. `V23_sc_tree_crown_260_attractor_leaf_shell`
4. `V23_dla_coral_cluster_900_staghorn_frontier`
5. `V23_dla_frontier_sheet_700_open_boundary`
6. `V23_dla_crystal_cluster_520_faceted_frontier`
7. `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges`
8. `V23_ifs_radial_ornament_o8_d4_orbit_spokes`

Current rendered PNG availability in `visuals/strict_visual_matched_texture_V23_all_family_selected8_zoom_20260510`:

| selected-8 case | overview | zoom1 | zoom2 | comparison |
|---|---|---|---|---|
| `V23_lsys_pine_canopy_d5_multi_root_smooth_needles` | yes | yes | yes | missing |
| `V23_lsys_root_fan_d5_dense_rootlets_variant` | yes | yes | yes | missing |
| `V23_sc_tree_crown_260_attractor_leaf_shell` | missing | missing | missing | missing |
| `V23_dla_coral_cluster_900_staghorn_frontier` | missing | missing | missing | missing |
| `V23_dla_frontier_sheet_700_open_boundary` | missing | missing | missing | missing |
| `V23_dla_crystal_cluster_520_faceted_frontier` | missing | missing | missing | missing |
| `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges` | missing | missing | missing | missing |
| `V23_ifs_radial_ornament_o8_d4_orbit_spokes` | missing | missing | missing | missing |

Interpretation: the selected-8 evidence package is not publication-ready. It has metrics and GLB paths, but the white-background multi-level visual set is only partially rendered and lacks comparison/contact sheets.

## 4. Main-text candidate readiness

### 4.1 Already plausible as main-text candidates after visual QA

These have two-seed post-GLB connectivity strong enough to remain in the main candidate pool:

- L-system: `V23_lsys_pine_canopy_d5_multi_root_smooth_needles`
  - Already has selected-8 overview/zoom PNGs.
  - Need human QA for visible depth-5 branching, whorl/needle attachment, no texture-only fake terminals.
- Space colonization: `V23_sc_tree_crown_260_attractor_leaf_shell`
  - Strong metrics; selected-8 PNGs missing.
  - Need attractor coverage/path-to-root metrics and leaf-shell attachment QA.
- DLA/frontier: `V23_dla_coral_cluster_900_staghorn_frontier`
  - Strongest DLA candidate by connectivity; selected-8 PNGs missing.
  - Need frontier/tip survival, porosity/neck, blockiness, and no physical-DLA overclaim.
- IFS/transform: `V23_ifs_radial_ornament_o8_d4_orbit_spokes`
  - Strongest IFS metric row; selected-8 PNGs missing.
  - Need order-8 orbit/symmetry/contact bridge QA.

### 4.2 Secondary candidates for main text if page budget allows

- L-system: `V23_lsys_root_fan_d5_multi_root_smooth_rootlets` or `V23_lsys_root_fan_d5_dense_rootlets_variant`
  - The smooth-rootlets row is semantically cleaner but not in current first-seed selected-8 manifest.
  - The dense-rootlets row has selected-8 PNGs and first-seed perfect LCR, but second seed fragments more.
- Space colonization: `V23_sc_root_network_260_attractor_rootlets`
  - Strong root-network strict target, but many small components across both seeds. Needs root-attached ratio and orphan mass.
- DLA/frontier: `V23_dla_frontier_sheet_700_open_boundary`
  - Metrics perfect across seeds; useful stress case if visual shows open boundary rather than smooth plate.
- IFS/transform: `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges`
  - Strong transform-copy/lattice admission evidence, but persistent small fragments and selected-8 PNGs missing.

### 4.3 Appendix/status candidates

- L-system: `V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils`
- Space colonization: `V23_sc_tree_crown_260_sparse_kill_variant`, `V23_sc_bush_shell_220_attractor_leaf_shell`
- DLA/frontier: `V23_dla_crystal_cluster_520_faceted_frontier`, `V23_dla_coral_cluster_900_lace_porosity_variant`
- IFS/transform: `V23_ifs_fractal_tree_d5_branch_copy`, `V23_ifs_branch_ornament_d5_contact_facets`

## 5. What still needs remote multi seed / root / grammar guide

The current V23 pair is a good screen, not a final publication selection budget. The following still need new remote generation if they are to support strong claims:

### L-system

- Need: at least 2 root/source variants and 3-4 total seeds for `pine_canopy` and `root_fan`.
- Guide/root need: clean pine/root-fan PBR guides with visible terminal hierarchy, not just dense texture.
- Grammar guide need: metadata should explicitly carry `depth=5`, branch/rootlet rule, terminal/tip survival target.
- Why: current metrics prove connectivity, not rule hierarchy or terminal attachment.

### Space colonization

- Need: multi root/attractor variants for tree crown and root network.
- Guide/root need: one crown guide and one root guide with clear attractor envelope; avoid branch-grammar-looking outputs.
- Grammar guide need: record attractor count, influence radius, kill radius, step size, alive attractors.
- Why: current metrics do not prove attractor-conditioned growth or coverage.

### DLA/frontier

- Need: more seeds for staghorn/frontier sheet plus a stricter porosity/blockiness sweep.
- Guide/root need: coral/frontier guides that preserve accretive tips and porous necks without becoming smooth plates.
- Grammar guide need: frontier event count, attachment bridge budget, tip/neck/porosity targets.
- Why: current LCR is excellent, but DLA/frontier claim depends on frontier survival, porosity, and avoiding smooth generic coral.

### IFS/transform

- Need: radial and lattice multi-seed plus at least one separate branch-tree/branch-ornament rerun if IFS tree is desired.
- Guide/root need: radial guide with clear order-8 spokes; lattice guide with obvious copy contacts; branch tree guide if claiming IFS-tree.
- Grammar guide need: transform list, depth, copy count per node, orbit-contact bridge rules.
- Why: current metrics do not prove orbit consistency or transform-copy hierarchy; pyrite/lattice cannot substitute for IFS tree.

## 6. Metric presentation plan by family

### Common table for all families

Use a compact candidate screening table:

- `case_id`
- `family`
- `seed`
- `components_r0/r1/r2`
- `LCR_r0/r1/r2`
- `occupied`
- `vertices/faces`
- `GLB import status`
- `visual QA verdict`
- `selection tier`: main / appendix / reject / rerun

### L-system metrics

Show as one table or grouped columns:

- visible recursive depth
- branch/root path-to-base rate
- terminal/tip survival
- needle/rootlet attachment ratio
- branch angle/length distribution summary
- surface connectivity LCR

Recommended chart: per-case rows with two seed columns for LCR plus a small family-specific block for attachment/depth.

### Space colonization metrics

Show:

- attractor coverage
- nearest-attractor distance distribution
- alive/killed attractor counts
- terminal path-to-root
- root/leaf orphan mass
- LCR and component count

Recommended chart: `tree crown` and `root network` as two primary rows, with coverage/path-to-root next to connectivity.

### DLA/frontier metrics

Show:

- frontier survival
- tip count / neck count / porosity proxy
- bridge cost / attachment success
- blockiness score
- open-boundary continuity for sheet case
- LCR and components

Recommended chart: separate `coral cluster` and `frontier sheet`; keep physical-DLA wording out of labels.

### IFS/transform metrics

Show:

- orbit error
- symmetry IoU
- copy-contact survival
- bridge survival
- self-similarity or transform consistency proxy
- LCR and components

Recommended chart: radial ornament and lattice as positive admission cases; branch-tree/branch-ornament as appendix or boundary unless rerun succeeds.

## 7. Next generation/render checklist

No remote jobs were started in this pass. Suggested next actions for the main thread or a generation worker:

1. Finish local V23 selected-8 rendering: generate missing PNGs and `strict_matched_zoom_comparison.png` for all 8 manifest cases, preferably with contact sheet.
2. Populate or replace the empty `case_gallery_for_user_20260509/06_baselines_metrics_ablation` evidence path. If the canonical gallery moved, add a README or index pointing to the actual baseline/ablation locations.
3. Compute family-specific metrics for the eight V23 primary/secondary cases:
   - L-system attachment/depth.
   - SC attractor coverage/path-to-root.
   - DLA frontier/porosity/blockiness.
   - IFS orbit/symmetry/contact.
4. Run a remote multi-seed/root/guide follow-up only after visual QA decides which of the V23 cases are worth expanding:
   - L-system: pine + root fan.
   - SC: tree crown + root network.
   - DLA: staghorn + frontier sheet.
   - IFS: radial + lattice.
5. Keep V5c as appendix/history only unless a case has uniquely better visual readability than V23 after side-by-side QA.

## 8. Bottom line

Current V23 evidence is promising but not yet publication-closed. The metric side supports a clear main-candidate pool, especially pine, SC tree crown, staghorn frontier, and radial ornament. The blocking gaps are visual package completion, family-specific metrics, and a real baseline/ablation gallery path. The next useful work should be local render/QA and metric aggregation, not another unscreened long remote batch.
