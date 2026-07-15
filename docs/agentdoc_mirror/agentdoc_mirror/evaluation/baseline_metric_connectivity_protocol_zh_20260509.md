# Baseline / Metric / Connectivity 闭环协议 20260509

项目：`recursive_3d_generative_growth`  
范围：baseline、metric、连通性实验闭环文档；不修改代码与 `paper_siga/main.tex`。  
目标读者：后续实验 worker、论文实验章节作者、严格图形学 reviewer。  
核心约束：所有最终视觉证据必须来自 mesh/GLB/Blender 或等价 mesh renderer；matplotlib 点云、scatter、voxel slice 只能用于定位问题，不能作为论文主图证据。

## 0. 结论先行

当前论文实验的主线不应继续写成“纹理/PBR 已经好看，所以方法有效”。纹理和 Trellis2 true GLB export 只能证明 appearance pipeline 基本可用；最危险的问题是 **DLA、晶体、径向复制、履带/机械、树叶/根系等 case 的碎块、漂浮片和 surface fragmentation**。这些问题会让资产不可用，也会让 reviewer 质疑递归生成系统是否真正稳定。

因此下一版实验闭环必须围绕下面三个问题组织：

1. **递归状态是否每一层都连回 root/scaffold？**  
   不能只看 final mesh，也不能只做最后一次 largest-component cleanup。

2. **传统递归 baseline、生成模型 baseline 和 proposed 是否在同一 mesh/render 协议下比较？**  
   传统 baseline 不能只给 skeleton/line preview；proposed 也不能只给 textured GLB 美图。

3. **DLA/晶体碎块如何被诚实写成 ablation/失败案例？**  
   负面结果不应占据主线，但必须作为方法边界、诊断和下一轮实验驱动，尤其要解释为什么 occupancy LCR=1.0 仍可能视觉碎。

## 1. 正式任务定义

### 1.1 Structure-first recursive asset generation

输入：

- root asset：root mesh、Trellis2 image-to-3D root mesh、或传统 procedural scaffold mesh；
- grammar program：typed rules、frontier/tip/anchor selector、transform、competition/projection policy；
- depth budget：`D`，必须保存 `d=0..D` 每层中间结果；
- resource budget：token/voxel/vertex/face 上限、projection 次数、sampler steps、texture export 开关；
- optional appearance guide：类别 prompt、root render、texture/PBR guide。

输出：

- 每层 mesh/OBJ；必要时包含 raw、final-only、per-depth projected 版本；
- final GLB/PBR，仅在 geometry 过关后作为 appearance evidence；
- 固定 Blender/Cycles 或等价 mesh renderer 下的 neutral 多视角 render；
- 若有 textured GLB，再提供同相机 textured render；
- 每层 metric JSON/CSV。

评价目标：

- 结构控制：branch/tip/frontier/transform-copy/space-competition 是否按 grammar 扩展；
- 连通稳定：component count、largest attached ratio、orphan mass、frontier validity 是否随 depth 受控；
- 资产可用性：mesh 是否可加载、GLB/PBR 是否有效、neutral render 是否能读出目标结构。

### 1.2 Connectivity-first frontier / crystal / DLA stress generation

输入：

- connected root/scaffold；
- DLA/frontier/crystal/radial rule；
- bridge-aware 或 prune-only projection policy；
- fixed occupancy resolution 和 fixed render protocol。

输出：

- raw proposal、direct recursion、final-only projection、prune-per-depth、bridge-per-depth 的同 root 对照；
- DLA/晶体/radial 的 zoom-in mesh render；
- failure label：floating shard、fake bridge、surface sheet、melted tip、over-closed cavity、texture masking。

评价目标：

- 不是证明“所有 DLA/晶体都修好了”，而是明确区分：
  - 哪些 case 是真正 mesh 连通且视觉可读；
  - 哪些只是 occupancy proxy 单连通；
  - 哪些是 surface fragmentation 或假桥；
  - 哪些只能进入 ablation/failure appendix。

### 1.3 Multiscale / transform / infinite-zoom proxy

输入：

- root motif；
- contractive transform、portal、scale-down、radial group orbit 或 recursive frame；
- visible window/LOD/cache budget。

输出：

- zoom panel；
- per-level local mesh/render；
- token budget、cache hit、transform consistency 和 self-similarity proxy。

