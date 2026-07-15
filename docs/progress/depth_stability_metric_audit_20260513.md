# Depth Stability Metric Audit - 2026-05-13

Scope: read-only audit of existing metric pulls under `results/` for `botanical_tree_root_recursive_remote_20260511*`, `fern_leaf_recursive_remote_20260511*`, and `fern_two_case_recursive_remote_20260512*`. No GPU jobs were launched. No `paper_siga/main.tex` or table files were edited.

## Executive recommendation

There are enough existing CSV/JSON metrics to support an appendix depth-stability/depth-scaling table immediately. A small main-text table is also defensible if it is framed as geometry-level evidence rather than perceptual quality:

- Best main-text-safe source: newer explicit fern root-depth sweeps in `fern_two_case_recursive_remote_20260512o_pull` and `fern_two_case_recursive_remote_20260512p_pull`, especially the surface fiddlehead rows with depths `0,2,4,6`, single mesh component, LCR `1.0`, and stable bbox extents.
- Best appendix source: full legacy recursive metrics in `fern_two_case_recursive_remote_20260512[a-i]_pull/metrics/*.csv` and botanical gate summaries in `botanical_tree_root_recursive_remote_20260511[o,p]_pull/analysis/metric_gate_summary_*.csv`.
- Use botanical tree/root rows cautiously in main text: many pass connectivity thresholds, but some are marked `pending_visual`, `diagnostic_only`, `weak_depth_change`, or have nontrivial fragmentation.

## Metric files found

### Shared full-metric CSV/JSON schema

The following metric files share the same rich schema and can support depth-stability summaries:

- `results/botanical_tree_root_recursive_remote_20260511i_pull/metrics/botanical_tree_root_metrics_20260511i.csv` and `.json` - 91 rows; depth counts: blank 4, d0 19, d1 19, d2 19, d3 19, d4 11.
- `results/botanical_tree_root_recursive_remote_20260511j_pull/metrics/botanical_tree_root_metrics_20260511j_rawonly.csv` and `.json` - 68 rows; d0 14, d1 14, d2 14, d3 14, d4 12.
- `results/botanical_tree_root_recursive_remote_20260511k_pull/metrics/botanical_tree_root_metrics_20260511k.csv` and `.json` - 84 rows; d0 18, d1 18, d2 18, d3 16, d4 14.
- `results/botanical_tree_root_recursive_remote_20260511l_pull/metrics/botanical_tree_root_metrics_20260511l.csv` and `.json` - 125 rows; blank 5, d0 25, d1 25, d2 25, d3 25, d4 20.
- `results/botanical_tree_root_recursive_remote_20260511n_pull/metrics/botanical_tree_root_metrics_20260511n.csv` and `.json` - 61 rows; d0 19, d1 19, d2 19, d3 2, d4 2.
- `results/botanical_tree_root_recursive_remote_20260511o_pull/metrics/botanical_tree_root_metrics_20260511o.csv` and `.json` - 81 rows; blank 4, d0 17, d1 17, d2 17, d3 17, d4 9.
- `results/botanical_tree_root_recursive_remote_20260511p_pull/metrics/botanical_tree_root_metrics_20260511p.csv` and `.json` - 109 rows; d0 23, d1 23, d2 23, d3 23, d4 17.
- `results/fern_leaf_recursive_remote_20260511d_pull/metrics/fern_leaf_recursive_metrics_20260511d.csv` and `.json` - 36 rows; d0 12, d1 12, d2 12.
- `results/fern_leaf_recursive_remote_20260511d_pull/metrics/followup_v24_v25sc_metrics_20260511d.csv` and `.json` - 18 rows; d0 6, d1 6, d2 6.
- `results/fern_leaf_recursive_remote_20260511e_pull/metrics/fern_leaf_recursive_metrics_20260511e.csv` and `.json` - 53 rows; d0 14, d1 14, d2 14, d3 11.
- `results/fern_leaf_recursive_remote_20260511f_pull/metrics/fern_leaf_recursive_metrics_20260511f.csv` and `.json` - 48 rows; d0 12, d1 12, d2 12, d3 12.
- `results/fern_leaf_recursive_remote_20260511g_pull/metrics/fern_leaf_recursive_metrics_20260511g.csv` and `.json` - 36 rows; d0 10, d1 10, d2 10, d3 6.
- `results/fern_two_case_recursive_remote_20260512a_pull/metrics/fern_two_case_metrics_20260512a.csv` and `.json` - 89 rows; depths blank, 0, 1, 2, 3, 4.
- `results/fern_two_case_recursive_remote_20260512b_pull/metrics/fern_two_case_metrics_20260512b.csv` and `.json` - 72 rows; depths 0-4.
- `results/fern_two_case_recursive_remote_20260512c_pull/metrics/fern_two_case_metrics_20260512c.csv` and `.json` - 72 rows; depths 0-4.
- `results/fern_two_case_recursive_remote_20260512d_pull/metrics/fern_two_case_metrics_20260512d.csv` and `.json` - 80 rows; depths 0-4.
- `results/fern_two_case_recursive_remote_20260512e_pull/metrics/fern_two_case_metrics_20260512e.csv` and `.json` - 80 rows; depths 0-4.
- `results/fern_two_case_recursive_remote_20260512g_pull/metrics/fern_two_case_metrics_20260512g.csv` and `.json` - 70 rows; depths 0-4.
- `results/fern_two_case_recursive_remote_20260512h_pull/metrics/fern_two_case_metrics_20260512h.csv` and `.json` - 65 rows; depths 0-4.
- `results/fern_two_case_recursive_remote_20260512i_pull/metrics/fern_two_case_metrics_20260512i.csv` and `.json` - 60 rows; depths 0-4.
- `results/fern_two_case_recursive_remote_20260512k_pull/metrics/fern_two_case_metrics_20260512k.csv` and `.json` - 6 rows; labels encode source depth but `depth_hint` is passthrough d0.
- `results/fern_two_case_recursive_remote_20260512l_pull/metrics/fern_two_case_metrics_20260512l.csv` and `.json` - 6 rows; labels encode source depth but `depth_hint` is passthrough d0.
- `results/fern_two_case_recursive_remote_20260512m_pull/metrics/fern_two_case_metrics_20260512m.csv` and `.json` - 6 rows; labels encode source depth but `depth_hint` is passthrough d0.
- `results/fern_two_case_recursive_remote_20260512o_pull/metrics/fern_two_case_metrics_20260512o.csv` and `.json` - 16 rows; labels encode source depth but `depth_hint` is passthrough d0.
- `results/fern_two_case_recursive_remote_20260512p_pull/metrics/fern_two_case_metrics_20260512p.csv` and `.json` - 16 rows; labels encode source depth but `depth_hint` is passthrough d0.

Shared columns in these full metrics:

`bbox_diag`, `bbox_extent_x`, `bbox_extent_y`, `bbox_extent_z`, `bbox_max_x`, `bbox_max_y`, `bbox_max_z`, `bbox_min_x`, `bbox_min_y`, `bbox_min_z`, `bbox_volume`, `box_count_dimension_proxy`, `box_count_occupied`, `box_count_resolutions`, `box_count_status`, `case_hint`, `component_count`, `component_status`, `depth_hint`, `extension`, `face_area_mean`, `face_area_median`, `faces`, `fragmentation_score`, `label`, `largest_component_vertex_ratio`, `largest_component_vertices`, `largest_occupancy_component_ratio_6n`, `largest_occupancy_component_voxels_6n`, `largest_welded_component_vertex_ratio`, `largest_welded_component_vertices`, `load_error`, `loader`, `method_hint`, `occupancy_component_count_6n`, `occupancy_coverage`, `occupancy_resolution`, `occupancy_status`, `occupied_voxels`, `path`, `primary_component_count`, `primary_connectivity_metric`, `primary_largest_component_ratio`, `small_component_count_lt100`, `small_welded_component_count_lt100`, `surface_area_est`, `vertices`, `vertices_per_bbox_volume`, `weld_tolerance`, `welded_component_count`, `welded_component_status`, `welded_vertex_reduction`, `welded_vertices`.

