# 连通性不变量评测协议与当前状态判断 20260509

项目：`recursive_3d_generative_growth`

写入范围：本文件只固化连通性/metric worker 的协议与状态判断；不修改 `paper_siga/main.tex`，不修改 plan 文档。

配套只读汇总表：

- `results/connectivity_status_summary_20260509/connected_scaffold_v2_source_scaffold_status.csv`
- `results/connectivity_status_summary_20260509/connected_scaffold_v2_textured_glb_case_status.csv`
- `results/connectivity_status_summary_20260509/vine_depth_status.csv`
- `results/connectivity_status_summary_20260509/cache_sampler_local_mesh_smoke_status.csv`
- `results/connectivity_status_summary_20260509/strict_category_verdicts.csv`

## 0. 直接结论

用户最新要求应被翻译为一个硬不变量：

> 对 DLA、crystal、tree、root、vine、radial、hard-surface 等递归资产，最终资产和每一层递归状态都必须保持连到 root/scaffold 的可检查 support。碎块、漂浮片、孤立晶面、孤立叶片、root orphan、靠纹理掩盖的 disconnected surface 都不可接受。

当前能严肃 claim 的范围很窄：

1. **occupancy 6-neighborhood 连通性可以作为 primary proxy**。connected scaffold v2 的 source scaffold 六个 case 都是 `occ_comp_6n=1, LCR_occ=1.0`；vine depth textured showcase 四个 stage 也是 `occ_comp_6n=1, LCR_occ=1.0`。
2. **connected scaffold v2 缓解了非 tree 类碎块问题**。`bismuth_hopper_cluster`、`pyrite_crystal_lattice_cluster`、`volumetric_dla_coral_cluster` 从规则 scaffold 层面给出了可渲染、可贴 PBR 的 connected support，比对碎片 GLB 做 post-hoc repair 更可写。
3. **GLB/PBR export 和 Blender render 成功只支持 asset-readiness / texture compatibility**。它们不能单独证明拓扑、递归稳定或真实 DLA/crystal 生长。
4. **raw face component 必须作为 caveat，而不是 primary failure metric**。textured GLB 的 raw face component count 可达数千到数万，largest vertex ratio 很低，可能来自材质分块、未 weld 面片或导出三角面分裂；它暴露 surface fragmentation 风险，但不能直接覆盖 occupancy 主指标。
5. **DLA/crystal/tree/root 还不能写成完全解决**。DLA/coral、bismuth/crystal、tree/root/vine 可以分别进入 stress-test、scaffold positive、depth-stability positive，但都需要 neutral render、zoom-in、branch/path/topology/PBR 完整指标后才能升级为主文强 claim。

一句话：**现在可以说 connected support 路线是正确方向，不能说 DLA/crystal/tree/root 的碎块问题已经系统性解决。**

## 1. 固定评测协议

### 1.1 输入

每个实验 case 必须记录：

| 字段 | 要求 |
|---|---|
| root/scaffold | root mesh、Trellis2 root mesh、procedural scaffold 或传统 baseline mesh；必须给 path |
| grammar type | `L-system/tree/root`、`space-colonization`、`DLA/frontier`、`crystal/lattice`、`radial/IFS`、`shape/hard-surface` |
| depth | 固定 `D`，保存 `d=0..D` 每层 state、mesh、metrics、render |
| seed/config | seed、frontier selector、projection threshold、bridge budget、collision/exclusion radius、sampler steps |
| projection/caching | direct、final-only、prune-per-depth、bridge-per-depth、bridge+cache+hard-mask 必须显式标记 |
| appearance | texture guide、PBR guide、texture size、GLB export settings；只在 geometry 过关后作为补充证据 |

### 1.2 Grammar 类型与最小 case 集

| 类别 | 必跑语法 | 传统 baseline | 当前论文定位 |
|---|---|---|---|
| vine/root/tree | conservative compete + branch/root grammar | L-system 或 space colonization | 主文 depth-stability 候选 |
| DLA/coral | parent-anchor frontier / DLA-inspired connected scaffold | voxel DLA / frontier accretion | stress-test / ablation |
| bismuth/crystal/pyrite | lattice/hopper/crystal scaffold with face-contact invariant | IFS / lattice / crystal growth proxy | non-tree scaffold positive 或 appendix |
| radial/transform | radial orbit + hub/ring bridge certificate | IFS/radial copy baseline | ablation/candidate |
| hard-surface/scifi | shape grammar / module transform | shape grammar baseline | stress/control |

### 1.3 Depth 与 projection/caching 条件

