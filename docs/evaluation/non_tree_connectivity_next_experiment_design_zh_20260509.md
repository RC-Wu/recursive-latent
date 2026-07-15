# Non-Tree Connected Mesh 下一轮实验设计 2026-05-09

项目：`recursive_3d_generative_growth`

本文只设计下一轮非树类 connected mesh 实验。当前结论是：DLA/crystal 的碎块输出不能进入正例；post-hoc `hard_dla` bridge/cache 只能作为负例或诊断，除非一个极小 smoke 同时证明连通性、视觉语义和无假桥。正向路线应优先使用 grammar-native connected scaffold：在生成语法内部维护 parent anchor、face-contact、root path 或局部桥接证书，而不是最终 mesh 之后补缝。

## 0. 核心 claim map

| claim | 最小证据 | 对应实验 |
|---|---|---|
| C1：非树类资产可以用 grammar-native connected scaffold 生成可用 mesh support | 每层 occupancy 6N 单连通或 root-connected，neutral render 无碎块，zoom 中 junction/facet/cavity 可读 | E1, E2 |
| C2：post-hoc bridge/cache 不能作为主要解决方案 | 同 root 同 depth 下，bridge/cache 即使改善 LCR，也会留下假桥、过闭合、块状化或 occupancy 残余碎块 | E3 |
| C3：论文只能声明 crystal/DLA-inspired scaffold，而不能声明真实物理 DLA/crystal growth | 指标和视觉证据只覆盖 connected scaffold、递归 depth stability、texture/PBR compatibility | E1, E2, E3 |

硬门槛：任何结果若出现漂浮块、孤立晶面、孤立 coral nodule、只靠 texture 掩盖的 disconnected surface，均不能作为主文正例。

## 1. 实验 E1：Bismuth/Pyrite grammar-native depth scaffold 正例

### 目标

验证当前最稳的 non-tree/crystal 路线：`bismuth_hopper_cluster` 与 `pyrite_crystal_lattice_cluster` 是否能从单个 source scaffold 扩展为 depth sequence，并在每层保持 connected support、清晰 facet/lattice 语义和可贴 PBR。

### 输入与方法

候选：

- `assets/connected_scaffold_cases_v2_20260509.py` 中的 `bismuth_hopper_cluster`
- `assets/connected_scaffold_cases_v2_20260509.py` 中的 `pyrite_crystal_lattice_cluster`
- 若需要 stage 序列，沿用 `connected_coral_depth_cases_20260509.py` 的 stage 组织方式，但语法必须是 face-contact / overlap-first，而不是 decode 后 bridge

最小矩阵：

| family | stages | seeds | variants |
|---|---:|---:|---|
| bismuth hopper | 1-4 | 3 | `connected_scaffold_v2`, `depth_growth_face_contact`, `depth_growth_no_contact_ablation` |
| pyrite lattice | 1-4 | 3 | `connected_scaffold_v2`, `depth_growth_face_contact`, `depth_growth_no_contact_ablation` |

`depth_growth_no_contact_ablation` 是必要负列：允许新增晶胞但不强制 face-contact/root path，用于证明 connected invariant 不是装饰。

### 必算指标

主指标：

- `occupancy_component_count_6n`
- `largest_occupancy_component_ratio_6n`
- `root_reachable_voxel_ratio`
- `new_cell_face_contact_rate`
- `orphan_voxel_ratio`
- `occupied_voxels`

mesh 诊断：

- `mesh_component_count`
- `largest_mesh_component_vertex_ratio`
- `raw_face_component_count`
- `welded_face_component_count`
- `non_manifold_edge_count`
- `degenerate_face_count`
- `surface_area / occupied_voxels`
- `bbox_diag`

语义与视觉 QA：

- `facet_readability_score`：人工 0/1/2，0=不可读，1=可读但混乱，2=清晰
- `fake_bridge_count`：zoom 中明显后处理细桥数量
- `overclosed_cavity_count`：本应开放的孔洞被块状填死数量
- neutral front/side/top/iso render
- zoom facet、junction、cavity、root attachment crops

PBR 只对 winner 做：

