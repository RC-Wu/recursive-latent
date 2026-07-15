# Recursive 3D Generative Growth baseline/metric protocol 20260509

范围：论文实验协议、baseline 公平性、connectivity/depth/parameter metric 闭环；只新增本地文档与小脚本，不修改 `main.tex`、figure 或主代码。

核心立场：

- DLA、crystal、radial、leaf/root 等输出只要出现漂浮碎块、假桥、surface soup 或 texture 掩盖结构，就不能作为主结果。
- 连通性是每一层递归状态的 invariant，不是最终 largest-component cleanup。
- 传统 L-system、space-colonization、IFS/DLA/shape grammar 是强结构 baseline，不能用缺纹理或 raw GLB face islands 作为 strawman。
- Same-condition depth/parameter visuals 是 method behavior characterization：展示稳定性、控制性和失败边界；不要写成单一 ablation 图。

## 1. 证据分层

### Level A: structure-first matched matrix

用途：证明比较协议公平，分离传统结构控制与生成模型外观质量。

固定条件：

- same root anchor；
- same seed 或显式 seed schedule；
- same max depth；
- same mesh renderer/camera；
- saved per-depth OBJ/GLB；
- neutral render 优先，texture render 只作为 appearance supplement。

必需列：

| Slot | Minimum method | 目的 |
|---|---|---|
| Traditional structural | L-system / space colonization / IFS / DLA / shape grammar | 结构控制强 baseline |
| Direct sparse grammar | no projection | 暴露 naive recursion 碎块积累 |
| Final-only projection | only final cleanup | 证明最后清理不能保证中间层 frontier/cache |
| Prune-per-depth | keep root-attached support per depth | per-depth projection lower bound |
| Bridge-per-depth | connect useful islands under budget | DLA/crystal/radial stress candidate |
| Proposed full policy | projection-stabilized grammar + cache/mask/naturalization when available | 主方法 |

当前 `results/baseline_matrix_20260509/metrics.csv` 已有 `lsystem`、`space_colonization`、`proposed_connected`，但还缺 `direct_sparse_grammar` 和 `final_only_projection`。因此它只能写成 matched structural sanity check，不能写成 proposed out-connects traditional baselines。

### Level B: per-depth connectivity curves

每个 case/method 必须输出深度曲线：

- `depth -> occupancy_component_count_6n`
- `depth -> largest_occupancy_component_ratio_6n`
- `depth -> root_component_ratio`
- `depth -> orphan_mass_ratio`
- `depth -> face_component_count` 或 mesh/component diagnostic
- `depth -> vertices/faces/tokens`
- `depth -> tips/branch_nodes/frontier_validity`
- `depth -> projection_survival_ratio`
- `depth -> bridge_survival_ratio`，只对 bridge-aware 方法填

判定规则：

- `Comp_6n=1` 且 `LCR_occ >= 0.98` 是最低 connectivity gate，不是 paper-safe gate。
- occupancy pass 但 face/render 碎，判为 `surface_fragmentation_diagnostic`。
- final-only pass 但中间层 fail，判为 `not_recursive_stable`。
- prune-only pass 但结构大量删除，判为 `negative_or_lower_bound_ablation`。
- bridge pass 但出现粗桥/假桥/过度闭孔，判为 `bridge_cost_visible`，不能升主结果。

### Level C: render/asset QA

每个 paper candidate 必须有：

- neutral mesh render，fixed camera；
- junction/tip/bridge/facet/cavity zoom-in；
- optional textured GLB render，同 camera；
- metric CSV/JSON；
- human QA label：`paper_safe_candidate`、`diagnostic_only`、`negative_ablation`、`do_not_claim`。

Texture/PBR 只回答 asset-readiness，不回答 geometry correctness。当前 cache-selected texture QA 已证明：GLB export 成功仍可能是块状几何或 surface fragmentation，不能作为 DLA/crystal 已解决的证据。

## 2. 主指标定义

### Connectivity

Primary:

- `occupancy_component_count_6n`
- `largest_occupancy_component_ratio_6n`
- `root_component_ratio`
- `orphan_mass_ratio`
- `component_growth_per_depth`

Diagnostics:

- `mesh_component_count` / `face_component_count`
- `largest_mesh_component_vertex_ratio`
- `surface_fragmentation_score`
- `small_component_count`
- non-manifold / degenerate / watertight status if available

Interpretation:

- occupancy 6N 是跨传统 tube OBJ、decoder mesh、GLB 的 primary proxy；
- face component 对 UV/material islands 过敏，只能做 diagnostic；
- 视觉碎块优先级高于单一 scalar metric。

### Space competition

必须记录：

- tip count；
- branch nodes；
- total length / mean segment length；
- attractor coverage where applicable；
- accepted proposal ratio；
- collision/exclusion rejection；
- path-to-root rate；
- orphan tip count。

Space-colonization depth 是 iteration-budget matched，不等同 grammar derivation depth。论文里必须显式说明，不要把 depth fairness 写满。

### Depth behavior

Depth strip 应展示：

- same root；
- same camera；
- d=0..D 或 d=1..D；
- direct/final-only/proposed 曲线并排；
- 每列旁只放核心数字：`Comp_6n`、`LCR_occ`、`FaceComp`、`Survival`。

写法：

> The same-condition depth sequence characterizes recursive behavior under a fixed rule and resource budget; it is not a standalone ablation against unrelated settings.

### Parameter behavior

Parameter grid 应覆盖：

- projection threshold；
- bridge budget / max bridge length；
- voxel closing radius；
- mask radius/dilation；
- sampler alpha/steps；
- cache/LOD resolution；
- random seed。

