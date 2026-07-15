# Space Competition / Baseline / Metric Protocol v2

创建时间：2026-05-08

目的：把 baseline 与 metric 固定成可执行实验协议，服务主张“递归生成不是最后清理一次 mesh，而是在每个深度维护结构状态”。本协议继承 `baseline_metric_eval_plan_zh_20260508.md`，但把主实验、可视化矩阵和最小指标脚本落到明确表格。

## 1. 主实验问题

主问题不是“哪张图更像植物”，而是：

> 在同一递归深度、同一输出接口、同一渲染协议下，传统 space-colonization、普通生成模型递归、final-only projection 和 proposed per-depth projection + sparse competition，谁能在增长过程中持续保持连通性、尺度受控、分枝/占据结构可解释、mesh/GLB 可加载。

因此每个 case 必须保留深度序列 `d=0..D`，不能只比较最终图。

## 2. 方法组

### 2.1 Traditional baselines

| Method | 必选输出 | 主要回答 |
|---|---|---|
| Space colonization | skeleton JSON, tube OBJ, neutral render, metric JSON/CSV | 显式 attractor/tip competition 能否给出清楚结构 scaffold |
| L-system / turtle | segment graph, tube OBJ, neutral render | 符号分枝递归与 branch/tip/angle 上限 |
| DLA / voxel frontier | voxel/cube OBJ 或 marching-cubes OBJ, neutral render | stochastic frontier growth 的 porous/fragment stress |
| IFS / transform-copy | copy graph, tube/mesh OBJ, neutral render | self-similar transform-copy 的尺度递归 |

Traditional baseline 只允许作为 structure-control 对比，不用 procedural texture 的弱项来证明 proposed texture 更好。

### 2.2 Generative baselines

| Method | 必选输出 | 失败模式 |
|---|---|---|
| One-shot 3D generation | single mesh/GLB/render | 局部外观好，但无递归 trace |
| Image-entry recursion | root generated from guide image, then depth mesh/render | root 可用但递归后结构漂移 |
| Direct sparse grammar | depth `0..D` OBJ/render | component 爆炸、floating fragments |
| Full flow repair | repaired depth/final OBJ/render | topology 被 denoise wash out |
| Masked weak blend | depth OBJ/render | 局部自然化与连接性 tradeoff |
| Final-only projection | raw depth trace + final projected OBJ/render | 中间深度不可用，最后补救不足 |
| Proposed | per-depth projected OBJ/GLB/render + trace/metrics | 主方法 |

### 2.3 主表必须同台比较

Space competition 主实验至少包含：

1. Traditional space colonization。
2. Direct sparse grammar。
3. Final-only projection。
4. Proposed sparse occupancy competition + per-depth projection。

可选加入 masked weak blend / full flow repair，但不能替代上述四列。

## 3. Case 固定

必跑 case：

| Case | 深度 | 用途 |
|---|---:|---|
| `vine_d5_projected_compete` / root-vine | 5 | 主线：空间竞争和深度稳定性 |
| `tree_projected_compete` / tree-canopy | 3 | 分枝/tip 结构 |
| `bush_shell` 或 root/branch scaffold | 3 | traditional space colonization 对齐 |
| `transform_portal_d3` 或 `transform_radial4_d3` | 3 | 非植物 transform-copy，避免 claim 只对树有效 |

Appendix / stress case：

- DLA/coral/porous：报告 occupancy/topology proxy，不放在主视觉第一行。
- `compete_fork`：作为 stability-expression boundary，明确它比 conservative `compete` 更碎。

## 4. 输出与可视化协议

每个方法和每个深度都要保存：

- `mesh.obj` 或 `mesh_pruned.obj`；
- 若可用，`asset.glb`；
- fixed-camera neutral render；
- 若有 GLB，fixed-camera textured/PBR render；
- metric JSON/CSV 行；
- trace/skeleton/attractor/proposal 统计，若方法能输出。

主图布局：

| Row | Col 1 | Col 2 | Col 3 | Col 4 |
|---|---|---|---|---|
| Mesh-based neutral | Traditional | Direct | Final-only | Proposed |
| Textured/PBR if available | Traditional simple material | One-shot/image-entry | Final-only textured | Proposed textured |
| Curves | LCR/components | LCR/components | LCR/components | LCR/components |

要求：

- neutral mesh row 是主证据，textured row 只说明资产可用性；
- 所有列使用同一 Blender/Cycles camera/light/resolution；
- texturing 不能遮挡结构判断，必须同时展示 neutral render；
- scatter/matplotlib preview 只能用于 debugging，论文主图用 mesh render；
- GLB import 或材质失败必须入表，不允许静默替换成最好看的结果。

## 5. 定量指标分层

### 5.1 必报 mesh/asset 指标

每个 mesh/GLB/点云行必须报告：

- `vertices`, `faces`；
- `bbox_extent_x/y/z`, `bbox_volume`, `bbox_diag`；
- `component_count`；
- `largest_component_vertex_ratio`；
- `fragmentation_score = 1 - largest_component_vertex_ratio`；
- `small_component_count_lt100`；
- `surface_area_est`，若有 faces；
- loader/import status。

### 5.2 必报 occupancy proxy

用统一 bbox normalization 和统一 resolution，例如 `64^3`：

- `occupied_voxels`；
- `occupancy_coverage = occupied_voxels / resolution^3`；
- `occupancy_component_count_6n`；
- `largest_occupancy_component_ratio_6n`；
- box-counting occupied counts at `8,16,32,64`；
- box-counting dimension proxy。

说明：这些是 vertex occupancy proxy，不等价于 watertight volume。论文中只把它们用于同协议横向比较。

