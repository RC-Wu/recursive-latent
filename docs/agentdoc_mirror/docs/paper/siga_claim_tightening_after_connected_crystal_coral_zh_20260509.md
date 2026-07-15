# SIGA 主文 Claim 收紧建议：connected crystal / coral 之后

日期：2026-05-09  
范围：基于当前 AgentDoc plan、`paper_siga/main.tex`、`docs/paper` 与 `docs/evaluation` 下 2026-05-09 最新中文文档，整理 SIGA 主文中现在可以 defend 的 claim、必须降级的 claim、以及下一步需要实验闭环的 claim。本文只做论文论证边界整理，不修改 `main.tex`，不触碰远端，不改图片。

## 0. 总体判断

现在最稳的 SIGA 主线不是“一个通用系统已经解决所有递归 3D 资产”，而是：

> PS-RSLG 把递归程序写成 generation-model-native 的 sparse latent grammar，并把 connected projection 放进每一层 transition；在保守增长和若干 connected scaffold 家族上，这能把 root-attached / occupancy-connected support 变成有限深度递归状态的不变量。Trellis2 textured GLB 是 selected projected mesh 的资产化兼容性证据，不是拓扑或物理生长证明。

这条主线已经可以 defend，但必须把 claim 分层：

- 方法 claim：PS-RSLG 是递归稀疏状态语言，而不是“procedural + Trellis2 + cleanup”的流水线。
- 稳定性 claim：per-depth projection 是递归 transition 的一部分，优于 direct recursion 和 final-only cleanup，证据目前最强在 conservative `compete` vine/tree。
- 非树扩展 claim：pyrite / bismuth / coral 是 connected crystal-like 或 coral/DLA-inspired scaffold，证明语言可覆盖非树形 family 与 PBR export。
- 资产化 claim：selected projected meshes 可进入 Trellis2 texture/PBR route 并生成可检查 GLB。
- 不能扩张成：真实 DLA、真实晶体生长、严格拓扑干净 mesh、通用无限递归、所有 operator family 都已解决。

## 1. 现在可以在 SIGA 主文 defend 的 claim

### 1.1 PS-RSLG 方法故事

可以 defend：

- 论文可以明确使用 **Projection-Stabilized Recursive Sparse-Latent Grammar (PS-RSLG)** 作为方法名。
- PS-RSLG 的核心不是把 mesh 生成器当后处理器，而是把 Trellis2 的 sparse O-Voxel / SLAT-like state 当作递归程序执行的状态空间。
- Grammar 拥有 global recursive structure：typed handles、anchors、frontiers、transforms、attachment certificates、projection parameters、material handles 和 caches。
- Frozen Trellis2 只提供 representation、decode/re-encode、masked local naturalization、selected texture/PBR export；它不拥有全局递归拓扑。
- Classical systems 的覆盖可以作为 semantic limit：IFS、L-system、space colonization、DLA/frontier、shape grammar、symmetry/lattice 都可写成受限 rule templates，但这只是表达力和 baseline 统一，不是说当前实现视觉上胜过成熟 procedural 系统。

主文建议写法：

> We formulate recursive asset synthesis as a generation-model-native sparse-latent grammar. The grammar controls handles, transforms, frontiers, attachment, and projection, while the frozen 3D generator supplies sparse representation, masked local realization, decoding, re-encoding, and selected appearance export.

必须避免：

- 不要把方法写成 `root mesh -> Trellis2 -> sparse edit -> cleanup -> texture`。
- 不要在主文塞过大的 state tuple；保留 compact state `z_d=(V_d,F_d,A_d)`，把 masks、seeds、caches、material metadata 放执行器或 appendix。
- 不要把 masked sampler 写成全局 repair；它是 local naturalization。

### 1.2 Per-depth projection

可以 defend：

