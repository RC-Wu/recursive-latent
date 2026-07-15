# Strict matched PS-RSLG proxy visual audit 2026-05-10

范围：只审阅现有本地输出，不修改代码、不修改论文、不重跑实验、不重渲染图像。

- Structure outputs: `results/strict_matched_psrslg_proxy_20260510_seed310`
- Visual outputs: `visuals/strict_matched_psrslg_proxy_20260510_seed310`
- Contact sheet: `visuals/strict_matched_psrslg_proxy_20260510_seed310/strict_matched_proxy_contact_20260510.png`
- Manifest: `results/strict_matched_psrslg_proxy_20260510_seed310/manifest.csv`

## Executive verdict

这批结果可以作为 **strict matched-task structure proxy 的中间审计材料**，但不能直接作为 paper-grade 主图或定量胜负表。最重要的结论是：

1. PS-RSLG proxy 行在四个 case 的 occupancy 连通指标都为 `occ_comp_6n=1, occ_lcr_6n=1.0, root_ratio=1.0`，说明本地 projection/root-attachment scaffold 确实消除了传统 scaffold 在同一 voxel proxy 下的大量碎片。
2. 视觉/task matching 只有 Space Colonization 和 DLA 可以暂时保留为 matched-mode proxy；L-system 和 IFS 当前失败，主要问题是 blob 化、分支语义丢失和方向/transform orbit 不对齐。
3. 这些图最多支撑“我们正在用同递归模式构造 connected structure proxy”的研发状态，不能支撑“PS-RSLG 已 paper-grade 优于 L-system/SC/DLA/IFS”。

## Pair-level verdict table

| Case | Matched-task proxy verdict | Visual/task matching verdict | 主要证据 | 论文使用建议 |
|---|---|---|---|---|
| `lsystem_pine_canopy` | Reject for matched L-system claim | Fail | baseline 与 ours 都呈团块/短粗 blob，几乎看不到 pine/tree canopy 的 branch hierarchy、tip distribution 或 turtle-rule 分叉；ours 虽 `1/1/1` 连通，但更像 naturalized lump | 只能放 failure appendix，不能进主表正例 |
| `space_colonization_tree_canopy` | Keep as provisional structure proxy | Partial visual pass | same attractor-driven canopy mode 明确；ours 保持 root-connected 且有 crown mass；但 naturalization 把 SC skeleton 变成密集 cauliflower canopy，branch readability 和 attractor coverage 未量化 | 可作为下一轮重点正例候选，但必须补 coverage、branch/path、zoom 和多 seed |
| `dla_crystal_cluster` | Keep as provisional stress proxy | Partial visual pass with risk | baseline 是 blocky DLA hit cluster；ours 保留 cluster/frontier 外轮廓并 root-connected；但 smooth/naturalized surface 可能过度桥接，且 crystal/DLA 物理语义、seed orientation、cavity preservation 未证明 | 可作为 DLA/frontier stress row，不可写成 true physical DLA solved |
| `ifs_transform_branching_tree` | Reject for matched IFS branch-tree claim | Fail | baseline 是清楚的 affine transform-copy branching fan；ours 变成 compact porous blob 加少量 tube，self-similar copy orbit、branch fan、scale decay 和方向关系都丢失 | 只能作为 operator_not_supported / transform-copy failure |

## Detailed notes

### 1. L-system pine canopy

Manifest claims:

- Traditional: symbolic turtle branching, `vertices=1257`, `faces=2518`, `occ_comp_6n=1`, `occ_lcr_6n=1.0`, `root_ratio=1.0`.
- Ours: same L-system skeleton with connected sparse support, tip naturalization and root projection, `vertices=2214`, `faces=4424`, `occ_comp_6n=1`, `occ_lcr_6n=1.0`, `root_ratio=1.0`.

Audit:

- The metrics pass is not informative here because both rows are already single connected supports.
- Visual result fails the task. A pine canopy / L-system tree should expose branch hierarchy, terminal tips, angle/length schedule, and at least a readable trunk-to-branch relation. The contact sheet shows two compact irregular blobs with a short protrusion; this reads as a smoothed mass, not as L-system branch rewriting.
- This is the clearest L-system blob problem in the set. The PS-RSLG row may have inherited the L-system skeleton internally, but the rendered geometry does not preserve enough visible task structure.
- Orientation is also weak: the object is normalized around the origin with a vertical bbox span, but the shown view reads sideways/horizontal. For tree/canopy comparison the root/trunk base and upright axis need to be fixed and visible.

Verdict: fail. Do not use as evidence of matched L-system success.

Next experiments needed:

1. Rebuild `lsystem_pine_canopy` with explicit skeleton-visible tubes before any naturalization; preserve per-segment branch IDs and tip IDs.
2. Add an ablation row: traditional L-system, direct PS-RSLG branch grammar, PS-RSLG without naturalization, PS-RSLG with weak masked tip-only naturalization.
3. Report branch angle distribution, branch length distribution, tip count, branch node count, path-to-root rate, and silhouette/canopy coverage.
4. Render upright front/iso/top plus root, primary junction, and terminal-tip zoom. The root/base must be at the bottom and the trunk/branch hierarchy must remain visible.
5. Run at least 4 seeds and 2 depth budgets; report mean/std and failure count, not a single selected mesh.

