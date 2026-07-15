# P0/P1 Claim Gate 最新状态汇总（2026-05-10）

本文件汇总 remaining P0/P1 的 publication claim gate 完成度。范围仅为本地文档与本地 evidence 汇总；未使用 SSH，未启动 GPU，未修改论文源码或实验代码。

## 读取依据

- `docs/progress/ralph_publication_closure_plan_20260510.md`
- `docs/evaluation/ablation_gap_status_publication_zh_20260510.md`
- `docs/evaluation/ablation_matrix_gap_closure_queue_zh_20260510.md`
- `docs/evaluation/same_root_miniset_render_qa_status_zh_20260510.md`
- `docs/evaluation/naturalization_lsystem_miniset_status_zh_20260510.md`
- `docs/evaluation/coral_mesh_space_generated_root_status_zh_20260510.md`
- `docs/paper/publication_structure_claim_gate_plan_zh_20260510.md`
- 额外核对：`docs/evaluation/publication_ablation_effective_resolution_plan_zh_20260510.md`、`docs/evaluation/dla_bridge_ablation_mesh_qa_zh_20260509.md`、`docs/evaluation/dla_bridge_smoke_rerun1455_qa_zh_20260509.md`、`docs/evaluation/crystal_symmetry_depth_audit_zh_20260509.md`

## 状态口径

- `complete`：已有本地资产、指标、manifest/QA 足以支撑限定 claim。
- `partial`：已有可用证据，但矩阵列、matched controls、source mesh、本地 GLB/render QA 或关键指标仍缺。
- `proxy`：只有方向性 proxy 或诊断指标，不能支撑强 claim。
- `blocked`：claim-critical 行或资产缺失，当前不可写为结果。

## P0/P1 Claim Gate 表

