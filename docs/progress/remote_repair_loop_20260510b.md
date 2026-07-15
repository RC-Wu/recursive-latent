# Remote Repair Loop 20260510b

Status: active remote-only repair loop  
Created: 2026-05-10 21:15 CST  
Remote root: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
Output root: `results/publication_repair_remote_20260510b`

## User Constraint

The user explicitly corrected the workflow: repair the bad tree-root and old non-tree cases with our own recursive algorithm on `a100-2`, not with local procedural generation. Local procedural previews from earlier notes are diagnostics only and must not be treated as final evidence.

## Code Change

`assets/trellis2_recursive_slat_grammar_workflow.py` now supports:

- `--growth-axis {x,y,z}`
- `--growth-sign {-1,1}`

This makes tip/crown selection and attached grammar shifts configurable instead of hard-coding the latent +Y side. The immediate reason is the bad `lsystem_spiky_iso.png` tree-root case: the old grammar could grow from the wrong side of the module, matching the user's diagnosis that the root/crown frame was inverted.

## Remote Inputs

Uploaded local stable candidates to:

- `results/publication_repair_remote_20260510b/inputs/V25_lsys_root_fan_smooth_anchorD_stable.obj`
- `results/publication_repair_remote_20260510b/inputs/V25_sc_tree_crown_tapered_B.obj`
- `results/publication_repair_remote_20260510b/inputs/V23_lsys_pine_canopy_d5_multi_root_smooth_needles.obj`
- `results/publication_repair_remote_20260510b/inputs/ruin_arch_portal_stage03.obj`

Existing remote roots used:

- `selected_meshes_extra_20260509/lsystem_fork_a0p5_pruned.obj`
- `results/siga_non_tree_root_sweep_20260508_1440/crown_radial_ornament/trellis2_dinov3_min.obj`
- `results/siga_non_tree_root_sweep_20260508_1440/scifi_mechanical_module/trellis2_dinov3_min.obj`
- `results/siga_non_tree_root_sweep_20260508_1440/snow_architecture/trellis2_dinov3_min.obj`

## Remote Lanes

Launcher:

- local/remote script: `assets/run_publication_repair_remote_20260510b.sh`

Because `screen` is not installed on `a100-2`, lanes were launched with `nohup` and PID files:

- tree: GPU 4, pid file `results/publication_repair_remote_20260510b/pids/tree.pid`
- crown_stable: GPU 5, pid file `results/publication_repair_remote_20260510b/pids/crown_stable.pid`
- crown_old: GPU 6, pid file `results/publication_repair_remote_20260510b/pids/crown_old.pid`
- arch_scifi: GPU 7, pid file `results/publication_repair_remote_20260510b/pids/arch_scifi.pid`

Session logs:

- `results/publication_repair_remote_20260510b/session_logs/tree.screen.log`
- `results/publication_repair_remote_20260510b/session_logs/crown_stable.screen.log`
- `results/publication_repair_remote_20260510b/session_logs/crown_old.screen.log`
- `results/publication_repair_remote_20260510b/session_logs/arch_scifi.screen.log`

## Current Interpretation

As of the launch check, all four lanes entered the TRELLIS2 SLat encoder/decoder and wrote real remote OBJ/preview outputs. No result is publication-ready until:

1. preview PNGs are visually inspected;
2. selected final OBJs are rendered with Blender/Cycles;
3. `recursive_growth_mesh_metrics.py` reports topology/fragmentation metrics;
4. the result is documented as usable, diagnostic, or failed.


## Update 2026-05-10 21:30 CST

First remote-only repair round completed on `a100-2`:

- `publication_repair_remote_20260510b`: 19 cases, 119 OBJ/preview outputs.
- Selected metrics: `results/publication_repair_remote_20260510b/metrics_selected/selected_metrics_20260510b.csv`.
- Local pulled QA mirror: `results/publication_repair_remote_20260510b_pull/`.

Key findings:

- The original tree-root semantic failure is real: full fork/side attached grammar can still copy large crown regions sideways and create floating leaf sheets. The new growth-axis/sign options fix the gross direction error but do not by themselves make the old fork grammar publication-grade.
- Best first-round tree candidate was `tree_v25_zpos_fork_d2`, with remote metrics: `129782` vertices, `268522` faces, raw LCR `0.7873`, occupancy LCR `0.9523`, `89` occupancy components. It is directionally correct but still visually dusty.
- Existing V25 root replacement remains stronger for paper use: `V25_lsys_root_fan_smooth_anchorD_stable` is already documented as r0 single-component / LCR 1.0 in `strict_visual_matched_texture_V25_root_sc_refine` and has textured GLB + zoom renders. This is the safer replacement for the bad `lsystem_spiky_iso` gallery slot while the SLat grammar repair continues.
- Old non-tree cases:
  - old crown/radial ornament: conservative portal avoids total collapse but remains a fragmented shell; not main-paper quality.
  - scifi: geometry is not collapsed; metrics are comparatively strong (`occ LCR ~0.945` before pruning). The old bad impression is mostly material/camera/dirty-root/readability.
  - snow arch remains fragmented (`occ LCR ~0.722`), while ruin arch is more stable (`occ LCR ~0.861`) but visually reads as a large base/shell rather than a clean arch.

