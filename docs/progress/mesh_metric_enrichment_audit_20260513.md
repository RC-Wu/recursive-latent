# Mesh Metric Enrichment Audit - 2026-05-13

Scope: read-only audit of metric-enrichment outputs and related mesh/topology metric CSVs for `paper_siga`. No `main.tex`, table `.tex`, git staging, commit, or push actions were performed.

## Files inspected

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/metric_enrichment_20260513/README.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/metric_enrichment_20260513/priority_mesh_metric_enrichment_20260513.csv`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/metric_enrichment_20260513/metric_enrichment_block_summary_20260513.csv`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/metric_enrichment_20260513/masked_naturalization_topology_summary_20260513.csv`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/metric_enrichment_20260513/smoke_manifest_metric_enrichment_20260513.csv`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_ps_rslg_metric_rows_20260511.csv`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_ps_rslg_metrics.csv`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_trellis2_baseline_metrics.csv`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/traditional_vs_ps_rslg_one_to_one_metrics_20260510/traditional_vs_ps_rslg_one_to_one_metric_rows_20260510.csv`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/gen3d_baseline_metrics_20260510/gen3d_baseline_summary_table_20260510.csv`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/claim_aligned_metric_summary_20260509/claim_aligned_metric_summary.csv`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/claim_aligned_metric_summary_20260509/claim_aligned_metric_long.csv`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/surface_voxel_connectivity_20260509/surface_voxel_connectivity_summary.csv`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/masked_naturalization_main_table_20260511.tex`

## High-level coverage

The enrichment output reports CPU-only mesh diagnostics from `assets/mesh_metric_enrichment_20260513.py`.

From `results/metric_enrichment_20260513/README.md`:

- Inputs requested: 120
- Meshes measured: 107
- Skipped/unloaded: 13
- Welded single-component meshes: 18
- Watertight meshes with volume/compactness: 26

Block summary from `results/metric_enrichment_20260513/metric_enrichment_block_summary_20260513.csv`:

| Block | Requested | Measured | Skipped | Welded single | Watertight | Median boundary edges | Median nonmanifold edges | Median triangle quality |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Experiment 3 priority assets | 65 | 52 | 13 | 1 | 0 | 154193.5 | 0.0 | 0.727 |
| V24 main-comparison scaffolds | 15 | 15 | 0 | 0 | 0 | 934.0 | 944.0 | 0.566 |
| Real-case projection/naturalization inputs | 22 | 22 | 0 | 8 | 8 | 1892.5 | 0.0 | 0.643 |
| Masked-naturalization manifest inputs | 18 | 18 | 0 | 9 | 18 | 0.0 | 0.0 | 0.692 |

Interpretation: the strongest new value is not a topology-clean claim. It is a caveat/diagnostic layer showing that raw face-edge mesh fragmentation, tolerance-welded fragmentation, occupancy connectivity, and visual/readiness status are distinct metrics and should remain separated in the paper.

## Candidate diagnostic 1: mesh fragment index

Recommended definition for reporting: use raw face-edge components plus welded components at tolerance `0.002`; the most compact table column is `welded_component_count`, optionally paired with `largest_welded_component_face_ratio`.

Main-ready successful method medians from `results/metric_enrichment_20260513/priority_mesh_metric_enrichment_20260513.csv`:

| Method id | Rows | Raw comp. median | Welded comp. median | Welded comp. range | Boundary median | Nonmanifold median | Triangle quality median | Watertight |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `hunyuan_root_meshcopy` | 4 | 272162.5 | 152126.5 | 79496-256216 | 820314.5 | 0.0 | 0.6966296225139275 | 0/4 |
| `trellis2_generatedroot_meshcopy` | 6 | 182031.0 | 69565.5 | 36037-145803 | 548062.0 | 0.0 | 0.7454516110159318 | 0/6 |
| `trellis2_oneshot_image` | 6 | 5816.0 | 85.5 | 5-1522 | 42457.0 | 0.5 | 0.7470151558474831 | 0/6 |
| `trellis2_root_latentcopy` | 2 | 95.0 | 80.5 | 26-135 | 7661.0 | 2660.5 | 0.773571997945082 | 0/2 |
| `ps_rslg` | 9 | 7444.0 | 132.0 | 1-442 | 38764.0 | 0.0 | 0.596352287649533 | 0/9 |

Strongest control rows showing mesh-copy fragmentation:

| Case | Method | Variant | Raw comp. | Welded comp. | Boundary edges | Largest welded face ratio | Triangle quality | Path |
|---|---|---|---:|---:|---:|---:|---:|---|
| bismuth | `hunyuan_root_meshcopy` | `bismuth_terrace_full_srt_depth02_direct` | 299200 | 256216 | 898400 | 0.000007782585686268406 | 0.8098924471503111 | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/publication_hunyuan_text_root_meshspace_20260511/bismuth_crystal_root/bismuth_terrace_full_srt_depth02_direct/bismuth_terrace_full_srt_depth02_direct_white_pbr.glb` |
| pyrite | `hunyuan_root_meshcopy` | `pyrite_lattice_full_srt_depth02_direct` | 297575 | 213358 | 895150 | 0.000013931004378979043 | 0.6831146500185317 | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/publication_hunyuan_text_root_meshspace_20260511/pyrite_crystal_root/pyrite_lattice_full_srt_depth02_direct/pyrite_lattice_full_srt_depth02_direct_white_pbr.glb` |
| pyrite | `trellis2_generatedroot_meshcopy` | `pyrite_lattice full_srt depth=2 direct merge` | 199950 | 145803 | 599900 | 0.0000137098045667359 | 0.7167990389269489 | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/publication_hunyuan_mesh_space_20260510/pyrite/pyrite_lattice/full_srt/depth_02/pyrite_pyrite_lattice_full_srt_depth_02_white_pbr.glb` |
| coral | `trellis2_generatedroot_meshcopy` | `coral_frontier_branch full_srt depth=2 direct merge` | 167412 | 80069 | 502824 | 0.00003731807438736161 | 0.737632415113993 | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/publication_hunyuan_mesh_space_20260510/coral/coral_frontier_branch/full_srt/depth_02/coral_coral_frontier_branch_full_srt_depth_02_white_pbr.glb` |

Strongest PS-RSLE candidate rows:

| Case | Variant | Vertices | Triangles | Raw comp. | Welded comp. | Largest welded face ratio | Boundary edges | Nonmanifold edges | Watertight | Triangle quality | Path |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| bismuth | `V21_ifs_bismuth_stepped_transform_d5_iridescent_steps8_tex2048_seed20293804_xformers` | 16960 | 11166 | 2973 | 179 | 0.6736048806746815 | 15848 | 0 | False | 0.5878987087165862 | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20291700_20260510/V21_ifs_bismuth_stepped_transform_d5_iridescent_steps8_tex2048_seed20293804_xformers/textured.glb` |
| coral | `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA_steps8_tex2048_seed20284523_xformers` | 17786 | 14342 | 1944 | 131 | 0.7641641082891432 | 17114 | 0 | False | 0.41873930123336595 | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510/V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA_steps8_tex2048_seed20284523_xformers/textured.glb` |
| coral | `strict_visual_matched_texture_20260510` | 146885 | 117340 | 19659 | 2 | 0.9998977330833475 | 139122 | 0 | False | 0.8660254037839693 | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_visual_matched_texture_20260510/dla_coral_cluster_900_frontier_connected_steps8_tex2048_seed20260711_xformers/textured.glb` |
| pyrite | `V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA_steps8_tex2048_seed20284526_xformers` | 28641 | 18498 | 5473 | 187 | 0.7954656133326119 | 27118 | 0 | False | 0.596352287649533 | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA_steps8_tex2048_seed20284526_xformers/textured.glb` |
| pyrite | `strict_visual_matched_texture_20260510` | 294399 | 226088 | 50396 | 1 | 1.0 | 262572 | 0 | False | 0.866025403783679 | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_visual_matched_texture_20260510/ifs_fractal_lattice_d4_pyrite_steps8_tex2048_seed20260841_xformers/textured.glb` |
| root_fan | `V25_lsys_root_fan_smooth_anchorD_stable_steps8_tex2048_seed20285514_xformers` | 40410 | 27168 | 7444 | 442 | 0.36480533396832954 | 38764 | 0 | False | 0.21517521665333914 | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_visual_matched_texture_V25_root_sc_refine_20260510/V25_lsys_root_fan_smooth_anchorD_stable_steps8_tex2048_seed20285514_xformers/textured.glb` |
| tree_crown | `V25_sc_tree_crown_tapered_B_steps8_tex2048_seed20285522_xformers` | 99455 | 74138 | 14172 | 169 | 0.948117486958494 | 96428 | 0 | False | 0.5513367258079581 | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_visual_matched_texture_V25_root_sc_refine_20260510/V25_sc_tree_crown_tapered_B_steps8_tex2048_seed20285522_xformers/textured.glb` |

