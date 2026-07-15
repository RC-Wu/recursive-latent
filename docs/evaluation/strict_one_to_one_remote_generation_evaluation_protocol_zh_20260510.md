# Strict one-to-one remote generation evaluation protocol

日期：2026-05-10

范围：本文只定义 Recursive 3D Generative Growth / PS-RSLG 与传统递归生成方法的一对一评估方案和论文写法。不启动远端实验，不修改 `paper_siga/main.tex`。最终实验证据应以 `a100-2` 上新生成的 matched cases 为主；已有 V6/V7/V8/V8-thin 结果用于候选筛选、协议校准和论文定位。

## 0. 核心修正

本轮评估不能再做“看起来相似”的宽泛比较。每个对照必须从一个具体传统 procedural task 出发，然后用 PS-RSLG 复现同类别、同复杂度、同递归深度、同生长/变换模式的任务。

严格匹配单位定义为：

```text
Task = (classical_family, exemplar_name, object_category,
        recursive_mode, target_silhouette, visible_depth,
        control_params, growth_or_transform_pattern)
```

PS-RSLG 输出允许使用更高质量 root、Trellis2 root、public guide/root 或已有项目内强 root，但必须满足：

```text
category(ours) ~= category(classical)
silhouette(ours) ~= silhouette(classical)
visible_depth(ours) ~= visible_depth(classical)
mode(ours) ~= mode(classical)
control_semantics(ours) ~= control_semantics(classical)
```

因此公平表述不是“同一个低质量 primitive 上谁更好”，而是“同一递归任务 family 下，传统 procedural primitive 与 PS-RSLG 的 generator-native root/operator/projection/naturalization 组合之间的对比”。每个最终 case 必须记录：

```text
traditional task -> root/source provenance -> PS-RSLG rule family
-> control parameters -> projection schedule -> masked naturalization schedule
-> texture/PBR guide -> render protocol -> selection budget
```

## 1. Exemplar tasks

### 1.1 L-system

L-system 任务必须保留 rewriting / turtle branch 语义，不能把 branch/tree 任务换成 unrelated vine 或 blob canopy。

| exemplar task | 传统模式 | 目标类别 | 复杂度/深度 | PS-RSLG matched case 要求 |
|---|---|---|---|---|
| `lsys_pine_canopy_d5` | whorl/side-branch rewriting，角度、缩放衰减、层级分叉 | 松树/针叶树冠 | depth 5，可见 trunk、branch whorl、needle clusters | 生成 upright pine/tree canopy；保留主干-轮生枝-针叶簇层级；不能只是球形树冠或裸杆 |
| `lsys_root_fan_d5` | root rewriting，主根分叉、尺度衰减、细根概率 | 根扇/根网 | depth 5，主根到 rootlet 可见 | 生成同向扩张的 root fan；细根必须 attach 到主根；不能是随机线团 |
| `lsys_climbing_vine_d6` | helicoidal main chain + tendril/leaf side symbols | 攀援藤蔓 | depth 6，主链、卷须、叶/附着点可见 | 生成 climbing vine；保留螺旋/攀援方向、侧卷须和叶片 token |

### 1.2 Space colonization

Space colonization 任务必须保留 attractor competition，不应只用普通 branch grammar 冒充。传统方法的强项是 coverage 和 branch path，论文中要承认。

| exemplar task | 传统模式 | 目标类别 | 复杂度/深度 | PS-RSLG matched case 要求 |
|---|---|---|---|---|
| `sc_tree_crown_260` | 260 个 crown attractors，influence radius / kill radius / tip budget | 树冠 | crown envelope filled by attractor-guided branches | 使用 attractor field / occupancy competition；输出 tree crown-like asset，而不是 root/vine |
| `sc_root_network_260` | downward/root field attractors，竞争生长和 kill radius | 根系/地下根网 | 多主根 + dense rootlets | 使用同类吸引点和排斥半径；rootlets 需要 attached |
| `sc_bush_shell_220` | shell/canopy attractor distribution | 灌木/壳层冠 | shell-like outer coverage | 使用 shell attractor + branch/leaf shell naturalization；不应变成实心 blob |

