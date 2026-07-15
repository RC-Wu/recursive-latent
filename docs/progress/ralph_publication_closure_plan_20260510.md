# R-SLG Publication-Grade Closure Ralph Plan

Date: 2026-05-10 15:13 CST  
Status: active long-running execution plan  
Project root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU policy: use only GPUs `4,5,6,7`  
SSH policy: at most 3 concurrent SSH shells; default this round is 1 persistent remote shell controlled by the main agent
Remote storage cap: relaxed to `200GB` by user on 2026-05-10 15:28 CST; still avoid stale caches and delete only clearly unused/rebuildable artifacts.

## 0. Recovery Contract

Read this file first after context compaction or heartbeat. Then read:

1. `docs/agent_handoff_2026-05-10.md`
2. `docs/obsidian_human_reports/2026-05-10_gen3d_ablation_round_closeout.md`
3. `docs/evaluation/gen3d_and_ablation_evidence_audit_zh_20260510_agent.md`
4. `docs/visuals/hero_multi_zoom_status_zh_20260510.md`
5. latest dated progress note under `docs/progress/`

The target is publication-grade SIGGRAPH/SIGGRAPH Asia evidence, not merely a working draft. Do not remove TODOs or write strong paper claims until matching evidence, metrics, and renders exist.

## 1. User Requirements Captured

### 1.1 Baseline Closure

Complete ordinary 3D generation baselines and trivial-recursion controls:

- TRELLIS non-2 / classic TRELLIS image-to-3D baseline must be made runnable if possible.
- Hunyuan3D 2.0 complete repo/package/weights must be installed or clearly proven blocked with exact logs.
- TRELLIS.2 existing baseline remains primary and must be extended to a complete case pool.
- Methods to compare:
  - TRELLIS image one-shot
  - TRELLIS.2 image one-shot
  - Hunyuan3D 2.0 image-to-3D and, if feasible, image+texture
  - TRELLIS.2 trivial latent-copy / direct sparse transform
  - TRELLIS.2 + mesh-space generated-root grammar
  - Hunyuan3D + mesh-space generated-root grammar when Hunyuan output exists
  - PS-RSLG / ours
- Each major category should have at least 10 selectable cases. The agent must recommend the subset that most clearly shows PS-RSLG's advantage.
- Baseline metrics must be complete enough for paper tables: vertices, faces, file size, raw/welded/occupancy components, LCR, root reachability where defined, orphan/fragment ratio, render import success, visual QA status, and per-case failure labels.

### 1.2 Hero / Head Figure Correction

The head figure should use five specific cases placed into one combined GLB and rendered together:

1. bismuth crystal, the pyramid/terraced case
2. pyrite crystal
3. coral
4. tree-root/tree-leaf case
5. plant-leaf case with a base

Required visual treatment:

- Put all five cases into a single `.glb`.
- Smooth the coral surface before final hero rendering if it remains too voxel/blocky.
- Current PBR renders are too dark; tune lighting and exposure.
- For the head figure only, use a light blue-gray seamless background plus a platform of the same family, without a visible horizon line.
- Add subtle shadow/contact grounding.
- Render overview and per-case local zoom-in panels.
- Try several lighting/camera settings and retain manifests so the final choice is reproducible.

### 1.3 Remaining P0/P1 Scientific Gaps

Continue until closed or explicitly blocked with evidence:

- coral mesh-space generated-root baseline is missing
- same-root matrix remains partial
- naturalization matrix remains partial
- effective-resolution / zoom-retention remains proxy-only
- DLA/crystal/non-tree fragmentation remains a risk
- appendix / main / supplement split is not final

## 2. Work Lanes

### Lane A: Remote Baseline Environment and Runs

Owner: main agent remote shell.  
Write scope:

