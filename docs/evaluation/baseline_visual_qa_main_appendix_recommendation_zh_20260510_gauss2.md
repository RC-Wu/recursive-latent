# R-SLG baseline 视觉 QA 与主文/appendix 推荐（Gauss2, 2026-05-10）

## 0. 输入证据与取舍原则

本轮只基于本地已完成证据做审稿视角判断，不修改论文、不启动远端任务。重点证据：

- 选择计划：`docs/evaluation/baseline_final_selection_and_generation_plan_zh_20260510_gauss.md`
- seed3 stable pool contact sheet：`visuals/strict_visual_matched_texture_V23_all_family_seed3_stable_pool_zoom_render_target_20260510/V23_seed3_stable_pool_contact_sheet_20260510.png`
- selected-8 render target contact sheet：`visuals/strict_visual_matched_texture_V23_all_family_selected8_zoom_render_target_20260510/strict_visual_matched_texture_V23_all_family_selected8_render_target_contact_sheet_20260510.png`
- traditional baseline one-to-one metrics：`results/baseline_one_to_one_surface_metrics_20260510/surface_metrics_occ64.csv`
- V23 三 seed comparison：`results/strict_visual_matched_texture_V23_all_family_seed3_comparison_20260510.csv`

审稿取舍原则：

1. traditional one-to-one baseline 的 LCR/连通性本身很高，不能把比较写成“baseline 碎、ours 连通”。正确写法是：在相近连通性下，ours 是否更好地保留 recursive growth semantics、局部 contact、family-specific morphology。
2. 主文最小组合必须覆盖 L-system、SC、DLA/frontier、IFS/transform 四个 family；每个 family 只放一个最能防审稿质疑的 case。
3. appendix 可以放稳定但视觉 claim 边界较窄的 case；root-quality 或 texture-naturalization 风险大的 case 不进主文。

## 1. 主文四 family 最小组合

| family | 主文 case | baseline pair | 指标证据 | 视觉 QA | claim boundary | 决策 |
|---|---|---|---|---|---|---|
| L-system | `V23_lsys_pine_canopy_d5_multi_root_smooth_needles` | `lsystem_branch_baseline` | 三 seed；min LCR 0.999703；max components_r0 2 | 分枝束和 needle/leaf-like tips 清楚，局部接触多数可见；仍有 faceted caps、细刺和局部重叠 | 可 claim “grammar-conditioned branching canopy with mostly coherent attachment”；不要 claim botanical realism 或 root-quality | **进主文** |
| Space colonization | `V23_sc_tree_crown_260_attractor_leaf_shell` | `sc_tree_canopy_baseline` | 三 seed；min LCR 0.999372；max components_r0 7 | tree-crown/canopy 语义最对齐；但 zoom 中有截断圆柱、小尖片和拥挤局部，碎片可能被视角放大 | 可 claim “attractor-guided crown-scale topology preserved under generation”；不要 claim fine-scale natural leaf/stem realism | **进主文但标注保守** |
| DLA/frontier | `V23_dla_coral_cluster_900_staghorn_frontier` | `dla_cluster_baseline` | 三 seed；min LCR 1.000000；max components_r0 1 | 连通性最强，frontier/staghorn branching 清楚；但整体偏稀疏、圆柱化，末端 caps 略程序感 | 可 claim “frontier growth remains connected and branch-like”；不要 claim high-density coral surface realism | **进主文第一强证据** |
| IFS/transform | `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges` | `ifs_branch_tree_baseline`；也可连接 pyrite baseline matrix | 三 seed；min LCR 0.999739；max components_r0 4 | lattice/pyrite copy structure 最清楚，overview 有层级和重复结构；zoom 中 bridge/cube-cap 较机械 | 可 claim “transform-copy lattice structure with connected copy bridges”；不要 claim organic smoothness | **进主文，优先于 radial 若要一对一/pyrite 对齐** |

主文最小组合排序建议：

1. `V23_dla_coral_cluster_900_staghorn_frontier`
2. `V23_lsys_pine_canopy_d5_multi_root_smooth_needles`
3. `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges`
4. `V23_sc_tree_crown_260_attractor_leaf_shell`

