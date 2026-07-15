# Recursive 3D Generative Growth Baseline / Metric / Related Evaluation Plan

创建时间：2026-05-08

写作目的：回应“baseline/metric 离方法很远”的批评，把评估从几张视觉结果改成可复现、可对照、可解释的实验协议。本文档只定义评估方案，不修改 `main.tex` 或 `references.bib`。

## 0. 结论先行

本文的评估主张不应是“生成模型比传统算法更漂亮”，而应是：

> 在同一递归程序、同一深度预算、同一 mesh/GLB/Blender 输出协议下，传统递归算法给出清楚但局部粗糙的结构 scaffold；one-shot 3D 生成给出局部自然但递归结构不稳的资产；Projection-Stabilized Recursive Generative Grammar 在反复增长中同时保持结构、连通性、尺度递归和可渲染性。

因此 baseline 和 metric 必须围绕三件事组织：

1. 结构是否按递归规则增长，而不是只看最终图像是否好看。
2. 每一深度的错误是否被稳定住，而不是最后用一次大 repair 粉饰。
3. 输出是否是可用资产：mesh/GLB 可加载、材质通道有效、固定 Blender 协议下可复现渲染。

## 1. 任务正式定义

### 1.1 任务 A：Structure-first recursive growth

输入：

- root asset：root mesh、root image-to-mesh asset，或传统程序 scaffold mesh；
- grammar program：一组递归规则、transform、anchor/frontier/tip 选择器、depth budget `D`；
- optional guide：类别 prompt、root render、SD3.5 guide image、或 textured root material intent；
- resource budget：每深度最大 token/vertex/face、最大运行时间、最大投影次数。

输出：

- 每个深度 `d=0..D` 的 mesh/OBJ；
- 如果 texturing 成功，则输出 GLB，包含 base color / roughness / metallic / opacity 等 PBR 通道；
- 固定 Blender/Cycles 协议下的多视图 render；
- 每个深度的 metric JSON/CSV。

评价目标：

- 结构保真：递归方向、branch/tip、transform-copy、space competition 是否保留；
- 递归稳定：component、collision、bbox、token/vertex 增长是否受控；
- 资产可用性：mesh/GLB 是否可加载、材质是否可渲染、视觉是否可解释。

### 1.2 任务 B：Multiscale refinement / infinite-zoom proxy

输入：

- root motif 或 root patch；
- contractive transform、portal/scale-down/recursive-frame grammar；
- logical depth `D_logical` 与 visible window / LOD budget；
- optional cache policy：motif cache、latent cache、LOD cache、sliding-window cache。

输出：

- zoom panel：固定相机下的 `z=0..K` 层局部放大图；
- 每个 zoom level 对应的 local mesh/OBJ/GLB 或 cropped render；
- cache 命中率、visible token 数、局部重建误差。

评价目标：

- 局部细节随 zoom 保持，而不是只把同一个 mesh 缩小；
- logical depth 可大于实际 decode depth，但 visible window 内 token/vertex budget 有界；
- transform/self-similarity 分数和视觉 panel 同时报告，不能只报 fractal dimension。

### 1.3 任务 C：Texture / PBR renderability

输入：

- high-quality textured root mesh，或 SD3.5 guide image -> Trellis2 root mesh；
- structure-first growth 输出的 final mesh；
- Trellis2 texture/PBR export pipeline；
- 固定 lighting/camera/material fallback。

输出：

- GLB；
- Blender/Cycles textured render；
- PBR 通道检查表；
- 如果 GLB 不可用，输出 neutral OBJ render 和失败原因。

评价目标：

- 递归结构不被 texture 隐藏；
- PBR 通道真的存在且数值有效；
- 同一几何在 neutral render 与 textured render 中都能读出结构。

## 2. 公平输出协议

所有 baseline 必须经过同一资产接口：

```text
baseline native output
-> normalized mesh/OBJ or point/voxel-to-mesh
-> optional O-Voxel/SLAT encode-decode/projection if baseline uses our generator interface
-> optional GLB texture export
-> same Blender/Cycles camera/light/resolution
-> same metric scripts
```

