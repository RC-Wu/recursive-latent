---
id: RESEARCH-RECURSIVE-GROWTH-LIT-BASELINE-20260507
title: Recursive Growth Literature And Baseline Notes
tags: [research, literature, trellis2, procedural_modeling, diffusion]
domain: [3d_generation, research]
summary: "Initial related-work synthesis and implications from first traditional procedural baselines for recursive 3D generative growth."
updated_at: "2026-05-07"
owner: "codex"
---

# Purpose

This note captures the first-pass research framing while Trellis2 weights download on the new A100. It is intentionally practical: each related-work cluster is mapped to an experiment implication for the current project.

# Source Anchors

| Work | Type | Key Point | Relevance |
|---|---|---|---|
| [TRELLIS.2: Native and Compact Structured Latents for 3D Generation](https://arxiv.org/abs/2512.14692) | arXiv 2025 | O-Voxel and SC-VAE provide structured sparse latents with arbitrary topology and PBR attributes. | Primary backbone. The proposal depends on whether these latents are spatially editable, not merely high-quality one-shot generation. |
| [DreamFusion](https://arxiv.org/abs/2209.14988) | arXiv 2022 | Uses a pretrained diffusion model as a prior through score distillation for 3D optimization. | Important contrast: this project should avoid becoming only an external guidance/loss method. |
| [MVDream](https://arxiv.org/abs/2308.16512) | arXiv 2023/2024 | Multi-view diffusion improves 3D consistency and stabilizes SDS-style lifting. | Shows that consistency priors matter; recursive growth must preserve structure across repeated operations, not only across views. |
| [DreamFlow](https://arxiv.org/abs/2403.14966) | ICLR 2024 | Interprets text-to-3D optimization through probability-flow-like deterministic schedules to reduce noisy timestep variance. | Supports testing deterministic or low-variance partial denoise schedules for recursive edits. |
| [Sin3DM](https://arxiv.org/abs/2305.15399) | ICLR 2024 | Learns internal patch distributions of a single 3D asset and supports retargeting/outpainting/local editing. | Closest conceptual neighbor for local 3D generative operations, but it trains per-shape; this project asks for frozen-model reuse. |

# Immediate Synthesis

## Why Trellis2 Is More Suitable Than 2D SDS For This Project

DreamFusion-style SDS proved that pretrained diffusion priors can drive 3D optimization without 3D training data, but it operates through rendered 2D views and gradient optimization. That makes it a weak match for recursive grammar operations, because the grammar state lives in a 3D structure while the guidance signal is view/image mediated.

Trellis2 is a better empirical target because its representation is already a sparse native 3D structure. If its SC-VAE and flow sampler expose coordinates and sparse latent features cleanly, recursive edits can be stated as actual spatial operations rather than as rendered-image penalties.

## Why Traditional Procedural Baselines Still Matter

The first local baselines confirm the proposal's motivation:

- IFS and L-systems make recursion highly legible but produce schematic local geometry.
- DLA gives useful organic/crystal topology but has lattice artifacts and weak asset usability.
- These baselines are not weak because they lack global structure; they are weak because they lack local naturalization, material plausibility, and semantic asset priors.

This suggests a clean research criterion: Trellis2 must improve local surface/material plausibility without erasing the recursive scaffold. If it only produces a high-quality unrelated asset, it fails the method claim.

## Operator Risks To Test First

1. Transform equivariance is not guaranteed. A sparse 3D latent may be coordinate-aware in ways that make arbitrary rotations or scales out-of-distribution.
2. Partial denoising may be a deletion operator. If re-noise levels are too high, the model may erase grammar scaffolds.
3. Low re-noise may preserve structure but fail to naturalize artifacts. This creates a preservation/naturalization Pareto curve.
4. Recursion can amplify bias. Small local cleanup errors can compound over depth and collapse into repeated noise, blobs, or disconnected components.

# Baseline Observations From 2026-05-07

Outputs:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/traditional_baselines/run_20260507_0300`
- contact sheet: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baselines_contact_sheet.png`

Observations:

- IFS branch has the best candidate silhouette for a first naturalization test because it resembles plant/coral growth but remains visibly procedural.
- L-system branch is better for preservation metrics because repeated structure is regular and easier to detect.
- DLA cluster is better for topology stress testing because it has many thin appendages and disconnected-looking local neighborhoods.

# Implications For Next Trellis2 Tests

Recommended first Trellis2 diagnostics:

1. Run the official image-to-3D example at low steps and `pipeline_type=512`.
2. Save returned `shape_slat` token count and coordinates; inspect whether coordinates are directly transformable.
3. Use L-system and DLA as image prompts or scaffold proxies only after the official example succeeds.
4. Build a preservation metric from simple bounding-box/self-similarity statistics before attempting subjective artistic demos.
5. For the first recursive method, prefer "sample once, transform sparse coordinates/features, decode or partially resample" over any full scene-level Droste/Escher task.

