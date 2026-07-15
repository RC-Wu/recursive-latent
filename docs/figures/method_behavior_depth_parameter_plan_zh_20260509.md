# Method Behavior / Depth-Parameter 展示线使用计划（2026-05-09）

## 核心定位

这条展示线应明确写成 **method behavior / controllability / recursive enrichment**，不是 ablation。

推荐叙事是：在同一 grammar family、同一 guide / material path、同一 camera、同一 renderer 条件下，只改变一个控制量，观察有限深度递归程序或 grammar 参数如何改变 textured mesh 的结构与局部细节。它服务于方法可控性和递归丰富化的可视证据，而不是证明某个 depth、参数或 family 更优。

和 `paper_siga/main.tex` 当前实验叙事一致，这组图应放在 texture/PBR export 与 qualitative breadth 之后，用来补充“经过 projection 的递归 mesh 可以进入 Trellis2 textured GLB 路径，并在固定条件下呈现可读的深度/参数响应”。不要把它放到 projection ablation 的证据链里，也不要用它替代 connectedness / LCR / component 表格。

## 推荐图表层级

### 主文优先图

首选：

- `paper_siga/figures/depth_parameter_mesh_showcase_zoom_20260509.pdf`
- `paper_siga/figures/depth_parameter_mesh_showcase_zoom_20260509.png`

理由：它只使用 mesh 或 textured mesh Blender render，三行分别覆盖 vine depth、coral depth、coral density parameter，并带 zoom crop。图面直接表达“同条件只改一个控制量”，也避免把 bismuth / pyrite 的弱行塞进主文核心。

主文建议保留：

1. `A Vine recursive depth`
2. `B Connected coral scaffold depth`
3. `C Coral density parameter`

如果版面紧张，优先保留 A/B，把 C 移到 supplement。C 的价值是回应“不同参数控制”，但视觉差异和指标单调性都弱于 depth 行。

### Supplement 总览图

建议 supplement 放：

- `paper_siga/figures/depth_parameter_mesh_showcase_20260509.pdf`
- `paper_siga/figures/depth_parameter_mesh_showcase_20260509.png`

该 5 行总览覆盖 vine、bismuth、pyrite、coral depth 和 coral guide sweep。它信息完整，但主文过密；B/C/E 行需要较多 caption caveat，放 supplement 更合适。

### 单项补充图

建议 supplement 或 appendix 分别放：

- `paper_siga/figures/vine_depth_textured_strip_20260509_vizworker.png`
  - 用于单独展示最强 vine depth strip。
- `paper_siga/figures/coral_density_param_showcase_20260509.png`
  - 用于密度/紧凑度参数控制的完整指标说明。
- `paper_siga/figures/bismuth_depth_textured_showcase_20260509.png`
  - 用于非树、晶体启发 scaffold 的 depth 补充。
- `paper_siga/figures/pyrite_depth_textured_showcase_20260509.png`
  - 仅建议作为 supplement 弱例或 gallery，不建议主文。

## 逐项视觉可用性评估

