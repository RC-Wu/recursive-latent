# strict visual V3 连通性风险与 V3b 修复方案（2026-05-10）

本文只做本地 read-only 审查与 V3b 方案整理，不修改生成脚本、不启动远端任务。依据：

- `assets/strict_visual_matched_cases_v3_20260510.py`
- `results/strict_visual_matched_cases_v3_20260510_dryrun/manifest.csv`
- `docs/evaluation/strict_matched_v3_metric_and_selection_plan_zh_20260510.md`

## 1. 当前结论

V3 strict visual matched 的远端结果仍值得看视觉，但不能直接把本地 dryrun 的 OBJ face/mesh component 当成可用 topology。dryrun 中大量 plant、SC、IFS branch case 是由独立 tube、leaf card、root hair、tip sphere 或 cache piece 拼接而成；这些子几何在视觉上可能贴合、交叠或被 Trellis2/PBR 纹理整合，但 OBJ 顶点并没有焊接，`mesh_component_count` 会非常高，`largest_mesh_component_vertex_ratio` 会极低。

因此 V3 的正确用法是：

1. 远端 V3 先用于判断 strict visual 是否比 V1/V2 更可读：类别、轮廓、递归模式、局部 zoom、材质可用性。
2. V3 不能用作 topology solved 的主张来源，尤其不能用 PBR render 证明连通性。
3. 若要进入主文正例或可复现实验资产，V3b 应把 mesh 生成改成 occupancy/implicit connected scaffold，再用 hard gate 拦截未连通或不可用 mesh。

## 2. dryrun mesh component 风险排序

按 manifest 中 `mesh_component_count` 与 `largest_mesh_component_vertex_ratio` 粗排，当前 topology/mesh component 风险最大的是：

| 风险级别 | case | component / LCR | 主要风险来源 | 当前判定 |
|---|---:|---:|---|---|
| 极高 | `v3_sc_tree_crown_260_leaf_clusters` | 46252 / 0.000225 | SC tube skeleton 加大量 leaf clusters，tube/card 未共享顶点 | 视觉可看，mesh 不可直接主张连通 |
| 极高 | `v3_sc_bush_shell_220_leaf_shell` | 39652 / 0.000247 | shell SC 分枝与叶簇离散拼接，组件数接近叶/管段数量 | 视觉可看，topology 主文高风险 |
| 极高 | `v3_dla_aniso_crystal_800_faceted_frontier` | 11841 / 0.844475 | implicit 后 round/merge/facet 处理产生大量小碎片，虽有大主成分但碎片多 | 只能作为边界，需清碎片和连通 gate |
| 极高 | `v3_sc_root_network_260_root_hierarchy` | 6997 / 0.000228 | root tube 与 root hair token 分离，face component 指标极差 | 视觉可看，mesh 不可用作 connected root |
| 高 | `v3_ifs_branch_tree_d6_clean_orbit` | 1822 / 0.000823 | IFS tree skeleton 转 tube 与 tip sphere 拼接，transform 层级未焊接 | mode 可读性待看，topology 不可过线 |
| 高 | `v3_lsys_root_fan_d5_hierarchy` | 442 / 0.003925 | root hierarchy tube 和 root hair token 分离 | 需要 V3b connected root scaffold |
| 高 | `v3_lsys_pine_canopy_d5_layered_conifer` | 433 / 0.004829 | trunk/branch cylinders、针叶 spray 独立组件 | 只看 pine 视觉，不看 topology |
| 中高 | `v3_lsys_climbing_vine_d6_leaf_cards` | 206 / 0.039187 | vine mesh 加独立 leaf cards | 若视觉强，也仍需 connected mesh 修复 |
| 中高 | `v3_ifs_radial_ornament_o8_d4_solid_gear` | 77 / 0.089109 | ring/tooth cylinders 与中心 sphere 拼接，局部接触未焊接 | radial 视觉可看，ring closure 不可声称 |
| 中低 | `v3_ifs_fractal_lattice_d4_pyrite_scaffold` | 20 / 0.999509 | scaffold 已接近单主成分，但仍有少量碎片 | V3b 清碎片后有主文潜力 |
| 低 | `v3_ifs_bismuth_hopper_d4_terraced_lattice` | 4 / 0.999395 | 近单主成分，少量残片 | V3b 清碎片即可进入可用 mesh 候选 |
| 低 | `v3_dla_coral_cluster_900_implicit_organic` | 1 / 1.000000 | 已为单 mesh component | 可重点看视觉与 DLA family 指标 |
| 低 | `v3_dla_frontier_sheet_700_implicit_reef` | 1 / 1.000000 | 已为单 mesh component | 可重点看 sheet/frontier 视觉与厚度指标 |