- remote under `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
- local pulled results under `results/`, `visuals/`, `docs/remote_results/`

Tasks:

1. Check remote storage/GPU/process state.
2. Locate existing conda/envs/repo paths for TRELLIS, TRELLIS.2, Hunyuan.
3. If no Hunyuan install exists, clone/setup in a controlled remote subdir and set all caches under remote project root.
4. Use GPUs 4/5/6/7 only.
5. Prepare target/reference image set and run one-shot baselines.
6. Export GLB/OBJ and pull selected artifacts/metrics.

Acceptance:

- A manifest records repo commit/path, env, model cache, command, seed, inputs, outputs, status.
- Hunyuan is either runnable with at least shape output or blocked with exact failing command/log.
- TRELLIS non-2 is either runnable or blocked with exact env/import/weight reason.

### Lane B: Baseline Case Pool and Metrics

Owner: local worker/subagent, no SSH.  
Write scope:

- `assets/`
- `results/publication_baseline_metrics_20260510/`
- `docs/evaluation/`

Tasks:

1. Inspect existing case pools and assemble at least 10 candidate cases per category.
2. Define recommended comparison subset showing PS-RSLG advantage.
3. Implement or adapt selected-final-only metrics so it does not recursively scan huge directories.
4. Add metric aggregation for baseline one-shot, latent-copy, mesh-space, ours, Hunyuan/TRELLIS rows.
5. Produce CSV + LaTeX draft table + claim-gate document.

Acceptance:

- A single master CSV covers all methods/cases/statuses.
- Missing or blocked rows are explicit, not silently omitted.
- Main-paper recommendation includes only evidence-backed rows.

### Lane C: Hero Combo GLB and Rendering Pipeline

Owner: local worker/subagent, no SSH unless explicitly delegated later.  
Write scope:

- `assets/hero_combo_*.py`
- `visuals/hero_combo_publication_20260510/`
- `paper_siga/figures/`
- `docs/visuals/`

Tasks:

1. Resolve the exact five GLB assets and verify paths.
2. Build a combined GLB scene with transforms, scale normalization, base/platform, and metadata.
3. Smooth coral via controlled mesh smoothing/decimation/remesh that improves surface without destroying silhouette.
4. Render hero overview with brighter PBR, light blue-gray seamless background/platform, no horizon seam, subtle shadow.
5. Render per-case zoom-in panels from real cameras, not 2D crops.
6. Save lighting/camera/material manifest.

Acceptance:

- Combined GLB exists and imports in Blender.
- Overview render is bright enough, with no horizon seam and no text in image.
- Per-case zooms are saved and linked to original case assets.
- Render QA confirms image dimensions, corner/background colors, and nonblank pixels.

### Lane D: Ablations and Effective Resolution

Owner: local worker/subagent for scripts, main agent for any remote execution.  
Write scope:

- `assets/`
- `results/publication_ablation_metrics_20260510/`
- `paper_siga/drafts/`
- `docs/evaluation/`

Tasks:

1. Close coral mesh-space generated-root baseline.
2. Build same-root matrix:
   - traditional
   - direct
   - final-only
   - prune
   - bridge
   - proposed
3. Build naturalization matrix:
   - rule-only
   - no-N
   - weak blend
   - masked local-N
   - global-N
   - with projection
   - without projection
4. Build one-shot vs recursive refinement evidence:
   - local feature scale
   - terminal detail count
   - zoom retention
   - face/GLB size
   - full-object high-resolution blow-up estimate
5. Re-run DLA/crystal connectedness candidate search only if it targets fragmentation closure.

Acceptance:

- Each matrix row has a status: complete, blocked, failed, diagnostic, or excluded with reason.
- Main text can cite a closed subset; appendix can cite full matrix.

### Lane E: Paper Integration

Owner: main agent after data arrives.  
Write scope:

- `paper_siga/main.tex`
- `paper_siga/drafts/`
- `docs/paper/`

Tasks:

1. Keep main paper claim-bearing and concise.
2. Rewrite/merge experimental sections after evidence arrives.
3. Move broad diagnostic galleries and partial matrices to appendix/supplement.
4. Add appendix index / main-vs-supplement figure table.
5. Compile PDF and record warnings.

Acceptance:

- No unsupported claim remains.
- Any `EvidencePending` or `ExpFigTODO` left in the paper has a reason and plan.
- PDF compiles.

## 3. First Execution Order

1. Create/update this plan and heartbeat.
2. Spawn local subagents:
   - metrics/case-pool worker
   - hero-combo worker
   - ablation/effective-resolution worker
3. Open one persistent SSH shell to `a100-2`; audit env/storage/GPU.
4. In parallel, local workers prepare scripts/manifests.
5. Start remote repo/weight setup only after cache/env paths are known.
6. Start the smallest smoke for TRELLIS non-2 and Hunyuan before large batches.
7. Start final hero combo path locally while remote baselines run.

## 4. Live Progress Log

### 2026-05-10 15:13 CST

- User requested a new Ralph loop with subagents and heartbeat.
- This plan was created as the recovery target.
- Heartbeat `r-slg-long-task-heartbeat` was updated to point to this plan.
- Current known status before new execution:
  - TRELLIS.2 baseline evidence exists.
  - TRELLIS non-2 and Hunyuan3D are not completed baselines.
  - coral mesh-space generated-root is missing.
  - same-root/naturalization/effective-resolution remain partial.
  - existing hero is a multi-zoom draft, not the requested five-case combined GLB.

### 2026-05-10 15:28 CST

- User relaxed remote storage cap to `200GB`.
- Operational decision: proceed with TRELLIS/Hunyuan repo and weight setup under the remote project root, but keep cache hygiene:
  - preserve weights, results, GLBs/OBJs, manifests, metrics, and logs;
  - remove only interrupted partial clones, stale temporary directories, and rebuildable caches when needed;
  - continue recording exact commands/logs for any blocked baseline.

### 2026-05-10 15:42-16:02 CST

- Re-read the handoff, closeout report, evidence audit, hero status, AgentDoc project entry, and local Codex history for thread `[R-SLG]continue`.
- Important recovered history from the Codex thread `019dfe99-7647-75d0-a741-c029c218f66a`:
  - the original project scope was Trellis2 capability testing on `a100-2`, local traditional baselines, visual pullback, and research documentation;
  - the older thread established that the Trellis2 package is `trellis2`, not `trellis`;
  - the previous round later paused and deleted an old heartbeat at the user's request. The current heartbeat is a new continuation request.
- Local subagents returned read-only/sidecar results:
  - baseline/case-pool metrics: 70 candidate rows, 25-row master manifest; TRELLIS non-2 and Hunyuan rows still blocked/missing.
  - ablation/effective-resolution aggregation: same-root 127 rows, naturalization 230 rows, effective-resolution 32 rows; still partial/status evidence.
  - paper review: appendix is on a new page but has no formal table of contents; 4.7 is claim-gated rather than closed; 4.9/4.10 are not fully merged/slimmed.
  - hero/case review: five-case combined GLB and camera zooms exist, but plant/base semantics are weak and earlier renders were too dark or had platform seams.
- Remote state:
  - Project size is about `79G`, below the updated `200GB` cap.
  - `repos/TRELLIS.zip` is valid and extracted to `repos/TRELLIS`.
  - Initial `repos/Hunyuan3D-2.zip` from codeload timed out (`CURL_STATUS 124`) and failed `zipfile` validation (`BadZipFile`). It was moved to `repos/Hunyuan3D-2.zip.bad`.
  - A second Hunyuan GitHub archive retry was started with Python `urllib`; it reached at least `20MB` by 16:00 CST but had not yet completed.
- TRELLIS classic / non-2 current blocker:
  - `torch` and `trimesh` import in the existing Trellis2 env.
  - `trellis.models` imports.
  - `trellis`, `trellis.pipelines`, and `trellis.representations` initially fail on `RuntimeError operator torchvision::nms does not exist`.
  - Defining a temporary `torchvision::nms` stub moves the blocker forward to `ModuleNotFoundError: No module named 'rembg'`.
  - Therefore TRELLIS non-2 is not yet a completed baseline; it is a repo+partial-import state with dependency/environment blockers.
- Hero render state:
  - `scripts/figures/hero_combo_publication_20260510.py` now uses a lighter blue-gray palette, Standard color management, stronger softbox lighting, emissive platform material, and an infinite plane platform instead of a cube stage.
  - `visuals/hero_combo_publication_20260510_plane_480/` completed: overview + five camera zoom PNGs + manifest + combined GLB.
  - 480px overview QA: mean RGB approximately `(231.2, 232.5, 231.2)`, corners range from about `(166,170,171)` to `(223,229,230)`, with no dark diagonal platform edge.
  - `--skip-glb-export` was added to avoid writing another 1GB combined GLB during higher-resolution render passes.
  - A 900px Cycles candidate render was started in `visuals/hero_combo_publication_20260510_plane_900/` using `--skip-glb-export`.
- Current claim gates remain:
  - Hunyuan baseline is still not runnable.
  - TRELLIS non-2 is not runnable until dependencies are fixed.
  - coral mesh-space generated-root baseline remains missing.
  - same-root/naturalization/effective-resolution remain partial or diagnostic, not closed quantitative proof.

### 2026-05-10 16:05-16:37 CST

- Heartbeat `r-slg-long-task-heartbeat` was updated to a 20-minute thread heartbeat with the latest constraints:
  - remote storage cap `200GB`;
  - use GPUs `4,5,6,7`;
  - continue TRELLIS classic and Hunyuan3D baselines;
  - keep five-case hero requirements explicit.
- Reused and then closed the existing local subagents to avoid the thread-limit problem. New local sidecar results:
  - Coral mesh-space generated-root baseline was closed locally:
    - script: `assets/coral_mesh_space_generated_root_20260510.py`;
    - results: `results/publication_coral_mesh_space_20260510/`;
    - status doc: `docs/evaluation/coral_mesh_space_generated_root_status_zh_20260510.md`;
    - recommended table row: `coral_frontier_branch full_srt depth=2 direct merge`;
    - metrics: `754194` vertices, `252000` faces, `31.281 MB`, raw face components `250404`, occupancy 6N components `8`, LCR `0.9918`, `21` copied instances.
    - claim gate: this is a mesh-space direct copy-paste negative control, but not a simple low-LCR failure. Its evidence is the repeated-root construction, no projection/repair/union, and extreme raw face islands.
  - Same-root and naturalization gap queues were generated:
    - `docs/evaluation/ablation_matrix_gap_closure_queue_zh_20260510.md`;
    - `results/publication_ablation_metrics_20260510/ablation_gap_queue_20260510.csv`;
    - `results/publication_ablation_metrics_20260510/claim_safe_miniset_20260510.csv`.
    - main-safe subset remains narrow: vine/tree projection 3-column subsets, selected L-system local-N visual/export subset, and effective-resolution proxy table only.
  - Hero QA was written:
    - `docs/visuals/hero_combo_publication_QA_zh_20260510.md`;
    - `results/hero_combo_publication_QA_20260510/`.
- Hero rendering state:
  - `visuals/hero_combo_publication_20260510_plane_900/` completed: overview + five zooms + manifest, all camera renders, bright light blue-gray platform/background, no dark platform edge.
  - `plane_900` weakness: tree and plant zooms were too small/faint (`tree_root_leaf` colored foreground proxy about `0.0065`; `plant_leaf_with_base` about `0.0175` to `0.0277` depending metric).
  - `scripts/figures/hero_combo_publication_20260510.py` was updated to preserve the five requested cases but add hero-only botanical contrast and tighter zooms for tree/plant:
    - `tree_root_leaf`: scale boost `1.92`, `botanical_contrast=leaf_bark`, zoom scale `1.9`;
    - `plant_leaf_with_base`: scale boost `2.05`, `botanical_contrast=base_stem`, zoom scale `1.8`;
    - default spacing `2.72`, overview scale default `9.45`, zoom default `2.45`.
  - `visuals/hero_combo_publication_20260510_contrast_520/` smoke completed. It made tree/plant zooms readable but cropped the left bismuth in the overview, so it is not a final overview candidate.
  - `visuals/hero_combo_publication_20260510_contrast_wide_720/` completed and is the current recommended layout candidate:
    - overview is bright, full five-case, and no hard horizon;
    - tree zoom colored foreground proxy improved to about `0.223`;
    - plant zoom colored foreground proxy improved to about `0.095`;
    - residual risk: the fifth asset is still semantically a climbing-vine/leaf cluster on the shared platform, not a strongly self-contained pedestal/base plant.
  - A `1200px`, `72` sample Cycles pass was started at `visuals/hero_combo_publication_20260510_contrast_wide_1200/` with `--skip-glb-export`.
- Hunyuan3D remote state:
  - Python `urllib` retry completed: `repos/Hunyuan3D-2.zip` is `80.28 MB`.
  - Zip validation passed: `testzip() == None`, `270` archive entries, root `Hunyuan3D-2-main`.
  - Extracted to `repos/Hunyuan3D-2` with `269` files.
  - Requirements/setup confirmed package name `hy3dgen`, with missing runtime dependencies including `diffusers`, `accelerate`, `rembg`, `onnxruntime`, `pymeshlab`, `xatlas`, etc.
  - System Python has no ML stack. Existing Trellis2 env has `torch 2.10.0+cu128`, CUDA available, `transformers`, `trimesh`, and `pygltflib`, but lacks `diffusers`, `rembg`, `onnxruntime`, `pymeshlab`, `xatlas`, and `hy3dgen`.
  - To avoid polluting Trellis2, a probe venv was created under `envs/hy3d_trellisclassic_probe_20260510` using `--system-site-packages` from the Trellis2 env.
  - `pip install -e repos/Hunyuan3D-2 --no-deps` plus missing dependencies was started in the probe venv; logs:
    - `logs/baseline_env/probe_pip_bootstrap_20260510.log`;
    - `logs/baseline_env/hy3d_editable_nodeps_20260510.log`;
    - `logs/baseline_env/hy3d_missing_deps_20260510.log`.
- TRELLIS classic / non-2 status:
  - The existing env still has the `torchvision::nms` import incompatibility (`torchvision` import raises `RuntimeError operator torchvision::nms does not exist`).
  - TRELLIS classic remains repo+partial-import only until the probe env install finishes and the nms-stub + missing-dependency smoke is rerun.

### 2026-05-10 16:38-16:46 CST

- Started `visuals/hero_combo_publication_20260510_contrast_wide_1200/`:
  - command uses Cycles, `1200px`, `72` samples, exposure `0.35`, overview scale `10.6`, zoom default `2.45`, `--skip-glb-export`;
  - overview, bismuth, pyrite, coral, and tree zooms completed by 16:45 CST;
  - plant zoom was still rendering at the time of this note.
- Remote dependency install status:
  - probe venv install is still running in the persistent SSH shell;
  - a read-only SSH probe showed the install is alive and currently downloading `pymeshlab-2025.7.post1` (`105.9 MB`) very slowly after completing the `onnxruntime` wheel (`17.4 MB` at about `78 KB/s`);
  - do not assume Hunyuan is blocked yet; current blocker is slow wheel retrieval, not a code/import failure.
- Additional local P0 closure:
  - Same-root miniset GLB/render QA completed:
    - script: `assets/same_root_miniset_render_qa_20260510.py`;
    - outputs: `results/same_root_miniset_render_qa_20260510/`;
    - doc: `docs/evaluation/same_root_miniset_render_qa_status_zh_20260510.md`;
    - `vine_compete_d3` direct/final-only/prune all complete with OBJ exists, GLB export/import OK, and clean white render QA;
    - conservative main-text statement: direct has `2059` components / LCR `0.9049`; final-only has `2` components / LCR `0.9934`; prune has `1` component / LCR `1.0`;
    - `tree_compete_d3` direct/final-only/prune also complete as backup or appendix support.
    - claim gate: full same-root matrix is still not closed because exact-case `traditional`, `bridge`, and `proposed` rows are missing.
  - Naturalization L-system miniset QA completed:
    - script: `assets/naturalization_lsystem_miniset_qa_20260510.py`;
    - outputs: `results/naturalization_lsystem_miniset_qa_20260510/`;
    - doc: `docs/evaluation/naturalization_lsystem_miniset_status_zh_20260510.md`;
    - four selected GLB columns (`rule-only`, `no-N`, `weak blend`, `masked local-N`) import locally with `trimesh`, and PBR/material/texture QA passes;
    - lightweight occupancy proxy was recorded.
    - claim gate: source OBJ paths are still remote-only, so no topology repair, root reachability, anchor preservation, mask leakage, or projection-vs-naturalization separation claim is safe yet.

### 2026-05-10 16:47-17:20 CST

- User reaffirmed the long-running Ralph loop and relaxed remote storage cap to `200GB`. This cap is now the operative storage budget, while stale/rebuildable caches should still be deleted only when clearly safe.
- Heartbeat `r-slg-long-task-heartbeat` was updated again:
  - interval: 20 minutes;
  - prompt explicitly points to this recovery plan;
  - constraints: `a100-2`, GPUs `4,5,6,7`, at most 3 SSH shells, `200GB` cap, cache hygiene, TRELLIS classic/Hunyuan closure, five-case hero combo, case pools, metrics, ablation claim gates, paper structure.
- Four fresh local subagents were launched with disjoint write scopes and then closed:
  - Baseline case-pool worker:
    - doc: `docs/evaluation/baseline_case_pool_recommendations_zh_20260510.md`;
    - CSV: `results/publication_baseline_metrics_20260510/baseline_case_pool_recommendations_20260510.csv`;
    - CSV has `103` data rows plus header.
    - category counts: `ablation_depth=13`, `crystal_coral_dla=11`, `gen3d_baselines=12`, `hero_zoom=11`, `needs_repair_or_discard=10`, `plant_root_tree=12`, `sci_fi_mechanical=10`, plus `controlled_main=12` and `blocked_or_missing_baselines=12`.
    - recommended main comparison remains pyrite/coral Trellis2 one-shot vs latent copy vs mesh-space generated-root vs PS-RSLG strict; vine should use the stronger stage-5 candidate rather than the weak strict-vine row.
    - still blocked/missing rows: TRELLIS classic, Hunyuan image one-shot, Hunyuan image+texture, and Hunyuan mesh-space generated-root.
  - Hero five-case status worker:
    - doc: `docs/visuals/hero_combo_five_case_status_zh_20260510.md`.
    - current best render: `visuals/hero_combo_publication_20260510_contrast_wide_1200/overview.png`.
    - five zoom renders exist in the same directory and are true Blender camera renders at `1200 x 1200`.
    - current reusable combined GLB: `visuals/hero_combo_publication_20260510_plane_480/hero_combo_publication_20260510.glb`.
    - important caveat: the best `contrast_wide_1200` render did not export a same-parameter combined GLB (`combined_glb_exported=false`), so a same-parameter GLB pass is still needed if exact reproducibility is required.
    - asset-risk assessment: bismuth and pyrite low risk; coral has smooth shading / weighted normals but not a true geometry remesh; tree-root/tree-leaf medium risk; `plant_leaf_with_base` highest semantic risk because the selected source metadata is a climbing-vine/leaf cluster, not a clearly self-contained pedestal/base plant.
  - Paper structure / claim-gate worker:
    - doc: `docs/paper/publication_structure_claim_gate_plan_zh_20260510.md`.
    - main-paper recommendation: keep only claim-bearing compact figures/tables in main; move Hunyuan/TRELLIS-classic blocked audit, long baseline zoom, effective-resolution proxy table, gapfill matrices, strict matched candidate screens, result matrices, guide sweeps, depth galleries, DLA bridge smoke, and broad diagnostics to appendix/supplement.
    - section rewrite recommendation: rewrite 4.7 as “Naturalization Is a Local Realization Operator, Not a Topology Repair Mechanism”; merge 4.9/4.10 into an export/effective-resolution/boundaries section.
    - forbidden claims remain explicit: no broad superiority over classical procedural methods; no categorical superiority over mesh-space recursion; no topology-repair claim for naturalization; no quantitative effective-resolution proof; no Hunyuan/TRELLIS-classic failure claim until runnable baselines/logged outputs exist.
  - Ablation gap status worker:
    - doc: `docs/evaluation/ablation_gap_status_publication_zh_20260510.md`;
    - CSV: `results/publication_ablation_metrics_20260510/ablation_gap_status_publication_20260510.csv`;
    - CSV has `15` data rows plus header, status distribution `complete=3`, `partial=3`, `proxy=3`, `blocked=6`.
    - main-safe minimum subset: `SR-vine-projection-3col`, backup `SR-tree-projection-3col`, `Coral-mesh-space-generated-root`, `N-lsystem-localN-4col` as visual/export ablation, and `ER-proxy-2group` labeled as proxy only.
- Remote dependency work continued in one SSH shell only:
  - project size remains about `79G`, below the `200GB` cap;
  - GPUs `0-7` were idle at the probe time; this task remains restricted to `CUDA_VISIBLE_DEVICES=4,5,6,7`;
  - shape-only packages completed in probe venv:
    - `diffusers`, `accelerate`, `rembg`, `onnxruntime`, `humanfriendly`, `coloredlogs`, `jsonschema-specifications`, `referencing`, `rpds-py`, `zipp`, and `hy3dgen` import visibility.
  - First import smoke (`logs/baseline_env/hy3d_trellisclassic_import_smoke_20260510.log`):
    - Hunyuan import failed before shape pipeline due to `RuntimeError: operator torchvision::nms does not exist`.
    - TRELLIS classic with an `nms` operator stub failed at `ModuleNotFoundError: No module named 'pymatting'`.
  - Second import smoke after installing `pymatting` (`logs/baseline_env/hy3d_trellisclassic_import_smoke_round2_20260510.log`):
    - Hunyuan with `nms` stub reached the next blocker: `ModuleNotFoundError: No module named 'pymeshlab'`.
    - TRELLIS classic with `nms` stub reached the next blocker: `ModuleNotFoundError: No module named 'pooch'`.
  - `pooch` was installed; round-3 smoke (`logs/baseline_env/hy3d_trellisclassic_import_smoke_round3_20260510.log`) showed:
    - TRELLIS/rembg next blocker: `ModuleNotFoundError: No module named 'jsonschema'`;
    - Hunyuan remains blocked on `pymeshlab`.
  - A logged `pymeshlab` install was started:
    - log: `logs/baseline_env/pymeshlab_install_20260510.log`;
    - package: `pymeshlab-2025.7.post1` wheel, `105.9 MB`;
    - this is the active remote command at the time of this note. Poll the existing SSH session before launching any new remote install or baseline run.

### 2026-05-10 17:21-17:30 CST

- Head-figure GLB gap was closed locally:
  - script updated: `scripts/figures/hero_combo_publication_20260510.py`;
  - new option: `--export-only`, which builds the five-case scene and exports the combined GLB without re-rendering overview/zoom PNGs;
  - command completed:
    - `/Applications/Blender.app/Contents/MacOS/Blender -b --python scripts/figures/hero_combo_publication_20260510.py -- --out-dir visuals/hero_combo_publication_20260510_contrast_wide_1200_glb --resolution 1200 --samples 72 --engine cycles --overview-scale 10.6 --zoom-scale 2.45 --exposure 0.35 --export-only`;
  - output GLB: `visuals/hero_combo_publication_20260510_contrast_wide_1200_glb/hero_combo_publication_20260510.glb`;
  - output manifest: `visuals/hero_combo_publication_20260510_contrast_wide_1200_glb/hero_combo_publication_manifest_20260510.json`;
  - QA:
    - `qa.status=glb_exported`;
    - `combined_glb_exported=true`;
    - size about `1056 MB`;
    - `trimesh.load(..., force="scene")` succeeds with geometry count `12`;
    - cases: bismuth, pyrite, coral, tree-root/tree-leaf, plant-leaf/base.
  - updated status doc: `docs/visuals/hero_combo_five_case_status_zh_20260510.md`.
  - Remaining head-figure semantic risk is still the fifth case: it is best described as a climbing-vine / plant-leaf cluster on the shared platform unless a true pedestal/base plant asset is found.
- Remote `pymeshlab` wheel download/install was still active with no new stdout at this checkpoint.

### 2026-05-10 17:31-17:50 CST

- `pymeshlab` install completed successfully in the remote probe venv:
  - log: `logs/baseline_env/pymeshlab_install_20260510.log`;
  - wheel download: `105.9 MB` at about `113.5 KB/s`, elapsed about `18:08`;
  - install status: `0`;
  - remaining Hunyuan dependency warnings at that moment: `opencv-python`, `pybind11`, `xatlas`.
- Installed additional remote dependencies:
  - `jsonschema`, `pybind11`, `xatlas`;
  - log: `logs/baseline_env/hy3d_trellis_nextdeps_after_pymeshlab_20260510.log`.
- Remote round-4 import smoke (`logs/baseline_env/hy3d_trellisclassic_import_smoke_round4_20260510.log`) changed baseline status:
  - Hunyuan shape pipeline import is now OK:
    - `HUNYUAN_IMPORT_OK <class 'hy3dgen.shapegen.pipelines.Hunyuan3DDiTFlowMatchingPipeline'>`.
  - TRELLIS classic import progressed past `rembg`, `pymatting`, `pooch`, and `jsonschema`, but now fails at `open3d` through the text pipeline imported by package init:
    - `ModuleNotFoundError: No module named 'open3d'`.
- Attempted to install `open3d` for TRELLIS classic:
  - log: `logs/baseline_env/trellis_open3d_install_20260510.log`;
  - wheel is `447.7 MB`;
  - SSH connection closed during download; a follow-up short SSH probe showed no `open3d` installed, no pip process, and only the partial log lines.
  - decision: do not spend another long blocking download immediately; first test image-pipeline import with an `open3d` stub because the image-to-3D baseline does not need text-pipeline `open3d` unless package init requires it.
- TRELLIS image-pipeline import with `open3d` stub (`logs/baseline_env/trellis_image_import_stub_open3d_20260510.log`):
  - `open3d` blocker was bypassed;
  - next failure is missing compiled/source extension:
    - `ModuleNotFoundError: No module named 'trellis.representations.mesh.flexicubes.flexicubes'`.
  - Interpretation: TRELLIS classic is no longer merely blocked by small Python deps; it likely needs repo extension/submodule build for FlexiCubes before it can run image-to-3D export.
- Hunyuan full shape-only weight-load smoke was launched as a remote background job with project-local caches:
  - script: `cache/tmp/hunyuan_full_weight_load_smoke_20260510.py`;
  - log: `logs/baseline_env/hunyuan_full_weight_load_smoke_20260510.log`;
  - pid file: `logs/baseline_env/hunyuan_full_weight_load_smoke_20260510.pid`;
  - current PID at launch: `3705429`;
  - cache variables:
    - `HF_HOME=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/huggingface`;
    - `HF_HUB_CACHE=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/huggingface/hub`;
    - `HY3DGEN_MODELS=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/hy3dgen`.
  - log confirms:
    - `PIPELINE_CLASS_OK`;
    - it tries local project cache first;
    - local Hunyuan path does not exist yet;
    - it started the HuggingFace download path.
  - As of this checkpoint, the process was alive, but no large cache file had landed yet; project size remained about `80G`.
  - 1800px head-figure render completed:
  - output dir: `visuals/hero_combo_publication_20260510_contrast_wide_1800/`;
  - files: overview + five zooms + manifest;
  - all PNGs are `1800 x 1800`;
  - manifest status: `rendered`, `combined_glb_exported=false` because this run intentionally used `--skip-glb-export`;
  - QA foreground proxies:
    - overview `0.2193`;
    - bismuth `0.5665`;
    - pyrite `0.4981`;
    - coral `0.2375`;
    - tree `0.2342`;
    - plant `0.1028`.
  - This is now the best PNG render set; pair it with the same-parameter export-only GLB in `visuals/hero_combo_publication_20260510_contrast_wide_1200_glb/`.

### 2026-05-10 17:51-17:56 CST

- Hunyuan official-endpoint background load was stopped because it was alive but stuck before writing any cache files and had already logged the undesired default cache lookup behavior.
- Read AgentDoc HF download runbook and `hf-download-cn` skill references:
  - preferred CN route is `HF_ENDPOINT=https://hf-mirror.com`;
  - unset proxy variables;
  - `HF_HUB_ENABLE_HF_TRANSFER=0`;
  - `HF_HUB_DISABLE_XET=1`;
  - keep cache roots under the project.