如果主文只能放 4 张，以上组合最均衡：DLA 和 L-system 提供最稳视觉/指标，IFS lattice 提供可解释 transform 结构，SC tree crown 负责 strict one-to-one 的 SC 语义。`V23_sc_bush_shell_220_attractor_leaf_shell` 指标更稳，但不是 tree-canopy baseline 的最佳一对一配对，因此不替代 tree crown 作为四 family 最小组合。

## 2. 可进 appendix 组合

| family | appendix case | 指标证据 | 视觉 QA | appendix claim boundary | 决策 |
|---|---|---|---|---|---|
| SC | `V23_sc_bush_shell_220_attractor_leaf_shell` | min LCR 0.999801；max components_r0 3；main-stable | bush shell 结构密集、稳定；zoom 中圆柱段和端帽明显，局部像管束 | 可 claim “SC attractor shell produces stable connected bush-like mass”；不作为 strict tree canopy 主证据 | **appendix 强** |
| DLA/frontier | `V23_dla_frontier_sheet_700_open_boundary` | min LCR 1.000000；max components_r0 1；main-stable | open-boundary frontier 有可辨认分叉；但 selected view 里部分枝条稀疏且端帽/尖刺很显眼 | 可 claim “open-boundary frontier remains connected”；不 claim 比 staghorn 更自然 | **appendix 强 / 主文小图备选** |
| DLA/frontier | `V23_dla_crystal_cluster_520_faceted_frontier` | min LCR 1.000000；max components_r0 1；main-stable | faceted crystal/fractal branch 结构清楚；整体偏 toy/synthetic，形态不如 staghorn 丰富 | 可 claim “faceted frontier variant”；不作为 coral/DLA 主正例 | **appendix** |
| IFS/transform | `V23_ifs_radial_ornament_o8_d4_orbit_spokes` | min LCR 0.999888；max components_r0 2；main-stable | radial/orbit symmetry 非常清楚，适合展示 transform copy；但视觉像 ornament，和 traditional branch baseline 一对一较弱 | 可 claim “orbit/radial transform preservation”；不 claim generic IFS branching | **appendix 强 / 若主文强调多样性可替 lattice** |
| IFS/transform | `V23_ifs_branch_ornament_d5_contact_facets` | min LCR 0.999485；max components_r0 3；main-stable | 稳定，但当前 selected contact sheet 未作为核心视觉证据；语义介于 branch 与 ornament | 可 claim “contact-facet transform variant”；不承担主 family claim | **appendix** |
| L-system | `V23_lsys_root_fan_d5_multi_root_smooth_rootlets` | min LCR 0.998854；max components_r0 3；appendix-stable | root fan 语义可用，但缺 selected-8 视觉证据；比 dense rootlets 可能更干净 | 可 claim “root-fan variant exists”；不 claim final root-quality | **appendix / rerun 后可升级** |

## 3. 需要继续 rerun 的 exact case

这些 case 不建议现在进主文，除非远端补生成或补视觉 QA 后明显改善：

| priority | exact case | 当前问题 | rerun 目标 | 是否可先放 appendix |
|---:|---|---|---|---|
| A1 | `V23_lsys_root_fan_d5_dense_rootlets_variant` | selected-8 里 root fan 有大量细根/毛刺、截断端、重叠枝条；虽三 seed 可用，但审稿人容易质疑 root attachment | 增强 root anchor/guide，减少 floating hair-like rootlets，导出近景 QA | 可以 appendix，但不主文 |
| A2 | `V23_sc_root_network_260_attractor_rootlets` | max components_r0 到 13，root-network claim 风险最高；缺 selected-8 主视觉 | 降低小碎片，补 path-to-root / orphan fragment 指标，生成 root close-up | 不建议 appendix 主图，只能作为待补 |
| B1 | `V23_sc_tree_crown_260_attractor_leaf_shell` | 是 SC 主文候选，但 max components_r0 到 7，zoom 中可见截断/尖片/拥挤 | 若时间允许补 2-3 seeds，选一张更少截断、更少 visible fragments 的 render | 当前可主文，但需保守写 |
| B2 | `V23_sc_tree_crown_260_sparse_kill_variant` | 指标近稳，可能比 attractor 更干净，但缺主 contact sheet 核心视觉位置 | 作为 SC backup rerun/render，比较 crown silhouette 与 fragment visibility | appendix/备选 |
| B3 | `V23_dla_coral_cluster_900_lace_porosity_variant` | near-stable；porosity 语义不错但 components_r0 到 7，可能有微碎片 | 做 porosity/frontier sweep，优先保持 LCR 和末端自然度 | 只 appendix，暂不主文 |
| C1 | `V23_ifs_fractal_tree_d5_branch_copy` | 指标 near-stable，但 branch-tree 视觉 claim 弱于 lattice/radial；容易和 baseline branch tree 混淆 | 只有在论文需要 IFS tree 正例时 rerun，目标是更清楚 self-similar branch hierarchy | 暂不放主文 |
| C2 | `V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils` | appendix-stable，但此前 vine strict candidate 有过弱视觉/QA 历史；不适合承担主文 | 若要 vine claim，单独做 vine/root guide sweep | appendix 小图可选 |

