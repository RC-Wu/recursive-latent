# Masked/Partial Trellis2 Repair Experiments

Date: 2026-05-07

## Question

The previous full flow-repair experiment showed that Trellis2 `shape_slat_flow_model_512` can naturalize recursively rewritten coordinates, but it also tends to turn the whole object into dense blob/sheet-like geometry. The masked repair question is:

> Can we preserve already-existing recursive structure while using Trellis2 flow only on newly grown latent coordinates?

This tests a more algorithmic use of Trellis2: the grammar owns topology and recursion; Trellis2 repairs only the new local feature field.

## Method

Pipeline:

```text
root mesh
  -> O-Voxel / Flexible Dual Grid
  -> shape_slat_encoder
  -> grammar proposes next sparse SLAT coordinate set
  -> shape_slat_flow_model_512 samples features at candidate coordinates
  -> old coordinates keep previous SLAT features
  -> new coordinates take flow-sampled features
  -> shape_slat_decoder
```

The implementation is:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/trellis2_recursive_masked_repair_workflow.py`
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/trellis2_recursive_masked_repair_workflow.py`

For the next ablation, new-coordinate features can be blended:

```text
new_feature = alpha * flow_feature + (1 - alpha) * copied_grammar_feature
```

`alpha=0` is pure recursive feature propagation. `alpha=1` is full masked repair on new coordinates.

## Completed Batch

Run roots:

- GPU0: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/trellis2_recursive_masked_repair/recursive_masked_repair_gpu0_20260507_1804`
- GPU1: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/trellis2_recursive_masked_repair/recursive_masked_repair_gpu1_20260507_1804`