### 1.3 DLA / frontier

DLA/frontier 不能写成真实物理 DLA 已解决。严格任务是 frontier attachment / occupancy exclusion / accretive growth 的资产生成对比。

| exemplar task | 传统模式 | 目标类别 | 复杂度/深度 | PS-RSLG matched case 要求 |
|---|---|---|---|---|
| `dla_coral_cluster_900` | stochastic walkers attach to occupied frontier，stickiness，exclusion | 珊瑚/礁状团簇 | 约 900 attachment events，分叉前沿和孔洞可见 | 使用 frontier mask + attachment kernel + bridge certificate；输出 continuous coral/reef，不是石块团 |
| `dla_frontier_sheet_700` | boundary/frontier accretion with occupancy exclusion | 薄片/边界膜/礁面 | 约 700 frontier events，open boundary 和 membrane 可见 | 使用 boundary sheet frontier + local membranes/ridges；避免漂浮薄片 |
| `dla_crystal_cluster_520` | frontier accretion constrained by facet directions | 晶体/晶簇 | 约 520 accretive events，facet/ridge 可见 | 使用 frontier attachment + facet/ridge rule；不能 claim physical crystallization |

### 1.4 IFS / transform-copy

IFS 必须按 transform family 匹配。`IFS fractal tree -> pyrite` 不合格，除非把任务重定义为 lattice/orbit。

| exemplar task | 传统模式 | 目标类别 | 复杂度/深度 | PS-RSLG matched case 要求 |
|---|---|---|---|---|
| `ifs_fractal_tree_d5` | contractive branch transforms，scale/rotate/copy | fractal tree / branch ornament | depth 5，自相似 branch hierarchy | ours 必须是 transform-copy tree/branch-like asset，不能用 pyrite 代替 |
| `ifs_radial_ornament_o8_d4` | order-8 radial transform orbit + contraction | 径向饰件/门户/花窗 | orbit 8，depth 4 | 使用同阶 radial transform set、ring/spoke/teeth 结构和 orbit consistency |
| `ifs_fractal_lattice_d4` | affine translation/scale/copy lattice | 晶格/pyrite-like lattice | depth 4，多尺度 lattice/facet | pyrite lattice 可以作为 matched 正例，但任务名应是 lattice/orbit，不是 tree |

## 2. PS-RSLG operator reproduction

### 2.1 L-system reproduction

传统 L-system production：

```text
F -> F [ + theta F_s ] [ - theta F_s ] F
F_s -> scale_decay * F
```

PS-RSLG 对应算子组合：

```text
root source:
  pine/tree/root/vine high-quality root or generated guide root
state fields:
  support S_d, oriented handles H_d, parent-child graph G_d,
  scale schedule s_d, branch angle theta_d, semantic token labels
operators:
  Attach(handle, child_token, T(theta, scale))
  Split(handle, k, angle_distribution)
  Prune/Compete(min_radius, collision_mask)
  ProjectConnected(root_component, bridge_radius)
  MaskedNaturalize(mask = new child + junction + local bark/needle/rootlet region)
controls:
  depth D, branch angle, scale decay, side-branch probability,
  token budget, needle/rootlet density, attachment radius
```

严格复现要点：

- 分叉图的 parent-child 拓扑必须对应传统 production 的层级。
- visible depth 用 branch hierarchy 和 zoom panel 证明，不能只用纹理噪声证明。
- naturalization 只允许改善局部连接、表面和材质，不允许把 L-system 树冠抹成全局 blob。

### 2.2 Space-colonization reproduction

传统 space colonization 更新：