- Restarted Hunyuan full shape-only weight-load smoke via mirror:
  - log: `logs/baseline_env/hunyuan_full_weight_load_smoke_mirror_20260510.log`;
  - pid file: `logs/baseline_env/hunyuan_full_weight_load_smoke_mirror_20260510.pid`;
  - current PID: `3707161`;
  - env confirms project-local cache:
    - `HF_HOME=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/huggingface`;
    - `HF_HUB_CACHE=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/huggingface/hub`;
    - `HY3DGEN_MODELS=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/hy3dgen`.
  - mirror route is working:
    - log shows `Fetching 6 files`;
    - cache grew from about `101M` to `871M`;
    - largest incomplete blobs at this checkpoint are about `514M` and `440M`.
  - Do not claim Hunyuan runnable yet: this is successful dependency/import + active weight-download progress, not a completed load or generated mesh.

### 2026-05-10 17:57-18:00 CST

- Hunyuan mirror download remains healthy:
  - PID `3707161` alive;
  - cache grew from `871M` to `1.6G`, then to `2.6G`;
  - two largest incomplete blobs grew to about `1.41G` and `1.31G`;
  - project size still around `80G`, well below the `200GB` cap.
- Current state interpretation:
  - Hunyuan repo/package/import blockers are resolved for shape-only pipeline;
  - Hunyuan is not yet a completed baseline because the weight-load smoke has not finished and no mesh output exists yet;
  - continue monitoring the existing mirror PID rather than launching duplicate downloads.