最小 rerun 清单：

1. `V23_lsys_root_fan_d5_dense_rootlets_variant`
2. `V23_lsys_root_fan_d5_multi_root_smooth_rootlets`
3. `V23_sc_root_network_260_attractor_rootlets`
4. `V23_sc_tree_crown_260_attractor_leaf_shell`
5. `V23_sc_tree_crown_260_sparse_kill_variant`

可选 rerun 清单：

1. `V23_dla_coral_cluster_900_lace_porosity_variant`
2. `V23_ifs_fractal_tree_d5_branch_copy`
3. `V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils`

## 4. 每个主/appendix 候选的 claim boundary

| case | 可以说 | 不要说 |
|---|---|---|
| `V23_lsys_pine_canopy_d5_multi_root_smooth_needles` | L-system grammar 的分枝方向、分叉层级和局部附着在生成中基本保留 | 不说真实植物针叶/根系精细结构达到自然级 |
| `V23_sc_tree_crown_260_attractor_leaf_shell` | SC attractor-guided tree crown 的整体拓扑和冠层密度可保留 | 不说小尺度叶片、端点、碎片完全无 artifacts |
| `V23_dla_coral_cluster_900_staghorn_frontier` | DLA/frontier 生成在三 seed 下完全连通，branch-frontier 形态稳定 | 不说表面材质/珊瑚孔隙真实，避免过度自然化 |
| `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges` | IFS/transform copy 的 lattice repetition 与桥接接触可见且连通 | 不说形态有机自然；它更像 engineered lattice/pyrite |
| `V23_sc_bush_shell_220_attractor_leaf_shell` | SC shell/bush morphology 稳定 | 不作为 tree canopy 一对一主 claim |
| `V23_dla_frontier_sheet_700_open_boundary` | open-boundary frontier variant 可连通生成 | 不声称比 staghorn 更强或更自然 |
| `V23_dla_crystal_cluster_520_faceted_frontier` | faceted/crystal frontier 变体可连通 | 不作为 DLA coral/staghorn 主例 |
| `V23_ifs_radial_ornament_o8_d4_orbit_spokes` | orbit/radial transform 的结构保存明显 | 不作为 branch-tree baseline 的唯一一对一证据 |
| `V23_lsys_root_fan_d5_dense_rootlets_variant` | 有 root-fan/rootlet 方向的形态探索 | 不 claim root quality 已发表级 |
| `V23_sc_root_network_260_attractor_rootlets` | 可作为待补 root-network case | 不 claim 已通过主文级 visual QA |

## 5. 传统 baseline 一对一比较写法

### 5.1 必须避免的写法

不要写：

- “traditional baseline fragmented while ours is connected”
- “ours uniquely solves connectivity”
- “baseline fails geometrically”

原因：`results/baseline_one_to_one_surface_metrics_20260510/surface_metrics_occ64.csv` 显示 traditional one-to-one baseline 的连通指标也很高：

| baseline | components_r0 | LCR_r0 | 备注 |
|---|---:|---:|---|
| `lsystem_branch_baseline` | 3 | 0.999711 | 几何连通性并不差 |
| `sc_tree_canopy_baseline` | 1 | 1.000000 | 完全连通 |
| `dla_cluster_baseline` | 3 | 0.999840 | 几何连通性很高 |
| `ifs_branch_tree_baseline` | 1 | 1.000000 | 完全连通 |