Recommendation: put the method-median table in the appendix, not the main paper. Add only a main-text caveat sentence that PS-RSLE has lower welded fragmentation than generated-root mesh-copy baselines in this subset, but no main-ready Experiment 3 group is watertight. Do not use triangle quality as a PS-RSLE advantage because PS-RSLE's median triangle quality is lower than several controls.

## Candidate diagnostic 2: occupancy components and LCR

This is already the strongest main-paper diagnostic layer because it is aligned with the existing tables and captions.

From `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/experiment3_sparse_latent_vs_meshspace_20260511/experiment3_ps_rslg_metric_rows_20260511.csv`:

| Case | Label | Raw component count in source row | Occupancy components 6n | LCR | Components r1 | LCR r1 | Path |
|---|---|---:|---:|---:|---:|---:|---|
| root_fan | `V25_lsys_root_fan_smooth_anchorD_stable_steps8_tex2048_seed20285514_xformers` | 1 | 1 | 1.0 | 1 | 1.0 | `visuals/strict_visual_matched_texture_V25_root_sc_refine_20260510/V25_lsys_root_fan_smooth_anchorD_stable_steps8_tex2048_seed20285514_xformers/textured.glb` |
| tree_crown | `V25_sc_tree_crown_tapered_B_steps8_tex2048_seed20285522_xformers` | 1 | 1 | 1.0 | 1 | 1.0 | `visuals/strict_visual_matched_texture_V25_root_sc_refine_20260510/V25_sc_tree_crown_tapered_B_steps8_tex2048_seed20285522_xformers/textured.glb` |
| coral | `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA_steps8_tex2048_seed20284523_xformers` | 1 | 1 | 1.0 | 1 | 1.0 | `visuals/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510/V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA_steps8_tex2048_seed20284523_xformers/textured.glb` |
| pyrite | `V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA_steps8_tex2048_seed20284526_xformers` | 3 | 3 | 0.9998265845833695 | 1 | 1.0 | `visuals/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510/V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seed20284526_xformers/textured.glb` |
| radial_ornament | `V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA_steps8_tex2048_seed20284527_xformers` | 1 | 1 | 1.0 | 1 | 1.0 | `visuals/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510/V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA_steps8_tex2048_seed20284527_xformers/textured.glb` |
| bismuth | `V21_ifs_bismuth_stepped_transform_d5_iridescent_steps8_tex2048_seed20293804_xformers` | 1 | 1 | 1.0 | 1 | 1.0 | `visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20291700_20260510/V21_ifs_bismuth_stepped_transform_d5_iridescent_steps8_tex2048_seed20293804_xformers/textured.glb` |
| vine | `vine_stage5_parthenocissus_warm_steps8_tex2048_xformers` | 113957 | 4 | 0.999 | blank | blank | `visuals/vine_stage5_guide_sweep_20260509/vine_stage5_parthenocissus_warm_steps8_tex2048_xformers/textured.glb` |