```text
for each tip h:
  A_h = attractors within influence radius r_i
  dir(h) = normalize(sum_{a in A_h} normalize(a - h))
  h' = h + step * dir(h)
remove attractors within kill radius r_k
```

PS-RSLG 对应算子组合：

```text
root source:
  tree crown / root network / bush shell guide
state fields:
  attractor set A_d, active tips H_d, occupied support S_d,
  kill mask K_d, influence graph I_d
operators:
  AttractorSelect(H_d, A_d, r_i)
  GrowTip(handle, dir, step, child_token)
  OccupancyCompetition(r_exclude, tip_budget)
  KillCoveredAttractors(r_k)
  ProjectConnected(root_component, path_certificate)
  MaskedNaturalize(mask = new growth + attractor-coverage junctions)
controls:
  attractor density, influence radius r_i, kill radius r_k,
  step length, tip budget, exclusion radius, depth/iteration count
```

严格复现要点：

- `sc_tree_crown_260` 的 ours 必须是 tree crown，不应拿 vine/root 代替。
- `sc_root_network_260` 的 ours 必须报告 attractor coverage 和 path-to-root。
- 可把传统 SC 写成强结构 baseline；PS-RSLG 的优势应集中在 generator-native surface/material 和 local naturalization，而非否定 SC 的结构能力。

### 2.3 DLA/frontier reproduction

传统 DLA/frontier 更新：

```text
particle random-walks until it hits frontier(S_d)
accept with stickiness p
S_{d+1} = S_d union particle
```

PS-RSLG 对应算子组合：

```text
root source:
  coral/reef/crystal frontier scaffold or generated high-quality root
state fields:
  occupied support S_d, frontier F_d, exclusion field E_d,
  attachment certificates C_d, bridge paths B_d
operators:
  FrontierSample(F_d, kernel, stickiness)
  AttachPatch(frontier_site, local_token, normal/tangent frame)
  ExcludeOccupied(E_d, min_distance)
  BridgeToRoot(frontier_site, path_certificate, max_bridge_cost)
  ProjectConnected(root_component, preserve_porosity=True)
  MaskedNaturalize(mask = frontier tip + bridge neck + local pore/facet region)
controls:
  number of attachment events, stickiness, kernel radius,
  bridge radius/cost, porosity target, frontier thickness,
  facet directions for crystal variants
```

严格复现要点：

- claim 是 `frontier-attachment asset generation`，不是物理 DLA 仿真。
- 视觉必须能读出前沿附着、tip、neck、pore/facet，不应是黑棕块状石头。
- 需要同时报告拓扑连通和 blockiness/naturalness，因为 DLA 的表面采样连通不等于视觉自然。

### 2.4 IFS / transform-copy reproduction

传统 IFS：

```text
S_{d+1} = union_i T_i(S_d),  T_i(x) = s_i R_i x + t_i
```

PS-RSLG 对应算子组合：

```text
root source:
  branch motif / radial ornament motif / lattice crystal motif
state fields:
  motif support M_d, transform set {T_i}, orbit graph O_d,
  contact anchors, symmetry/lattice certificates
operators:
  TransformCopy(motif, T_i)
  OrbitComplete(group_or_lattice_set)
  ContactBridge(anchor_i, anchor_j, face_or_edge_contact)
  CollisionReject / OccupancyMerge
  ProjectConnected(root_component, orbit_preserve=True)
  MaskedNaturalize(mask = contact facets + copied motif boundary)
controls:
  transform matrices, contraction ratios, orbit order,
  depth, contact threshold, symmetry tolerance
```

严格复现要点：

- tree IFS 必须对 tree/branch IFS；lattice IFS 才能对 pyrite/lattice。
- 可说 PS-RSLG 支持 transform-copy grammar，并用 transform diagnostics 筛选稳定 operator。
- 不能说 Trellis2 严格 equivariant；只能报告 empirical orbit/symmetry consistency。

## 3. Metrics and computation

### 3.1 Connectivity and topology