### 2026-05-10 18:01-18:07 CST

- Hunyuan mirror download continued with resumable timeouts:
  - log records a `read operation timed out` from a `cas-bridge.xethub.hf.co` URL followed by `Trying to resume download...`;
  - despite the timeout, cache continued growing:
    - about `3.3G` with two incomplete blobs about `1.82G` and `1.72G`;
    - then about `4.2G` with two incomplete blobs about `2.30G` and `2.25G`;
  - PID `3707161` remained alive.
- Operational decision: do not interrupt or duplicate the download while incomplete files are growing. This is the expected HF mirror/resume path under CN network conditions.

### 2026-05-10 18:08-18:15 CST

- Hunyuan mirror download continued to grow:
  - cache about `5.2G`, then `6.4G`;
  - two largest incomplete blobs about `2.89G`/`2.73G`, then `3.51G`/`3.36G`;
  - PID `3707161` still alive;
  - GPU `4-7` memory remained only about `4 MiB`, so it had not yet entered model load / inference.
- Continue to wait for the existing process. Do not start another Hunyuan download.

### 2026-05-10 18:16-18:22 CST

- Hunyuan mirror download continued:
  - cache about `7.9G`;
  - two largest incomplete blobs about `4.31G` and `4.17G`;
  - PID `3707161` still alive for about `31` minutes;
  - GPU `4-7` still at about `4 MiB`, so still pre-load/download phase.
