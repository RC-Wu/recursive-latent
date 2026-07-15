# Plant Leaf / Spider-Plant Recursive Remote Loop 20260511

Status: active
Created: 2026-05-11 CST
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
GPU policy: use only GPUs `4,5,6,7`
SSH policy for this user request: at most 2 SSH shells

## User Request

The user noted that hero cases 4/5 look visually promising and asked to turn the fifth `plant_leaf_with_base` case into real recursive evidence: use its leaf/plant mesh as the root mesh, run our own recursive SLat/TRELLIS2 method remotely, try different depths, and judge visual naturalness rather than connectivity alone. The user also asked to search for a spider plant / 吊兰 GLB and, if found, run the same method quickly.

## Source Asset Provenance

The current fifth hero asset is not yet a true recursive-depth proof. It is a presentation/root-stamped botanical variant:

- Hero manifest case: `plant_leaf_with_base`
- Current presentation GLB: `visuals/hero_botanical_variants_20260510/vine_stage5_parthenocissus_warm_upright_green_leaf_brown_base.glb`
- Source family: `vine_d5_projected_compete` / `vine_stage5_parthenocissus_warm`
- Earlier root-stamped proxy: `visuals/strict_matched_root_stamped_20260510/lsys_climbing_vine_d6__rootstamped_vine_stage5/root_stamped_candidate.glb`

Interpretation: good visual plant/vine asset, but not enough to claim that the fifth hero case itself has per-depth SLat recursion. This loop is intended to close that gap.

## Root Mesh Inputs Prepared Locally

Created under `results/plant_leaf_recursive_root_20260511/inputs/`:

1. `plant_leaf_full_upright_root.obj` / `.glb`
   - all three presentation geometry splits
   - 651144 vertices, 455964 faces
   - purpose: whole plant/root as root input
2. `plant_leaf_green_cluster_root.obj` / `.glb`
   - upper green leaf-cluster geometry only
   - 204028 vertices, 151683 faces
   - purpose: leaf-root recursion without low brown base bulk
3. `plant_leaf_base_mid_cluster_root.obj` / `.glb`
   - middle+upper geometry
   - 397415 vertices, 289140 faces
   - purpose: retain emergence-from-base semantics while avoiding full pedestal/brown root mass

Local simplification attempt was blocked because local `trimesh.simplify_quadric_decimation` requires `fast_simplification`, which is absent. The first remote sweep uses the raw exported OBJ roots; if encoding is slow, the next step is Blender decimate or remote simplification.

## Initial Remote Sweep Design

Run real `assets/trellis2_recursive_slat_grammar_workflow.py` on a100-2, not local procedural geometry.

Initial matrix:

- Roots:
  - `plant_leaf_green_cluster_root`
  - `plant_leaf_base_mid_cluster_root`
  - optionally `plant_leaf_full_upright_root` if the first two run cleanly
- Grammars:
  - `crown_bud_attach`: conservative upward local leaf/bud growth
  - `crown_micro_fork_attach`: small forked leaf/tendril growth
  - `fork_side_attach`: stronger branching, likely higher failure risk
- Depths: 0-3 for fast visual inspection
- Growth frames to test first:
  - `growth-axis=y`, `growth-sign=1` for the presentation root's upright coordinate
  - backup: `growth-axis=z`, `growth-sign=1` if preview shows wrong growth side after workflow y/z remap
- Fit scales: start `0.62` or `0.68`; reduce if token count/decoder instability occurs
- Max tokens: 20000 for first two roots, less for full root if needed

Acceptance gate before calling any result successful:

1. remote summary JSON records status and token counts;
2. OBJ and preview PNG exist for depths;
3. selected cases pass metrics using occupancy LCR and component counts;
4. local/remote Blender render QA shows readable botanical structure and recursive state;
5. if used for paper, GLB/textured or controlled material render is produced with manifest.

## Spider Plant / 吊兰 Asset Search

Local project search found no existing file named `spider`, `chlorophytum`, or `吊兰`. Web search found Sketchfab spider-plant model pages, but direct API download requires authentication. Therefore spider-plant acquisition is not yet closed.