Note: the path strings above are copied from the inspected CSV where available. The enrichment CSV uses the full absolute paths for the corresponding PS-RSLE GLBs.

From `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/experiment3_sparse_latent_vs_mesh_space_table_20260511.tex`, the current paper-facing Experiment 3 comparison already gives the strongest compact LCR comparison:

| Case | Method | Occ. comp. | LCR | Status |
|---|---|---:|---:|---|
| tree crown | Trellis2 one-shot | 19 | 0.978 | one-shot control |
| tree crown | Trellis2 latent-copy | 11 | 0.995 | copy-state control |
| tree crown | Trellis2 root+mesh-copy | 32 | 0.993 | copy-state control |
| tree crown | Hunyuan root+mesh-copy | 40 | 0.998 | copy-state control |
| tree crown | PS-RSLE | 1 | 1.000 | selected positive |
| bismuth | Trellis2 one-shot | 1 | 1.000 | one-shot control |
| bismuth | Trellis2 latent-copy | 7 | 0.909 | copy-state control |
| bismuth | Trellis2 root+mesh-copy | 53 | 0.112 | copy-state control |
| bismuth | Hunyuan root+mesh-copy | 22 | 0.999 | copy-state control |
| bismuth | PS-RSLE | 1 | 1.000 | selected positive |
| coral | Trellis2 one-shot | 5 | 0.971 | one-shot control |
| coral | Trellis2 latent-copy | 4 | 0.992 | copy-state control |
| coral | Trellis2 root+mesh-copy | 43 | 0.990 | copy-state control |
| coral | Hunyuan root+mesh-copy | 3 | 0.916 | copy-state control |
| coral | PS-RSLE | 1 | 1.000 | selected positive |
| pyrite | Trellis2 one-shot | 9 | 0.999 | one-shot control |
| pyrite | Trellis2 latent-copy | 17 | 0.714 | copy-state control |
| pyrite | Trellis2 root+mesh-copy | 46 | 0.750 | copy-state control |
| pyrite | Hunyuan root+mesh-copy | 3 | 0.929 | copy-state control |
| pyrite | PS-RSLE | 3 | 1.000 | proxy-positive+caveat |