每个主 case 至少比较五列：

| Method | 固定含义 | 可写 claim |
|---|---|---|
| traditional baseline | 同 root 或同目标类别的结构 baseline | 结构控制参考，不是 learned PBR 上限 |
| direct sparse grammar | 不做 per-depth projection | naive recursion failure 或下界 |
| final-only cleanup | 只在最终 mesh 修复 | 证明最终清理不能保证递归过程 |
| prune-per-depth | 每层删除/裁剪 orphan | conservative 稳定性，但可能删掉有用结构 |
| bridge-per-depth | 每层添加受限桥/接触证书 | 连接候选，必须报告 fake bridge/over-closing 代价 |
| bridge+cache+hard-mask | 可选强列 | 目前只能作为下一轮候选，未证明完成 |

对用户当前“asset 必须连通”的要求，后续协议必须把 `per-depth connected-to-root` 作为 hard gate：

```text
每个新 support voxel / branch / crystal cell / radial copy
-> 必须有 parent anchor、face-contact、bridge certificate 或 root path
-> 通过 6-neighborhood root reachability
-> 才允许成为下一层 active frontier/cache state
```

### 1.4 渲染条件

所有可进入论文或附录的结果必须有同一协议下的 mesh render：

- neutral material Blender render：front、side、top、iso；
- same-camera textured render：只作为 texture/PBR 兼容性补充；
- zoom-in crops：junction、bridge、tip、facet、cavity、root attachment；
- 禁止用 matplotlib 点云、voxel slice、texture beauty render 单独证明连通性；
- 如果 neutral render 不可读而 textured render 可读，只能写 texture compatibility，不能写结构成功。

### 1.5 Metrics

主指标必须分层报告，不能混成单分数。

| 层级 | 必报 metric | 判读 |
|---|---|---|
| occupancy connectivity | `occupancy_component_count_6n`、`largest_occupancy_component_ratio_6n`、`occupied_voxels`、`orphan_mass_ratio` | primary proxy；`Comp_6n=1, LCR=1.0` 是必要但非充分条件 |
| root reachability | attached-to-root voxels、frontier validity、path-to-root rate | 直接对应“asset 必须连通” |
| branch/path skeleton | tips、branch nodes、total path length、path length to root、junction degree、dead-end orphan tips | tree/root/vine 主指标 |
| face/mesh diagnostics | raw face component count、largest face component ratio、welded component count、non-manifold edges、degenerate faces、watertight/winding | surface fragmentation caveat；不能单独替代 occupancy |
| topology/porosity | Euler characteristic proxy、hole/cavity count、tunnel/genus proxy、surface area/volume proxy、contact area | DLA/coral/crystal 必报 |
| stability | depth-vs-component、depth-vs-LCR、accepted ratio、projection survival、bridge survival、vertex/face/token growth | 证明 per-depth invariant |
| zoom-in stability | junction/bridge/tip/facet crop label、fake bridge label、over-closing label | 人工 QA 必须落表 |
| texture/PBR completeness | GLB export、Blender import、base color、roughness、metallic、opacity、texture resolution、missing texture count | 只支持 asset-readiness |

建议 gate：

- `paper_safe_candidate`：occupancy root-connected + face diagnostics 无严重碎裂 + neutral render/zoom-in 过关 + PBR 完整；
- `appendix_candidate`：occupancy 过关，但 face/render/语义仍有 caveat；
- `negative_ablation`：指标或视觉暴露碎块、假桥、过闭合、结构删除；
- `do_not_claim`：texture 掩盖结构、点云预览、occupancy 过关但 neutral mesh render 不过关。

## 2. 当前状态严格判断

### 2.1 connected scaffold v2

source scaffold 层：

| case | occ | mesh caveat | 判断 |
|---|---:|---|---|
| `bismuth_hopper_cluster` | `1 / 1.0` | mesh comps 4，largest vertex ratio 0.999 | 最强 non-tree scaffold 正例 |
| `pyrite_crystal_lattice_cluster` | `1 / 1.0` | mesh comps 20，largest vertex ratio 0.9995 | 最强 crystal/lattice 正例 |
| `volumetric_dla_coral_cluster` | `1 / 1.0` | mesh comps 33，largest vertex ratio 0.9983 | DLA/coral-inspired stress 正例，不是真 DLA 成功 |
| `porous_coral_mineral` | `1 / 1.0` | mesh comps 29，largest vertex ratio 0.9568 | appendix/compatibility，不宜主文成功图 |
| `root_vine_connected_control` | `1 / 1.0` | mesh comps 2，largest vertex ratio 0.9997 | root/vine control |
| `sci_fi_recursive_module` | `1 / 1.0` | mesh comps 1，largest vertex ratio 1.0 | hard-surface control |

