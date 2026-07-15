---
title: Trellis2 Conditioning Problem Reframe And VAE Coverage
date: 2026-05-07
tags: [trellis2, conditioning, vae, problem_definition, recursive_generation]
---

# Trellis2 Conditioning Problem Reframe And VAE Coverage

This note records the shift in framing after official DINOv3-conditioned smoke tests and the first mesh-conditioned texturing latent smoke.

## Updated Problem Definition

The empirical evidence so far argues against framing Trellis2 as a generator that should be forced to directly follow arbitrary recursive point/line scaffolds.

The sharper problem is:

> How can a recursive/procedural coarse representation be converted into a Trellis2-native condition or latent state so that Trellis2 performs learned naturalization while preserving recursive structure?

This changes the method search:

- weak framing: feed unusual scaffold renderings and hope the image-conditioned generator follows them;
- stronger framing: learn or design a coarse-to-native adapter that maps recursive state into one of Trellis2's native interfaces:
  - normal image condition with transparent object-like render;
  - sparse-structure occupancy;
  - shape SLat coordinates/features;
  - mesh-to-shape-SLat texturing path;
  - shallow latent coordinate edits followed by decoder or partial denoising.

## Evidence: Procedural Scaffolds Are Out Of Distribution

Official DINOv3 path, procedural scaffolds, `steps=2`:

| Input | Vertices | Faces | Shape tokens | Visual |
|---|---:|---:|---:|---|
| IFS | 62174 | 103168 | 162 | thin oval sheet |
| L-system | 16094 | 28494 | 316 | separated flakes/layers |
| DLA | 2424 | 2368 | 334 | tiny sparse sheet fragments |

IFS `steps=8` improved 3D extent and produced a canopy-like fragment, but component count worsened:

| Run | Vertices | Faces | Tokens | Components | Largest component ratio |
|---|---:|---:|---:|---:|---:|
| IFS steps=2 | 62174 | 103168 | 162 | 312 | 0.9379 |
| IFS steps=8 | 91628 | 104054 | 481 | 3320 | 0.1792 |

Interpretation: more denoising steps can make the output less flat, but it does not solve scaffold preservation. It increases fragmentation.

## Evidence: Normal Trellis Example Images Work Better

Using Trellis2's own transparent example images with official DINOv3 features, alpha preprocessing, `steps=8`:

| Input | Vertices | Faces | Shape tokens | Visual reading |
|---|---:|---:|---:|---|
| vine curl / ornamental plant | 459010 | 878142 | 2010 | plausible curled plant-like structure |
| tree | 868409 | 1780806 | 3544 | recognizable tree/canopy-trunk organization |
| lattice with vines | 1625023 | 3368154 | 3879 | large structured wall/lattice-like volume, though preview is dense |

Contact sheet:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_dinov3_example_inputs_20260507_seed300/trellis2_dinov3_example_inputs_contact_sheet_20260507_seed300.png`

Interpretation: Trellis2 is functioning as a condition generator when the input is object-like and close to its expected image distribution. The failure on procedural scaffold images is therefore not merely a broken environment or missing VAE path.

## VAE / Decoder Coverage

The current smoke tests cover more than only the sparse-structure VAE.

### Image-To-3D Pipeline

The `Trellis2ImageTo3DPipeline` path uses:

1. image feature extractor: DINOv3;
2. sparse-structure flow model;
3. `sparse_structure_decoder`, producing sparse occupancy coordinates;
4. shape SLat flow model;
5. `shape_slat_decoder`, producing mesh geometry and substructures;
6. texture SLat flow model;
7. `tex_slat_decoder`, producing PBR voxel attributes;
8. mesh-with-voxel packaging.

So the image-to-3D tests do use sparse structure, shape, and texture decoder branches. They do not test the corresponding encoders.

### Texturing Pipeline

The `Trellis2TexturingPipeline` adds a mesh-native path:

1. input mesh normalization;
2. `shape_slat_encoder`, encoding mesh geometry into shape SLat;
3. DINOv3 image condition;
4. texture SLat flow model;
5. `tex_slat_decoder`, producing PBR voxel attributes;
6. optional UV/PBR postprocess.

The full GLB postprocess currently requires `nvdiffrast`, which is missing in the A100 environment. Instead, a latent-level texturing smoke was run without the rasterization postprocess.

Latent texturing smoke:

- mesh: traditional L-system branch mesh;
- image condition: Trellis example tree image;
- resolution: `512`;
- texture steps: `4`;
- `shape_slat_tokens=1692`;
- `tex_slat_tokens=1692`;
- `pbr_voxel_tokens=661423`;
- `pbr_voxel_channels=6`;
- `pbr_mean=0.4413`;
- load seconds: `20.10`;
- run seconds: `96.76`.

This confirms the mesh-to-shape-SLat encoder path and texture decoder path can execute up to PBR voxel output.

## Method Implications

The method should not be "Trellis2 follows recursive line art." A stronger thesis is:

> Recursive growth should be expressed as a coarse object-level condition in Trellis2's native geometry or image manifold, then Trellis2 is used as a learned naturalization operator.

Promising routes:

1. **Object-like render adapter**
   - Render procedural growth as shaded, alpha-masked, object-like images rather than dots/line scaffolds.
   - Test whether Trellis2 preserves structure better when input resembles its examples.

2. **Mesh-first shape encoder route**
   - Use procedural mesh as coarse geometry.
   - Encode with `shape_slat_encoder`.
   - Use Trellis2 texture / latent operators for naturalization.
   - This is conservative because it preserves geometry by construction.

3. **Sparse latent operator route**
   - Use Trellis2 to obtain a plausible base latent.
   - Apply shallow copy/mirror/branch edits in sparse coordinates.
   - Decode or partially re-noise/denoise.
   - This is the closest route to a recursive generative operator, but it requires careful boundedness and fragmentation metrics.

The next empirical priority should be route 1 and route 2 before more exotic guidance tricks.
