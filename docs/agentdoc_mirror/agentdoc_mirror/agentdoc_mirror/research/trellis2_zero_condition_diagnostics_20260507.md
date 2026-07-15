---
title: Trellis2 Zero-Condition Diagnostics
date: 2026-05-07
tags: [trellis2, diagnostics, zero_condition, a100]
---

# Trellis2 Zero-Condition Diagnostics

This note records the first Trellis2 executable baseline on `a100-2`. The run intentionally bypasses image conditioning because official TRELLIS.2 image conditioning currently depends on gated DINOv3 weights.

## Environment Findings

- Trellis2 imports work in the existing new-A100 environment.
- `o_voxel` and `cumesh` import successfully.
- Required 512-resolution TRELLIS.2 flow and decoder weights are present in the project-local Hugging Face cache.
- `microsoft/TRELLIS-image-large/ckpts/ss_dec_conv3d_16l8_fp16.*` is present.
- Official image conditioning is blocked by gated `facebook/dinov3-vitl16-pretrain-lvd1689m` access. The local cache only contains DINOv3 README/LICENSE metadata, not model weights.
- The environment also lacks installed `torchvision`; a minimal local shim was sufficient for zero-condition import tests, but not a substitute for official image-conditioned quality evaluation.

## Cache Findings

Triton/flex_gemm dynamic-library cache initially failed on BeEGFS when Triton tried to replace loaded dynamic libraries with `os.replace(...cuda_utils.so)`, raising `Errno 16 Device or resource busy`.

An intermediate smoke used `/dev/shm` as a transient cache and confirmed the model path, but this is no longer the active policy. The user explicitly requested no `/dev/shm` and no `/tmp` use for this project.

The current workable configuration uses only project-directory caches:

- `TRITON_CACHE_DIR` under `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/triton/<run>`;
- `TORCHINDUCTOR_CACHE_DIR` under the same project cache tree;
- `XDG_CACHE_HOME`, `TORCH_HOME`, `MPLCONFIGDIR`, and `TMPDIR` under the same project root;
- `triton_beegfs_cache_patch.py`, which catches the BeEGFS `Errno 16` path in Triton's `FileCacheManager.put` and falls back to direct run-scoped cache writes.

The project-cache patch was validated by `zero_cond_projectcache_patch_20260507_1251_seed123`, which completed without `/dev/shm` or `/tmp`.

## Single Smoke

Run:

`zero_cond_xformers_shmtriton_20260507_1228_seed123`

Metrics:

- steps: `2`
- seed: `123`
- vertices: `16`
- faces: `12`
- shape latent tokens: `2`
- texture latent tokens: `2`
- load seconds: `50.38`
- run seconds: `11.72`

Visual:

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_zero_cond_shmtriton_20260507_1228_seed123/trellis2_zero_cond_preview.png`

Interpretation:

The complete Trellis2 sparse-structure, shape-SLat, texture-SLat, and decoder path can execute. The output is a tiny degenerate fragment and has no generative baseline value.

## Seed Sweep

Run:

`zero_cond_seed_sweep_shmtriton_20260507_1231_seeds120_129`

Inputs:

- seeds: `120..129`
- steps: `2`
- conditioning: zero DINO token tensor, not image conditioning

Summary:

- successful seeds: `3/10`
- failed seeds: `7/10`
- recurring failure: empty sparse coordinates before shape SLat, producing `RuntimeError: max(): Expected reduction dim to be specified for input.numel() == 0`.

Successful seeds:

| Seed | Vertices | Faces | Shape Tokens | Visual Note |
|---:|---:|---:|---:|---|
| 123 | 16 | 12 | 2 | tiny diagonal point/triangle fragment |
| 126 | 10903 | 11216 | 482 | flat oval sheet with speckled holes; not object-like |
| 129 | 21248 | 33026 | 185 | flat torn sheet/flake; not object-like |

Visuals:

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_zero_cond_seed_sweep_20260507_1231_seeds120_129/seed_123/trellis2_zero_cond_preview.png`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_zero_cond_seed_sweep_20260507_1231_seeds120_129/seed_126/trellis2_zero_cond_preview.png`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/trellis2_zero_cond_seed_sweep_20260507_1231_seeds120_129/seed_129/trellis2_zero_cond_preview.png`

## Research Interpretation

Zero-condition Trellis2 is useful only as an availability and operator-path diagnostic.

It is not a valid baseline for recursive generative growth because:

- most seeds collapse before shape SLat;
- successful seeds produce thin fragments or tiny debris rather than coherent geometry;
- there is no scaffold preservation signal because no scaffold is actually conditioned;
- face count alone is misleading: seed `129` has `33,026` faces but visually remains a flat torn sheet.

The next useful baseline must restore a meaningful conditioning path. Without DINOv3, a DINOv2 proxy smoke can test whether the Trellis2 conditioning API remains executable, but it must be labelled as non-official because the learned model was configured for DINOv3.
