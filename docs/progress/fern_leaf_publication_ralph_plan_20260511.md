# Fern / Spider-Plant Recursive Asset Ralph Plan

Date: 2026-05-11 CST  
Status: active  
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU policy: use only GPUs `4,5,6,7`  
Storage cap: `200GB`; current remote project size after 20260511b pull is about `111GB`.

## 1. User Objective

Produce a publication-grade recursive botanical case, preferably fern / spider-plant / recursively branching root-vine, with:

- a high-quality root mesh chosen before grammar design;
- multi-depth outputs where every displayed depth is visually strong;
- clear semantic differences across depths;
- grammar behavior analogous to tree-crown growth: local recursive leaflets/fronds grow from credible anchors, not random global duplication;
- minimal mesh breakage, or breakage small enough to justify a documented naturalization/postprocess pass;
- final evidence from remote TRELLIS2 SLat recursion on `a100-2`, not local procedural stand-ins.

The user-provided visual references are:

- a compound fern frond image: many leaflets along branching stems;
- a fiddlehead/crozier fern image: curled recursive spiral with nested leaves.

Additional public reference images prepared locally:

- `downloads/fern_spider_sources_20260511/spider_plant_commons_pd_condition_1024.png`  
  Source: Wikimedia Commons `Chlorophytum comosum.png`, public domain.
- `downloads/fern_spider_sources_20260511/fiddlehead_golden_spiral_ccby4_condition_1024.png`  
  Source: Wikimedia Commons `Golden spiral in a fiddlehead fern.jpg`, CC BY 4.0.
- `downloads/fern_spider_sources_20260511/koru_unfurling_ccby25_condition_1024.png`  
  Source: Wikimedia Commons `Koru Unfurling.JPG`, CC BY 2.5.
- `downloads/fern_spider_sources_20260511/new_fern_fronds_ccby2_condition_1024.png`  
  Source: Wikimedia Commons `New Fern fronds (3672804706).jpg`, CC BY 2.0.

Manifest: `downloads/fern_spider_sources_20260511/manifest_fern_spider_sources_20260511.json`.

## 2. Why 20260511 / 20260511b Failed

The fifth hero plant case is visually nice as a presentation asset, but the root is not ideal for recursive proof:

- `plant_leaf_with_base` is a root-stamped / presentation GLB, not a clean isolated recursive root.
- The extracted `green_cluster` omits basal/root emergence semantics.
- The extracted `base_mid` keeps more semantics but has thin overlapping surfaces and many pre-existing components.
- `leaf_basal_fan_attach` copied too much of the thin leaf cluster and produced detached sheets.
- `leaf_basal_handle_attach` narrowed the copy, but the decoded thin sector still fragmented badly at depth 1+.

Measured 20260511b result:

- remote output: `results/plant_leaf_recursive_remote_20260511b`
- local mirror: `results/plant_leaf_recursive_remote_20260511b_pull`
- 22 OBJ/preview outputs, all real remote SLat runs.
- `leaf_green_handle_zpos` depth-1 LCR drops to about `0.815`; depth-3 to about `0.607`.
- `leaf_basemid_handle_zpos` depth-1 LCR about `0.833`; deeper rows continue degrading.

Decision: 20260511b is a negative diagnostic. It should not be used in the paper or hero figure except as an internal failure explanation.

## 3. New Strategy

The next loop prioritizes root quality before grammar:

1. Search or generate multiple root families:
   - real or generated fern frond root;
   - real or generated fiddlehead / spiral fern root;
   - spider-plant / chlorophytum rosette root if a license-compatible GLB or direct image-to-3D root can be obtained;
   - existing strong local roots such as `V25_sc_tree_crown_leafshield_B`, `V22/V25 bush/leafshield`, and root/vine candidates, but only if they read botanically.
2. For each root, run fast depth-0 import/encode/decode QA first.
3. Only roots with clean depth-0 decode and good visual semantics enter multi-depth grammar sweeps.
4. Use grammar families that preserve fern semantics:
   - `crown_bud_attach` / `crown_micro_fork_attach` for conservative crown-like growth;
   - a new `fern_frond_tip_attach` for leaflets growing along terminal/tip stems;
   - a new `fern_spiral_echo_attach` for fiddlehead-like nested curl / scaled echo;
   - existing `leaf_basal_micro_attach` only as a low-risk basal diagnostic;
   - avoid full-cluster fan copying unless used as a negative control.
