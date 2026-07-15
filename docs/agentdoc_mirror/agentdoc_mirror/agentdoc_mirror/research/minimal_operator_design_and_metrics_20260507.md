---
id: RESEARCH-RECURSIVE-GROWTH-OPERATOR-DESIGN-20260507
title: Minimal Operator Design And Metrics For Recursive Trellis2 Growth
tags: [research, method_design, metrics, trellis2, recursive_generation]
domain: [3d_generation, experiments]
summary: "Concrete minimal algorithms, diagnostics, and metrics for testing Trellis2 as a recursive naturalization operator."
updated_at: "2026-05-07"
owner: "codex"
---

# Goal

Turn the proposal into falsifiable experiments. The method claim is not "Trellis2 can make nice 3D assets"; it is:

> A frozen structured 3D generator can be repeatedly used as a local naturalization operator inside a recursive procedural sampling program.

# Minimal Operators

## Operator 0: One-Shot Image-To-3D

Input:

- an ordinary image prompt
- a procedural scaffold render

Output:

- a single Trellis2 mesh
- returned sparse/structured latents if `return_latent=True`

Purpose:

- establish base model usability
- measure whether a procedural scaffold image can be interpreted as a plausible 3D object

Failure modes:

- model download/load failure
- prompt ignored
- model produces unrelated object
- model overfits to 2D view and loses recursive structure

## Operator 1: Geometry-Space Scaffold Naturalization Proxy

Input:

- procedural mesh or point scaffold
- one or more rendered views of that scaffold

Procedure:

1. render scaffold to image
2. feed image to Trellis2
3. compare output against scaffold statistics

This is not the final latent method, but it is a valid baseline because it tests whether the pretrained model can map a recursive scaffold cue to a usable 3D asset.

## Operator 2: Sparse Coordinate Transform Probe

Input:

- `(shape_slat, tex_slat, resolution)` returned by Trellis2

Candidate transforms:

- translation in sparse coordinate space
- mirror across one axis
- scale toward/away from local centroid
- copy-and-merge token subset

Core question:

- Are sparse coordinates and features independent enough that coordinate transforms survive decode?

Implementation note:

- This should start with shape-only decode because texture latents may contain coordinate-coupled PBR attributes.
- The first copy/merge should use tiny token subsets and collision resolution by unique coordinates.

Concrete first probe:

Let a structured latent be

\[
S = (C, F), \quad C \in \mathbb{Z}^{N \times 4}, \quad C_i = (b_i, x_i, y_i, z_i)
\]

where `b_i` is the batch id and `(x_i,y_i,z_i)` are sparse-grid coordinates. A coordinate transform leaves feature vectors unchanged first:

\[
T_\phi(S) = (\phi(C), F)
\]

The first transform family is intentionally simple:

\[
\phi_{\text{mirror-x}}(b,x,y,z) = (b, x_{\min} + x_{\max} - x, y, z)
\]

This tests equivariance of the decoder to a coordinate-space symmetry without increasing token count.

The first recursive/copy transform is:

\[
S' = \operatorname{merge}\left(S,\; (C_{\Omega} + \Delta, F_{\Omega})\right)
\]

where \(\Omega=\{i: z_i \geq \operatorname{median}(z)\}\) and \(\Delta=(0,\Delta_x,0,\Delta_z)\). Coordinate collisions are merged by averaging features at identical coordinates:

\[
F'_c = \frac{1}{|\{i:C'_i=c\}|}\sum_{i:C'_i=c}F'_i
\]

This is deliberately not yet a learned denoising step. It asks a narrower question: can Trellis2's decoder render a shallow coordinate-space recursive edit without immediate collapse, explosion, or disconnected debris?

Acceptance criteria for this probe:

- mirror-x should preserve token count and produce a decodable mesh with comparable vertex/face count;
- copy-shift should increase token count modestly and remain within the normalized bbox, not fill the whole cube;
- disconnected component count should not increase superlinearly;
- if texture decode fails while shape decode works, future probes should separate shape and texture operators.

## Operator 3: Recursive Depth Probe

State:

\[
S_k = (C_k, F_k)
\]

where `C` are sparse coordinates and `F` are latent features or a geometry proxy.

Rewrite:

\[
S_{k+1} = \operatorname{merge}(S_k, T_k(P_{\Omega}(S_k)))
\]

Then either:

- decode directly, or
- if sampler hooks are accessible, partially re-noise and denoise.

Depths:

- `K=1`: one copy/branch
- `K=2`: repeated self-similar copy
- `K=3`: first stress test

# Metrics

## Preservation

Preservation asks whether the recursive scaffold remains legible.

Suggested metrics:

- bounding-box extent ratio compared with scaffold
- principal-axis alignment from PCA
- occupancy/token count growth across depth
- connected component count and largest component ratio
- self-similarity proxy: nearest-neighbor distance histogram at multiple scales

## Naturalization

Naturalization asks whether Trellis2 improves raw procedural artifacts.

Suggested metrics:

- visual smoothness and local surface continuity
- face count and degenerate face ratio
- non-manifold or boundary count if a mesh library is available
- reduction in obviously lattice-like artifacts for DLA
- material/color plausibility if texture decode/export works

## Recursive Stability

Recursive stability asks whether repeated application remains bounded.

Track:

- token/vertex/face growth per depth
- bbox growth per depth
- number of tiny disconnected components
- collapse score: output bbox or vertex count shrinks sharply despite intended expansion
- explosion score: token count or bbox grows superlinearly beyond rule expectation

# First Decision Tree

1. If full Trellis2 image-to-3D works:
   - run official image smoke
   - run L-system and DLA scaffold prompt smoke
   - inspect visuals locally
2. If image-to-3D load works but generation is too slow:
   - reduce sampler steps
   - restrict to `pipeline_type=512`
   - run one scaffold prompt only
3. If full generation fails but SC-VAE models load:
   - pivot to shape SC-VAE reconstruction and sparse coordinate transform probes
4. If model weights/deps fail:
   - document exact missing file/dependency and do not claim model behavior

# Current Hypothesis

The likely first useful method is not a full Droste/Escher scene. It is a recursive growth scaffold whose image or sparse-latent proxy is repeatedly transformed at shallow depths, with Trellis2 used to replace procedural local artifacts with learned geometry. The first publishable figure should show a preservation/naturalization trade-off curve rather than only a cherry-picked final asset.
