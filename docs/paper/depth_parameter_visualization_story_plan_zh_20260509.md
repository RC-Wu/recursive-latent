# 同条件 depth / parameter 可视化论文叙事计划与审计

日期：2026-05-09  
项目：Recursive 3D Generative Growth  
范围：SIGA paper / supplement 中 depth、参数、guide 控制可视化的定位、claim 边界、图资产选择、caption 与章节放置建议。  
约束：本文只做写作和图选择计划，不修改 `paper_siga/main.tex`、实验脚本或任何图资产。

## 0. 总体结论

同根、同条件、不同 recursion depth 或控制参数的可视化，应该作为 **method behavior / controllability display / qualitative control evidence** 来呈现，而不是 ablation。它回答的问题是：在固定 grammar family、guide 或 material path、camera、renderer 和 texture schedule 后，递归深度或 grammar 参数是否能以可读方式调制 mesh / textured mesh 的整体组织和局部结构。

这条展示线不能替代 projection ablation。projection ablation 的证据链仍然是 direct recursion、final-only projection、per-depth projection 的 matched comparison；depth / parameter 图只说明方法行为和可控性，不证明某个算法组件因果有效。

建议主文只保留一张紧凑的 same-condition 控制图，优先使用 `paper_siga/figures/depth_parameter_mesh_showcase_zoom_20260509.pdf` 或 `paper_siga/figures/depth_parameter_main_candidate_20260509.pdf`。完整 5 行 gallery、旧密度 sweep、bismuth / pyrite depth、guide sweep 应进入 supplement。

## 1. 论文中的正确角色

### 1.1 支持的 claim

这组图可以支持以下有限 claim：

- Same-condition recursive depth control：固定 family、guide、camera、renderer 后，depth 改变整体组织、分枝尺度、端部细节和局部复杂度。
- Method controllability：grammar 参数或 depth 是可读的控制旋钮，能够改变结构密度、紧凑度或递归丰富化程度。
- Mesh / textured-mesh level display：这些变化发生在可渲染 mesh 或 Trellis2 textured GLB render 上，而不是点云、scatter 或 occupancy debug preview 上。
- Selected projected mesh export compatibility：通过 projection 的部分递归 mesh 可以进入 Trellis2 texture/PBR export 路径，并在固定条件下形成可检查的资产展示。
- Non-tree extension：connected coral / crystal-inspired scaffold 的 depth 展示说明该语言不只适用于 vine / tree 形态。

### 1.2 不支持的 claim

这组图不能支持以下说法：

- 不能说 “depth ablation”、“parameter ablation” 或 “control ablation”。
- 不能说 depth 越大质量越好；只能说 depth 改变组织、尺度和局部细节。
- 不能说参数响应是 calibrated monotonic law；coral density 的视觉和指标只能支持定性可控性。
- 不能说 raw GLB face graph topology clean；raw face components 仍是 texture/export diagnostic caveat。
- 不能说 material recursion consistency 已解决；当前证据只是 selected projected meshes can enter texture/PBR export。
- 不能把 coral、DLA、bismuth、pyrite 写成真实物理生长模拟；应写成 “coral/DLA-inspired connected scaffold”、“bismuth-inspired scaffold”、“pyrite/lattice-inspired family”。
- 不能把 fixed-geometry guide sweep 写成 geometry parameter control；它只展示 material / image guide variation。

## 2. 与 projection ablation 的边界

Projection ablation 的核心图仍应是：

- `paper_siga/figures/projection_ablation_mesh_contact_20260509.png`
- `paper_siga/figures/projection_depth_curves_20260508.pdf`
- `Table~\ref{tab:projection-ablation}` 或其压缩版

这些图比较 direct、final-only、per-depth 三种执行位置，支持 “projection inside recursive transition is necessary for current conservative programs”。

Depth / parameter display 的核心图应放在 texture/export 和 qualitative behavior 之后。它展示同条件控制结果，不参与 “per-depth projection beats final-only cleanup” 的因果论证。正文可用一句桥接：

> After the projection-stability evidence, we use same-condition depth and parameter displays to show how the stabilized recursive programs can be controlled visually; these displays are qualitative behavior evidence rather than ablations.

