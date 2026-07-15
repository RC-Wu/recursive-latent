# Claim-Aligned Metric Summary 20260509

范围：本文件汇总当前本地已有 metric CSV/JSON 与评审闭环文档，目标是把论文可写 claim、负面证据、待补实验分开。本文不修改 `paper_siga/main.tex`，也不新增远端/GPU 实验。

生成产物：

- 结果目录：`results/claim_aligned_metric_summary_20260509/`
- 主表：`results/claim_aligned_metric_summary_20260509/claim_aligned_metric_summary.csv`
- 长表：`results/claim_aligned_metric_summary_20260509/claim_aligned_metric_long.csv`
- 图：`paper_siga/figures/claim_aligned_metric_summary_20260509.pdf`
- 图 PNG：`paper_siga/figures/claim_aligned_metric_summary_20260509.png`
- LaTeX 表：`paper_siga/figures/claim_aligned_metric_summary_table_20260509.tex`
- 生成脚本：`assets/claim_aligned_metric_summary_20260509.py`

## 1. 总体结论

当前最稳的正面证据是 **occupancy 6-neighborhood connectedness**，而不是 raw face / textured GLB mesh topology。可以写 per-depth voxelized occupancy support 的连通性；不能写所有导出 mesh 都 topology-clean，也不能写真实 DLA/crystal growth 已经解决。

| Family | 当前正面证据 | 当前负面 / caveat | 现在可写 claim | 不能写 |
|---|---|---|---|---|
| vine/root/tree | vine textured stages 1-4: `occ_comp_6n=1`, `occ_lcr_6n=1.0`; root reachability proxy 为 1.0 | textured GLB raw face components 约 85k-107k，face LCR 约 0.001-0.002；branch/path 仍是 mesh-voxel proxy | projection-stabilized vine showcase keeps voxelized 6N occupancy support connected across displayed depths | tree/root/vine assets are fully topology-clean or systematically beat traditional baselines |
| bismuth | source depth scaffold stages 1-4: `occ_comp_6n=1`, `occ_lcr_6n=1.0`; mesh component 2-4，mesh LCR 约 0.999-1.000 | 只是 bismuth-like scaffold；缺 facet/contact/neutral zoom QA；HQ GLB 仍有 occupancy component 2 | bismuth-like non-tree scaffold can be kept occupancy-connected across depth | bismuth crystallization or physical growth is solved |
| pyrite | source depth scaffold stages 1-4: `occ_comp_6n=1`, `occ_lcr_6n=1.0` | mesh component count 从 1 增到 139；GLB raw face fragmentation 仍严重 | pyrite-like lattice scaffold maintains connected voxel support across depth | crystal generation/topology is solved at mesh-face level |
| DLA/coral | grammar-native `volumetric_coral_depth` source stages 1-4: `occ_comp_6n=1`, `occ_lcr_6n=1.0` | DLA bridge ablation 的 occupancy components 为 4-9；视觉有 fake bridge / over-closing | DLA/coral is a stress test motivating grammar-native connected support | true DLA growth/frontier process is solved |

## 2. 指标对齐表

| Case | Occ comp / LCR | Mesh or face comp / LCR | Effective resolution / proxy | Branch/path proxy | Visual pass/fail |
|---|---:|---:|---|---|---|
| `vine_d5_projected_compete` | 1 / 1.000 | 85381-107213 / 0.001-0.002 | occ64 occupied voxels 6016-6188；box-count curve available | root ratio 1.0, path span 1.048-1.307, orphan tip proxy 0；mesh proxy only | textured asset exists；neutral/zoom QA missing |
| `bismuth_hopper_depth` | 1 / 1.000 | 2-4 / 0.999-1.000 | occupied voxels 45885-59574 | not measured | pending neutral/zoom QA |
| `pyrite_lattice_depth` | 1 / 1.000 | 1-139 / 0.998-1.000 | occupied voxels 45996-232441 | not measured | pending neutral/zoom QA |
| `volumetric_coral_depth` | 1 / 1.000 | 1-12 / 0.999-1.000 | occupied voxels 35719-125958 | not measured；needs frontier/porosity metrics | pending neutral/zoom QA |
| `dla_bridge_ablation` | 4-9 / 0.387-0.961 | 1-8 / 0.301-1.000 | mesh-only QA summary | not measured | mostly fail；best bridge still has `occ_comp=4` |