Recommendation: keep this in main text/table form. It is the clearest PS-RSLE vs controls comparison. Pair it with the appendix mesh-fragment table as a caveat, because high occupancy LCR can coexist with severe raw or welded mesh fragmentation.

## Candidate diagnostic 3: masked-naturalization topology

From `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/metric_enrichment_20260513/masked_naturalization_topology_summary_20260513.csv`:

| Variant | Raw comp. median | Welded comp. median | Boundary median | Nonmanifold median | Triangle quality median | Watertight | Rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| `raw_grammar_proposal` | 16.0 | 16.0 | 0.0 | 0.0 | 0.7034477901716824 | 3 | 3 |
| `final_only_projection_repair` | 4.0 | 4.0 | 0.0 | 0.0 | 0.6904004958349854 | 3 | 3 |
| `per_depth_projection` | 4.0 | 4.0 | 0.0 | 0.0 | 0.6883055379712126 | 3 | 3 |
| `per_depth_weak_naturalization` | 1.0 | 1.0 | 0.0 | 0.0 | 0.6882511283042331 | 3 | 3 |
| `per_depth_masked_naturalization` | 1.0 | 1.0 | 0.0 | 0.0 | 0.6905292651046249 | 3 | 3 |
| `per_depth_global_naturalization` | 1.0 | 1.0 | 0.0 | 0.0 | 0.6939672189439087 | 3 | 3 |

The smoke manifest exact rows show the underlying pattern:

- `raw_grammar_proposal`: raw components 16, welded components 16, largest welded face ratio 0.8015267175572519, watertight True, compactness 0.4244216273462208, path `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/masked_naturalization_ablation_20260510_seed20260512/tasks/botanical_root/raw_grammar_proposal/mesh.obj`.
- `final_only_projection_repair`: raw components 4, welded components 4, largest welded face ratio 0.9916434540389972, watertight True, compactness 0.5249889863833094, path `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/masked_naturalization_ablation_20260510_seed20260512/tasks/botanical_root/final_only_projection_repair/mesh.obj`.

Recommendation: appendix only. This subset supports a cautious statement that weak, masked-local, and global naturalization become single-component in this small mesh subset. It should not be used to distinguish masked from global topology-wise, because both have median raw/welded component count 1 and 3/3 watertight rows. The main preference for masked local naturalization should continue to rely on locality, quality, drift, handle survival, and committed pass rate.

## Candidate diagnostic 4: handle/readiness/pass metrics

From `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/masked_naturalization_main_table_20260511.tex`:

| Naturalization variant | Rough. down | Normal up | Artifacts down | Drift down | Handle surv. up | Quality up | Committed pass up |
|---|---:|---:|---:|---:|---:|---:|---:|
| rule-only | 50.00 | 0.000 | 0.487 | 0.203 | 0.500 | 0.529 | 0.000 |
| masked/no-proj | 47.45 | 0.003 | 0.488 | 0.201 | 0.500 | 0.530 | 0.000 |
| no-N/+proj | 16.94 | 0.597 | 0.348 | 0.000 | 1.000 | 0.771 | 0.750 |
| weak/+proj | 14.11 | 0.664 | 0.228 | 0.088 | 1.000 | 0.805 | 1.000 |
| masked/+proj | 13.92 | 0.669 | 0.227 | 0.090 | 1.000 | 0.807 | 1.000 |
| global/+proj | 13.58 | 0.677 | 0.229 | 0.090 | 1.000 | 0.735 | 1.000 |

Recommendation: keep this as the main Experiment 4 table. It carries the actual masked-vs-global argument: masked/+proj matches the 1.000 committed pass and 1.000 handle survival of global/+proj while keeping higher quality (0.807 vs 0.735) and similar drift (0.090 vs 0.090). Add the masked-naturalization mesh topology table only as a supplement.

Readiness/pass metadata from `priority_mesh_metric_enrichment_20260513.csv` is useful only as appendix or audit text:

- `manifest_ready_for_main=yes`: 28 rows.
- Main-ready successful `ps_rslg`: 9 rows.
- Main-ready successful `hunyuan_root_meshcopy`: 4 rows.
- Main-ready successful `trellis2_generatedroot_meshcopy`: 6 rows.
- Main-ready successful `trellis2_oneshot_image`: 6 rows.
- Main-ready successful `trellis2_root_latentcopy`: 2 rows.

