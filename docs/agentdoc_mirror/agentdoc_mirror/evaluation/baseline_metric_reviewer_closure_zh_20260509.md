# Baseline / Metric Reviewer Closure Plan 20260509

范围：本文件只回应 reviewer 对 baseline、metric、claim 证据链的质疑；不修改论文、不启动远程任务。配套只读汇总写在：

- `results/baseline_metric_inventory_20260509/existing_metric_inventory.csv`
- `results/baseline_metric_inventory_20260509/traditional_baseline_inventory.csv`
- `results/baseline_metric_inventory_20260509/claim_coverage_matrix.csv`

## 0. Reviewer 关切翻译成硬闭环

当前论文不能只说“程序化递归 + 生成模型结合”。Reviewer 会追问三件事：

1. **baseline 是否公平**：同 root、同 depth、同 seed/预算、同 renderer，对比传统程序化方法、naive 递归、final-only repair、per-depth projection/bridge。
2. **metric 是否直接证明 claim**：texture GLB、beauty render、点云预览都不能证明连通性或递归稳定；必须有 per-depth support/root-connected 指标、mesh diagnostics、neutral render 和 zoom-in QA。
3. **claim 是否过度**：DLA/crystal/bismuth/pyrite/vine 现在能 claim 的内容不同，不能把 scaffold connected 写成真实物理/算法生长，也不能把 PBR 成功写成 topology 成功。

因此本闭环采用最严格写法：

> 每个主文 claim 必须绑定到一个实验 family、一个 matched baseline matrix、一组 primary metrics、一组 diagnostics、一组 render/zoom QA。缺任何一项，降级为 appendix、stress-test 或 negative ablation。

## 1. 现有结果库存

### 1.1 Vine / root / tree

现有正证据：

| 证据 | 已有指标 | 当前可写 |
|---|---:|---|
| `vine_d5_projected_compete` textured stages 1-4 | 每层 `occ_comp_6n=1`, `occ_lcr_6n=1.0` | per-depth occupancy-connected vine showcase |
| `root_vine_connected_control` source scaffold | `occ_comp_6n=1`, `occ_lcr_6n=1.0`, mesh comps 2, mesh LCR 0.9997 | connected root/vine scaffold control |
| space-colonization v2 baselines | `root_vine`: 1628 nodes, 456 tips, max depth 24, coverage 0.97125 | traditional control metrics available, but not matched yet |

严格限制：

- vine textured GLB raw face components 很高：stage 1-4 分别约 85k、90k、101k、107k，raw face LCR 约 0.0012-0.0016。只能作为 textured surface splitting caveat，不能作为 clean mesh topology 证据。
- tree/root 还缺 branch/path/root reachability 指标，不能把 vine occupancy 结果外推成 tree/root 全解决。

当前 claim：

> 可以写“projection-stabilized vine showcase keeps a voxelized 6-neighborhood occupancy support connected across displayed depths”。不能写“tree/root/vine assets are fully topology-clean”。

### 1.2 Bismuth

现有正证据：

| 证据 | 已有指标 | 当前可写 |
|---|---:|---|
| `bismuth_hopper_cluster` source scaffold | `occ_comp_6n=1`, `occ_lcr_6n=1.0`, mesh comps 4, mesh LCR 0.9994 | connected non-tree scaffold |
| `bismuth_hopper_depth` stages 1-4 | 每层 `occ_comp_6n=1`, `occ_lcr_6n=1.0`; mesh comps 4/2/2/2 | depth-stable bismuth scaffold |
| HQ textured GLB | `occ_comp_6n=2`, `occ_lcr_6n=0.99956` | near-connected PBR compatibility, caveated |
| cache smoke `hard_bismuth` | selected method gives comp 1, LCR 1.0 | candidate only; needs semantic/visual QA |

严格限制：

- 这是 hopper/crystal-like scaffold，不是 bismuth 结晶物理模拟。
- HQ GLB 仍是 2 components，raw face components 约 3674-3675，不能当 topology proof。

当前 claim：

