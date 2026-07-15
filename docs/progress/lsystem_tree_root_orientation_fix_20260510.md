# L-system tree-root orientation fix note（2026-05-10）

## Case

- Bad render inspected:
  `case_gallery_for_user_20260510_matched_selection/01_lsystem_tree_root/case_gallery_for_user_20260509__08_method_figures__visuals__public_guide_textured_glb_20260509d__renders__lsystem_spiky_iso.png`
- Source GLB:
  `visuals/public_guide_textured_glb_20260509d/lsystem_fork_spiky_steps8_tex2048_xformers/textured.glb`
- Source remote OBJ:
  `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/selected_meshes_extra_20260509/lsystem_fork_a0p5_pruned.obj`

## Diagnosis

The old case is not primarily a material problem.  Its snow-cedar-like colors are usable, but the growth semantics are wrong:

- the root/crown module was not normalized into a stable local frame;
- child modules were stamped with mismatched orientation;
- several complete crown chunks float or point sideways instead of attaching through the parent crown/trunk;
- therefore this render should be treated as a failure/diagnostic, not a selectable final case.

The user interpretation is correct: normalize or flip the original root so the crown points upward, then grow child modules from crown handles in different outward/upward directions.

## One-shell remote attempt

One SSH shell was opened to `a100-2`.

- GPUs 4/5/6/7 were all free: 0 MB used on each A100 80GB.
- Remote project storage was about 90G, within the relaxed 200GB limit.
- The old source OBJ and spiky guide existed on remote.
- The attempt failed before geometry generation because the script selected system `python3`, which had no `numpy`.

Rerun note: after sourcing `/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env`, select `$MESHVAE_ENV/bin/python` explicitly instead of resolving `PYBIN` before environment setup.

## Local reproducible fix preview

Script added:

- `assets/lsystem_tree_root_orientation_fix_20260510.py`

Outputs:

- v1: `results/lsystem_tree_root_orientation_fix_20260510_local/`
- v2 dense cedar preview: `results/lsystem_tree_root_orientation_fix_20260510_local_v2/`

Current v2 artifacts:

- OBJ: `results/lsystem_tree_root_orientation_fix_20260510_local_v2/mesh/lsystem_tree_root_upward_crown_handles_fix.obj`
- GLB: `results/lsystem_tree_root_orientation_fix_20260510_local_v2/glb/lsystem_tree_root_upward_crown_handles_fix.glb`
- ISO preview: `results/lsystem_tree_root_orientation_fix_20260510_local_v2/renders/lsystem_tree_root_upward_crown_handles_fix_iso.png`
- Front preview: `results/lsystem_tree_root_orientation_fix_20260510_local_v2/renders/lsystem_tree_root_upward_crown_handles_fix_front.png`

Current v2 stats:

- vertices: 62,790
- faces: 106,436
- bbox: 2.0299 x 1.7651 x 2.85
- surface split components: 3,842
- largest component area ratio: 0.0411

## Status

The corrected preview fixes the major semantic error: no upside-down or floating full-tree chunks; children attach from upper crown handles and grow outward/upward from an explicitly +Z crown frame.

It is not yet publication-ready:

- leaf/needle clusters are still many separate small surfaces, so connectivity metrics are not claim-safe;
- the silhouette reads more like a connected procedural cedar/pine preview than the old textured snow-cedar final;
- TRELLIS2/PBR texturing was not completed in the failed remote shell.

Recommended next step: rerun on `a100-2` with `$MESHVAE_ENV/bin/python`, then convert the quick fix to the established V6/V17 shared-anchor style so needles and crown masses are welded or bridged before TRELLIS2 texturing.
