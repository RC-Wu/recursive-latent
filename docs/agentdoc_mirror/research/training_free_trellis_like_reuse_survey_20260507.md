---
id: NOTE-TRAINING-FREE-TRELLIS-LIKE-REUSE-20260507
title: Training-Free Trellis-Like Reuse Survey For Recursive 3D Growth
tags: [literature, training_free, trellis, trellis2, mesh_first, o_voxel, slat]
created_at: "2026-05-07T18:05:00+08:00"
---

# 结论先行

当前文献和本项目实验共同指向一个判断：如果目标是“递归 3D 生成增长”，最值得先做的 baseline 不是把递归结构渲成不自然的 2D 线稿再让 Trellis2 猜，而是把递归状态放在 Trellis/Trellis2 原生的 3D 中间表示里：

1. **mesh-first**：传统/程序方法产生粗 mesh，进入 O-Voxel/FDG，再进入 `shape_slat_encoder`。
2. **O-Voxel-first**：递归算子直接作用于 sparse voxel / FDG coordinates / intersected flags。
3. **SLAT-first**：递归算子作用于 sparse coordinates 和局部 latent features，必要时只在局部 mask 内重新采样或替换。
4. **tile/overlap composition**：大结构由多个局部块生成，通过重叠区域 blend，而不是一次性让模型生成全局。

这些方向都比“非自然 2D 条件图像”更符合 frozen 3D generator 的训练分布。

# 相关工作梳理

## TRELLIS / SLAT