textured GLB 层：

- `pyrite_lattice_*` 和 `volumetric_dla_coral_*` 在 GLB metric 中仍有 `Comp_6n=1, LCR=1.0`；
- `bismuth_hopper_*` 在 GLB metric 中是 `Comp_6n=2, LCR=0.99956`，不是严格单 component；
- `porous_coral_*` 是 `Comp_6n=3, LCR=0.99274`，只能写 near-connected / caveated；
- 所有 textured GLB 的 raw face component count 都非常高，必须用 raw face caveat 和 visual QA 解释。

严格结论：connected scaffold v2 **能缓解碎块**，尤其可支撑“connected non-tree scaffold + Trellis2 texture/PBR route 可用”；但它还不能证明“真实 DLA/crystal/tree/root 全部解决”，也不能用 GLB beauty render 覆盖 face fragmentation。

### 2.2 DLA / coral

正面：

- `volumetric_dla_coral_cluster` source scaffold occupancy 单连通，GLB 可导出、可渲染；
- cache/sampler local smoke 的 `hard_dla` 相比 naive component 数下降。

负面：

- `hard_dla` 选择方法后仍是 3 components，LCR 0.99969；文档 QA 已标为视觉过度闭合/块状，不可作为成功 DLA；
- 现有 DLA/coral 更准确叫 `DLA-inspired connected scaffold`，不是物理或算法意义上的真实 DLA growth；
- 如果只是 sparse closing/cache post-hoc，它可能把开放分支压成块状 support，破坏 DLA/coral 语义。

当前 paper status：appendix / stress-test / negative ablation。除非下一轮 bridge-aware true mesh + neutral zoom QA 通过，否则不要放主文 DLA 成功 claim。

### 2.3 Crystal / bismuth / pyrite

正面：

- `bismuth_hopper_cluster` 是当前最稳的 non-tree connected scaffold 正例；
- `pyrite_crystal_lattice_cluster` 是当前最稳 crystal/lattice 正例；
- HQ textured GLB 可用于 PBR/texture compatibility figure。

负面：

- 当前是 scaffold/crystal-lattice 语义，不是晶体成核、生长或材料物理模拟；
- textured GLB raw face components 很高，不能作为 topology proof；
- `hard_bismuth` cache smoke 指标可用，但仍需语义与 zoom-in QA。

当前 paper status：可以主文小 panel 写成“connected scaffold + PBR compatibility”，不能写成“真实 crystal generator solved”。

### 2.4 Tree / root / vine

正面：

- vine depth textured showcase 四个 stage 都是 occupancy `Comp_6n=1, LCR=1.0`；
- 它最适合支撑 per-depth projection / depth-stability 主线。

负面：

- GLB raw face components 非常高，face-level surface fragmentation 仍需解释；
- tree/root 还缺 branch/path/skeleton 指标、root reachability、leaf/root zoom-in QA；
- 不能只用 vine GLB 纹理证明 tree/root 结构资产可用。

当前 paper status：主文正结果候选，但必须补 L-system/space-colonization baseline、branch/path metrics、neutral zoom-in。

### 2.5 Radial / transform / cache

正面：

- 本地 repair 文档中 radial4 是少数 before/after metrics 和视觉保守性同时改善的 safe candidate；
- cache smoke 的 `hard_radial` 被降到 2 components，LCR 0.99998。

负面：

- `hard_radial` 仍不是严格单连通；
- sparse closing / cache fusion 容易生成 hub-like fake bridge、粗桥或过闭合；
- symmetry error 不能替代 contact/root path 指标。

当前 paper status：ablation/candidate。必须补 orbit hub bridge、bridge survival、symmetry + contact 双指标。

## 3. Cache / sparse closing 的局限

cache/sampler smoke 的定位必须写清：

1. 它是低成本 proxy，不是真正 Trellis2 latent/cache 修改；
2. 它能帮忙筛选 candidate，也能暴露 negative ablation；
3. 它不能替代 grammar-native connected proposal；
4. sparse closing 能改善 component/LCR，但可能产生假桥、粗桥、闭孔、melted crystal facet、DLA 块状化；
5. before 已经 `Comp_6n=1, LCR=1.0` 的 case，closing no-op 或微调不能被写成“连通性修复成功”；
6. 真正主方法应该把 parent anchor / bridge certificate / face-contact invariant 放进每层生成和 frontier 更新，而不是只在最后修补。