- This remains positive progress, not a failure. Keep waiting for the same process unless incomplete files stop growing.

### 2026-05-10 18:23-18:28 CST

- Hunyuan weight-load smoke completed successfully:
  - mirror download fetched `6/6` files after one timeout+resume event;
  - log: `logs/baseline_env/hunyuan_full_weight_load_smoke_mirror_20260510.log`;
  - cache: `cache/huggingface` about `9.2G`;
  - key weight files in HF cache:
    - `model.fp16.safetensors` blob about `4.928G`;
    - VAE or companion blob about `4.928G`;
  - final log line:
    - `HUNYUAN_FULL_LOAD_OK seconds 2215.33 type <class 'hy3dgen.shapegen.pipelines.Hunyuan3DDiTFlowMatchingPipeline'>`;
    - `device cuda dtype torch.float16`.
  - Hunyuan status upgrade: shape pipeline repo/deps/weights/load are now OK. It is still not a completed baseline until at least one image-to-shape mesh is generated and metrics/render QA exist.
- Started Hunyuan low-cost image-to-shape smoke:
  - script: `cache/tmp/hunyuan_shape_generate_smoke_20260510.py`;
  - log: `logs/baseline_env/hunyuan_shape_generate_smoke_20260510.log`;
  - pid file: `logs/baseline_env/hunyuan_shape_generate_smoke_20260510.pid`;
  - PID: `3739518`;
  - bound to physical GPU `4` via `CUDA_VISIBLE_DEVICES=4`;
  - input: `repos/Hunyuan3D-2/assets/demo.png`;
  - low-cost settings: `num_inference_steps=8`, `octree_resolution=192`, `num_chunks=4000`, seed `12345`;
  - output target: `results/remote_smoke_20260510/hunyuan_shape_demo_lowcost/hunyuan_demo_lowcost_steps8_oct192.glb`;
  - metrics target: `results/remote_smoke_20260510/hunyuan_shape_demo_lowcost/hunyuan_demo_lowcost_steps8_oct192_metrics.json`.
  - Initial monitor showed local HF cache hit (`Fetching 6 files: 100%` immediately) and loading from cached `model.fp16.safetensors`; no mesh output yet at this checkpoint.

### 2026-05-10 18:29-18:34 CST

- Hunyuan low-cost image-to-shape smoke completed successfully:
  - log: `logs/baseline_env/hunyuan_shape_generate_smoke_20260510.log`;
  - remote output GLB: `results/remote_smoke_20260510/hunyuan_shape_demo_lowcost/hunyuan_demo_lowcost_steps8_oct192.glb`;
  - remote metrics: `results/remote_smoke_20260510/hunyuan_shape_demo_lowcost/hunyuan_demo_lowcost_steps8_oct192_metrics.json`;
  - local copies:
    - `results/remote_smoke_20260510/hunyuan_shape_demo_lowcost/hunyuan_demo_lowcost_steps8_oct192.glb`;
    - `results/remote_smoke_20260510/hunyuan_shape_demo_lowcost/hunyuan_demo_lowcost_steps8_oct192_metrics.json`.
  - metrics:
    - status `ok`;
    - load seconds `20.63`;
    - generation seconds `4.17`;
    - total seconds `24.82`;
    - vertices `90297`;
    - faces `180598`;
    - GLB size `3.101 MB`;
    - settings: `num_inference_steps=8`, `octree_resolution=192`, `num_chunks=4000`, seed `12345`.
  - local `trimesh` import QA:
    - geometry count `1`;
    - bounds approximately `[[-0.669, -0.999, -0.775], [0.661, 0.991, 0.770]]`.
  - Hunyuan status upgrade: Hunyuan3D 2.0 shape-only repo/deps/weights/load/generate are now runnable on remote. This is still only a low-cost smoke on the official demo image, not a completed recursive-case baseline.
- Unexpected remote process audit:
  - a pre-existing V24 Trellis2 texture launcher appears to be running workers for GPUs `4-7`:
    - `assets/launch_strict_visual_matched_texture_V24_priority_rerun_20260510.sh --worker 4/5/6/7`;
    - child commands use `assets/trellis2_texturing_export_glb.py` on V24 priority rerun inputs.
  - Do not kill automatically without a resource decision. If the next step is Hunyuan formal baseline generation on GPU `4`, pause/coordinate the V24 launcher first to avoid contention.
  - Remote project size after Hunyuan cache and smoke: about `89G`, still below `200GB`.
  - Follow-up quick status showed the V24 launcher is still making progress:
    - launcher parents alive for workers `4`, `5`, `6` at the time of probe;
    - one active GPU process on bus `69:03.0` using about `3866 MiB`;
    - result/log file count under `results/strict_visual_matched_texture_V24_priority_rerun_seed20260511_20260510` was `22`.
    - Since it is producing outputs and Hunyuan smoke is complete, it was not killed. Revisit before launching formal Hunyuan case batch.

### 2026-05-10 18:35-18:50 CST

- Hunyuan formal recursive-guide baseline moved from smoke to a real 13-case shape-only pool:
  - reusable local script added: `assets/hunyuan_recursive_guides_batch_20260510.py`;
  - remote script path: `cache/tmp/hunyuan_recursive_guides_batch_20260510.py`;
  - output root: `results/publication_hunyuan_recursive_guides_20260510`;
  - settings: `num_inference_steps=30`, `octree_resolution=320`, `num_chunks=12000`, `guidance_scale=5.0`, base seed `20260510`;
  - four shards were launched on physical GPUs `4,5,6,7`; all completed and GPUs returned to idle.
- The initial 3 recursive-guide cases completed first and were pulled locally:
  - `vine_lsystem_grammar`: `745382` vertices, `1484726` faces, `25.522 MB`;
  - `pyrite_lattice`: `2058208` vertices, `4119162` faces, `70.695 MB`;
  - `coral_frontier`: `837923` vertices, `1675900` faces, `28.769 MB`.
  - local import QA: `results/publication_hunyuan_recursive_guides_20260510/local_trimesh_import_qa_20260510.json`, all `trimesh` scene imports OK.
  - local white render QA:
    - flattened white renders: `results/publication_hunyuan_recursive_guides_20260510/render_qa_white_900/flattened_white/`;
    - contact sheet: `results/publication_hunyuan_recursive_guides_20260510/hunyuan_recursive_guides_white_contact_20260510.png`;
    - warning: the original Blender PNGs are transparent; use flattened white PNGs or the contact sheet for paper/QA, otherwise naive RGB conversion shows black corners.