| 展示项 | 视觉判断 | 论文位置 | 可支撑说法 | 主要 caveat |
|---|---|---|---|---|
| Vine depth `d=1..4` | 最强主文正例。形态变化清楚，branch / tip zoom 能读出局部递归细节，textured mesh 质量也最容易被接受。 | 主文核心；也可单独作为 depth figure。 | Same-condition recursive depth control；recursive enrichment；mesh-level local detail。 | 不要说 depth 单调提升质量；不同 depth 的姿态变化较大，应写成 shape reorganization / enrichment，而不是同一形状线性增长。 |
| Coral depth `d=1..4` | 主文可用。connected scaffold 的尺度、局部模块数和端部 bead-like 结构随 depth 更丰富，和 vine 形成非树 family 对照。 | 主文核心第二行；完整单图可进 supplement。 | Depth behavior extends beyond vine/tree-like assets；connected scaffold recursion。 | 不要写真实珊瑚物理模拟或严格 DLA；不要把视觉连接等同于 face-welded topology proof。 |
| Coral density `lambda=0.45..1.20` | 可用但较弱。局部紧凑度、遮挡和质量分布有差异，但主视角下变化温和；已有指标不严格单调。 | 主文第三行可选；更稳妥是 supplement。 | Fixed-stage parameter-control case；qualitative controllability under fixed guide/stage。 | 避免 calibrated monotonic response、density strictly increases occupied volume、ablation over parameter quality。 |
| Bismuth depth `d=1..4` | 视觉精致，适合作为非树/晶体启发结构补充；但读起来像建筑/矿物资产，递归深度变化不如 vine 明确。 | Supplement 强候选；主文只有在需要第三个 depth family 时才加入。 | Non-tree connected scaffold depth behavior；crystal-inspired transform/frontier family。 | 不要写 physical bismuth growth；不要把绿色材质变化读成 geometry 控制；主文使用需解释 scaffold 语义。 |
| Pyrite depth `d=1..4` | 不建议主文。整体密度高，stage 2-4 差异被碎块和材质噪声掩盖，读者不容易一眼看出 recursive enrichment。 | Supplement gallery 或负/边界例。 | Lattice/crystal-inspired family can be rendered under fixed conditions。 | 避免强控制性 claim；不要作为方法质量代表；stage 1 tiny island / 高密度碎块 caveat 需要保留。 |
| Coral guide sweep | 不是 depth/geometry parameter 控制。它展示固定 stage-4 geometry 下 material/image guide 改变外观语义。 | Supplement 或 texture-control appendix。 | Same geometry can be textured under different guides。 | 不能叫 geometry sweep、parameter ablation 或 recursive control。 |

## 推荐主文 caption

可直接作为主文 `depth_parameter_mesh_showcase_zoom_20260509` 的 caption 草案：

> Same-condition method-behavior visualization with local zooms. Each row changes one control variable while keeping the grammar family, material/image guide, camera, and renderer fixed. The vine and connected-coral rows vary recursive depth and show finite-depth recursive enrichment; the coral row varies a density/compactness parameter at a fixed stage. All panels are mesh or textured-mesh Blender renders. The figure illustrates controllability of the recursive program and is not an ablation study; the parameter row is qualitative control evidence rather than a calibrated monotonic response.

更短版本：

> Same-condition method-behavior cases. Each row varies one control while locking the family, guide, camera, and renderer. Depth rows visualize recursive enrichment; the density row visualizes fixed-stage parameter control. These textured mesh renders are qualitative controllability evidence, not an ablation.

Supplement 5 行总览 caption 建议：

> Same-condition depth and guide-control gallery using textured mesh or Blender mesh renders only. Rows A-D lock family, guide, camera, and renderer while varying recursive depth. Row E fixes the stage-4 coral geometry and changes only the image/material guide. The gallery is supplementary method-control evidence and should not be read as physical growth simulation or topology-clean mesh proof.

## 需要避免的过度 claim

- 不要写 “ablation study”、“depth ablation”、“parameter ablation”。应写 “method-behavior visualization”、“controllability case display”、“qualitative control evidence”。
- 不要说 depth 越大结果越好。可说 “changes global organization and local detail” 或 “adds finite-depth recursive enrichment”。
- 不要说 coral / bismuth / pyrite 是真实物理生长模拟。应写 “coral/DLA-inspired scaffold”、“bismuth-inspired scaffold”、“pyrite/lattice-inspired family”。
- 不要把 Trellis2 GLB raw face components 当作结构失败的主指标，也不要把 visual connectedness 当作 topology-clean proof。现有正文已经把 occupancy 6-neighborhood proxy 作为 primary connectivity proxy。
- 不要声称 coral density 参数有严格单调几何响应。已有数据中 occupied voxels 和 box-count proxy 不严格单调，视觉差异也偏温和。
- 不要把 coral guide sweep 叫作 geometry control。它只适合写成 fixed geometry 的 material / image guide variation。
- 不要暗示 texture/PBR 递归一致性已经解决。当前证据是 selected projected meshes can enter Trellis2 textured GLB export。

