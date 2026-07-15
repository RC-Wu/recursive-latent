# Tree-Root First-Split 20260511q Execution Plan

Date: 2026-05-11 CST  
Status: remote SLat sweep complete; metrics and Blender QA reject q as publication-grade root evidence  
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU policy: use only remote GPUs `4,5,6,7`.  
Storage policy: remote project must stay under the relaxed `200GB` cap; pull selected outputs only.  
Evidence policy: input root modules are not final evidence. A q case is not publication-grade until it has remote SLat OBJ/GLB outputs, metrics CSV/JSON, Blender QA, depth/contact/zoom renders, and paper-safe provenance wording.

## Why q Exists

`20260511p` proved that whole-rootfan perturbation is the wrong next step for the fourth hero `tree_root_leaf` root side.

- `spider_runner`, `fern_part`, `potted_tip`, and `tree_pine` are usable supplement candidates.
- All `tree_rootfan_firstsplit_*` rows are rejected or diagnostic because the depth change is too weak and fragmentation/component counts are high.
- The failure is not only grammar parameters; the V23 whole rootfan is too diffuse for the mask to reliably lock onto the semantic first split.

q therefore changes the input root acquisition step: create clean first-split root modules with explicit trunk, split, branch, terminal-rootlet anchors, then run the same remote SLat/grammar workflow.

## Completed Local Input Acquisition

Added:

- `assets/prepare_tree_root_firstsplit_candidates_20260511q.py`

Generated:

- `results/tree_root_firstsplit_candidates_20260511q/`
- `results/tree_root_firstsplit_candidates_20260511q/manifest.csv`
- `results/tree_root_firstsplit_candidates_20260511q/initial_metrics.csv`
- `results/tree_root_firstsplit_candidates_20260511q/tree_root_firstsplit_candidates_contact_sheet.png`

Eight candidate input root modules were generated:

| candidate | orientation | suggested axis/sign | role |
|---|---|---:|---|
| `first_split_root_down_compact_a` | downward original z | `y,+1` | compact sanity root |
| `first_split_root_down_smooth_b` | downward original z | `y,+1` | smoother compact root |
| `first_split_root_down_sidecar_c` | downward original z | `y,+1` | primary q candidate |
| `first_split_root_down_deep_dense_d` | downward original z | `y,+1` | primary q candidate with more rootlets |
| `first_split_root_up_compact_e` | upward original z | `y,-1` | orientation stress |
| `first_split_root_up_smooth_f` | upward original z | `y,-1` | orientation stress |
| `first_split_root_up_sidecar_g` | upward original z | `y,-1` | orientation stress |
| `first_split_root_up_asym_deep_h` | upward original z | `y,-1` | asym/deeper stress |

All local inputs pass initial connectivity:

- `mesh_component_count = 1`
- `largest_mesh_component_vertex_ratio = 1.0`
- face counts range from `840` to `2222`

This only validates root input quality; it does not validate recursive generation.

## q Grammar Plan

Modify:

- `assets/trellis2_recursive_slat_grammar_workflow.py`

Add narrow q aliases that preserve the p root-sidecar idea but tune it for clean root modules rather than an entire rootfan:

- `v25q_root_module_sidecar`
- `v25q_root_module_chain`
- `v25q_root_module_dense_rootlets`

Fallback aliases in the same run:

- `v25p_root_first_split_sidecar`
- `v25p_root_first_split_then_rootlets`
- `v25n_root_first_split_taper`
- `v25l_root_primary_branch`

## Remote Launcher Plan

Add:

- `assets/run_tree_root_firstsplit_remote_20260511q.sh`

Four lanes:

- GPU 4: `down_compact_a` and `down_smooth_b`, depth 4.
- GPU 5: `down_sidecar_c` and `down_deep_dense_d`, depth 4.
- GPU 6: `up_compact_e` and `up_smooth_f`, depth 4.
- GPU 7: `up_sidecar_g` and `up_asym_deep_h`, depth 4.