- The full Hunyuan guide pool then completed:
  - result rows: `13/13` status `ok`;
  - merged remote metrics:
    - `results/publication_hunyuan_recursive_guides_20260510/hunyuan_recursive_guides_fullpool_metrics.json`;
    - `results/publication_hunyuan_recursive_guides_20260510/hunyuan_recursive_guides_fullpool_metrics.csv`;
  - local copy complete, local result dir about `362M`;
  - local full-pool import QA: `results/publication_hunyuan_recursive_guides_20260510/local_trimesh_import_qa_fullpool_20260510.json`, all 13 GLBs import with `geometry_count=1`.
  - full-pool rows:
    - `branch_ornament`: `645778` vertices, `1284416` faces, `22.090 MB`;
    - `branch_tree`: `571112` vertices, `1133892` faces, `19.513 MB`;
    - `bush_shell`: `603547` vertices, `1207092` faces, `20.722 MB`;
    - `coral_frontier`: `837923` vertices, `1675900` faces, `28.769 MB`;
    - `crystal_frontier`: `603372` vertices, `1206740` faces, `20.716 MB`;
    - `frontier_sheet`: `603748` vertices, `1207488` faces, `20.729 MB`;
    - `pine_grammar`: `603556` vertices, `1207108` faces, `20.722 MB`;
    - `pyrite_lattice`: `2058208` vertices, `4119162` faces, `70.695 MB`;
    - `radial_ornament`: `671760` vertices, `1334676` faces, `22.963 MB`;
    - `root_fan_grammar`: `603644` vertices, `1207276` faces, `20.725 MB`;
    - `root_network`: `690084` vertices, `1372808` faces, `23.609 MB`;
    - `tree_crown`: `621097` vertices, `1234552` faces, `21.237 MB`;
    - `vine_lsystem_grammar`: `745382` vertices, `1484726` faces, `25.522 MB`.
- Visual interpretation from the 3-case contact sheet:
  - Hunyuan is now a runnable and evidence-backed secondary one-shot baseline.
  - It should still be written as shape-only one-shot baseline, not texture baseline and not grammar-state baseline.
  - The current three rendered examples are useful negative controls: vine becomes many curled filaments; pyrite becomes a cage/block hybrid; coral collapses into a block-like solid. This supports the "ordinary image-to-3D does not provide grammar-readable recursive state" story, but quantitative claims require the full-pool render QA and merged baseline table.
- Remote storage/process state:
  - Hunyuan result dir about `339M`;
  - remote project total still about `89G`, below the user-relaxed `200GB` cap;
  - GPUs `4-7` idle after full-pool completion.
- Remaining Hunyuan gaps:
  - full-pool white render/contact sheet still running locally at this checkpoint;
  - no Hunyuan texture/paint baseline yet;
  - no Hunyuan + mesh-space generated-root baseline yet;
  - Hunyuan rows are not yet merged into the master baseline CSV/LaTeX table with failure labels.

### 2026-05-10 19:00-19:31 CST

- Heartbeat `r-slg-long-task-heartbeat` was updated to a 20-minute thread heartbeat pointing back to this plan and the latest claim gates.
- Remote audit:
  - remote project size about `90G`, below the user-relaxed `200GB` cap;
  - GPUs `0-7` idle at audit time; policy remains use physical GPUs `4,5,6,7` only;
  - repos present: `repos/TRELLIS`, `repos/Hunyuan3D-2`;
  - Hunyuan full-pool metrics present remotely.
- Subagent outputs:
  - baseline/case-pool recommendation doc added: `docs/evaluation/baseline_case_pool_recommendation_zh_20260510.md`;
  - hero five-case QA doc added: `docs/visuals/hero_combo_five_case_qa_recommendation_zh_20260510.md`;
  - paper/ablation claim-gate doc added: `docs/paper/paper_ablation_claim_gate_next_actions_zh_20260510.md`.
- Hunyuan status updates:
  - 13-case shape-only Hunyuan full-pool is local/import/render-QA complete:
    - `results/publication_hunyuan_recursive_guides_20260510/hunyuan_recursive_guides_fullpool_metrics.csv`;
    - `results/publication_hunyuan_recursive_guides_20260510/local_trimesh_import_qa_fullpool_20260510.json`;
    - `results/publication_hunyuan_recursive_guides_20260510/hunyuan_recursive_guides_fullpool_white_contact_20260510.png`.
  - Hunyuan + mesh-space generated-root negative control is now complete for vine/pyrite/coral:
    - script: `assets/hunyuan_mesh_space_generated_root_20260510.py`;
    - outputs: `results/publication_hunyuan_mesh_space_20260510/`;
    - status doc: `docs/evaluation/hunyuan_mesh_space_generated_root_status_zh_20260510.md`.
  - Key Hunyuan mesh-space rows:
    - vine: `309764` vertices, `104000` faces, raw comps `101985`, occ comps `885`, occ LCR `0.843`;
    - pyrite: `599000` vertices, `200000` faces, raw comps `199050`, occ comps `15`, occ LCR `0.965`;
    - coral: `500535` vertices, `168000` faces, raw comps `165123`, occ comps `50`, occ LCR `0.998`.
  - These rows are negative controls only: Hunyuan root mesh copied by S/R/T and direct concat; no generation, latent update, projection, weld, boolean, remesh, or repair.
  - Master baseline manifest/table updated:
  - aggregator updated: `assets/publication_baseline_metrics_20260510.py`;
  - master CSV: `results/publication_baseline_metrics_20260510/publication_baseline_master_manifest_20260510.csv`;
  - LaTeX draft: `results/publication_baseline_metrics_20260510/publication_baseline_table_draft_20260510.tex`;
  - current status counts: blocked `6`, fragmented `5`, fragmented_copy_paste `6`, Hunyuan shape-only generated/import/render-QA pending topology metrics `3`, success `5`.
  - Remaining blocked rows are TRELLIS classic image one-shot and Hunyuan image+texture; Hunyuan mesh-space is no longer missing.
- Hunyuan one-shot topology/failure-label proxy was added:
  - metrics: `results/publication_hunyuan_recursive_guides_20260510/hunyuan_fullpool_topology_metrics_20260510.csv`;
  - labels: `results/publication_hunyuan_recursive_guides_20260510/hunyuan_fullpool_failure_labels_20260510.csv`;
  - script: `assets/hunyuan_failure_label_summary_20260510.py`;
  - key main-table labels:
    - vine Hunyuan one-shot: raw comps `1526`, occ comps `445`, LCR `0.0589`, label `fragmented_or_filamentary_one_shot`;
    - pyrite Hunyuan one-shot: raw comps `582`, occ comps `65`, LCR `0.9930`, label `one_shot_category_match_without_recursive_state`;
    - coral Hunyuan one-shot: raw comps `44`, occ comps `30`, LCR `0.9959`, label `one_shot_category_match_without_recursive_state`.
  - This closes the "only V/F/MB" weakness for Hunyuan shape-only rows, but labels still need human visual review before being phrased as final paper conclusions.
- TRELLIS classic / TRELLIS1 status:
  - still not a runnable baseline;
  - import probe logs:
    - `logs/baseline_env/trellisclassic_import_probe_20260510_1907.log`;
    - `logs/baseline_env/trellisclassic_stub_import_probe_20260510.log`;
    - `logs/baseline_env/trellisclassic_flexicubes_fetch2_stub_probe_20260510.log`.
  - blockers found and fixes attempted:
    - `torchvision::nms` requires a temporary stub in the current probe env;
    - real `open3d` is missing; installing `open3d-0.19.0` starts a `447.7 MB` wheel download and was stopped after it hung too long;
    - `.gitmodules` points to `https://github.com/MaxtirError/FlexiCubes.git`; because the repo was extracted from zip/codeload, the submodule directory was initially empty;
    - remote SSL certificate verification blocked Python `urllib` download of FlexiCubes from codeload, so the zip was downloaded locally and copied to remote cache;
    - FlexiCubes has now been extracted into `repos/TRELLIS/trellis/representations/mesh/flexicubes`;
    - with open3d stubbed and FlexiCubes present, import now reaches `ModuleNotFoundError: No module named 'kaolin'`.
  - Therefore TRELLIS classic should be reported as repo present and submodule repaired, but still not runnable until `open3d`, `kaolin`, and likely version-specific CUDA/PyTorch dependencies are resolved. This is still an environment/repo dependency blocker, not a model failure.
- Hero combo status:
  - current usable combined GLB: `visuals/hero_combo_publication_20260510_contrast_wide_1200_glb/hero_combo_publication_20260510.glb`;
  - current high-res PNG/zoom package: `visuals/hero_combo_publication_20260510_contrast_wide_1800/`;
  - bismuth, pyrite, coral, and tree-root/tree-leaf are layout-usable;
  - fifth case is render-usable but semantically should be renamed `plant leaf / climbing vine` or replaced if strict `plant with base` is required;
  - coral smoothing is only smooth shading + weighted normals, not geometric remesh.

### 2026-05-10 21:03-21:12 CST: user correction and remote-only repair lane

