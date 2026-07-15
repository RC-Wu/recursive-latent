# Baseline matrix paper integration 20260509

范围：本地评测支线；不使用 SSH；不修改 `paper_siga/main.tex`。

输入依据：

- `docs/evaluation/baseline_matrix_zh_20260509.md`
- `results/baseline_matrix_20260509/metrics.csv`
- `docs/evaluation/traditional_matched_guide_texture_baseline_zh_20260509.md`
- `docs/paper/current_story_risk_audit_zh_20260509.md`
- `paper_siga/main.tex`

产出建议：

- 主文只使用 baseline matrix 的一张精简数值表或一两句文字，作为 matched structural-control diagnostic。
- 完整 per-depth CSV、contact sheet、protocol caveat 放补充材料。
- 不把它写成最终 baseline closure，因为 direct/final-only/prune-per-depth/bridge-per-depth 和 zoom QA 仍缺。

## 1. 当前 baseline matrix 的真实含义

这组 `results/baseline_matrix_20260509/metrics.csv` 是第一版 same-root / same-seed / same-depth / same renderer 的本地 CPU 结构矩阵。它已经修复了此前传统 baseline 不同 guide、不同入口、不同渲染协议的部分公平性问题，但它仍然不是论文中最关键的 projection ablation matrix。

当前协议包含：

- Cases：`tree`, `root`, `vine`。
- Methods：`lsystem`, `space_colonization`, `proposed_connected`。
- Depth：1--4，最终深度为 depth 4。
- Same-root：全部从 `(0,0,0)` root anchor 出发。
- Same-seed：`20260509`，脚本内固定 case/method offset。
- Same renderer：最终深度 contact sheet 使用同一 mesh renderer。
- Primary connectivity metric：voxel occupancy 6-neighborhood connected components 和 largest component ratio。

最关键判断：这组实验不能证明 proposed 在 connectivity 上击败传统方法。因为传统 `lsystem` 和 `space_colonization` 在这个协议里也通过 skeleton-to-voxel tube mesh 形成了 occupancy-connected support，最终深度的 `occ_comp_6n=1`, `occ_lcr_6n=1.0`, `root_component_ratio=1.0` 全部成立。

它能证明的是：

- 在一个 matched structural-control 协议下，三类方法都能生成 root-attached occupancy-connected branching support。
- 当前 proposed proxy 的差异主要不在“最终是否连通”，而在递归语义：每层 projection-positive scaffold 将 root-attached support 作为递归不变量，而传统方法是规则化 scaffold 或 attractor coverage。
- Space-colonization 在最终 OBJ mesh 上仍出现多 mesh components：tree=9, root=9, vine=24；但 occupancy proxy 是单连通。因此可以作为 mesh-export caveat，不能当作拓扑失败。
- `proposed_connected` 在 depth 1--4 各层都维持 occupancy 单连通，且 projection survival ratio 约为 tree 0.830--0.895、root 0.840--0.907、vine 0.917--0.925，说明它有稳定 pruning/projection 代价，而不是免费保留全部 proposed support。

## 2. 能写进论文的 claim

### Claim A：matched structural-control sanity check

可写：

> Under a matched root, seed, depth, and mesh-render protocol, classical L-system, space-colonization, and our connected scaffold proxy all produce root-attached voxel-occupancy connected supports for tree/root/vine cases.

中文判断：这是最稳的 claim。它对审稿人有价值，因为它主动承认传统 structural baselines 在公平 tube-occupancy 协议下不是失败样本。

支持数值：最终深度 9 个 case/method 组合全部 `occ_comp_6n=1`, `occ_lcr_6n=1.0`, `root_component_ratio=1.0`, `path_to_root_rate=1.0`, `orphan_tip_count=0`。

### Claim B：传统 procedural baseline 是结构控制强 baseline，不是 texture/asset-ready 上界

可写：

> The matched structural matrix separates structural control from material/export quality: procedural methods are strong connected-support baselines under tube occupancy, while separate matched-guide texture diagnostics show that the same procedural supports do not automatically become single-component textured GLB assets after Trellis2 export.