公平约束：

- 不允许传统 baseline 只展示 line/point preview，而方法展示 Blender render。
- 不允许方法只展示最终 textured GLB，而 baseline 使用 raw untextured scaffold；至少提供 neutral geometry render 行。
- 所有方法都报告 depth `0,1,2,3`；主 case 增加 vine depth 5。
- 所有方法都报告失败：empty mesh、GLB import fail、材质缺失、component 爆炸都进入表格。
- 所有视觉图都从可追溯 mesh path 和 render path 生成。

## 3. 传统 baseline

| Baseline | 参考来源 | 适配任务 | 公平输出方式 | 主要比较点 |
|---|---|---|---|---|
| IFS / fractal transform-copy | Barnsley `barnsley1988fractalsEverywhere`，Hutchinson 语义需补 bib/待核验 | contractive motif、scale-down、portal/infinite-zoom proxy | 用 cylinder/tube 或 implicit sweep 把 transform copies 转成 OBJ；可再 O-Voxel encode-decode；同相机 render | 自相似与尺度递归强，但局部几何和材质弱 |
| L-system / turtle plant | Lindenmayer `lindenmayer1968lsystemsI`，ABOP `prusinkiewicz1990abop` | tree/vine/root branching | turtle segments -> tapered cylinders -> OBJ；必要时 skeleton-to-mesh；同一 branch radius schedule | 符号递归清楚，适合 branch/tip/angle metric |
| Space colonization | Runions et al. `runions2007spacecolonization` | tree/root/vine competition | attractor/tip graph -> tapered cylinder mesh；可输出 skeleton JSON + OBJ；同 depth/attractor count | 与本文 `compete` 最直接对比：传统显式 competition vs sparse latent competition + projection |
| DLA / frontier growth | Witten and Sander `witten1981dla`，review `sander2000dlaReview` | coral/crystal/porous/frontier accretion | occupied voxels -> cubes 或 marching-cubes mesh；同 voxel resolution 和 smoothing budget | stochastic accretion 与 porous topology 强，但资产可用性弱 |
| Shape grammar / CGA / split grammar | Stiny/Gips 1972 待补 bib；Muller et al. 2006 CGA 待补 bib | architecture/ornament/portal/radial modules | split/extrude/replace rules -> watertight-ish OBJ；可加 procedural UV/material；同 render protocol | 建筑规则强，局部 variation 和 learned material 弱 |

当前代码状态：

- `assets/procedural_baselines.py` 已有 IFS、L-system、DLA 的 OBJ/PNG/metric 输出。
- Space colonization 和 shape grammar 还需补 baseline generator；本文档先定义评估接口，不改脚本。

## 4. 生成模型 baseline

| Baseline | 输入 | 输出 | 目的 | 失败判据 |
|---|---|---|---|---|
| One-shot Trellis2 | root/guide image 或 category prompt | 单个 mesh/GLB/render | 测试原生 3D 生成质量上限 | 递归 branch/scale/portal 不保留 |
| Image-entry then recursion | image -> Trellis2 root mesh -> grammar recursion | depth mesh/GLB/render | 测试普通用户只有图像入口时的路径 | root 可以，但递归后 component 爆炸或结构丢失 |
| Direct grammar | root mesh/O-Voxel/SLAT + coordinate grammar，无 projection | depth OBJ/render | 证明 naive recursive edit 会积累碎片 | component count 超线性增长，largest ratio 下降 |
| Final-only projection | direct grammar 到 final depth 后只投影一次 | final OBJ/render | 检验“最后清理”是否足够 | final 外观改善但中间深度不可用，或 topology 已不可恢复 |
| Full flow repair | 每步或末尾强 denoise/flow repair | repaired mesh/render | 检验 frozen sampler 是否会 wash out topology | branch/tip/portal scaffold 消失 |
| Masked weak blend | 局部 mask + 小 alpha + 少步 denoise | depth OBJ/render | 检验低强度 naturalization 的 Pareto 点 | 局部没改善，或弱改善但连接性下降 |
| Proposed projection-stabilized grammar | sparse merge -> competition -> masked naturalization -> per-depth projection -> re-encode | depth OBJ/GLB/render | 主方法 | 如果与 direct/final-only 无统计差异，则 claim 不成立 |
| Texture/PBR variants | final projected geometry + guide/root texture | GLB/PBR render | 测试外观资产化能力 | GLB import fail、PBR 通道缺失、texture 隐藏结构 |