- GLB export 是否成功
- Blender import 是否成功
- missing texture count
- base color / roughness / metallic map 是否存在
- same-camera textured render 是否比 neutral render 更可读，但不得替代 neutral gate

### 成功标准

一个 family 可进入主文小 panel 的条件：

- 所有 4 个 stage、3 个 seed 均满足 `occupancy_component_count_6n=1`
- 所有 4 个 stage、3 个 seed 均满足 `largest_occupancy_component_ratio_6n=1.0`
- `root_reachable_voxel_ratio >= 0.995`
- `new_cell_face_contact_rate >= 0.98`
- `orphan_voxel_ratio <= 0.005`
- winner 的 `largest_mesh_component_vertex_ratio >= 0.995`
- neutral render 中无漂浮块，zoom 中 `fake_bridge_count=0`
- `facet_readability_score >= 1`，主文候选最好为 2
- winner 的 GLB/PBR export 完整，missing texture count 为 0

### 失败标准与解释

失败即满足任一条件：

- 任一 stage/seed 出现 `occupancy_component_count_6n > 1`
- `root_reachable_voxel_ratio < 0.995`
- zoom 出现孤立晶面或明显长细假桥
- bismuth hopper 退化为单个台阶塔，pyrite 退化为密集灰团
- neutral render 不可读，只能靠 texture 看出结构

若失败，论文中应写：crystal/lattice 类仍只能作为 appendix diagnostic；connected scaffold 方向有潜力，但当前 stage grammar 尚未稳定到主文正例。

### 论文可 claim

可写：

> Crystal-inspired non-tree examples are generated as connected scaffold assets with explicit face-contact/root-reachability constraints and are compatible with textured GLB export.

不可写：

> We simulate physical crystal nucleation/growth.

不可写：

> Raw face topology is clean.

主文定位：若通过，作为 non-tree connected scaffold 正例小 panel；pyrite 可偏 supplement，bismuth warm 更适合作主图。

## 2. 实验 E2：Volumetric coral/DLA-inspired connected depth stress 正例

### 目标

测试 DLA/coral-like 非树形状能否在 grammar-native connected support 下形成有体积、有分支、有孔洞的 stage sequence。该实验不是证明真实 DLA；它只证明 DLA/coral-inspired connected scaffold 可以避免碎块。

### 输入与方法

候选：

- `assets/connected_coral_depth_cases_20260509.py` 的 `volumetric_coral_stage`
- `assets/connected_coral_depth_cases_20260509.py` 的 `porous_mineral_stage`
- `assets/connected_scaffold_cases_v2_20260509.py` 的 `volumetric_dla_coral_cluster`

最小矩阵：

| family | stages | seeds | variants |
|---|---:|---:|---|
| volumetric coral depth | 1-4 | 3 | `parent_anchor_frontier`, `parent_anchor_plus_ribs`, `unanchored_frontier_ablation` |
| porous mineral/coral | 1-4 | 3 | `beam_repaint_after_pores`, `no_repaint_after_pores` |

关键原则：

- 每个新增 branch/tip/nodule 必须记录 parent id；
- pore subtraction 后必须重新验证 root path；
- stabilizing ribs 属于 grammar-native scaffold，必须在 config 中标明数量、半径、连接端点；
- 不能使用最终 mesh bridge 修复作为正列。

### 必算指标

连通性：

- `occupancy_component_count_6n`
- `largest_occupancy_component_ratio_6n`
- `root_reachable_voxel_ratio`
- `tip_root_path_rate`
- `orphan_tip_count`
- `parent_anchor_valid_rate`

形态：

- `branch_count`
- `tip_count`
- `mean_tip_path_length`
- `max_tip_path_length`
- `branch_radius_distribution`
- `volume_growth_ratio_by_stage`
- `surface_area_volume_ratio`
- `cavity_or_pore_count`
- `pore_preservation_ratio`

视觉 QA：

- `coral_volume_score`：0=薄片/块，1=有体积但弱，2=清晰 3D coral/mineral
- `dla_semantic_score`：0=完全不像，1=有扩散/团簇感，2=强 DLA/coral-inspired
- `fake_bridge_count`
- `overclosed_region_count`
- neutral render + zoom tip、neck、pore、root attachment