Local contact sheets:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_recursive_masked_repair_20260507_1804/contact_sheets`

## Metrics

### DLA Procedural

Base: `985` tokens, `320,355` vertices.

| grammar | depth | steps | tokens | new tokens | vertices | faces |
|---|---:|---:|---:|---:|---:|---:|
| radial | 2 | 1 | 1898 | 360 | 341750 | 693224 |
| radial | 2 | 2 | 1898 | 360 | 349437 | 721162 |
| radial | 2 | 4 | 1898 | 360 | 371306 | 772976 |
| side | 2 | 1 | 1346 | 164 | 344391 | 704310 |
| side | 2 | 2 | 1346 | 164 | 356291 | 731290 |
| side | 2 | 4 | 1346 | 164 | 345823 | 713806 |
| echo | 2 | 1 | 1582 | 273 | 348284 | 706866 |
| echo | 2 | 2 | 1582 | 273 | 347708 | 720612 |
| echo | 2 | 4 | 1582 | 273 | 339999 | 710166 |

### IFS Procedural

Base: `571` tokens, `190,845` vertices.

| grammar | depth | steps | tokens | new tokens | vertices | faces |
|---|---:|---:|---:|---:|---:|---:|
| fork | 3 | 1 | 1856 | 465 | 612784 | 1535970 |
| fork | 3 | 2 | 1856 | 465 | 604667 | 1390106 |
| fork | 3 | 4 | 1856 | 465 | 716120 | 1757818 |
| fork_side | 3 | 1 | 2158 | 303 | 845337 | 2404690 |
| fork_side | 3 | 2 | 2158 | 303 | 857348 | 2284058 |
| fork_side | 3 | 4 | 2158 | 303 | 949030 | 2749438 |
| continue | 3 | 1 | 1292 | 259 | 351628 | 752132 |
| continue | 3 | 2 | 1292 | 259 | 330874 | 645794 |
| continue | 3 | 4 | 1292 | 259 | 376256 | 847492 |
| side | 3 | 1 | 1053 | 160 | 323263 | 736342 |
| side | 3 | 2 | 1053 | 160 | 302455 | 635830 |
| side | 3 | 4 | 1053 | 160 | 322440 | 676600 |
| echo | 3 | 1 | 1775 | 379 | 1002594 | 3395170 |
| echo | 3 | 2 | 1775 | 379 | 1010251 | 3005368 |
| echo | 3 | 4 | 1775 | 379 | 1024551 | 3523136 |

### L-System Procedural

Base: `684` tokens, `239,082` vertices.

| grammar | depth | steps | tokens | new tokens | vertices | faces |
|---|---:|---:|---:|---:|---:|---:|
| fork | 3 | 1 | 1700 | 346 | 712530 | 1840204 |
| fork | 3 | 2 | 1700 | 346 | 610398 | 1244802 |
| fork | 3 | 4 | 1700 | 346 | 530045 | 1037048 |
| fork_side | 3 | 1 | 2134 | 332 | 885167 | 2076166 |
| fork_side | 3 | 2 | 2134 | 332 | 885626 | 1697962 |
| fork_side | 3 | 4 | 2134 | 332 | 784342 | 1515052 |
| continue | 3 | 1 | 1112 | 136 | 351725 | 833036 |
| continue | 3 | 2 | 1112 | 136 | 346021 | 812608 |
| continue | 3 | 4 | 1112 | 136 | 343079 | 778866 |
| side | 3 | 1 | 996 | 94 | 333090 | 792498 |
| side | 3 | 2 | 996 | 94 | 325585 | 799706 |
| side | 3 | 4 | 996 | 94 | 336399 | 822020 |
| echo | 3 | 1 | 1280 | 168 | 356059 | 957356 |
| echo | 3 | 2 | 1280 | 168 | 337862 | 767804 |
| echo | 3 | 4 | 1280 | 168 | 350883 | 798270 |

### Image-Entry Roots

Image-entry IFS base: `462` tokens, `220,797` vertices.

| grammar | depth | steps | tokens | new tokens | vertices | faces |
|---|---:|---:|---:|---:|---:|---:|
| fork | 2 | 1 | 927 | 287 | 396319 | 921766 |
| fork | 2 | 2 | 927 | 287 | 398656 | 862208 |
| fork | 2 | 4 | 927 | 287 | 381203 | 774914 |
| side | 2 | 1 | 657 | 105 | 308596 | 723656 |
| side | 2 | 2 | 657 | 105 | 314204 | 738074 |
| side | 2 | 4 | 657 | 105 | 310622 | 644200 |
| continue | 2 | 1 | 753 | 145 | 279001 | 549696 |
| continue | 2 | 2 | 753 | 145 | 302032 | 622888 |
| continue | 2 | 4 | 753 | 145 | 294273 | 595250 |
| echo | 2 | 1 | 883 | 176 | 347942 | 743480 |
| echo | 2 | 2 | 883 | 176 | 342123 | 674358 |
| echo | 2 | 4 | 883 | 176 | 382093 | 761506 |

Image-entry L-system warm base: `880` tokens, `156,900` vertices.

| grammar | depth | steps | tokens | new tokens | vertices | faces |
|---|---:|---:|---:|---:|---:|---:|
| fork | 2 | 1 | 1798 | 464 | 320866 | 574272 |
| fork | 2 | 2 | 1798 | 464 | 325076 | 580552 |
| fork | 2 | 4 | 1798 | 464 | 336830 | 616212 |
| side | 2 | 1 | 1122 | 91 | 192166 | 345324 |
| side | 2 | 2 | 1122 | 91 | 189820 | 339380 |
| side | 2 | 4 | 1122 | 91 | 188639 | 335766 |
| continue | 2 | 1 | 1162 | 139 | 184248 | 318722 |
| continue | 2 | 2 | 1162 | 139 | 186613 | 324292 |
| continue | 2 | 4 | 1162 | 139 | 190608 | 332084 |
| echo | 2 | 1 | 1438 | 225 | 258682 | 488486 |
| echo | 2 | 2 | 1438 | 225 | 240842 | 386438 |
| echo | 2 | 4 | 1438 | 225 | 259096 | 456920 |

## Visual Conclusions

1. Procedural L-system masked repair is currently the strongest baseline. It becomes bush-like and remains structurally coherent, especially under `fork` and `fork_side`.
2. IFS masked repair preserves the original sweeping branch scaffold, but Trellis2 flow tends to turn copied branches into parallel struts and striping rather than natural solid surfaces.
3. DLA masked repair is stable and coherent for cluster growth, but it is a different morphology from recursive trees.
4. Image-entry IFS root is too blob-like; recursion works numerically but has weak semantic growth because the first mesh is weak.
5. Image-entry L-system warm root preserves the Trellis2 first-mesh grid/sheet artifact. This is important: masked repair is conservative and does not repair a bad inherited root.
6. Step count mainly affects surface density and fragmentation; grammar determines topology. This supports treating grammar as the structural model and Trellis2 as a local feature/surface model.

## Current Direction

The next active experiment is a blend-strength ablation over `alpha in {0, 0.25, 0.5, 0.75, 1}`. The goal is to find whether partial use of Trellis2 flow can reduce IFS striping and L-system over-densification while retaining some learned naturalization.

If the blend ablation shows that `alpha=0.25` or `0.5` is visually better than `alpha=1`, the recommended baseline should be:

```text
mesh root
  -> shape SLAT
  -> recursive grammar proposes coordinates
  -> copied feature propagation for structural continuity
  -> weak Trellis2 flow blend on new coordinates
  -> texture latent fill