| 优先级 | 项目 | 当前状态 | 已有证据路径 | 主要缺口 | 论文可写/不可写 |
|---|---|---|---|---|---|
| P0 | Coral mesh-space generated-root baseline | complete | `docs/evaluation/coral_mesh_space_generated_root_status_zh_20260510.md`; `results/publication_coral_mesh_space_20260510/manifest.csv`; `results/publication_coral_mesh_space_20260510/coral_mesh_space_metrics.csv`; 推荐 row: `results/publication_coral_mesh_space_20260510/coral_frontier_branch/full_srt/depth_02/coral_frontier_branch_full_srt_depth_02_white_pbr.glb` | 仅闭合 coral mesh-space generated-root 负控；full latent-vs-mesh baseline 尚未完全闭合，仍缺更完整的 latent direct/projected/masked-N、mesh repair/re-encode、同 root/depth/camera/token/face budget 对齐。 | 可写：coral one-shot root 经 S/R/T copy-paste direct merge 的 mesh-space generated-root 负控已闭合，raw face islands 极高，推荐 row raw comps=250404、occ comps=8、occ LCR=0.992、copy_repetition_score=1.0。不可写：mesh-space coral 递归生成成功，或 sparse-latent language 已全面优于 mesh-space recursion。 |
| P0 | Same-root matrix: vine/tree strict miniset | partial | `docs/evaluation/same_root_miniset_render_qa_status_zh_20260510.md`; `results/same_root_miniset_render_qa_20260510/metrics/same_root_miniset_render_qa_metrics.csv`; `results/same_root_miniset_render_qa_20260510/manifest/same_root_miniset_render_qa_manifest.json`; `results/same_root_miniset_render_qa_20260510/glb/`; `results/same_root_miniset_render_qa_20260510/renders/` | `vine_compete_d3` 和 `tree_compete_d3` 只有 direct/final-only/prune 三列本地 OBJ/GLB/render QA；strict `traditional`、`bridge`、`proposed` 未补齐。 | 可写：matched vine/tree depth-3 projection subset 显示 direct 高碎片，final-only/prune 明显改善；vine prune 为 1 component/LCR=1.0。不可写：same-root matrix 已闭合，或 six-row full matrix 结论。 |
| P0 | Same-root matrix: full six-row closure | blocked | `docs/evaluation/ablation_matrix_gap_closure_queue_zh_20260510.md`; `results/publication_ablation_metrics_20260510/ablation_gap_queue_20260510.csv`; `results/publication_ablation_metrics_20260510/matrix_coverage_summary.csv` | `vine_compete_d3` 缺 `bridge/traditional/proposed`；coral/bismuth/pyrite 多数仍是远端指标快照或缺本地 final asset/GLB；bridge 只有极少 row。 | 可写：full matrix 仍是 explicit gap/status。不可写：projection, bridge, traditional, proposed 已在同根同预算下完成公平矩阵比较。 |
| P0 | Naturalization matrix: L-system selected 4-col | partial | `docs/evaluation/naturalization_lsystem_miniset_status_zh_20260510.md`; `results/naturalization_lsystem_miniset_qa_20260510/naturalization_lsystem_miniset_qa.csv`; `results/naturalization_lsystem_miniset_qa_20260510/naturalization_lsystem_miniset_qa_manifest.json` | `rule-only/no-N/weak blend/masked local-N` 四个 selected textured GLB import OK，但 source OBJ 仍是 remote-only；缺 OBJ connectivity、root reachability、mask leakage、anchor drift，以及 with/without projection matched controls。 | 可写：selected L-system 四列均可进入同一 texture/export path，本地 GLB/PBR/material QA 通过，适合作为谨慎 visual/export ablation。不可写：masked local-N 修复 topology、保持 root/anchor、无 mask leakage，或 naturalization matrix 已闭合。 |
| P0 | Naturalization matrix: projection 分离与 non-tree controls | blocked | `docs/evaluation/ablation_gap_status_publication_zh_20260510.md`; `docs/evaluation/ablation_matrix_gap_closure_queue_zh_20260510.md`; `results/publication_ablation_metrics_20260510/manifest_selected_final_rows.csv` | `with projection` 与 `without projection` 控制未在 selected L-system/coral/pyrite 上补齐；coral/pyrite 主要只有 weak-vs-masked selected GLB，缺 rule-only/global-N/projection on-off/topology metrics。 | 可写：coral/pyrite weak-vs-masked 可作为 stress inset 或 appendix visual status。不可写：naturalization 与 projection 贡献已分离，或 coral/crystal naturalization 稳定成功。 |
| P0 | Effective-resolution / zoom-retention | proxy | `docs/evaluation/publication_ablation_effective_resolution_plan_zh_20260510.md`; `results/publication_ablation_metrics_20260510/effective_resolution_schema.csv`; `results/effective_resolution_metrics_20260510/effective_resolution_metrics.csv`; `results/effective_resolution_metrics_20260510/effective_resolution_comparisons.csv`; `paper_siga/drafts/publication_ablation_effective_resolution_status_20260510.tex` | 当前是 local_feature_scale、terminal_detail_count、zoom_retention proxy、face/GLB size、high-res blow-up estimate；缺 matched zoom render panels、人眼/渲染 QA、same token/face budget one-shot vs recursive 定量。 | 可写：effective-resolution diagnostics/proxy table。不可写：quantitative effective-resolution superiority、强 zoom-retention claim、abstract/contribution 级 resolution claim。 |
| P0 | DLA / hard frontier fragmentation | blocked | `docs/evaluation/dla_bridge_smoke_rerun1455_qa_zh_20260509.md`; `docs/evaluation/dla_bridge_ablation_mesh_qa_zh_20260509.md`; `paper_siga/figures/dla_bridge_smoke_stage1_rerun1455_20260509.png`; `paper_siga/figures/dla_bridge_ablation_mesh_qa_20260509.png` | hard-DLA raw 明显碎块；post-hoc bridge 可改善 face-level diagnostic，但 occupancy/support 仍碎或视觉桥接很假；grammar-native connected scaffold 仍需作为正路线闭合。 | 可写：post-hoc bridge 是 negative/boundary diagnostic，支持 connected-support invariant 与 projection-inside-recursion 的必要性。不可写：DLA/frontier growth 已解决，或 bridge/cache 能稳定修复碎片。 |
| P1 | Crystal / symmetry non-tree positive case | partial | `docs/evaluation/crystal_symmetry_depth_audit_zh_20260509.md`; `paper_siga/figures/pyrite_hq_depth_textured_showcase_20260509.pdf`; `results/surface_voxel_connectivity_20260509/surface_voxel_connectivity_summary.csv`; `results/symmetry_orbit_metrics_20260509/symmetry_orbit_metrics_stage4.csv` | Pyrite HQ 是强 selected positive，但仍不是完整 same-root/naturalization matrix；symmetry/orbit 指标只是 screening；raw GLB face components 不能当 topology proof；bismuth 视觉/material 仍不够主结果级。 | 可写：pyrite lattice 是 crystal/symmetry-inspired group/lattice recursive scaffold，surface-sampled voxel connectivity 支持其不是碎块。不可写：真实晶体生长、严格 symmetry/equivariance、watertight/manifold topology、crystal family 全面闭合。 |
| P1 | Coral non-tree connected scaffold | partial | `docs/paper/publication_structure_claim_gate_plan_zh_20260510.md`; `docs/evaluation/ablation_gap_status_publication_zh_20260510.md`; `paper_siga/figures/coral_depth_textured_showcase_rerun1640_20260509.pdf`; `results/publication_coral_mesh_space_20260510/` | Selected coral/coral-inspired scaffold 可作非树展示，但 same-root coral direct/prune/bridge 多为远端或局部证据；naturalization coral 只 partial；mesh-space full baseline 只完成 generated-root 负控。 | 可写：selected coral-inspired connected recursive asset / stress case。不可写：coral/DLA family 已闭合，或 coral mesh-space、same-root、naturalization 均完成。 |
| P1 | Full latent-vs-mesh baseline | partial | `docs/paper/publication_structure_claim_gate_plan_zh_20260510.md`; `docs/evaluation/ablation_gap_status_publication_zh_20260510.md`; `results/publication_coral_mesh_space_20260510/`; `paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex` | Coral mesh-space generated-root 已补，但 TRELLIS non-2/Hunyuan、strict ordinary gen3D rows、latent-copy vs mesh-space vs PS-RSLG 的 full same-budget alignment 仍不完整；一些 rows 是 blocked/missing 或 selected 口径。 | 可写：ordinary one-shot/naive latent/mesh recursion 是有用 controls，且当前可用 rows 不提供 grammar-owned typed recursive state。不可写：所有普通 3D generator 已公平评估并被击败，或 full latent-vs-mesh baseline 已闭合。 |

