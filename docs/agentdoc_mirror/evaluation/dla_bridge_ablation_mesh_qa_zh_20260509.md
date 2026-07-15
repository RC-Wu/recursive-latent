# DLA Bridge-Aware Mesh QA 2026-05-09

本文件记录 `dla_bridge_ablation_20260509` 的 mesh-only QA。该批次的目的不是生成最终图，而是检查“对碎块 DLA 做后处理桥接”能否解决用户指出的不可用碎片问题。

## 1. 输入与输出

- 远端结果：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/dla_bridge_ablation_20260509`
- 本地镜像：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/dla_bridge_ablation_20260509`
- QA 渲染：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/dla_bridge_ablation_20260509/renders`
- 合成图：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/dla_bridge_ablation_mesh_qa_20260509.png`

所有 QA 图都是 Blender mesh renders，不是 point cloud / matplotlib scatter。

## 2. 指标结果

| case | method | face comps | face LCR | occ comps | occ LCR | 结论 |
|---|---:|---:|---:|---:|---:|---|
| hard DLA | raw | 5 | 0.301 | 4 | 0.387 | 明显碎块 |
| hard DLA | raw bridge smooth | 1 | 1.000 | 6 | 0.670 | 面连通但 occupancy 仍碎 |
| hard DLA | sparse close bridge | 3 | 0.931 | 4 | 0.738 | 指标改善但视觉桥接很假 |
| hard DLA | mesh bridge smooth | 3 | 0.916 | 6 | 0.615 | 仍不可用 |
| volumetric DLA | raw | 8 | 0.447 | 8 | 0.408 | 主体较自然但碎 |
| volumetric DLA | raw bridge smooth | 2 | 0.984 | 9 | 0.416 | face 变好但 occupancy 没好 |
| volumetric DLA | mesh bridge smooth | 1 | 1.000 | 4 | 0.961 | 当前最好，但仍非单连通 |
| volumetric DLA | sparse close bridge | 4 | 0.935 | 5 | 0.482 | 过闭合/桥接痕迹明显 |

## 3. 视觉判断

- `hard_dla` 原始结果是完全不可接受的碎块。
- `hard_dla` 的 sparse/mesh bridge 版本虽然把若干块连接起来，但形成了很明显的细杆和三角拉线，视觉上像后处理缝合，不像自然生成的资产。
- `volumetric_dla + mesh_bridge_smooth` 是半正例：主体有更连续的体积感，occupancy LCR 达到 0.961，但仍有 4 个 occupancy component，且桥线人工痕迹明显。
- 这一批不能作为“DLA 已解决”的正例。它更适合作为消融/负例，说明 post-hoc bridge 不足以替代 grammar-native connected support。

## 4. 对论文 claim 的影响

可以写：

- 后处理 bridge 可以改善部分 face-level 或 LCR 指标，但不能可靠恢复可用 asset。
- DLA/coral 需要在 grammar proposal 阶段保持 connected support，而不是在 decoder 后用长桥线连接碎块。
- 该结果支持 PS-RSLG 中 connected-support invariant 和 projection-inside-recursion 的必要性。

不能写：

- 不能写 DLA/frontier growth 已经被解决。
- 不能把 `face_component_count=1` 当作连通性证明，因为 occupancy components 仍可大于 1。
- 不能把 bridge 后的视觉结果放入主图正例；除非后续 connected scaffold 或 true frontier grammar 版本通过 zoom QA。

## 5. 后续动作

已转向新的 `connected_coral_depth_cases_20260509`：

- 先用 grammar-native connected scaffold 生成 volumetric coral/DLA-like depth stages；
- 再走 Trellis2 texture/PBR；
- 若该路线视觉和 metrics 过关，作为非树递归展示候选；
- 该路线仍只应称为 coral/DLA-inspired connected scaffold，而非真实 DLA 物理过程。