支持数值：

- baseline matrix：传统 L-system 和 space-colonization occupancy 都单连通。
- matched-guide texture diagnostic：space-colonization root `218 / 0.524`，space-colonization tree `278 / 0.364`，L-system branch `315 / 0.115`，IFS branch tree `62 / 0.920`。

注意：这两组协议不同，必须写成“separate diagnostic”，不能把 texture diagnostic 当作 matched matrix 的延伸。

### Claim C：proposed proxy 展示了 projection-positive 递归语义，但不是完整 Trellis2 sparse-latent pipeline

可写：

> In the local matrix, the proposed connected scaffold acts as a projection-positive proxy: every displayed depth remains root-attached and occupancy-connected, exposing the intended invariant before running the full sparse latent decode-project-encode pipeline.

支持数值：

- tree proposed depth 1--4：`occ_comp_6n=1`, `occ_lcr_6n=1.0`, projection survival ratio `0.895, 0.845, 0.830, 0.848`。
- root proposed depth 1--4：`occ_comp_6n=1`, `occ_lcr_6n=1.0`, projection survival ratio `0.907, 0.866, 0.840, 0.858`。
- vine proposed depth 1--4：`occ_comp_6n=1`, `occ_lcr_6n=1.0`, projection survival ratio `0.917, 0.925, 0.918, 0.918`。

### Claim D：complexity/control differences can be reported descriptively

可写成 descriptive metrics，不写成 superiority：

- L-system：规则化分叉，最终 depth tips：tree=27, root=27, vine=4。
- Space-colonization：高 tip/branch count 和 attractor coverage，最终 depth tips：tree=143, root=118, vine=124。
- Proposed proxy：更稀疏、更受 projection 控制，最终 depth tips：tree=9, root=7, vine=6。

合理句式：

> The protocols produce different structural regimes: L-systems emphasize regular branching, space colonization produces dense attractor coverage, and the connected scaffold proxy is intentionally sparse because each depth is projected back to a root-attached admissible support.

## 3. 不能写的 claim

### 不能写：proposed 在 matched matrix 中 connectivity 优于 L-system/space-colonization

原因：最终 depth 以及 per-depth occupancy 指标里，传统方法也全部 `occ_comp_6n=1`, `occ_lcr_6n=1.0`。

如果论文需要“per-depth projection beats direct/final-only”的 claim，应继续使用当前主稿 Table `projection-ablation` 的 direct/final-only/per-depth 数据，而不是这组三方法 matrix。

### 不能写：传统 baseline 在结构上失败

原因：在公平 tube-occupancy 协议下传统 baseline 很强。可以说传统方法是 structural-control baseline，可以说 texture diagnostic 暴露 export fragmentation；不能说它们结构连通失败。

### 不能写：baseline matrix 证明 proposed 是完整 generation-model-native pipeline

原因：`proposed_connected` 是 connected scaffold/projection-positive proxy，不是完整 sparse latent decode-project-encode，也不经过 Trellis2 texture/GLB。

### 不能写：texture/material 质量或 GLB asset-ready 由 baseline matrix 支撑

原因：baseline matrix 是 structure-first OBJ mesh render，不经过 Trellis2 texture/GLB。texture claim 只能引用 traditional matched-guide texture diagnostic 或 selected projected textured GLB 表。

### 不能写：space-colonization depth 与 grammar derivation depth 完全公平等价

原因：文档已标注 space-colonization depth 是 iteration budget 对齐，不等同于 grammar derivation depth。可保留 `graph_max_depth` 暴露这个限制。

### 不能写：mesh topology clean

原因：primary metric 是 voxel occupancy 6N proxy。mesh component count 对 tube mesh、UV/material islands、未焊接面敏感，只能作为 diagnostic。

## 4. 推荐论文放置方案

### 主文位置

建议放在 `\subsection{Baselines}` 或 Results 中 traditional baseline figures 后，作为一个短段落 + 精简表格：