- Source: [Structured 3D Latents for Scalable and Versatile 3D Generation](https://huggingface.co/papers/2412.01506)
- 关键思想：
  - TRELLIS 使用 Structured LATent, 即稀疏 3D 坐标 + 每个坐标的局部 latent feature；
  - sparse structure 定义粗几何支架，local latents 定义局部几何/外观；
  - 这天然适合“递归增长”的形式化，因为递归增长可以被定义为对 sparse coordinates 的 rewrite、copy、transform、mask edit。
- 对本项目的启发：
  - 递归算子应尽量定义在 `z = {(p_i, f_i)}` 上，而不是定义在像素线稿上；
  - 衡量 operator 的核心指标是坐标集合是否稳定扩张、局部 latent 是否可解码、未编辑区域是否保持。

## TRELLIS.2 / O-Voxel

- Sources:
  - [TRELLIS.2 project page](https://microsoft.github.io/TRELLIS.2/)
  - [microsoft/TRELLIS.2 GitHub](https://github.com/microsoft/TRELLIS.2)
- 关键思想：
  - TRELLIS.2 用 O-Voxel 作为 field-free sparse voxel representation；
  - O-Voxel/FDG 支持 open surfaces、non-manifold geometry 和内含结构；
  - mesh 与 O-Voxel 的双向转换是 rendering-free / optimization-free 的；
  - TRELLIS.2 的 Sparse 3D VAE 使用 16x spatial compression。
- 对本项目的启发：
  - 用户提出的 mesh-first 很合理，因为 O-Voxel 正是 TRELLIS.2 原生的数据入口；
  - 传统程序 mesh 不需要完美 watertight，O-Voxel 明确支持开放和非流形拓扑；
  - 最简单的可跑 baseline 是 `mesh -> O-Voxel -> shape_slat_encoder -> shape_slat_decoder`，然后再加局部 latent rewrite。

## VoxHammer

- Sources:
  - [arXiv:2508.19247](https://arxiv.org/abs/2508.19247)
  - [VoxHammer project page](https://huanngzh.github.io/VoxHammer-Page/)
  - [VoxHammer GitHub](https://github.com/Nelipot-Lee/VoxHammer)
- 关键思想：
  - training-free 3D editing；
  - 直接在 native 3D latent space 操作，而不是多视图 2D editing 后重建；
  - 对输入 3D 模型做 inversion，缓存每个 timestep 的 latents 和 key-value tokens；
  - denoising 时在保留区域替换回 source latents / cached K-V tokens，以保证未编辑区域一致。
- 对本项目的启发：
  - 递归增长可以被看成“局部编辑 + 保留区域约束”的反复应用；
  - 如果未来能接入 Trellis/Trellis2 sampler timestep hooks，优先尝试 masked latent replacement / K-V replacement；
  - 我们当前的 shallow sparse-coordinate transform probe 是 VoxHammer 思路的弱化版本：还没有 inversion trajectory，也没有 K-V cache，但已经证明 sparse coordinate edit 可解码。

## 3D-LATTE

- Source: [arXiv:2509.00269](https://arxiv.org/abs/2509.00269)
- 关键思想：
  - training-free instruction editing；
  - 在预训练 native 3D diffusion model 的 latent space 内编辑；
  - 使用 3D attention injection、geometry-aware regularization、frequency modulation 和 refinement；
  - 主要反对点同样是：2D priors / multi-view editing 容易引入 view inconsistency。
- 对本项目的启发：
  - 递归 operator 需要显式的 geometry regularization，否则结构可能变透明、消失或漂移；
  - 频域/尺度退火可借鉴到递归增长：先低频/粗结构稳定，再加入高频局部细节；
  - 评估应分离“语义变化/增长成功”和“未编辑区域保持”。

## TRELLISWorld

- Sources:
  - [arXiv:2510.23880](https://arxiv.org/abs/2510.23880)
  - [Hugging Face paper page](https://huggingface.co/papers/2510.23880)
- 关键思想：
  - training-free world generation from object generators；
  - 将对象级 3D generator 重用为局部 tile generator；
  - overlapping 3D regions 独立生成后用 weighted/cosine blending 融合；
  - 避免 scene-level dataset 和 retraining。
- 对本项目的启发：
  - 递归增长可以被定义为 tile/branch/node 的局部块生成，而不是全局一次性生成；
  - 对树、珊瑚、晶体这类递归结构，可把每个分支/团簇看作局部 tile；
  - overlap blending 是处理递归连接处的关键，而不是简单 copy-paste。

## SK-Adapter

- Source: [SK-Adapter project page](https://sk-adapter.github.io/)
- 关键思想：
  - 用 Trellis 作为 backbone；
  - 把 skeleton 作为 native 3D structural control，而非 2D projection；
  - 注入 joint-based positional tokens 到 sparse structure transformer blocks；
  - 这是 adapter/fine-tuning 方向，不是完全 training-free。
- 对本项目的启发：
  - 虽然本阶段以 training-free 为主，但它说明“骨架/图结构直接进入 3D token space”是合理控制形式；
  - 对后续可训练版本，递归 L-system tree skeleton 可以成为控制 token，而非图片条件。

# 和本项目当前实验的关系

## 已被否定或降级的路径

1. **zero-condition Trellis2**
   - 大量 seed collapse 或薄片化；
   - 只能证明环境可用，不是有效生成 baseline。
2. **handcrafted image feature proxy**
   - scale 敏感，弱则空，强则爆；
   - 递归拓扑不保留。
3. **普通 DINOv3 image-conditioned procedural line/point render**
   - Trellis2 对正常 object-like example images 表现好；
   - 对程序线稿/点云渲染表现差，说明输入分布不对。

## 新的正信号

`mesh_first_reconstruct_proc_gpu0_projectcache_20260507_1745` 直接测试：

```text
procedural mesh
  -> O-Voxel / Flexible Dual Grid
  -> shape_slat_encoder
  -> shape_slat_decoder
```

结果：

| Input | FDG voxels | Shape SLat tokens | Shape SLat reconstruction | Visual conclusion |
|---|---:|---:|---:|---|
| IFS tree mesh | 530,379 | 1,514 | 530,379 V / 1,155,682 F | branch layout preserved |
| L-system branch mesh | 661,423 | 1,692 | 661,423 V / 1,502,740 F | branch mass preserved |

这说明：

- O-Voxel 可以吃下当前程序 mesh；
- `shape_slat_encoder -> shape_slat_decoder` 不会像 image-conditioned scaffold 那样崩掉；
- mesh-first 是当前最可信的 baseline 起点；
- 但这只是 reconstruction，不是 naturalization。下一步需要在 mesh/O-Voxel/SLAT 层加入 generative operator。

# 下一批实验设计

## A. Mesh-First Reconstruction Matrix

目的：确认哪些 coarse element 可以进入 Trellis2-native path。

Cases:

- IFS mesh, L-system mesh, DLA voxel mesh；
- Trellis2 generated tree mesh recycled as next root；
- later: image-to-mesh generated root, user-provided mesh root。

Metrics:

- FDG active voxel count；
- shape SLat token count；
- decode mesh V/F；
- connected components；
- bbox drift；
- visual preservation score。

## B. O-Voxel Recursive Operators

Training-free operators:

- coordinate copy + rigid transform；
- branch-tip duplication；
- voxel dilation/erosion；
- overlap blend between copied branches；
- local replacement only within mask。

关键问题：

- O-Voxel roundtrip 后结构是否仍可辨认；
- FDG 的 `intersected` flags 能否简单变换；
- 操作后是否还能进入 `shape_slat_encoder`。

## C. SLAT Recursive Operators

Training-free operators:

- sparse coordinate transform；
- copy subset based on branch-tip mask；
- feature interpolation / feature reuse；
- local latent noise injection；
- optional sampler re-denoise if hooks accessible。

借鉴 VoxHammer/3D-LATTE：

- 保留区 latent replacement；
- edited/grown region 单独采样；
- geometry regularization；
- 多尺度或频率退火。

## D. Object-Like Render Adapter

这不是主线，但仍值得做一批对照：

- 从 mesh 渲染 alpha-masked shaded object image；
- 避免点云/线稿；
- 用 DINOv3-conditioned Trellis2 跑；
- 比较是否比先前 procedural PNG 更稳定。

这个路径的作用是验证“如果最粗元素只有图片，怎么得到第一个 mesh”。一旦得到 mesh，应转入 mesh-first/O-Voxel-first。

# 当前最小方法雏形

一个可发表方向的最小形式可以是：

```text
root coarse element
  -> mesh or O-Voxel
  -> shape SLat
  -> recursive sparse operator
  -> local generative repair / denoise / texture fill
  -> next depth
```

核心主张不应是“训练一个更强 3D 生成器”，而是：

> 用 frozen native 3D generator 的 mesh/O-Voxel/SLAT 中间空间，把传统递归结构转成可自然化、可局部编辑、可多步组合的生成过程。

# 风险

- 当前 mesh-first reconstruction 会把简单程序 mesh 变成高面数 dense mesh，后续需要 decimation 或 token budget 控制。
- Reconstruction 保留结构不等于 generative naturalization，需要额外 sampler/latent repair 才能提升自然性。
- Trellis2 texturing full GLB 仍缺 `nvdiffrast`，但 latent-only texture path 已经可跑。
- 如果直接在 FDG/O-Voxel 上做拓扑操作，`intersected` flags 的物理意义可能被破坏，需要 roundtrip 检查。