最需要优先修复的是 SC crown、SC bush、SC root、IFS branch、L-system root/pine/vine、radial ornament。这些 case 的 component 爆炸不是小问题，而是当前几何表达方式与“可用 connected mesh”目标不一致。

## 3. 为什么远端 V3 仍值得看视觉

V3 的远端结果仍然有评估价值，原因不是 topology 已经解决，而是它能回答另一组问题：

1. **V3 改的是视觉输入分布**：脚本已经把 V1/V2 的弱点改成更强的 target-specific controls，例如 pine 的 trunk/whorl/needle sprays、root 的 thick-to-thin hierarchy、DLA 的 frontier-local implicit surface、lattice/hopper 的 scaffold cache。这些改动可能显著提升 textured render 的类别可读性。
2. **Trellis2/PBR 可能掩盖 OBJ 组件碎裂，但不能替代 mesh gate**：远端纹理和重建可能让 leaf/tube/card 的接触在图像上读成连续资产，这对 paper figure 的视觉诊断有用；但这只证明 asset-readiness 或 render-readiness，不证明本地 mesh 或导出的 GLB 拓扑连通。
3. **V3 能帮助决定 V3b 的视觉目标**：如果某些 V3 case 视觉已经强，例如 coral/frontier、pyrite/bismuth、某些 root/crown silhouette，就应保留其外观设计，把底层几何换成 connected scaffold；如果视觉仍失败，则 V3b 不应只做焊接，而要重设 target shape。
4. **V3 是 V1/V2 到 V3b 的筛选层**：远端结果可用于区分三类 case：视觉强但 topology 弱、topology 近似可用但 family 指标不足、视觉与 topology 都弱。V3b 只应优先投入第一类和少数第二类。

文案边界必须保持清楚：V3 可以说“strict visual matched candidates are worth inspecting for category and asset-readiness”，不能说“plant/SC/IFS branch topology is connected”。

## 4. V3b 总体方向：occupancy/implicit connected scaffold

V3b 不应继续依赖“很多 cylinder/card/sphere 在空间中相交，看起来像连接”的 mesh 表达。核心改法是先构造一个离散或隐式的 connected scaffold，再从同一个 scaffold 导出 mesh、occupancy metrics、root/path metrics 和 render。

### 4.1 推荐生成管线

1. **先生成递归支撑图**
   - L-system：保留 symbol rewrite、depth、branch token、leaf/root token，但输出为带 parent 的 support graph。
   - SC：保留 attractor competition、coverage、kill/influence radius，但输出 node-parent graph 和 attraction assignment。
   - DLA/frontier：保留 particle attachment/frontier order，输出 particle-parent graph。
   - IFS：保留 transform orbit、level、copy id，输出 copy graph/contact graph。

2. **把支撑图栅格化为 connected occupancy**
   - 对每条 parent-child edge 做 capsule/segment voxelization。
   - 对 root、junction、tip、leaf cluster anchor、gear tooth、lattice contact 做 dilation kernel。
   - 所有新增 token 必须以 anchor voxel 附着到主 scaffold，不允许直接以独立 mesh primitive 写入最终 OBJ。
   - 只保留 6-neighbor 或 26-neighbor 最大主成分；若需要保留多个语义块，必须有显式 bridge voxel 和 path-to-root 记录。

3. **从 occupancy/implicit field 导出 mesh**
   - 对植物/根系/branch：用 union-of-capsules SDF 或 voxel EDT 生成连续 implicit field，再 marching cubes。
   - 对 leaf/card：不要输出离散 card；改成附着在 branch 上的薄叶片 occupancy/SDF lobe，叶柄与 branch 共享 field。
   - 对 root hair/needle：作为主 SDF 的细分枝或附着 lobe，给最小半径下限，避免碎成独立小管。
   - 对 radial/gear：先生成闭环 occupancy skeleton，再导出单个 solid gear field；中心、环、齿、跨层 connector 都来自同一 field。
   - 对 lattice/hopper/crystal：继续用 scaffold occupancy，但导出前执行 largest component、morphological closing、small island removal。