```

## Blend Ablation Results

Output root:

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/trellis2_recursive_masked_blend`

Local contact sheets:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_recursive_masked_blend_20260507_1824/contact_sheets`

The result supports weak/mid flow blend. Full flow on new coordinates (`alpha=1`) usually increases density and face count without improving topology.

### Representative Metrics

| case | grammar | alpha | depth | tokens | vertices | faces |
|---|---|---:|---:|---:|---:|---:|
| L-system procedural | fork_side | 0.25 | 3 | 2134 | 465698 | 929254 |
| L-system procedural | fork_side | 0.5 | 3 | 2134 | 599122 | 1092676 |
| L-system procedural | fork_side | 1.0 | 3 | 2134 | 944006 | 2101684 |
| IFS procedural | fork_side | 0.25 | 3 | 2158 | 466199 | 873514 |
| IFS procedural | fork_side | 0.5 | 3 | 2158 | 496085 | 837474 |
| IFS procedural | fork_side | 1.0 | 3 | 2158 | 940305 | 3084752 |
| IFS procedural | fork | 0.5 | 3 | 1856 | 364959 | 632228 |
| IFS procedural | fork | 1.0 | 3 | 1856 | 632855 | 1277098 |

Visual interpretation:

1. L-system `fork_side alpha0.25` is the current strongest baseline. It is bush-like, compact, and less over-dense than alpha1.
2. IFS benefits numerically from weak/mid alpha, but the output still shows parallel struts, so the IFS root/grammar pair is less promising than L-system.
3. Image-entry roots do not improve qualitatively under alpha blend. Bad first meshes remain bad roots.

## Texture-Latent Follow-Up

Output root:

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/trellis2_recursive_blend_texture`

The selected recursive blend outputs were fed into:

```text
shape_slat_encoder -> tex_slat_flow_model_512 -> tex_slat_decoder
```

Results:

| case | mesh vertices/faces | shape/tex tokens | PBR voxels | PBR mean |
|---|---:|---:|---:|---:|
| L-system fork_side alpha0.25 d3 | 455510 / 929254 | 2922 | 675941 | 0.3898 |
| L-system fork alpha0.5 d3 | 410766 / 823250 | 2538 | 628403 | 0.4089 |
| IFS fork alpha0.5 d3 | 339681 / 632228 | 1627 | 319628 | 0.4506 |
| IFS fork_side alpha0.25 d3 | 455889 / 873514 | 2454 | 548696 | 0.4662 |

This closes the current complete executable baseline:

```text
mesh root
  -> O-Voxel / FDG
  -> shape SLAT
  -> recursive grammar
  -> weak/mid masked flow blend on new coordinates
  -> decoded recursive mesh
  -> texture latent / PBR voxel
```

Full textured GLB export remains blocked by missing `nvdiffrast`, but the texture latent path itself is confirmed on the final recursive candidates.

## Mesh Quality Metrics

