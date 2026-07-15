---
title: Trellis2 Latent Coordinate Transform Probe
date: 2026-05-07
tags: [trellis2, sparse_latent, coordinate_transform, recursive_generation, diagnostics]
---

# Trellis2 Latent Coordinate Transform Probe

This note records the first non-weight-dependent probe of Trellis2 structured latent geometry operations. It uses the handcrafted conditioning proxy only to obtain an initial `shape_slat` and `tex_slat`; the experiment itself edits sparse latent coordinates and decodes without resampling.

## Setup

- Host: `a100-2`
- GPU: `CUDA_VISIBLE_DEVICES=4`
- Input scaffold: IFS branch-tree render
- Conditioning source: handcrafted proxy, scale `1.0`
- Seed: `300`
- Steps: `2`
- Cache policy: project-directory caches only, with `triton_beegfs_cache_patch.py`

Output folder:

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/trellis2_latent_transform_probe/latent_transform_ifs_handcrafted_scale1_gpu4_projectcache_20260507_1524_seed300`

Local visuals:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_latent_transform_ifs_20260507_1524_seed300/latent_transform_contact_sheet.png`

## Operators Tested

Identity:

\[
T_{\text{id}}(C,F)=(C,F)
\]

Mirror across occupied x-range:

\[
T_{\text{mirror-x}}(b,x,y,z,F)=(b,x_{\min}+x_{\max}-x,y,z,F)
\]

Copy and shift upper-z subset:

\[
T_{\text{copy}}(S)=\operatorname{merge}(S,(C_\Omega+\Delta,F_\Omega)),
\quad \Omega=\{i:z_i\geq \operatorname{median}(z)\}
\]

Duplicate-coordinate collisions are averaged in feature space.

## Results

| Transform | Shape tokens | Vertices | Faces | Components | Largest component ratio | Visual reading |
|---|---:|---:|---:|---:|---:|---|
| identity | 87 | 28851 | 71726 | 34 | 0.3924 | same block/plate proxy artifact as base IFS |
| mirror_x | 87 | 28708 | 72654 | 34 | 0.4316 | stable mirror-like rearrangement; no collapse |
| copy_shift_upper_z | 122 | 42219 | 105576 | 47 | 0.4562 | adds shifted fragments with moderate growth; no whole-cube explosion |

Timing:

- model load: `54.64s`
- initial sample and decode: `15.73s`
- identity decode: `2.90s`
- mirror decode: `2.24s`
- copy-shift decode: `60.20s`

## Interpretation

This is the first positive technical signal for the recursive-growth idea.

The base geometry is still a poor handcrafted-proxy artifact, so the visual quality is not useful. However, the decoder tolerates sparse-coordinate edits:

- `mirror_x` preserves token count and mesh scale almost exactly;
- `copy_shift_upper_z` increases token count by `40.2%` and face count by `47.2%`, but stays bounded in the normalized coordinate range;
- component count grows from `34` to `47`, which is worse but not catastrophic;
- the copied region appears as extra shifted fragments rather than random noise.

This suggests that a latent-coordinate recursive operator is more promising than handcrafted image features while official DINOv3 weights are unavailable.

## Next Probe

The next experiment should separate shape and texture:

1. Decode transformed `shape_slat` with original or omitted texture guidance if Trellis2 permits it.
2. Try smaller copy subsets and shifts.
3. Run the same transform on a better official DINOv3-conditioned latent once the user provides weights.
4. Add a boundedness score:

\[
B = \frac{\operatorname{extent}(T(S))}{\operatorname{extent}(S)}
\]

and a fragmentation score:

\[
F_{\text{frag}} = \frac{\#\operatorname{components}(T(S))}{\#\operatorname{components}(S)}
\]

For this first copy-shift probe, \(F_{\text{frag}}=47/34=1.38\), which is acceptable for a shallow proof of executability but too high for a final recursive generator.