设 mesh 或 sampled surface 转为体素占据集合 `V_r`，`r` 为体素半径或采样分辨率，`CC(V_r)` 为 6-neighborhood connected components。

| metric | 公式/计算方式 | 用途 |
|---|---|---|
| component count | `C_r = |CC(V_r)|` | 主连通性诊断 |
| largest component ratio | `LCR_r = max_{c in CC(V_r)} |c| / |V_r|` | 主体质量是否集中 |
| root-attached ratio | `RAR_r = |component(root) intersect V_r| / |V_r|` | 是否从 root 连到全体 |
| orphan mass ratio | `OMR_r = 1 - RAR_r` | 浮动/断裂质量 |
| path-to-root rate | `PTR = #terminal handles with path to root / #terminal handles` | 分枝、rootlet、frontier tip 是否 attached |
| attachment survival | `AS = #expected attachments still connected after decode / #expected attachments` | Trellis2 decode/texture 后连接是否保留 |
| bridge cost | `BC = mean length_or_voxels(bridge path)`；同时报 `max BC` | DLA/frontier fake bridge 风险 |

主表建议用 surface-sampled voxel connectivity 作为跨 OBJ/GLB 的主指标；raw face components 只作为 mesh diagnostic，因为材质 seam 和 GLB 三角化会夸大 face components。

### 3.2 Mesh quality

| metric | 公式/计算方式 | 备注 |
|---|---|---|
| raw face component count | mesh face adjacency components | 诊断材质岛、碎面、未焊接情况 |
| welded component count | weld vertices within epsilon 后重新算 face components | 比 raw face 更公平 |
| non-manifold edge count | incident faces not equal 2 的 edge 数 | mesh validity |
| boundary edge count / hole proxy | incident faces equal 1 的 edge 数 | holes / open surfaces |
| degenerate face ratio | `#area(face) < eps / #faces` | 几何退化 |
| normal consistency | 相邻面法线夹角异常比例或 signed normal flips | 表面方向稳定 |
| triangle aspect ratio | `AR = longest_edge / (2 * sqrt(3) * area / longest_edge)` 或等价质量指标 | thin triangles / slivers |
| Laplacian roughness | `R = mean_v ||v - mean(N(v))||_2`，可按 bbox 归一化 | 表面粗糙和噪声 |
| blockiness score | voxelized surface normal 与轴方向对齐比例，或 `mean max(|n_x|,|n_y|,|n_z|)` 高轴对齐占比 | DLA/coral 是否变成方块 |
| watertight / repair status | trimesh/blender import check + repair flags | 资产可用性 |

### 3.3 Recursive pattern and morphology

| family | metric | 计算方式 |
|---|---|---|
| L-system | branch angle distribution | skeletonize 后统计 parent-child angle，与 target distribution 的 Wasserstein/KS distance |
| L-system | branch length distribution | 每层 edge length 的 mean/std/decay ratio |
| L-system/root | terminal density | terminal tips per bbox volume 或 per root length |
| Space colonization | attractor coverage | `coverage = #attractors within r_k of support / #attractors` |
| Space colonization | nearest-attractor distance | `mean_a min_{x in support} ||a-x||` |
| DLA/frontier | frontier attachment survival | accepted frontier sites 中 decode 后仍 root-connected 的比例 |
| DLA/frontier | porosity/cavity proxy | bbox 内空体素比例、local cavity count、pore size histogram |
| DLA/frontier | tip/neck count | frontier tips 和 narrow necks 的数量、平均半径 |
| IFS/transform | orbit error | `OE = mean_i d(T_i(M_d), matched_component_i)`，用 Chamfer/IoU |
| IFS/transform | symmetry IoU | `IoU(S, gS)` over orbit group/lattice transforms |
| IFS/transform | self-similarity | zoom crop/mesh patch 与 transformed parent patch 的 DINO/Chamfer similarity |

### 3.4 Multi-scale zoom and effective detail