- Per-depth projection 是当前论文最强因果 claim。
- direct recursion 会让 fragments 在中间层成为 parent/frontier/cache/material source。
- final-only projection 能清最终 mesh，但不能阻止中间错误传播。
- per-depth projection 把 decoded asset 投影回 admissible connected state，再 re-encode，因而是 recursive invariant。
- projection ablation 数值可主文保留：
  - `vine compete d3`: direct `2059` comps / LCR `0.9049`，final-only `2` / `0.9934`，per-depth kept `1` / `1.0000`。
  - `tree compete d3`: direct `3201` comps / LCR `0.9169`，final-only `4` / `0.9842`，per-depth kept `2` / `0.9949`。

主文建议写法：

> On conservative competition programs, placing projection inside the recursive transition substantially reduces fragment propagation compared with direct recursion and final-only cleanup. This supports connected support as a per-depth execution invariant, not a post-hoc mesh target.

必须附带 caveat：

- 这是 conservative `compete` 线最强，不覆盖 `compete_fork`、radial、hard-DLA、cache repair。
- 表中 component / LCR 是 raw mesh diagnostic；跨 OBJ/GLB 比较时 primary connectivity 应用 occupancy / surface-voxel proxy。
- expressive fork cases 是 stability-expression boundary，不是成功结果。

### 1.3 Grammar-native connected scaffold

可以 defend：

- connectedness 现在应写成 grammar-native / attachment-aware scaffold claim。
- 当前结果支持“先在 grammar support 中保持连接，再 texture/export”，而不是“碎了以后靠 bridge/cache/texture 修好”。
- DLA bridge rerun 已经说明 post-hoc repair 可能让 face metric 变好但 occupancy support 变差；这反而支持 grammar-native connected scaffold。
- coral rerun 1640 和 crystal surface-voxel QA 使 non-tree connected scaffold 可以作为正面证据，但必须是 scaffold claim。

主文建议写法：

> For non-tree families, we use grammar-native connected scaffolds rather than post-hoc repair. The connected coral and crystal-like examples demonstrate that the same recursive sparse-latent execution can maintain coarse support connectivity beyond vine/tree programs.

必须避免：

- 不要说 “DLA solved”。
- 不要说 “bridge projection is a general topology repair”。
- 不要用 beauty render 替代 connectivity table。

### 1.4 Bismuth / pyrite crystal-like depth sequence

可以 defend：

- Pyrite lattice 是当前最强 crystal/symmetry positive case。
- Pyrite HQ depth 在 surface-sampled voxel metric 下 stage 1-4 strict r0 都是 `1 comp, LCR=1.000`，比旧 raw face component 更适合作主文支持。
- Pyrite 的 lattice / orbit 语义可读，可支撑 group-orbit / lattice grammar 小节。
- Bismuth hopper 在结构连通性上也强，cross-guide rerun 1755 用同一 bismuth scaffold 换 pyrite guide 后 stage 1-4 surface metrics 全部 `1 comp, LCR=1.000`，可用作 material guide sensitivity 或 mineral-like scaffold 支撑。
- Bismuth 不应取代 pyrite 做主晶体强图，因为外观仍不如 pyrite 稳定。

主文建议写法：

> We report pyrite-like lattice and bismuth-like stepped scaffold examples as crystal-inspired recursive scaffolds. They demonstrate group/lattice-style rule execution and PBR export compatibility under connected support diagnostics, but not physical crystallization.

必须避免：

- 不要写真实 pyrite / bismuth crystal growth。
- 不要说 Trellis2 保证 symmetry/equivariance。
- 不要把 symmetry/orbit IoU 写成 theorem；它只是 screening / supplement metric。
- 不要隐藏 raw GLB face fragmentation caveat。

### 1.5 Coral / DLA-inspired sequence

可以 defend：

- Coral depth rerun 1640 比早先版本强：四个 stage 在 surface-voxel strict diagnostic 下都是 `1 comp, LCR=1.000`。
- 这可以作为 non-tree / coral-DLA-inspired connected scaffold 的正面 method-behavior evidence。
- Coral density endpoint sweep 可以作为 qualitative parameter control：固定 stage、guide、texture schedule、renderer、camera，只改 density / compactness。
- Coral stage 4 guide sweep只能是 material / appearance guide control，不是 geometry ablation。