> We additionally run a matched structural baseline matrix for tree/root/vine under the same root, seed, depth, and mesh renderer. This matrix is not used to claim that our proxy out-connects classical procedures: all methods are root-attached and occupancy-connected under the fair tube-occupancy protocol. Instead, it separates structural-control baselines from the projection-ablation and texture-export claims.

主文表格只放最终深度，每个 case/method 一行，保留：

- case
- method
- occ comps
- occ LCR
- root ratio
- tips
- branch nodes
- mesh comps

可以把这个表格作为 `Table S?` 提前放 supplement；如果主文篇幅紧，主文只放一句并引用 supplement。

### 补充材料位置

完整内容放 supplement 的 `Matched Structural Baseline Matrix` 小节：

- protocol
- per-depth metrics CSV
- final-depth contact sheet
- per-depth OBJ 路径
- space-colonization depth/iteration caveat
- proposed proxy caveat
- mesh component vs occupancy component 解释

### 与现有主文元素的关系

- `Table projection-ablation`：仍是主证据，支持 direct/final-only/per-depth projection 的方法 claim。
- `traditional_matched_texture_baseline` figure：是 texture/export diagnostic，支持“texture alone is insufficient”。
- 新 baseline matrix：是 fairness/sanity check，支持“我们没有把传统结构 baseline 设成 strawman”。
- `claim_aligned_metric_summary`：适合继续作为主文 claim 边界总览。

## 5. 主文/补充材料分流

### 主文可放

1. 一句 protocol summary：
   same root, same seed, depth 1--4, same mesh renderer, tree/root/vine。
2. 一句 key result：
   all three structural families are occupancy-connected and root-attached at final depth。
3. 一句 interpretation：
   the matrix is a fairness check, while projection advantage is evaluated in the direct/final-only/per-depth ablation。
4. 可选精简表格：
   9 行最终 depth 结构指标。

### 补充材料必须放

1. 完整 `metrics.csv`。
2. Contact sheet：`results/baseline_matrix_20260509/contact_sheet_final_depth.png`。
3. Per-depth metric table 或 aggregated per-depth plots。
4. Caveat：space-colonization depth 是 iteration-budget matched。
5. Caveat：proposed 是 connected scaffold proxy。
6. Caveat：texture/export 不在该矩阵中评估。
7. Caveat：occupancy 6N 是 primary metric，mesh components 是 diagnostic。

### 不建议放主文

- 全部 per-depth 36 行表格。
- OBJ 路径。
- projection survival ratio 全部细节。
- 只凭 mesh component count 给传统方法判负。

## 6. 需要新增的最小补实验列表

优先级按“补上后能让论文 claim 闭环”的程度排序。

### P0：direct / final-only / prune-per-depth / bridge-per-depth / proposed per-depth matched matrix

目的：把当前 baseline matrix 从 structural sanity check 升级为真正方法 ablation。

最小设置：

- Cases：tree, root, vine。
- Depth：1--4。
- Same root：`(0,0,0)`。
- Same seed：固定 `20260509` 或新固定 seed。
- Same renderer：沿用当前 mesh renderer。
- Methods：
  - `direct_sparse_grammar`：不做 projection，直接递归到最终深度。
  - `final_only_projection`：递归中不投影，只对最终 depth 做一次 connected projection/pruning。
  - `prune_per_depth`：每层只保留 root-connected largest/admissible component，不添加 bridge。
  - `bridge_per_depth`：每层允许 bridge repair，再 re-encode/继续递归。
  - `proposed_per_depth`：当前论文定义的 projection-stabilized transition。
  - 可保留 `lsystem` 和 `space_colonization` 作为 structural baselines，但它们不替代上述 ablation。

必须记录：

- `occ_comp_6n`
- `occ_lcr_6n`
- `root_component_ratio`
- `orphan_mass_ratio`
- `path_to_root_rate`
- `orphan_tip_count`
- `tips`
- `branch_nodes`
- `graph_max_depth`
- `projection_survival_ratio`
- `bridge_added_voxels` 或 `bridge_mass_ratio`
- `pruned_voxels` 或 `pruned_mass_ratio`
- `mesh_component_count`
- render status