Useful table fields: `label`, `depth_hint`, `primary_largest_component_ratio`, `largest_component_vertex_ratio`, `primary_component_count`, `component_count`, `vertices`, `faces`, `bbox_extent_{x,y,z}`, `occupancy_coverage`, `fragmentation_score`.

### Explicit root-depth sweep manifests

These files are especially useful because `depth` is an explicit design variable, not inferred from recursive postprocessing labels:

- `results/fern_two_case_recursive_remote_20260512k_pull/roots/initial_metrics.json`
- `results/fern_two_case_recursive_remote_20260512k_pull/roots/manifest.csv`
- `results/fern_two_case_recursive_remote_20260512l_pull/roots/initial_metrics.json`
- `results/fern_two_case_recursive_remote_20260512l_pull/roots/manifest.csv`
- `results/fern_two_case_recursive_remote_20260512m_pull/roots/initial_metrics.json`
- `results/fern_two_case_recursive_remote_20260512m_pull/roots/manifest.csv`
- `results/fern_two_case_recursive_remote_20260512n_pull/roots/initial_metrics.json`
- `results/fern_two_case_recursive_remote_20260512n_pull/roots/manifest.csv`
- `results/fern_two_case_recursive_remote_20260512o_pull/roots/initial_metrics.json`
- `results/fern_two_case_recursive_remote_20260512o_pull/roots/manifest.csv`
- `results/fern_two_case_recursive_remote_20260512p_pull/roots/initial_metrics.json`
- `results/fern_two_case_recursive_remote_20260512p_pull/roots/manifest.csv`

`initial_metrics.json` keys: `bbox_diag`, `bbox_extent`, `bbox_max`, `bbox_min`, `case_id`, `depth`, `faces`, `largest_mesh_component_vertex_ratio`, `mesh_component_count`, `surface_area`, `vertices`.

`manifest.csv` columns: `case_id`, `family`, `variant`, `depth`, `mesh_path`, `leaflet_count`, `tendril_count`, `support_node_count`, `vertices`, `faces`, `largest_mesh_component_vertex_ratio`, `root_design`.

### Botanical gate summaries

These are curated for final-depth pass/fail diagnostics:

- `results/botanical_tree_root_recursive_remote_20260511o_pull/analysis/metric_gate_summary_20260511o.csv`
- `results/botanical_tree_root_recursive_remote_20260511o_pull/analysis/metric_gate_summary_20260511o.json`
- `results/botanical_tree_root_recursive_remote_20260511p_pull/analysis/metric_gate_summary_20260511p.csv`
- `results/botanical_tree_root_recursive_remote_20260511p_pull/analysis/metric_gate_summary_20260511p.json`

`20260511o` columns: `group`, `final_depth`, `status`, `final_plcr`, `final_vertex_lcr`, `final_raw_components`, `final_faces`, `delta_bbox_x`, `delta_bbox_y`, `delta_bbox_z`, `final_label`.

`20260511p` columns: `group`, `final_depth`, `status`, `final_plcr`, `final_vertex_lcr`, `final_primary_components`, `final_raw_components`, `final_vertices`, `final_faces`, `delta_bbox_x`, `delta_bbox_y`, `delta_bbox_z`, `max_abs_delta`, `depth0_diag`, `final_label`, `final_path`.

## Candidate table rows

### Main-text candidate: explicit root-depth scaling, no GPU rerun needed

These rows are from `roots/initial_metrics.json`. `max abs bbox delta` is computed from depth 0 to final depth using relative bbox extent change. For surface fiddleheads in n/o/p, bbox delta is `0.00%`, so the growth is count/detail scaling without envelope drift.