> 可以写“bismuth-like non-tree scaffold can be kept occupancy-connected across depth and textured as an asset candidate”。不能写“bismuth crystal growth is solved”。

### 1.3 Pyrite / crystal lattice

现有正证据：

| 证据 | 已有指标 | 当前可写 |
|---|---:|---|
| `pyrite_crystal_lattice_cluster` source scaffold | `occ_comp_6n=1`, `occ_lcr_6n=1.0`, mesh comps 20, mesh LCR 0.9995 | connected crystal-lattice scaffold |
| `pyrite_lattice_depth` stages 1-4 | 每层 `occ_comp_6n=1`, `occ_lcr_6n=1.0`; mesh comps 1/20/73/139 | depth occupancy connected, mesh fragmentation caveat grows |
| HQ textured GLB | `occ_comp_6n=1`, `occ_lcr_6n=1.0` | PBR compatibility candidate |

严格限制：

- source depth scaffold 的 mesh component count 随 stage 增长到 139，说明 face/mesh diagnostics 不能忽略。
- textured GLB raw face components 约 50k，raw face LCR 极低，只能作为 export/material caveat。
- 不能写真实 crystal nucleation/growth，只能写 crystal-lattice scaffold / symmetry-like support。

当前 claim：

> 可以写“pyrite-like lattice scaffold maintains connected voxel support across depth”。不能写“crystal generation/topology is solved at mesh-face level”。

### 1.4 DLA / coral

现有正证据：

| 证据 | 已有指标 | 当前可写 |
|---|---:|---|
| `volumetric_dla_coral_cluster` source scaffold | `occ_comp_6n=1`, `occ_lcr_6n=1.0`, mesh comps 33, mesh LCR 0.9983 | DLA/coral-inspired connected scaffold stress result |
| HQ textured GLB | `occ_comp_6n=1`, `occ_lcr_6n=1.0` | textured asset compatibility candidate |
| traditional DLA baseline | 900 points, 7200 vertices, 10800 faces | baseline geometry exists, but metrics are too thin |

现有负证据：

| 证据 | 指标 | 解释 |
|---|---:|---|
| cache smoke `hard_dla` | selected comp 3, LCR 0.99969 | metric improves vs naive, but status marks visual over-closing |

严格限制：

- 当前 DLA 只能叫 `DLA-inspired connected scaffold`。
- 没有证明随机游走 hitting distribution、frontier attachment、branch openness、porosity/cavity 保真。
- sparse closing/cache 可能把 DLA/coral 压成块状，正好回应 reviewer 的担忧：metric 变好不等于语义正确。

当前 claim：

> 可以写“DLA/coral is a stress-test motivating bridge-aware connected proposal; current connected scaffold is renderable but not a true DLA growth proof”。不能放主文成功 claim。

## 2. 缺失 baseline 矩阵

每个进入主文或强 appendix 的 family 必须补齐同 root、同 depth、同 renderer 的矩阵：

| Family | Traditional baseline | Naive / ablation | Proposed columns | 当前缺口 |
|---|---|---|---|---|
| vine/root/tree | L-system, space colonization | direct sparse grammar, final-only cleanup | prune-per-depth, bridge-per-depth, proposed projection-stabilized grammar | 缺 matched depth/seed；缺 branch/path/root reachability |
| bismuth | IFS/lattice/hopper proxy | direct lattice copy, final-only cleanup | connected scaffold v2, bridge/contact constrained | 缺同 root baseline；缺 facet/contact/neutral zoom |
| pyrite | IFS/lattice/crystal proxy | direct lattice copy, final-only cleanup | connected scaffold v2, bridge/contact constrained | 缺 symmetry/contact 双指标；mesh comps 随深度增长未解释 |
| DLA/coral | voxel DLA / frontier accretion | direct frontier, final-only closing | prune, bridge, bridge+cache+hard-mask | 缺真实 DLA baseline metrics；缺 over-closing/fake bridge labels |

不建议现在新增昂贵 texture baselines。先做 geometry/neutral/metric baseline closure，winner 再 texture。