评价目标：

- 证明有限窗口内的递归细节可控，而不是声称真实无限几何；
- radial/crystal 只能在 mesh 连通和 symmetry/transform consistency 同时过关时进入主结果。

## 2. Baseline 固定

### 2.1 传统 baseline

| Baseline | 任务 | 公平输出 | 主指标 | 不能怎么写 |
|---|---|---|---|---|
| IFS / fractal transform-copy | scale-down、portal、motif recursion | transform copies -> tube/implicit/marching-cubes OBJ -> fixed render | transform consistency、box-count proxy、component | 不能用纹理缺失证明 proposed 更强 |
| L-system / turtle | tree、vine、root、leaf skeleton | turtle segments -> tapered tube OBJ + skeleton trace | tip count、branch nodes、angle/length distribution、coverage | 不能用 raw face components 惩罚 tube 未 weld |
| Space colonization | tree/root/space competition | skeleton JSON + tube OBJ + fixed render | attractor coverage、tips、branches、total length | 不能把低 occupancy LCR 直接写成结构失败 |
| DLA / frontier growth | coral、porous、crystal stress | voxels -> marching-cubes/cube mesh + fixed render | occupied voxels、components、cavities、Euler proxy | 不能作为 asset-quality 上限，只是 accretion topology baseline |
| Shape grammar / split grammar | architecture、ornament、hard-surface | split/extrude/replace -> OBJ/GLB + fixed render | rule coverage、component、renderability | 不应与植物 branch metric 混成一个分数 |

传统 baseline 的定位：它们是 **结构控制与递归规则上限**，不是 learned material/asset-quality 上限。论文中必须给 neutral geometry render 行，否则 reviewer 会认为比较协议不公平。

### 2.2 生成模型 baseline

| Baseline | 目的 | 关键失败判据 |
|---|---|---|
| One-shot Trellis2 | 测试原生 3D 生成质量和 PBR 上限 | 不能保持指定递归 depth、branch trace、portal/scale/radial relation |
| Image-entry then recursion | 测试用户只有图像入口时的路径 | root 可用但递归后碎片积累或结构丢失 |
| Direct sparse grammar | 证明 naive recursive edit 会积累碎块 | component count 超线性增长、LCR 下降、frontier 变成 orphan |
| Final-only projection | 检验最后清理是否足够 | 中间层不可用；碎块已污染 frontier/cache/history |
| Full flow repair | 检验 frozen sampler 是否能全局修复 | topology 被洗掉、branch/tip/portal 消失 |
| Masked weak blend | 检验低强度 local naturalization | 局部变自然但连通性下降，或几何塌缩 |
| Prune-only per-depth projection | 当前已有主证据之一 | 能删碎片但可能牺牲表达性，无法连接有用子结构 |
| Bridge-aware per-depth projection | 下一轮关键候选 | 若引入假桥、粗桥、过度膨胀，必须标为 negative ablation |
| Bridge + cache + hard-mask sampler | 方法目标闭环 | 目前不能写成已充分验证，需 true decode mesh 证据 |

### 2.3 必须成组比较的列

每个主 case 至少保留四列：

| Method column | 是否必须 | 说明 |
|---|---|---|
| Traditional procedural baseline | 是 | L-system/SC/DLA/IFS/shape grammar 按 case 选择 |
| Direct sparse grammar | 是 | 显示 naive recursion 的碎片积累 |
| Final-only projection | 是 | 证明最后清理不足以保证递归过程 |
| Proposed per-depth projection | 是 | 当前 conservative compete 主证据 |
| Bridge-aware per-depth | 下一轮必须 | DLA/晶体/径向碎块的关键补充 |
| Bridge + cache + hard-mask sampler | 下一轮可选强列 | 只有 true mesh/Blender 结果过关才升主文 |

## 3. Metric 体系

### 3.1 连通性主指标

主文建议以 voxel occupancy 6-neighborhood 作为 primary mesh connectivity proxy，同时保留 face diagnostics。原因：传统 tube OBJ、textured GLB 和部分 decoder 输出可能视觉接触但不共享顶点，raw face component 会误报。

必须报告：