| Source | Group | Depths | Final depth | LCR | Components | Vertices d0 -> final | Faces d0 -> final | Max abs bbox delta | Safety |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `results/fern_two_case_recursive_remote_20260512o_pull/roots/initial_metrics.json` | `fiddlehead_log_surface_recursive_s` | 0,2,4,6 | 6 | 1.0000 | 1 | 5,644 -> 13,820 | 11,275 -> 27,501 | 0.00% | Main text safe |
| `results/fern_two_case_recursive_remote_20260512o_pull/roots/initial_metrics.json` | `fiddlehead_log_surface_recursive_t` | 0,2,4,6 | 6 | 1.0000 | 1 | 7,032 -> 16,484 | 14,042 -> 32,802 | 0.00% | Main text safe |
| `results/fern_two_case_recursive_remote_20260512p_pull/roots/initial_metrics.json` | `fiddlehead_log_surface_recursive_u` | 0,2,4,6 | 6 | 1.0000 | 1 | 5,644 -> 13,820 | 11,275 -> 27,501 | 0.00% | Main text safe |
| `results/fern_two_case_recursive_remote_20260512p_pull/roots/initial_metrics.json` | `fiddlehead_log_surface_recursive_v` | 0,2,4,6 | 6 | 1.0000 | 1 | 7,032 -> 16,484 | 14,042 -> 32,802 | 0.00% | Main text safe |
| `results/fern_two_case_recursive_remote_20260512o_pull/roots/initial_metrics.json` | `fern_mesh_frond_n` | 0,2,4,6 | 6 | 1.0000 | 1 | 3,559 -> 4,860 | 6,826 -> 9,294 | 6.34% | Main text or appendix |
| `results/fern_two_case_recursive_remote_20260512o_pull/roots/initial_metrics.json` | `fern_mesh_frond_m` | 0,2,4,6 | 6 | 1.0000 | 1 | 4,665 -> 9,367 | 8,910 -> 17,822 | 15.07% | Main text or appendix |
| `results/fern_two_case_recursive_remote_20260512p_pull/roots/initial_metrics.json` | `fern_mesh_frond_p` | 0,2,4,6 | 6 | 1.0000 | 1 | 4,977 -> 10,202 | 9,534 -> 19,492 | 27.59% | Appendix |
| `results/fern_two_case_recursive_remote_20260512p_pull/roots/initial_metrics.json` | `fern_mesh_frond_q` | 0,2,4,6 | 6 | 1.0000 | 1 | 3,775 -> 5,233 | 7,258 -> 10,040 | 27.74% | Appendix |

Good shorter-depth appendix rows:

| Source | Group | Depths | Final depth | LCR | Components | Vertices d0 -> final | Faces d0 -> final | Max abs bbox delta | Safety |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `results/fern_two_case_recursive_remote_20260512m_pull/roots/initial_metrics.json` | `fiddlehead_log_organic_crozier_o` | 0,2,4 | 4 | 1.0000 | 1 | 4,972 -> 8,126 | 9,931 -> 16,194 | 8.59% | Appendix |
| `results/fern_two_case_recursive_remote_20260512m_pull/roots/initial_metrics.json` | `fiddlehead_log_organic_crozier_p` | 0,2,4 | 4 | 1.0000 | 1 | 6,206 -> 8,866 | 12,390 -> 17,674 | 6.20% | Appendix |
| `results/fern_two_case_recursive_remote_20260512n_pull/roots/initial_metrics.json` | `fiddlehead_log_surface_recursive_q` | 0,2,4 | 4 | 1.0000 | 1 | 4,774 -> 8,729 | 9,544 -> 17,405 | 0.00% | Appendix or supporting row |
| `results/fern_two_case_recursive_remote_20260512n_pull/roots/initial_metrics.json` | `fiddlehead_log_surface_recursive_r` | 0,2,4 | 4 | 1.0000 | 1 | 5,440 -> 10,525 | 10,876 -> 20,983 | 0.00% | Appendix or supporting row |

### Main-text candidate: full recursive metric stability rows

Rows below use the rich full-metric CSVs with `depth_hint` 0-4. `PLCR` is `primary_largest_component_ratio`; `vertex LCR` is `largest_component_vertex_ratio`; bbox delta is computed from d0 to d4.