必须成组比较：

- geometry-only：Direct / Final-only / Full flow / Masked weak / Proposed。
- image-entry：One-shot / image-entry recursion / proposed mesh-first recursion。
- texture/PBR：neutral OBJ / textured GLB / high-quality root texture / SD3.5 guide variants。

## 5. 定量指标设计

### 5.1 Connectivity and component stability

已有脚本 `assets/mesh_quality_metrics.py` 可直接支持：

- `component_count`
- `largest_component_vertices`
- `largest_component_vertex_ratio`
- `small_component_count_lt100`
- `fragmentation_score = 1 - largest_component_vertex_ratio`
- `vertices / faces / bbox_extent / bbox_volume / bbox_diag`

新增建议：

- component growth rate：`component_count(d) / component_count(d-1)`；
- fragment survival after projection：投影前小 component 中仍保留到投影后的比例；
- attachment success rate：新增 branch/proposal 中与 largest component 相接的比例；
- per-depth stability AUC：`largest_component_vertex_ratio` 对 depth 的面积。

### 5.2 Branch / tip / angle metrics

适用 L-system、space colonization、tree/vine/root：

- skeletonize 或直接使用 baseline 的 segment graph；
- tip count：degree-1 non-root nodes；
- branch count：degree >= 3 nodes；
- branch length distribution：每条 edge 或 polyline path 长度；
- branching angle distribution：child edge 与 parent edge 的夹角；
- branch radius taper consistency：半径随 depth 是否单调/平滑；
- tip direction entropy：分枝是否塌缩到单一方向。

对生成 mesh：

- 优先从 grammar trace / anchor trace 读取 branch graph；
- 如果没有 trace，做 voxel/skeleton proxy，但必须标注为 proxy metric。

### 5.3 Occupancy / collision / space competition metrics

- occupancy coverage：占据 voxel 数 / bounding volume voxel 数；
- attractor coverage：每个 attractor 到最近 tip/branch 的距离分布；
- collision violation：同一 voxel/网格 cell 内多个 proposal 的冲突率；
- exclusion success：competition 后被成功移除的冲突 proposal 比例；
- new support acceptance：新增 token/voxel 中通过 projection 的比例；
- frontier compactness：frontier voxel 与 occupied voxel 的接触边数。

### 5.4 Fractal / scale metrics

谨慎使用：

- box-counting dimension：只用于同一 voxel resolution、同一 bbox normalization、同一 depth 的横向比较；
- log token/vertex growth slope：`log N(d)` vs `d`；
- transform self-similarity error：把子结构按 grammar inverse transform 对齐到 root/motif 后的 Chamfer/occupancy IoU；
- zoom consistency：相邻 zoom panel 的 DINO/LPIPS/occupancy 相似度。

注意：branching structure 不一定满足严格 self-similarity。Cheeseman and Vrscay `cheeseman2022fractalCaution` 已指出 branching fractal dimension 的解释风险；论文中应把 fractal dimension 放在 appendix 或辅助指标，不能作为主结论。

### 5.5 Minkowski / Euler / topology metrics

对 voxelized occupancy 计算：

- volume / voxel count；
- surface area proxy；
- mean curvature proxy，如工具可用；
- Euler characteristic；
- cavity/void count proxy；
- connected components / tunnels proxy。

适用：

- DLA/coral/porous/crystal；
- projection 是否保留孔洞/内腔；
- non-manifold mesh 不稳定时，用 voxel occupancy 上的 topology metric 代替 mesh genus。

参考：Minkowski functionals 可用于 2D/3D binary image 的体积、面积/边界、Euler-Poincare characteristic 等几何拓扑量；当前 bib 有 `martinez2018minkowskiPorosity`，可再补更通用的 binary image 计算引用。