最终图必须使用 Blender camera-level zoom，不使用 2D crop 作为论文证据。每个 case 至少输出：

- overview raw：纯白、正方形、居中、无文字；
- overview callout：矩形框标出 zoom 来源；
- zoom 1：root/seed attachment；
- zoom 2：junction/contact/frontier neck；
- zoom 3：terminal tip、needle/rootlet、pore、facet 或 transform-contact。

多尺度指标：

```text
zoom_detail_density_l = #detectable terminal/detail tokens in zoom_l / visible_area_l
zoom_consistency_l = sim_DINO(render_zoom_l, render_expected_l)
detail_retention = zoom_detail_density_final / zoom_detail_density_initial_or_target
```

论文中只能把这些写成 finite-depth visible detail / recursive zoom evidence，不能写成真正 infinite recursion 或严格有效分辨率提升，除非补 one-shot vs recursive under same token budget 的实验。

### 3.5 Visual semantic and naturalness metrics

这些指标只能作为辅助，不替代结构指标。

| metric | 计算方式 | 使用边界 |
|---|---|---|
| multiview CLIP category score | 对固定多视角白底 render，算 image-text cosine，取 mean/std | 类别语义一致性 |
| CLIP negative gap | `score(prompt_pos) - score(prompt_neg)`，neg 包括 `broken floating pieces`, `blocky voxel chunks`, `unconnected fragments` | 粗略视觉质量，不作硬结论 |
| DINO zoom consistency | overview callout 区域与 camera zoom 的 feature consistency | 检查 zoom 是否来自真实区域 |
| aesthetic score | LAION aesthetic 或类似模型，多视角平均 | 可选，仅写 appendix |
| human QA label | `paper-grade / appendix / screening / fail`，附理由 | 主图选择必须保留人工 QA |

### 3.6 Runtime, budget, and controls

每个 matched case 必须记录：

```text
classical_runtime_total
classical_depth_or_iterations
classical_control_params
ours_encode_time
ours_per_depth_rule_time
ours_projection_time
ours_masked_naturalization_time
ours_decode_time
ours_texture_export_time
ours_total_time
peak_gpu_memory
token_count_per_depth
vertices/faces/file_size
root_selection_budget
seed_count
candidate_count
selection_rule
```

公平表述必须包含 selection budget。若 ours 从多个 root/seed/operator settings 中挑选最强结果，传统 baseline 也应有相近 seed/control sweep，或者在表中明确 `selection budget` 不同。

## 4. Paper presentation

### 4.1 主文图建议

主文不应塞满所有 family。建议最小主文组合：

1. L-system：`lsys_pine_canopy_d5` 或 `lsys_root_fan_d5` vs matched PS-RSLG tree/root。
2. Space colonization：`sc_tree_crown_260` 或 `sc_root_network_260` vs matched attractor/competition PS-RSLG。
3. DLA/frontier：`dla_coral_cluster_900` 或 `dla_frontier_sheet_700` vs V8/V8-thin 中筛出的 frontier case。
4. IFS/transform：`ifs_fractal_lattice_d4` vs pyrite/lattice，或 `ifs_radial_ornament_o8_d4` vs radial ornament。

每个 family 的展示格式：

```text
Classical baseline overview + 2-3 camera zooms
PS-RSLG overview + matched 2-3 camera zooms
small metric strip: LCR, RAR/PTR, mesh validity, family-specific metric, runtime
operator line: root -> rule -> projection -> masked-N -> texture
```

### 4.2 Coverage matrix

论文中应有 coverage matrix，但措辞必须是 restricted finite-step instances。

