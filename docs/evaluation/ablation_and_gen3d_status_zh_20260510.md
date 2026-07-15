# Ablation 与 Gen-3D Baseline 状态整理（2026-05-10）

## 本轮已完成

- 已把 Trellis2 one-shot、Trellis2 trivial latent copy、mesh-space generated-root direct merge、以及 PS-RSLG/ours 候选汇总到 `results/gen3d_baseline_metrics_20260510/gen3d_baseline_summary_table_20260510.csv`。
- 已生成可贴入论文草稿的紧凑 LaTeX 表：`paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex`。
- 已把 same-root projection 和 naturalization/projection 现有表格压缩到 `results/ablation_summary_20260510/`，用于快速查看 available rows 与缺口计数。
- 没有修改 `paper_siga/main.tex`，也没有触碰任何视觉渲染输出。

## Gen-3D baseline 关键发现

1. Trellis2 one-shot 在 vine 上 occupancy LCR 为 1.000，但它只是普通 one-shot 生成；pyrite one-shot 的 occupancy LCR 只有 0.127，coral one-shot 为 0.600，说明非树状递归结构仍存在明显碎片/局部失真风险。
2. Trivial latent copy 不能替代递归语义：vine latent copy 的 LCR 为 0.689，pyrite 为 0.102，coral 虽有 0.824 的 occupancy LCR，但 face components 达 2208，且只是 copy_shift_upper_z 控制，没有投影稳定、attachment certificate 或局部自然化语义。
3. Mesh-space generated-root baseline 是强负例：用 Trellis2 one-shot root 做 S/R/T direct merge 后，vine depth=2 有 101699 个 face components，pyrite depth=2 有 173575 个 face components；即使 occupancy proxy 对 vine 给出 0.813 LCR，mesh 级别仍是明显 copy-paste 碎片结构。
4. Ours/PS-RSLG 的 pyrite 和 coral strict visual matched textured GLB 行 occupancy LCR 都是 1.000，可作为非树状 connected recursive asset 的主要候选。当前 exact `ours_vine` strict row 的 occupancy LCR 低，主文若要写 vine 正向结果，应优先换用 summary table 中附带的 `stronger vine stage5 reference` 并配合视觉 QA。
5. Hunyuan3D 2.0 当前仍应写为 blocked/install-needed；本地没有可复用 Hunyuan/HY3D repo、cache 或结果。Trellis2 也不能写成 native text-to-3D baseline，只能写 image-to-3D，或 text-to-image 前端后的非原生设置。

## Ablation 已完成与缺口

- Same-root projection matrix 已有 `traditional/direct/final-only/prune/bridge/proposed` 的 inventory，但很多 case 不是完整同根同深闭环。`vine_compete_d3` 有 direct/final-only/prune 的可用负例和正向候选；bridge/proposed 仍不完整。
- Naturalization/projection matrix 已显式区分 `masked local-N`、`global-N`、`with projection`、`without projection`、`post-hoc repair baseline`。多数 `rule-only`、`no-N`、`weak blend` 行仍是 missing，不能在主文中声称完整 naturalization ablation 已闭合。
- `global-N` 多来自 flow/SDE grid，当前多是负例或 near-lcr fragmented；它不能被写成 projection evidence。
- `post-hoc repair baseline` 已单独列出，不能混入 PS-RSLG projection 或 masked local-N。

## 建议写进实验部分的方式

- 主文表格可以采用三组对照：ordinary Trellis2 one-shot、trivial recursion controls（latent copy 与 mesh-space direct merge）、PS-RSLG candidates。表格中保留 status，不要只报成功行。
- 文本重点写“ordinary generator can create plausible objects but does not enforce controlled recursive attachment/local recurrence”，再用 pyrite/coral one-shot 与 mesh-space generated-root 的低 LCR/高 component count 做证据。
- Ablation 主文只使用同根同深、render QA 通过的子集；其余 same-root/naturalization inventory 放 appendix 或 supplement，明确标为 gap/status table。
- Effective-resolution claim 仍需要 matched nested zoom render 和人工 QA。现有 metrics 可以作为 proxy，但不要把 box-count dimension 或 local_feature_scale_proxy 写成严格视觉保真结论。

## 新文件索引

- `results/gen3d_baseline_metrics_20260510/gen3d_baseline_summary_table_20260510.csv`
- `paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex`
- `results/ablation_summary_20260510/same_root_projection_available_rows_20260510.csv`
- `results/ablation_summary_20260510/naturalization_projection_available_rows_20260510.csv`
- `results/ablation_summary_20260510/ablation_gap_counts_20260510.csv`