### 成功标准

可作为 DLA/coral-inspired connected scaffold 正例的条件：

- 每个 stage/seed：`occupancy_component_count_6n=1`
- 每个 stage/seed：`largest_occupancy_component_ratio_6n=1.0`
- `root_reachable_voxel_ratio >= 0.995`
- `tip_root_path_rate >= 0.98`
- `orphan_tip_count = 0`
- `parent_anchor_valid_rate >= 0.99`
- `coral_volume_score >= 1`，主文候选必须为 2
- `fake_bridge_count = 0`
- stage 1 到 4 的 `occupied_voxels` 与 `tip_count` 单调或近似单调增加；若减少，必须由 pore subtraction 或 pruning 解释

### 失败标准与解释

失败即满足任一条件：

- 出现任意孤立 nodule、孤立 tip 或 disconnected pore shell
- `tip_root_path_rate < 0.98`
- branch 被 stabilizing ribs 压成块状，`coral_volume_score=0`
- `fake_bridge_count > 0`
- unanchored ablation 反而等同或优于 anchored variant，说明当前 anchor 设计没有贡献

若失败，论文中应写：DLA/coral 仍是 stress-test 和负例；不要把 textured result 放入主文正例。

### 论文可 claim

可写：

> DLA/coral-inspired structures require connected proposal rules; grammar-native parent anchoring avoids the severe fragmentation observed in post-hoc bridge repair.

不可写：

> DLA growth is solved.

不可写：

> The generator reproduces physical diffusion-limited aggregation.

主文定位：即使成功，也建议称为 `DLA/coral-inspired connected scaffold stress case`。若视觉强，可放 supplement 或主文小插图；不要作为核心 claim。

## 3. 实验 E3：Post-hoc hard_dla bridge/cache 极小 smoke 负例/诊断

### 目标

只跑一个极小 smoke 来决定 post-hoc bridge/cache 是否还有继续投入价值。默认假设它是负例：它可能改善 face LCR 或 occupancy LCR，但会制造假桥、过闭合或块状化，不能替代 grammar-native scaffold。

### 输入与方法

候选：

- `assets/connectivity_first_dla_crystal_20260509.py`
- `hard_dla` 或现有 `dla_voxel_root`
- `volumetric_dla` 作为较宽松对照

最小矩阵：

| case | stages | seeds | methods |
|---|---:|---:|---|
| hard_dla | 1 | 1 | `raw`, `sparse_close_bridge`, `mesh_bridge_smooth`, `bridge_cache_hard_mask_tiny` |
| volumetric_dla | 1 | 1 | `raw`, `sparse_close_bridge`, `mesh_bridge_smooth` |

限制：

- 只跑 geometry 和 neutral render；
- 不跑 expensive texture；
- 不扩大到多 seed，除非 tiny smoke 满足下方所有正向门槛；
- bridge budget、close radius、voxel pitch 必须写入 config；
- 每条 bridge 必须输出长度、半径、连接 component id 和是否仍在 final occupancy root path 中。

### 必算指标

基础连通：

- `face_component_count`
- `face_largest_component_ratio`
- `occupancy_component_count`
- `occupancy_lcr`
- `root_reachable_voxel_ratio`
- `orphan_mass_ratio`

bridge/cache 代价：

- `bridge_voxels_added`
- `bridge_meshes_added`
- `mean_bridge_length`
- `max_bridge_length`
- `bridge_radius`
- `bridge_survival_rate`
- `bridge_to_original_voxel_ratio`
- `closed_cavity_delta`
- `surface_area_delta`
- `bbox_diag_delta`

视觉诊断：

- `fake_bridge_count`
- `overclosing_score`：0=无，1=轻微，2=明显块状化
- `semantic_preservation_score`：0=不像 DLA/coral，1=弱，2=保留分枝/团簇语义
- neutral iso/front/side render
- zoom bridge、tip、largest gap、root attachment

### 正向继续条件

只有同时满足以下条件，才允许把 bridge/cache 从负例升级为下一轮候选：