主文建议写法：

> The coral/DLA-inspired sequence is a connected scaffold stress case. It shows finite-depth recursive enrichment under fixed conditions, not a physical DLA simulation or a calibrated coral growth model.

必须避免：

- 不要写 random-walk hitting distribution 已被实现为视觉上 faithful 的 DLA。
- 不要叫 depth / density 图 “ablation”。
- 不要说 density 响应严格单调。

### 1.6 Mesh / textured GLB 可视化规则

可以 defend：

- 主文和用户可见 qualitative evidence 必须是 mesh render 或 textured-mesh render。
- Point cloud、matplotlib scatter、occupancy debug preview 只允许内部诊断，不应进主文正例。
- 绿色 / 蓝色 / 灰色 protocol separation 是合理的：true Trellis2 GLB、programmatic PBR、neutral mesh render 必须在 caption 中区分。
- Textured GLB export 支持 asset-readiness：GLB import/render、PBR route、material guide compatibility。
- Textured GLB 不支持 topology-clean claim；raw face components 和 UV/material seams 要单独作为 diagnostic。
- Surface-sampled voxel connectivity 是 GLB export 后更合理的 visual-support proxy，但仍不是 watertight topology proof。

主文建议写法：

> We separate structural connectivity from texture/export diagnostics. Occupancy and surface-voxel metrics support connected scaffold claims; raw face components, material seams, and GLB import/render status are reported as export diagnostics.

## 2. 必须降级的 claim

### 2.1 “PS-RSLG 全面解决递归 3D 生成”

必须降级为：

- finite-depth recursive asset generation；
- selected operator families；
- selected projected meshes；
- training-free framework with current stability boundary。

原因：

- aggressive fork、radial、echo、hard-DLA、cache-selected repair 仍有 fragment、blocky slab、semantic collapse 或 surface soup。
- infinite recursion 仍只是 finite active window / cache descriptor 的方法扩展，没有完整主文实验闭环。

### 2.2 “per-depth projection 对所有 operator 都有效”

必须降级为：

- conservative competition programs 下有效；
- expressive fork 是边界；
- bridge / cache / radial / DLA 需要单独 stress analysis。

证据：

- `vine compete-fork d3`: direct `11490` comps，per-depth LCR 仍 `0.5758`。
- `tree compete-fork d3`: direct `12166` comps，per-depth LCR 仍 `0.6141`。

### 2.3 “传统 baseline 结构失败，所以我们赢”

必须降级为：

- traditional L-system / space-colonization 是 strong structural baseline；
- matched structural matrix 是 fairness sanity check，不是 connectivity victory；
- proposed 的核心优势应放在 generated sparse-latent recursive execution、projection placement、selected texture/PBR asset readiness、non-tree scaffold language 上。

证据：

- 传统 baseline texture rerun 1554 中 `sc_tree_canopy` strict `1 / 1.000`；`sc_root_vine`、`lsystem_branch` strict 近单连通，radius-1 单连通。
- DLA-like procedural cluster 虽然 metric 近连通，但视觉块状；这只能说明 visual/semantic asset readiness 需要额外评估，不能反推传统方法都弱。

### 2.4 “DLA bridge/cache 修复成功”

必须降级为：

- negative / stress / boundary result；
- post-hoc bridge 或 cache repair 可以暴露 metric tradeoff，但不是主路线。

证据：

- hard-DLA raw: occupancy `4`, LCR `0.380`；sparse bridge 后 occupancy `5`, LCR `0.591`，support 仍碎。
- volumetric-DLA raw: occupancy `1`, LCR `1.000`；sparse bridge 后 occupancy 变 `7`, LCR `0.873`，说明 over-bridge 可损伤 support。
- cache-selected rerun 1516 中 DLA/radial/scifi 在 radius-1 surface metric 下可接近连通，但视觉偏 blocky monolith，语义弱；bismuth cache fusion 失败。