- User clarified that the tree-root and old non-tree repair must run with our own recursive algorithm on remote `a100-2`, not local procedural experiments. Treat earlier local procedural previews as diagnostics only; they are not final evidence and must not be used in the paper or gallery as completed outputs.
- Heartbeat `r-slg-long-task-heartbeat` was updated to a 30-minute thread heartbeat with explicit remote-only / no-overclaim instructions.
- Current immediate P0 focus:
  - repair `lsystem_spiky_iso.png` semantics by selecting a better upward crown/root mesh, fixing attachment grammar, and running recursive SLat grammar remotely on GPUs 4/5/6/7;
  - diagnose and repair the old `non_tree_recursive_20260508` last-three-case failures (crown, scifi, arch) by locating original roots/operators and rerunning improved attached grammars remotely;
  - run render QA and topology/fragment metrics before calling any result usable.
- Operational constraint: one persistent SSH shell is preferred; all persistent outputs stay under `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`; remote storage cap is `200GB`, with storage hygiene still required.

### 2026-05-10 21:45 CST: tree-root repair status after remote micro grammar

- User-requested remote-only repair was performed on `a100-2` using our TRELLIS2 SLat recursive grammar workflow, not local procedural generation.
- Workflow code update: `assets/trellis2_recursive_slat_grammar_workflow.py` now supports `--growth-axis/--growth-sign` and two local crown grammars `crown_bud_attach` / `crown_micro_fork_attach`.
- First broad sweep: `results/publication_repair_remote_20260510b`, 19 remote cases and 119 OBJ/preview outputs. It fixed the gross direction issue but full fork grammar still produced floating crown fragments.
- Best broad-sweep tree row: `tree_v25_zpos_fork_d2`, occ LCR `0.9523`, raw LCR `0.7873`; visually direction-correct but dusty.
- Second micro sweep: `results/publication_repair_remote_20260510c`.
  - `tree_micro_ypos_bud_d2`: raw LCR `0.9622`, occ LCR `0.9914`, occ components `10`.
  - `tree_micro_zpos_bud_d2`: raw LCR `0.9160`, occ LCR `0.9891`, occ components `15`.
  - Blender white-background QA: `results/publication_repair_remote_20260510c_pull/blender_renders_micro_white_flat/contact_sheet.png`.
- Current interpretation: the bad lsystem/spiky case is no longer directionally wrong; the micro-bud grammar gives usable candidates. It is not yet final publication-grade until TRELLIS2 texturing GLBs, final camera/material renders, and final visual QA pass.
- Texturing jobs launched on GPUs 4-7 in `results/publication_repair_remote_20260510c/textured_micro/` for `tree_micro_ypos_bud_d2` and `tree_micro_zpos_bud_d2` with root-guide and spiky-guide variants.
- Important distinction: the V25 root/SC refinement already has a safer metric-stable root replacement (`V25_lsys_root_fan_smooth_anchorD_stable`, r0 single-component/LCR 1.0, textured GLB and zoom renders). Use V25 root as the paper-safe replacement if the repaired spiky SLat case remains visually dusty.

### 2026-05-10 22:12 CST: tree-root PBR GLB repair outputs

- Four remote PBR GLBs completed in `results/publication_repair_remote_20260510c/textured_micro/`, all `summary.status=ok`, each 12-14 MB.
- Local pulled mirror: `results/publication_repair_remote_20260510c_pull/textured_micro/`.
- Render QA contact sheet: `results/publication_repair_remote_20260510c_pull/textured_micro_renders_white_flat/contact_sheet.png`.
- Recommended repaired snow-cedar/spiky variant: `micro_zpos_bud_d2_spikyguide_steps8_tex2048_seed202605304_xformers/textured.glb`.
- Remaining visual caveat: top crown has a few fine speckles; final figure should either use a camera crop/lighting that suppresses them or run a final conservative small-island cleanup before the final gallery export.

### 2026-05-11 00:16 CST: root/anchor protocol and 20260510f PBR closure batch

- Method protocol clarified by code/paper audit:
  - root mesh, growth axis/sign, grammar family, fit scale, depth, max tokens, seed, guide image, pruning/texturing, camera/render setup are authored controls and must be manifest-recorded;
  - operator-internal frontier masks are deterministic geometry heuristics after the authored controls are fixed;
  - PS-RSLG currently does not discover semantic roots, search roots, or learn grammar parameters.
- `paper_siga/main.tex` was updated accordingly:
  - `Root and Program Specification` now includes manifest-locked fairness for root source, growth frame, grammar controls, random seeds, camera, renderer, and render/export schedule;
  - `Discussion and Limitations` now explicitly says roots/programs are authored and case-specific and multi-root robustness remains future work.
- `publication_repair_remote_20260510e` anchor screen is complete and pulled:
  - manifest: `results/publication_repair_remote_20260510e_pull/root_anchor_manifest_20260510e.tsv`;
  - metrics: `results/publication_repair_remote_20260510e_pull/metrics/selected_metrics_20260510e.csv`;
  - white QA sheet: `results/publication_repair_remote_20260510e_pull/blender_white_qa/contact_sheet_white.png`.
- Candidate claim gates from 20260510e:
  - PBR/main candidates: `tree_v25_bud_d1`, `scifi_old_tight_d1`, `arch_clean_key_d2`;
  - PBR/appendix candidates: `crown_old_rim_d1`, `ornament_v24_rim_d1`;
  - diagnostic only: `crown_tapered_rim_d1`, `scifi_clean_translate_d2`, `snow_arch_key_d1`;
  - excluded from positive claims: `tree_flipz_bud_d2`, `island_city_scale_d1`.
- New remote launcher `assets/run_publication_repair_remote_20260510f.sh` was added, synced to `a100-2`, and launched on GPUs `4,5,6,7`.
  - It uses only remote SLat-generated 20260510e OBJ outputs, conservative pruning, and TRELLIS2 texturing/export.
  - Project storage was about `94G` at launch, below the `200GB` cap.
  - First completed GLBs:
    - `tree_v25_bud_d1_spiky_pruned_steps8_tex2048_seed202605601_xformers/textured.glb`, ok;
    - `scifi_old_tight_d1_metal_pruned_steps8_tex2048_seed202605621_xformers/textured.glb`, ok;
    - `arch_clean_key_d2_stone_pruned_steps8_tex2048_seed202605631_xformers/textured.glb`, ok.
- Remaining immediate gate: wait for all 20260510f lanes, pull outputs, run local Blender/GLB metrics QA, then update gallery/figure manifests. Do not call these publication-grade until render QA passes.

### 2026-05-11 00:32 CST: 20260510f completed; render/metric QA verdict

- `publication_repair_remote_20260510f` fully completed:
  - all 9 GLB summaries are `status=ok`;
  - local mirror: `results/publication_repair_remote_20260510f_pull/`;
  - render QA sheet: `results/publication_repair_remote_20260510f_pull/blender_textured_white_qa/contact_sheet_textured_white_all.png`;
  - material-override QA sheet: `results/publication_repair_remote_20260510f_pull/blender_material_override_qa/contact_sheet_material_override.png`;
  - all-GLB metric CSV: `results/publication_repair_remote_20260510f_pull/metrics/textured_glb_metrics_all_20260510f.csv`.
- Usable geometry candidates from this round:
  - `tree_v25_bud_d1_spiky_pruned`: best tree/root repair; occ LCR `0.9930`;
  - `scifi_old_tight_d1_metal_pruned`: best hard-surface proxy, not tank/weapon; occ LCR `0.9952`;
  - `arch_clean_key_d2_stone_pruned`: best architecture/portal proxy, not city proof; occ LCR `0.9984`;
  - `crown_old_rim_d1_ornament_pruned`: appendix/ornament candidate; occ LCR `0.9997`.
- Texture/visual caveat:
  - raw TRELLIS2 PBR export works technically, but not all automatic textures are publication-safe;
  - `scifi_old` raw texture is too red/toy-like, `arch_clean` raw texture is too dirty/wood-like, and tree variants are dark;
  - use controlled Blender material/lighting renders for main-paper visuals unless a better texture-guide rerun is launched.
- Diagnostic-only outputs remain:
  - `ornament_v24` is metric-clean but visually flat;
  - `crown_tapered` has a pole/root-ball semantic issue;
  - `scifi_clean` is weaker than `scifi_old`;
  - `snow_arch` is stable but not clean architecture/city semantics.

### 2026-05-11 03:15 CST: controlled material zoom and remote baseline audit

