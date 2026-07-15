# Visual Recursive Case 11u Execution Plan 20260511

Status: active follow-up after 11t  
Local root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
Remote root: `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU policy: use only GPUs `4,5,6,7`  
Goal: test whether low-frequency, solid authored roots plus a single-child grammar can avoid 11t black holes and shredded top modules.

## Reason For 11u

11t proved that applying `--preencode-transform rot_x_neg90` before the fixed mesh-to-SLat conversion is useful: original z-up roots effectively stay z-up in SLat, so `growth_axis=z`, `growth_sign=1` makes top recursion more legible than 11r/11s. However, controlled Blender QA still exposed black holes, shell gaps, and shredded cap/body copies. That means root-frame alignment is necessary but not sufficient.

11u changes the root and grammar, not merely camera:

- roots are low-frequency fused solids with broad platforms and no thin battlement strips;
- grammar copies one central solid child body, not cap/corner detail tokens;
- support is broad and compact, with fewer bridge/support tokens than the earlier shell-copy operators.

## Cases

- `city_solid_podium_11u`: root `city_solid_podium_v1.obj`, grammars `v25u_solid_rooftop_child_clean` and `v25u_solid_rooftop_child_large`, depth 2.
- `city_solid_keep_11u`: root `city_solid_keep_v1.obj`, same grammars, depth 2.
- `castle_solid_keep_11u`: root `castle_solid_keep_v1.obj`, same grammars, depth 2.
- `castle_solid_gate_11u`: root `castle_solid_gate_v1.obj`, same grammars, depth 2.

All cases use:

- `preencode_root_transform=rot_x_neg90`;
- `semantic_growth_frame=original z+ becomes SLat z+`;
- `growth_axis=z`, `growth_sign=1`;
- final paper QA should prefer `rot_x_neg90_then_center_floor` only if it visually aligns the case; otherwise identity presentation should remain explicit.

## Claim Gate

Promote nothing unless:

- token/bbox growth is nontrivial;
- occupancy LCR is at least `0.995`;
- fragmentation is below `0.01` for city and below `0.02` for castle;
- controlled Blender QA shows a child above the roof/cap in iso, front, and side;
- no large black holes, torn shell edges, or side-graft reading.

## Live Log

- 2026-05-11: Created low-frequency roots with `assets/create_visual_recursive_solid_roots_20260511u.py`; preview sheet is `results/visual_recursive_solid_roots_20260511u/root_contact_sheet.png`.
- 2026-05-11 late: Remote 11u completed successfully on `a100-2` using GPUs `4,5,6,7`; outputs were pulled locally under `results/visual_recursive_cases_remote_20260511u_preview_pull/` and `results/visual_recursive_cases_remote_20260511u_selected_meshes/`.
- Metric gate results for the best clean rows:
  - `city_solid_keep_11u/v25u_solid_rooftop_child_clean/depth_02`: faces `762370`, occupancy LCR `0.9951219512`, occupancy components `2`, fragmentation `0.003417`, raw face components `194`.
  - `castle_solid_keep_11u/v25u_solid_rooftop_child_clean/depth_02`: faces `753108`, occupancy LCR `1.0`, occupancy components `1`, fragmentation `0.001134`, raw face components `121`.
  - `city_solid_podium_11u/v25u_solid_rooftop_child_clean/depth_01`: faces `530744`, occupancy LCR `0.9997499687`, occupancy components `3`, fragmentation `0.002905`, raw face components `291`.
  - `castle_solid_gate_11u/v25u_solid_rooftop_child_clean/depth_01`: faces `412506`, occupancy LCR `0.9980303030`, occupancy components `3`, fragmentation `0.020941`, raw face components `183`.
- Controlled Blender QA was generated locally with Blender 5.1.1 after presentation-frame transforms:
  - identity OBJ/manifest/cases: `results/visual_recursive_cases_remote_20260511u_selected_meshes/identity_center_floor/`;
  - identity stone-white contact sheet: `results/visual_recursive_cases_remote_20260511u_selected_meshes/identity_center_floor/blender_qa_stone_white_contact_sheet.png`;
  - `rot_x_neg90_then_center_floor` OBJ/manifest/cases: `results/visual_recursive_cases_remote_20260511u_selected_meshes/rot_x_neg90_then_center_floor/`;
  - `rot_x_neg90_then_center_floor` stone-white contact sheet: `results/visual_recursive_cases_remote_20260511u_selected_meshes/rot_x_neg90_then_center_floor/blender_qa_stone_white_contact_sheet.png`.
- 11u verdict:
  - Low-frequency solid roots and the 11u clean single-child operator are a real improvement over 11t/11r: the primary city/castle bodies are less shredded and the presentation-frame top hierarchy is clearer in `rot_x_neg90_then_center_floor`.
  - The results still fail the publication visual gate. `identity_center_floor` reveals front/side grafting rather than true rooftop growth; `rot_x_neg90_then_center_floor` makes the child read as top-attached, but the recursive cap/top surfaces contain visible black holes, thin shell breaks, and small floating fragments. `castle_solid_gate_clean_d1` is especially rough.
  - Do not promote 11u city/castle rows to main figures or call city/castle solved. Keep `city_solid_keep_clean_d1/d2` and `castle_solid_keep_clean_d1/d2` only as diagnostic/near-miss evidence that root-frame alignment plus low-frequency roots help but do not yet give a paper-safe city/castle recursive showcase.
- Next pivot:
  - stop trying to recover city/castle by merely rotating the presentation frame or scaling the same cap child;
  - use a new 11v-style route with explicitly authored top semantic anchors in the root mesh, a solid child generated/encoded as its own root token, and a support/plinth bridge that is visually clean before SLat encoding;
  - prefer a visually richer but topologically simpler city/castle source root over further tuning `city_solid_keep_v1` and `castle_solid_keep_v1`.
