# Baseline case pool 推荐与 claim gate 更新（2026-05-10）

作者：R-SLG baseline/metrics 汇总 worker  
执行范围：本地只读结果与文档；未 SSH；未覆盖 `results/` 文件；仅新增本文档。  

## 0. 本轮结论

当前最适合主文的对比不是“全 baseline 大表”，而是一个小而硬的受控表：

1. **主文首选 1：pyrite / recursive lattice**。Trellis2 one-shot、latent copy、mesh-space generated-root 都已有可比负控；PS-RSLG strict row 为 success，occupancy comps=1、LCR=1.000。Hunyuan shape-only `pyrite_lattice` 已生成并通过 import/render QA，可作为 secondary one-shot appendix 或主文 claim-gated row。
2. **主文首选 2：coral / frontier**。Trellis2 one-shot、latent copy、PS-RSLG strict 均已有；coral mesh-space generated-root 已在后续状态文档中闭合，但 master CSV/LaTeX 仍未同步。Hunyuan `coral_frontier` 已生成并通过 import/render QA。
3. **主文候选 3：vine / L-system grammar**。Trellis2/latent/mesh-space/ours rows 已有，但 strict vine 弱；主文若放 vine，应使用 `stronger vine stage5 reference`，并把 Hunyuan `vine_lsystem_grammar` 当作 ordinary shape-only generated row，而不是递归语义成功。

一句话推荐：主文放 `pyrite + coral` 两个强非树 case；若需要 botanical 覆盖，再加 `vine stage5`。Hunyuan/TRELLIS classic 的完整池放附录或 claim-gated 扩展表，避免把 runnable/generated 误写成 topology/recursive semantics 成功。

## 1. 证据路径

### 计划与状态

- `docs/progress/ralph_publication_closure_plan_20260510.md`
- `docs/evaluation/hunyuan3d_recursive_guide_baseline_status_zh_20260510.md`
- `docs/evaluation/baseline_case_pool_recommendations_zh_20260510.md`
- `docs/evaluation/publication_baseline_case_metric_plan_zh_20260510.md`
- `docs/evaluation/coral_mesh_space_generated_root_status_zh_20260510.md`

### 结果与 QA

- Hunyuan full-pool metrics: `results/publication_hunyuan_recursive_guides_20260510/hunyuan_recursive_guides_fullpool_metrics.csv`
- Hunyuan import QA: `results/publication_hunyuan_recursive_guides_20260510/local_trimesh_import_qa_fullpool_20260510.json`
- Hunyuan render QA: `results/publication_hunyuan_recursive_guides_20260510/render_qa_fullpool_white_600_summary.json`
- Hunyuan flattened renders: `results/publication_hunyuan_recursive_guides_20260510/render_qa_fullpool_white_600/flattened_white/`
- Existing gen3d summary: `results/gen3d_baseline_metrics_20260510/gen3d_baseline_summary_table_20260510.csv`
- Current master manifest: `results/publication_baseline_metrics_20260510/publication_baseline_master_manifest_20260510.csv`
- Current LaTeX draft: `results/publication_baseline_metrics_20260510/publication_baseline_table_draft_20260510.tex`
- Coral mesh-space closure: `results/publication_coral_mesh_space_20260510/coral_mesh_space_metrics.csv`

## 2. 推荐候选 case pool

下表是 Hunyuan / TRELLIS / Trellis2 / ours 合并后的候选池。`主文优先` 只表示适合进入主文小表，不表示所有方法行已经完整闭合。