### 5.6 Symmetry / equivariance error

适用 radial4、mirror、crystal、portal-like transform-copy：

设 group action `g in G`，occupancy `O`，render feature `f`。

- occupancy equivariance error：

```text
E_occ(g) = 1 - IoU(g(O), O)
```

- geometry equivariance error：

```text
E_chamfer(g) = Chamfer(g(P), P)
```

- render equivariance error：

```text
E_render(g) = || DINO(render(g(mesh))) - DINO(g(render(mesh))) ||
```

注意：portal/scale-down 不是严格 symmetry，不能报 invariant error；只能报 transform consistency。

### 5.7 Renderability / PBR channel success

每个 GLB 必须有表：

- GLB export success：yes/no；
- Blender import success：yes/no；
- visible material assignment：yes/no；
- base color valid：非空、非 NaN、非全常数；
- roughness valid：范围在 `[0,1]` 或可 clamp；
- metallic valid：范围在 `[0,1]` 或可 clamp；
- opacity/alpha valid：存在时可解释；
- texture resolution；
- missing texture count；
- render warning count；
- neutral-vs-textured structure readability label。

主指标建议：

- GLB success rate；
- PBR channel success rate；
- fixed-render failure rate；
- human binary QA：usable / not usable / hides structure。

### 5.8 Multi-view CLIP / DINO metrics

用途：

- 多视图 render 与 category prompt / root guide 的语义一致性；
- textured root 与 final asset 的 appearance drift；
- zoom panel 或 transform panel 的视觉一致性。

协议：

- 每个 mesh 固定 `iso/front/side/top/detail` 5 个 view；
- CLIP：image-text score 用于 category/prompt alignment；
- DINO/DINOv2：image-image feature distance 用于 root/final 或 zoom consistency；
- 报 mean、min、std，而不是只报最高视角。

不要过度使用：

- CLIP/DINO 不是 3D topology metric；
- 对几何孔洞、component、collision 不敏感；
- 只能作为视觉语义辅助指标，主结构 claim 仍靠 geometry/occupancy/branch metrics。

## 6. Space Competition 主实验

### 6.1 固定算法定义

将 `compete` 固定为可描述算法：

```text
Input: state S_d, frontier/tip set T_d, attractor field A, occupancy O_d, rule proposals R
1. Extract frontier and active tips from grammar trace or occupancy boundary.
2. For each tip, sample K proposal directions from rule prior and attractor direction.
3. Convert each proposal to candidate sparse support / branch segment.
4. Score proposal:
   score = w_a * attractor_gain
         + w_f * forward_continuity
         - w_c * collision_penalty
         - w_o * out_of_bounds_penalty
         - w_k * curvature_penalty
5. Resolve competition per voxel/local cell: keep max-score proposal or soft top-k.
6. Sparse merge accepted proposals into S_d.
7. Apply masked weak naturalization only on new/boundary support.
8. Project/prune per depth, re-encode, update trace/cache.
Output: S_{d+1}, mesh, trace, metrics
```

### 6.2 对比对象

必须三方同台：

1. Traditional space colonization：显式 attractor/tip 算法，输出 skeleton+tube mesh。
2. Direct sparse grammar：同样的 tips/proposals，但不做 competition/projection。
3. Proposed sparse competition + projection：完整方法。

可选第四方：

- Final-only projection：证明“每步稳定”优于“最后补救”。

### 6.3 Case 选择

必须跑：

- vine/root：`vine_d5_projected_compete` 对应主线，depth `0..5`；
- tree/bush：`tree_projected_compete`，depth `0..3`；
- root/branch traditional：传统 L-system/space-colonization scaffold；
- non-organic：`transform_portal_d3` 或 `transform_radial4_d3`，证明 competition 不是只对植物有效。

建议跑：

- DLA/coral stress-test：只作为 appendix/stress；
- lattice/ornament：若 symmetry error 和 render 足够好，作为第二类主结果。

### 6.4 曲线和表格

主曲线：

