# Depth / Parameter Showcase 论文使用说明（2026-05-09）

## 定位

这组图应写成 **method behavior showcase / case display**，不是 ablation。核心叙事是：在相同生成家族、guide / material path、camera 与 renderer 条件下，只改变一个控制量，观察递归深度或 grammar 参数对 textured mesh 结果的影响。

所有建议使用的图都来自本地 mesh 或 textured-mesh Blender render；不要混入点云、scatter 或 occupancy 点图。本文档不要求修改 `paper_siga/main.tex`。

## 建议主文图

优先使用新合成候选：

- `paper_siga/figures/depth_parameter_main_candidate_20260509.png`
- `paper_siga/figures/depth_parameter_main_candidate_20260509.pdf`

该候选图只裁剪并组合现有渲染，包含三行：

| 子图 | 内容 | 主 claim | 写法建议 |
|---|---|---|---|
| A | Vine family, depth `d=1..4` | 在同一 vine family 与固定 guide / texture / renderer 下，recursive depth 改变整体分枝尺度、卷曲方式与局部复杂度。 | “same-condition recursive depth control” |
| B | Connected coral scaffold, depth `d=1..4` | depth 控制不局限于藤蔓/树状外观；在 connected coral scaffold 中也能产生逐级扩展的几何复杂度。 | “connected coral scaffold family” 或 “coral/DLA-inspired scaffold”，不要写真实珊瑚物理生长。 |
| C | Coral scaffold density/compactness 参数 `lambda={0.45,0.70,0.95,1.20}` | 固定 stage 与 material guide 后，grammar 参数可以改变局部致密度和分布，但该组当前视觉差异较温和。 | “parameter-control case display”，不要写成强消融或严格单调响应。 |

主文 caption 建议明确：

> Same-condition method behavior cases. Each row changes one control variable while keeping the generator family, material/image guide, camera, and renderer fixed. All panels are textured mesh Blender renders; the figure is not an ablation study.

## 不建议主文直接使用的完整总览

`paper_siga/figures/depth_parameter_mesh_showcase_20260509.png` / `.pdf` 更适合 supplement 总览。它的优点是覆盖范围完整，包含 vine、bismuth、pyrite、coral depth 和 coral guide sweep；缺点是主文版面过密，且 B/C/E 三行需要更多 caption 解释。

若主文篇幅充足，可从完整总览中补充一行 `B Bismuth depth`，用于说明非树、晶体/建筑感 scaffold 也能在固定条件下做 depth 展示。但不建议把 `C Pyrite depth` 放主文核心位置：stage 2-4 视觉密度高，depth 变化不如 vine / coral 清楚。

## Supplement 建议

建议 supplement 放以下材料：

1. `paper_siga/figures/depth_parameter_mesh_showcase_20260509.png`
   - 用途：完整 “same-condition depth and guide control” 总览。
   - 包含：vine depth、bismuth depth、pyrite depth、coral depth、coral guide sweep。
   - caption 重点：E 行是固定 stage-4 coral geometry，只改变 material / image guide，不是 geometry sweep。

2. `paper_siga/figures/coral_density_param_showcase_20260509.png`
   - 用途：参数控制补充图。
   - claim：固定 connected coral grammar family、固定 stage、固定 octopus material guide，只改变 density/compactness 参数。
   - caveat：occupancy connectivity proxy 全部通过，但 occupied voxels 与 box-count proxy 不严格单调，因此更适合定性展示或 supplement。

3. `paper_siga/figures/vine_depth_textured_strip_20260509_vizworker.png`
   - 用途：vine depth 的横向大图版本。
   - claim：在同一 grammar / material 设置下，depth 增加带来形态重排与多尺度分枝变化。
   - 使用场景：如果主文只放一条 depth case，这张比完整 5 行总览更清晰。

4. `paper_siga/figures/vine_zoom_in_multiscale_20260509.png`
   - 用途：mesh 级细节和多尺度结构说明。
   - claim：结果包含可见的 branch-level / terminal-level geometric detail。
   - caveat：不要把它写成 topology-clean mesh proof；它是 textured mesh visual QA 和细节展示。

## 每张现有图对应的 claim

- `depth_parameter_mesh_showcase_20260509.png`
  - Claim：方法能在多个结构 family 上进行同条件 depth / guide 控制展示。
  - 最适合位置：supplement overview。

- `coral_density_param_showcase_20260509.png`
  - Claim：固定 coral family、stage、guide 后，grammar density/compactness 参数能改变结构外观。
  - 最适合位置：supplement 或主文候选图的第三行。

- `vine_depth_textured_strip_20260509_vizworker.png`
  - Claim：vine depth 是最清楚的主文正例，能直观看到 recursive depth 下的形态变化。
  - 最适合位置：主文单独条带或 supplement。

- `vine_zoom_in_multiscale_20260509.png`
  - Claim：递归生成的 textured mesh 支持从 overview 到 terminal detail 的多尺度视觉检查。
  - 最适合位置：补充材料，或主文中作为 zoom-in inset 的素材来源。

## 还缺的 zoom-in crop

如果后续要把主文图做成最终版，建议补三类 crop；目前不需要重新渲染，可先从现有 PNG 或原始 Blender render 中裁剪：

1. Vine depth 的 branch-level crop
   - 来源优先：`vine_zoom_in_multiscale_20260509.png` 的 B panel。
   - 用途：支撑 “branch-level recursion / multi-scale detail”。

2. Vine terminal crop
   - 来源优先：`vine_zoom_in_multiscale_20260509.png` 的 C panel。
   - 用途：展示 terminal tendril / thin appendage detail。

3. Coral stage-4 local crop
   - 来源优先：`depth_parameter_mesh_showcase_20260509.png` 的 `D Coral depth, d=4` panel，或原始 `visuals/coral_depth_textured_showcase_20260509/renders/stage04_iso.png`。
   - 用途：对应主文 B 行，补足 coral scaffold 的局部连接和端部 bead-like detail。

可选 crop：

- Coral density `lambda=0.45` 与 `lambda=1.20` 的局部对比 crop，用于 supplement 说明参数控制差异。但当前参数 sweep 视觉差异不强，不建议放在主文核心位置。
- Bismuth depth 的局部 crop，用于说明 non-tree scaffold 的重复层级，但其外观容易被读成建筑/矿物资产，应放 supplement。

## 视觉判断

主文最稳组合是 `vine depth + coral depth`。这两行差异清楚，且分别覆盖藤蔓类递归形态与 connected scaffold 形态。`coral density` 可以作为第三行保留，用来回应“不同参数控制”的要求，但措辞要弱于 depth 行：它证明参数控制有可见影响，而不是证明参数与某个几何指标严格单调。

新合成候选图 `depth_parameter_main_candidate_20260509.png/.pdf` 可以作为当前 main-paper draft figure。若版面紧张，建议删去第三行参数 sweep，把它移到 supplement；主文只保留 A/B 两行并在正文引用 supplement 中的完整参数控制图。