### 5.3 Branch / tip / angle 指标

Traditional space-colonization 和 L-system 必须从 skeleton/segment graph 直接报告：

- `nodes`, `segments`, `tips`, `branch_nodes`；
- total length and mean segment length；
- branch angle mean/std/histogram；
- attractor coverage ratio。

Proposed 若有 grammar trace，优先从 trace 统计同名指标；若没有 trace，只能报告 voxel/skeleton proxy，并在表头标注 `proxy`。

### 5.4 Competition / projection 指标

有 trace 的方法必须报告：

- proposal count；
- accepted proposal count；
- accepted proposal ratio；
- collision violation count/rate；
- projection kept component count；
- projection survival ratio；
- per-depth component growth rate；
- per-depth largest-component-ratio AUC。

没有 trace 的方法对应列填 `n/a`，不能用图像分数替代。

### 5.5 Texture / PBR 指标

每个 GLB 必须报告：

- GLB export success；
- Blender import success；
- material count；
- base color valid；
- roughness valid；
- metallic valid；
- opacity valid；
- missing texture count；
- render warning count；
- human QA: `usable / not_usable / hides_structure`。

Texture/PBR success table 不用于证明递归结构，只用于说明 asset readiness。

## 6. 主表模板

| Case | Method | D | vertices | faces | comp | LCR | frag | occ vox | occ comp | box dim | collision | accepted | GLB | Read |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| vine/root | Traditional SC | 5 |  |  |  |  |  |  |  |  | n/a | n/a | optional | scaffold strong, material weak |
| vine/root | Direct grammar | 5 |  |  |  |  |  |  |  |  |  |  | optional | fragment propagation |
| vine/root | Final-only | 5 |  |  |  |  |  |  |  |  |  |  | optional | final cleanup only |
| vine/root | Proposed | 5 |  |  |  |  |  |  |  |  |  |  | yes/no | per-depth stable |

Curve plots:

- depth vs `largest_component_vertex_ratio`；
- depth vs `component_count`；
- depth vs `fragmentation_score`；
- depth vs `occupied_voxels`；
- depth vs accepted proposal ratio；
- depth vs collision violation rate；
- depth vs branch/tip count。

## 7. 解释规则

成功：

- conservative `compete` 在 vine/tree 上 LCR 接近或高于 `0.95`；
- component count 不随 depth 爆炸；
- accepted proposal ratio 与 collision rate 显示 competition 起作用；
- branch/tip 指标没有被 repair 抹平；
- neutral render 和 metric 同向支持。

弱成功：

- geometry 稳定优于 direct/final-only，但 GLB/PBR 成功率有限。此时 texture 只写 compatibility。

失败但有价值：

- `compete_fork` component 多、LCR 低：写成 expression-stability boundary；
- full repair 更平滑但 branch/tip 减少：写成 repair wash-out；
- one-shot 视觉好但 trace/递归指标差：写成问题定义证据。

## 8. 可执行指标脚本

新增脚本：

```bash
python3 assets/recursive_growth_mesh_metrics.py \
  --case tree_compete_d3=docs/remote_results/system_grammar_remote_20260508_1839/cache_lod_probe/prototype_manifest/tree_compete_d3.obj \
  --case sc_tree=results/traditional_baselines_space_colonization_20260508/tree_canopy/space_colonization.obj \
  --out-json results/metrics/space_competition_metrics.json \
  --out-csv results/metrics/space_competition_metrics.csv
```

批量扫描：

```bash
python3 assets/recursive_growth_mesh_metrics.py \
  visuals/siga_night_20260508/selected_vine_meshes \
  --recursive \
  --out-json results/metrics/selected_vine_mesh_metrics.json \
  --out-csv results/metrics/selected_vine_mesh_metrics.csv
```

脚本能力：

- OBJ：内置 parser，支持 polygon face fan triangulation；
- GLB/GLTF/PLY/STL/OFF：若 `trimesh` 可用则加载，否则记录 `load_error`；
- point cloud text：支持 `.xyz/.pts/.txt/.csv` 的前三列 xyz；
- component：mesh face connectivity；无 face 时降级为 point proxy；
- occupancy：vertex voxelization proxy；
- box-counting：统一 bbox normalized vertex occupancy proxy；
- 输出 JSON 和 CSV。

未实现但保留接口位置：

- watertight volume / true voxel fill；
- mesh genus / exact Euler characteristic；
- skeletonization from arbitrary generated mesh；
- CLIP/DINO multi-view；
- Blender import/PBR channel inspection；
- trace-level collision/proposal parsing。

## 9. 与现有结果的衔接

`projection_ablation_table.md` 已显示：

- conservative `vine_compete_d3` 与 `tree_compete_d3` 中，per-depth projection 明显降低 raw component 爆炸，并保持 dominant component；
- expressive `compete_fork` 虽降低 raw component，但 final LCR 仍低，应作为边界案例。

`system_grammar_remote_20260508_1839/summaries/cache_lod_probe/prototype_manifest.log` 是 cache/LOD prototype，不是完整实验结果；它可用于说明 transform-copy/cache handles，但不能替代 space competition 主表。

## 10. 最小落地顺序

1. 用 `recursive_growth_mesh_metrics.py` 对已有 traditional space-colonization OBJ、projection ablation OBJ、selected vine/tree OBJ 生成统一 CSV/JSON。
2. 补 trace 层 proposal/collision/accepted ratio 到同一表。
3. 用 Blender/Cycles 固定相机渲染四列主图。
4. 对可用 GLB 跑 PBR/import success table。
5. 把 `compete_fork`、DLA、box-counting、CLIP/DINO 放 appendix 或 failure/stress section。