- depth vs largest component ratio；
- depth vs component count；
- depth vs accepted proposal ratio；
- depth vs collision violation；
- depth vs branch/tip count；
- depth vs occupancy coverage；
- depth vs renderability status。

主表格：

| Case | Method | D | LCR up | components down | collision down | tip coverage up | GLB | Notes |
|---|---|---:|---:|---:|---:|---:|---|---|

其中 `LCR` 是 largest-component ratio。表格中必须同时放传统 space colonization、direct grammar、final-only projection、proposed。

图形布局：

- 一行四列：traditional / direct / final-only / proposed；
- 每列下面放 depth curve 小图；
- 右侧放一张 method score table；
- 不把 DLA stress-test 放在主图第一行，避免视觉弱项拖垮主叙事。

### 6.5 成功标准

强成功：

- Proposed 在 vine/tree 上 LCR 保持 `>0.95`，component 数随 depth 不爆炸；
- branch/tip 数按规则增长，不被 full repair 抹掉；
- collision violation 低于 direct grammar；
- neutral render 可读，至少 4 个 case 有 GLB/PBR 成功。

弱成功：

- 几何稳定显著优于 direct/final-only，但 texture/PBR 只作为 compatibility table。

失败但有价值：

- full flow repair 视觉更平滑但 branch metrics 明显下降；
- one-shot 视觉好但 recursion metric 差。这正好支撑本文问题定义。

## 7. Texture / PBR 实验

### 7.1 两条输入路线

路线 A：高质量 textured root。

```text
textured root mesh/GLB
-> O-Voxel/shape SLAT encode
-> recursive geometry growth
-> projected final mesh
-> Trellis2 texture SLAT / PBR decode
-> GLB render
```

优点：root appearance 明确，适合 appearance preservation。
风险：root mesh 许可证和材质通道质量要记录。

路线 B：SD3.5 guide image。

```text
SD3.5 guide image
-> Trellis2 root mesh
-> recursive geometry growth
-> Trellis2 texture/PBR export conditioned by guide/root render
-> GLB render
```

优点：可快速做多类别视觉。
风险：guide image 与最终结构可能语义不一致；需要记录 prompt、seed、model card citation。

### 7.2 传统方法 vs 生成方法如何比较

传统方法：

- geometry：IFS/L-system/space-colonization/DLA/shape grammar；
- texture：procedural material、simple UV/noise、category color；
- output：OBJ + optional GLB with simple material。

生成方法：

- geometry：one-shot/direct/final-only/full-flow/masked/proposed；
- texture：Trellis2 PBR export；
- output：GLB + same Blender render。

公平比较：

- 主图不要把传统 procedural texture 的弱项当成方法胜利；传统 baseline 主要回答 structure control。
- Texture/PBR 表只比较 asset renderability，不用于证明递归结构。
- 如果 PBR 成功率低，改成“texture compatibility”小表，不阻塞 geometry paper story。

### 7.3 不该过度使用的指标

- 不把 CLIPScore 当作几何指标；
- 不用单视角 CLIP/DINO 证明 3D 一致性；
- 不用 LPIPS/CLIP 奖励 texture 噪声；
- 不用人类偏好替代 component/collision/branch metric；
- 不用 PBR 成功掩盖 holes、floating fragments、collapsed branch。

## 8. Related evaluation and citation status

已在 `references.bib` 中可直接引用：

- L-system / plant grammar：`lindenmayer1968lsystemsI`, `prusinkiewicz1990abop`
- IFS/fractal：`barnsley1988fractalsEverywhere`
- Space colonization：`runions2007spacecolonization`
- DLA：`witten1981dla`, `sander2000dlaReview`
- TRELLIS / TRELLIS.2：`trellis2024`, `trellis2project`
- PBR 3D generation：`assetgen2024`, `hunyuan3d2025`
- SD3/SD3.5：`stableDiffusion3`, `stableDiffusion35ModelCard`
- 3D generation baseline：`shapE2023`, `objaverse2023`, `objaverseXL2023`
- Training-free / editing contrast：`sdeedit2021`, `flowedit2024`, `nano3d2025`, `voxhammer2025`, `latte3d2025`, `inpaintslat2025`
- Topology/fractal caution：`martinez2018minkowskiPorosity`, `cheeseman2022fractalCaution`