论文用途：

- 主文：支持“projection inside recursive transition beats direct/final-only”。
- 补充：展开 prune vs bridge 的失败模式。

### P0：zoom QA for root / junction / tip

目的：避免只看 overview contact sheet，补审稿人最容易质疑的局部结构证据。

最小设置：

- Cases：tree, root, vine。
- Methods：至少 `lsystem`, `space_colonization`, `direct_sparse_grammar`, `final_only_projection`, `prune_per_depth`, `bridge_per_depth`, `proposed_per_depth`。
- Views：
  - neutral overview front/side/top/iso；
  - root attachment zoom；
  - primary junction zoom；
  - terminal tip zoom；
  - optional failure zoom for orphan/fake bridge。

必须固定：

- camera focal length；
- orthographic scale；
- lighting；
- material；
- crop size；
- mesh renderer。

论文用途：

- 主文最多放一组 proposed vs strongest baseline 的 zoom。
- 补充放完整 grid。

### P1：matched-guide texture export on the same matrix winners

目的：连接 structural matrix 和 texture diagnostic，但不混淆两者。

最小设置：

- 对每个 case 选择同一 appearance guide；
- 对 `lsystem`, `space_colonization`, `proposed_per_depth` 各取 final depth mesh；
- 跑同一 Trellis2 texture/PBR schedule；
- 报告 GLB import/render status、occupancy comps/LCR、raw face components、PBR token count、visual failure label。

论文用途：

- 支持“texture path is compatible with selected projected meshes, but material transfer alone is not structural repair”。

### P1：coverage / collision metrics for space-colonization

目的：公平记录 space-colonization 的强项，避免 baseline 章节显得只挑对我们有利的指标。

最小指标：

- attractor coverage ratio；
- mean nearest-attractor distance；
- collision/self-intersection proxy；
- bounding box occupancy；
- tips per occupied volume。

论文用途：

- 补充材料 fairness table。

### P2：IFS 加入 matched structural matrix

原因：matched-guide texture diagnostic 中 IFS 是最强传统 baseline，`LCR=0.920`，不能长期缺席 matched structural matrix。

最小设置：

- 加入 `ifs_branch_tree` 或 transform-copy family；
- same root/depth/seed；
- same neutral renderer；
- same occupancy and root metrics。

## 7. 精简 LaTeX 表格建议

已生成草稿：

- `paper_siga/drafts/baseline_matrix_table_20260509.tex`

推荐用法：

- 若放主文：表格 caption 必须写明这是 matched structural baseline matrix，不是 projection ablation。
- 若放补充：可以保留当前 9 行最终 depth 表格，并在主文 Results 中一句引用。

表格核心 caption 应包含：

> All methods are evaluated under the same root, seed, maximum depth, and mesh-render protocol. Occupancy connectivity is measured by a voxel 6-neighborhood proxy. The table is a structural sanity check rather than evidence that the proposed proxy out-connects classical procedures.

## 8. 最终写作建议

最稳论文叙事顺序：

1. 先用 projection ablation table 证明 direct/final-only 不够，per-depth projection 对 conservative branching 有效。
2. 再用 matched structural baseline matrix 承认传统 methods 在公平 tube occupancy 下也是 strong connected structural baselines。
3. 再用 matched-guide texture diagnostic 说明 texture export alone 不能把 traditional scaffolds 自动变成 single-component textured assets。
4. 最后用 selected Trellis2 textured GLB rows 说明 proposed projected meshes 可以进入 texture/export path，但不把 texture 当作 topology proof。

一句话判断：当前 baseline matrix 可以写进论文，但只能作为 fairness/sanity check 和 structural-control context；论文主 claim 仍必须依赖 direct/final-only/per-depth projection ablation，以及新增的 prune-per-depth、bridge-per-depth、zoom QA 来闭环。