- `occupancy_component_count_6n`
- `largest_occupancy_component_ratio_6n`
- `occupied_voxels`
- `orphan_mass_ratio`
- `component_count_by_depth`
- `component_growth_rate`
- `projection_survival_ratio`
- `frontier_validity`
- `bridge_survival_ratio`，bridge-aware 实验必须有

安全定义：

\[
\mathrm{LCR}_{\mathrm{occ}}
=
\frac{|C_{\mathrm{largest\ attached}}|}{|C|+\epsilon},
\qquad
\mathrm{Frag}=1-\mathrm{LCR}_{\mathrm{occ}}.
\]

\[
\mathrm{FrontierValidity}
=
\frac{\#\{f\in\mathcal F:f\leadsto R\}}{|\mathcal F|+\epsilon}.
\]

注意：

- before 已经 `occ comps=1, LCR=1.0` 的 DLA/leaf case，不能写成“修复连通性成功”；最多写“occupancy proxy 保持连通，但 face/render 暴露 surface fragmentation”。
- largest-component 删除法不能作为主方法，只能作为 diagnostic lower bound。

### 3.2 Face / mesh quality diagnostics

必须补充：

- `face_component_count`
- `largest_face_component_ratio`
- vertices / faces
- non-manifold edge count
- watertight / winding / degenerate face 状态
- bbox、surface area、volume proxy
- mesh import/render success

解释口径：

- occupancy 单连通但 face components 极多：这是 surface fragmentation，不是完全意义上的 topology success。
- face component 下降但几何被抹平：这是 over-smoothing 或 over-closing negative。
- bridge 后面积/体积大幅增长：需要报告代价，不能只报 component 改善。

### 3.3 多尺度与递归稳定指标

必须报告：

- depth vs `component_count`
- depth vs `LCR_occ`
- depth vs token/vertex/face count
- depth vs accepted proposal ratio
- depth vs collision/exclusion rejection
- depth vs branch/tip count
- depth vs renderability status

辅助报告：

- log token/vertex growth slope；
- box-counting dimension proxy，仅同 resolution/bbox 下比较；
- transform self-similarity error；
- zoom consistency panel + DINO/LPIPS 辅助分数。

限制：

- fractal dimension 不能作为主 claim；
- branching/root 并不一定严格自相似；
- zoom panel 必须由 mesh render 生成。

### 3.4 拓扑 / porous / crystal 指标

对 DLA/coral/porous/crystal，必须从 voxelized occupancy 计算：

- volume / occupied voxel count；
- surface area proxy；
- Euler characteristic proxy；
- cavity/void count proxy；
- tunnel/genus proxy，如果工具稳定；
- Minkowski-functionals-like descriptors；
- local contact area / face-contact ratio；
- crystal/radial 的 symmetry/equivariance error。

Radial/crystal 指标不能只报 symmetry error。必须同时报告：

- `occ comps`
- `LCR_occ`
- attached ratio
- bridge survival
- neutral render 语义可读性。

### 3.5 纹理/PBR 指标

Texture/PBR 只支撑 asset-readiness，不支撑连通性主张。必须报告：

- GLB export success；
- Blender import success；
- base color / roughness / metallic / opacity 通道是否存在且数值有效；
- texture resolution；
- missing texture count；
- render warning count；
- neutral-vs-textured structure readability label。

如果 neutral render 看不出 DLA/晶体结构，而 textured render 靠 bismuth/pyrite/coral 材质暗示类别，该结果不能作为结构主图，只能作为 texture compatibility。

### 3.6 CLIP/DINO 辅助指标

CLIP/DINO 可用于多视角语义或 root-final appearance drift，但不能证明 3D topology：

- 每个 mesh 固定 `front/side/top/iso/detail` 视角；
- 报 mean/min/std；
- 只作为 semantic auxiliary；
- 不替代 component、frontier、branch、mesh render QA。

## 4. 固定空间竞争实验流程

Space competition 应成为最稳的主实验，因为已有结果显示 conservative `compete` 能支持 projection-stabilized story，而 `compete_fork` 能展示 expression-stability boundary。

固定流程：

```text
root asset / scaffold
-> extract frontier / active tips
-> generate K grammar proposals per tip
-> score proposals by attractor gain, forward continuity, collision, exclusion, curvature, attachment
-> resolve local competition per voxel/cell
-> sparse merge accepted proposals
-> optional masked weak naturalization only on new/boundary support
-> per-depth projection or bridge-aware projection
-> decode mesh, render, metrics
-> re-encode projected state
-> continue to d+1
```

必须对照：

| Case | Traditional | Direct | Final-only | Prune-per-depth | Bridge-per-depth |
|---|---|---|---|---|---|
| vine/root conservative compete | required | required | required | required | required |
| tree/bush conservative compete | required | required | required | required | required |
| fork expression stress | optional traditional | required | required | required | required |
| DLA/porous frontier | DLA baseline required | required | required | required | required |
| radial / crystal / lattice | IFS/crystal baseline required | required | required | required | required |
| non-organic hard-surface | shape grammar baseline if possible | required | required | required | required |

主图建议：

- 一行四到五列：traditional / direct / final-only / prune-per-depth / bridge-per-depth；
- 每列用同 root、同 depth、同 camera 的 neutral mesh render；
- 图旁只放 3-4 个核心数字：`Comp_6n`、`LCR_occ`、`FaceComp`、`GLB?`；
- DLA/晶体如果仍碎，放到 ablation/failure 行，不放头图第一行。

## 5. Depth / Parameter 展示图定位

### 5.1 Depth 图

Depth 图服务的 claim：

> per-depth projection 把错误挡在当前递归层，避免 orphan fragment 进入下一层 frontier、symbol owner 和 cache。

Depth 图必须包含：

- `d=0..D` 的 mesh render strip；
- raw/direct 与 proposed 的 component/LCR 曲线；
- final-only 只能显示最终 cleanup，不得暗示中间层稳定；
- 至少一条 conservative success case 和一条 expressive boundary case。

推荐写法：

- `vine_compete` / `tree_compete`：主文正结果；
- `compete_fork`：稳定性-表达性边界；
- DLA/crystal/radial：若没有真 mesh 连通，则放 ablation 或 appendix。

### 5.2 Parameter 图

Parameter 图服务的 claim：

> method 的稳定性不是单个 lucky seed，而是受 projection threshold、bridge budget、mask radius、alpha、sampler steps 控制。

必须展示：

- projection threshold / pruning threshold；
- bridge budget / max bridge length；
- voxel closing radius；
- masked sampler alpha；
- sampler steps；
- mask dilation；
- cache/LOD resolution；
- random seed。

图形建议：

- 小 multiples：每格一个 mesh render，不用点云；
- heatmap 只作为 metric summary，旁边必须有选中参数的 mesh render；
- 不把最漂亮纹理图作为 parameter sweep 证据。

## 6. DLA / 晶体碎块如何写成 ablation / 失败案例

Reviewer 视角下，DLA/晶体碎块不能被隐藏。正确写法是把它们变成方法设计的证据：

1. **Naive frontier accretion failure**  
   DLA 在连续算法中天然通过 hitting frontier attach；但 sparse latent recursion 经过 transform、decode/re-encode 和 sampler 后，hit point 可能变成多个 disconnected voxels 或 triangle sheets。因此 direct DLA 是负 baseline。

2. **Occupancy metric insufficiency**  
   某些 DLA/textured GLB 在 occupancy 口径下 `Comp_6n=1, LCR=1.0`，但 neutral mesh render 仍像块状碎片或 surface soup。这说明 occupancy connectivity 只能作为 primary proxy，不能替代 face diagnostics 和 render QA。

3. **Prune-only limitation**  
   largest-component 或 prune-only 能删碎片，但会删除本来有用的 branch/crystal substructure。它证明 final cleanup 不够，不是最终方法。

4. **Bridge-aware projection risk**  
   bridge 能降低 component count，但可能产生假桥、粗桥、过度膨胀、闭孔、melted crystal facet。它必须作为 ablation 显示代价。

5. **Connectivity-first rule proposal**  
   下一轮 DLA/晶体必须要求每个新增 support 有 parent anchor、bridge certificate 或 face-contact invariant，否则不允许成为 active frontier。

论文位置：

- 主文 Results：只放已通过 mesh render 和 metric 的正结果；
- Ablation：放 direct / final-only / prune-only / bridge 的 DLA/晶体对比；
- Limitations：说明当前 DLA/crystal 仍是最难 case；
- Supplement：放完整失败表、zoom-in 和 seeds。

建议标签：

- `paper_safe_candidate`：metric 改善 + face/render 通过 + 语义可读；
- `diagnostic_only`：指标有信息量但视觉不足；
- `negative_ablation`：用于说明限制，例如 largest-component 删除、fake bridge、over-closing；
- `do_not_claim`：texture 掩盖结构、点云预览、occupancy 单连通但 mesh 碎。

## 7. 图形学 reviewer 视角的 claim 边界

### 7.1 当前可以支撑的 claim

可以写：

- PS-RSLG/PS-SLG 应把连通性定义为递归 sparse state invariant，而不是最终 mesh cleanup。
- Conservative space competition case 支持 per-depth projection 优于 direct recursion 和 final-only cleanup。
- Traditional space colonization 是强结构 baseline；proposed 的优势必须体现在 mesh asset、projection stability 和 texture/PBR compatibility 的组合上。
- Trellis2 true textured GLB route 已经可以作为 appearance pipeline 证据，但不是几何连通性的证据。
- DLA/leaf/textured GLB 中存在 occupancy 单连通但 surface fragmentation 的诊断现象。
- Bridge-aware projection、cache attachment certificate、hard-mask sampler 是合理方法扩展和下一轮核心实验。

### 7.2 当前还不能支撑的 claim

不能写：

- Trellis2 sampler 保证拓扑连通。
- DLA/晶体/径向复制已经被系统性修好。
- cache fusion 已在真实 decoded mesh 中解决碎块。
- radial/crystal symmetry exact。
- infinite recursion 已经实现。
- 纹理/PBR 质量证明 geometry method 成功。
- matplotlib 点云或 voxel slice 能证明 paper-quality mesh result。

### 7.3 必须靠 mesh / Blender / GLB 支撑的 claim

下列 claim 只有在固定 mesh render 协议下才成立：

- usable asset；
- connected visual structure；
- DLA/coral/crystal semantic readability；
- bridge 没有假连接；
- surface 没有 triangle soup；
- texture 没有掩盖几何失败；
- final GLB 可在标准 viewer/Blender 中加载并保留材质通道。

最低证据包：

```text
OBJ/GLB path
-> neutral Blender render, fixed camera
-> optional textured Blender render, same camera
-> zoom-in crops for junction / bridge / tip / cavity / facet
-> metric JSON/CSV
-> failure label if not paper-safe
```

## 8. 下一轮必须跑的表格

### 8.1 主闭环表：同 root / 同 depth / 同 renderer

| Case | Traditional | Direct | Final-only | Prune-per-depth | Bridge-per-depth | Bridge+cache+mask | Paper status |
|---|---|---|---|---|---|---|---|
| vine/root compete | required | required | required | required | required | optional | main positive |
| tree/bush compete | required | required | required | required | required | optional | main positive |
| fork expression | optional | required | required | required | required | optional | boundary |
| DLA/coral frontier | required | required | required | required | required | optional | stress/ablation |
| bismuth/pyrite crystal | required | required | required | required | required | optional | stress/ablation |
| radial4 symmetry | IFS/radial baseline | required | required | required | required | optional | ablation unless render-safe |
| scifi/mechanical/crawler | shape grammar if possible | required | required | required | required | optional | hard-surface stress |
| leaf/root fine structure | L-system/SC | required | required | required | required | optional | surface fragmentation check |

每格必须链接：

- mesh path；
- render path；
- metrics path；
- seed/config；
- failure label。

### 8.2 Connectivity metrics table

| Case | Method | D | Comp_6n | LCR_occ | OrphanMass | FaceComp | FaceLCR | ProjectionSurvival | BridgeSurvival | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|

规则：

- `BridgeSurvival` 只对 bridge-aware 方法填；
- before 已单连通时，verdict 不能写 `connectivity_repaired`；
- FaceComp/FaceLCR 与 render verdict 不一致时，优先做人工 zoom-in QA。

### 8.3 Space competition table

| Case | Method | Depths | Tips | Branch nodes | Coverage | Collision violation | Accepted ratio | Comp_6n | LCR_occ | GLB | Render verdict |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|

必须含 traditional SC、direct、final-only、proposed。SC 的主指标是 skeleton coverage/tips/branches，mesh occupancy 只做导出诊断。

### 8.4 Texture/PBR asset-readiness table

| Case | Geometry verdict | GLB export | Blender import | Base color | Roughness | Metallic | Opacity | Texture hides geometry? | Final use |
|---|---|---|---|---|---|---|---|---|---|

规则：

- Geometry verdict 不过关时，GLB 成功只能写 compatibility；
- neutral render 与 textured render 都必须可读，才能写 asset-ready。

### 8.5 Failure / ablation table

| Case | Failure mode | Metric symptom | Render symptom | Root cause hypothesis | Next action | Paper placement |
|---|---|---|---|---|---|---|
| DLA direct | floating shard / surface sheet | high FaceComp or low FaceLCR | chunk cloud | no bridge certificate | connected proposal + bridge | ablation |
| crystal direct | separated facets | multiple occ comps or fake LCR | isolated blocks | lattice copy lacks face contact | lattice skeleton + face-contact invariant | ablation |
| radial4 direct | orbit islands | 4 comps | four detached copies | no hub/ring connector | orbit hub bridge | ablation |
| tree/leaf | surface fragmentation | occ LCR high, FaceComp high | leaf shards / noisy sheets | decoder surface split | weld/remesh + attachment-aware surface | limitation |
| largest_component | deletion | improved LCR but low retention | missing structure | metric-only cleanup | diagnostic only | negative |
| voxel_close | over-closing | area/volume growth | melted cavities/facets | morphological bridge too broad | bridge budget + smooth | negative/appendix |

## 9. 计划修正

读取 active plan 后，发现以下旧约束或旧叙事需要在执行层修正，但本文件不修改 plan：

1. active plan 顶部仍写 `Max SSH shells: 3`、remote storage cap `70GB`；2026-05-09 连通性优先计划已更新为 shell 上限 `4`、storage cap `100GB`。后续实验 worker 应以最新连通性计划为准。

2. active plan 早期强调 head figure、texture/PBR 和多类别视觉扩展；最新用户需求已经把优先级转为 DLA/晶体/履带车/树叶/根系碎块问题。头图与 30+ 视觉矩阵应暂停抢占主线，直到连通性闭环有 mesh 证据。

3. reviewer 建议“负面结果不要作为主线展开”，但最新需求明确要求把 DLA/晶体碎块负面结果写成 ablation/失败案例。因此修正为：负面结果不放主叙事第一线，但必须进入 ablation、diagnostic、limitations 和 supplement。

4. active plan 中一些早期数值用 LCR 或 component pruning 表达“稳定”；最新 QA 说明 LCR 可能掩盖 surface fragmentation。后续所有 claim 必须同时过 `occupancy + face diagnostics + Blender render + zoom-in + semantic readability`。

5. active plan 曾把 DLA/coral/porous 视为潜在主视觉类别；当前严格口径下，DLA/晶体只有在 true mesh neutral render 可读、且 bridge/face diagnostics 过关时才能升级为主结果，否则降级为 stress test。

## 10. 最小落地顺序

1. 先补同 root、同 depth、同 renderer 的四列主表：traditional / direct / final-only / per-depth。
2. 对 DLA、crystal、radial4 加 bridge-aware per-depth 列，并记录 bridge survival 与面积/体积代价。
3. 每个候选生成 fixed-camera neutral Blender render；GLB textured render 只作为补充。
4. 对 DLA/晶体/叶片/根系加 2-3 个 zoom-in crop，标注 junction、bridge、tip、facet、cavity。
5. 把 before 已 `Comp_6n=1, LCR=1.0` 但视觉碎的 case 统一标成 surface fragmentation diagnostic。
6. 只把 `paper_safe_candidate` 放入主结果；`diagnostic_only` 和 `negative_ablation` 放入 ablation/supplement。

## 11. 一句话论文实验口径

推荐实验章节的核心表述：

> We evaluate recursive 3D generation as a per-depth mesh asset problem, not as a final image preference problem. Connectivity is measured on voxelized occupancy and checked against face-level mesh diagnostics and fixed-camera Blender renders. Traditional recursive systems are used as structure-control baselines, one-shot and repair-based generators as generative baselines, and DLA/crystal/radial fragmentation is reported as an ablation that motivates connected proposal, bridge-aware projection, and hard-mask local naturalization.