If a license-compatible direct `.glb` or `.zip` download is found, place it under:

- `downloads/spider_plant_sources_20260511/`
- converted root inputs under `results/plant_leaf_recursive_root_20260511/spider_inputs/`

and then run the same remote sweep. Until that happens, the current fifth hero plant/vine asset is the closest spider-plant-like root because leaves emerge from a central base.

## Live Log

### 2026-05-11 03:47 CST

- Re-read `ralph_publication_closure_plan_20260510.md` and `remote_repair_loop_20260510b.md`.
- Confirmed remote a100-2 GPUs 4/5/6/7 were idle and project size was about `95G`, under the user-relaxed `200GB` cap.
- Confirmed fifth hero asset provenance and presentation/proxy caveat.
- Exported three root meshes from the current fifth hero botanical variant.
- Created this progress note as the recovery target for this plant-leaf subloop.


### 2026-05-11 04:12 CST

Remote execution update:

- Added two leaf-specific sparse-latent operators to `assets/trellis2_recursive_slat_grammar_workflow.py`:
  - `leaf_basal_fan_attach`: copies a leaf cluster from a low central basal anchor with bridge tokens;
  - `leaf_basal_micro_attach`: copies only small basal bud/frontier tokens.
- Synchronized the workflow and launcher to `a100-2` and ran real remote TRELLIS2 SLat encode/rewrite/decode on GPUs `4,5,6,7`.
- Completed fifth-case root sweeps:
  - `leaf_basemid_basal_fan_zpos`: base+upper leaf root, `leaf_basal_fan_attach` and `leaf_basal_micro_attach`, depths 0-3;
  - `leaf_basemid_fork_side_zpos`: base+upper leaf root, `fork_side_attach` and `crown_micro_fork_attach`, depths 0-2;
  - `leaf_green_basal_fan_zpos`: green leaf-cluster only, `leaf_basal_fan_attach` and `leaf_basal_micro_attach`, depths 0-3;
  - `leaf_green_crown_micro_zpos`: green leaf-cluster only, `crown_bud_attach` and `crown_micro_fork_attach`, depths 0-3.
- Completed fallback external plant smoke:
  - `poly_small_plant_leaf_basal_smoke`, from Poly Pizza `Small Plant` CC0, used only as an external plant-root smoke, not as a spider-plant/吊兰 claim.
- Remote status: all lanes exited `status=ok`; latest status reported `42` OBJ outputs and `42` preview PNGs, with GPUs 4-7 idle afterwards.

Pulled local QA:

- Preview/contact sheet: `results/plant_leaf_recursive_remote_20260511_pull/plant_leaf_recursive_preview_contact_sheet_20260511.png`
- Selected Blender white renders: `results/plant_leaf_recursive_remote_20260511_pull/blender_selected_white/selected_blender_contact_sheet_white.png`
- Selected local OBJs: `results/plant_leaf_recursive_remote_20260511_pull/selected_meshes/`
- Metrics CSV/JSON: `results/plant_leaf_recursive_remote_20260511_pull/metrics/plant_leaf_recursive_metrics_20260511.csv` / `.json` (first run covers base-mid and Poly small plant; green metrics were started after green lanes completed and should be refreshed/pulled for final table).

Metric snapshot for fifth-case base-mid rows from the first completed CSV:

| label | V/F | occ comps | occ LCR |
| --- | ---: | ---: | ---: |
| `leaf_basemid_fork_side_zpos__crown_micro_fork_attach__depth_01` | 212677/484710 | 20 | 0.9044 |
| `leaf_basemid_fork_side_zpos__crown_micro_fork_attach__depth_00` | 188909/436952 | 10 | 0.8944 |
| `leaf_basemid_fork_side_zpos__fork_side_attach__depth_00` | 188909/436952 | 10 | 0.8944 |
| `leaf_basemid_basal_fan_zpos__leaf_basal_fan_attach__depth_00` | 203076/467236 | 11 | 0.8829 |
| `leaf_basemid_basal_fan_zpos__leaf_basal_micro_attach__depth_00` | 203076/467236 | 11 | 0.8829 |
| `leaf_basemid_basal_fan_zpos__leaf_basal_micro_attach__depth_01` | 199064/436096 | 43 | 0.8806 |

