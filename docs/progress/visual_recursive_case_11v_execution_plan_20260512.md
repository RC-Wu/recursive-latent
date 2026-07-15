# Visual Recursive Case 11v Execution Plan 20260512

Status: planned pivot after 11r/11t/11u diagnostics  
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU policy: use only GPUs `4,5,6,7`; prefer at most two concurrent lanes until first QA.  
Storage policy: keep remote project under the user-relaxed `200GB` cap.  
Goal: produce at least one publication-grade hard-surface recursive visual case, preferably city/castle/mechanical, by changing root/source and anchor construction rather than continuing to tune the failed 11r/11t/11u roots.

## Recovery Contract

After heartbeat/context compaction, read:

1. `docs/progress/visual_recursive_case_ralph_plan_20260511.md`
2. `docs/progress/visual_recursive_case_11u_execution_plan_20260511.md`
3. this file
4. newest `docs/progress/*20260512*.md`, if any

Do not promote any 11v result without:

- remote SLat/grammar OBJ or GLB output from our own workflow;
- metrics CSV/JSON with occupancy and component diagnostics;
- presentation-transform manifest;
- controlled Blender render QA in iso/front/side;
- root/source, semantic anchor, growth frame, render frame, grammar, seed, and depth documented;
- visual pass: clear recursion, no major top-cap holes, no thin/floating shell fragments, no side/front graft reading.

## Why 11v Is Needed

11r/11t/11u established the failure mode:

- presentation-frame rotation can make a result look more upright, but it cannot fix a semantic anchor that decoded as a side/front graft;
- low-frequency solid roots improve global body quality and occupancy metrics, but top child surfaces still show holes, shell breaks, and small floating fragments;
- repeatedly scaling/offsetting the same cap/body token source is now a low-yield path.

11v should therefore change the input construction:

- use roots with explicit, visually clean top anchors before SLat encoding;
- make the support/plinth bridge a real, broad, simple geometric part of the authored input or operator, not a fragile high-frequency cap copy;
- prefer simpler topologically solid source roots over visually busy roots with thin battlements, hollow shells, or decoder-sensitive surface detail;
- keep semantic growth frame and render frame separate in manifests.

## Candidate Lanes

### Lane A: Mechanical Socket Promotion

Starting point:

- `mech_frame_11s_socket_pods_s` remains the nearest hard-surface candidate.
- Existing QA pack:
  - `results/publication_repair_20260511s_mech_frame_socket_pods_s_qa_pack/`
  - `visuals/publication_repair_20260511s_mech_frame_socket_pods_qa/blender_qa_metal_white_contact_sheet_whitecomposite.png`

11v action:

- run only if a richer socket/mechanical source root or cleaner support operator is available;
- otherwise treat 11s mech-frame as near-main backup and spend GPU time on city/castle root acquisition.

### Lane B: City Top-Anchor Pivot

Root/source requirement:

- compact city block, tower, arcology, or courtyard with one broad, flat, explicitly marked top pad;
- no thin railings, narrow battlements, or hollow shell top;
- top pad should be recognizable in both semantic growth frame and final presentation frame.

Operator requirement:

- one child or two mirrored child masses at most;
- broad plinth/support bridge below child;
- child scale chosen so it stands clearly above the roof in `rot_x_neg90_then_center_floor` and in at least one identity/frame diagnostic;
- reject rows where bbox growth is mostly side/front or where controlled front/side reads as a facade attachment.

### Lane C: Castle Keep/Gate Pivot

Root/source requirement:

- solid keep or gate body with a simple roof/cap pad and no thin battlement strips;
- if turrets are used, they should be coarse cylinders/boxes with fused supports, not copied noisy cap fragments.

Operator requirement:

- prefer single central turret/keep child or four clean corner turrets, not both in the first pass;
- include a low-frequency support mask/plinth;
- require top child visibility in front and side controlled renders.

## First Remote Sweep Proposal

Use one small batch, not a broad sweep:

- GPU 4: city top-anchor root, depth 1 and 2, clean single-child grammar.
- GPU 5: castle top-anchor root, depth 1 and 2, clean turret/plinth grammar.
- GPU 6: optional mechanical socket cleanup only if a better root/operator is ready.
- GPU 7: reserved for metrics/QA or idle.

Stop after the first complete controlled QA if all city/castle rows repeat 11u top-cap holes; switch root/source before further grammar tuning.

## Acceptance / Rejection Rules

Promote to near-main only if all are true:

- token/bbox growth is nontrivial and in the intended semantic growth frame;
- occupancy LCR is at least `0.995` for city/castle and fragmentation below `0.01`;
- raw/face components are reported and not hidden behind occupancy-only success;
- controlled Blender white/studio render shows clear top-attached recursion in iso/front/side;
- no large black holes, torn cap surfaces, or floating shell strips on the recursive child;
- the visual still reads as city/castle/mechanical rather than an abstract block test.

Diagnostic only if:

- metrics are good but visual QA shows top holes or side grafting;
- the recursion is visible only in quick mesh/point preview;
- presentation frame fixes the look but semantic growth frame remains ambiguous;
- root/source provenance is not documented.

## Paper-Safe Claim Boundary

If 11v succeeds, claim only:

- an authored visual showcase demonstrating that explicit top anchors and support plinths can produce a cleaner hard-surface recursive case under PS-RSLG.

Do not claim:

- automatic root/anchor discovery;
- general city/castle solution;
- full resolution/effective-detail proof;
- that occupancy LCR alone proves visual or topological success.

## Live Log

- 2026-05-12: Created this 11v plan after the heartbeat confirmed 11r/11t/11u city/castle are diagnostic only. No remote job launched in this heartbeat; next action is source/root selection plus a narrow launcher once a cleaner top-anchor root is chosen.