Metrics script:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/mesh_quality_metrics.py`

Outputs:

- A100: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/mesh_quality_metrics/quality_metrics_20260507_1920`
- Local: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/mesh_quality_metrics/quality_metrics_20260507_1920`

Metrics include:

- connected component count;
- largest component vertex ratio;
- fragmentation score `1 - largest_component_vertex_ratio`;
- bbox extent/volume;
- PCA linearity and planarity;
- sampled face-area statistics.

Representative results:

| case | vertices | components | largest ratio | fragmentation | PCA linearity | PCA planarity |
|---|---:|---:|---:|---:|---:|---:|
| masked L-system fork_side steps2 d3 | 885626 | 71223 | 0.8098 | 0.1902 | 0.743 | 0.202 |
| blend L-system fork_side alpha0.25 d3 | 465698 | 13549 | 0.6165 | 0.3835 | 0.809 | 0.133 |
| blend L-system fork_side alpha0.5 d3 | 599122 | 30822 | 0.5268 | 0.4732 | 0.797 | 0.150 |
| blend L-system fork alpha0.5 d3 | 428764 | 22099 | 0.6263 | 0.3737 | 0.827 | 0.117 |
| direct L-system fork d3 | 503162 | 4113 | 0.3843 | 0.6157 | 0.777 | 0.174 |
| direct IFS fork_side d3 | 482285 | 5625 | 0.3871 | 0.6129 | 0.753 | 0.185 |
| blend IFS fork alpha0.5 d3 | 364959 | 30985 | 0.5509 | 0.4491 | 0.566 | 0.348 |
| image-entry L-system warm fork alpha0.25 d2 | 310774 | 2920 | 0.2337 | 0.7663 | 0.400 | 0.549 |
| DLA masked radial steps2 d2 | 349437 | 5328 | 0.9127 | 0.0873 | 0.382 | 0.289 |

Interpretation:

1. Full masked L-system is the most connected among tree-like candidates, but visual inspection showed it is too dense.
2. L-system weak blend (`alpha=0.25`) is visually cleaner but more fragmented, so the next useful algorithmic step is pruning or merging small floating components after weak blend.
3. Image-entry L-system warm is quantitatively sheet-like: high planarity and high fragmentation.
4. DLA is highly connected but belongs to cluster/coral morphology, not tree morphology.
5. Direct coordinate-copy decode has fewer components than weak blend but lower largest-component ratio, which suggests the components are more evenly fragmented.

Next recommended engineering target:

```text
weak blend candidate
  -> connected-component pruning / floating-island removal
  -> optional branch-local smoothing or remeshing
  -> texture latent fill
```

## Component Pruning Post-Process

A simple connected-component pruning pass was tested on the weak-blend candidates:

- script: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/prune_mesh_components.py`
- output: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/component_pruning/prune_20260507_1953`
- rule: keep the largest component and every component with at least `1000` vertices.

Results:

| case | input vertices | input components | output vertices | kept components | largest ratio after pruning | fragmentation after pruning |
|---|---:|---:|---:|---:|---:|---:|
| L-system fork_side alpha0.25 | 465698 | 13549 | 373843 | 14 | 0.7680 | 0.2320 |
| L-system fork alpha0.5 | 428764 | 22099 | 324187 | 11 | 0.8284 | 0.1716 |
| IFS fork alpha0.5 | 364959 | 30985 | 249192 | 16 | 0.8068 | 0.1932 |

This is a strong positive post-process result. It reduces tens of thousands of floating components to about 10-16 retained components and raises largest-component ratio to roughly `0.77-0.83`.

Updated recommendation:

1. For visual branch richness, keep `L-system fork_side alpha0.25`.
2. For quantitative connectedness, prefer `L-system fork alpha0.5` after pruning.
3. Run texture latent on the pruned L-system candidates next, because pruning changes geometry but should remain compatible with `shape_slat_encoder -> tex_slat_flow -> tex_slat_decoder`.

## Pruned Visual Inspection

Local visual folder:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/component_pruning_20260507_1953`

Contact sheet:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/component_pruning_20260507_1953/component_pruning_pruned_contact_sheet_20260507_1953.png`

Visual interpretation:

1. `L-system fork_side alpha0.25` remains the best visual candidate. It preserves the richest bush/tree-like growth and pruning removes most tiny debris, although some trailing branch-like satellite pieces remain.
2. `L-system fork alpha0.5` is the best quantitative connectedness candidate. It has the highest post-pruning largest-component ratio, but the preview still shows several separated upper/right chunks and is less organic than `fork_side`.
3. `IFS fork alpha0.5` still shows long parallel struts, so pruning is not enough to make IFS the main tree/root baseline.

Pruned texture follow-up was prepared but not launched because GPUs `0/1` on `a100-2` were occupied by other training processes. Prepared script:

- local: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/run_pruned_texture_gpu01_20260507_2318.sh`
- A100: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/run_pruned_texture_gpu01_20260507_2318.sh`

Planned cases:

| case | mesh | planned output |
|---|---|---|
| L-system fork_side alpha0.25 pruned | `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/component_pruning/prune_20260507_1953/lsystem_fork_side_a0p25/mesh_pruned.obj` | `trellis2_pruned_texture/pruned_texture_gpu01_20260507_2318/lsystem_fork_side_a0p25_pruned_texture` |
| L-system fork alpha0.5 pruned | `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/component_pruning/prune_20260507_1953/lsystem_fork_a0p5/mesh_pruned.obj` | `trellis2_pruned_texture/pruned_texture_gpu01_20260507_2318/lsystem_fork_a0p5_pruned_texture` |