Do not turn `manifest_ready_for_main` into a quantitative performance metric; it is a curation/status field, not an experimental endpoint.

## Candidate diagnostic 5: skipped/high-face-count rows

From `priority_mesh_metric_enrichment_20260513.csv`, all 13 skipped priority rows were skipped by the face-count guard. This is important for any appendix caption.

| Case | Method id | Variant | Raw faces in file | Vertices | Load error | Path |
|---|---|---|---:|---:|---|---|
| bismuth | `trellis2_oneshot_image` | `target_guide_seed2026061101` | 1052758 | 496482 | `face_count_above_limit:1052758>750000` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/experiment3_sparse_latent_vs_meshspace_20260511/trellis2_oneshot/bismuth_target_seed2026061101/trellis2_dinov3_min.obj` |
| bismuth | `trellis2_root_latentcopy` | `root_guide_copy_shift_upper_z_seed2026061201` | 919990 | 441910 | `face_count_above_limit:919990>750000` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/experiment3_sparse_latent_vs_meshspace_20260511/trellis2_latentcopy/bismuth_root_seed2026061201/copy_shift_upper_z/mesh.obj` |
| coral | `trellis2_root_latentcopy` | `copy_shift_upper_z` | 2453600 | 1226785 | `face_count_above_limit:2453600>750000` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/gen3d_baseline_trellis2_one_shot_latent_nopre_20260510/coral_latent_transform_seed610_steps6_nopre/copy_shift_upper_z/mesh.obj` |
| pyrite | `trellis2_oneshot_image` | `target_guide_seed2026061101` | 2983152 | 1447791 | `face_count_above_limit:2983152>750000` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/experiment3_sparse_latent_vs_meshspace_20260511/trellis2_oneshot/pyrite_target_seed2026061101/trellis2_dinov3_min.obj` |
| pyrite | `trellis2_root_latentcopy` | `root_guide_copy_shift_upper_z_seed2026061201` | 8413466 | 3209572 | `face_count_above_limit:8413466>750000` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/experiment3_sparse_latent_vs_meshspace_20260511/trellis2_latentcopy/pyrite_root_seed2026061201/copy_shift_upper_z/mesh.obj` |
| radial_ornament | `trellis2_oneshot_image` | `target_guide_seed2026061101` | 3439614 | 1273674 | `face_count_above_limit:3439614>750000` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/experiment3_sparse_latent_vs_meshspace_20260511/trellis2_oneshot/radial_ornament_target_seed2026061101/trellis2_dinov3_min.obj` |
| radial_ornament | `trellis2_root_latentcopy` | `root_guide_copy_shift_upper_z_seed2026061201` | 3361712 | 1553983 | `face_count_above_limit:3361712>750000` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/experiment3_sparse_latent_vs_meshspace_20260511/trellis2_latentcopy/radial_ornament_root_seed2026061201/copy_shift_upper_z/mesh.obj` |
| vine | `trellis2_oneshot_image` | `target_guide_seed2026061101` | 3323032 | 1658111 | `face_count_above_limit:3323032>750000` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/experiment3_sparse_latent_vs_meshspace_20260511/trellis2_oneshot/vine_target_seed2026061101/trellis2_dinov3_min.obj` |

Recommendation: mention the skip count in the appendix caption. Do not state full Experiment 3 coverage for raw/welded mesh diagnostics.

## Main vs appendix recommendation

Main paper:

- Keep the existing Experiment 3 occupancy component/LCR table as the main quantitative comparison. It directly compares PS-RSLE with one-shot, latent-copy, root+mesh-copy, and Hunyuan root+mesh-copy controls.
- Keep the masked-naturalization handle/readiness/pass table as the main Experiment 4 quantitative result.
- Add at most one main-text caveat sentence: raw/welded mesh diagnostics show lower median welded fragmentation for PS-RSLE than generated-root mesh-copy controls in the main-ready subset, but no main-ready Experiment 3 group is watertight; therefore mesh diagnostics are export/fragmentation caveats rather than topology-clean proof.

Appendix or supplement:

- Add a mesh-fragmentation diagnostic table using method medians: rows, raw component median, welded component median, welded range, boundary median, nonmanifold median, watertight count.
- Add the masked-naturalization topology summary table only if appendix space permits.
- Add a skip/coverage note: 13/65 Experiment 3 priority assets were skipped in the enrichment run because they exceeded the 750000 face-count guard.

Do not add:

- Do not add triangle quality as a main superiority metric.
- Do not claim watertightness, manifoldness, or physical simulation readiness for PS-RSLE outputs from these diagnostics.
- Do not merge raw/welded mesh components into the main LCR table without a caveat; they measure different things and can disagree sharply.
