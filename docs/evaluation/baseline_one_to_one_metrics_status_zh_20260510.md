# Baseline 一对一候选指标状态 2026-05-10

## 输出位置

- 渲染目录：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/baseline_one_to_one_white_20260510/renders`
- contact sheet：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/baseline_one_to_one_white_20260510/baseline_one_to_one_white_contact_20260510.png`
- zoom callout sheet：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/baseline_one_to_one_white_20260510/baseline_one_to_one_white_zoom_20260510.png`
- 指标 CSV：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/baseline_one_to_one_metrics_20260510/metrics.csv`
- 指标 JSON：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/baseline_one_to_one_metrics_20260510/metrics.json`
- Surface-sampled 指标 CSV：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/baseline_one_to_one_surface_metrics_20260510/surface_metrics_occ64.csv`
- Surface-sampled 指标 JSON：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/baseline_one_to_one_surface_metrics_20260510/surface_metrics_occ64.json`
- CLIP 多视角 prompt 指标 CSV：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/baseline_one_to_one_clip_metrics_20260510/multiview_clip_prompt_scores.csv`
- CLIP 多视角 prompt 指标 JSON：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/baseline_one_to_one_clip_metrics_20260510/multiview_clip_prompt_scores.json`

## 快速读数

当前 `recursive_growth_mesh_metrics.py` 的 primary metric 是 vertex-occupancy 6-neighborhood 连接性，比 raw face component 更适合混合比较 OBJ/GLB/tube/材质 seam。raw face components 对 GLB 材质岛极其敏感，只能做 mesh diagnostic。

| 对比 | baseline primary comp/LCR | ours primary comp/LCR | 当前建议 |
|---|---:|---:|---|
| L-system branch vs ours vine | 315 / 0.115 | 1 / 1.000 | 对比优势很强：baseline textured export 后 occupancy 破碎，我们保持主支持连通；但 baseline 在原始结构域并不弱，文中要分开讲。 |
| Space colonization tree vs ours vine/root | 278 / 0.364 | 1 / 1.000 | 可展示 ours 在 Trellis2 texture/export 后保持连通；SC 传统结构控制强，不能 strawman。 |
| DLA cluster vs ours coral | 2511 / 0.002 | 1 / 1.000 | 指标差异极强，但必须谨慎：DLA baseline 本身是 cluster/fragments 生成，视觉上 ours coral 更像资产，但不是物理 DLA 复现。 |
| IFS transform tree vs ours pyrite | 62 / 0.920 | 1 / 1.000 | 适合作为 transform-copy/symmetry 正例；IFS baseline LCR 已经不错，但 component count 不为 1。 |

## 细节注意

- `ours_vine_stage5` raw face components 很高，但 occupancy connected；这说明 GLB 材质/面片 seam 不能作为主拓扑指标。
- `ours_vine_root`, `ours_coral_octopus`, `ours_pyrite_lattice` 的 welded components 都是 1，较适合正面展示。
- `dla_cluster_baseline` 在 welded component 上是 1，但 occupancy 6N 很碎，说明它的顶点/表面几何分布在固定 voxel proxy 下离散严重；这可以解释为什么视觉上是碎块状。
- 这张 screening 图仍需重新做 camera-tuned zoom：当前 zoom 是从 2D render 自动 crop，满足“矩形框对应 crop”的格式要求，但不是最终论文级相机 zoom。

## Surface-sampled 指标修正

为了避免 vertex-occupancy 对 GLB 顶点分布、材质 seam、三角化方式过敏，我把同一批 8 个 GLB 用 `batch_surface_voxel_metrics_20260509.py` 做了表面采样体素连通性。这个指标更适合回答“渲染表面是否连成一个可用 asset”。

| case | comps r0 | LCR r0 | comps r1 | box dim | verts | faces |
|---|---:|---:|---:|---:|---:|---:|
| dla_cluster_baseline | 3 | 0.9998 | 1 | 2.015 | 21,600 | 10,800 |
| ifs_branch_tree_baseline | 1 | 1.0000 | 1 | 2.006 | 93,494 | 65,600 |
| lsystem_branch_baseline | 3 | 0.9997 | 1 | 1.977 | 32,426 | 20,736 |
| ours_coral_octopus | 1 | 1.0000 | 1 | 2.182 | 237,047 | 180,132 |
| ours_pyrite_lattice | 1 | 1.0000 | 1 | 2.153 | 294,399 | 226,088 |
| ours_vine_root | 1 | 1.0000 | 1 | 2.027 | 39,704 | 29,496 |
| ours_vine_stage5 | 1 | 1.0000 | 1 | 1.970 | 647,958 | 455,964 |
| sc_tree_canopy_baseline | 1 | 1.0000 | 1 | 1.806 | 44,960 | 31,700 |

这个结果改变了论文里的表述方式：

- 不应该说传统 baseline “本质上破碎”。在 surface-sampled proxy 下，L-system、IFS、SC、DLA 基本都可以形成一个连通表面支持。
- 更合理的 claim 是：传统方法在结构控制上强，但视觉/纹理/PBR 需要额外工程；我们的最终候选在同一 Trellis2 纹理化和 GLB 出口下，仍能保持单主连通表面，同时给出更 asset-like 的材质和高频细节。
- DLA baseline 的 vertex-occupancy 极碎但 surface-sampled 连通，说明“碎块问题”要分两类：视觉碎块/体素块感是一类，拓扑断裂是另一类。后续 DLA/晶体线应同时报告 surface connectivity 和 blockiness/naturalization 指标。

## 多视角 CLIP prompt 指标

我新增了 render-based CLIP 文本图像指标脚本：`assets/multiview_clip_prompt_metrics_20260510.py`。它只读取白底 Blender render 图，不读点云或内部 mesh，因此更接近论文读者看到的视觉证据。当前模型为 `openai/clip-vit-base-patch32`，缓存放在项目目录 `cache/huggingface` 下。

| case | prompt mean cosine | 解释 |
|---|---:|---|
| lsystem_branch_baseline | 0.2473 | 传统 branch 语义可读，但无现代 asset texture。 |
| ours_vine_stage5 | 0.2731 | 高于 L-system branch；适合支持 vine/root 类视觉优势。 |
| sc_tree_canopy_baseline | 0.2745 | 比当前 ours vine/root 高，说明这组需要换更贴近 tree canopy 的 ours 候选，不能直接宣称胜出。 |
| ours_vine_root | 0.2593 | 作为 root/vine 可用，但不是 tree canopy 的语义最佳匹配。 |
| dla_cluster_baseline | 0.2501 | DLA/coral 类语义一般。 |
| ours_coral_octopus | 0.2655 | 高于 DLA baseline；但仍需 blockiness/naturalization ablation 支撑视觉质量。 |
| ifs_branch_tree_baseline | 0.2718 | 对 recursive branching tree prompt 仍然强。 |
| ours_pyrite_lattice | 0.3584 | 对 pyrite crystal lattice prompt 优势很强，建议作为 symmetry/transform 正例。 |

这组指标只适合作为 auxiliary semantic/render metric，不能替代结构指标或人类视觉选择。最重要的策略变化是：Space Colonization 对比要么换 ours tree/canopy 候选，要么明确写成“结构控制 baseline vs root/vine asset candidate”的非同类筛选，不适合主文最终定量表。

## 下一步

1. 给 Space Colonization 组重新找或生成 ours tree/canopy 候选，至少做 3 个候选后再让用户挑。
2. 对最终选中 case 用 Blender camera-level zoom 而不是 2D crop，至少 overview + root/junction/tip/facet 三层。
3. 为 DLA/晶体线单独增加 blockiness、surface smoothness、mask naturalization 前后差异指标，避免把拓扑连通性和视觉块感混为一谈。
4. 如果要把 CLIP 写入正文，只写成辅助语义一致性指标；核心结论仍应来自 connectivity、projection stability、surface/mesh quality 和人类视觉筛选。