## 3. Metric Gate

### 3.1 Primary metrics

主指标必须按层报告：

| Metric | 字段 | Gate |
|---|---|---|
| occupancy connectivity | `occupancy_component_count_6n`, `largest_occupancy_component_ratio_6n` | 主文正例要求每层 `1 / 1.0` |
| root reachability | `root_reachable_voxel_ratio`, `orphan_mass_ratio`, `path_to_root_rate` | reviewer closure 必补；正例要求 orphan 近 0 |
| depth stability | component/LCR vs depth, token/vertex/face growth | 画折线，不只报 final |
| mesh diagnostics | raw/welded component count, largest vertex ratio, non-manifold/degenerate/watertight | 不能替代 occupancy，但必须解释 surface caveat |
| structure semantics | tips, branch nodes, path length, contact area, symmetry/contact error, cavity/porosity | 按 family 选择 |

### 3.2 Family-specific metrics

| Family | 必报补充指标 |
|---|---|
| vine/root/tree | tip count、branch nodes、path length to root、dead-end orphan tips、junction zoom labels |
| bismuth/pyrite | face-contact count、facet size distribution、lattice/symmetry proxy、contact bridge area、facet/cavity zoom labels |
| DLA/coral | branch openness、frontier attachment rate、cavity/porosity proxy、bridge survival、over-closing/fake bridge labels |

### 3.3 Render / QA gate

进入论文图的结果必须有：

- neutral material front/side/top/iso；
- zoom crops：junction、bridge/contact、tip/facet、cavity；
- same-camera textured render 只作为 PBR/asset-readiness 补充；
- `failure_labels.csv`：`floating_fragment`, `fake_bridge`, `over_closed`, `melted_facet`, `texture_hides_geometry`, `surface_fragmented`。

## 4. 当前能写与不能写

### 4.1 可以写

- 我们把 per-depth connected support 当成 recursive generation 的 hard invariant，而不是最后修补。
- 对 vine showcase，已有每层 occupancy 6-neighborhood connected evidence。
- 对 bismuth/pyrite，已有 connected scaffold 和 depth scaffold evidence，可作为 non-tree/crystal-lattice scaffold candidates。
- 对 DLA/coral，已有 connected scaffold stress result，但它主要说明问题和评测协议，不是主文成功。
- PBR/GLB export 成功只说明 asset compatibility，不说明拓扑正确。

### 4.2 不能写

- 不能写 DLA/crystal/bismuth 的真实物理或算法生长已经解决。
- 不能把 raw beauty render 或 textured GLB 当作 connectivity proof。
- 不能把 occupancy `Comp=1` 当作充分条件；仍需 mesh diagnostics、neutral render、zoom QA。
- 不能把 cache/sparse closing 的 metric 改善写成主方法成功，尤其 `hard_dla` 已标注 visual over-closing。
- 不能把 pyrite source depth mesh component 增长忽略掉；这正是 reviewer 会抓的问题。

## 5. 具体表格与图

### Table 1: Claim Boundary Table

列：

`Family | Existing evidence | Primary metric | Diagnostics caveat | Claim allowed now | Claim not allowed`

用途：放在内部 rebuttal / paper rewrite checklist，防止过度声称。

### Table 2: Matched Baseline Matrix

列：

`Family | Root/case | Traditional | Direct | Final-only | Prune-per-depth | Bridge-per-depth | Proposed | Seeds/depth | Missing`

用途：这是 reviewer 最关心的 baseline 公平性表。当前大多是 `Missing`，必须作为下一轮实验清单。

### Table 3: Per-Depth Connectivity

列：

`Family | Case | Method | Depth | OccComp6N | OccLCR6N | RootReach | OrphanMass | MeshComp | MeshLCR | Vertices | Faces`

用途：主文/附录核心 metric 表。现有可填 vine、bismuth depth、pyrite depth；root reachability/orphan 目前为空。

### Table 4: Family Semantics Metrics

列：

`Family | Case | Method | Tips | BranchNodes | ContactArea | SymmetryError | CavityCount | PorosityProxy | FailureLabel`