### 5.2 推荐写法

主文中应把 traditional baseline 定义为“procedural/geometry-only or canonical one-to-one target”，把 ours 定义为“Trellis2-backed, projection-stabilized recursive generation”。比较点不是单纯连通性，而是以下四点：

1. Family-specific structure retention：
   - L-system：branching hierarchy / canopy bundle / recursive grammar cue。
   - SC：attractor-driven crown silhouette / dense local branching。
   - DLA：frontier/staghorn growth and connected branch tips。
   - IFS：copy-transform lattice and contact bridges。

2. Generation-domain relevance：
   - traditional baseline 是可控几何 baseline；
   - ours 是经过生成模型 texture/geometry synthesis 的 output，因此应比较“是否在生成过程中保留规则结构”。

3. Comparable connectivity floor：
   - baseline 和 ours 都报告 components/LCR；
   - 重点展示 ours 在高 LCR 下没有丢掉 family morphology，而不是说 baseline 低 LCR。

4. Visual QA boundary：
   - 对每个 ours 主文 case 标注存在的 artifacts：端帽、截断、小尖片、局部重叠；
   - 声明这些 artifacts 不影响本 claim 的 family-level topology，但限制 fine-scale realism claim。

### 5.3 可直接放进论文/response 的措辞草案

> The one-to-one procedural baselines are not intended as weak connectivity baselines; several are already nearly fully connected under our occupancy metric. We therefore use them as controlled family targets and compare whether the generated R-SLG outputs preserve the family-specific recursive morphology under the same visual-matching protocol. The main claim is preservation of structured growth cues, not a blanket improvement over procedural geometry in raw connectivity.

中文解释版：

> 传统一对一 baseline 不是“弱连通 baseline”，其中若干样例在 occupancy 连通指标上已经接近满分。因此，主文应把它们作为受控 family target，而不是失败对照；比较重点是 R-SLG 在生成模型输出中是否仍保留 L-system/SC/DLA/IFS 的递归形态线索。

## 6. 最终明确取舍

主文四 family 最小组合：

1. `V23_lsys_pine_canopy_d5_multi_root_smooth_needles`
2. `V23_sc_tree_crown_260_attractor_leaf_shell`
3. `V23_dla_coral_cluster_900_staghorn_frontier`
4. `V23_ifs_fractal_lattice_d4_pyrite_copy_bridges`

主文可替换项：

- 若 IFS 想强调视觉多样性而非 pyrite 一对一，替换为 `V23_ifs_radial_ornament_o8_d4_orbit_spokes`。
- 若 SC tree crown 近景被认为 artifact 太强，暂用 `V23_sc_bush_shell_220_attractor_leaf_shell`，但正文必须承认它不是 tree-canopy baseline 的最严格一对一配对。
- 若 DLA 需要第二张主文小图，加入 `V23_dla_frontier_sheet_700_open_boundary`，但 staghorn 仍是主正例。

appendix 推荐组合：

1. `V23_sc_bush_shell_220_attractor_leaf_shell`
2. `V23_dla_frontier_sheet_700_open_boundary`
3. `V23_dla_crystal_cluster_520_faceted_frontier`
4. `V23_ifs_radial_ornament_o8_d4_orbit_spokes`
5. `V23_ifs_branch_ornament_d5_contact_facets`
6. `V23_lsys_root_fan_d5_multi_root_smooth_rootlets`

不建议当前主文：

1. `V23_lsys_root_fan_d5_dense_rootlets_variant`
2. `V23_sc_root_network_260_attractor_rootlets`
3. `V23_dla_coral_cluster_900_lace_porosity_variant`
4. `V23_ifs_fractal_tree_d5_branch_copy`
5. `V23_lsys_climbing_vine_d6_multi_root_leaf_tendrils`

最需要补的视觉 QA：

1. SC tree crown：确认 zoom 中小碎片/截断端是否会在主文裁图中显眼。
2. L-system root fan：重新渲染 root attachment close-up，当前 dense rootlets 不够稳。
3. IFS lattice：检查 bridges 是否像有效接触而不是机械穿插。
4. DLA staghorn/frontier：检查 branch thickness 与端帽是否在 textured render 中被弱化。