### 2.5 “crystal / coral 是物理模拟”

必须降级为：

- crystal-inspired / mineral-inspired / lattice scaffold；
- coral/DLA-inspired connected scaffold；
- grammar coverage includes DLA/frontier limit，但当前视觉实验不是 faithful physical simulation。

### 2.6 “textured GLB 证明 topology clean”

必须降级为：

- textured GLB 证明 selected projected mesh 可以进入 Trellis2 texture/PBR export；
- topology / connectedness 要看 occupancy-primary、surface-voxel、root reachability、mesh diagnostic 和视觉 zoom。

原因：

- raw face components 对 GLB UV/material seams 过敏。
- vertex occupancy 对 textured GLB seam 也可能过于悲观。
- surface-sampled voxel metric 更适合 renderability connectivity，但仍非 watertight mesh proof。

## 3. 需要下一步实验闭环的 claim

### 3.1 Tree/root/vine matched projection matrix

需要闭环的 claim：

> PS-RSLG per-depth projection 在 tree/root/vine 的 same-root / same-seed / same-depth 条件下稳定优于 direct sparse grammar 和 final-only cleanup。

最小闭环：

- cases：`tree`, `root`, `vine`。
- methods：traditional L-system、traditional space-colonization、direct sparse grammar、final-only projection、prune-per-depth、bridge-per-depth、proposed per-depth。
- outputs：每 depth mesh/GLB、neutral mesh strip、root/junction/tip zoom。
- metrics：`Comp_6n`, `LCR_occ`, `root_component_ratio`, `orphan_mass_ratio`, `path_to_root_rate`, projection survival, bridge mass, mesh component diagnostic。

主文现在可以先用已有 conservative projection ablation，但 reviewer 很可能追问 root/vine/tree 是否都 matched。

### 3.2 Root / branch / tip 真实结构指标

需要闭环的 claim：

> 递归程序不仅 occupancy connected，还保持 root-attached branching semantics。

最小闭环：

- 不只用 mesh_voxel_proxy 的 tips / branch nodes。
- 对 traditional skeleton 与 proposed voxelized scaffold 给出可比的 root path / orphan tip / branch endpoint proxy。
- 对主图提供 root attachment zoom、primary junction zoom、terminal tip zoom。

否则只能写 support connected，不能写完整 branch topology clean。

### 3.3 DLA / coral stress matrix

需要闭环的 claim：

> grammar-native connected scaffold 是 DLA/coral-like non-tree family 的可靠路线。

最小闭环：

- methods：direct frontier、final-only cleanup、prune-per-depth、bridge-per-depth、grammar-native connected scaffold。
- cases：hard-DLA、volumetric coral、porous scaffold。
- metrics：component growth、root ratio、bridge added voxels、bridge length、face/surface fragmentation。
- visuals：neutral mesh stages + bridge / fake strut zoom。

主文当前可以用 coral rerun 1640 做 positive scaffold，用 hard-DLA bridge rerun 做 negative diagnostic；不能说 DLA family 已完全闭环。

### 3.4 Crystal / lattice symmetry closure

需要闭环的 claim：

> group/lattice rule 不仅看起来像晶体，还在 symmetry/orbit metric 上可测。

最小闭环：

- pyrite / bismuth / IFS-lattice / direct sparse / final-only / proposed scaffold。
- symmetry/orbit error、occupancy connectedness、facet/contact zoom、fixed-camera depth strip。
- 明确 symmetry metric 是 approximate screening，不是 strict equivariance。

主文现在可用 pyrite lattice + surface-voxel connected + supplement symmetry IoU；如果要把 symmetry 写成更强贡献，需要补齐 matched lattice baseline。

### 3.5 Cache / LOD / infinite recursion

需要闭环的 claim：

