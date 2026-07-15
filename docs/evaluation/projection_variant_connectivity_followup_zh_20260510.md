# Projection Variant Connectivity Follow-up / Revision Closure Note（2026-05-10）

本文档用于把新 revision 要求中的实验项逐项闭环到当前证据状态，并记录新启动的 projection/connectivity variant run 的聚合准备情况。本文只新增评估记录；未修改 `paper_siga/main.tex`，未启动新重任务，未删除远端文件。

## 0. 输入与远端状态

### 本地依据

- `/Users/fanta/Downloads/agent_revision_and_experiment_requirements.md`
- `docs/experiments/occupancy_primary_connectivity_and_flow_summary_zh_20260509.md`
- `docs/evaluation/latest_textured_connectivity_metric_reconciliation_zh_20260510.md`
- `docs/method/revision_requirements_to_ps_rslg_plan_zh_20260510.md`

### 新远端 run

- host：`a100-2`
- results：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/projection_variant_connectivity_ralph_20260510_0018`
- logs：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/projection_variant_connectivity_ralph_20260510_0018`
- 远端结果目录当前约 `2.0G`；`/mnt/beegfs` 为 `28T` 总量、`6.7T` 已用、`22T` 可用、`24%` 使用率。相对 100GB 项目 cap 当前不接近上限。
- 远端 worker 仍在运行：`gpu4_bismuth`、`gpu5_pyrite`、`gpu6_coral`、`gpu7_hard_dla` 四个 Python 进程仍匹配该 run name。`screen` 在该 host 上不可用，日志文件当前为空。

### 本地聚合文件

已将小型 `run_config.json`、`summary.json`、`summary_partial.json` 拉到：

- `results/projection_variant_connectivity_ralph_20260510_0018_summary/`

已生成当前可用聚合：

- `results/projection_variant_connectivity_ralph_20260510_0018_summary/projection_variant_final_metrics_available_20260510.csv`
- `results/projection_variant_connectivity_ralph_20260510_0018_summary/projection_variant_expected_status_20260510.csv`

注意：因为远端仍在运行，CSV 是当前快照，不是最终完整结果。

## 1. Revision-required 实验闭环表