## 3. 主文图选择

### 3.1 首选主文图：zoom 版 same-condition behavior

推荐资产：

- `paper_siga/figures/depth_parameter_mesh_showcase_zoom_20260509.pdf`
- `paper_siga/figures/depth_parameter_mesh_showcase_zoom_20260509.png`

建议主文角色：Main Figure 7 或 Results 后段的 qualitative controllability figure。

建议保留三行：

| 行 | 内容 | 支持的说法 | 写法边界 |
|---|---|---|---|
| A | Vine / root depth `d=1..4` + local zoom | 同一 vine family 与固定 guide / renderer 下，depth 改变整体递归组织和 terminal detail。 | 不说 depth 提升质量；写成 recursive enrichment / shape reorganization。 |
| B | Connected coral scaffold depth `d=1..4` + local zoom | depth 控制不局限于树/藤蔓；connected scaffold 也能形成逐级复杂化。 | 不说真实 coral 或 DLA 物理过程。 |
| C | Coral density / compactness parameter at fixed stage | 固定 stage、guide、texture schedule、camera 后，参数改变局部密度和紧凑度。 | 只写 qualitative control，不写严格单调响应。 |

如果主文版面紧张，保留 A/B 两行，把 C 移到 supplement；正文仍可用一句引用 supplement 中的 density control。

### 3.2 主文备选图：更紧凑候选

可选资产：

- `paper_siga/figures/depth_parameter_main_candidate_20260509.pdf`
- `paper_siga/figures/depth_parameter_main_candidate_20260509.png`

适用场景：主文只能容纳更干净、更少 inset 的三行图时。它的 caption 必须明确 “not an ablation study”，并说明每行只改变一个 control variable。

### 3.3 不建议主文核心使用的图

- `paper_siga/figures/depth_parameter_mesh_showcase_20260509.pdf`：完整 5 行图信息量过密，更适合 supplement overview。
- `paper_siga/figures/pyrite_depth_textured_showcase_20260509.png`：depth 差异不如 vine / coral 清楚，建议只作 supplement gallery 或边界例。
- `paper_siga/figures/coral_stage4_guide_sweep_20260509.png`：固定 geometry 变 guide，是 material control，不是 depth 或 geometry parameter 控制。
- `paper_siga/figures/coral_density_param_showcase_20260509.png`：旧参数跨度偏小，若有新版 extreme endpoint 图，应降级为 supplement 或不再优先使用。

## 4. Supplement 图选择

### 4.1 完整 same-condition gallery

推荐资产：

- `paper_siga/figures/depth_parameter_mesh_showcase_20260509.pdf`
- `paper_siga/figures/depth_parameter_mesh_showcase_20260509.png`

Supplement 角色：完整 method-control overview。包含 vine depth、bismuth depth、pyrite depth、coral depth、coral guide sweep。

Caption 重点：

- Rows A-D lock family、guide、camera、renderer and vary recursive depth。
- Row E fixes stage-4 coral geometry and changes only image/material guide。
- 该 gallery 是 supplementary method-control evidence，不是 physical growth simulation 或 topology-clean proof。

### 4.2 Coral density endpoint control

推荐资产：

- `paper_siga/figures/coral_density_extreme_texture_20260509.png`
- `paper_siga/figures/coral_density_extreme_texture_20260509.pdf`

该图比旧 `coral_density_param_showcase_20260509.png` 更适合展示参数端点。固定条件包括 connected coral scaffold family、同一 stage、同一 public octopus-sucker material guide、同一 Trellis2 texture schedule、同一 Blender/Cycles camera 和 render protocol。density 端点为 `0.25, 0.45, 1.35, 1.75`。

可支持说法：

- endpoint sweep demonstrates qualitative controllability under fixed guide and render protocol。
- density / compactness 参数改变开放程度、局部拥挤度和 mesh/token budget。
- occupancy-primary support remains connected in the reported endpoint cases。

必须保留 caveat：

- raw GLB face components 很高，不能作为 topology-clean proof。
- 不是物理 DLA 或 coral 生长模拟。
- 不暗示严格单调控制律。