| Source | Group | Depths | PLCR d4 | Vertex LCR d4 | Primary comps d4 | Raw comps d4 | Vertices d0 -> d4 | Faces d0 -> d4 | Max abs bbox delta | Safety |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `results/fern_two_case_recursive_remote_20260512e_pull/metrics/fern_two_case_metrics_20260512e.csv` | `fiddlehead_dense_crozier_j_d4_20260512e__v26e_fiddlehead_surface_microbuds` | 0-4 | 1.0000 | 0.9988 | 1 | 119 | 104,332 -> 104,495 | 218,380 -> 219,054 | 0.01% | Main text safe |
| `results/fern_two_case_recursive_remote_20260512g_pull/metrics/fern_two_case_metrics_20260512g.csv` | `fiddlehead_log_spiral_i_d4_20260512g__v26e_fiddlehead_surface_microbuds` | 0-4 | 1.0000 | 0.9991 | 1 | 69 | 75,859 -> 76,611 | 164,608 -> 167,924 | 0.01% | Main text safe |
| `results/fern_two_case_recursive_remote_20260512h_pull/metrics/fern_two_case_metrics_20260512h.csv` | `fiddlehead_log_spiral_i_d4_20260512h__v26e_fiddlehead_surface_microbuds` | 0-4 | 1.0000 | 0.9991 | 1 | 69 | 75,859 -> 76,611 | 164,608 -> 167,924 | 0.01% | Main text safe |
| `results/fern_two_case_recursive_remote_20260512d_pull/metrics/fern_two_case_metrics_20260512d.csv` | `fern_lacy_frond_h_d4_20260512d__v26d_fern_visible_refinement` | 0-4 | 1.0000 | 0.9987 | 1 | 59 | 42,029 -> 44,100 | 99,420 -> 107,466 | 0.06% | Main text safe |
| `results/fern_two_case_recursive_remote_20260512e_pull/metrics/fern_two_case_metrics_20260512e.csv` | `fern_tiered_frond_i_d4_20260512e__v26e_fern_hierarchical_visible` | 0-4 | 1.0000 | 0.9984 | 1 | 85 | 50,336 -> 52,445 | 116,984 -> 123,668 | 0.08% | Main text safe |
| `results/fern_two_case_recursive_remote_20260512b_pull/metrics/fern_two_case_metrics_20260512b.csv` | `fern_broad_frond_c_d4_20260512b__v26b_fern_broad_pinnae` | 0-4 | 1.0000 | 0.9986 | 1 | 42 | 29,450 -> 30,300 | 65,768 -> 68,834 | 0.08% | Main text safe |
| `results/fern_two_case_recursive_remote_20260512b_pull/metrics/fern_two_case_metrics_20260512b.csv` | `fern_branching_frond_d_d4_20260512b__v26a_fern_showcase_pinnae` | 0-4 | 1.0000 | 0.9987 | 1 | 43 | 31,079 -> 32,058 | 71,550 -> 76,418 | 0.17% | Main text safe |
| `results/fern_two_case_recursive_remote_20260512a_pull/metrics/fern_two_case_metrics_20260512a.csv` | `fern_compound_a_d4_20260512a__v25p_fern_midrib_pinnae_handles` | 0-4 | 1.0000 | 0.9990 | 1 | 29 | 26,546 -> 27,332 | 62,046 -> 67,022 | 1.76% | Main text safe |

### Botanical/tree-root candidate rows

These rows are useful for appendix or a small "botanical generalization" note. I would not use them as the primary main-text depth-stability table because the curated gate files label many of them as `pending_visual` or diagnostic.