| revision-required experiment / evidence gate | 当前状态 | 当前证据 | 论文处理建议 |
|---|---|---|---|
| Projection variants：`no projection / final-only / per-depth prune-only / model-bridge / traditional repair baseline` | **partial** | 旧 `projection_matrix_gap_closure_20260509` 已能支持 `vine_compete_d3`：`no_projection comp=2059, LCR=0.9049`，`final_only comp=2, LCR=0.9934`，`per_depth comp=1, LCR=1.000`。新 run 是 case/grammar/method connectivity matrix，当前还不是完整 no/final/per-depth 五路闭环。 | 主文可以保守写“per-depth projection 在 clean vine case 上抑制碎片传播”；`model-bridge` 与 `traditional repair` 仍保留 `\EvidencePending{Need complete projection variants proving model-native state selection rather than manual patching.}` |
| Occupancy-primary connectivity 主指标 | **ready** | 旧汇总已有 coral `fork_side_attach + sparse_close` depth=3：`occ=1, occ_lcr=1.000, face=1, face_lcr=1.000`；bismuth selected positive 可支持 occupancy-primary 正例；pyrite/hard-DLA 为边界或负例。 | 可作为主实验表核心，但必须同时报告 face/mesh diagnostics，不能用 occupancy LCR 证明 mesh topology clean。 |
| Textured GLB / PBR export compatibility | **ready / partial** | 最新 textured 对齐文档支持 pyrite/bismuth textured exports 在 vertex-voxel 与 surface-voxel 下连通；coral 是 surface-renderability 边界正例；scifi 只支持 seam-tolerant export compatibility。 | 只写 selected projected meshes can enter frozen Trellis2 texture/export path。不要列为核心贡献，不要写 texture repairs structural connectivity。 |
| Non-tree scaffold evidence：coral / bismuth / pyrite / hard-DLA | **partial** | coral/bismuth 有可进入主文的 occupancy-primary 正例；pyrite 参数敏感；hard-DLA 是负例。新 run 目前没有新增强正例，反而显示若干 stage-2 variant 仍碎。 | 主文保留 coral/bismuth selected positive；pyrite、hard-DLA 放 appendix/boundary。 |
| Flow/SDE / masked naturalization ablation：rule-only、no-N、masked-N、global-N、weak blend、with/without projection | **missing** | 旧 Flow/SDE 只有 tokens/verts/faces/runtime，没有 occupancy/face component 指标；不能证明 topology 或 connectedness 改善。 | 所有 masked naturalization 改善质量且不漂移的 claim 继续 `EvidencePending`。Flow/SDE 当前适合 appendix negative/boundary。 |
| Sparse-latent grammar vs mesh-space procedural + Trellis texture baseline | **missing / partial** | 已有方法叙事和若干 traditional baseline sanity check，但还没有公平完整矩阵证明 sparse-latent addressability、transform/cache/local naturalization 优势。 | 这是 novelty-critical gate。Abstract/Intro 中相关强 claim 必须保守或标 `EvidencePending`。 |
| Direct sparse edit / 2D scaffold -> image-to-3D / global repair / final-only cleanup failure evidence | **partial** | 文档中已有 failure chain 和部分 projection/fork/flow 负例；但不是每一点都有同协议、同 root、同 renderer 的可发表图和指标。 | 可以作为动机，但强措辞需要标 `EvidencePending{Need failure evidence for direct sparse edit / global repair.}`。 |
| Metrics suite：mesh validity、skeleton/root/tip、morphology/porosity、latent stability、effective resolution、asset diagnostics | **partial / missing** | 当前最稳是 occupancy component/LCR + face component/LCR + textured surface-voxel reconciliation。skeleton、root reachability、orphan handle、deleted mass、morphology、latent drift、runtime/memory 仍不完整。 | 主文指标表必须限定为当前已有指标；完整 metric suite 继续 `ExpFigTODO`。 |
| Effective resolution / recursive refinement / one-shot Trellis2 comparison | **missing** | 目前没有 same-budget one-shot vs recursive local detail、terminal detail survival、local token density、高 depth refinement 指标闭环。 | 不应在 abstract/contribution 中写 effective-resolution 优势；保留 `EvidencePending`。 |
| Root/seed robustness / success rate / mean/std | **missing** | 当前证据多为 selected cases。没有 multiple roots/seeds 的成功率和 mean/std 闭环。 | 所有 robustness/泛化 claim 继续 `EvidencePending`。 |
| Runtime / complexity / memory | **partial** | 部分旧 Flow/SDE 记录 seconds；新 run 可后续从 summary/log 补，但当前没有 per-depth encode/decode/projection/naturalization/texture cost 表。 | Implementation/evaluation 中只能写需要报告的协议；不能写已完成复杂度对比。 |
| Paper-grade visual rerender / figure-only page organization | **partial** | 已有若干 white-background/Blender/GLB contact sheet；但主图仍需一图一 claim、固定相机、指标绑定。 | 可推进图筛选，但仍不能清除 `ExpFigTODO{Re-render all visual results...}`。 |

## 2. 新 run 聚合状态

新 run 计划矩阵来自四个 `run_config.json`：

- cases：`bismuth`、`pyrite`、`coral`、`hard_dla`
- grammars：`fork_side_attach`、`compete_fork_attach`
- methods：`raw`、`sparse_close`、`sparse_close_bridge`、`mesh_bridge_smooth`
- stages：2
- expected combinations：`4 x 2 x 4 = 32`

当前本地快照：

- `summary.json` final rows：6 / 32
- status CSV 中 `partial_summary_available_running` rows：2 / 32
- status CSV 中 `not_yet_observed_running` rows：24 / 32
- variant-level `summary_partial.json` files：8，其中 6 个已对应 final summary，2 个仍是 partial-only

因此本轮不能给出 final matrix conclusion，只能给出 available-row interpretation。

## 3. 当前可用 final_metrics 快照

