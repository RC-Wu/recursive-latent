# Tree-Root Visible-Child 20260511s Execution Plan

Date: 2026-05-11 CST  
Status: completed; diagnostic negative, not publication-grade root evidence  
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU policy: use only remote GPUs `4,5,6,7`.  
Evidence policy: s is not complete without remote OBJ outputs, metrics CSV/JSON, selected d0-d4 pull, controlled Blender/contact-sheet QA, and a pass/reject verdict.

## Why s Exists

`20260511q` proved that clean first-split input roots alone do not solve the fourth hero root-side problem: terminal-heavy operators made dust and small islands.

`20260511r` suppressed root hairs and improved connectivity, but the best rows are visually too close to no-op. They preserve the base silhouette and add only tiny terminal specks. That makes r useful as diagnostic evidence only.

s changes the sparse-latent operator so the visual gate is decisive: it selects a mid-body branch handle, moves it visibly outward/along the growth direction, and bridges it back to the source. If it passes, d0-d4 should show coherent coarse child-root growth. If it fails, the failure should be obvious as fragmentation or semantic mismatch rather than hidden by high LCR.

## Code Changes

Modify:

- `assets/trellis2_recursive_slat_grammar_workflow.py`

New functions:

- `root_module_visible_child_20260511s`
- `root_module_visible_child_far_20260511s`
- `root_module_visible_child_pair_20260511s`
- `root_module_visible_child_late_taper_20260511s`

New grammar aliases:

- `v25s_root_visible_child_far`
- `v25s_root_visible_child_pair`
- `v25s_root_visible_child_late_taper`

Remote launcher:

- `assets/run_tree_root_coarse_remote_20260511s.sh`

Input pool:

- `results/tree_root_coarse_candidates_20260511r/`

## Remote Lanes

Remote output:

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/tree_root_coarse_recursive_remote_20260511s`

Lanes:

- GPU 4: `coarse_down_compact_a_d4_20260511s`, `coarse_down_smooth_b_d4_20260511s`
- GPU 5: `coarse_down_thick_stub_c_d4_20260511s`, `coarse_down_swept_asym_d_d4_20260511s`
- GPU 6: `coarse_up_compact_e_d4_20260511s`, `coarse_up_smooth_f_d4_20260511s`
- GPU 7: `coarse_up_thick_stub_g_d4_20260511s`, `coarse_up_swept_asym_h_d4_20260511s`

Primary grammars:

- `v25s_root_visible_child_far`
- `v25s_root_visible_child_pair`
- `v25s_root_visible_child_late_taper`

`v25r_root_coarse_visible` is kept on smooth/swept rows only as a direct r-vs-s sanity baseline.

## QA After Remote Completion

Run remote metrics:

```bash
bash /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/run_tree_root_coarse_remote_20260511s.sh metrics
```

Pull light artifacts first:

- `metrics/tree_root_coarse_metrics_20260511s.csv`
- `metrics/tree_root_coarse_metrics_20260511s.json`
- `tree_root_coarse_manifest_20260511s.tsv`
- logs and summaries

Select d0-d4 OBJ sequences for at least:

- down smooth + `v25s_root_visible_child_far`
- down swept + `v25s_root_visible_child_far`
- down thick-stub + `v25s_root_visible_child_far`
- down compact + `v25s_root_visible_child_pair`
- one late-taper diagnostic
- one up-orientation diagnostic

Run local contact sheet and Blender QA. A row is positive only if it passes both metrics and visual gates.

## Pass/Reject Gate

Pass candidate:

- Down-oriented sequence.
- d0-d4 visibly adds coherent coarse child-root mass from the first-split branch.
- Final primary LCR preferably `>=0.95` with low component count.
- No visible floating dust halo, hairline-only change, or terminal debris cloud.
- Depth changes remain readable in iso/front/side controlled renders.

Reject:

- r-style metric-clean near-no-op: high PLCR but almost unchanged silhouette and only tiny specks.
- Any row whose visible change is mostly disconnected islands or rootlet dust.
- Up-oriented rows as hero proof; they are diagnostics unless later flipped/composed deliberately.

## Claim Boundary

Until s passes the visual gate, the fourth hero `tree_root_leaf` root-side remains open. Paper wording should continue to say authored/geometric handles and diagnostic root-side attempts, not automatic semantic root discovery or completed dual root+leaf recursion.

## 2026-05-11 s Closeout

Remote execution completed successfully:

- 8 case lanes, 120 OBJ outputs, 120 previews, all summaries `status=ok`.
- Metrics and local QA were pulled to `results/tree_root_coarse_recursive_remote_20260511s_pull/`.
- Blender ISO QA sheet: `results/tree_root_coarse_recursive_remote_20260511s_pull/blender_qa_20260511s/tree_root_coarse_20260511s_blender_iso_sheet.png`.

Metric/visual verdict:

- `coarse_down_smooth_b_d4_20260511s / v25s_root_visible_child_far` is the best s row by combined objective: final `PLCR=0.9643`, final primary components `6`, and a real bbox diagonal increase of about `21.5%`. However, final vertex LCR is only `0.8826`, and Blender shows torn side sheets / small fragments rather than a continuous coarse root branch.
- `v25s_root_visible_child_pair` rows make depth change more visible but fragment further, with final down-oriented PLCR ranging roughly `0.62..0.86`.
- r baseline rows (`v25r_root_coarse_visible`) remain the opposite failure mode: high PLCR but almost unchanged silhouette, so they are metric-clean near-no-ops.

Conclusion:

- s is a useful diagnostic because it proves the operator can create visible displacement, but it fails the publication visual gate.
- The blocker has narrowed: a successful root-side operator must provide continuous branch support to the decoder, not just move a sparse branch mask farther away.
- Next loop is t: use a smaller moved branch handle plus an explicit sparse tube/support path between source and target anchors before decode.