### 2. Space-colonization tree canopy

Manifest claims:

- Traditional: attractor-field crown growth, `vertices=32040`, `faces=32040`, `occ_comp_6n=778`, `occ_lcr_6n=0.130879`, `root_ratio=0.000779`.
- Ours: same attractor-driven competition skeleton with connected sparse interpretation and local naturalization, `vertices=137285`, `faces=278340`, `occ_comp_6n=1`, `occ_lcr_6n=1.0`, `root_ratio=1.0`.

Audit:

- This is the strongest matched-mode candidate in the current batch. Both rows target attractor-driven canopy growth, and ours visibly forms a single dense crown with a root/stem-like protrusion.
- The traditional baseline is structurally strong in the visual domain: its branch skeleton is readable and naturally aligned with SC controls. The manifest occupancy metric penalizes it heavily, but that may partly reflect tube/voxel sampling rather than a true task failure.
- Ours has a real strength: connected support and dense organic mass are visually stable. It is closer to an asset-ready canopy than the skeletal SC baseline.
- Main risk: over-naturalization hides the SC branch competition process. The result reads as a connected lumpy crown, but it does not yet prove attractor coverage, uncovered-attractor ratio, branch length distribution, or tip competition quality.

Verdict: keep as provisional structure proxy, not paper-grade yet.

Next experiments needed:

1. Re-run SC with identical attractor set, influence radius, kill radius, step size and iteration/depth budget for traditional, direct PS-RSLG, final-only projection, per-depth prune, bridge-aware projection, and masked naturalization.
2. Add SC-specific metrics: attractor coverage, uncovered-attractor ratio, nearest-attractor distance distribution, branch length distribution, tip count, branch node count, collision/rejection count, and root path length.
3. Separate topology from appearance: report skeleton graph metrics before surface naturalization and surface/voxel connectivity after naturalization.
4. Render camera-level overview and zooms: root/stem attachment, internal junction region, terminal canopy tips, and a representative dense crown region.
5. Run seed robustness: at least 4 attractor seeds and one stress case with sparse attractors. Report success/failure rates and do not select only the best crown.

### 3. DLA crystal cluster

Manifest claims:

- Traditional: random-walk hitting and accretive particle attachment, `vertices=7200`, `faces=10800`, `occ_comp_6n=3232`, `occ_lcr_6n=0.000309`, `root_ratio=0.000309`.
- Ours: same DLA hit set with frontier-local masked naturalization and root-attached projection, `vertices=46339`, `faces=95900`, `occ_comp_6n=1`, `occ_lcr_6n=1.0`, `root_ratio=1.0`.

Audit:

- This is a useful stress proxy because the baseline has a clear DLA/block accretion look and the PS-RSLG row visibly keeps a branched cluster silhouette while connecting the support.
- The strength is not “DLA solved”; the strength is that frontier-local naturalization plus projection can turn a highly fragmented DLA hit-set proxy into one root-attached surface support.
- Visual risk is substantial. The PS-RSLG object may over-bridge sparse hits and erase physical accretion evidence. The surface is less blocky and more asset-like, but cavity preservation, frontier validity and fake-bridge rate are unknown.
- Crystal wording is risky. The baseline is a voxel DLA cluster, not a clean faceted crystal; ours is naturalized porous cluster, not a verified crystal lattice or facet-preserving growth.
- Orientation/root policy is underdefined. A DLA seed can be center seed, bottom attachment, or nucleus; the current render does not make that choice visually explicit.

Verdict: keep as provisional DLA/frontier stress proxy with explicit caveats.

Next experiments needed:

1. Define DLA root policy: center nucleus, bottom attachment, or prescribed seed. Use the same root policy in all rows and show it in zoom.
2. Add rows for raw DLA, direct PS-RSLG frontier attachment, final-only projection, per-depth bridge-aware projection, masked local naturalization, and over-bridge negative.
3. Report DLA/frontier metrics: frontier attachment survival, effective stickiness, orphan frontier rate, fake bridge count, porosity/cavity count, surface-to-volume proxy, blockiness, Euler proxy, and root-connected frontier ratio.
4. Add visual zooms for seed/root attachment, frontier branch, cavity/void, terminal cluster, and suspected bridge.
5. Run at least 4 seeds and one high-stickiness / low-stickiness sweep. Paper-grade claim requires mean/std plus failure examples.
6. Rename in paper-facing material unless faceting is measured: use `DLA/frontier porous cluster` instead of `crystal` when facet/lattice metrics are absent.

### 4. IFS transform branching tree

Manifest claims:

- Traditional: recursive contractive transform-copy branching tree, `vertices=21860`, `faces=21860`, `occ_comp_6n=529`, `occ_lcr_6n=0.043128`, `root_ratio=0.000322`.
- Ours: transform-copy anchor grammar with connected sparse projection and local tip kernels, `vertices=45839`, `faces=93200`, `occ_comp_6n=1`, `occ_lcr_6n=1.0`, `root_ratio=1.0`.

Audit:

- The baseline visibly exposes the IFS task: a branching fan with repeated tapered copies and a clear transform hierarchy.
- The PS-RSLG row fails the visual task. It reads as a compact porous blob with a few tubes, not as an affine transform-copy branch tree.
- This is both a blob problem and an orientation/orbit problem. The baseline has a diagonal branch fan and visible level-to-level scale decay; ours is normalized into a compact central mass with no readable self-similar orbit.
- Connectivity metrics are misleading here: `1/1/1` root connectivity is achieved by sacrificing the transform-copy task.

Verdict: fail. Mark as `operator_not_supported` or `transform_orbit_lost`, not as matched IFS success.

Next experiments needed:

1. Implement/verify an explicit PS-RSLG transform-copy operator with per-copy IDs, affine matrices, scale decay, rotation schedule, and parent-child orbit records.
2. Add transform metrics: transform orbit error, copy survival ratio, self-similarity score, branch topology edit distance, scale drift, and path-to-root per copy.
3. Compare traditional IFS, direct transform-copy grammar, final-only projection, per-depth projection, and masked local tip naturalization with naturalization strength swept from none to weak to strong.
4. Render overview plus level-0 motif, level-1 copy, terminal copy, and self-similarity zoom. The copy hierarchy must be visible without relying on metrics.
5. Add an explicit failure row where naturalization is too strong and collapses the orbit into a blob; the current ours row likely belongs there.

## SC and DLA strengths / risks

### Space colonization strengths

- Same recursive mode is plausible: attractor competition and canopy growth are aligned across baseline and ours.
- Ours visibly converts a fragmented occupancy proxy into a single root-attached crown.
- This case can become paper-grade fastest because SC has well-defined coverage and branch-path metrics.

### Space colonization risks

- The traditional SC baseline is a strong structural baseline, not a strawman. It may outperform ours on branch readability, attractor coverage, and controllability.
- Ours may be asset-like but over-smoothed/over-dense. Without coverage and branch metrics, the lumpy crown could be visually pleasing but structurally less faithful.
- Contact-sheet scale/camera is not enough; root, junction and terminal-tip zooms are required.

### DLA strengths

- This is a useful stress test for projection and masked local naturalization because raw DLA hit sets are sparse, blocky and fragment-prone.
- Ours has a clear root-connectivity improvement in the manifest and a more continuous surface in the render.
- The pair can support a conservative claim about connected frontier proxy construction if failure cases and bridge metrics are included.

### DLA risks

- Over-bridging can create fake connectivity and destroy DLA porosity/cavity structure.
- Smooth naturalization can make the result look more asset-like while drifting away from frontier accretion physics.
- `crystal` wording is too strong unless facet, anisotropy, lattice/contact or symmetry metrics are added.
- Orientation/root policy must be made explicit. DLA is not inherently upright, so the seed/base convention has to be pre-registered.

## Minimum paper-grade experiment package

Before any of these pairs enter the paper as positive evidence, the next package should be:

1. **Matched row matrix per family**: traditional baseline, direct sparse grammar, final-only projection, per-depth prune projection, bridge-aware projection where relevant, and full masked naturalization.
2. **Multi-seed reporting**: at least 4 seeds per family, with failure counts and mean/std for metrics.
3. **Family-specific metrics**:
   - L-system: branch angle/length, tip count, branch nodes, path-to-root, canopy silhouette.
   - SC: attractor coverage, uncovered attractors, branch/path statistics, collision/rejection.
   - DLA: frontier validity, fake bridge, porosity/cavity, blockiness, effective stickiness.
   - IFS: transform orbit error, copy survival, self-similarity, scale drift.
4. **Visual protocol**: pure-white fixed-camera overview plus root/seed, junction/frontier, terminal tip/cavity/copy zooms. Use camera-level zooms, not 2D crops.
5. **Ablation on naturalization strength**: no naturalization, weak masked local, strong masked local, and global/over-smooth negative.
6. **Claim gating**: only SC and DLA can proceed as near-term positive candidates; L-system and IFS must first fix blob/orientation/orbit failures.

## Allowed and disallowed claims

Allowed from this batch:

- “The strict matched proxy run contains same-family/same-mode scaffolds for L-system, SC, DLA and IFS, with PS-RSLG proxy rows enforcing root-connected occupancy support.”
- “SC and DLA are promising but incomplete matched-mode structure proxies.”
- “L-system and IFS currently expose failure modes where connectivity is achieved but visual/task structure is not preserved.”

Not allowed from this batch:

- “PS-RSLG beats L-system/SC/DLA/IFS.”
- “The L-system and IFS matched tasks are solved.”
- “DLA crystal growth is physically reproduced.”
- “Connectivity metrics alone prove visual or recursive-task fidelity.”
- “These renders are paper-grade final figures.”
