# 非树状递归资产扩展计划与视觉矩阵复核

日期：2026-05-08  
范围：仅基于本地已有文档与视觉目录复核，不启动 Blender，不使用 SSH 或远程资源。  
输出目标：把当前“树/藤/DLA”结果扩展成更有说服力的非树状递归资产集合，并明确头图、30+ 结果矩阵和降级素材。

## 0. 本地证据入口

已复核的本地计划：

- `/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_texture_visuals_plan_20260508.md`

重点视觉目录：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/matrix_test_one/`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/textured_glb_previews_20260508/`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/textured_glb_previews_steps8_20260508/`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/non_tree_recursive_20260508/`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/contact_sheets/`

当前硬判断：

- `vine_d5_compete` 是唯一接近头图主视觉强度的已有结果，尤其是 textured GLB 版本。
- `tree_compete` 可用于论文叙事，但本任务要求扩展非树状资产，因此树只能作为参照/对照，不能继续占据矩阵主体。
- DLA/porous 已稳定但视觉块状感强，应从“头图主类”降为“压力测试/失败边界”。
- `tree_portal` 目前更像树的 operator 变体，不足以代表独立的 architectural/portal 类别。
- `non_tree_recursive_20260508` 已经出现 crown、snow arch、scifi module 等方向，但当前本地可见产物很少，需要作为下一轮非树扩展的种子，而不是立即替代成熟的 vine 结果。

## 1. 非树状类别扩展矩阵

目标不是找 8 个名称，而是让每一类在形态语义、根源输入和递归 operator 上都能区分。每类至少产出 3-4 个矩阵 tile；头图只选其中 4 个最稳类别。

| 类别 | 形态目标 | 本地 root-source 候选 | 推荐 grammar/operator | 进入头图条件 | 进入 30+ 矩阵方式 |
|---|---|---|---|---|---|
| 1. 藤蔓/根须/tendril | 长条卷曲、悬垂、可见递归层级 | `trellis_example_inputs_subset_20260507/04_...webp`；`siga_night_20260508/root_quality_sweep/root_quality_steps12_contact_sheet.png`；已有 `vine_d5_projected_compete` | `compete` 为主；`fork_side` 作表现力变体；`portal/radial4` 作对照 | 必进头图，优先使用 `textured_glb_previews_steps8_20260508/vine_d5_compete_s5_steps8_tex2048_iso.png` 或 Cycles preserved material render | 一整行可保留：d3/d5、compete/fork_side、projected/pruned、textured/neutral |
| 2. 海草/水草/触手簇 | 与藤蔓相近但更扁平、流体、径向散开 | `trellis_example_inputs_subset_20260507/33_...webp`；`vine_projected_fork_side_s3`；`vine_d5_fork_side_s5` | `fork_side`、`radial4`、`echo`；投影后保留 1-3 个大连通块 | 若 textured GLB 不碎裂，可作为头图第二有机类；否则留矩阵 | 3-4 tile：fork_side d3/d5、radial4、echo，展示“同一根源不同有机展开” |
| 3. 多孔珊瑚/porous aggregate | 孔洞、团簇、空间填充，但不能像方块噪声 | `dla_cluster_points.png`；`textured_glb_previews_20260508/dla_compete_s3_iso.png`；`siga_night_20260508/smoothing/dla_compete_fork_d4_pruned/` | `compete`、`compete_fork`、`radial`；必要时用 smoothing 版本 | 暂不进头图，除非 smoothed DLA 明显像珊瑚而不是 voxel cube | 矩阵中作为压力测试行：raw/projected/smoothed/texture 四种状态 |
| 4. 晶簇/矿物/crystal | 硬边、放射、层级重复、非植物 | `non_tree_recursive_20260508/crown_radial_projected_radial4/`；`siga_night_20260508/selected_meshes/transform_radial4_d3.obj`；可从 DLA radial 派生 | `radial4`、`scale_down`、`compete`；需要更强法向/材质区分 | 只有在径向结构清晰且不被误读为树冠时进头图 | 矩阵 3 tile：radial4、scale_down、compete_fork，强调 hard-surface/mineral 语义 |
| 5. 冠状/花环/crown ornament | 中心对称、环形、花冠、可用于 method tease | `non_tree_recursive_20260508/crown_radial_projected_portal/`；`non_tree_recursive_20260508/crown_radial_projected_radial4/` | `portal`、`radial4`、`echo`；深度 3 优先，避免过碎 | 可竞争头图第 4 类，比 tree_portal 更符合非树要求 | 矩阵 4 tile：portal/radial4/echo/scale_down，作为 ornamental category |
| 6. 冰雪拱/arch/snow formation | 拱形、桥接、自然但非植物 | `non_tree_recursive_20260508/snow_arch_projected_portal/`；`object_like_conditions_20260507_1842/object_like_conditions_contact_sheet.png` | `portal`、`translate`、`scale_down`；需要 projection 防止桥断裂 | 如果本地 mesh 可渲染且轮廓明确，应替换现有 head figure 的 porous 或 tree_portal | 矩阵 3 tile：portal arch、translate arch、scale-down arch，展示非植物结构控制 |
| 7. 科幻模块/greeble/module | 重复模块、硬表面、机械块，不靠植物先验 | `non_tree_recursive_20260508/scifi_module_projected_translate/`；`trellis_example_inputs_subset_20260507` 中硬表面 webp 候选；`transform_portal_d3.obj` | `translate`、`portal`、`radial4`；投影阈值要偏严，控制漂浮碎片 | 头图候选，但前提是形体不再像树叶/灌木 | 矩阵 4 tile：translate、portal、radial4、compete，展示 operator 泛化到非有机资产 |
| 8. 门廊/portal/architectural copy | 拱门、框架、层级复制，强调空间递归 | `siga_night_20260508/selected_meshes/transform_portal_d3.obj`；`tree_portal_s3` 仅作备选；`non_tree_recursive_20260508/snow_arch_projected_portal/` | `portal` 为主；`translate` 与 `scale_down` 辅助；不建议 `fork_side` | 如果能脱离“树状叶片”语义，应进入头图第 4 格 | 矩阵 4 tile：transform portal、snow arch portal、vine portal 对照、tree portal 对照 |
| 9. 网格/格架/lattice/web | 交错、悬空、稀疏骨架，介于建筑和有机之间 | `siga_night_20260508/contact_sheets/lattice_root_direct_gpu6_0615_sheet.png`；`trellis_example_inputs_subset_20260507/33_...webp` | `compete`、`portal`、`translate`；需要 component pruning | 不建议头图，容易碎；适合展示 breadth | 矩阵 3 tile：lattice compete、lattice portal、lattice translate/scale |
| 10. 壳体/旋涡/shell spiral | 卷曲但非藤，强调螺旋和壳状表面 | 当前无强本地 root；可从 vine curl 与 crown radial 中筛选近似源 | `scale_down`、`radial4`、`echo`；低深度，避免变回藤须 | 当前不进头图 | 作为下一轮 root-source 扩展目标，矩阵预留 2-3 个 slot |

优先级排序：

1. 先保住 `vine/root`，这是唯一可直接承担论文封面强度的类别。
2. 立刻补强 `crown/ornament`、`snow arch/portal`、`scifi module`，它们是最明确的非树方向。
3. 将 `porous/DLA` 改成 stress-test，不再让它承担“漂亮结果”的职责。
4. `tree` 只保留少量对照 tile，用来说明原始四类计划的继承，不作为本任务主体。

## 2. Root-source 候选与取舍

### A. 可立即使用的成熟 root-source

- `trellis_example_inputs_subset_20260507/04_130c2b18f1651a70f8aa15b2c99f8dba29bb943044d92871f9223bd3e989e8b1.webp`  
  用于 vine/root/tendril。当前最强，不应动摇。
- `trellis_example_inputs_subset_20260507/33_7d6f4da4eafcc60243daf6ed210853df394a8bad7e701cadf551e21abcc77869.webp`  
  用于 lattice vine / seaweed / web 类别。
- `visuals/dla_cluster_points.png`  
  用于 porous stress-test，不建议作为正面主视觉。
- `visuals/non_tree_recursive_20260508/roots/trellis2_dinov3_min_preview.png`  
  用于检查 non-tree pipeline 的根源质量，但当前只有单张 preview，不能支撑全部类别。

### B. 已有 mesh/source 但需要重新定位的候选

- `siga_night_20260508/selected_meshes/transform_portal_d3.obj`：应归入 portal/architectural，而不是 tree。
- `siga_night_20260508/selected_meshes/transform_radial4_d3.obj`：应归入 crystal/crown，而不是笼统 transform。
- `non_tree_recursive_20260508/crown_radial_projected_radial4/`：最值得优先复核为 crown/crystal。
- `non_tree_recursive_20260508/snow_arch_projected_portal/`：最值得替换现有 head figure 的弱 porous/tree_portal 位。
- `non_tree_recursive_20260508/scifi_module_projected_translate/`：用于证明非有机、非植物、非树。

### C. 只能作为负例或 appendix 的 root-source

- 早期 handcrafted/zero-cond 结果：`trellis2_handcrafted_cond_*`、`trellis2_zero_cond_*`。它们能说明直接图像/点线条件弱，但不能进入主图。
- `object_like_conditions_20260507_1842/object_like_conditions_contact_sheet.png` 可作为“object-like root 尝试”的索引，不作为最终矩阵 tile。
- DLA 原始点图和 blocky textured render 只能作为 stress-test，不能让读者误以为主方法只会生成方块团。

## 3. Grammar/operator 选择

按论文故事，operator 不是随便排列组合，应承担不同视觉论证：

| Operator | 推荐用途 | 风险 | 矩阵中怎么用 |
|---|---|---|---|
| `compete` | 稳定主线，适合 vine、tree-like reference、porous | 视觉保守，容易像已有 root 的自然扩张 | 每类至少 1 个，作为稳定 baseline |
| `fork_side` | 有机分叉、触手、水草、细节丰富 | 碎片多，GLB texture 可能放大碎裂 | 只放 projected/pruned 后的版本；不做头图除非连通性好 |
| `compete_fork` | 稳定性与表现力折中 | 对 tree/DLA 会产生过多组件 | 作为 ablation/expressiveness tile |
| `portal` | arch、crown、architectural、transform-copy | 若 root 是树，会被读成树的姿态变化 | 必须配非树 root；tree_portal 只能备选 |
| `radial4` | crystal、crown、ornament、shell | 可能产生漂浮碎片或像花冠 | 适合非树类别扩展；需要 top/iso 视角 QA |
| `translate` | scifi module、lattice、建筑重复件 | 容易变成简单复制，不显“生长” | 用于非有机泛化，不作为主方法唯一证据 |
| `scale_down` | shell、fractal inset、层级缩放 | 容易塌缩或变小到不可见 | 少量矩阵 tile，配 detail crop |
| `echo` | 轨迹/残影/环绕 | 容易显得杂乱 | 用于 stress-test 和 appendix，不做头图 |

推荐组合：

- 头图：`vine + compete`、`crown/crystal + radial4`、`snow arch/portal + portal`、`scifi module + translate/portal`。
- 30+ 矩阵：每个类别包含一个稳定 `compete` 或 `portal` tile，再放一个表现力 operator 和一个失败边界 operator。
- 消融图：固定同一 root，展示 `raw -> projected -> pruned -> textured/neutral render`，不要和结果矩阵混在一起。

## 4. 头图应进入什么

当前 `head_figure_draft_4cat_20260508.png` 的问题是：第一格 vine 很强，后三格没有形成“四个不同资产类别”的说服力；tree、porous、transform/portal 都还像同一植物/块状系统的变体。

建议头图 4 格：

| 位置 | 资产 | 使用已有视觉 | 说明 |
|---|---|---|---|
| 1 | Textured vine/root | `textured_glb_previews_steps8_20260508/vine_d5_compete_s5_steps8_tex2048_iso.png`；或 `paper_quality_renders_20260508/textured_glb_preview/vine_d5_compete_tex_iso.png` | 主 hero，证明 depth-5、texture、递归生长成立 |
| 2 | Crown/crystal/radial ornament | 优先从 `non_tree_recursive_20260508/crown_radial_projected_radial4/` 和 `transform_radial4_d3.obj` 选择 | 替代纯 tree/bush，展示非树、非藤类别 |
| 3 | Snow arch / portal | `non_tree_recursive_20260508/snow_arch_projected_portal/` 或 `transform_portal_d3.obj` | 展示结构性、建筑性递归，不要再用 tree_portal 冒充 |
| 4 | Scifi module / hard-surface recursive copy | `non_tree_recursive_20260508/scifi_module_projected_translate/` | 证明方法不是植物先验，也不是树状 L-system 变体 |

备用策略：

- 如果 crown/snow/scifi 三类没有可用 render，则保留 `tree_compete_s3_steps8_tex1024_iso.png` 作为 reference，但 caption 中明确是 tree reference，不列入 non-tree breadth。
- Porous/DLA 不建议进入头图。若必须放，只能以“stress-test”小图出现，不能和 vine 等权。

## 5. 30+ 结果矩阵建议

矩阵目标：至少 32 个 tile，其中 24 个以上必须是非树类别；树类最多 4 个 reference tile。

推荐 8 行 x 4 列：

| 行 | 类别 | 4 个 tile |
|---|---|---|
| R1 | Vine/root/tendril | `vine_d5_compete_s5` textured；`vine_d5_fork_side_s5`；`vine_projected_fork_side_s3`；`vine_prune_portal` |
| R2 | Seaweed/tentacle cluster | `vine_prune_radial4`；`vine_prune_echo`；`vine_proj_fork_s3`；`vine_d5_fork_s4/s5` |
| R3 | Crown/ornament | `crown_radial_projected_radial4`；`crown_radial_projected_portal`；`transform_radial4_d3`；`vine_prune_radial4` as fallback |
| R4 | Snow/arch/portal | `snow_arch_projected_portal`；`transform_portal_d3`；`tree_portal_s3` as reference only；`vine_prune_portal` |
| R5 | Scifi/module | `scifi_module_projected_translate`；`transform_portal_d3`；`transform_radial4_d3`；`translate/portal` variant if available |
| R6 | Lattice/web | lattice direct compete；lattice portal；lattice scale/translate；`vine_projected_fork_side_s3` as organic web fallback |
| R7 | Porous/coral stress-test | `dla_compete_s3`；`dla_radial_s3`；`dla_compete_fork_s3`；smoothed DLA compete fork |
| R8 | Tree/reference/demotion row | `tree_compete_s3`；`tree_portal_s3`；`tree_compete_fork_s3`；`tree_fork_s3` |

如果必须维持 4 行 x 8 列，也应这样分配：

- Row 1：有机非树，vine + seaweed + tendril。
- Row 2：ornamental/mineral，crown + crystal + radial。
- Row 3：architectural/hard-surface，snow arch + portal + scifi module + lattice。
- Row 4：stress/reference，DLA + tree + early failures。

每个 tile 的最小标注字段：

- 类别：例如 `crown/ornament`，而不是只写 root 名。
- root-source：具体 webp、OBJ 或本地结果目录。
- operator：`compete`、`fork_side`、`portal`、`radial4`、`translate` 等。
- depth/stage：例如 `d3/s3`、`d5/s5`。
- stabilization：direct、projected、pruned、smoothed。
- material：neutral OBJ render、textured GLB render、preview only。
- 是否进入 paper main：hero、matrix、appendix、demote。

## 6. 现有视觉的降级清单

这些素材不是没用，而是不应占据主图/主矩阵的黄金位置。

| 素材 | 当前问题 | 建议位置 |
|---|---|---|
| `paper_quality_renders_20260508/head_figure_draft_4cat_20260508.png` | 只有 vine 强；tree、porous、transform 三格类别区分弱 | 废弃为 draft，不再作为最终头图 |
| `paper_quality_renders_20260508/blender_tiles/dla_compete_iso.png` | 稳定但块状，像 voxel aggregate，不像高质量资产 | stress-test 或 appendix |
| `textured_glb_previews_20260508/dla_compete_s3_iso.png` | 木纹/棕色 texture 让 DLA 更像方块积木 | texture failure/stress-test |
| `textured_glb_previews_20260508/tree_portal_s3_iso.png` | 漂浮碎片和树叶语义明显，不足以代表 portal/architecture | reference/demotion row |
| `textured_glb_previews_steps8_20260508/tree_portal_s3_steps8_tex1024_iso.png` | 高步数 texture 没解决形体类别问题 | 不进头图，可保留矩阵参考 |
| `paper_quality_renders_20260508/matrix_test_one/vine_prune_radial4_iso.png` | 结构断裂、主体弱 | operator failure 或 appendix |
| `paper_quality_renders_20260508/matrix_test_one/vine_prune_scale_down_iso.png` | 局部碎、层级语义不明显 | appendix，除非重渲染后明显改善 |
| `trellis2_handcrafted_cond_*` 与 `trellis2_zero_cond_*` | 早期条件路径弱，视觉不 paper-ready | 方法动机/负例，不进结果矩阵 |
| `object_like_conditions_20260507_1842/*contact_sheet*` | 更像 root 尝试索引，非最终资产 | appendix/source audit |
| `tree_compete_s1/s2/s3` 全序列 | 有用但树状，不符合本任务“非树扩展”重点 | 最多保留 1-2 个 reference tile |

## 7. 立即可执行的本地复核顺序

不运行 Blender 的前提下，下一位执行者可按以下顺序做资产筛选：

1. 先打开 `non_tree_recursive_20260508/*/latest_mesh.txt`，确认 crown、snow arch、scifi 的 mesh 是否已经本地存在。
2. 对每个 non-tree 候选补一行 metadata：root-source、operator、stage、是否已有 preview/render。
3. 用现有 PNG/contact sheet 先做人工 shortlist，不要先批量渲染。
4. 选定头图四格后，再统一走同一 Cycles/GLB render protocol。
5. 30+ 矩阵先补非树类别空位，最后才用 tree/DLA 填充。

最终判断：

- 论文主视觉应从“树/藤/DLA/portal 四类”改成“藤根、冠状/晶簇、拱/portal、模块/硬表面”四类。
- 结果矩阵应展示 operator 跨形态类别的泛化，而不是同一树/藤 root 的 operator sweep。
- DLA、tree_portal、早期 handcrafted 条件都要保留，但位置从 main visual 降为 stress-test、reference 或 appendix。
