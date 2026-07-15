---
id: NOTE-COMPLETE-RECURSIVE-TRELLIS2-WORKFLOW-20260507
title: Complete Recursive Trellis2 Workflow Experiments
tags: [experiment, trellis2, recursive_workflow, mesh_first, slat, texture, flow_repair]
created_at: "2026-05-07T19:20:00+08:00"
---

# Summary

This batch moves the project from isolated Trellis2 probes to full recursive workflows.

We now have three complete frozen-Trellis2 routes:

1. **Mesh-first recursive grammar**
   ```text
   procedural mesh -> O-Voxel/FDG -> shape SLAT -> recursive grammar -> decode each depth
   ```
2. **Image-entry closed loop**
   ```text
   object-like render -> DINOv3-conditioned Trellis2 mesh -> O-Voxel/shape SLAT -> recursive grammar -> decode
   ```
3. **Recursive output repair/texturing**
   ```text
   recursive mesh -> shape_slat_encoder -> texture flow/decoder
   recursive coords -> shape_slat_flow_model_512 repair -> decode
   ```

The strongest empirical result is that recursive operators are much more stable in mesh/O-Voxel/SLAT space than in unusual 2D scaffold image conditions.

# Scripts

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/trellis2_recursive_slat_grammar_workflow.py`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/render_mesh_object_like_conditions.py`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/trellis2_recursive_slat_flow_repair.py`

# Runs

## Recursive Shape-SLAT Grammar

Run:

```text
/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/trellis2_recursive_slat_grammar/recursive_slat_grammar_gpu0_20260507_1842
```

Local visuals:

```text
/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_recursive_slat_grammar_20260507_1842
```

Compact result:

| Root | Grammar | Tokens | Vertices | Interpretation |
|---|---|---:|---:|---|
| IFS | continue | 571 -> 1292 | 190,845 -> 348,090 | stable extension |
| IFS | fork | 571 -> 1856 | 190,845 -> 445,182 | strong branch duplication |
| IFS | fork_side | 571 -> 2158 | 190,845 -> 482,285 | strongest growth primitive |
| IFS | echo | 571 -> 1775 | 190,845 -> 292,056 | bounded, more thickening than branching |
| IFS | mirror_fork | 571 -> 2178 | 190,845 -> 466,802 | coherent global transform + branching |
| L-system | fork | 684 -> 1700 | 239,082 -> 503,162 | clean structural growth |
| L-system | mirror_fork | 684 -> 1858 | 239,082 -> 453,002 | stable but more compact |
| DLA voxel | radial | 985 -> 1898 | 320,355 -> 444,971 | suitable for crystal/coral growth |
| DLA voxel | side | 985 -> 1346 | 320,355 -> 430,941 | coherent cluster expansion |

Conclusion:

- This satisfies the requirement of integrating Trellis2 into a complete recursive grammar flow.
- The workflow is fully training-free.
- The recursive operator is defined in native sparse 3D latent coordinates, not 2D image space.

## Object-Like Image Entry

Run:

```text
/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/trellis2_object_like_image_entry/recursive_image_entry_gpu1_retryshim_20260507_1845
```

Local visuals:

```text
/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_object_like_image_entry_20260507_1845
```

Results:

| Condition | Vertices | Faces | Shape tokens | Visual note |
|---|---:|---:|---:|---|
| IFS solid-depth front | 184,524 | 319,200 | 316 | coarse mass, fragmented tail |
| IFS warm silhouette | 197,314 | 518,476 | 316 | split sheet/blobs |
| L-system solid-depth front | 70,964 | 210,366 | 389 | sparse vertical point/sheet structure |
| L-system warm silhouette | 451,647 | 837,584 | 2,447 | large grid/sheet component |

Conclusion:

- Object-like render adapter is useful as an entry route, but output quality is inconsistent.
- Once any mesh exists, the mesh-first route should take over.

## Image-Entry To Recursive Grammar

Run:

```text
/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/trellis2_recursive_slat_from_image_entry/recursive_slat_from_image_entry_gpu0_20260507_1900
```

This tests the full chain:

```text
object-like image -> Trellis2 mesh -> shape SLAT -> recursive grammar -> decoded depths
```

Results:

| Root | Grammar | Tokens | Vertices |
|---|---|---:|---:|
| image IFS solid | continue | 462 -> 753 | 220,797 -> 275,305 |
| image IFS solid | fork | 462 -> 927 | 220,797 -> 315,720 |
| image IFS solid | side | 462 -> 657 | 220,797 -> 288,473 |
| image IFS solid | echo | 462 -> 883 | 220,797 -> 427,099 |
| image L-system warm | continue | 940 -> 1240 | 167,390 -> 218,553 |
| image L-system warm | fork | 940 -> 1944 | 167,390 -> 361,346 |
| image L-system warm | side | 940 -> 1239 | 167,390 -> 222,938 |
| image L-system warm | echo | 940 -> 1534 | 167,390 -> 200,963 |

Conclusion:

- The image-entry closed loop works.
- Its bottleneck is quality of the first image-generated mesh, not the recursive SLAT machinery.

## Recursive Texture Latent Path

Run:

```text
/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/trellis2_recursive_texture_latent/recursive_texture_latent_gpu1_20260507_1900
```

Results:

| Mesh | Shape/Tex tokens | PBR voxels | PBR mean |
|---|---:|---:|---:|
| IFS fork_side depth3 | 2,552 | 579,665 | 0.4215 |
| L-system fork depth3 | 2,424 | 761,508 | 0.4485 |
| Image-entry L-system warm | 2,445 | 446,782 | 0.4340 |

Conclusion:

- Texture latent path can consume recursive outputs.
- Full GLB/PBR export remains blocked by missing `nvdiffrast`, but latent texture generation works.

## Shape Flow Repair

Run:

```text
/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/trellis2_recursive_flow_repair/recursive_flow_repair_gpu01_20260507_1912
```

Method:

```text
mesh root -> shape SLAT coords -> recursive coord rewrite
  -> shape_slat_flow_model_512 resamples features under DINOv3 condition
  -> shape_slat_decoder
```

Results:

| Case | Depth | Tokens | Vertices | Faces |
|---|---:|---:|---:|---:|
| IFS mesh fork repair | 0 | 571 | 468,275 | 1,545,944 |
| IFS mesh fork repair | 1 | 926 | 458,467 | 1,537,886 |
| IFS mesh fork repair | 2 | 1,391 | 663,243 | 2,160,934 |
| Image L-system warm fork repair | 0 | 940 | 193,453 | 270,126 |
| Image L-system warm fork repair | 1 | 1,475 | 275,171 | 382,634 |
| Image L-system warm fork repair | 2 | 1,944 | 409,927 | 663,042 |

Conclusion:

- Flow repair is the first actual generative naturalization module after recursive coordinate rewrite.
- It makes denser, more continuous geometry than direct coordinate-copy decoding.
- It can also drift toward blobs/sheets, so the next version should preserve old features and resample only new regions.

# Overall Interpretation

Current best algorithmic baseline:

```text
root coarse element
  -> mesh/O-Voxel
  -> shape SLAT
  -> recursive grammar operator on sparse coords
  -> masked flow repair for new/edited coords
  -> texture flow for final shape
  -> decode/export
```

The most promising next method is not a better 2D prompt/render. It is a masked 3D latent rewrite system:

- preserve old coordinates/features;
- add new recursive coordinates;
- flow-sample only new features under image/text/style condition;
- texture only after geometry stabilizes.