4. **导出后做 mesh cleanup**
   - `merge_vertices` 只能作为辅助，不能替代 occupancy 连接。
   - 删除小于总顶点/面积阈值的 isolated islands。
   - 重新计算 normals、修复 degenerate faces。
   - 同步输出 debug layers：support graph、occupancy component map、mesh component map、root path map。

### 4.2 各类 V3b 修复要点

| family / case | V3b 修复方向 |
|---|---|
| L-system pine | trunk、whorl branches、needle sprays 全部写入同一 capsule/SDF scaffold；针叶必须有 branch anchor，不能是独立 cylinder spray。hard gate 关注主干可见性、whorl 层级、needle bundle 附着率。 |
| L-system root fan | root hierarchy 先转 root-to-tip connected occupancy；root hair 作为主根场的 attached lobe。hard gate 关注 single root attachment、fan silhouette、path-to-root。 |
| L-system vine | vine 主干、tendril、leaf lobe 全部从同一 implicit field 导出；leaf card 改为带叶柄的 attached thin lobe。hard gate 关注 helix continuity、tendril attachment、leaf anchor rate。 |
| SC tree crown | SC node-parent graph 转 connected branch SDF，leaf clusters 只允许附着到 branch terminal occupancy。hard gate 关注 attractor coverage、branch path-to-root、leaf anchor rate、crown silhouette。 |
| SC root network | root graph 转 thick-to-thin root SDF，细根必须连到 parent root voxel。hard gate 关注 root path-to-root、terminal root density、orphan root hair ratio。 |
| SC bush shell | shell attractor graph 转内部 branch scaffold，再添加 attached foliage shell lobe。hard gate 关注 shell coverage、inner/outer branch support、orphan foliage ratio。 |
| DLA coral/frontier | 保留 V3 implicit 思路，但从 parent graph 建 bridge samples；导出后只保留最大主成分并报告 deleted island mass。hard gate 关注 frontier attachment survival、porosity、fake bridge count。 |
| DLA aniso crystal | 先修正 facet/rounding 后碎片问题：facet quantization 必须在 connected field 上做，之后清 small islands；如果仍像 ordered crystal，文案改为 boundary，不当 DLA 正例。 |
| IFS branch tree | transform orbit 的每个 child copy 必须有 parent connector capsule/SDF；tip sphere 改为主场 terminal swelling。hard gate 关注 orbit error、copy survival、copy-to-root path。 |
| IFS radial ornament | 先建立 8-fold ring occupancy skeleton，所有齿和跨层 connector 附着到 ring；导出单一 solid field。hard gate 关注 8-fold symmetry、ring closure、radial connector path。 |
| IFS lattice / bismuth | 现有 scaffold 最接近可用；V3b 重点做 largest component、closing、island deletion 与 facet preservation。hard gate 关注 LCR、copy/contact graph、facet normals。 |

## 5. V3b hard gate

V3b 的 hard gate 应分成 mesh 可用性、occupancy 连通、root/path、family 匹配、视觉证据五层。建议主文正例必须全部通过，supplement 可以注明失败项。

### 5.1 mesh 可用性 gate

- `loader_status == success`
- OBJ/GLB export success，neutral render success，PBR render 可选但不作为结构 gate。
- `vertices >= 1000` 且 `faces >= 1000`，除非 case 本身是低复杂度 ornament。
- `bbox_diag` 在预设范围内，禁止 vine 类出现异常巨大尺度。
- `nonmanifold_edges`、`degenerate_faces`、`boundary_edges` 必须报告；主文正例不得有影响 render/printing 的明显破面。

### 5.2 mesh component gate

- `mesh_component_count <= 3` 作为主文 hard gate；植物/根/SC/IFS branch/radial 原则上要求 `== 1`。
- `largest_mesh_component_vertex_ratio >= 0.98`。
- `largest_mesh_component_area_ratio >= 0.98`。
- `small_island_vertex_ratio <= 0.02`，并记录 deleted island mass。
- 若保留多组件，必须是语义上合理的 detachable parts，并在 caption 中说明；strict matched 主表默认不接受。

### 5.3 occupancy 连通 gate

