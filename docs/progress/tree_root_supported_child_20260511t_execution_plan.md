# Tree-Root Supported-Child 20260511t Execution Plan

Date: 2026-05-11 CST  
Status: completed; diagnostic negative, not publication-grade root evidence  
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU policy: use only remote GPUs `4,5,6,7`.  
Evidence policy: t is not complete without remote OBJ outputs, metrics CSV/JSON, selected d0-d4 pull, controlled contact-sheet/Blender QA, and a paper-safe pass/reject verdict.

## Why t Exists

q failed because terminal/rootlet-heavy masks produced dust.  
r failed because coarse masks preserved connectivity but barely changed the silhouette.  
s fixed visible displacement, but the displaced child branch decoded as torn side sheets / point fragments rather than a continuous coarse root.

t is therefore a narrower repair: keep the visible child branch idea, but add an explicit sparse tube support between the source branch anchor and target child branch anchor before decode. The goal is a continuous coarse child root first; no fine rootlets or hairline claims are allowed at this stage.

## Code Changes

Modify:

- `assets/trellis2_recursive_slat_grammar_workflow.py`

New helper:

- `masked_target_copies_with_tube_support_20260511t`

New root operators:

- `root_module_supported_child_20260511t`
- `root_module_supported_child_single_20260511t`
- `root_module_supported_child_pair_20260511t`
- `root_module_supported_child_micro_20260511t`

New grammar aliases:

- `v25t_root_supported_child_single`
- `v25t_root_supported_child_pair`
- `v25t_root_supported_child_micro`

Remote launcher:

- `assets/run_tree_root_coarse_remote_20260511t.sh`

Input pool:

- `results/tree_root_coarse_candidates_20260511r/`

## Remote Lanes

Remote output:

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/tree_root_coarse_recursive_remote_20260511t`

Lanes:

- GPU 4: compact/smooth down, depth 4.
- GPU 5: thick-stub/swept-asym down, depth 4.
- GPU 6: compact/smooth up diagnostics, depth 4.
- GPU 7: thick-stub/swept-asym up diagnostics, depth 4.

Primary grammars:

- `v25t_root_supported_child_single`: main candidate.
- `v25t_root_supported_child_micro`: conservative sanity candidate.
- `v25t_root_supported_child_pair`: risk/stress candidate.
- `v25r_root_coarse_visible`: retained on smooth/swept only as r near-no-op control.

## Pass/Reject Gate

Positive candidate requires:

- Down-oriented sequence.
- d0-d4 shows a continuous child root branch, not torn sheets, floating dust, or hairline-only changes.
- Final PLCR preferably `>=0.95`; if lower, Blender must show a plausible connected main mass and low visible islands before any further naturalization.
- Vertex LCR and face component behavior must not collapse like s.
- Visual change must be readable in iso/front/side controlled renders.

Reject if:

- The support tube decodes as an artificial rod with no natural branch taper.
- Added geometry is still a torn sheet/point cloud.
- Metrics are high only because the row is near-no-op.
- Up-oriented rows pass; they remain diagnostics, not hero evidence.

## Immediate QA After Completion

1. Run remote metrics via `bash assets/run_tree_root_coarse_remote_20260511t.sh metrics`.
2. Pull metrics/logs/manifest.
3. Rank d0-d4 deltas against PLCR and vertex LCR.
4. Pull selected d0-d4 OBJ sequences for the best `single`, `micro`, one `pair`, one r control, and one up diagnostic.
5. Generate contact sheet and Blender ISO/front/side QA before any claim.

## 2026-05-11 t Closeout

Remote execution completed successfully:

- Remote output: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/tree_root_coarse_recursive_remote_20260511t`
- Local pull: `results/tree_root_coarse_recursive_remote_20260511t_pull/`
- Metrics: `results/tree_root_coarse_recursive_remote_20260511t_pull/metrics/tree_root_coarse_metrics_20260511t.csv`
- Rank summary: `results/tree_root_coarse_recursive_remote_20260511t_pull/analysis/d0_d4_rank_summary_20260511t.tsv`
- Contact sheet: `results/tree_root_coarse_recursive_remote_20260511t_pull/analysis/tree_root_coarse_20260511t_selected_d0d4_contact_sheet.png`
- Blender ISO sheet: `results/tree_root_coarse_recursive_remote_20260511t_pull/blender_qa_20260511t/tree_root_coarse_20260511t_blender_iso_sheet.png`

Metric/visual verdict:

- `coarse_down_compact_a_d4_20260511t / v25t_root_supported_child_pair` is the cleanest objective row: final `PLCR=0.9895`, primary components `6`, vertex LCR `0.9948`, and bbox diagonal ratio about `1.0013`.
- `coarse_down_thick_stub_c_d4_20260511t / v25t_root_supported_child_pair` is similar: final `PLCR=0.9885`, primary components `5`, vertex LCR `0.9968`, bbox diagonal ratio about `1.0096`.
- Blender QA shows that these high scores are mostly because the depth sequence remains visually close to the input root. The added supported child either disappears into the base branch or decodes as tiny speck/rod fragments.
- Compared with `20260511s`, `t` removes much of the torn sheet failure mode, but it does not create a readable four-depth thick-to-thin root hierarchy.

Conclusion:

- `t` is a useful diagnostic: explicit sparse tube support improves connectivity, but the current coarse-root input plus SLat mask still yields a near-no-op visual sequence.
- This should not be promoted in the paper, teaser, or hero `tree_root_leaf` claim.
- The next loop should change the input-acquisition stage: create stronger multiscale root modules where the desired thick-to-thin hierarchy is already continuous geometry before encode/decode, then use remote SLat recursion and QA as evidence. This becomes `20260511u`.