Visual QA interpretation:

- Current result is a real remote SLat recursive run, not a local procedural proxy and not the previous root-stamped presentation asset.
- It is **not yet publication-grade**. Blender renders show many detached/fragmented thin leaf pieces, especially for `leaf_basal_fan_attach`; deeper fan depths visibly degrade into dust/tears.
- `leaf_basal_micro_attach` is more stable and preserves the plant silhouette better, but the recursive state is subtle.
- `leaf_green_crown_micro_zpos/crown_bud_attach/depth_02` is the cleanest-looking selected render among pulled candidates, but it lacks enough base/root emergence semantics to be a strong paper case by itself.
- `leaf_basemid_fork_side_zpos/crown_micro_fork_attach/depth_01` has the best first-pass occupancy LCR among base-mid rows (`~0.9044`) and visibly adds a top cluster, but still contains floating fragments and should not be called final.

Spider-plant / 吊兰 search status:

- Local project search found no existing `spider`, `chlorophytum`, or `吊兰` mesh.
- Sketchfab pages exist but direct download API requires authentication, so no reproducible spider-plant GLB was obtained in this pass.
- Poly Pizza search did not yield a true spider plant; it yielded a CC0 `Small Plant` (`https://poly.pizza/m/MZdeiQApSb`) with direct static GLB. This was downloaded and run as a smoke only.

Next repair direction:

- Do not continue with full leaf-cluster copy as the main operator; it copies too much thin geometry and creates detached strips.
- Implement a stricter basal operator that selects only low central petiole/root-handle tokens plus a narrow leaf-tip mask, then grows 2-4 attached child blades instead of duplicating the entire leaf cluster.
- Add component-pruning before Blender/material renders for candidate rows, but do not use pruning to hide a semantically failed growth operator.
- For a publishable plant case, prefer a root with clear petiole/base handles or a true spider-plant/chlorophytum GLB if a license-compatible direct source is obtained.


### 2026-05-11 04:18 CST

Refreshed complete metrics after the green-cluster lanes finished and pulled the updated CSV/JSON locally. The refreshed table has `42` rows, including all fifth-case green/base-mid outputs plus the external Poly Pizza small-plant smoke.


Top green-cluster metrics:
| label | V/F | occ comps | occ LCR |
| --- | ---: | ---: | ---: |
| `leaf_green_crown_micro_zpos__crown_bud_attach__depth_02` | 179765/394096 | 6 | 0.9487 |
| `leaf_green_crown_micro_zpos__crown_micro_fork_attach__depth_01` | 202206/439960 | 7 | 0.9483 |
| `leaf_green_crown_micro_zpos__crown_bud_attach__depth_01` | 177724/392054 | 8 | 0.9481 |
| `leaf_green_crown_micro_zpos__crown_bud_attach__depth_03` | 182490/398584 | 7 | 0.9469 |
| `leaf_green_basal_fan_zpos__leaf_basal_fan_attach__depth_00` | 170023/371082 | 6 | 0.9455 |

Top base-mid metrics:
| label | V/F | occ comps | occ LCR |
| --- | ---: | ---: | ---: |
| `leaf_basemid_fork_side_zpos__crown_micro_fork_attach__depth_01` | 212677/484710 | 20 | 0.9044 |
| `leaf_basemid_fork_side_zpos__crown_micro_fork_attach__depth_00` | 188909/436952 | 10 | 0.8944 |
| `leaf_basemid_fork_side_zpos__fork_side_attach__depth_00` | 188909/436952 | 10 | 0.8944 |
| `leaf_basemid_basal_fan_zpos__leaf_basal_fan_attach__depth_00` | 203076/467236 | 11 | 0.8829 |
| `leaf_basemid_basal_fan_zpos__leaf_basal_micro_attach__depth_00` | 203076/467236 | 11 | 0.8829 |

