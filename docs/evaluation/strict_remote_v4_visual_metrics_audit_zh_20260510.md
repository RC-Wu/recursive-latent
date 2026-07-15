# V4 严格一对一远端生成：视觉与指标审计（2026-05-10 08:30）

## 结论先行

V4 确认了一件重要事情：**在 a100-2 远端重新生成，而不是本地挑选/后处理的前提下，连接性可以基本做稳**。seed `20260510` 的 12 个 Trellis2 textured GLB 中，10 个在 occ64 surface metric 上是严格 `components_r0=1`，另外 `pyrite` 与 `SC root` 仅有极小附属组件，LCR 分别约 `0.99982` 和 `0.99995`；所有 case 在 r1/r2 膨胀后均为单组件。

但 V4 也暴露了新的视觉问题：**全局 continuous implicit naturalization 会把植物、根系、DLA/coral 的递归结构抹成块状团块**。因此 V4 不能作为最终主文植物/根/珊瑚结果，只能作为“连通性修复成功、但递归结构可读性下降”的关键 ablation/反例。下一步 V5 必须转成 hybrid：保留可读 branch/leaf/coral/radial primitive，只在 attachment、connector、bridge、spine 上做必要融合。

## 路径

- V4 seed `20260510` GLB：`visuals/strict_visual_matched_texture_v4_20260510`
- V4 seed `20260510` 指标：`results/strict_visual_matched_texture_v4_20260510_remote/surface_metrics_occ64.csv`
- V4 seed `20260510` 白底 zoom sheet：`visuals/strict_visual_matched_texture_v4_zoom_20260510/strict_visual_matched_texture_v4_contact_sheet_20260510.png`
- V4 seed `20260511` GLB：`visuals/strict_visual_matched_texture_v4_seed20260511_20260510`
- V4 seed `20260511` 指标：`results/strict_visual_matched_texture_v4_seed20260511_20260510_remote/surface_metrics_occ64.csv`
- V4 seed `20260511` 白底 zoom sheet：`visuals/strict_visual_matched_texture_v4_seed20260511_zoom_20260510/strict_visual_matched_texture_v4_seed20260511_contact_sheet_20260510.png`

## V4 算法相对 V3/V3b 的变化

V3 的问题是局部视觉元素更丰富，但 tree/root/SC/radial 等 case 有大量独立 primitive，严格 r0 component 不稳。

V3b 的问题是 connected occupancy scaffold 让指标非常稳，但结果明显体素块状，很多 case 看起来像 voxel sculpture。

V4 尝试中间路线：

- L-system / SC：用 continuous implicit trunk/branch/root occupancy 代替 disconnected cards。
- DLA/frontier：用 connected DLA support + smooth implicit surface + bump/faceting。
- IFS/radial/lattice：用 ring/spine/bridge/cache 保留 transform orbit，同时降低碎片。

指标上 V4 基本达到目标；视觉上，global implicit 的副作用仍很强。

## 视觉审计

### 可继续作为主文候选或强候选

- `v4_ifs_fractal_lattice_d4_connected_pyrite`：pyrite/lattice 结构清楚，PBR 质量可接受，递归/对称/晶格语义较强。缺点是仍有少量近似体素/块状感，但这对晶体类是可接受的。
- `v4_ifs_radial_ornament_o8_d4_bridged_gear`：径向结构比 V3/V3b 更连贯，8-fold/ring 语义可读，适合作为 transform/等变性/对称性 case。缺点是局部 zoom 下纹理不稳定，几何有细杆断裂感。
- `v4_dla_aniso_crystal_connected_implicit`：比 coral 更像矿物/晶体，可作为 DLA frontier -> faceted mineral 的边界候选。缺点是仍像有机块状矿物，而不是明确的 anisotropic DLA crystal。

### 指标好但视觉不够主文

- `v4_lsys_pine_canopy_d5_continuous_conifer`：连通性好，但不像松树冠，更像绿色连续叶片/海藻状团块。递归 whorl 和针叶被 implicit 抹平。
- `v4_lsys_root_fan_d5_continuous_hierarchy`：连通性好，但根系分叉层级不清楚，像黑色根团/岩团。可以作为 negative ablation。
- `v4_sc_tree_crown_continuous_leaf`、`v4_sc_bush_shell_continuous_leaf`：比 V3b 少一些纯体素块，但仍像块状叶团；可以证明空间竞争 support 可连通，但不是最终视觉。
- `v4_sc_root_network_continuous_root`：连通性和体量不错，但 root path 和分叉不清楚，被自然化成根团。
- `v4_lsys_climbing_vine_d6_connected_leaf_shell`：几何细长结构保留一些，但叶/藤语义弱，纹理单一。

### 仍需替换

- `v4_dla_coral_cluster_connected_implicit`、`v4_dla_frontier_sheet_connected_implicit`：连通性解决了，但仍是红色团块，不是珊瑚/reef/frontier sheet。DLA 线需要 V5/V6 使用 tube/branch coral primitive + local masked naturalization，而不是全局隐式 blob。

## 指标摘要

V4 seed `20260510`：

- `single_r0 = 10/12`
- `min_lcr_r0 ~= 0.99982`
- `avg_box_dim_32_96 ~= 1.904`
- `r1/r2 = 12/12 single`

V4 seed `20260511`：

- `single_r0 = 10/12`
- `min_lcr_r0 ~= 0.99982`
- `avg_box_dim_32_96 ~= 1.905`
- `r1/r2 = 12/12 single`

这说明 seed 改变主要影响纹理/局部形态，不改变 V4 的根本缺陷：connected implicit support 稳但视觉过块。

## 下一步 V5 的明确要求

1. 植物/根系不能再只依赖 global implicit surface。应使用可见 trunk/branch/root tubes + attached leaf/needle/root-hair primitives，并用 short connector/bridge/spine 保证 surface voxel 连通。
2. DLA/coral 要从“红色 blob”改成 branch/tube coral。保留 DLA/frontier parent graph，用 tube radius schedule 和 local pore/bump，而不是把所有 frontier 点做高斯场融合。
3. IFS/radial/pyrite 可以沿 V4 继续，只需微调材质和 zoom 位置。
4. 最终主文比较应该把 V4 作为 ablation：`V3 rich but fragmented -> V4 connected but over-naturalized -> V5 hybrid connected and readable`。
