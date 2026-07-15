---
title: Trellis2 Handcrafted Conditioning Proxy Diagnostics
date: 2026-05-07
tags: [trellis2, diagnostics, conditioning_proxy, a100, recursive_generation]
---

# Trellis2 Handcrafted Conditioning Proxy Diagnostics

This note records the first Trellis2 image-conditioning-path experiment that does not require gated DINOv3 weights. It is deliberately labelled as a proxy, not an official TRELLIS.2 baseline.

## Method

The proxy replaces the official DINOv3 image encoder with a deterministic handcrafted feature extractor:

- resize scaffold image to `512 x 512`;
- pool RGB, grayscale intensity, simple image gradients, and coordinate channels to a `32 x 32` token grid;
- project these 8 handcrafted channels to `1024` channels with a fixed random matrix;
- run the standard Trellis2 sparse-structure, shape-SLat, texture-SLat, and decoder path at 512 resolution;
- use `NoOpRembg` so procedural scaffold images are not modified by an unavailable background-removal model.

This tests whether the image-conditioning plumbing can execute and whether any coarse scaffold signal survives through a non-learned proxy feature. It does not test official DINOv3-conditioned quality.

## Base Runs

All runs used:

- A100 host: `a100-2`
- GPU: `CUDA_VISIBLE_DEVICES=4`
- steps: `2`
- seed: `300`
- scale: `1.0`
- Triton cache: project directory only, via `triton_beegfs_cache_patch.py`

| Input scaffold | Vertices | Faces | Shape tokens | Component count | Largest component ratio | Visual conclusion |
|---|---:|---:|---:|---:|---:|---|
| IFS branch tree | 28851 | 71726 | 87 | 34 | 0.3924 | vertical block/plate fragments; original recursive crown mostly lost |
| L-system branch | 22442 | 49322 | 84 | 46 | 0.2899 | stacked block fragments; tree-like branching not preserved |
| DLA cluster | 23841 | 56620 | 86 | 41 | 0.5684 | pillar-like fragments; DLA topology not preserved |

Visual contact sheet:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_handcrafted_cond_contact_sheet_20260507.png`

## Scale Sensitivity

To test whether the proxy merely needed stronger or weaker conditioning, I fixed the IFS scaffold and seed and changed only the feature scale.

| Scale | Status | Vertices | Faces | Shape tokens | Interpretation |
|---:|---|---:|---:|---:|---|
| 0.25 | failed | - | - | - | collapsed to empty sparse coordinates before shape-SLat sampling |
| 1.0 | complete | 28851 | 71726 | 87 | executable but under-conditioned; disconnected block fragments |
| 2.0 | complete | 1566333 | 6611672 | 2375 | over-conditioned/explosive fill; large planar and blob-like fragments span most of the normalized box |

Scale contact sheet:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_handcrafted_cond_ifs_scale_sweep_contact_sheet_20260507.png`

## Interpretation

The handcrafted proxy is useful as an executable diagnostic and a negative baseline.

It shows:

- Trellis2's image-conditioned pipeline can be driven by a custom feature extractor without official DINOv3 weights;
- nonzero image features avoid the worst zero-condition collapse at `scale=1.0`;
- conditioning strength has a real effect: too weak collapses, too strong explodes;
- simple handcrafted features do not preserve recursive scaffold structure.

The important research result is therefore negative: Trellis2 needs a semantically meaningful learned image feature space, or a lower-level latent/geometry operator, for recursive growth. A random-projected handcrafted image descriptor is not enough.

## Design Implication

The next non-weight-dependent direction should focus on Trellis2 latent/geometry probes rather than more handcrafted image features:

- decode and transform returned sparse coordinates from successful runs;
- test copy, mirror, translate, and merge operators on tiny token subsets;
- measure whether decoded geometry remains bounded and whether disconnected-component count explodes;
- use procedural baselines as geometry scaffolds and metrics targets, not only as images.

Official DINOv3 weights are still needed for the real image-to-3D baseline once the user provides the manually downloaded file location.