Updated interpretation:

- Green-cluster rows are numerically much cleaner than base-mid rows (`occ LCR` around `0.947-0.949` for the best crown/bud depths), but they are weaker semantic evidence because they omit the original base/root emergence region.
- Base-mid rows preserve the intended basal origin better, but current operators still fragment too much. The best base-mid metric row is `leaf_basemid_fork_side_zpos__crown_micro_fork_attach__depth_01` with `occ LCR=0.9044` and `20` occupancy components.
- The Poly Pizza small plant smoke has high metrics for fan depths, but it is low-poly and not a true spider plant. It should remain a workflow smoke/fallback, not a paper claim.
- Current publication gate remains **not passed** for the fifth-case recursive leaf experiment. The closest visual candidates are useful for diagnosing the next grammar change, not for the hero figure yet.


### 2026-05-11 next-loop plan: stricter basal-handle operator

To address the failure mode above, the workflow now includes a narrower sparse-latent plant operator in `assets/trellis2_recursive_slat_grammar_workflow.py`:

- `leaf_basal_handle_attach`: selects a low central basal/root handle plus one narrow radial leaf/petiole sector, rotates only that sector into a few child directions, and bridges only the basal handle tokens.
- `leaf_basal_handle_micro_attach`: applies the same handle/blade operator followed by the existing basal micro-bud operator.

Rationale: the previous `leaf_basal_fan_attach` copied too much thin leaf-cluster geometry, causing detached sheets after decode. The new operator tries to express the intended spider-plant/rosette semantics: several new blades should emerge from the same root crown rather than duplicating the whole plant beside itself.

Prepared launcher:

- `assets/run_plant_leaf_handle_remote_20260511b.sh`
- remote output target: `results/plant_leaf_recursive_remote_20260511b`
- planned lanes on GPUs `4,5,6,7` only:
  - `leaf_basemid_handle_zpos`: base+upper root, handle-only and handle+micro, depths 0-3;
  - `leaf_green_handle_zpos`: green leaf-cluster, handle-only and handle+micro, depths 0-3;
  - `leaf_basemid_handle_ypos`: axis-sensitivity diagnostic, depths 0-2;
  - `leaf_full_handle_zpos`: full presentation root smoke, depths 0-1.

Publication gate remains unchanged: this becomes usable only if the remote OBJ outputs, occupancy metrics, and Blender QA renders show both basal emergence semantics and visually acceptable natural plant structure. Otherwise it remains a negative/diagnostic repair attempt.


### 2026-05-11 09:58 CST: 20260511n confirms true-cut plant failure

The latest 20260511n remote-only SLat repair batch explicitly retested the true fifth-hero plant cuts:

- `plant_leaf_green_v25n_yneg_20260511n`
- `plant_leaf_basemid_v25n_yneg_20260511n`

with the newer basal/midrib operators:

- `v25n_plant_basal_midrib_leaflet`
- `v25n_plant_basal_crown_leaflets`

Evidence:

- Remote output: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/botanical_tree_root_recursive_remote_20260511n`.
- Local metrics/previews: `results/botanical_tree_root_recursive_remote_20260511n_pull/`.
- Blender QA: `results/botanical_tree_root_recursive_remote_20260511n_selected_meshes/blender_qa_20260511n/contact_sheet_20260511n_selected_blender_whitecomposite.png`.

Verdict:

- Both true-cut plant roots remain **rejected_fragmented**. Blender QA shows torn lamina sheets, floating strips, and no clean petiole/root emergence. The best green rows still sit near `PLCR~0.81`; base-mid rows fall near `PLCR~0.75`.
- This failure is no longer plausibly a lighting/material issue. It is a semantic root-selection and grammar issue: the source cuts contain too much thin sheet geometry and too little clean petiole/root handle geometry.
- Future plant-leaf attempts should switch root source: cleaner spider/rosette roots, CC0 Poly Haven plant/fern meshes, or a new manually exported single petiole/leaf module. Do not promote the existing green/base-mid true cuts as paper-positive evidence.