## 当前总判断

1. Coral mesh-space generated-root baseline 已闭合，但闭合的是 direct copy-paste mesh-space 负控，不是 full latent-vs-mesh baseline。论文中应把它放入 baseline/ablation 表，并明确无 generator、无 projection、无 repair、无 learned recursion。
2. Same-root 仍是 `partial`：vine/tree 三列 miniset 是可写的 claim-safe subset，但 full six-row same-root matrix 仍缺 `traditional/bridge/proposed` 的 strict matched rows。
3. Naturalization 仍是 `partial`：L-system 四列 selected GLB 足够写 visual/export ablation，但缺 source mesh、root/anchor/mask 指标和 projection on/off 控制，不能写 topology repair。
4. Effective-resolution / zoom-retention 仍是 `proxy`：只适合 appendix/status/proxy table，不能放强主张。
5. DLA/crystal/non-tree 碎片风险仍是 P0 风险：pyrite 是较强 selected positive，coral 是 partial positive，DLA bridge 是 negative diagnostic；不能把 non-tree family 写成整体闭合。

## 下一步最高收益执行顺序

1. 补 `vine_compete_d3` same-root 的 `bridge/traditional/proposed`，并保持与已有 `direct/final-only/prune` 同 root、同 depth、同 renderer、同 GLB/render QA。收益最高，因为它直接把主文核心 projection claim 从三列 subset 推向最小 full matrix。
2. 闭合 `lsystem_branch/fork_side` naturalization：本地化四个 selected source OBJ，计算 connectivity/root reachability/mask leakage/anchor drift，并补 with/without projection。收益在于把 4.7 从 visual/export status 升级为真正的 claim gate。
3. 做 matched zoom render QA：为 effective-resolution proxy 的 tree/vine 与 coral/crystal 对照补同相机局部 zoom panels、人工 QA 和 budget 对齐说明。收益在于把 proxy table 升级到可进主文的弱定量/强诊断。
4. 对 coral/pyrite naturalization 补 rule-only、global-N、projection on/off 和 topology/root metrics。收益是把 non-tree naturalization 从 stress inset 推向 appendix matrix；不建议优先抢主文 P0。
5. 针对 DLA/coral 碎片风险继续走 grammar-native volumetric/attachment-aware connected scaffold，而不是扩展 post-hoc bridge。收益是修复 reviewer 最容易质疑的非树碎片边界，同时避免把失败修补线写成正贡献。
6. 最后再扩展 full latent-vs-mesh baseline：补 TRELLIS non-2/Hunyuan blocked audit 或 runnable rows、mesh repair/re-encode variants、同预算 alignment。收益大但链路长，适合在 P0 claim gates 稳住后推进。
