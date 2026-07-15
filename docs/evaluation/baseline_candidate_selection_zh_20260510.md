# Baseline / Candidate Selection 汇总 2026-05-10

范围：最终 baseline/candidate selection 汇总线。本文只汇总本地已有文件，不修改 `paper_siga`，不删除文件，不使用 SSH。目标是为主文 figure/table 候选提供一个可执行的选择清单。

## 1. 可用 metrics 与 contact sheet

### 1.1 V23 all-family first seed

- surface metrics: `results/strict_visual_matched_texture_V23_all_family_20260510_remote/surface_metrics_occ64.csv`
- inputs metrics: `results/strict_visual_matched_texture_V23_all_family_20260510_remote/inputs/initial_metrics.csv`
- textured GLB root: `visuals/strict_visual_matched_texture_V23_all_family_20260510`
- zoom plan only: `visuals/strict_visual_matched_texture_V23_all_family_zoom_20260510/matched_camera_zoom_plan.json`
- contact sheet: not found; only zoom plan exists.

Post-GLB surface metrics summary:

| family | candidate | comp r0 | LCR r0 | note |
|---|---|---:|---:|---|
| L-system | `V23_lsys_pine_canopy_d5_multi_root_smooth_needles` | 2 | 0.999703 | strong connectivity; needs visual QA for trunk/needle hierarchy |
| L-system | `V23_lsys_root_fan_d5_multi_root_smooth_rootlets` | 2 | 0.999654 | strong; compare with dense-rootlet variant |
| L-system | `V23_lsys_root_fan_d5_dense_rootlets_variant` | 1 | 1.000000 | best L-system connectivity in first seed |
| L-system | `V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils` | 2 | 0.999245 | acceptable metrics; higher visual risk |
| Space colonization | `V23_sc_tree_crown_260_attractor_leaf_shell` | 1 | 1.000000 | strongest SC first-seed connectivity |
| Space colonization | `V23_sc_root_network_260_attractor_rootlets` | 6 | 0.999549 | good LCR; orphan/rootlet QA needed |
| Space colonization | `V23_sc_bush_shell_220_attractor_leaf_shell` | 3 | 0.999801 | appendix/backup unless shell-vs-blob QA passes |
| Space colonization | `V23_sc_tree_crown_260_sparse_kill_variant` | 3 | 0.999841 | parameter-control candidate |
| DLA/frontier | `V23_dla_coral_cluster_900_staghorn_frontier` | 1 | 1.000000 | best DLA main candidate by metrics |
| DLA/frontier | `V23_dla_frontier_sheet_700_open_boundary` | 1 | 1.000000 | good sheet stress case; needs open-boundary QA |
| DLA/frontier | `V23_dla_crystal_cluster_520_faceted_frontier` | 1 | 1.000000 | appendix unless facet/crystal visual strong |
| DLA/frontier | `V23_dla_coral_cluster_900_lace_porosity_variant` | 6 | 0.999305 | visually useful only if lace/porosity survives |
| IFS/transform | `V23_ifs_radial_ornament_o8_d4_orbit_spokes` | 1 | 1.000000 | strongest IFS first-seed metric row |
| IFS/transform | `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges` | 4 | 0.999739 | good pyrite/lattice row; needs orbit/contact QA |
| IFS/transform | `V23_ifs_fractal_tree_d5_branch_copy` | 4 | 0.999228 | appendix/needs visual QA |
| IFS/transform | `V23_ifs_branch_ornament_d5_contact_facets` | 2 | 0.999733 | appendix/backup ornament row |

### 1.2 V23 all-family second seed

- surface metrics: `results/strict_visual_matched_texture_V23_all_family_seed20260511_20260510_remote/surface_metrics_occ64.csv`
- inputs metrics: `results/strict_visual_matched_texture_V23_all_family_seed20260511_20260510_remote/inputs/initial_metrics.csv`
- textured GLB root: `visuals/strict_visual_matched_texture_V23_all_family_seed20260511_20260510`
- selected8 zoom plan only: `visuals/strict_visual_matched_texture_V23_all_family_selected8_zoom_20260510/matched_camera_zoom_plan.json`
- contact sheet: not found; only zoom plan exists.

Second-seed confirmation:

| family | candidate | comp r0 | LCR r0 | note |
|---|---|---:|---:|---|
| L-system | `V23_lsys_pine_canopy_d5_multi_root_smooth_needles` | 1 | 1.000000 | robust main candidate |
| L-system | `V23_lsys_root_fan_d5_dense_rootlets_variant` | 5 | 0.997882 | still high LCR but more fragments |
| L-system | `V23_lsys_root_fan_d5_multi_root_smooth_rootlets` | 3 | 0.998854 | acceptable; needs rootlet attachment QA |
| L-system | `V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils` | 3 | 0.998551 | weak main candidate; appendix only unless visual excellent |
| Space colonization | `V23_sc_bush_shell_220_attractor_leaf_shell` | 1 | 1.000000 | robust but main priority lower |
| Space colonization | `V23_sc_tree_crown_260_sparse_kill_variant` | 3 | 0.999848 | robust parameter-control row |
| Space colonization | `V23_sc_root_network_260_attractor_rootlets` | 8 | 0.999319 | good LCR; many small fragments require QA |
| Space colonization | `V23_sc_tree_crown_260_attractor_leaf_shell` | 7 | 0.999372 | good LCR; leaf shell orphan QA required |
| DLA/frontier | `V23_dla_coral_cluster_900_staghorn_frontier` | 1 | 1.000000 | robust across two seeds |
| DLA/frontier | `V23_dla_frontier_sheet_700_open_boundary` | 1 | 1.000000 | robust across two seeds |
| DLA/frontier | `V23_dla_crystal_cluster_520_faceted_frontier` | 1 | 1.000000 | robust metrics, visual/facet QA pending |
| DLA/frontier | `V23_dla_coral_cluster_900_lace_porosity_variant` | 3 | 0.999630 | acceptable backup |
| IFS/transform | `V23_ifs_radial_ornament_o8_d4_orbit_spokes` | 2 | 0.999888 | robust main candidate |
| IFS/transform | `V23_ifs_fractal_tree_d5_branch_copy` | 2 | 0.999734 | improved vs first seed; still needs copy hierarchy QA |
| IFS/transform | `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges` | 4 | 0.999739 | stable LCR, persistent small fragments |
| IFS/transform | `V23_ifs_branch_ornament_d5_contact_facets` | 2 | 0.999739 | stable appendix/backup |

### 1.3 V5c detail naturalized

- first seed dryrun metrics: `results/strict_visual_matched_cases_v5c_detail_naturalized_20260510_dryrun/initial_metrics.csv`
- second seed dryrun metrics: `results/strict_visual_matched_cases_v5c_detail_naturalized_seed20265110_20260510_dryrun/initial_metrics.csv`
- second seed contact sheet: `visuals/strict_visual_matched_texture_v5c_detail_seed20265110_zoom_20260510/strict_visual_matched_texture_v5c_detail_seed20265110_contact_sheet_20260510.png`

V5c is useful as historical/detail-naturalized reference, but its dryrun mesh-component metrics are much weaker than V23 post-GLB metrics. Best V5c rows are `sc_root_network` and `sc_tree_crown`; weakest are `lsys_climbing_vine` and DLA/frontier sheet. Do not promote V5c to main text over V23 unless visual QA shows a uniquely clear detail example.

| candidate | seed 1 comp | seed 1 LCR | seed 2 comp | seed 2 LCR | selection |
|---|---:|---:|---:|---:|---|
| `v5c_sc_root_network_260_welded_root_spurs` | 123 | 0.966669 | 133 | 0.974772 | appendix/reference |
| `v5c_sc_tree_crown_260_welded_branch_leaf_shell` | 125 | 0.956159 | 116 | 0.954594 | appendix/reference |
| `v5c_lsys_root_fan_d5_welded_hair_hierarchy` | 121 | 0.899683 | 112 | 0.918703 | appendix only |
| `v5c_ifs_radial_ornament_o8_d4_welded_ring_spokes` | 60 | 0.893048 | 53 | 0.931016 | appendix only if contact sheet is visually strong |
| `v5c_lsys_pine_canopy_d5_welded_whorl_needles` | 139 | 0.870181 | 132 | 0.869717 |淘汰主文 |
| `v5c_dla_coral_cluster_900_welded_tube_frontier` | 227 | 0.842780 | 234 | 0.849050 |淘汰主文 |
| `v5c_dla_frontier_sheet_700_welded_boundary_reef` | 240 | 0.766804 | 249 | 0.619484 |淘汰主文 |
| `v5c_lsys_climbing_vine_d6_welded_leaf_tendrils` | 67 | 0.084763 | 64 | 0.139980 |淘汰 |

### 1.4 Masked naturalization ablation

- metrics: `results/masked_naturalization_ablation_20260510/evaluation_current/metrics.csv`
- paper short table: `results/masked_naturalization_ablation_20260510/evaluation_current/paper_table_masked_naturalization_ablation_20260510.csv`
- protocol means: `results/masked_naturalization_ablation_20260510/evaluation_current/protocol_summary_masked_naturalization_ablation_20260510.csv`
- summary: `results/masked_naturalization_ablation_20260510/evaluation_current/masked_naturalization_ablation_summary_zh_20260510.md`
- contact sheet: `visuals/masked_naturalization_ablation_zoom_20260510/masked_naturalization_ablation_contact_sheet_20260510.png`

