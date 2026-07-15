# Visual Recursive Case 11t Execution Plan 20260511

Status: active continuation from 11s  
Created: 2026-05-11 CST  
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU policy: use only GPUs `4,5,6,7`  
SSH policy: at most two SSH shells; use one persistent shell by default  
Current machine / target machine: `mac_local_only` orchestration, `development_machine_only` remote generation

## Recovery Contract

After context compaction, read in order:

1. `docs/progress/visual_recursive_case_ralph_plan_20260511.md`
2. this file
3. newest `docs/progress/*20260511*.md`
4. `results/visual_recursive_cases_remote_20260511s_selected_meshes/presentation_rot_x_neg90/compact_metrics_20260511s.csv`

Do not promote a case to publication-grade unless it has:

- remote SLat/grammar OBJ or GLB output;
- metrics with occupancy/component sanity checks;
- presentation-transform manifest;
- controlled Blender render QA under paper-safe material and lighting;
- root/source, anchor, semantic growth frame, render frame, grammar, seed, and depth documented;
- visual pass: obvious recursion, no major holes, sheet fragments, side-graft reading, or distracting islands.

## Current 11s Facts

11s completed on `a100-2` with GPUs `4,5,6` and left GPU `7` open. Storage after pull/QA was about `145G`, below the user-relaxed `200GB` cap.

Best candidate:

- `mech_frame_11s_socket_pods_l/s`
- token delta: `448 -> 504`
- occupancy LCR: `1.0`
- fragmentation: about `0.005`
- visual verdict: readable symmetric hard-surface socket/pod recursion under controlled metal render; near-main mechanical candidate after one cleanup/material/zoom pass.

Do not promote from 11s:

- `city_arcology_11s_topbody_protrude`: good metrics, but controlled render still reads like front/side attachment rather than clean rooftop recursion.
- `city_courtyard_11s_topbody_protrude`: weaker metric gate and side/front read.
- `castle_gate_11s_cap_pair_protrude` and `castle_keep_11s_cap_pair_protrude`: cap/turret growth visible in quick view, but controlled renders show horizontal/sideward growth and shredded cap ends.
- `mecha_cruciform_11s_socket_pods_*`: occupancy connected, but face LCR about `0.545-0.556`, so not paper-safe.

## 11t Objectives

### Track A: Mechanical Promotion

Promote only the `mech_frame` branch to a presentation package:

- choose `mech_frame_11s_socket_pods_s` unless render comparison shows `l` is visibly better;
- generate controlled bright metal renders, white and light blue-gray studio variants;
- generate two-level zooms around socket/pod recursion;
- export or package OBJ/GLB plus metrics/manifest;
- update the main visual plan with a conservative label: mechanical/hard-surface recursive socket case, not tank/mecha proof unless the render clearly supports that label.

### Track B: City/Castle Pivot

Do not keep tuning `city_cluster_11r_protruding_stack`.

For city/castle, the current failure is not only grammar strength. It is a frame/root problem: a z-up authored root is encoded through `(x, y, z) -> (x, -z, y)`, while the paper presentation uses `rot_x_neg90_then_center_floor`. Post-hoc presentation fixes can make the object look upright, but the decoded child can still read as a side/front graft in the final camera. The next pass must use either:

- render-frame-aware authored roots before SLat encoding, where the intended visible top plane already aligns with the decoder/presentation frame; or
- a new workflow mode that applies the presentation/root-frame transform before encoding and records the semantic growth frame separately.

11t minimum cases:

- one clean city root with a very simple top platform and single child tower;
- one clean castle keep/gate root with a simple top cap and single child turret;
- optional mechanical rerun only if the local 11s package exposes a serious visual flaw.

Claim gate:

- reject unchanged token/bbox rows before rendering;
- require controlled Blender front/side/iso plus at least one camera where top hierarchy is unambiguous;
- require no visible side-graft reading in the controlled sheet.

## Live Log