- Local controlled-material camera zooms were rendered for the four best `20260510f` candidates:
  - output root: `visuals/publication_repair_20260510f_controlled_zoom_1200/`;
  - manifest: `assets/generated_manifests/publication_repair_20260510f_controlled_zoom_manifest.json`;
  - render plan: `visuals/publication_repair_20260510f_controlled_zoom_1200/matched_camera_zoom_plan.json`;
  - contact sheet: `visuals/publication_repair_20260510f_controlled_zoom_1200/contact_sheet_controlled_zoom_1200.png`;
  - image QA: `visuals/publication_repair_20260510f_controlled_zoom_1200/image_qa_metrics.csv`.
- `scripts/figures/matched_camera_zoom_render_20260510.py` was extended with controlled material presets (`cedar`, `metal`, `stone`, `ornament`) so these renders do not depend on raw TRELLIS2 automatic textures.
- Rendered cases:
  - `tree_v25_bud_d1_spiky_controlled_cedar`: overview + two nested zooms; clean but small overview silhouette. Keep as tree/root repair candidate.
  - `scifi_old_tight_d1_controlled_metal`: overview + two nested zooms; current best hard-surface proxy. Do not call it tank/weapon.
  - `arch_clean_key_d2_controlled_stone`: overview + two nested zooms; current best architecture/portal proxy. Do not call it city proof.
  - `crown_old_rim_d1_controlled_ornament`: overview + two nested zooms; visually dense/darker. Keep as appendix/ornament candidate unless improved.
- White-background postprocessing and callout/comparison sheets were completed with system Python because Blender's bundled Python lacked PIL.
- Remote baseline/storage audit was completed read-only by subagent; log:
  - `docs/progress/remote_baseline_audit_20260511_subagent.md`.
- Baseline audit conclusions:
  - remote project is `95G`, below the `200GB` cap; GPUs 0-7 were idle during audit.
  - TRELLIS classic/non-2 has repo, probe env, and `TRELLIS-image-large` cache, but is still blocked by environment/compiled dependencies (`torchvision::nms`, real `open3d`, `kaolin`, likely CUDA/PyTorch extension compatibility). Do not write it as runnable.
  - Hunyuan3D has repo/package/cache plus shape-only smoke/full-pool outputs. Shape-only is available; image+texture/paint is not closed.
  - TRELLIS.2 remains the usable main generator/baseline stack with weights, scripts, logs, and successful `20260510b/c/e/f` outputs.
- Current claim gate after this update:
  - `20260510f` has GLBs, metrics, and controlled zoom render QA for four candidates, so these can be used as paper-layout candidates with scoped labels.
  - Still not closed: TRELLIS classic runnable baseline, Hunyuan paint/texture baseline, same-root matrix, naturalization matrix, coral mesh-space generated-root row, and final appendix/main-paper slimming.

### 2026-05-11 03:20 CST: remote minimal smoke evidence

- A lightweight remote smoke log was written locally:
  - `results/remote_smoke_logs_20260511/baseline_min_smoke_20260511_0318.log`.
- The first attempt confirmed remote project size and idle GPUs but stopped early because the non-interactive SSH shell had no `python` command. The second attempt used explicit env Python / `python3` paths.
- Verified by smoke:
  - remote storage remains about `95G`;
  - GPUs `0-7` showed `0 MiB` used and `0%` utilization;
  - TRELLIS.2 help smoke exits `0` via `assets/trellis2_dinov3_official_min_smoke.py --help`;
  - Hunyuan3D import smoke exits `0`: `hy3dgen`, `hy3dgen.shapegen`, and `torch` are importable;
  - TRELLIS classic import probe exits cleanly but reports `trellis=False`, `kaolin=False`, `open3d=False`, `torchvision=True`.
- Claim implication:
  - Hunyuan shape-only environment/package is present and importable, consistent with the existing shape-only output pool; image+texture/paint is still not closed.
  - TRELLIS classic/non-2 remains blocked as a runnable baseline because the tested environment cannot import `trellis`, `kaolin`, or `open3d`.
  - TRELLIS.2 remains the only fully usable generator stack in the current remote environment.

### 2026-05-11 03:35 CST: ablation gap audit update

- Local read-only ablation audit was completed by subagent:
  - `docs/progress/ablation_gap_audit_20260511_subagent.md`.
- Most important evidence paths:
  - `results/publication_ablation_metrics_20260510/matrix_coverage_summary.csv`;
  - `results/publication_ablation_metrics_20260510/claim_safe_miniset_20260510.csv`;
  - `results/publication_baseline_metrics_20260510/publication_baseline_master_manifest_20260510.csv`;
  - `results/publication_coral_mesh_space_20260510/summary.json`.
- Updated gap status:
  - coral mesh-space generated-root is no longer missing; it is a completed negative-control row in `results/publication_coral_mesh_space_20260510/summary.json`.
  - same-root matrix remains partial: vine/tree `direct`, `final-only`, and `prune` subset rows are usable, but the full six-column matrix is not closed; `bridge` coverage is especially sparse.
  - masked naturalization has a focused three-task/three-seed masked-local claim that can be used cautiously; the full naturalization matrix remains partial/blocked.
  - effective-resolution / zoom-retention remains proxy evidence and must not be written as a strong quantitative proof.
- Paper routing:
  - possible main-text cautious claims: coral mesh-space negative row, vine/tree same-root subset trends, masked-local local-surface evidence, effective-resolution proxy;
  - appendix/status only: full same-root/naturalization coverage, global-N, post-hoc repair, stress insets;
  - blocked/diagnostic only: full six-column same-root, full naturalization matrix, topology/root/mask leakage claims, strong zoom-retention/effective-resolution superiority.

### 2026-05-11 heartbeat: effective-resolution claim gate clarified

- Added a dedicated claim-gate note:
  - `docs/evaluation/effective_resolution_zoom_retention_claim_gate_20260511.md`.
- Current status is "selected-case proxy + matched zoom visualization", not "strong quantitative proof".
- Current numeric table has two selected comparisons:
  - crystal/coral: local scale improvement `4.09x`, terminal detail ratio `2.46x`;
  - tree/vine: local scale improvement `3.79x`, terminal detail ratio `0.54x`.
- Existing zoom render packs that can support a cautious selected panel:
  - `visuals/gen3d_baseline_matched_white_renders_20260510_flatwhite/`;
  - `visuals/gen3d_baseline_texture_fair_matched_20260510_flatwhite/`;
  - `visuals/gen3d_baseline_geometry_control_20260510_flatwhite/`;
  - `visuals/publication_repair_20260510f_controlled_zoom_1200/`.
- Remaining blocker is not absence of all assets; it is that the current metrics are proxy definitions and the rows are not yet same-root/same-condition/same-budget/multi-seed.

## 2026-05-11 05:45 CST Update: Hunyuan Fair Mesh-Space Baseline Closed

Status: `closed_for_three_primary_cases`, with visual/paper-integration QA still pending.

The fair Hunyuan route requested by the user has now been executed end-to-end:

```text
text prompt -> HunyuanDiT root image -> Hunyuan3D root GLB -> deterministic mesh S/R/T copy -> direct concat / laplacian upper-bound -> metrics
```

Remote output:

```text
a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/publication_hunyuan_text_root_meshspace_20260511/
```

Local lightweight pull:

```text
/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/remote_pull_hunyuan_text_root_meshspace_20260511/
```

Contact sheet:

```text
/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/remote_pull_hunyuan_text_root_meshspace_20260511/hunyuan_text_root_meshspace_contact_sheet_20260511.png
```

Verification summary:

```text
manifest_rows 3 statuses ['ok']
metrics_rows 6 statuses ['fragmented_copy_paste', 'smoothed_copy_paste']
missing_or_empty 0
BASELINE_ALL_DONE at 2026-05-11 05:36:36
```

Cases closed:

- `tree_trunk_branch`: root image, root GLB, direct mesh-copy, laplacian3 upper-bound, preview, metrics.
- `pyrite_crystal_root`: root image, root GLB, direct mesh-copy, laplacian3 upper-bound, preview, metrics.
- `coral_branch_root`: root image, root GLB, direct mesh-copy, laplacian3 upper-bound, preview, metrics.

Important interpretation:

- This is now a fair Hunyuan text-root mesh-space copy baseline for three primary cases, unlike the old recursive-guide Hunyuan one-shot results.
- Direct rows are the paper-comparable mesh route; laplacian rows are upper-bound smoothing only.
- Main negative evidence is extremely high raw component count plus `copy_repetition_score=1.0`; do not overinterpret high occupancy LCR as success.
- Still needed: visual QA/rendering under paper style, table integration, and expansion to the requested at-least-10 selectable cases per category if the main paper requires a larger pool.

Detailed protocol and metrics are in:

```text
/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/hunyuan_text_root_meshspace_protocol_zh_20260511.md
```