### 4.3 单项 depth / guide 补充

建议 supplement 或 appendix 放：

- `paper_siga/figures/vine_depth_textured_strip_20260509_vizworker.png`：最清楚的 vine depth progression，可作为主文 A 行的展开。
- `paper_siga/figures/coral_depth_textured_showcase_20260509.png`：connected coral depth 的完整 textured sequence，强调 grammar-native connected scaffold。
- `paper_siga/figures/bismuth_depth_textured_showcase_20260509.png`：非树、晶体启发 scaffold depth 的强补充，但 caption 要避免 physical bismuth growth。
- `paper_siga/figures/crystal_stage4_guide_sweep_20260509.png` 或 `paper_siga/figures/coral_stage4_guide_sweep_20260509.png`：只放 material/image guide control appendix。

## 5. 建议章节放置

### 5.1 主文 Results 顺序

建议 Results 中的逻辑顺序：

1. Claim-aligned metrics：先说明 occupancy-primary metric、raw mesh diagnostics、raw GLB face caveat。
2. Projection ablation：direct / final-only / per-depth 的核心因果证据。
3. Texture/export compatibility：selected projected meshes can enter Trellis2 textured GLB export。
4. Same-condition controllability：depth / density / guide behavior display。
5. Boundary cases：fork、radial、DLA bridge、pyrite dense cases 等作为 stress / boundary，不包装成成功正例。

Depth / parameter 图应放在第 4 部分。不要提前放在 projection ablation 前，否则 reviewer 容易把它读成 “visual ablation without metrics”。

### 5.2 主文小节标题建议

可选标题：

- `Same-condition depth and parameter control`
- `Qualitative controllability under fixed rendering conditions`
- `Method behavior across depth and grammar parameters`

不建议标题：

- `Depth ablation`
- `Parameter ablation`
- `Control ablation`
- `Ablation on recursive depth`

## 6. Caption 草案

### 6.1 主文 zoom 版 caption

> Same-condition method-behavior visualization with local zooms. Each row changes one control variable while keeping the grammar family, material/image guide, camera, and renderer fixed. The vine and connected-coral rows vary recursive depth and show finite-depth recursive enrichment; the coral row varies a density/compactness parameter at a fixed stage. All panels are mesh or textured-mesh Blender renders. The figure illustrates controllability of the recursive program and is not an ablation study; the parameter row is qualitative control evidence rather than a calibrated monotonic response.

更短版本：

> Same-condition method-behavior cases. Each row varies one control while locking the family, guide, camera, and renderer. Depth rows visualize recursive enrichment; the density row visualizes fixed-stage parameter control. These textured mesh renders are qualitative controllability evidence, not an ablation.

### 6.2 Coral density endpoint caption

> Same-condition density-parameter control for a connected coral/DLA-inspired scaffold. The grammar family, recursion stage, public material guide, Trellis2 texture schedule, renderer, and camera are fixed; only the density parameter changes. The endpoint sweep shows qualitative changes in local branching density and compactness while retaining occupancy-primary connected support. It is a method-behavior visualization rather than an ablation or calibrated monotonic control law.

### 6.3 Supplement full gallery caption

> Same-condition depth and guide-control gallery using textured mesh or Blender mesh renders only. Rows A-D lock the generator family, guide, camera, and renderer while varying recursive depth. Row E fixes the stage-4 coral geometry and changes only the image/material guide. The gallery is supplementary method-control evidence and should not be read as a physical growth simulation, topology-clean GLB proof, or method ablation.

### 6.4 Coral guide sweep caption

> Fixed-geometry material guide sweep for the connected coral scaffold. All panels use the same stage-4 projected geometry, Trellis2 texture schedule, camera, and renderer; only the public image/material guide changes. This figure shows appearance-guide compatibility, not geometry control or recursive-depth behavior.

## 7. 正文句子建议

可放在 Results 的 controllability 段落：

> Same-condition displays are used to show method behavior rather than to prove a causal ablation. Within each row, we fix the grammar family, appearance guide, camera, renderer, and texture schedule, then vary only recursive depth or a grammar parameter. The resulting mesh and textured-mesh renders show that finite-depth recursive programs expose readable controls over global organization and local detail.