5. Select candidates by both metrics and visual QA:
   - every depth 0..D has a nonbroken render;
   - depth differences are visible at object scale and in zoom;
   - occupancy LCR should preferably stay above `0.95`; if lower, visual fragments must be negligible and documented;
   - final candidate must have white-background Blender QA and, if promoted, GLB/PBR or controlled material render.

## 4. Immediate Work Packages

### A. Root Acquisition

- Search the local project for existing leaf/crown/root GLBs/OBJs and rank by depth-0 decode cleanliness.
- Search web for direct-download, license-compatible fern/spider-plant/rosette GLB/OBJ/ZIP assets.
- Search web image results for clean fern/frond/fiddlehead/spider-plant images; use top references as TRELLIS2 image-conditioned root candidates if the repo pipeline supports it.
- If direct web assets are not reliable, use the provided reference images and/or public guide images to generate candidate roots through the existing TRELLIS2 image-entry path.

### B. Candidate Root Pool

At least 8-12 candidate root meshes should be assembled before deep recursion:

- fern frond root candidates, 3-4;
- fiddlehead / spiral fern candidates, 2-3;
- spider-plant / rosette candidates, 2-3;
- existing project botanical roots, 2-3.

Each root gets a manifest row with path, source/license/provenance, mesh stats, depth-0 decode status, and visual notes.

### C. Remote Parallel Grammar Sweep

Use GPUs 4-7 in four lanes:

- lane 4: best fern-frond roots with conservative crown/tip grammars;
- lane 5: fiddlehead / spiral roots with scale/echo grammars;
- lane 6: rosette/spider-plant roots with basal/crown grammars;
- lane 7: existing project botanical roots as control and fallback.

Start with depths `0..2`; only extend to depth 3 or 4 if depth 2 is visually strong.

### D. Postprocess / Naturalization

Postprocess is allowed only after a candidate has valid recursive semantics:

- conservative small-island pruning;
- smoothing / weighted normals;
- texture/material override;
- optional voxel close/open/naturalization if it does not erase the recursive structure.

Postprocess must have before/after metrics and render QA; it cannot rescue a semantically failed grammar.

## 5. Acceptance Gates

A botanical recursive case is publication-grade only if all are true:

1. root provenance is documented and acceptable;
2. root depth-0 decode is visually clean;
3. multi-depth outputs show meaningful recursive growth, not just scale/noise drift;
4. all selected depths have OBJ/GLB outputs;
5. metrics CSV includes components, occupancy LCR, face/vertex counts, and file size where relevant;
6. Blender QA renders are clean on white background;
7. if used in hero/main figure, final material/render is controlled and bright enough;
8. any postprocess has a manifest and does not hide a failed grammar.

## 6. Current Next Commands

1. Build scripts for:
   - root candidate acquisition/manifest;
   - new fern-specific sparse-latent operators;
   - 4-lane root image generation sweep `results/fern_root_image_generation_remote_20260511c`;
   - 4-lane recursive grammar sweep `results/fern_leaf_recursive_remote_20260511c`.
2. Run the sweep on `a100-2` GPUs `4,5,6,7`.
3. Pull selected outputs and render QA.
4. Update this document with pass/fail and promoted candidates.

## 7. Live Log

### 2026-05-11 04:45 CST

- Added fern-specific sparse-latent grammar operators to `assets/trellis2_recursive_slat_grammar_workflow.py`:
  - `fern_frond_tip_attach`
  - `fern_frond_pinnae_attach`
  - `fern_spiral_echo_attach`
  - `fern_recursive_frond_attach`
- Added root image-generation launcher: `assets/run_fern_root_image_generation_remote_20260511c.sh`.
- Local syntax checks passed:
  - `python3 -m py_compile assets/trellis2_recursive_slat_grammar_workflow.py`
  - `bash -n assets/run_fern_root_image_generation_remote_20260511c.sh`
- Stage-1 plan: use TRELLIS2 image-conditioned generation to produce 8 root candidates from the four public reference images; evaluate root quality before deeper recursion.