写法：

> The parameter sweep measures controllability and failure boundaries under the same recursive task. It should be reported as method behavior, with representative renders linked to metric heatmaps.

## 3. Fair baseline protocol by case

| Case family | Traditional baseline | Generative baselines | Primary metric | Paper placement |
|---|---|---|---|---|
| tree/root/vine | L-system + space colonization | direct, final-only, prune-per-depth, proposed | connectivity + tips/branches + path-to-root | main if render passes |
| DLA/coral/frontier | DLA/frontier occupancy baseline | direct, final-only, prune, bridge, proposed | component growth + bridge survival + surface diagnostics | stress/ablation unless clean |
| crystal/radial | IFS/crystal lattice/radial baseline | direct, final-only, bridge, proposed | connectivity + symmetry/transform error + face contact | ablation until visually clean |
| hard-surface/scifi | shape/split grammar if possible | direct, final-only, bridge/cache/mask | renderability + components + semantic readability | supplement unless strong |
| texture/PBR | none as structure baseline | one-shot Trellis2, image-entry recursion, proposed GLB | GLB/import/material validity | appearance only |

Traditional methods must receive neutral mesh renders from the same renderer. Proposed methods must show neutral geometry, not only textured GLB.

## 4. Current local summary from scaffold

Generated with:

```bash
python3 scripts/evaluation/connectivity_depth_parameter_protocol.py
```

Outputs:

- `docs/evaluation/connectivity_depth_parameter_summary_20260509.csv`
- `docs/evaluation/connectivity_depth_parameter_summary_20260509.json`

Inputs used by default:

- `results/baseline_matrix_20260509/metrics.csv`
- `results/branch_path_metrics_20260509/branch_path_metrics.csv`
- `results/coral_depth_textured_showcase_metrics_20260509/metrics.csv`
- `results/vine_depth_textured_showcase_metrics_20260509/metrics.csv`

Observed protocol gaps:

- `tree`, `root`, `vine`: traditional + proposed scaffold exist, but `direct_sparse_grammar` and `final_only_projection` are missing in the matched matrix.
- `vine_d5_projected_compete` and `volumetric_coral_depth`: depth/showcase metrics exist, but they are not fair baseline matrices because traditional/direct/final-only/proposed columns are not grouped under the same condition.

Observed metric notes:

- `tree/root/vine` baseline matrix rows pass occupancy curve gates for `lsystem`, `space_colonization`, and `proposed_connected`; this is a fairness sanity check, not superiority evidence.
- `volumetric_coral_depth` has max `Comp_6n=2` across the depth summary, so it remains stress/ablation until bridge/projection and neutral render QA close the gap.
- `vine_d5_projected_compete` passes the current occupancy gate, but still needs matched direct/final-only/traditional rows before it can support a fair method claim.

## 5. Tables to add before paper integration

### Connectivity table

| Case | Method | D | MaxComp_6n | MinLCR_occ | FinalRootRatio | MaxOrphanMass | FaceComp | ProjectionSurvival | BridgeSurvival | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|

Verdict vocabulary:

- `paper_safe_candidate`
- `matched_structural_sanity`
- `diagnostic_only`
- `negative_ablation`
- `surface_fragmentation_diagnostic`
- `do_not_claim`

### Fair comparison matrix

| Case | Traditional | Direct | Final-only | Prune-per-depth | Bridge-per-depth | Proposed | Same root/seed/depth/render? |
|---|---|---|---|---|---|---|---|

No row should be marked fair unless all method columns are generated under the same root, seed schedule, max depth, resolution, and renderer.

### Depth/parameter behavior table

| Case | Behavior view | Fixed conditions | Varied parameter | Required curves | Required renders |
|---|---|---|---|---|---|
| vine/root/tree | depth | root, seed, camera, renderer | depth | Comp/LCR/root/tips/vertices | mesh strip |
| DLA/crystal | bridge stress | root, seed, depth, renderer | bridge budget/radius | Comp/LCR/bridge/surface | zoom bridge/facet |
| cache/mask | sampler behavior | root, depth, renderer | alpha/steps/mask | Comp/LCR/renderability/material validity | neutral + textured |

## 6. Claim boundaries for paper text

Can write now:

- Under a same-root/same-seed/same-depth structural matrix, traditional L-system and space-colonization baselines are root-attached and occupancy-connected; they are not strawman failures.
- The proposed connected scaffold proxy preserves root-attached occupancy across tree/root/vine depths, but this is not yet the full sparse latent decode-project-encode pipeline.
- DLA/coral/crystal/radial remain stress cases where occupancy metrics, face diagnostics, and neutral render QA must all agree before promotion to main results.
- Same-condition depth and parameter panels characterize recursive method behavior and stability boundaries.

Do not write:

- Proposed is more connected than traditional baselines in the current matched structural matrix.
- Trellis2 texture export proves geometry connectivity.
- DLA/crystal/radial fragmentation is solved.
- Final-only projection is sufficient because the final mesh is clean.
- Occupancy LCR alone proves paper-safe mesh quality.

## 7. Next local experiment minimum

For `tree`, `root`, `vine`, `DLA/coral`, and one `crystal/radial` case:

1. Generate same-root/same-seed/same-depth rows for `direct_sparse_grammar`, `final_only_projection`, `prune_per_depth`, and `bridge_per_depth`.
2. Save per-depth OBJ/GLB and metrics.
3. Run `scripts/evaluation/connectivity_depth_parameter_protocol.py --input ...` on the new CSVs.
4. Render fixed-camera neutral contact sheets plus 2-3 zoom-in crops.
5. Assign final verdict labels before any paper/table integration.