因此下一轮实验要优先比较：

```text
direct sparse grammar
vs final-only cleanup
vs prune-per-depth
vs bridge-per-depth
vs bridge+cache+hard-mask
```

并且每列都用同 root、同 depth、同 renderer、同 metric gate。

## 4. 下一轮最小可执行实验矩阵

优先适配 `a100-2` 的 GPU 4/5/6/7。建议一台机器上开 4 个互不抢输出目录的 worker，每个 worker 固定一个 case family，先跑 geometry/neutral render，再决定是否做 expensive texture export。

| GPU | 实验 | Case | Methods | Depth/seed | 必交结果 | 论文用途 |
|---:|---|---|---|---|---|---|
| 4 | tree/root/vine depth invariant | `vine/root/tree conservative compete` | traditional SC/L-system、direct、final-only、prune-per-depth、bridge-per-depth | `D=0..5`, seeds 0/1/2 | branch/path metrics、root reachability、neutral render strip、zoom junction | 主文正结果候选 |
| 5 | DLA/coral connected frontier | `volumetric_dla_coral`, `hard_dla` | direct、final-only、prune、bridge、bridge+cache+hard-mask | `D=3/4`, seeds 0/1/2 | Comp/LCR、bridge survival、Euler/cavity、zoom tip/neck、failure labels | stress/ablation |
| 6 | crystal/bismuth/pyrite scaffold | `bismuth_hopper`, `pyrite_lattice` | direct lattice、final-only、prune、bridge、connected scaffold v2 | `D=3/4`, seeds 0/1/2 | face-contact, facet/cavity zoom, PBR completeness for winners | 主文小 panel + appendix |
| 7 | radial/transform/cache boundary | `radial4`, `hard_radial`, optional scifi | direct orbit、final-only、voxel_close、orbit-hub bridge、cache fusion | `D=3/4`, seeds 0/1/2 | component/contact/symmetry, bridge cost, neutral render | ablation/boundary |

每个实验输出必须有：

- `metrics.csv/json`，包含上文所有 primary 与 diagnostics 字段；
- `config.json`，包含 seed、depth、method、threshold、bridge budget、sampler steps；
- `renders/neutral_front_side_top_iso/*.png`；
- `renders/zoom_junction_bridge_tip_facet/*.png`；
- `failure_labels.csv`；
- winner 才做 textured GLB / PBR export。

## 5. 最应该马上跑的 3 个实验

1. **tree/root/vine depth invariant 主闭环**  
   目的：拿到最可能进主文的正结果。用 conservative compete 对比 traditional、direct、final-only、prune、bridge，补 root reachability、branch/path metrics 和 neutral zoom QA。

2. **DLA/coral bridge-aware negative/positive ablation**  
   目的：正面回应“DLA 碎块不可接受”。不要从 beauty GLB 开始，先跑 `hard_dla` 与 `volumetric_dla_coral` 的同 root 五列对比，明确 bridge 是否真连、是否过闭合、是否仍保留 DLA/coral 语义。

3. **bismuth/pyrite connected scaffold depth + PBR completeness**  
   目的：保住当前最稳 non-tree/crystal 结果。对 `bismuth_hopper` 和 `pyrite_lattice` 跑 depth/parameter 展示，winner 再做 HQ texture/PBR，主文只写 connected scaffold / crystal-lattice，不写真实晶体生长。

## 6. 论文写法边界

可以写：

- connectivity is enforced and evaluated as a per-depth invariant;
- occupancy 6-neighborhood LCR 是 primary mesh connectivity proxy；
- face diagnostics、neutral render、zoom-in QA 是必要补充；
- connected scaffold v2 makes non-tree scaffold assets renderable and texture-compatible；
- DLA/crystal fragmentation motivates bridge-aware projection and root-connected proposal;
- cache/sparse closing is a useful diagnostic/proxy, not a solved method.

不能写：

- DLA growth 已解决；
- crystal nucleation/growth 已解决；
- tree/root/leaf surface fragmentation 已解决；
- Trellis2 sampler 保证拓扑连通；
- textured GLB beauty render 证明几何连通；
- raw face component alone proves failure or success；
- final-only cleanup 足以满足 asset connected invariant。

最终执行标准：**只有同时通过 occupancy root-connectivity、face diagnostics、neutral render、zoom-in QA、texture/PBR completeness 的结果，才能进入主文强 claim；其余结果进入 appendix、ablation、diagnostic 或 do-not-claim。**