Main claim support: per-depth masked local naturalization is the recommended variant for all 3 representative tasks.

| task | family | recommended variant | score | comp | LCR | locality | silhouette |
|---|---|---|---:|---:|---:|---:|---:|
| `botanical_root` | botanical/root | `per_depth_masked_naturalization` | 0.875703 | 1 | 1.000000 | 0.923912 | 0.913689 |
| `coral_frontier` | coral/frontier | `per_depth_masked_naturalization` | 0.869856 | 1 | 1.000000 | 0.925879 | 0.904730 |
| `ifs_crystal` | IFS/crystal | `per_depth_masked_naturalization` | 0.885595 | 1 | 1.000000 | 0.940559 | 0.925961 |

Protocol mean scores: rule-only 0.4414, final-only 0.7519, per-depth/no-N 0.7854, per-depth/weak 0.8462, per-depth/global-N 0.8180, per-depth/masked local-N 0.8771. Use this as an ablation table, not as a substitute for family-specific baseline selection.

## 2. Family candidate ranking

### 2.1 L-system

1. Main text candidate: `V23_lsys_pine_canopy_d5_multi_root_smooth_needles`.
   - Reason: robust across two V23 seeds; first seed LCR 0.999703, second seed LCR 1.0.
   - Needs QA: visible depth-5 hierarchy, trunk/whorl/needle attachment, no leaf/noise hallucination.

2. Main text or appendix candidate: `V23_lsys_root_fan_d5_multi_root_smooth_rootlets`.
   - Reason: strong strict root-fan mapping; first seed LCR 0.999654, second seed LCR 0.998854.
   - Needs QA: rootlet attachment ratio, root base/junction/terminal zoom, compare against dense-rootlet variant.

3. Appendix candidate: `V23_lsys_root_fan_d5_dense_rootlets_variant`.
   - Reason: first seed perfect LCR, second seed still high but more fragmented.
   - Use as parameter-control appendix row if dense terminal structure is visually readable.

4. Appendix or淘汰: `V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils`.
   - Reason: metrics acceptable but consistently weaker than pine/root fan and known visual risk for vine/tendril strict mapping.
   - Main text only if manual QA shows clear curl, leaves, tendrils, and attachment.

淘汰主文：V5c L-system rows. Their mesh component counts are high and LCR is below V23, especially `v5c_lsys_climbing_vine`.

### 2.2 Space colonization

1. Main text candidate: `V23_sc_tree_crown_260_attractor_leaf_shell`.
   - Reason: first seed comp=1/LCR=1.0; second seed LCR remains 0.999372.
   - Needs QA: attractor coverage, terminal path-to-root, leaf shell attached rather than blob/shell artifact.

2. Main text candidate: `V23_sc_root_network_260_attractor_rootlets`.
   - Reason: strong root-network strict task; both seeds LCR > 0.999.
   - Needs QA: rootlet orphan mass, attractor coverage, path-to-root, root fan vs SC root distinction.

3. Appendix/control candidate: `V23_sc_tree_crown_260_sparse_kill_variant`.
   - Reason: robust LCR across seeds; useful parameter-control evidence.
   - Needs QA: sparse-kill visibly changes crown density/envelope without destroying attachment.

4. Appendix backup: `V23_sc_bush_shell_220_attractor_leaf_shell`.
   - Reason: second seed comp=1/LCR=1.0, but main claim is weaker unless shell-vs-blob QA is very good.

V5c SC rows can stay appendix/reference only; they are useful for continuity with earlier batches but not stronger than V23.

### 2.3 DLA / frontier

1. Main text candidate: `V23_dla_coral_cluster_900_staghorn_frontier`.
   - Reason: robust comp=1/LCR=1.0 in both V23 seeds.
   - Needs QA: frontier/tip survival, porosity/neck count, blockiness, avoid overclaiming physical DLA or real coral simulation.

2. Main text or appendix candidate: `V23_dla_frontier_sheet_700_open_boundary`.
   - Reason: comp=1/LCR=1.0 across seeds; good stress case for open boundary/frontier sheet.
   - Needs QA: open boundary continuity, membrane is not just a smooth plate, floating sheet/orphan mass.

3. Appendix candidate: `V23_dla_crystal_cluster_520_faceted_frontier`.
   - Reason: perfect connectivity metrics; good for frontier/crystal boundary evidence.
   - Needs QA: facet/ridge readability, crystal-like structure rather than ornament/rod.

4. Appendix/backup: `V23_dla_coral_cluster_900_lace_porosity_variant`.
   - Reason: high LCR but persistent small fragments; useful only if lace/porosity is visually clearer than staghorn.