Each run writes manifest, logs, summaries, and OBJ depth outputs under:

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/tree_root_firstsplit_recursive_remote_20260511q`

## QA Gate

After remote completion:

1. Run remote `metrics`.
2. Pull light artifacts and selected depth sequences only.
3. Render selected final depth and depth sequences with controlled Blender material on white background.
4. Promote only if:
   - `PLCR >= 0.95`, preferred vertex LCR `>= 0.95`;
   - primary components remain low enough that Blender does not show visible islands;
   - d0-d4 shows obvious thick-to-thin recursive root hierarchy, not only token dust;
   - the root growth direction is semantically correct for the tree-root case.

Expected q outcomes:

- If `down_sidecar_c` or `down_deep_dense_d` passes, use it as the root-side subprogram for the fourth hero.
- If only up variants pass visually, keep them as orientation diagnostics and decide whether to flip/compose them with the hero source.
- If all q variants fail after clean input acquisition, the blocker becomes SLat root-branch grammar expressivity rather than source-root quality.

## 2026-05-11 q Closeout

Remote q completed successfully as an execution run, but it does **not** pass the publication visual gate.

Evidence written locally:

- Metrics: `results/tree_root_firstsplit_recursive_remote_20260511q_pull/metrics/tree_root_firstsplit_metrics_20260511q.csv`
- Gate summary: `results/tree_root_firstsplit_recursive_remote_20260511q_pull/analysis/metric_gate_summary_20260511q.csv`
- Selected OBJ pull manifest: `results/tree_root_firstsplit_recursive_remote_20260511q_pull/analysis/selected_obj_pull_20260511q.csv`
- Selected OBJ depth sequences: `results/tree_root_firstsplit_recursive_remote_20260511q_pull/selected_meshes_20260511q/`
- Blender QA renders: `results/tree_root_firstsplit_recursive_remote_20260511q_pull/blender_qa_20260511q/renders_iso/`
- Blender depth contact sheet: `results/tree_root_firstsplit_recursive_remote_20260511q_pull/blender_qa_20260511q/tree_root_firstsplit_q_selected_depth_sequences_contact_sheet.png`

Metric verdict:

- No q `(case, grammar)` pair clears the conservative publication gate of final `PLCR >= 0.95`, final vertex LCR `>= 0.95`, low primary components, and visible depth-change proxy.
- Best metric-down row, `firstsplit_down_compact_a_d4_20260511q / v25n_root_first_split_taper`, reaches only final `PLCR=0.906`, vertex LCR `0.944`, occupancy LCR `0.906`.
- Target-oriented down sidecar row, `firstsplit_down_sidecar_c_d4_20260511q / v25p_root_first_split_sidecar`, reaches final `PLCR=0.932`, vertex LCR `0.949`, occupancy LCR `0.932`, with `17` primary components.
- The best up-orientation diagnostic, `firstsplit_up_sidecar_g_d4_20260511q / v25q_root_module_chain`, has final `PLCR=0.954`, vertex LCR `0.982`, occupancy LCR `0.954`, but still has `14` primary components, weak depth-change proxy, and unstable depth history.

Visual verdict:

- q produced real remote SLat OBJ outputs and valid Blender renders, but the depth sequences show weak semantic growth. Most d1-d4 changes read as small floating rootlet debris or shaved-off terminal fragments rather than natural thick-to-thin first-split hierarchy.
- Down-oriented candidates keep a plausible trunk/split silhouette but accumulate visible fine islands near branch tips.
- The up-oriented diagnostic can look cleaner in silhouette, but it partially deletes/attenuates the lower root mass and still does not show a convincing four-depth recursive root hierarchy.

Conclusion:

- q is diagnostic negative evidence, not hero/root-side success.
- The local first-split inputs are clean; therefore the remaining blocker is not only source-root connectivity. The current SLat root operators still select/copy too much fragile terminal detail and do not preserve a visually coherent coarse root branch across four depths.
- Next loop should select or generate a coarse first-split branch module with rootlet detail suppressed, use one-sided visible coarse side-branch growth first, and add small rootlets only after a stable coarse branch passes Blender QA.

Paper-method note:

- q root modules use explicit, manually defined semantic anchors (`first_split_anchor_node`, trunk, branch mid/terminal nodes). They are not automatic semantic root discovery. Paper wording should describe PS-RSLG runs as authored roots/rules with declared or geometry-heuristic handles.

## 2026-05-11 r Follow-Up Launch

r is the immediate follow-up to q. It changes both the input acquisition and grammar:

- Input root pool: `results/tree_root_coarse_candidates_20260511r/`
- Input generator: `assets/prepare_tree_root_coarse_candidates_20260511r.py`
- Remote launcher: `assets/run_tree_root_coarse_remote_20260511r.sh`
- New grammar aliases in `assets/trellis2_recursive_slat_grammar_workflow.py`:
  - `v25r_root_coarse_visible`
  - `v25r_root_coarse_pair`
  - `v25r_root_coarse_then_hairline`

Design change:

- r roots suppress terminal root hairs and keep only coarse trunk/first-split branches.
- r operators copy a capped, coarse mid-branch mask with long bridges. Fine rootlets are absent or limited to a tiny diagnostic late pass.
- The goal is to first make the four-depth coarse thick-to-thin hierarchy visually stable. Root hairs can only be reintroduced after this gate passes.

Local input evidence:

- 8 coarse roots generated.
- Local input metrics pass single-component/LCR gate.
- Contact sheet: `results/tree_root_coarse_candidates_20260511r/tree_root_coarse_candidates_contact_sheet.png`

Remote launch:

- Output target: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/tree_root_coarse_recursive_remote_20260511r`
- Started: `2026-05-11T18:36:09+08:00`
- GPUs: `4,5,6,7`
- Initial pids: `629748 629749 629750 629751`
- Initial status after 4 seconds: all four lanes running, `OBJ_COUNT=0`, `PREVIEW_COUNT=0`.