### 2026-05-11 05:20 CST

- Remote stage-1 `results/fern_root_image_generation_remote_20260511c` launched successfully on `a100-2` GPUs `4,5,6,7`.
- Four raw image-conditioned TRELLIS2 root candidates completed:
  - `spider_plant_commons_pd_steps14_seed202605805_raw`: 152063 vertices, 302506 faces, 672 SLat tokens.
  - `koru_unfurling_ccby25_steps14_seed202605808_raw`: 333824 vertices, 667644 faces, 1408 SLat tokens.
  - `new_fern_fronds_ccby2_steps14_seed202605806_raw`: 1566728 vertices, 3133452 faces, 5768 SLat tokens.
  - `fiddlehead_golden_spiral_ccby4_steps14_seed202605807_raw`: 1566728 vertices, 3133452 faces, 5768 SLat tokens.
- The four `preprocess` runs failed before sampling with `IndexError('index 3 is out of bounds for axis 2 with size 3')`. Cause: NoOp rembg leaves RGB images unchanged while TRELLIS2 `preprocess_image` expects an alpha channel. Local script fix: convert input images to RGBA when `--preprocess` is set in `assets/trellis2_dinov3_official_min_smoke.py`.
- Added six local procedural root candidates from Copernicus under `results/fern_root_candidates_20260511/`. These are only root candidates / fallback probes, not final evidence. They are clean single-component meshes and can be used to test root-first grammar behavior if image-conditioned roots remain semantically weak.
- Current next gate: run metrics and white-background preview for the four raw remote roots, rerun the four fixed preprocess roots, and promote only visually clean roots into a depth-0/1/2 recursive grammar sweep. Large 3M-face roots must be simplified or decoded through a smaller root path before deep recursion.

### 2026-05-11 05:30 CST

- Raw root metrics completed for `20260511c`: all four raw roots are occupancy-connected. `spider_plant_commons_pd_steps14_seed202605805_raw` and `koru_unfurling_ccby25_steps14_seed202605808_raw` are the most practical immediate recursion roots because they are lighter than the 3M-face frond/fiddlehead roots.
- `preprocess` retry still failed with the same RGB/alpha error. The deeper cause is that the official pipeline's preprocess path calls the configured rembg/preprocess code in a way that still emits an RGB array before alpha indexing. Updated local `NoOpRembg.__call__` to force RGBA as a follow-up fix, but this is no longer a blocker because raw roots exist and are connected.
- Added `assets/run_fern_leaf_recursive_remote_20260511d.sh` for the first root-first recursive sweep:
  - lane 4: raw TRELLIS2 spider-plant image root with basal handle/crown grammars.
  - lane 5: raw TRELLIS2 koru/fiddlehead image root with spiral/frond grammars.
  - lane 6: strong V25 root-fan with basal handle/frond grammars.
  - lane 7: strong V22 vine runner with crown/frond grammars.
  - follow-up lanes: V24 root-network and V25 SC crown if first four lanes complete cleanly.
- Selection rule: first accept only depth `0..2` outputs with clear multi-depth visual difference, clean white renders, and metrics CSV. Do not use the 3M-face raw frond/fiddlehead roots for deep recursion until simplified or visually proven worth the cost.

### 2026-05-11 06:35 CST

- 20260511d remote sweep completed and was pulled locally under `results/fern_leaf_recursive_remote_20260511d_pull`.
- Visual/metric verdict:
  - raw TRELLIS2 image roots (`spider`, `koru`) are connected but nearly flat, so they are negative diagnostics / conditioning-root failures rather than positive recursive botanical cases.
  - `V25_sc_tree_crown_tapered_B` is the strongest 3D root geometry, but the old `crown_micro_fork_attach` produces long parallel rod artifacts; the issue is grammar semantics rather than runtime.
  - `V24_sc_root_network_260_anchorA_seedA` reads naturally as a root/rhizome mass but accumulates many small fragments at depth 2.
  - `V25_lsys_root_fan_dense_anchorD_stable` remains a stable fallback, with good nonflat geometry but more root-fan than spider plant.