- `occupancy_component_count = 1`
- `occupancy_lcr = 1.0`
- `root_reachable_voxel_ratio >= 0.995`
- `bridge_survival_rate >= 0.95`
- `bridge_to_original_voxel_ratio <= 0.08`
- `max_bridge_length <= 0.12 * bbox_diag`
- `fake_bridge_count = 0`
- `overclosing_score = 0`
- `semantic_preservation_score >= 1`
- neutral render 不出现明显拉线、缝合杆或块状糊合

### 失败标准与解释

只要违反上述任一条件，就把该实验作为 negative/diagnostic。尤其注意：

- `face_component_count=1` 但 `occupancy_component_count>1` 不是成功；
- `occupancy_lcr` 高但仍有孤立小块不是成功；
- 指标变好但 fake bridge 可见不是成功；
- DLA 被 close 成实心块不是成功；
- texture 能遮住 bridge 也不是成功。

### 论文可 claim

若失败，可写：

> Post-hoc bridge/cache repair improves selected connectivity diagnostics but does not reliably produce visually plausible connected DLA assets; this motivates enforcing connectivity inside the proposal grammar.

若极小 smoke 意外通过，只能写：

> A constrained bridge/cache smoke test suggests a possible diagnostic repair path, but the main positive evidence remains grammar-native connected scaffold generation.

不可写：

> Bridge/cache solves DLA fragmentation.

主文定位：默认 appendix negative ablation；只有 tiny smoke 全过才允许作为 appendix candidate，不进主文正例。

## 4. 推荐执行顺序

| 顺序 | 实验 | 先停/继续 gate | 原因 |
|---:|---|---|---|
| 1 | E1 bismuth/pyrite depth scaffold | 4 stage x 3 seed 全部 occupancy 单连通，且 neutral render 可读 | 最可能成为 non-tree 主文正例 |
| 2 | E2 volumetric coral/DLA-inspired connected depth | anchored variant 明显优于 unanchored ablation，且无 fake bridge | 正面回应 DLA/coral 碎块问题，但 claim 要保守 |
| 3 | E3 hard_dla bridge/cache tiny smoke | 只要出现假桥、过闭合或 occupancy 残余碎块即停止扩展 | 控制预算，避免继续押注负路线 |

## 5. 最终论文写法边界

可以作为主文强 claim 的句子：

> We enforce connected support as a per-depth invariant for non-tree scaffold grammars, and evaluate it with occupancy root reachability, mesh diagnostics, neutral renders, and zoom-in QA.

可以作为主文或 supplement 的句子：

> Crystal-inspired and coral-inspired examples demonstrate that non-tree recursive assets can be made texture-compatible when connectivity is native to the grammar.

必须保留的 caveat：

> These examples are connected scaffold assets, not physical simulations of crystal growth or diffusion-limited aggregation.

不能写：

- DLA/crystal generation 已系统解决；
- textured GLB beauty render 证明 topology clean；
- final-only cleanup 足以保证 connected asset；
- face component count 单独决定成功或失败；
- bridge/cache 是正向主方法，除非 E3 tiny smoke 全过。

## 6. 交付物格式

每个实验目录至少包含：

- `config.json`
- `metrics.csv`
- `metrics.json`
- `stage_summary.json`
- `renders/neutral_front_side_top_iso/*.png`
- `renders/zoom_junction_bridge_tip_facet/*.png`
- `failure_labels.csv`
- winner only：`textured_glb/` 与 Blender same-camera render

`failure_labels.csv` 建议字段：

| field | 含义 |
|---|---|
| `case` | family/case 名称 |
| `stage` | depth stage |
| `seed` | seed |
| `method` | variant |
| `failure_type` | `orphan`, `fake_bridge`, `overclosed`, `thin_sheet`, `semantic_loss`, `texture_only` |
| `crop_path` | 对应 zoom crop |
| `paper_status` | `main_candidate`, `appendix_candidate`, `negative_ablation`, `do_not_claim` |

最终选择规则：E1 是下一轮最高优先级，E2 是必要 stress 正例，E3 只做 tiny diagnostic。若三者预算冲突，先保 E1；若 E2 失败，仍可把失败作为 DLA/coral stress ablation；若 E3 失败，不再扩展 hard_dla bridge/cache 路线。