Second remote-only micro grammar round completed in `publication_repair_remote_20260510c`:

- Added `crown_bud_attach` and `crown_micro_fork_attach` to `trellis2_recursive_slat_grammar_workflow.py`.
- `crown_bud_attach` copies only the top 8% growth-side sparse tokens through six bridge steps, avoiding whole-crown lateral duplication.
- Best micro candidates:
  - `tree_micro_ypos_bud_d2`: raw LCR `0.9622`, occupancy LCR `0.9914`, occupancy components `10`.
  - `tree_micro_zpos_bud_d2`: raw LCR `0.9160`, occupancy LCR `0.9891`, occupancy components `15`.
  - `tree_micro_ypos_bud_d3`: raw LCR `0.9548`, occupancy LCR `0.9784`, occupancy components `16`.
- Blender white-background QA from remote-generated OBJs is in `results/publication_repair_remote_20260510c_pull/blender_renders_micro_white_flat/contact_sheet.png`.
- Visual status: the case is no longer directionally wrong and is a usable candidate; it still has small crown-tip dust and should not yet be called final publication-grade without texturing/material/camera cleanup and possibly minor component pruning.

## Update 2026-05-10 22:12 CST: PBR GLB Closure For Tree-Root Repair

Remote TRELLIS2 texturing/export completed for the best micro-bud tree candidates in `publication_repair_remote_20260510c/textured_micro/`:

| Candidate | Guide | Remote GLB | Status | Notes |
|---|---|---|---|---|
| `micro_ypos_bud_d2_rootguide` | V25 root guide | `results/publication_repair_remote_20260510c/textured_micro/micro_ypos_bud_d2_rootguide_steps8_tex2048_seed202605301_xformers/textured.glb` | ok | overly red/warm; not recommended |
| `micro_ypos_bud_d2_spikyguide` | old spiky guide | `results/publication_repair_remote_20260510c/textured_micro/micro_ypos_bud_d2_spikyguide_steps8_tex2048_seed202605303_xformers/textured.glb` | ok | gray cedar tone, but weaker silhouette than zpos |
| `micro_zpos_bud_d2_rootguide` | V25 root guide | `results/publication_repair_remote_20260510c/textured_micro/micro_zpos_bud_d2_rootguide_steps8_tex2048_seed202605302_xformers/textured.glb` | ok | stable shape but too dark/brown |
| `micro_zpos_bud_d2_spikyguide` | old spiky guide | `results/publication_repair_remote_20260510c/textured_micro/micro_zpos_bud_d2_spikyguide_steps8_tex2048_seed202605304_xformers/textured.glb` | ok | current recommended repaired spiky/tree-root candidate |

Pulled local QA mirror:

- GLBs: `results/publication_repair_remote_20260510c_pull/textured_micro/`
- PBR render QA: `results/publication_repair_remote_20260510c_pull/textured_micro_renders_white_flat/contact_sheet.png`

Current recommendation:

- Use `micro_zpos_bud_d2_spikyguide` as the repaired version of the bad `lsystem_spiky` direction case if the gallery needs this snow-cedar visual family.
- Use `V25_lsys_root_fan_smooth_anchorD_stable` as the stricter paper-safe root replacement if the requirement is metric-stable, clean, and already zoom-rendered.
- Do not claim the repaired spiky case is fully publication-grade until a final render pass hides/removes tiny crown-tip speckles and the chosen GLB is placed into the target gallery/figure layout.

## Update 2026-05-10 23:08 CST: Root/Anchor Protocol Clarification

The user asked whether the tree, crown, weapon/tank/hard-surface, and city-style structures need explicit root and growth-anchor definitions. Code and paper audit show the answer is yes:

- The current executor is `mesh root -> Trellis2 shape-SLat encode -> sparse-coordinate grammar rewrite -> decode/export`.
- `--mesh` is a predeclared root asset. It is normalized and encoded into Trellis2 SLat; the generator does not discover the root automatically.
- `--growth-axis` and `--growth-sign` are predeclared case controls. Operator-internal frontier masks are then chosen automatically from SLat coordinates by geometric selectors:
  - tree/root: top growth-height quantile;
  - crown/ornament: lateral-radius frontier plus cap filter;
  - arch: top/center/depth keystone filter;
  - hard-surface/scifi: side-socket plus height filter.