Cross-batch note: V8 and V13/V14 contact sheets remain useful for historical screening (`case_gallery_for_user_20260510_remote_matched_candidates/index_20260510_current/contact_sheets` and `visuals/strict_visual_matched_texture_v8_frontier_refine*_zoom_20260510`). Use them to choose visual style, not as the final metrics source unless their metrics are re-tabulated.

### 2.4 IFS / transform

1. Main text candidate: `V23_ifs_radial_ornament_o8_d4_orbit_spokes`.
   - Reason: first seed comp=1/LCR=1.0; second seed LCR=0.999888.
   - Needs QA: order-8 symmetry/orbit error, spoke/ring/tooth contact, sampler did not destroy radial structure.

2. Main text or appendix candidate: `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges`.
   - Reason: stable high LCR; best lattice/copy case for transform-copy evidence.
   - Needs QA: copy-bridge survival, orbit/contact metrics, lattice symmetry consistency. Do not claim IFS tree from this pyrite/lattice row.

3. Appendix/needs QA: `V23_ifs_fractal_tree_d5_branch_copy`.
   - Reason: second seed improves to comp=2/LCR=0.999734, but first seed has more fragments; visual copy hierarchy is unverified.
   - Main text only after copy hierarchy and self-similarity QA.

4. Appendix backup: `V23_ifs_branch_ornament_d5_contact_facets`.
   - Reason: stable high LCR; useful if radial/lattice visuals fail.

V21 IFS/transform contact sheets remain useful secondary evidence:

- `visuals/strict_visual_matched_texture_V21_ifs_transform_natural_zoom_20260510/strict_visual_matched_texture_V21_ifs_transform_natural_contact_sheet_20260510.png`
- `visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293300_zoom_20260510/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293300_contact_sheet_20260510.png`
- `visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_zoom_20260510/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_contact_sheet_20260510.png`

Use V21 as appendix/robustness evidence unless it has stronger visual QA than V23.

## 3. Core recommendation for paper assembly

Main text should use one strongest row per family first, then optionally one secondary row if page budget allows:

| family | primary | secondary |
|---|---|---|
| L-system | `V23_lsys_pine_canopy_d5_multi_root_smooth_needles` | `V23_lsys_root_fan_d5_multi_root_smooth_rootlets` |
| Space colonization | `V23_sc_tree_crown_260_attractor_leaf_shell` | `V23_sc_root_network_260_attractor_rootlets` |
| DLA/frontier | `V23_dla_coral_cluster_900_staghorn_frontier` | `V23_dla_frontier_sheet_700_open_boundary` |
| IFS/transform | `V23_ifs_radial_ornament_o8_d4_orbit_spokes` | `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges` |

Appendix candidates:

- L-system: dense rootlets, climbing vine if visually clear.
- Space colonization: sparse-kill crown and bush shell.
- DLA/frontier: crystal faceted frontier and lace porosity coral.
- IFS/transform: branch tree and branch ornament.
- V5c: detail-naturalized historical/reference row, not main evidence.
- Masked naturalization: ablation table and contact sheet, independent from family candidate ranking.

淘汰或不要进入主文:

- V5c `lsys_climbing_vine`, V5c DLA/frontier sheet, V5c DLA coral as main positives.
- Any IFS tree claim before copy hierarchy / self-similarity QA.
- Any DLA/crystal claim phrased as physical simulation rather than frontier-attachment asset generation.

## 4. Missing visual QA

Highest priority missing QA:

1. V23 contact sheets are missing. `visuals/strict_visual_matched_texture_V23_all_family_zoom_20260510` and `visuals/strict_visual_matched_texture_V23_all_family_selected8_zoom_20260510` currently contain only `matched_camera_zoom_plan.json`; render the actual white-background zoom sheets before final selection.
2. V23 family metrics beyond connectivity are missing: L-system branch/attachment metrics, SC attractor coverage, DLA frontier/porosity/blockiness, IFS orbit/symmetry/contact metrics.
3. Need manual visual verdict for the eight proposed main/secondary V23 candidates, with close-up zoom on junctions, terminals, contact bridges, and frontier/open boundaries.
4. Need compare figure alignment against traditional baselines from `case_gallery_for_user_20260510_remote_matched_candidates`, ensuring one-to-one task names and camera protocols match.
5. Masked naturalization has metrics and contact sheet, but should receive final figure QA for whether the neutral render clearly shows local naturalization without changing old state.

## 5. Current status

Recommended current paper-grade direction:

- Use V23 as the main candidate pool because it has two post-GLB metric seeds and strong LCR across all four families.
- Use masked naturalization as method ablation evidence, not as baseline family evidence.
- Keep V5c as appendix/history only.
- Do not modify `paper_siga` until V23 contact sheets and family-specific QA are complete.