关于 coral density：

> The density endpoint sweep is qualitative: it shows visible changes in compactness and local branching under a fixed guide and render protocol, but it is not a calibrated monotonic law and is evaluated separately from raw GLB face-connectivity diagnostics.

关于 non-tree depth：

> The connected coral and crystal-inspired rows are scaffold cases, not physical growth simulations. Their role is to show that the same recursive sparse-latent execution can be inspected beyond vine/tree-like branching.

关于 guide sweep：

> Guide sweeps are reported only as appearance-control displays on fixed projected geometry; they are not geometry ablations.

## 8. Figure-to-claim 审计表

| 图资产 | 建议位置 | 支持 claim | 禁止叫法 / caveat |
|---|---|---|---|
| `depth_parameter_mesh_showcase_zoom_20260509.pdf` | 主文首选 | same-condition method behavior；depth 和 density 控制；local zoom 细节 | 不能叫 ablation；density 不是严格单调律 |
| `depth_parameter_main_candidate_20260509.pdf` | 主文备选 | 紧凑展示 depth / parameter row | 无 zoom 时局部证据较弱；caption 要降级 |
| `vine_depth_textured_strip_20260509_vizworker.png` | 主文替代或 supplement | vine depth progression；selected textured recursive asset | 不是 texture recursion consistency proof |
| `coral_depth_textured_showcase_20260509.png` | 主文支撑或 supplement | connected coral scaffold depth behavior | 不是真实 DLA / coral 物理模拟；stage 1 tiny island caveat 需保留 |
| `coral_density_extreme_texture_20260509.png` | supplement 强候选；主文 C 行素材 | fixed-stage density endpoint control | 不是 ablation；不是 calibrated monotonic law；raw GLB face caveat |
| `depth_parameter_mesh_showcase_20260509.pdf` | supplement overview | 多 family depth / guide control 总览 | 过密，不宜作主文核心证据 |
| `bismuth_depth_textured_showcase_20260509.png` | supplement 强候选 | non-tree crystal-inspired scaffold depth | 不说 physical bismuth growth |
| `pyrite_depth_textured_showcase_20260509.png` | supplement gallery / 边界例 | lattice-inspired family can be rendered | 不建议作为主文质量代表 |
| `coral_stage4_guide_sweep_20260509.png` | supplement material-control appendix | fixed geometry, varied material/image guide | 不能叫 geometry control 或 parameter ablation |
| `vine_stage5_guide_sweep_20260509.png` | 主文 texture/export 或 supplement | same projected stage-5 mesh, varied public guide | guide sweep，不是 ablation；raw GLB face caveat |

## 9. 最终推荐组合

主文最稳组合：

1. `paper_siga/figures/depth_parameter_mesh_showcase_zoom_20260509.pdf`
   - 使用 A/B/C 三行；若版面紧张，保留 A/B，C 转 supplement。
2. 在正文中把它放在 texture/export compatibility 之后，projection ablation 之后。
3. Caption 使用 “same-condition method-behavior” 和 “qualitative controllability evidence”，显式写 “not an ablation”。

Supplement 最稳组合：

1. `paper_siga/figures/depth_parameter_mesh_showcase_20260509.pdf`
   - 完整 5 行 overview。
2. `paper_siga/figures/coral_density_extreme_texture_20260509.png`
   - 新 endpoint density control。
3. `paper_siga/figures/vine_depth_textured_strip_20260509_vizworker.png`
   - vine depth 展开。
4. `paper_siga/figures/coral_depth_textured_showcase_20260509.png`
   - connected coral scaffold depth 展开。
5. `paper_siga/figures/bismuth_depth_textured_showcase_20260509.png`
   - 非树 depth 补充。
6. `paper_siga/figures/coral_stage4_guide_sweep_20260509.png`
   - material guide control appendix。

一句话写作纪律：

> Same-condition depth and parameter figures are controllability displays for stabilized recursive programs; projection ablation remains the only ablation story, and texture/guide sweeps remain selected export or appearance-control evidence.