## 后续扩展优先级

### 最值得继续跑的同条件参数

1. **Vine depth 到 `d=5` 或 `d=6` 的同条件 textured mesh**
   - 价值最高。vine 是最强主文视觉线；如果能在同 guide/camera/render 下补 `d=5`，能更自然连接正文 “finite-depth recursive growth”。
   - 需要控制：同 seed、同 guide、同 camera framing、同 texture schedule；最好同时保留 iso/front/detail。

2. **Coral depth 的局部 zoom / 更强局部 crop**
   - 不一定需要新 GPU；优先从现有 `stage04_iso/front` 裁剪更清楚的连接和端部模块。
   - 若要重跑，目标不是更多 depth，而是更清晰的 camera / local detail，用于证明 connected scaffold 的递归丰富化。

3. **Coral density 增加更宽参数端点**
   - 当前 `lambda=0.45..1.20` 差异偏温和。若确实需要主文参数控制，建议试更分离的端点，例如更稀疏、更紧凑各一个，同时固定 stage/guide/camera。
   - 判断标准应是视觉可读性优先，再看 occupancy connectivity；不要只追求指标单调。

4. **一个非树结构的 clean depth family**
   - 如果主文需要第三个 depth family，优先改进 bismuth 而不是 pyrite。bismuth 已经有较强资产感，只需更克制的 caption 和可能更中性的材质/视角。

### 可做但不急的扩展

- **Coral guide sweep 单独做 texture-control appendix**
  - 只在论文需要解释 material guide 路线时使用；它不补强 depth/parameter claim。

- **Bismuth 局部 zoom**
  - 可补 supplement，但主文收益有限。它更像“可扩展 family 覆盖”，不是核心方法证据。

### 不建议继续花 GPU 的方向

- **Pyrite depth 同设置继续加深**
  - 现有 stage 2-4 已经很密，视觉差异不随 depth 清晰增加；继续跑更深大概率只会更碎、更难读。

- **当前 coral density 小步长密集 sweep**
  - `0.45, 0.70, 0.95, 1.20` 已说明温和参数效应。继续补中间值对论文没有明显收益；若跑，应改成少量更分离端点。

- **把 guide sweep 当作 geometry 参数矩阵扩展**
  - 这会混淆 claim。固定 geometry 换 guide 的材料展示可以保留，但不该占用 depth/parameter 控制线的算力。

- **只为了让 pyrite / bismuth 更像真实矿物而重跑**
  - 本文 claim 不是物理矿物生长，也不是真实材料拟真；过度优化这一路线容易偏离 PS-RSLG 的主要贡献。

## 建议最终使用组合

主文最稳组合：

1. `depth_parameter_mesh_showcase_zoom_20260509.pdf`
   - A/B 行作为核心，C 行可保留但 caption 降级。
2. `vine_depth_textured_strip_20260509_vizworker.png`
   - 若需要单独强调最强 depth progression，可替代或补充 A 行。

Supplement 组合：

1. `depth_parameter_mesh_showcase_20260509.pdf`
   - 完整 5 行 gallery。
2. `coral_density_param_showcase_20260509.png`
   - 参数控制 + 指标 caveat。
3. `bismuth_depth_textured_showcase_20260509.png`
   - 非树 connected scaffold 补充。
4. `pyrite_depth_textured_showcase_20260509.png`
   - 仅作为 crystal/lattice-inspired 边界例。

最关键的写作纪律：主文不要把这组图包装成“验证某个算法组件有效”的 ablation；它的正确角色是让读者看到同一个递归程序在固定渲染条件下可以被 depth 和参数以可读方式调制，并且这种调制发生在 mesh/textured-mesh 结果上。