用途：避免只用 connectivity 指标掩盖语义失败。

### Figure A: Connectivity vs Depth

四个小图：

- occupancy component count vs depth；
- occupancy LCR vs depth；
- mesh/raw face component count vs depth；
- vertices/faces/token growth vs depth。

现有可画：vine、bismuth depth、pyrite depth。DLA 需要补 per-depth。

### Figure B: Baseline Strip

每个 family 一行，同 camera neutral render：

`traditional | direct | final-only | prune | bridge | proposed`

用途：直接回应“是不是只是传统方法 + texture / 后处理”。

### Figure C: Zoom QA Panel

每个 family 选 3 个 zoom：

- vine/root：root attachment、junction、tip；
- bismuth/pyrite：facet contact、bridge/contact、cavity；
- DLA/coral：frontier branch、thin neck、over-closing failure。

### Figure D: Failure/Ablation Panel

必须把失败放出来：

- `hard_dla` cache smoke：component/LCR 改善但 visual over-closing；
- pyrite mesh component growth：occupancy connected 但 face diagnostics caveat；
- textured GLB raw face fragmentation：PBR 成功不等于 topology proof。

## 6. 最小下一步实验闭环

优先级 1：vine/root/tree 主文闭环

- Cases：`vine_d5_projected_compete` 或同 root root/vine/tree。
- Methods：space-colonization / L-system / direct / final-only / prune-per-depth / bridge-per-depth / proposed。
- Metrics：root reachability、branch/path、dead-end orphan tips、neutral zoom。
- 目标 claim：主文正结果。

优先级 2：bismuth/pyrite non-tree scaffold 闭环

- Cases：`bismuth_hopper_depth`, `pyrite_lattice_depth`。
- Methods：IFS/lattice baseline / direct / final-only / connected scaffold v2 / bridge/contact constrained。
- Metrics：contact area、facet distribution、symmetry/contact error、neutral facet zoom、PBR completeness for winner。
- 目标 claim：主文小 panel 或 appendix strong candidate。

优先级 3：DLA/coral stress/negative 闭环

- Cases：`volumetric_dla_coral_cluster`, `hard_dla`。
- Methods：voxel DLA / direct frontier / final-only closing / prune / bridge / bridge+cache。
- Metrics：frontier attachment、porosity/cavity、bridge survival、over-closing label。
- 目标 claim：stress-test + negative ablation；除非 zoom QA 通过，不进主文正结果。

## 7. 当前 blockers

1. 缺 matched baseline matrix：现有传统 baseline 与 proposed 结果不是严格同 root、同 depth、同 renderer。
2. 缺 root reachability / orphan mass：这是回应“必须连到 root/scaffold”的关键字段。
3. 缺 neutral render 和 zoom QA：textured GLB 不能支撑结构 claim。
4. 缺 family semantics metrics：DLA 缺 porosity/frontier，tree/root 缺 skeleton path，crystal 缺 contact/facet/symmetry。
5. face/raw component caveat 很严重：vine/pyrite textured GLB raw face component count 极高，必须解释为 export/surface-splitting diagnostic，并用 welded/neutral/occupancy 三层指标补证。
6. DLA 当前最危险：`hard_dla` 明确是 metric 改善但视觉过闭合，不能作为正例。

## 8. 配套库存文件

本次只从已有结果生成以下文件：

| 文件 | 内容 |
|---|---|
| `results/baseline_metric_inventory_20260509/existing_metric_inventory.csv` | vine/bismuth/pyrite/DLA/cache smoke 已有 metric 行 |
| `results/baseline_metric_inventory_20260509/traditional_baseline_inventory.csv` | IFS/L-system/DLA 和 space-colonization 传统 baseline 库存 |
| `results/baseline_metric_inventory_20260509/claim_coverage_matrix.csv` | 每个 family 的当前正证据、可写 claim、缺口 |
| `results/baseline_metric_inventory_20260509/README.md` | 库存说明 |

这些文件不是新实验结果，只是 existing-result inventory。
