# 主实验收束状态：corrected V67B 四类传统对比（2026-05-12）

## 当前收束口径

本轮目标从继续扩张远端搜索，切换为收束可写入正文的主实验证据。当前四行一对一传统对比固定为：

1. Space colonization：传统 tree canopy vs ours V32 balanced canopy D。
2. L-system：摆正后的传统 OBJ neutral branch-with-side-branches vs ours V67 tapered dense B textured GLB。
3. DLA/frontier：传统 voxel/block DLA cluster vs ours V8 lace reef coral A。
4. IFS/transform：传统 matched branch-tree vs ours V21 branch-tree natural bark。

这版修正了两个旧问题：

- IFS 行不再放 pyrite。Pyrite 只保留给 transform/lattice/crystal 故事，不作为 branch-tree row 的 ours。
- DLA/frontier 行不再放语义不明对象，改为复杂 coral/frontier case。

## 固定资产路径

- manifest：`results/main_experiment_case_metrics_20260511/main_experiment_traditional_vs_ours_manifest_corrected_V67B_20260512.json`
- 论文 manifest 副本：`paper_siga/figures/main_experiment_traditional_vs_ours_manifest_corrected_V67B_20260512.json`
- 白底 zoom render：`visuals/main_experiment_traditional_vs_ours_white_zoom_corrected_V67B_20260512/`
- 论文矩阵图：`paper_siga/figures/main_experiment_traditional_vs_ours_white_zoom_matrix_corrected_V67B_20260512.png`
- 论文指标表：`paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`
- metrics 输出：`results/main_experiment_case_metrics_20260511/main_experiment_selected_corrected_V67B_metrics_20260512/`

## 视觉 QA 结论

- SC：传统 baseline 是强结构控制，但视觉仍是 tube/cylinder canopy；V32 ours 有更明显叶团和自然外观。正文中应写成视觉自然度和材质/detail 更好，不声称真实植物生长仿真。
- L-system：V67 textured dense B 是当前用户认可的“多尖刺/密度深度基本可用”版本。传统 OBJ 已用 neutral/upright 方式渲染，避免拿歪斜 baseline 当 strawman。V67 的 exact r0 指标被细尖刺和 texture-export 小岛惩罚，但 r1 单连通，正文必须明确 caveat。
- DLA/frontier：V8 lace reef coral A 语义正确，避免传统 DLA block/voxel 感，surface r0/r1 都单连通，是四行里指标和视觉最干净的一行。zoom_02 仍偏端枝，但不影响主 claim：frontier/coral asset 不再体素化。
- IFS/transform：V21 branch-tree natural bark 修正了旧 pyrite 错位问题。它和传统 IFS branch-tree 在语义上对齐；ours 视觉更自然，但当前自动 zoom 偏主干，因此正文不能把它写成完美局部接缝证明，只写 branch-tree row 的 semantic correction 与材质自然化。

## 指标摘要

Surface-sampled voxel occ64：

| Family | Method | C_r0 | LCR_r0 | C_r1 | Faces | Welded comp. |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Space colonization | Traditional | 1 | 1.000 | 1 | 31,700 | 627 |
| Space colonization | Ours | 6 | 0.996 | 1 | 84,062 | 1 |
| L-system | Traditional | 6 | 0.999 | 1 | 20,736 | 508 |
| L-system | Ours V67 | 107 | 0.979 | 1 | 75,528 | 9 |
| DLA/frontier | Traditional | 6 | 1.000 | 1 | 10,800 | 1 |
| DLA/frontier | Ours V8 | 1 | 1.000 | 1 | 42,491 | 1 |
| IFS/transform | Traditional | 1 | 1.000 | 1 | 65,600 | 15 |
| IFS/transform | Ours V21 | 6 | 0.999 | 1 | 19,454 | 1 |

解释边界：

- r0 是 exact surface occupancy；尖刺、薄片、texture export 的微小岛会被严厉计数。
- r1 是一体素 dilation 后的 seam/alias tolerant 连接性；四个 ours 都为单连通。
- welded component 是 tolerance-based mesh diagnostic，不替代 recursive handle validity；handle validity 仍由 projection ablation 和 trace metrics 支撑。

## 正文写作口径

主实验段落应该强调：

1. 传统程序是强结构 baseline，不是 strawman。
2. 我们不是证明“全面打败成熟 procedural system”，而是展示：在相同白底/zoom/metrics 协议下，PS-RSLE 可以把递归结构、generator-native naturalization、texture export 合到一个可执行 finite-depth asset pipeline。
3. 对不同家族的优势不同：
   - SC：自然叶团/局部细节更好；
   - L-system：深度和密度接近传统递归分支，同时不再是纯 tube primitive，但 exact r0 有尖刺小岛 caveat；
   - DLA：从 voxel/block accretion 变成复杂 coral/frontier asset，指标最干净；
   - IFS：纠正为 branch-tree 对齐，pyrite 只作为 transform/lattice operator story。
4. 不做 GPT/user study claim；不声称 physical DLA、真实植物生长、watertight topology 或最终 PBR seam 完全解决。

## 当前状态

- 更正版矩阵图和指标表已生成。
- 下一步：局部 patch `paper_siga/main.tex`，把旧 V24/V25 一对一段落替换为 corrected V67B 主实验段落；随后编译并 push Overleaf。