| rank | case | families covered | 当前证据 | 推荐位置 | claim-safe 用法 |
|---:|---|---|---|---|---|
| 1 | `pyrite_lattice` / pyrite recursive lattice | Hunyuan shape-only, Trellis2 one-shot, Trellis2 latent copy, mesh-space generated-root, ours | Hunyuan V=2058208/F=4119162/import OK/render QA；Trellis2 one-shot LCR=0.127；latent LCR=0.102；mesh-space LCR=0.033；ours LCR=1.000 | **主文最适合** | 普通 one-shot / trivial recursion 难以替代 projection-stabilized recursive asset evidence |
| 2 | `coral_frontier` / coral frontier | Hunyuan shape-only, Trellis2 one-shot, Trellis2 latent copy, coral mesh-space, ours | Hunyuan V=837923/F=1675900/import OK/render QA；Trellis2 one-shot LCR=0.600；latent LCR=0.824；ours LCR=1.000；coral mesh-space closure doc gives raw comps=250404 | **主文最适合** | 报告 copy-paste fragmentation 与 PS-RSLG connected asset evidence；不要只用 occupancy LCR 判失败 |
| 3 | `vine_lsystem_grammar` + stronger vine stage5 | Hunyuan shape-only, Trellis2 one-shot, Trellis2 latent copy, mesh-space, ours stage5 | Hunyuan V=745382/F=1484726/import OK/render QA；Trellis2 one-shot LCR=1.000；latent LCR=0.689；mesh-space LCR=0.813；stage5 ours LCR=0.999 | **主文可选第 3 个** | 用 stronger stage5 替代 weak strict vine；强调递归语义需 visual/zoom QA，不把 one-shot LCR=1 当成功 |
| 4 | `crystal_frontier` | Hunyuan shape-only, ours/strict crystal pool candidate | Hunyuan V=603372/F=1206740/import OK/render QA | 附录优先 | 可作为 Hunyuan 13-case pool 展示；缺同协议 Trellis2/mesh/ours 主表合并 |
| 5 | `frontier_sheet` | Hunyuan shape-only, DLA/frontier family | Hunyuan V=603748/F=1207488/import OK/render QA | 附录优先 | 展示 ordinary shape generator can output an importable mesh；不声明 frontier attachment semantics |
| 6 | `branch_ornament` | Hunyuan shape-only, IFS ornament | Hunyuan V=645778/F=1284416/import OK/render QA | 附录 | 适合 broad pool，不适合主文 claim-bearing comparison |
| 7 | `branch_tree` | Hunyuan shape-only, IFS/tree-like | Hunyuan V=571112/F=1133892/import OK/render QA | 附录 | 可与 plant/tree appendix 对齐；缺 root reachability/failure label |
| 8 | `radial_ornament` | Hunyuan shape-only, IFS/radial | Hunyuan V=671760/F=1334676/import OK/render QA | 附录 | 适合 showing coverage；不要写 symmetry/orbit preservation 已验证 |
| 9 | `root_network` | Hunyuan shape-only, space-colonization/root | Hunyuan V=690084/F=1372808/import OK/render QA | 附录 | root network 名称不能自动等于 path-to-root metric 通过 |
| 10 | `tree_crown` | Hunyuan shape-only, space-colonization/tree | Hunyuan V=621097/F=1234552/import OK/render QA | 附录 | 作为 botanical breadth；缺 same-root and task semantics metrics |
| 11 | `pine_grammar` | Hunyuan shape-only, L-system pine | Hunyuan V=603556/F=1207108/import OK/render QA | 附录 | 可作 L-system pool 补充；不进主文核心表 |
| 12 | `root_fan_grammar` | Hunyuan shape-only, L-system/root | Hunyuan V=603644/F=1207276/import OK/render QA | 附录 | 可作 root appendix；需 root reachability 后再增强 |
| 13 | `bush_shell` | Hunyuan shape-only, space-colonization/bush | Hunyuan V=603547/F=1207092/import OK/render QA | 附录/低优先 | 名称和视觉可能偏 generic；只作 generated pool row |

额外必须保留但不推荐主文正面叙事的 row：

| row | 状态 | 用法 |
|---|---|---|
| TRELLIS classic image one-shot: vine/pyrite/coral | still blocked / no local output in master CSV | 保留 blocked slot；不能写 TRELLIS classic 失败，只能写未完成/环境阻塞 |
| Hunyuan image+texture: vine/pyrite/coral | missing | 与 shape-only 分开；不能混入 Hunyuan shape-only row |
| Hunyuan + mesh-space generated-root | missing | 需要先从 Hunyuan root mesh 生成 direct copy/merge 负控 |
| weak strict `ours_vine` | needs candidate swap / QA | 不作为主文正例；用 stronger vine stage5 |

## 3. Master CSV / LaTeX 检查

已有文件：

- `results/publication_baseline_metrics_20260510/publication_baseline_master_manifest_20260510.csv`：26 行，含 header，实际 25 个 data rows。
- `results/publication_baseline_metrics_20260510/publication_baseline_table_draft_20260510.tex`：32 行。

已覆盖：

- Vine / pyrite / coral 的 Trellis2 one-shot、Trellis2 trivial latent、vine+pyrite mesh-space generated-root、ours strict rows、stronger vine stage5 row。
- TRELLIS classic、Hunyuan image one-shot、Hunyuan image+texture、Hunyuan mesh-space generated-root 的 future/blocked/missing slots。

当前缺口：

