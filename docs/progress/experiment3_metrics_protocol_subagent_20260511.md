# Experiment 3 Metrics / Paper Protocol Subagent Note

Date: 2026-05-11 CST
Scope: local-only document synthesis; no SSH; no new experiments; no main-paper edits.
Project root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`

## 0. Read Sources

- `paper_siga/main.tex` novelty-gate/TODO context around Experiment 3.
- `paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex`.
- `docs/progress/ablation_gap_audit_20260511_subagent.md`.
- `docs/evaluation/hunyuan_text_root_meshspace_protocol_zh_20260511.md`.
- `results/publication_baseline_metrics_20260510/summary.json`.
- `results/publication_baseline_metrics_20260510/publication_baseline_master_manifest_20260510.csv`.
- `results/remote_pull_hunyuan_text_root_meshspace_20260511/hunyuan_text_root_meshspace_metrics.csv`.
- `results/remote_pull_hunyuan_text_root_meshspace_20260511/hunyuan_text_root_meshspace_metrics.json`.
- Related local metric scripts: `assets/recursive_growth_mesh_metrics.py`, `assets/publication_baseline_metrics_20260510.py`, `assets/mesh_space_trivial_recursion_baseline_20260510.py`, `assets/hunyuan_text_root_meshspace_baseline_20260511.py`, `assets/effective_resolution_metrics_20260510.py`.

## 1. Recommendation Summary

Experiment 3 should be framed as a novelty gate for "sparse-latent grammar state vs mesh-space alternatives", not as a general 3D generation leaderboard. The strongest clean claim is:

> One-shot generators and mesh/latent copy controls can make plausible objects or repeated geometry, but they do not maintain a grammar-readable, root-attached recursive state across depth. PS-RSLG's advantage is typed sparse-latent state plus per-depth admissibility projection and re-encoding, with texture/PBR treated as export compatibility.

Main text should use a compact Table 3 with only claim-bearing metrics:

- structural validity: status, raw components, occupancy components, LCR, copy repetition / route flags;
- surface/export scale: faces or vertices, MB, render/import status;
- semantic/visual: a small human/GPT placeholder score column if not yet closed, otherwise keep in supplement.

Supplement should hold full raw columns, smoothing/remesh upper-bound rows, runtime/memory, visual-semantic rubrics, effective-resolution proxy, and per-case prompts/paths.

## 2. Recommended Metric Set

### A. Structure Validity

1. `raw_component_count`
   - Definition: number of connected components under raw mesh face connectivity.
   - Input: OBJ/GLB asset path in `source_path`, `asset_path`, `obj_path`, or `glb_path`.
   - Existing script: `assets/recursive_growth_mesh_metrics.py` computes `component_count`; baseline manifests store it as `raw_component_count`.
   - Paper use: main-text diagnostic for mesh copy-paste failure. Very high raw component count means the mesh route concatenated many unmerged islands even when voxel LCR is high.

2. `largest_component_vertex_ratio`
   - Definition: vertices in largest raw face-connected component divided by total vertices.
   - Input: same mesh files as above.
   - Existing script: `assets/recursive_growth_mesh_metrics.py`.
   - Paper use: supplement or diagnostic column. It is especially revealing for Hunyuan text-root mesh-space: values are about `1e-5`, because copied instances remain separate raw mesh islands.

3. `occupancy_component_count_6n`
   - Definition: number of 6-neighborhood connected components after vertex voxelization in a normalized grid, currently resolution 64 in `recursive_growth_mesh_metrics.py`.
   - Input: mesh vertices from OBJ/GLB.
   - Existing script: `assets/recursive_growth_mesh_metrics.py`; stored as `occupancy_component_count_6n`.
   - Paper use: main text, but never alone. It is robust to unwelded tube pieces and useful for coarse support attachment, but can over-credit close copy-paste routes.

4. `LCR` / `largest_occupancy_component_ratio_6n`
   - Definition: largest 6-neighborhood occupancy component voxel count divided by occupied voxel count.
   - Input: mesh vertices from OBJ/GLB.
   - Existing script: `assets/recursive_growth_mesh_metrics.py`; aggregators normalize it into `LCR`.
   - Paper use: main text as the primary coarse support-connectivity proxy. Must be paired with raw components and route flags.

5. `root_reachability`
   - Definition: fraction or binary status indicating whether reported active support remains reachable from the declared root component through admissible connectors.
   - Input: PS-RSLG sidecar/state trace with root id, active support, connector certificates; for mesh baselines this should be `N/A` or `not available`.
   - Existing script: not closed in the baseline manifest; current columns are present but mostly blank.
   - Needs script: a small state-trace evaluator that reads PS-RSLG per-depth sidecars and emits `root_reachability`, `active_orphan_handle_count`, `orphan_fragment_ratio`, and `deleted_or_inactive_support_ratio`.
   - Paper use: main text only for PS-RSLG/projection ablation once sidecars are standardized; otherwise supplement/gated.

6. `copy_repetition_score`
   - Definition: binary or normalized score that marks direct repeated use of the same root mesh/latent copy without grammar-readable state update. Hunyuan text-root rows currently report `1.0`.
   - Input: route manifest or baseline generator output, not inferred from geometry.
   - Existing script: `assets/hunyuan_text_root_meshspace_baseline_20260511.py` and mesh-space manifests emit it.
   - Paper use: main text for mesh-space copy baselines, because it explains why high LCR is not recursive-state success.

7. Route flags
   - Definition: `projection_used`, `latent_update_used`, `generator_calls_after_root`, `weld_boolean_or_remesh_used`, `post_copy_smoothing_iterations`, `latent_or_mesh_repair_used`.
   - Input: method manifest rows.
   - Existing script: Hunyuan text-root baseline already emits these; older Trellis2 mesh-space rows have equivalent notes but not all flags.
   - Needs script: optional manifest-normalization pass to backfill route flags for all Experiment 3 rows.
   - Paper use: main text in compressed form: "route" or "state update" column.

### B. Surface Quality

1. `vertices`, `faces`, `file_size_mb`
   - Definition: mesh size and asset footprint.
   - Input: OBJ/GLB files.
   - Existing scripts: all baseline metric scripts emit these.
   - Paper use: main text as scale/context columns, or supplement if Table 3 gets too wide.

2. `surface_area_est`, `face_area_mean`, `face_area_median`
   - Definition: estimated triangle surface area and face area statistics.
   - Input: mesh vertices/faces.
   - Existing script: `assets/recursive_growth_mesh_metrics.py` has `face_area_stats`; Hunyuan text-root metrics include `surface_area_est`.
   - Paper use: supplement. These are useful for roughness/scale sanity, but not central to novelty.

3. Normal / non-manifold / degenerate face diagnostics
   - Definition: counts of degenerate faces, non-manifold edges, self-intersection proxy, and watertightness if trimesh can compute them.
   - Input: OBJ/GLB.
   - Existing script: not in current selected-final baseline manifest.
   - Needs script: small `trimesh`-based supplement evaluator. Do not block main claim on this.
   - Paper use: supplement/export QA only.

4. Smoothing/remesh upper-bound delta
   - Definition: difference between direct mesh concat row and smoothing/remesh row in LCR/components/surface stats.
   - Input: paired direct and `laplacian3` rows for Hunyuan text-root; optional remesh rows for procedural baselines if available.
   - Existing script: `assets/hunyuan_text_root_meshspace_baseline_20260511.py` emits `post_copy_smoothing_iterations`.
   - Paper use: supplement or a short note: smoothing does not create recursive state and did not repair raw component count in current Hunyuan rows.

### C. Local Detail Consistency

1. `local_feature_scale_proxy`
   - Definition: `bbox_diag / sqrt(face_count)`, lower means finer average triangle-scale detail at object scale.
   - Input: mesh faces and bounding box.
   - Existing script: `assets/effective_resolution_metrics_20260510.py`.
   - Paper use: supplement/status unless the same-root/same-budget protocol is closed.

2. `terminal_detail_count_proxy`
   - Definition: occupied voxel count when available; otherwise vertices/faces as a fallback terminal-detail proxy.
   - Input: occupancy metrics or mesh counts.
   - Existing script: `assets/effective_resolution_metrics_20260510.py`.
   - Paper use: supplement. Current evidence is proxy, not universal effective-resolution proof.

3. `zoom_retention_score`
   - Definition: current proxy `LCR * (1 + box_count_dimension_proxy / 3)`.
   - Input: occupancy LCR and box-counting proxy.
   - Existing script: `assets/effective_resolution_metrics_20260510.py`.
   - Paper use: supplement or figure caption support for zoom diagnostics, not a main superiority claim.

4. Handle/detail survival
   - Definition: fraction of typed terminal handles or local motifs surviving after each depth and after export.
   - Input: PS-RSLG state traces plus matched render/mesh diagnostics.
   - Existing script: not closed.
   - Needs script: sidecar evaluator keyed by root/depth/operator, with matched camera/ROI metadata.
   - Paper use: future main metric if closed; current text should not claim it quantitatively.

### D. Texture / Export Compatibility

1. `render_import_success` / `visual_qa_status`
   - Definition: whether asset imports into local renderer and whether white/PBR preview exists.
   - Input: manifest `render_path`, `preview_path`, GLB path, image path.
   - Existing script: `assets/publication_baseline_metrics_20260510.py` normalizes available rows; Hunyuan protocol notes contact sheet path.
   - Paper use: main or supplement as compatibility, not topology.

2. GLB/PBR presence
   - Definition: GLB exists, material slots/textures present, expected PBR channels available if inspected.
   - Input: GLB files.
   - Existing script: partial via file paths and import/render QA; no complete PBR-channel table in current metrics.
   - Needs script: lightweight GLB inspector for material count, texture image count, channels, file size, renderer warnings.
   - Paper use: supplement; main text can say selected projected states enter the frozen Trellis2 texture/PBR export path.

3. Procedural+Trellis2 texture/PBR route flag
   - Definition: whether a classical procedural support was passed through the same texture/export route.
   - Input: traditional procedural baseline manifests and texture export paths.
   - Existing evidence: paper text says traditional supports can become renderable textured GLBs, but table integration is not as clean as Trellis2/Hunyuan baseline manifest.
   - Needs script: manifest row unification for classical procedural, procedural+smoothing/remesh, and procedural+Trellis2 texture/PBR.
   - Paper use: important protocol fairness statement, likely supplement table plus short main-text note.

### E. Visual-Semantic Score

1. Human visual QA score
   - Definition: 1-5 or 0-2 rubric for category match, recursive motif readability, attachment plausibility, local detail, material plausibility.
   - Input: standardized contact sheets / fixed Blender renders.
   - Existing evidence: qualitative visual audits exist in docs, but not a clean numeric table.
   - Needs script/process: a CSV template and blind/randomized sheet IDs. Recommended fields: `category_match`, `recursive_readability`, `junction_naturalness`, `artifact_penalty`, `material_match`, `overall`.
   - Paper use: placeholder only unless scored by at least 2 raters or a predeclared rubric.

2. GPT/vision score placeholder
   - Definition: model-based score on fixed renders using the same rubric.
   - Input: fixed white/PBR renders and prompts.
   - Existing evidence: none closed in named sources.
   - Needs script: batch prompt + image list + cached outputs.
   - Paper use: supplement placeholder only. Do not present as final quantitative proof without cached prompts, model version, and calibration examples.

3. Text-image/CLIP-style semantic score
   - Definition: similarity between render and target prompt/category.
   - Input: rendered images and textual target descriptions.
   - Existing evidence: not present in read sources.
   - Needs script: optional; lower priority than human QA.
   - Paper use: supplement at most, because it will not test recursive-state validity.

### F. Runtime / Memory

1. Per-row runtime
   - Definition: root generation time, shape generation time, texture/export time, mesh grammar time, metric/render time.
   - Input: logs/manifests. Hunyuan protocol has root T2I and shape seconds in prose; Hunyuan text-root metrics rows have `generator_calls_after_root=0` but not all timing fields in the pulled CSV.
   - Existing evidence: Hunyuan protocol lists T2I sec and shape sec for root generation; `effective_resolution_metrics_20260510.py` can read `results/runtime_token_growth_aggregate_20260510/runtime_token_growth_case_summary.csv` for PS-RSLG-related rows if present.
   - Needs script: normalize runtime/memory fields across baseline routes.
   - Paper use: supplement. Main text can include "generator calls after root" as a fairness flag.

2. Peak GPU memory / peak CPU memory
   - Definition: peak allocation during root generation, recursive execution, texture export, or metric pass.
   - Input: run logs or profiler sidecars.
   - Existing evidence: not closed in named sources.
   - Needs script: future instrumentation only.
   - Paper use: supplement/future; do not claim.

### G. Human / GPT Placeholders

Use explicit placeholder columns if the table needs to show planned evaluation:

- `Human QA`: `pending`, `pass`, `mixed`, `fail`, or numeric score if rubric is done.
- `GPT/vision QA`: `pending` until model, prompts, images, and cache are fixed.
- `Semantic note`: short manual label such as `plausible one-shot`, `fragmented`, `copy-paste`, `connected scaffold`, `selected candidate`.

Do not mix these with closed geometry metrics unless the caption says which columns are measured and which are QA annotations.

## 3. Candidate Table 3 Layout

### Main-Text Table 3: Compact Novelty Gate

Recommended columns:

| Case | Route | Method | State update | Projection | Repair/smooth | Inst. | Raw comps | Occ. comps | LCR | Copy rep. | Faces | MB | Status |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|

Suggested rows:

- `vine`, `pyrite`, `coral` x Trellis2 one-shot image condition.
- `vine`, `pyrite`, `coral` x Trellis2 trivial latent transform-copy.
- `vine`, `pyrite`, `coral` x Trellis2 mesh-space generated-root direct merge.
- `tree_trunk_branch`, `pyrite_crystal_root`, `coral_branch_root` x Hunyuan text-root mesh-space direct merge.
- Optional Hunyuan `laplacian3` rows only if the table has room; otherwise supplement as smoothing upper-bound.
- Classical procedural mesh, procedural+smoothing/remesh, procedural+Trellis2 texture/PBR: include one compact aggregate or three representative rows if the manifests are cleanly unified.
- PS-RSLG selected/strict rows for `vine`, `pyrite`, `coral`, with strict vs selected explicitly separated. Do not replace weak strict vine with selected vine without labeling it.

Main-text metrics:

- Must include: route flags, raw components, occupancy components, LCR, copy repetition, status.
- Include if space: faces, MB, render/import status.
- Avoid in main Table 3 unless closed: human/GPT score, runtime/memory, local detail proxies.

Caption rule:

- "LCR is an occupancy connectivity proxy, not a topology proof."
- "Smoothing/remesh rows are mesh-route upper bounds and do not introduce recursive-state update."
- "Selected PS-RSLG rows are visual candidates unless the row is explicitly labeled strict protocol."

### Supplement Table S-Experiment-3A: Full Geometry / Export

Columns:

| Case | Method | Variant | Prompt/root | Obj/GLB | Vert. | Faces | Raw comps | Largest raw ratio | Weld comps | Occ comps | LCR | Surface area | Face area med. | GLB MB | Render QA |

Include all selected-final rows from `publication_baseline_master_manifest_20260510.csv` and Hunyuan text-root rows.

### Supplement Table S-Experiment-3B: Route Audit

Columns:

| Method | Root source | Generator calls after root | Latent update | Projection | Weld/boolean/remesh | Smoothing iters | Texture/PBR route | Copy repetition | Allowed claim |

This table is valuable because it prevents reviewers from reading mesh-space copies as learned recursive generation.

### Supplement Table S-Experiment-3C: Visual / Semantic QA Placeholder

Columns:

| Case | Method | Render sheet | Category match | Recursive motif readability | Junction naturalness | Material match | Overall | Rater/source |

Keep empty/pending until scored.

### Supplement Table S-Experiment-3D: Runtime / Memory

Columns:

| Method | Case | Root gen sec | Shape/mesh sec | Recursive exec sec | Texture/export sec | Metric/render sec | Peak GPU GB | Peak CPU GB | Notes |

Current evidence is incomplete, so this should not be a main claim yet.

## 4. Paper Experiment-Section Logic

### 4.1 Why Hunyuan Mesh-Based Route Fails

Use the fair text-root protocol, not the older full recursive-guide one-shot result, when discussing mesh-space recursion.

Closed local evidence:

- The fair Hunyuan route generated one reusable root primitive per case, then copied it by deterministic S/R/T grammar with no generator call after root.
- Direct rows:
  - `tree_trunk_branch`: 13 instances, 156000 faces, raw components 153608, occupancy components 40, LCR 0.9977, copy repetition 1.0.
  - `pyrite_crystal_root`: 25 instances, 300000 faces, raw components 283875, occupancy components 3, LCR 0.9293, copy repetition 1.0.
  - `coral_branch_root`: 21 instances, 252000 faces, raw components 213465, occupancy components 3, LCR 0.9159, copy repetition 1.0.
- Laplacian smoothing rows remain copy-paste rows. They do not change the raw component count in current Hunyuan metrics and do not add latent update, projection, or grammar-readable handles.

Paper wording:

- Say "the mesh route can create a repeated object and may achieve high occupancy proximity, but the raw mesh remains a collection of repeated root islands and exposes no recursive state for the next rule."
- Do not say "Hunyuan fails at 3D generation." The fair claim is narrower: one-shot root mesh + mesh-space S/R/T composition is not a substitute for sparse-latent recursive-state execution.

### 4.2 Why Trellis2 Latent-Copy Fails

Closed local evidence from the current summary table:

- Vine latent-copy: raw components 283, occupancy components 9, LCR 0.689.
- Pyrite latent-copy: raw components 985, occupancy components 100, LCR 0.102.
- Coral latent-copy: raw components 2208, occupancy components 39, LCR 0.824, labeled uncontrolled copy.

Paper wording:

- Direct sparse support/feature copy is a strong negative control because it touches the same model substrate, but it bypasses typed handles, masks, projection, and decode/re-encode admission.
- The failure is not just "bad geometry"; it is that copied sparse support does not become certified active support with valid frontier/handle semantics for the next depth.
- For coral, avoid over-reading LCR 0.824 as total failure on coarse occupancy. The safer statement is "it remains uncontrolled and fragmented relative to the recursive-state contract."

### 4.3 Why One-Shot Trellis2 Is Not Enough

Closed local evidence:

- Vine one-shot: plausible and LCR 1.0.
- Pyrite one-shot: occupancy components 17, LCR 0.127.
- Coral one-shot: occupancy components 30, LCR 0.600.

Paper wording:

- One-shot generation is an object prior, not an execution state.
- It may produce plausible individual assets, and vine can look good, but it does not guarantee the requested recursive attachment structure or expose reusable typed handles across depth.
- This is a baseline for object plausibility, not a claim that Trellis2 cannot generate attractive objects.

### 4.4 Where PS-RSLG Has Advantage

Use the advantage language precisely:

- PS-RSLG makes the grammar own the recursive state: active support, typed handles, rule traces, connector/projection decisions.
- The frozen generator is used as codec/local realization/export path, not as a post-hoc topology solver.
- Per-depth projection prevents invalid detached fragments from becoming future handles.
- Decode/project/re-encode turns final connectedness into an intermediate-state admission problem.

Closed evidence:

- Current selected PS-RSLG pyrite and coral rows have occupancy components 1 and LCR 1.0.
- Selected vine candidate has LCR 0.999 but occupancy components 4; strict vine row is weak and must remain labeled as such.
- Masked naturalization evidence supports local surface/material realization under projection, not topology repair.

Safe wording:

- "In the tested pyrite/coral rows, PS-RSLG preserves a connected projected support where one-shot, latent-copy, and mesh-space routes fragment or remain copy-paste controls."
- "For vine, the strict row remains weak, while a selected visual candidate exists; therefore vine should not be used as the strongest quantitative proof."

Avoid:

- "PS-RSLG universally outperforms mesh-space recursion."
- "Texture/PBR proves topology."
- "Masked naturalization repairs global topology."
- "Effective resolution is proven generally."

## 5. Existing Evidence Closure

### Closed Enough For Main Text

- Trellis2 one-shot vs Trellis2 latent-copy vs Trellis2 mesh-space generated-root vs PS-RSLG selected/strict rows are locally present in `publication_baseline_master_manifest_20260510.csv` and the LaTeX draft table.
- Coral mesh-space generated-root row is complete and integrated; it is a clean negative control despite high LCR because raw components/copy-paste diagnose failure.
- Hunyuan text-root mesh-space fair route is now locally pulled with 3 direct rows and 3 smoothing rows; it can replace the older "future Hunyuan mesh route" statement in any new protocol/table draft.
- Hunyuan text-root direct rows support the mesh-space failure argument: high raw component counts, `copy_repetition_score=1.0`, no generator calls after root, no projection, no latent update.
- Trellis2 latent-copy failure is quantitatively supported by fragmentation metrics.
- PS-RSLG pyrite/coral selected rows are connected under current occupancy proxy and can support a cautious positive claim.

### Closed Only As Compatibility / Diagnostic

- Procedural+Trellis2 texture/PBR shows classical supports can enter the texture/export route. This supports fairness/protocol separation, not a PS-RSLG structural superiority proof.
- Hunyuan one-shot image/full-recursive-guide rows are object-generation baselines or broad pool QA; they should not be used as the fair mesh-space recursion baseline.
- Effective-resolution metrics are proxy/status evidence only.
- Masked naturalization metrics support local continuity under projection, not global topology repair.
- Smoothing/remesh rows are upper bounds for mesh-space appearance, not recursive-state rows.

### Not Closed / Do Not Write As Quantitative Proof

- Universal sparse-latent superiority over all mesh-space recursion.
- Same-root, same-seed, same-depth closure across every listed method family.
- Runtime/memory comparison across all methods.
- Human/GPT visual-semantic scores.
- Root reachability and orphan-handle metrics for all rows.
- Watertight topology or manifoldness.
- Category-wide naturalness for coral/tree/vine.
- Effective-resolution superiority under a strict same-budget protocol.

## 6. Concrete Next Local-Only Script Gaps

No new experiments are needed for this protocol note, but the following small local scripts would make Table 3 cleaner later:

1. `assets/experiment3_route_manifest_normalize_20260511.py`
   - Read baseline master manifest plus Hunyuan text-root metrics.
   - Emit one unified CSV with route flags for all methods.

2. `assets/experiment3_table3_export_20260511.py`
   - Read unified CSV.
   - Emit compact main Table 3 and supplement tables.

3. `assets/experiment3_glb_export_qa_20260511.py`
   - Inspect GLB existence, importability, material/texture counts, renderer warning status.

4. `assets/experiment3_psrslg_state_trace_metrics_20260511.py`
   - Read PS-RSLG sidecars.
   - Emit root reachability, active orphan handles, handle survival, projection deletion/inactivation mass.

5. `docs/evaluation/experiment3_visual_qa_rubric_20260511.md`
   - Freeze human/GPT scoring rubric before scores are generated.

## 7. Suggested One-Paragraph Experiment 3 Text

Draft wording for later paper editing:

"We evaluate the novelty gate with routes that a straightforward practitioner might try before adopting a sparse-latent recursive state: classical procedural meshes, smoothed/remeshed procedural outputs, procedural supports passed through the same texture/PBR export path, one-shot image-conditioned generation, direct sparse-latent copy, and mesh-space recursion from a generated root mesh. The key diagnostic is not final visual plausibility alone, but whether the intermediate representation remains root-attached and grammar-readable after each depth. One-shot Trellis2 can produce plausible individual objects, but it does not enforce recursive attachment in the pyrite and coral targets. Direct Trellis2 latent copy and generated-root mesh-space composition expose the failure mode more directly: repeated fragments may be close in occupancy, and may even render as an asset, but they are still copy-paste islands without typed handles, projection, or re-encoded active support. In the tested pyrite/coral rows, PS-RSLG keeps the recursive state inside the sparse-latent execution loop and applies projection before later rules fire, yielding connected projected support under the current occupancy diagnostic. We therefore treat texture/PBR export and smoothing as compatibility/upper-bound controls, not as substitutes for recursive-state validity."