| case | grammar | method | occ comp | occ LCR | face comp | face LCR | verts / faces | 当前解释 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| bismuth | fork_side_attach | raw | 2 | 0.9975 | 9 | 0.9165 | 592877 / 1121170 | 接近 occupancy 正例但不是单组件；不能写 fully connected。 |
| pyrite | fork_side_attach | raw | 9 | 0.9367 | 18 | 0.8805 | 663913 / 1236328 | 边界/负例，符合 pyrite 参数敏感判断。 |
| coral | fork_side_attach | raw | 4 | 0.9142 | 8 | 0.9049 | 162271 / 299044 | 边界；不如旧 depth=3 coral 正例。 |
| coral | fork_side_attach | sparse_close | 7 | 0.9021 | 9 | 0.9084 | 161003 / 294132 | 没有改善 occupancy；不能作为正例。 |
| coral | fork_side_attach | sparse_close_bridge | 51 | 0.9441 | 5 | 0.9649 | 222610 / 410274 | bridge 改善 face LCR/组件，但 occupancy component 明显变多；支持“face repair 不等于 occupancy invariant”的边界论点。 |
| hard_dla | fork_side_attach | raw | 6 | 0.9861 | 7 | 0.9880 | 751515 / 1402320 | 仍是 hard-DLA 边界/负例；不能升级为主文正面。 |

### 当前 variant 解读

1. **新 run 目前没有新增可以替代旧主正例的结果。** 旧 coral depth=3 `fork_side_attach + sparse_close`、bismuth selected positive、vine projection matrix 仍是当前主文最稳证据。
2. **coral stage-2 variant 显示 sparse/bridge 操作并非单调改善。** `sparse_close_bridge` 把 face component 从 raw 的 8 降到 5、face LCR 从 0.9049 提到 0.9649，但 occupancy component 从 4 增到 51。这正好说明论文不能只用 raw face 或视觉结果判断连通性。
3. **bismuth raw 当前只是 near-positive。** occ LCR 很高，但 occ comp=2、face comp=9；可以作为 partial，不可写成 strict connected positive。
4. **pyrite 与 hard-DLA 延续边界判断。** 当前完成行均非 strict occupancy connected，不应进入主文正面 claim。
5. **还不能解释 `compete_fork_attach` 或 `mesh_bridge_smooth`。** 这些组合尚未完成，必须等 run 结束后重新拉取并重建 CSV。

## 4. 当前可支持的论文 claim

可以支持：

- PS-RSLG 应被定位为 frozen 3D generator native sparse support / sparse latent state 上的 finite-depth recursive grammar，而不是 texture 或 mesh cleanup 论文。
- Connected support 可以作为 recursive state invariant 的主实验口径，用 occupancy component count 和 occupancy LCR 做 primary metric，并同时报告 face/mesh diagnostics。
- 在已有旧证据中，per-depth projection 对 conservative vine case 比 no-projection / final-only 更能抑制碎片传播。
- Selected connected scaffolds 可以进入 frozen Trellis2 texture/PBR export path；texture 是 compatibility / asset-readiness evidence，不是结构正确性证据。
- post-hoc bridge / mesh repair / face-level improvement 与 occupancy-primary connectedness 不等价；新 coral `sparse_close_bridge` 快照进一步支持这个 caveat。

## 5. 仍应保持 EvidencePending 的 claim

必须继续标 `EvidencePending` 或 `ExpFigTODO`：

- sparse-latent recursive grammar 明确优于 mesh-space procedural recursion + Trellis texture export。
- masked local naturalization 能稳定提升 surface quality 且不造成 topology drift。
- projection 已完整证明是 model-native state admissibility，而不是传统 repair 或 manual patching。
- model-proposed bridge projection 的正面效果。
- effective resolution / recursive refinement / one-shot Trellis2 对比优势。
- root/seed robustness、success rate、mean/std。
- skeleton/root/tip/path preservation、orphan handle rate、deleted mass、latent drift、morphology、runtime/memory 等完整 metric suite。
- 全部主文视觉图已达到 paper-grade、白底、固定相机、一图一 claim。

## 6. 等 run 完成后的最小下一步

1. 重新拉取 `summary.json`、`summary_partial.json`、`run_config.json` 到 `results/projection_variant_connectivity_ralph_20260510_0018_summary/`。
2. 重建 `projection_variant_final_metrics_available_20260510.csv` 和 `projection_variant_expected_status_20260510.csv`。
3. 若 32/32 完成，再按 case 分别比较 `raw / sparse_close / sparse_close_bridge / mesh_bridge_smooth`，并单独标出 occupancy-positive、face-only-positive、negative/boundary。
4. 只有当某个 variant 同时满足 `occupancy_component_count=1`、`occupancy_lcr=1.000` 且 face diagnostics 可解释时，才考虑升级为主文正例。
5. 若 bridge 只改善 face 而恶化 occupancy，应写入 appendix/boundary，作为“traditional/post-hoc repair cannot replace recursive state admissibility”的证据。