## 3. 正面证据边界

1. **Vine/root/tree**  
   可以作为主文候选的是 vine depth showcase 的 occupancy-depth stability：四个 textured stages 都是 `occ_comp_6n=1` 和 `occ_lcr_6n=1.0`，branch/root proxy 里 root ratio 也是 1.0。写法必须限定为 voxelized 6N occupancy support 和 mesh-voxel root reachability proxy。

2. **Bismuth**  
   `bismuth_hopper_depth` 是 non-tree scaffold 的较稳正例。四层 occupancy 都连通，mesh component 很低且 LCR 高。它可以支持“bismuth-like scaffold”或“non-tree connected scaffold”，不能支持真实 bismuth crystallization。

3. **Pyrite**  
   `pyrite_lattice_depth` 可以支持 connected voxel support；但 mesh component 从 1 增到 139 是必须正面交代的负面诊断。它适合写成 lattice scaffold candidate，而不是 clean crystal topology。

4. **DLA/coral**  
   `volumetric_coral_depth` 的 grammar-native source scaffold 是 occupancy-connected 的 stress positive；但 DLA/coral 的主叙事应是“post-hoc bridge 不足，必须在 grammar proposal 阶段保持 connected support”。除非补齐 true DLA/frontier baseline、porosity/cavity、over-closing label 和 zoom QA，否则不能作为主文成功 claim。

## 4. 负面证据必须保留

- Vine textured GLB raw face components 极高，说明 texture/export surface splitting 不能被 occupancy connectedness 掩盖。
- Pyrite source depth mesh components 随 depth 增长明显，说明 face-level mesh diagnostics 与 occupancy connectedness 不一致。
- DLA bridge ablation 中，`raw_bridge_smooth` 可出现 face component 为 1 但 occupancy component 仍为 6 的情况；这直接证明 face connectivity 或 LCR 不能单独作为主指标。
- `sparse_close_bridge` / `mesh_bridge_smooth` 的视觉 QA 标记包含 fake bridge、over-closing、不可用等，不应进入正例图。

## 5. 待补定量实验

优先级 1：tree/root/vine 公平 baseline 矩阵。

- 同 root、同 depth、同 seed、同 renderer。
- Methods：L-system、space-colonization、direct sparse grammar、final-only cleanup、prune-per-depth、bridge-per-depth、proposed。
- Metrics：skeleton/root anchor、path-to-root rate、root component ratio、orphan mass、tip count、branch nodes、orphan tips。
- QA：neutral front/side/top/iso render，以及 root attachment、junction、tip zoom。

优先级 2：bismuth/pyrite scaffold 语义指标。

- Same-root IFS/lattice baseline、direct、final-only、connected scaffold v2、bridge/contact constrained。
- Metrics：facet size distribution、face-contact count、contact area、symmetry/contact error、cavity proxy。
- QA：neutral facet/contact/cavity zoom；winner 再做 PBR completeness。

优先级 3：DLA/coral stress 和负例闭环。

- True voxel DLA / frontier accretion baseline、direct frontier、final-only closing、prune、bridge、bridge+cache。
- Metrics：frontier attachment rate、branch openness、porosity/cavity proxy、bridge survival、fake bridge / over-closing labels。
- QA：thin neck、frontier branch、cavity、over-closing zoom。

## 6. 推荐论文写法

推荐主文只写：

> We evaluate connected support as a hard per-depth invariant using voxelized 6-neighborhood component count and largest-component ratio, and report mesh/face diagnostics separately to expose export and surface fragmentation. The current evidence supports connected voxel support for the vine showcase and non-tree scaffold candidates, while DLA/coral remains a stress-test and negative-ablation setting rather than a solved growth model.

不推荐写：

> Our method solves tree, crystal, bismuth, and DLA topology.

原因：当前证据还没有同 root baseline matrix、可靠 skeletonization、family-specific semantic metrics、neutral render/zoom QA。