建议补 bib 或文中标“待核验”的来源：

- Hutchinson IFS formalism：用于 IFS coverage proof；
- Stiny and Gips shape grammar 1972：用于 shape grammar 起源；
- Muller et al. 2006 Procedural Modeling of Buildings / CGA shape grammar，DOI `10.1145/1141911.1141931`；
- CLIP / CLIPScore：用于 multi-view image-text 辅助指标；
- DINOv2 或项目实际使用的 DINOv3 model card/paper：用于 multi-view image-image feature consistency；
- 通用 3D binary image Minkowski functional computation，如 Ohser/Schladitz 类引用，需核验后补。

Web/arXiv 查证要点：

- Runions et al. space colonization 官方 Algorithmic Botany 页面确认 Eurographics Workshop on Natural Phenomena 2007, pp. 63-70。
- Witten and Sander DLA APS 页面确认 Phys. Rev. Lett. 47, 1400, DOI `10.1103/PhysRevLett.47.1400`。
- TRELLIS.2 官方页面确认 O-Voxel、PBR 通道和 4B image-to-3D model；arXiv `2512.14692` 确认 title/authors/abstract。
- AssetGen arXiv `2407.02445` 明确 PBR material 输出，适合作为 PBR evaluation 相关工作。
- DINOv2 arXiv `2304.07193` 和 CLIPScore arXiv `2104.08718` 只支撑视觉特征/语义辅助，不支撑 topology claim。

## 9. 优先级最高的 10 个实验 / 表格 / 图

1. **Space Competition main table**：vine/tree/root/non-organic 四类，traditional space colonization vs direct grammar vs final-only projection vs proposed。
2. **Depth stability curves**：每个 case 的 `component_count`、`largest_component_vertex_ratio`、`fragmentation_score` 随 depth 变化。
3. **Projection ablation figure**：raw direct -> final-only -> per-depth projection 的同相机 render + component stats。
4. **Branch/tip/angle table**：L-system、space colonization、proposed tree/vine 的 tip count、branch angle distribution、tip coverage。
5. **Occupancy/collision table**：proposal 数、accepted ratio、collision violation、occupancy coverage、projection survival。
6. **Traditional baseline render row**：IFS、L-system、space colonization、DLA、shape grammar 全部转 OBJ/GLB/Blender render，证明 baseline 公平。
7. **Generative baseline render row**：one-shot Trellis2、image-entry recursion、direct、full flow、masked weak blend、proposed。
8. **Texture/PBR success table**：每个 selected case 的 GLB export/import、base color、roughness、metallic、opacity、render warning、usable label。
9. **Multiscale / infinite-zoom proxy panel**：scale-down/portal case 的 zoom levels、cache/token budget、self-similarity error。
10. **Symmetry/transform consistency appendix**：radial4/mirror/portal 的 occupancy equivariance 或 transform consistency error，避免过度主张。

## 10. 最小可执行落地顺序

第一天只做能直接改变论文说服力的事：

1. 复用 `mesh_quality_metrics.py` 生成所有已有 candidate 的 component/depth 表。
2. 给 `procedural_baselines.py` 增补或另开脚本生成 traditional space colonization 和 simple shape grammar，但这一步由实验 worker 执行，不在本文档中改代码。
3. 对 vine/tree 的 direct、final-only、projected compete 生成同相机 render row。
4. 做 Space Competition 主表和 depth curves。
5. Texture/PBR 只先做 4 个 head assets 的 success table；不要等待 30+ 全部 GLB 成功。

论文主文优先放：

- Space Competition 主实验；
- projection stability；
- traditional/generative baseline matrix；
- texture/PBR compatibility as asset-readiness evidence。

Appendix 放：

- fractal/box-counting；
- Minkowski/Euler topology；
- CLIP/DINO multi-view；
- failure cases and GLB failure table。