| classical system | PS-RSLG restriction | extra PS-RSLG ingredient | claim type |
|---|---|---|---|
| L-system | typed rewrite over handles with transform/copy and branch labels | per-depth projection + local naturalization of junction/material | formal coverage + selected visual evidence |
| Space colonization | attractor field controls handle selection and growth direction | occupancy competition + root-attached projection | formal coverage + matched task evidence |
| DLA/frontier | frontier mask controls attachment proposals | bridge certificate + connectivity projection + masked frontier naturalization | stress/selected asset evidence |
| IFS | finite transform set over motif/support | orbit/contact projection and empirical transform diagnostics | formal coverage + selected lattice/radial evidence |
| Shape/scifi grammar | split/extrude/replace over modules | collision mask, module cache, texture export | appendix/extension unless fully evaluated |

### 4.3 Fair claims

可以 claim：

- PS-RSLG gives a unified finite-depth grammar view that can instantiate restricted versions of L-system, space-colonization, DLA/frontier, and IFS/transform-copy patterns.
- Under matched exemplar tasks, selected PS-RSLG outputs combine classical recursive controls with generator-native mesh/texture/PBR naturalization.
- Per-depth projection and attachment certificates are important for maintaining root-connected recursive state before continuing recursion.
- For selected tree/root/coral/lattice cases, surface-sampled connectivity and camera-level zoom show a dominant connected renderable asset with visible multi-scale structure.
- Traditional procedural systems remain strong structural baselines; the comparison isolates asset-readiness and generator-native naturalization, not a universal structural defeat of procedural methods.

不能 claim：

- PS-RSLG universally outperforms L-system / SC / DLA / IFS.
- Trellis2 or the sampler is strictly equivariant under arbitrary transforms.
- The DLA/frontier results are physically accurate DLA or real crystal growth.
- Texture/PBR export proves topology is clean.
- Multi-scale zoom proves infinite recursion or true effective resolution increase without same-budget one-shot controls.
- Current weak strict vine rows support positive vine claims; those must be replaced by stronger matched tree/vine/root candidates or marked appendix/status.
- Pyrite proves IFS tree matching; it only supports lattice/orbit matching.

### 4.4 Caption discipline

每个图 caption 应明确：

- classical task and controls；
- PS-RSLG operator composition；
- root/source provenance；
- whether result is newly generated on `a100-2` or an existing candidate；
- selection budget；
- which metrics are structural vs visual auxiliary。

推荐英文句式：

```text
We compare each procedural family on a matched exemplar task rather than on
loosely similar outputs. The PS-RSLG row uses the same recursive mode and
control semantics, while instantiating grammar tokens through generator-native
roots, per-depth projection, masked local naturalization, and textured GLB
export.
```

## 5. Positioning current V6 / V7 / V8 / V8-thin results

### 5.1 V6

V6 的定位：全类 strict matched remote-generation candidate batch。它覆盖 L-system、SC、DLA/frontier、IFS/radial/lattice，且 dry-run 输入强调 single component、metadata 和 traditional alignment。

可用方式：

- 作为最终远端新 case 的主要输入池和 protocol proof。
- 植物/根/SC 类可优先从 V6 seed sweeps 中筛选 paper-grade candidates。
- V6 DLA/coral/frontier 解决了连通性输入门槛，但视觉反馈显示仍可能像块状石头，因此不能自动进主文。

论文定位：

- `candidate generation and screening`；
- 不应把 V6 全部写成最终成功结果；
- 只把通过 white overview + camera zoom + metrics + human QA 的子集升为 main evidence。

### 5.2 V7

V7 的定位：DLA/frontier 视觉自然度修正批次，重点从块状石头转向 brighter organic tube/reef/frontier。

可用方式：

- 作为 DLA/frontier 的中间候选和视觉方向证据。
- 可用于说明 V6 后发现 frontier visual naturalness 不足，随后改进 root/guide/operator instantiation。

论文定位：

- screening / appendix；
- 若 V7 某个 case 指标和 camera zoom 均过关，可升级为 DLA/frontier 候选；
- 不能用 V7 的视觉改善单独支撑 method claim，必须配合 connectivity、bridge survival、blockiness 和 human QA。