First r attempt result:

- All lanes exited quickly with `status=failed`.
- Cause: workflow registry bug, not model failure. New `v25r_*` aliases existed in `GRAMMARS`, but `apply_op` did not register the underlying `root_module_coarse_*_20260511r` functions.
- Failed output directory is retained as code-run evidence: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/tree_root_coarse_recursive_remote_20260511r`.

Fix:

- Registered `root_module_coarse_pair_20260511r`, `root_module_coarse_visible_20260511r`, and `root_module_coarse_then_hairline_20260511r` in `apply_op`.
- Created/started clean rerun launcher `assets/run_tree_root_coarse_remote_20260511r_fix.sh`.
- Output target: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/tree_root_coarse_recursive_remote_20260511r_fix`.
- Started: `2026-05-11T18:38:11+08:00`.
- Initial pids: `633815 633816 633817 633818`.
- Initial status after 4 seconds: all four lanes running, `OBJ_COUNT=0`, `PREVIEW_COUNT=0`.

r_fix is not complete until remote summaries, metrics, selected OBJ pulls, Blender QA, and a pass/reject verdict are written.

## 2026-05-11 r/r_fix Path Correction And Metric Gate

The `r_fix` rerun did execute after the `apply_op` registry fix, but its launcher had a self-call path bug:

- `assets/run_tree_root_coarse_remote_20260511r_fix.sh` set `OUT=...20260511r_fix`;
- however, `start_main4()` still called `run_tree_root_coarse_remote_20260511r.sh` for the four lanes;
- therefore the successful rerun wrote real outputs into the original remote directory:
  `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/tree_root_coarse_recursive_remote_20260511r`;
- the `...20260511r_fix` directory contains only the fix launcher manifest, nohup logs, and pid files.

This is an execution bookkeeping bug, not a model or grammar failure. The local and remote `r_fix` launcher have now been patched so future reruns self-call `run_tree_root_coarse_remote_20260511r_fix.sh`.

Current evidence:

- remote successful output directory: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/tree_root_coarse_recursive_remote_20260511r`
- output count: `120` OBJ meshes, `120` previews, `8` summary JSON files
- local light pull: `results/tree_root_coarse_recursive_remote_20260511r_pull/`
- metrics: `results/tree_root_coarse_recursive_remote_20260511r_pull/metrics/tree_root_coarse_metrics_20260511r.csv`

Metric screen:

- Down-direction rows with final `PLCR >= 0.95` exist:
  - `coarse_down_smooth_b_d4_20260511r / v25r_root_coarse_visible`: final `PLCR=0.9649`, final primary components `6`, final vertex LCR `0.9832`;
  - `coarse_down_swept_asym_d_d4_20260511r / v25r_root_coarse_visible`: final `PLCR=0.9572`, final primary components `6`, final vertex LCR `0.9820`;
  - `coarse_down_compact_a_d4_20260511r / v25r_root_coarse_visible` and `v25r_root_coarse_then_hairline`: final `PLCR=0.9546`, final primary components `4`, final vertex LCR `0.9696`.
- However, the d0-to-d4 bbox extent deltas are very small for the best rows. These rows are therefore not paper-positive until Blender depth-sequence QA confirms visible coarse thick-to-thin growth rather than a near-no-op.
- `v25r_root_coarse_pair` and `v25l_root_primary_branch` rows generally fragment more and are currently diagnostic/risk rows, not positives.

Immediate QA selection:

- Pull full d0-d4 OBJ sequences for:
  - `coarse_down_smooth_b_d4_20260511r / v25r_root_coarse_visible`;
  - `coarse_down_swept_asym_d_d4_20260511r / v25r_root_coarse_visible`;
  - `coarse_down_compact_a_d4_20260511r / v25r_root_coarse_visible`;
  - `coarse_down_compact_a_d4_20260511r / v25r_root_coarse_then_hairline`;
  - `coarse_down_thick_stub_c_d4_20260511r / v25r_root_coarse_visible` as a target-shape but metric-rejected stress row;
  - one up-direction row only as orientation diagnostic.

Pass boundary:

- Do not call r successful for the fourth hero root side unless controlled Blender renders show a clear d0-d4 root hierarchy, correct root-side direction, no visible large islands, and no terminal dust cloud.
- If Blender shows near-no-op geometry, r should be recorded as a metric-clean but visual-weak diagnostic, and the next loop should change the operator to visibly extend one coarse child branch before adding any fine rootlets.

## 20260511p Verdict To Preserve

Supplement candidates:

- `spider_runner_visible_chain`: visually depth-visible but with leaf tearing/noise; supplement only.
- `polyhaven_fern_part + v25k_spider_terminal_leaflet`: clean fern/leaf supplement candidate.
- `polyhaven_potted_leaves + v25l_spider_leaf_tip_clean`: semantically useful but render/face pressure.
- `tree_pine_leaf_visible + v25n/v25p`: clean-ish leaf/branch supplement, not root-side proof.

Rejected root rows:

- `root_yneg_sidecar`
- `root_ypos_sidecar`
- `root_fit052_then`

Reason: weak depth change plus fragmentation; not publication-grade.

## 2026-05-11 s Visible-Child Coarse Branch Plan

`20260511r` is now closed as diagnostic evidence, not a fourth-hero root-side positive.

Evidence from the r pull:

- Successful remote outputs are in `results/tree_root_coarse_recursive_remote_20260511r`, with a local pull at `results/tree_root_coarse_recursive_remote_20260511r_pull/`.
- Metrics include several down-oriented final rows above the coarse connectivity threshold, e.g. `coarse_down_smooth_b_d4_20260511r / v25r_root_coarse_visible` with final `PLCR=0.9649`, final primary components `6`, and final vertex LCR `0.9832`.
- Controlled/contact-sheet QA shows these rows are visually weak: d0 and d4 have nearly the same coarse silhouette, with the main change appearing as tiny terminal specks. This is a metric-clean near-no-op, not the requested thick-to-thin recursive root hierarchy.

Therefore s changes the operator, not the input pool:

- Input pool remains the clean coarse first-split roots from `results/tree_root_coarse_candidates_20260511r/`.
- New grammar aliases in `assets/trellis2_recursive_slat_grammar_workflow.py`:
  - `v25s_root_visible_child_far`
  - `v25s_root_visible_child_pair`
  - `v25s_root_visible_child_late_taper`
- New remote launcher: `assets/run_tree_root_coarse_remote_20260511s.sh`.

s operator intent:

- Select a mid-body first-split branch handle rather than fragile terminal rootlets.
- Move the selected handle several sparse cells outward and along the root growth direction with shorter, explicit support bridges.
- Force the d0..d4 sequence to visibly add a coherent coarse child branch, so it cannot pass solely by preserving the old silhouette.
- Keep the late-taper/rootlet variant diagnostic only; a positive must pass through coarse branch visibility first.

Remote lane plan:

- GPU 4: down compact/smooth, depth 4.
- GPU 5: down thick-stub/swept-asym, depth 4.
- GPU 6: up compact/smooth orientation diagnostics, depth 4.
- GPU 7: up thick-stub/swept-asym diagnostics, depth 4.

Pass boundary:

- Final row should maintain `primary_largest_component_ratio >= 0.95` and vertex LCR near `>= 0.95`, but metrics alone are not enough.
- Blender/contact-sheet QA must show a clear d0-to-d4 coarse branch hierarchy. Reject any row that keeps the same silhouette with only dust/hairline changes, even if PLCR is high.
- Down-oriented rows are the only candidates for the fourth-hero root side. Up-oriented rows remain orientation diagnostics unless explicitly flipped/composed later.