> cache / latent / LOD 可支持 finite-memory infinite logical recursion。

当前只能写：

- cache 是 method extension；
- island_city_lod256 或 selected cache smoke 表明 token budget / reuse 方向有潜力；
- cache repair 尚不能作为主文 positive visual。

最小闭环：

- visible-window depth sweep；
- active token budget 曲线；
- cache hit / reuse / projection survival；
- same-window zoom consistency；
- 至少一个视觉非 blocky、语义清楚的 mesh/textured-mesh result。

否则不要在 abstract 或 contribution 中把 infinite recursion 写成已验证贡献。

### 3.6 Texture/PBR 与 structural closure 的 matched export

需要闭环的 claim：

> projection-stabilized geometry 比传统结构更适合进入 selected Trellis2 texture/PBR asset route。

当前只能写：

- 传统 baseline 也能 texture，说明比较公平；
- selected PS-RSLG connected scaffolds 也能 texture，说明 pipeline compatible。

最小闭环：

- 从同一 structural matrix 选择 traditional 和 proposed final-depth mesh；
- same guide / same texture schedule / same camera；
- 报 GLB import/render、surface-voxel connectivity、raw face diagnostic、visual QA；
- 不把 texture route 当 topology repair。

## 4. 建议的主文 claim 分配

### Abstract

应保留：

- training-free recursive sparse-latent grammar；
- projection inside recursive transition；
- finite-depth connected support；
- selected textured GLB export。

应删除或降级：

- “supports all recursive families”；
- “DLA/crystal growth solved”；
- “infinite recursion”；
- “topology-clean textured meshes”。

### Introduction / Contributions

推荐贡献顺序：

1. PS-RSLG：generation-model-native recursive language over sparse 3D latents。
2. Per-depth projection：connected support as recursive invariant。
3. Rule-template semantics：growth、frontier、transform-copy、lattice、material/cache hooks。
4. Evidence：projection ablation、connected vine/tree/coral/crystal scaffold、traditional baseline fairness、selected Trellis2 texture/PBR export。

不要把 texture/PBR 放在 projection 之前，否则 reviewer 会以为论文核心是美化资产。

### Method

应收紧：

- State 保持 compact。
- Rule template 强调 handle-to-proposal，不是 mesh macro。
- Naturalization 是 masked local prior。
- Projection 是 transition 内部的 admissible-state projection。
- Classical coverage 放 concise main-text + appendix proof sketch。
- Cache/infinite recursion 写成 finite active window extension。

### Experiments / Results

建议顺序：

1. Metrics and protocol separation。
2. Projection ablation。
3. Matched structural baseline fairness。
4. Selected connected scaffold + texture/PBR export。
5. Same-condition method behavior。
6. Boundary / negative cases。

这一顺序能直接回应 reviewer：不是先给 gallery，再倒推方法；而是先给 claim-aligned metric 和 ablation，再给视觉资产。

## 5. Reviewer 可能质疑与应答策略

### Q1: 这不就是 procedural grammar 加 Trellis2 后处理吗？

应答：

- PS-RSLG 在 sparse latent state 内执行 rule proposal、masked merge、attachment feasibility、projection、re-encode。
- Trellis2 不是最后修图；decode / projection / re-encode 在每层 recursion 中参与 state transition。
- final-only cleanup 的失败正是关键对照。

### Q2: 传统 L-system / space-colonization 本来就连通，你们的优势在哪里？

应答：

- 承认传统 structural baseline 强。
- 我们不把传统 baseline 写成 strawman。
- 核心比较是 generated sparse-latent recursive execution 中 direct / final-only / per-depth projection 的稳定性，以及 selected projected mesh 进入 texture/PBR asset route 的兼容性。

### Q3: DLA / crystal / coral 是否真实物理模型？

应答：

- 不是。
- 主文称为 DLA-inspired、coral-inspired、crystal-like、lattice scaffold。
- Grammar coverage 中可表达 DLA/frontier limit，但当前视觉实验是 connected scaffold stress test。