### 5.3 V8

V8 的定位：DLA/frontier refine 主批次。它保留 stochastic frontier attachment、occupancy exclusion、DLA/coral/frontier/crystal 的 accretive attachment comparison，同时改用 rooted skeleton、tapered tubes、branchlets、thin plates/ridges 和 porous membranes 来减少块状感。

可用方式：

- DLA/coral/frontier 主文候选应优先从 V8 中选，而不是旧 DLA/coral。
- `v8_dla_coral_lace_reef_branching_a`、`v8_dla_coral_antler_ridge_branching`、`v8_dla_frontier_fan_lace_membrane_a`、`v8_dla_crystal_accretive_blade_cluster` 等适合作为下一轮远端优先队列。

论文定位：

- 如果远端 textured GLB + camera zoom 通过，V8 可成为 DLA/frontier 主证据。
- claim 仍是 `frontier-attachment asset generation`，不是 physical DLA。

### 5.4 V8-thin

V8-thin 的定位：V8 的细端头/薄枝版本，用来改善 DLA/coral/frontier 的 terminal tip、branchlet 和 porous membrane 读法。

可用方式：

- 用于 DLA/frontier zoom panel 的 terminal tip 和 fine branch evidence。
- 若 V8 主体较好但端头偏粗，V8-thin 可作为同一 task 的 stronger seed/root/operator candidate。

论文定位：

- 适合作为 final selection pool，不单独作为一个新方法版本宣传。
- 必须记录它与 V8 的差异：thin-tip instantiation changed root/operator geometry, not the evaluation rule family。

### 5.5 当前旧强结果

现有 `hero_multi_zoom_white_20260510` 中 bismuth、pyrite、coral、root_fan 可作为白底 camera zoom 格式参考。它们不是本协议下所有 family 的最终严格 evidence：

- pyrite：可用于 `IFS/lattice/orbit`，不可用于 `IFS fractal tree`。
- coral：可作为 DLA/frontier 候选，但 blocky 感需要与 V8/V8-thin 比较后再决定。
- root_fan：可用于 L-system root fan 候选；若主文写 tree canopy，则还需要 tree/canopy matched candidate。
- bismuth：可作为 crystal/stepped growth appendix 或 candidate，不应 claim strict physical crystal growth。

## 6. Immediate execution recommendation

不在本文启动远端任务。下一轮实际执行应按以下顺序：

1. 为每个 family 固定 2-3 个 exemplar tasks，上表任务名不再随意改。
2. 在 `a100-2` 远端以新 case 为主生成 matched PS-RSLG candidates；每个 task 至少 3 seeds / roots / operator settings，记录 selection budget。
3. 先筛硬门槛：surface-sampled `C_r <= 2`、`LCR_r >= 0.98`、`RAR_r >= 0.95`、render import 成功、metadata 完整。
4. 再筛 family metric：L-system branch distribution、SC attractor coverage、DLA frontier survival/blockiness、IFS orbit error。
5. 最后做纯白 overview + nested camera zoom + human QA。只有 paper-grade 子集进入主文。
6. 主文优先使用 L-system root/tree、SC root/tree、V8/V8-thin DLA/frontier、IFS lattice/pyrite 四类；不合格或模式不匹配的旧配对全部降为 appendix/screening。

## 7. Bottom line

这套评估的核心不是证明传统方法弱，而是证明：在严格 matched recursive task 下，PS-RSLG 可以把传统递归控制模式移植到 generator-native 3D asset pipeline 中，并通过 per-depth projection、attachment certificates、masked local naturalization 和 textured GLB export 得到可渲染、可放大的有限深度递归资产。

最重要的论文风险是过度泛化。只要坚持 task-level strict matching、selection budget 透明、traditional baselines 作为强结构方法呈现、DLA/IFS claims 按任务边界收紧，这组实验可以从“漂亮但松散的相似比较”升级为 defensible one-to-one evaluation。