- 2026-05-11: Created this 11t execution plan after reading AgentDoc, the 11s handoff, and current project progress docs. Main thread will run the remote shell; subagents are read-only and scoped to mechanical packaging and city/castle diagnosis.
- 2026-05-11: City/castle read-only audit confirmed the next highest-value move is `root transform before encoding`, not more 11s operator tuning. The z-up to SLat frame (`growth_axis=y`, `growth_sign=-1`) remains correct, but post-decode presentation transforms cannot fix encoder/decoder-facing top-plane ambiguity. 11t should minimally test `city_arcology`, `city_cluster`, and `castle_keep` with manifest-recorded `preencode_root_transform` plus the existing presentation transform.
- 2026-05-11 22:08 CST: Synced the workflow patch and `assets/run_visual_recursive_cases_remote_20260511t.sh` to `a100-2`; launched 11t on GPUs 4/5/6, leaving GPU 7 free.
- 2026-05-11 22:13 CST: 11t completed, metrics computed, and remote shell closed after confirming GPUs 0-7 idle and remote project size about `145G`.
  - remote output: `results/visual_recursive_cases_remote_20260511t`;
  - local preview/metrics/log pull: `results/visual_recursive_cases_remote_20260511t_preview_pull/`;
  - selected OBJ pull: `results/visual_recursive_cases_remote_20260511t_selected_meshes/raw_selected/`;
  - identity presentation QA: `results/visual_recursive_cases_remote_20260511t_selected_meshes/identity_center_floor/blender_qa_stone_white_contact_sheet.png`;
  - old-style `rot_x_neg90` presentation QA: `results/visual_recursive_cases_remote_20260511t_selected_meshes/rot_x_neg90/blender_qa_stone_white_contact_sheet.png`.
- 11t metric verdict:
  - `city_arcology_11t_v25s_d2`: occ LCR about `0.9996`, fragmentation about `0.0032`; z/top extent grows in the intended frame. Best city metric row.
  - `castle_keep_11t_v25s_d1`: occ LCR about `0.997-0.998`, fragmentation about `0.0055`; best castle metric row.
  - `castle_gate_11t_v25s_d1`: occ LCR about `0.999`, fragmentation about `0.0159`; near threshold but cap ends are visually rough.
  - `city_cluster_11t_v25s_d1`: metric-clean but almost no visible new hierarchy; treat as near-noop.
  - `city_cluster_11t_v25p_d1`: more visible top child but fragmentation about `0.030`; reject for main evidence.
- 11t visual verdict:
  - preencode top-frame helped: point previews and `rot_x_neg90` presentation make city/castle top hierarchies more legible than 11r/11s.
  - controlled Blender QA still exposes black holes, shell gaps, and shredded cap/top modules, so 11t is not publication-grade.
  - Do not promote 11t city/castle to main figures. Use it as diagnostic evidence that root-frame alignment is necessary but not sufficient.
  - Next loop should stop using the current cap/body token source masks for city/castle and instead use lower-frequency, more solid authored roots plus a single-child grammar with stronger support and fewer copied top details.
- Mechanical side package completed locally for 11s `mech_frame_11s_socket_pods_s`:
  - selected OBJ: `results/visual_recursive_cases_remote_20260511s_selected_meshes/presentation_rot_x_neg90/mech_frame_11s_socket_pods_s.obj`;
  - metrics/manifest: `results/publication_repair_20260511s_mech_frame_socket_pods_s_qa_pack/`;
  - white-composited metal QA: `visuals/publication_repair_20260511s_mech_frame_socket_pods_qa/blender_qa_metal_white_contact_sheet_whitecomposite.png`;
  - raw zoom renders: `visuals/publication_repair_20260511s_mech_frame_socket_pods_controlled_zoom_1200/mech_frame_zoom_raw_contact_sheet.png`;
  - verdict: near-main mechanical candidate, but not final hero-grade because the end sockets still show small debris and the object reads as a compact mechanical module rather than a rich mecha/weapon/city showcase.