- Added 20260511e grammar wrappers to `assets/trellis2_recursive_slat_grammar_workflow.py`:
  - `crown_bud_micro_20260511e`
  - `crown_scatter_micro_fork_20260511e`
  - `rim_leaflet_micro_20260511e`
  - `tiplet_short_20260511e`
  - `basal_micro_short_20260511e`
- Added 20260511e grammar aliases:
  - `v25e_crown_bud_micro`
  - `v25e_crown_scatter_fork`
  - `v25e_rim_leaflet_micro`
  - `v25e_crown_tiplet_short`
  - `v25e_root_basal_micro`
  - `v25e_root_rim_tiplet`
  - `v25e_root_crown_micro`
- Added launcher `assets/run_fern_leaf_recursive_remote_20260511e.sh`.
- 20260511e plan:
  - lane GPU5: `V25_sc_tree_crown_tapered_B`, depths 0..3, short crown/rim/tiplet grammars.
  - lane GPU6: `V25_sc_tree_crown_leafshield_B`, depths 0..3, same grammars for more visual crown cover.
  - lane GPU7: `V25_lsys_root_fan_dense_anchorD_stable`, depths 0..3, basal/rim micro growth.
  - lane GPU4: `V24_sc_root_network_260_anchorA_seedA`, depths 0..2, short local buds.
  - optional lane GPU6 after slot frees: `V22_lsys_climbing_vine_d6_smooth_leaf_tendrils`, depths 0..3, light runner fallback.
- Claim gate for promoting a 20260511e result:
  - depth 0, 1, 2 must all be visually usable;
  - depth 2 must show clear local recursive growth without long rods;
  - occupancy LCR target >= 0.95, with fragments visually negligible if lower;
  - Blender white-background QA and selected OBJ/GLB pull required before paper use.

### 2026-05-11 06:58 CST

- 20260511e remote sweep completed successfully:
  - remote output: `results/fern_leaf_recursive_remote_20260511e`
  - local mirror: `results/fern_leaf_recursive_remote_20260511e_pull`
  - outputs: 53 OBJ/preview rows, full metrics CSV/JSON.
- 20260511e verdict:
  - `v25e_rim_leaflet_micro` preserved connectivity very well, e.g. tapered/leafshield depth 2-3 occupancy LCR about `0.999`, but the visible depth difference is too weak for a main figure.
  - `v25e_crown_bud_micro` is stable enough, but the visual root still contains a protruding rod/handle, so it does not solve the core semantic problem.
  - `v25e_crown_scatter_fork` and `v25e_crown_tiplet_short` create clearer depth differences, but they reintroduce rod-like parallel structures and drop LCR for V25SC, so they are not paper-grade.
  - `V25_rootfan` is connected and leaf-bundle-like, but the multi-depth change is too subtle and still reads as a single handle/fan rather than a natural recursive plant.
  - `V24_rootnet` remains the most natural as a rhizome/root mass, but it does not satisfy the user-requested leaf/spider/fern recursive case by itself.
- Main lesson: 20260511e confirms the problem is not just operator magnitude. The root and anchor/orientation must be chosen so the recursive growth starts from a meaningful biological handle. Patching V25SC with shorter deltas cannot make it a publication-grade plant case.
- Web/source scout started:
  - promising external references/assets found: Pixabay fern GLB, Sketchfab CC0 spear-leaf fern, Sketchfab CC-BY spider plant, Kenney/Eclair CC0 nature GLB kit, CG3D public-domain/CC0 model catalog.
  - These need license/download verification before use as final root provenance.
- 20260511f plan: switch to clean root-candidate pool and explicitly sweep axis/sign.
  - Use `results/fern_root_candidates_20260511/` roots: `fern_compound_frond_arch_a`, `fern_compound_frond_lacy_b`, `spider_rosette_strapleaf_a`, `fiddlehead_crozier_open_a`, and optional `root_vine_fallback_web_a`.
  - For fern/frond/fiddlehead roots, primary growth direction is latent `y, sign=-1` because the workflow maps original OBJ `z` to latent `-y`.
  - Run on remote `a100-2` GPUs 4,5,6,7 with depths 0..3, then pull metrics/previews and judge before any Blender render.
  - Promotion gate remains strict: clear root semantics, visible multi-depth difference, no major rod artifact, LCR preferably >= 0.95, and white-background Blender QA before paper use.