- `occupancy_component_count_6n_r0 <= 3`，主文正例优先 `== 1`。
- `largest_occupancy_component_ratio_6n_r0 >= 0.98`。
- `occupancy_component_count_6n_r1 == 1` 或 `largest_occupancy_component_ratio_6n_r1 >= 0.995`。
- `occupancy_component_count_26n_r0 == 1` 用作宽松 sanity check，但不能单独替代 6n。
- `deleted_mass_ratio <= 0.03`，否则说明连接是靠后处理删碎片得到的。

### 5.4 root/path gate

- `root_component_ratio >= 0.98`。
- `path_to_root_rate >= 0.98`，对根/植物/SC/IFS branch 必须接近 1。
- `orphan_mass_ratio <= 0.02`。
- `orphan_handle_rate <= 0.02`。
- `leaf_or_needle_anchor_rate >= 0.95`。
- `tip_to_root_path_rate >= 0.98`。

### 5.5 family metric gate

- L-system：depth token survival、branch order consistency、branch length decay、branch angle spread、tip count、root/leaf attachment rate。
- SC：attractor coverage、alive/uncovered attractor ratio、branch support density、nearest-attractor distance、collision/rejection count。
- DLA/frontier：frontier attachment survival、effective stickiness、porosity/cavity proxy、surface-to-volume ratio、blockiness、fake bridge count。
- IFS/radial/lattice：transform orbit error、copy survival ratio、scale drift、symmetry IoU、contact graph consistency、facet normal consistency。

### 5.6 视觉 gate

- 同一 mesh 的 overview、root/seed、junction/contact、terminal/facet/cavity camera zoom 必须齐全。
- neutral render 先过 category、silhouette、recursive-mode QA；PBR 只作为 asset-readiness。
- human QA 必须显式记录 `fragmented`、`wrong_category`、`wrong_mode`、`silhouette_mismatch`、`texture_masks_geometry_failure`、`tube_skeleton`、`bead_chunk`、`thin_sheet_missing` 等标签。

## 6. V3 到 V3b 的优先级

建议按“视觉潜力高、topology 风险高、论文收益高”的顺序推进：

1. **第一优先级：SC tree crown、SC root network、L-system pine/root/vine、IFS radial**
   - 这些是用户最关心的 plant/SC/IFS branch/radial 可用 mesh 问题。
   - 当前 component/LCR 指标最差，必须用 connected scaffold 重做。

2. **第二优先级：IFS branch tree、SC bush shell**
   - 视觉若远端 V3 可读，值得 V3b 修复。
   - 若远端仍像 spike/blob，则先重设视觉 target，再做 topology。

3. **第三优先级：DLA aniso crystal**
   - 已有大主成分但碎片多；重点是 facet 后处理不要打碎 mesh。
   - 仍需避免把 ordered crystal 写成 stochastic DLA solved。

4. **低成本修复：IFS pyrite lattice、bismuth hopper**
   - 已接近可用 mesh，V3b 做 cleanup、component gate、metric logging 即可。

5. **保持观察：DLA coral、frontier sheet**
   - dryrun 已单 mesh component。远端 V3 主要看 visual/family：是否 coral porous、是否 frontier sheet，而不是再优先修 connectivity。

## 7. 论文与实验表述建议

V3 当前可以写：

> V3 was launched as a strict visual matched screening run. Several cases improve category readability, but local dryrun mesh statistics show that plant, SC, and transform-branch candidates are not yet connected export meshes because tubes/cards/tips are emitted as independent primitives.

V3 当前不应写：

- “SC crown/root、pine/root fan、IFS branch/radial 已经拓扑连通。”
- “远端 textured render 证明 mesh connected。”
- “leaf cards/root hairs/needle sprays 是可打印或可仿真的 connected mesh。”
- “component count 高只是统计噪声，可以忽略。”

V3b 可作为下一轮目标写：

> V3b will replace primitive-level tube/card assembly with an occupancy/implicit connected scaffold, then gate every selected asset by mesh components, occupancy connectivity, path-to-root, family metrics, and neutral-render visual evidence before considering PBR asset-readiness.

## 8. 最终文件路径

- 输入脚本：`assets/strict_visual_matched_cases_v3_20260510.py`
- 输入 manifest：`results/strict_visual_matched_cases_v3_20260510_dryrun/manifest.csv`
- 输入指标方案：`docs/evaluation/strict_matched_v3_metric_and_selection_plan_zh_20260510.md`
- 本方案文档：`docs/evaluation/strict_visual_v3_connectivity_risk_and_v3b_plan_zh_20260510.md`