### Q4: GLB raw face components 很高，为什么还能说连通？

应答：

- raw face components 是 export/UV/material seam diagnostic。
- 主结构 claim 使用 occupancy 6N 或 surface-sampled voxel connectivity，并配合 fixed-camera render / zoom QA。
- 论文明确不宣称 watertight topology。

### Q5: Same-condition depth / parameter 图是不是 cherry-pick？

应答：

- 将其定位为 method-behavior visualization，不叫 ablation。
- 每行固定 family、guide、camera、renderer、texture schedule，只改变 depth 或单一 grammar parameter。
- 主 ablation 仍是 projection direct/final-only/per-depth。

## 6. 推荐保留、降级、移补充的图表

### 主文应保留

- Method overview：突出 grammar handle、proposal、competition/projection、masked Trellis2 naturalization、decode/re-encode。
- Projection ablation：`projection_ablation_mesh_contact_20260509` + `tab:projection-ablation`。
- Claim-aligned metric summary：解释 occupancy primary / face diagnostic 分层。
- Traditional baseline texture rerun 1554：作为公平 baseline 和 protocol separation。
- Pyrite HQ depth / crystal case：当前最强 non-tree lattice scaffold。
- Coral depth rerun 1640：connected coral/DLA-inspired scaffold positive。
- DLA bridge smoke rerun：boundary / negative diagnostic。

### 主文可选，版面紧张时移 supplement

- full result matrix；
- depth_parameter full gallery；
- bismuth cross-guide depth；
- coral density extreme；
- vine guide sweep。

### 应移 supplement 或 appendix

- cache-selected texture smoke；
- older matched-guide texture diagnostic；
- raw face component 大表；
- symmetry/orbit screening metric；
- branch/path proxy 全表；
- cache / LOD / infinite recursion proof-of-concept。

## 7. 五个最高优先级论文修改建议

1. **把主文 claim map 收窄到一句话**：PS-RSLG 的核心是 per-depth projected sparse-latent recursion；selected texture/PBR 是资产化兼容性，不是 topology proof。
2. **重排 Results**：先 metrics/protocol separation，再 projection ablation，再 baseline fairness，再 connected crystal/coral/vine positive，最后放 boundary cases；不要先用 gallery 开场。
3. **把 traditional baseline 写强**：承认 L-system / space-colonization 在结构连通性上很强，把比较焦点转到 projection placement、生成式 sparse latent execution、selected GLB export。
4. **统一 non-tree 命名**：全部写成 `crystal-like / lattice-inspired / coral-DLA-inspired connected scaffold`，禁止写真实晶体生长、真实 DLA、物理 coral。
5. **每张 texture 图都加 metric caveat**：caption 中说明 true textured GLB / programmatic PBR / neutral mesh 的协议，并明确 occupancy/surface-voxel 支持 connected scaffold，raw face components 只是 export diagnostic。

## 8. 可直接贴入主文的保守句子

> Our strongest claim is not that every recursive operator produces a clean watertight asset, but that connected support must be enforced inside the sparse-latent recursive transition. Final-only cleanup can improve the terminal mesh, but it cannot prevent intermediate fragments from becoming active handles, frontiers, cache entries, or material sources.

> Classical procedural baselines are strong structural controls under favorable tube-occupancy protocols. We therefore use them as fairness baselines rather than strawmen, and evaluate our design claim through direct, final-only, and per-depth projection variants of recursive sparse-latent execution.

> Crystal and coral examples are reported as connected scaffold families. They demonstrate group/lattice-style and coral/DLA-inspired recursive supports with selected PBR export, not physical crystallization, faithful DLA simulation, or watertight topology.

> Textured GLB export is evaluated separately from structural connectivity. Surface-sampled voxel connectivity and fixed-camera mesh renders support connected-scaffold claims, while raw face components and material seams remain export diagnostics.

