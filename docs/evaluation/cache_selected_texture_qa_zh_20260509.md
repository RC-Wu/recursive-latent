# Cache-selected 非树纹理批次 QA（2026-05-09）

## 目的

这轮实验直接回应用户对 DLA、晶体、radial、sci-fi 等非树类结果“碎块不可接受”的批评。我们从 cache / voxel fusion / masked local sampler 代理实验中选出更连通的 OBJ mesh，再送入真实 Trellis2 texture/PBR export，测试它们能否成为可用 textured mesh。

## 输入与运行

本地输入：

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/inputs/cache_sampler_selected_20260509`

远端运行：

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/cache_selected_texture_20260509`

本地拉回：

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/cache_selected_texture_20260509`

四个 case：

| case | 输入来源 | guide | 结果 |
|---|---|---|---|
| `cache_dla_masked_sampler` | masked-local-sampler-selected DLA mesh | octopus suckers | GLB 成功 |
| `cache_radial_transform_fusion` | transform-cache radial mesh | gear train | GLB 成功 |
| `cache_bismuth_transform_fusion` | transform-cache bismuth mesh | bismuth crystal | GLB 成功 |
| `cache_scifi_connected` | connected sci-fi control mesh | gear train | GLB 成功 |

## 视觉结果

合成图：

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/cache_selected_texture_qa_20260509.png`

视觉判断：

- DLA/octopus：纹理上有语义，但顶部大平面和块状支撑很明显，更像 voxel artifact 资产，不适合作主结果。
- Radial/gear：有机械/绿色材质感，但几何仍是块状体，递归优势不够清楚。
- Bismuth：视觉上比早期碎片结果更统一，但更像方块矿物/建筑块，不像高质量铋晶体；可以作为诊断或补充。
- Sci-fi：材质和硬表面感较好，但结构语义仍不够明确，适合作为支线候选，不适合当前头图。

## 指标结果的关键解释

直接对导出的 GLB 做 vertex-only occupancy proxy 会显示大量组件，这是误导性的，因为 Trellis2 texture/postprocess 的 GLB 顶点、UV 和 face islands 会导致 raw face / vertex metrics 爆炸。

因此又跑了 `mesh_connectivity_repair_20260509.py` 的 surface/edge/centroid occupancy QA：

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/cache_selected_texture_repair_zh_20260509.md`

更稳的诊断结果：

- DLA 和 radial 在 surface occupancy 口径下已经是 `component_count=1`, `LCR=1.0`，因此没有 metric improvement 空间；但视觉仍块状，不足以作为主结果。
- Bismuth 从 `4 comps / LCR 0.751` 通过 `bridge_to_largest` 可变成 `1 comp / LCR 1.0`，几何保留率接近 1；这是一个可用的修复诊断，但桥接会引入细桥，不应自动用于美术图。
- Sci-fi 从 `3 comps / LCR 0.998` 通过 `bridge_to_largest` 可变成 `1 comp / LCR 1.0`，保留率较高；可作为工程修复候选。

## 论文使用建议

这批结果不应作为主文正例。它最适合写成以下用途：

1. **Cache / repair 支线诊断**：cache / voxel fusion 可以让非树 mesh 进入真实 Trellis2 texture path，但视觉和拓扑口径仍需严格 QA。
2. **Negative boundary**：Trellis2 texture export 成功不等于拓扑 clean，也不等于 DLA/crystal 线已经解决。
3. **补充材料候选**：如果需要展示探索过 cache-selected 非树资产，可放 supplement，并明确“不作为主贡献图”。

当前不建议写的 claim：

- 不要说 DLA / bismuth / sci-fi 已经解决碎块问题。
- 不要说 GLB raw face components 能直接代表真实结构连通性。
- 不要说 `bridge_to_largest` 是默认美术修复方法，它更像诊断和工程兜底。

当前可写的 claim：

- Cache-selected meshes can be exported through the real Trellis2 texture/PBR path.
- Mesh-level QA must separate surface-occupancy connectedness from raw GLB face/UV fragmentation.
- Non-tree recursive assets remain the main open visual-quality bottleneck; bismuth/sci-fi have repair candidates, but not yet main-paper-level visuals.
