# Mesh / Textured Mesh Depth-Parameter 展示图 2026-05-09

## 产物

新增合成图：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/depth_parameter_mesh_showcase_20260509.png`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/depth_parameter_mesh_showcase_20260509.pdf`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/depth_parameter_mesh_showcase_20260509.py`

该图只使用本地已有 Trellis2 textured GLB 的 Blender render，没有使用点云、matplotlib scatter、SSH、远端任务或 GPU。未修改 `paper_siga/main.tex`。

## 图面结构

图面共 5 行，每行 4 列，统一浅暖灰背景、白色 panel、同一标签样式，并在每个 panel 右下角加入 front-view inset：

1. `A Vine depth`
   - 来源：`visuals/vine_depth_textured_showcase_20260509/renders/vine_depth{1..4}_{iso,front}.png`
   - 语义：固定 vine family、projection-stabilized recursive loop、Parthenocissus guide、texture schedule、camera / render protocol，只改变 depth。

2. `B Bismuth depth`
   - 来源：`visuals/bismuth_depth_textured_showcase_20260509/renders/stage{01..04}_{iso,front}.png`
   - 语义：非树 connected bismuth-hopper scaffold，在固定 bismuth guide 和同一渲染协议下的 depth 展示。

3. `C Pyrite depth`
   - 来源：`visuals/pyrite_depth_textured_showcase_20260509/renders/stage{01..04}_{iso,front}.png`
   - 语义：晶格 / 对称重复 family 的固定 pyrite guide depth 展示。

4. `D Coral depth`
   - 来源：`visuals/coral_depth_textured_showcase_20260509/renders/stage{01..04}_{iso,front}.png`
   - 语义：grammar-native connected volumetric coral scaffold，在固定 coral guide 下的递归深度展示。

5. `E Coral guide sweep`
   - 来源：`visuals/coral_stage4_guide_sweep_20260509/renders/{octopus,spikyplant,bismuth,pyrite}_{iso,front}.png`
   - 语义：stage-4 coral 几何固定，只改变 Trellis2 material / image guide；这是材质控制展示，不是几何消融。

## 主文候选

优先主文候选：

- `A Vine depth`：最适合放入主文作为同条件 depth 控制的强正例。读者能看到递归阶段变化，且 textured mesh 形式明确，不会被误解为点云结果。
- `D Coral depth`：适合和 vine 搭配，说明方法不只适用于树 / 藤蔓类结构。建议 caption 写成 `connected coral/DLA-inspired scaffold`，不要写真实 coral 或 DLA 物理生长。
- `B Bismuth depth`：可作为主文小图候选或 supplement 强候选。它补充非树、晶体启发结构，但材质偏绿且建筑感强，主文使用时需要谨慎措辞。

主文不优先：

- `C Pyrite depth`：更适合 supplement。stage 2-4 的密度很高，递归深度变化不如 vine / coral 易读；stage 1 有 tiny occupancy island caveat。
- `E Coral guide sweep`：适合 supplement 或附图，证明同一 stage-4 geometry 可以通过 guide 改变外观语义。不能作为 geometry parameter sweep 或 depth 消融。

## 补充材料建议

完整 5 行图更适合作为 supplement 总览图，标题可写：

> Same-condition textured mesh depth and guide controls.

主文若篇幅有限，建议只裁出或重排：

- `A Vine depth`
- `D Coral depth`
- 可选加 `B Bismuth depth`

coral guide sweep 建议单独放 supplement，并在 caption 中明确：

> Geometry is fixed at stage 4; only the image/material guide changes.

## Visual QA 判断

- 合规性：通过。图中所有 panel 均来自本地 existing Blender/Trellis2 textured mesh render；没有点云或 scatter。
- 版式：通过。统一浅底、白色 panel、简短标题、front inset 和低饱和标签，较适合论文或 supplement。
- 可读性：vine 和 coral 最清楚；bismuth 可读但偏建筑 / 矿物资产；pyrite 递归增长存在但 stage 3-4 较密。
- 风险：不能把该图称为 topology-clean mesh proof；应保留 raw GLB face fragmentation / material export caveat。不能把 guide sweep 称为几何参数消融。