| Source | Group | Final depth | Status | PLCR | Vertex LCR | Primary comps | Raw comps | Vertices final | Faces final | Max abs delta | Safety |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| `results/botanical_tree_root_recursive_remote_20260511p_pull/analysis/metric_gate_summary_20260511p.csv` | `spider_runner_visible_d4_yneg_20260511p__v25k_spider_terminal_leaflet` | 4 | `metric_positive_candidate_pending_visual` | 0.9970 | 0.9862 | 6 | 333 | 106,561 | 232,188 | 0.154151 | Appendix |
| `results/botanical_tree_root_recursive_remote_20260511p_pull/analysis/metric_gate_summary_20260511p.csv` | `spider_runner_visible_d4_yneg_20260511p__v25l_spider_leaf_tip_clean` | 4 | `metric_positive_candidate_pending_visual` | 0.9970 | 0.9862 | 6 | 344 | 106,586 | 232,178 | 0.154150 | Appendix |
| `results/botanical_tree_root_recursive_remote_20260511p_pull/analysis/metric_gate_summary_20260511p.csv` | `tree_pine_leaf_visible_d4_yneg_20260511p__v25n_pine_leaf_gated` | 4 | `metric_positive_candidate_pending_visual` | 0.9969 | 0.9915 | 5 | 414 | 139,105 | 326,660 | 0.123982 | Appendix |
| `results/botanical_tree_root_recursive_remote_20260511p_pull/analysis/metric_gate_summary_20260511p.csv` | `tree_pine_leaf_visible_d4_yneg_20260511p__v25l_pine_leaf_cluster_clean` | 4 | `metric_positive_candidate_pending_visual` | 0.9969 | 0.9916 | 5 | 429 | 138,971 | 326,074 | 0.123982 | Appendix |
| `results/botanical_tree_root_recursive_remote_20260511p_pull/analysis/metric_gate_summary_20260511p.csv` | `polyhaven_fern_part_handles_d3_yneg_20260511p__v25k_spider_terminal_leaflet` | 3 | `metric_positive_candidate_pending_visual` | 0.9948 | 0.9936 | 3 | 137 | 67,302 | 131,072 | 0.094049 | Appendix |

Additional raw full-metric row that is strong numerically but should be checked visually:

| Source | Group | Depths | PLCR d4 | Vertex LCR d4 | Primary comps d4 | Raw comps d4 | Vertices d0 -> d4 | Faces d0 -> d4 | Max abs bbox delta | Safety |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `results/botanical_tree_root_recursive_remote_20260511i_pull/metrics/botanical_tree_root_metrics_20260511i.csv` | `plant_broad_yneg_20260511i__v25h_spider_basal_crown_micro` | 0-4 | 1.0000 | 0.9974 | 1 | 289 | 111,773 -> 113,467 | 242,532 -> 246,348 | 0.05% | Appendix or main with visual |

## Caveats

- `depth_hint` in `fern_two_case_recursive_remote_20260512k/l/m/o/p_pull/metrics/*.csv` is not the root design depth; it is passthrough depth `0`. Use `roots/initial_metrics.json` or `roots/manifest.csv` for those depth-sweep tables.
- Full-metric CSVs from older recursive runs are rich but mix several method variants and source meshes. They support a depth-stability table, but rows should be grouped by the label prefix before `__depth_XX`.
- `component_count` can be high even when `primary_component_count` is 1 and PLCR is 1.0. For main text, use `primary_largest_component_ratio` and `largest_component_vertex_ratio` as the connectivity metrics, and mention raw components only as diagnostic fragmentation.
- Several botanical gate rows are already marked `pending_visual`, `diagnostic_only`, `weak_depth_change`, or `fragment_risk`. These are not clean main-text evidence without image inspection.
- `max_abs_delta` in the botanical gate summaries appears to be stored as a raw relative value, not a percent. In the full-metric and root-depth tables above, bbox delta is reported as percent and was recomputed from bbox extents.
- The metric audit does not validate rendered visual quality, biological plausibility, or paper figure alignment. It only checks existing geometry metrics.

## Table-ready recommendation

For a concise main-text table, use four to six rows:

1. `fiddlehead_log_surface_recursive_s` and `t` from `20260512o`, depths `0,2,4,6`.
2. `fiddlehead_log_surface_recursive_u` and `v` from `20260512p`, depths `0,2,4,6`.
3. Optionally add `fern_mesh_frond_n` from `20260512o` to show non-fiddlehead fern scaling.
4. Optionally add one full-recursive legacy row, such as `fern_lacy_frond_h_d4_20260512d__v26d_fern_visible_refinement`, to connect the newer root-depth sweep to the existing recursive metric schema.

For the appendix, include the larger legacy full-metric candidates and the botanical gate summaries with their status labels.