1. **Hunyuan shape-only rows 未同步**。master CSV/LaTeX 仍把 vine/pyrite/coral Hunyuan image one-shot 写成 blocked；新证据显示 13-case shape-only pool 已生成、13/13 local import OK、full-pool render QA 已有。应把 Hunyuan shape-only image one-shot 改为 generated/import-render-QA-done，但仍缺 connectivity/occupancy/failure labels。
2. **Coral mesh-space row 未同步**。master CSV/LaTeX 仍把 coral mesh-space generated-root 写 missing；`docs/evaluation/coral_mesh_space_generated_root_status_zh_20260510.md` 与 `results/publication_coral_mesh_space_20260510/` 显示该负控已闭合，推荐 row 为 `coral_frontier_branch full_srt depth=2 direct merge`。
3. **Hunyuan full-pool没有进入 master**。13 个 Hunyuan rows 可进 appendix master/secondary CSV，但主表只建议选 vine/pyrite/coral 三个。
4. **缺 Hunyuan connectivity/occupancy metrics**。现有 Hunyuan metrics 是 vertices/faces/file size/bounds/import/render QA；没有 raw/welded/occupancy components、LCR、root reachability、orphan/fragment ratio、failure labels。
5. **TRELLIS classic 仍缺 runnable output**。可保留 blocked slot，不能作为失败结论。
6. **Hunyuan image+texture 仍缺**。shape-only 不能替代 paint/textured baseline。
7. **LaTeX 草稿需要重生成**。当前表仍含旧 Hunyuan blocked rows、旧 coral mesh-space missing row，且未反映 Hunyuan generated/import QA 状态。

## 4. 主文最小表建议

推荐主文只放 2-3 个 case：

| case | Trellis2 one-shot | Trellis2 latent copy | mesh-space generated-root | Hunyuan shape-only | Ours / PS-RSLG | 主文地位 |
|---|---|---|---|---|---|---|
| pyrite | fragmented, LCR=0.127 | fragmented, LCR=0.102 | fragmented_copy_paste, LCR=0.033 | generated/import/render QA, missing topology metrics | success, LCR=1.000 | **主文核心** |
| coral | fragmented, LCR=0.600 | fragmented, LCR=0.824 | generated-root negative now complete; raw comps=250404, occ LCR=0.992 | generated/import/render QA, missing topology metrics | success, LCR=1.000 | **主文核心** |
| vine | one-shot LCR=1.000 but semantics not proven | fragmented, LCR=0.689 | fragmented_copy_paste, LCR=0.813 | generated/import/render QA, missing topology metrics | use stronger stage5, LCR=0.999 | 可选第 3 个 |

表注必须写清：

- Hunyuan row 是 **shape-only image one-shot**，不是 texture baseline，也不是 recursive state baseline。
- Hunyuan vertices/faces/file size 只证明 generated/importable mesh，不证明 root reachability、递归语义或拓扑正确。
- Coral mesh-space 的高 occ LCR 不能单独看作成功；需要同时报告 raw components、copy repetition、无 projection/repair。
- TRELLIS classic 若仍无 output，只能保留 blocked / not completed row。

## 5. Claim gate

可以写：

- Hunyuan3D 2.0 shape-only baseline 已从 feasibility/blocked 推进到 13 个 recursive guide case generated，并完成本地 import QA 与 full-pool white render QA。
- Pyrite/coral 是当前最适合主文的非树对比 case，因为 Trellis2 one-shot、latent copy、mesh-space direct-copy 负控与 PS-RSLG positive row 都有可引用指标。
- Coral mesh-space generated-root 负控已在本地闭合，但 master CSV/LaTeX 仍需同步。
- 当前 master CSV/LaTeX 已存在，但不是最新论文表；需要 merge Hunyuan shape-only 与 coral mesh-space closure 后重生成。

不能写：

- 不能写 Hunyuan baseline 已完整闭合或弱于/强于 PS-RSLG；它还缺 connectivity/occupancy metrics、failure labels、texture baseline、Hunyuan mesh-space negative。
- 不能写 Hunyuan shape-only 输出具有 grammar-readable recursive state、root reachability 或可继续执行 grammar。
- 不能写 TRELLIS classic 已失败；当前仍是 blocked / no local runnable output。
- 不能写所有 ordinary 3D generators 都失败；当前只支持具体 case / method / protocol 下的 bounded conclusion。
- 不能把 vine Trellis2 one-shot 的 LCR=1.000 当作递归语义成功；需要 zoom/semantic QA。

## 6. 后续轻量同步建议

若后续允许更新 `results/publication_baseline_metrics_20260510/`，建议只做 selected-final merge：

1. 追加或替换 vine/pyrite/coral 的 `Hunyuan3D shape-only image one-shot` rows，asset path 指向本地 GLB，status 暂设 `generated_import_render_QA_pending_topology_metrics`。
2. 追加 13-case Hunyuan appendix CSV rows，避免塞进主表。
3. 将 coral mesh-space generated-root row 从 missing 改为 `fragmented_copy_paste`，使用 `results/publication_coral_mesh_space_20260510/...depth_02...white_pbr.glb` 与 metrics。
4. 重生成 LaTeX 草稿，并在 caption 中明确 Hunyuan shape-only 和 TRELLIS classic blocked 状态。