- The following are authored, case-specific, and must be recorded in manifests and paper protocol: root mesh, growth frame, grammar family, fit scale, depth, max tokens, seed, guide image, pruning/texture settings, and camera/render style.
- The paper was updated to add a `Root and Program Specification` subsection after `Problem Setting`, clarifying that PS-RSLG currently executes authored sparse-latent recursive programs; it does not learn grammar parameters, discover semantic roots, or automatically search roots.

Implication for current repair cases:

- Tree: the old bad `lsystem_spiky_iso` is consistent with an incorrect root/growth frame plus overly broad crown frontier. Continue using micro-bud/top-frontier grammars and record `z,+1` vs `y,+1` choices.
- Crown: the old root has useful ornament semantics, but whole-ring/radial/portal copy is too broad. Positive reruns should prefer masked rim/bud/frontier attach; old radial4 remains a failure boundary.
- Hard-surface / tank / weapon: no dedicated tank/weapon root was found in the current workflow. The available positive proxy is `scifi_mechanical_module`; call it hard-surface/scifi module unless a true tank/weapon root is introduced.
- City: the only located city-style root is `island_city_scale_down_stage03.obj`, an old scale-down proxy. It is not an implemented city grammar proof; use as architecture/city-scale diagnostic unless a new city root/operator is authored and measured.

Next remote batch should be `publication_repair_remote_20260510e`: run manifest-first anchored variants for tree, crown, scifi/hard-surface, and city/architecture; pull OBJ/GLB outputs; run metrics and Blender render QA before any paper-safe claim.

## Update 2026-05-11 00:16 CST: 20260510e Anchor Screen And 20260510f PBR Launch

The manifest-first anchored screen `publication_repair_remote_20260510e` completed on `a100-2` and was pulled locally:

- manifest: `results/publication_repair_remote_20260510e_pull/root_anchor_manifest_20260510e.tsv`;
- metrics: `results/publication_repair_remote_20260510e_pull/metrics/selected_metrics_20260510e.csv`;
- Blender white QA: `results/publication_repair_remote_20260510e_pull/blender_white_qa/contact_sheet_white.png`.

Claim-gated visual/metric interpretation:

- `tree_v25_bud_d1` is the current best tree/root repair candidate: occ LCR `0.9927`, visual crown/trunk direction reads correctly.
- `scifi_old_tight_d1` is the best hard-surface proxy: occ LCR `0.9950`, readable mechanical module. It must not be described as a tank or weapon.
- `arch_clean_key_d2` is the best architecture/portal proxy: occ LCR `0.9984`, readable as an arch/portal with minor lower fragments. It is an architecture proxy, not city proof.
- `crown_old_rim_d1` and `ornament_v24_rim_d1` are worth PBR as ornament/appendix candidates. `ornament_v24_rim_d1` is metric-clean (occ LCR `1.0`) but visually flat.
- `tree_flipz_bud_d2` is excluded from positive claims because of lateral spray/floating fragments and occ LCR `0.8791`.
- `island_city_scale_d1` is excluded from PBR/main claims. It remains a city/LOD diagnostic only; visual quality is fragmented and occ components remain high.

New remote PBR/cleanup launcher:

- local/remote script: `assets/run_publication_repair_remote_20260510f.sh`;
- remote output root: `results/publication_repair_remote_20260510f`;
- storage at launch: project size about `94G`, below the current `200GB` cap;
- GPUs 4/5/6/7 were free at launch and are the only GPUs used by the four lanes.

The `20260510f` batch uses only remote SLat-generated `20260510e` OBJ outputs. It applies conservative small-island pruning and TRELLIS2 mesh texturing/export. It does not introduce local procedural geometry as final evidence.

Launched lanes:

- GPU 4 tree: `tree_v25_bud_d1_spiky_pruned`, `tree_v25_bud_d1_root_pruned`;
- GPU 5 crown/ornament: `crown_old_rim_d1_ornament_pruned`, `ornament_v24_rim_d1_ornament_raw`, `crown_tapered_rim_d1_ornament_pruned`;
- GPU 6 hard-surface proxy: `scifi_old_tight_d1_metal_pruned`, `scifi_clean_translate_d2_metal_pruned`;
- GPU 7 architecture proxy: `arch_clean_key_d2_stone_pruned`, `snow_arch_key_d1_stone_pruned`.

First completed GLBs at `2026-05-11 00:14 CST`:

- `tree_v25_bud_d1_spiky_pruned_steps8_tex2048_seed202605601_xformers/textured.glb`, `status=ok`, `12.3MB`;
- `scifi_old_tight_d1_metal_pruned_steps8_tex2048_seed202605621_xformers/textured.glb`, `status=ok`, `23.3MB`;
- `arch_clean_key_d2_stone_pruned_steps8_tex2048_seed202605631_xformers/textured.glb`, `status=ok`, `24.4MB`.

Next gate before any paper-safe statement:

1. wait for all `20260510f` lanes to exit;
2. pull `results/publication_repair_remote_20260510f`;
3. run local Blender render QA on textured GLBs with white and/or studio backgrounds;
4. run GLB import/metrics QA;
5. update figure/gallery manifests with explicit claim scopes.

## Update 2026-05-11 00:32 CST: 20260510f Completed And Local QA

The `publication_repair_remote_20260510f` remote PBR batch fully completed on `a100-2`:

- all four lanes exited;
- all 9 `summary.json` files report `status=ok`;
- local pull mirror: `results/publication_repair_remote_20260510f_pull/`;
- manifest: `results/publication_repair_remote_20260510f_pull/selected_texture_manifest_20260510f.tsv`;
- textured GLB metrics: `results/publication_repair_remote_20260510f_pull/metrics/textured_glb_metrics_all_20260510f.csv`;
- textured GLB render QA: `results/publication_repair_remote_20260510f_pull/blender_textured_white_qa/contact_sheet_textured_white_all.png`;
- material-override render QA for main candidates: `results/publication_repair_remote_20260510f_pull/blender_material_override_qa/contact_sheet_material_override.png`.

Completed GLB outputs:

| Label | GLB size | Current visual status |
|---|---:|---|
| `tree_v25_bud_d1_spiky_pruned` | 12.3MB | best tree/root repair from this lane; usable geometry, PBR texture acceptable but slightly dark |
| `tree_v25_bud_d1_root_pruned` | 11.6MB | same geometry, root-guide material darker/less useful than spiky guide |
| `scifi_old_tight_d1_metal_pruned` | 23.3MB | strongest hard-surface geometry; automatic red texture is not paper-safe, material-override metal render is better |
| `arch_clean_key_d2_stone_pruned` | 24.4MB | readable architecture/portal geometry; automatic texture is too dirty/wood-like, material-override stone render is better |
| `crown_old_rim_d1_ornament_pruned` | 21.2MB | ornate crown/ornament appendix candidate; automatic green/gold texture is acceptable but not main-claim safe |
| `ornament_v24_rim_d1_ornament_raw` | 47.4MB | metric-clean but visually flat disk; appendix/diagnostic only |
| `crown_tapered_rim_d1_ornament_pruned` | 33.5MB | readable root-ball/ornament but vertical pole weakens semantics; appendix/diagnostic only |
| `scifi_clean_translate_d2_metal_pruned` | 15.4MB | backup hard-surface diagnostic; weaker than old scifi |
| `snow_arch_key_d1_stone_pruned` | 24.8MB | topology stable but not clean arch/city semantics; diagnostic only |

Metric caveat:

- GLB raw face-component counts are extremely fragmented because the exported textured mesh is split across many material/texture islands. Do not use raw face components from textured GLBs as the topology proof.
- Occupancy connectivity remains consistent with source OBJ evidence and is the primary QA signal for these GLBs. Key values from `textured_glb_metrics_all_20260510f.csv`:
  - `tree_v25_bud_d1_spiky_pruned`: occ LCR `0.9930`;
  - `scifi_old_tight_d1_metal_pruned`: occ LCR `0.9952`;
  - `arch_clean_key_d2_stone_pruned`: occ LCR `0.9984`;
  - `crown_old_rim_d1_ornament_pruned`: occ LCR `0.9997`;
  - `ornament_v24_rim_d1_ornament_raw`: occ LCR `1.0`.

Current figure recommendation:

- For main paper or high-visibility gallery, use geometry from `tree_v25_bud_d1_spiky_pruned`, `scifi_old_tight_d1_metal_pruned`, and `arch_clean_key_d2_stone_pruned`, but render with controlled Blender materials/lighting rather than the raw automatic TRELLIS2 texture if the raw texture looks too dark/red/dirty.
- Use `crown_old_rim_d1_ornament_pruned` as an appendix or ornament-breadth candidate unless a stronger crown/ornament case appears.
- Keep `ornament_v24`, `crown_tapered`, `scifi_clean`, and `snow_arch` diagnostic/appendix only.
- Do not use `tree_flipz` or `island_city` as positives.
