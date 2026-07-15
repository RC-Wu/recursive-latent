# Gen-3D baseline 与 ablation 证据严谨性审查

日期：2026-05-10  
作者：并行子任务 C  
范围：只读核对 `results/gen3d_baseline_metrics_20260510/`、`results/ablation_summary_20260510/`、`paper_siga/drafts/`、`docs/evaluation/*20260510*`，并额外检查已存在的 `results/naturalization_projection_ablation_20260510/`。未修改 `paper_siga/main.tex`。

## 0. 总体判断

当前证据可以支持一个谨慎的主文故事：Trellis2 ordinary one-shot、Trellis2 trivial latent copy、mesh-space generated-root direct merge 都不能稳定保证受控递归结构；PS-RSLG 在 pyrite/coral 的 strict textured rows 上有强 occupancy connectivity 证据，vine 需要使用 `stronger vine stage5 reference`，不能把 strict `ours_vine` 弱行写成成功。

当前证据不能支持“所有 baseline / ablation 已完成”。Hunyuan 只能写成 feasibility / planned / blocked baseline；same-root matrix 与 naturalization matrix 都是 partial coverage；rule-only、no-N、weak blend 仍无本地完成行。

## 1. Gen-3D baseline 当前已有证据

证据源：`results/gen3d_baseline_metrics_20260510/gen3d_baseline_summary_table_20260510.csv`。`asset_path` 已逐项检查：除 coral mesh-space missing 外，表内列出的 GLB/OBJ 均在本地存在，文件大小与 CSV 一致。

| case | method | variant | asset | V/F | MB | face comps | occ comps | occ LCR | status |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| vine | Trellis2 one-shot | image-conditioned one-shot | `visuals/gen3d_baseline_trellis2_one_shot_textured_20260510/one_shot_tex_vine_front_seed613/textured.glb` | 330677 / 662194 | 20.791 | 202 | 1 | 1.000 | success |
| pyrite | Trellis2 one-shot | image-conditioned one-shot | `visuals/gen3d_baseline_trellis2_one_shot_textured_20260510/one_shot_tex_pyrite_iso_seed612/textured.glb` | 75922 / 152446 | 5.748 | 198 | 17 | 0.127 | fragmented |
| coral | Trellis2 one-shot | image-conditioned one-shot | `visuals/gen3d_baseline_trellis2_one_shot_textured_20260510/one_shot_tex_coral_iso_seed612/textured.glb` | 944986 / 1917216 | 72.274 | 1050 | 30 | 0.600 | fragmented |
| vine | Trellis2 trivial latent | copy_shift_upper_z | `visuals/gen3d_baseline_trellis2_one_shot_latent_nopre_20260510/vine_latent_transform_seed610_steps6_nopre/copy_shift_upper_z/mesh.obj` | 66101 / 129972 | 4.326 | 283 | 9 | 0.689 | fragmented |
| pyrite | Trellis2 trivial latent | copy_shift_upper_z | `visuals/gen3d_baseline_trellis2_one_shot_latent_nopre_20260510/pyrite_latent_transform_seed610_steps6_nopre/copy_shift_upper_z/mesh.obj` | 44540 / 79226 | 2.745 | 985 | 100 | 0.102 | fragmented |
| coral | Trellis2 trivial latent | copy_shift_upper_z | `visuals/gen3d_baseline_trellis2_one_shot_latent_nopre_20260510/coral_latent_transform_seed610_steps6_nopre/copy_shift_upper_z/mesh.obj` | 1226785 / 2453600 | 89.819 | 2208 | 39 | 0.824 | fragmented |
| vine | Mesh-space generated-root baseline | full_srt depth=2 direct merge | `results/gen3d_meshspace_generatedroot_20260510/vine_tree/full_srt/depth_02/vine_tree_full_srt_depth_02_white_pbr.glb` | 309647 / 104000 | 4.735 | 101699 | 5 | 0.813 | fragmented_copy_paste |
| pyrite | Mesh-space generated-root baseline | full_srt depth=2 direct merge | `results/gen3d_meshspace_generatedroot_20260510/pyrite_lattice/full_srt/depth_02/pyrite_lattice_full_srt_depth_02_white_pbr.glb` | 570200 / 200000 | 8.815 | 173575 | 145 | 0.033 | fragmented_copy_paste |
| coral | Mesh-space generated-root baseline | full_srt depth=2 direct merge | none | - | - | - | - | - | missing |
| vine | Ours / PS-RSLG | strict_visual_matched_texture_20260510 | `visuals/strict_visual_matched_texture_20260510/lsys_climbing_vine_d6_tendrils_steps8_tex2048_seed20260539_xformers/textured.glb` | 2032 / 1492 | 0.362 | 200 | 30 | 0.072 | needs_vine_candidate_swap_or_QA |
| pyrite | Ours / PS-RSLG | strict_visual_matched_texture_20260510 | `visuals/strict_visual_matched_texture_20260510/ifs_fractal_lattice_d4_pyrite_steps8_tex2048_seed20260841_xformers/textured.glb` | 294399 / 226088 | 12.678 | 50396 | 1 | 1.000 | success |
| coral | Ours / PS-RSLG | strict_visual_matched_texture_20260510 | `visuals/strict_visual_matched_texture_20260510/dla_coral_cluster_900_frontier_connected_steps8_tex2048_seed20260711_xformers/textured.glb` | 146885 / 117340 | 6.746 | 19659 | 1 | 1.000 | success |
| vine | Ours / PS-RSLG | stronger vine stage5 reference | `visuals/vine_stage5_guide_sweep_20260509/vine_stage5_parthenocissus_warm_steps8_tex2048_xformers/textured.glb` | 647958 / 455964 | 26.230 | 113957 | 4 | 0.999 | success |

审查要点：

- Trellis2 one-shot 只能说明 ordinary image-to-3D baseline 已有三例。vine 的 occupancy LCR=1.000，但 pyrite/coral 分别为 0.127/0.600，不能写成 ordinary generator 可靠保持非树状递归结构。
- Trivial latent 三例均是 `copy_shift_upper_z`，均标为 fragmented；它是负控，不是本文方法的 latent-space 递归成功替代。
- Mesh-space generated-root 只有 vine/pyrite 两例，coral 缺失；vine/pyrite face component 数为 101699/173575，是强 copy-paste fragmentation 证据。
- PS-RSLG strict pyrite/coral 可作为 connected 非树类证据；strict vine 行失败，主文若需要 vine 正例，应写 stronger stage5 reference，并说明它不是 strict matched weak vine row。
- `paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex` 中 mesh-space generated-root 的 MB 写成 13.0/21.6，与 CSV 和实际 GLB 文件 4.735/8.815 MB 不一致；修表时应以 CSV/实际文件为准。

## 2. Hunyuan 状态边界

`docs/evaluation/hunyuan3d_baseline_feasibility_zh_20260510.md` 和 `docs/evaluation/gen3d_baseline_feasibility_zh_20260510.md` 的结论一致：当前项目本地/远端未发现 Hunyuan3D/HY3D repo、`hy3dgen` 包、Hugging Face cache 或结果目录；官方 image-to-3D 需要安装与权重，text-to-3D 还涉及额外 T2I worker 风险。

因此论文中只能写：

- Hunyuan3D 2.0 was audited as a planned / secondary baseline.
- 当前环境缺少 repo/package/weights，数值结果未完成。
- Hunyuan image-to-3D、image+texture、text-to-3D 行若出现在表里，应标 `planned / blocked / install-needed`。

不能写：

- Hunyuan baseline 已完成。
- Hunyuan 数值可与 Trellis2/PS-RSLG 直接比较。
- Hunyuan text-to-3D 是当前已复现的 native baseline。

## 3. Same-root projection matrix 覆盖缺口

证据源：`results/ablation_summary_20260510/same_root_projection_available_rows_20260510.csv` 与 `ablation_gap_counts_20260510.csv`。

| variant | available | missing | 当前边界 |
|---|---:|---:|---|
| traditional | 30 | 8 | 传统 baseline inventory 较多，但 source 混合；可作 proxy/appendix，不等于完整同根矩阵。 |
| direct | 8 | 8 | 有 bismuth/coral/hard_dla/pyrite 与 tree/vine compete 类行；仍缺一半。 |
| final-only | 4 | 12 | 只覆盖 tree/vine compete 类少量行。 |
| prune | 5 | 11 | vine_compete_d3 有 LCR=1 正向候选，coral 也有 sparse_close 行；不能泛化。 |
| bridge | 1 | 15 | 只有 coral bridge 一行；最多 appendix/status。 |
| proposed | 15 | 10 | root/tree/vine 与 strict proxy 有证据，但矩阵未闭合。 |

结论：same-root matrix 不能写成 exhaustive ablation。主文最多选一个固定 root/operator/depth/render 的 matched subset 展示趋势；全量表应作为 status/gap table 放附录。

## 4. Naturalization ablation 与 gap-fill 检查

除 `results/ablation_summary_20260510/naturalization_projection_available_rows_20260510.csv` 外，本地已经存在更完整的 gap-fill 目录：`results/naturalization_projection_ablation_20260510/`。其 `summary.json` 显示总计 174 行，available 70，missing 104；required variants 为 `rule-only`、`no-N`、`weak blend`、`masked local-N`、`global-N`、`with projection`、`without projection`，并把 `post-hoc repair baseline` 单独报告。

本地 gap-fill 后的覆盖如下：

| variant | available | missing | 当前边界 |
|---|---:|---:|---|
| rule-only | 0 | 18 | 完全缺失；不能写实验结论。 |
| no-N | 0 | 18 | 完全缺失；不能写实验结论。 |
| weak blend | 0 | 18 | 完全缺失；不能写实验结论。 |
| masked local-N | 14 | 13 | partial；多来自 strict matched proxy/visual manifest，部分行缺 connectivity metrics。 |
| global-N | 12 | 14 | partial；来自 flow/SDE diagnostic，多为 negative 或 near_lcr_fragmented，不能写成成功自然化。 |
| with projection | 35 | 9 | partial；证据最多但混合 projection/status/proxy 行。 |
| without projection | 4 | 14 | minimal；主要 tree/vine compete 负控。 |
| post-hoc repair baseline | 5 | 0 | 单独 repair baseline；不能混称 projection 或 masked local-N。 |

自然化 gap-fill 结论：

- 已有本地 gap-fill 文件，不能再简单写“等待远端 metrics”。
- 但 gap-fill 并没有闭合 required matrix：rule-only/no-N/weak blend 仍为 0 available。
- masked local-N 和 with projection 的可用行很多只是 manifest / proxy inventory，缺少 before/after components、LCR delta、root reachability 等完整指标；可作状态证据，不能作强 ablation。
- post-hoc repair baseline 中 `transform_radial4_pyrite_steps8_tex2048_xformers` 从 118 comps 降到 8 comps、LCR 从 0.9649 到 0.9983；这说明 mesh-space repair 有诊断价值，但不是 recursive projection 成功证据。

## 5. Claim gate

### 可以写

- Trellis2 image one-shot baseline 已有 vine/pyrite/coral 三例；pyrite/coral 的 occupancy connectivity 明显弱于 PS-RSLG strict rows。
- Trellis2 trivial latent `copy_shift_upper_z` 三例均 fragmented，不能替代 projection-stabilized recursive semantics。
- Mesh-space generated-root direct merge 在 vine/pyrite 上严重 face-level fragmentation；coral mesh-space generated-root 缺失。
- PS-RSLG strict pyrite/coral 的 occupancy comps=1、LCR=1.000，可作为非树类 connected recursive asset evidence。
- Vine 正向结果应使用 stronger stage5 reference，写成 candidate swap / stronger available vine evidence，而不是 strict weak row。
- Hunyuan3D 已做 feasibility audit，但当前是 planned/blocked baseline。
- Same-root 与 naturalization 表可以作为 partial status/gap table；主文只能用 matched subset。
- Global-N naturalization 可写成不稳定/诊断性负控，而不是成功方法。

### 不能写

- 不能写 Hunyuan3D baseline 完成或已有数值结果。
- 不能写 TRELLIS 非 2 baseline 已完成；当前主证据是 Trellis2。
- 不能写 coral mesh-space generated-root baseline 已完成。
- 不能写 same-root projection matrix 完整闭合。
- 不能写 naturalization/projection matrix 完整闭合。
- 不能写 rule-only/no-N/weak blend 已比较。
- 不能把 post-hoc mesh repair baseline 写成 projection 或 masked local-N。
- 不能把 raw face component 数直接解释为 GLB 视觉失败的唯一判据；应同时报告 occupancy proxy、render/import success 和视觉 QA。
- 不能写 effective-resolution / zoom-retention 已完成定量证明，除非另有 matched zoom metrics。

## 6. 建议放置

主文：放 Gen-3D compact table，但修正 mesh-space MB；保留 Hunyuan planned/blocked 注释；使用 pyrite/coral strict PS-RSLG 与 stronger vine stage5 reference；ablation 只展示 matched subset。

附录：放 same-root full available rows、gap counts、naturalization gap-fill 174 行摘要、global-N negative rows、post-hoc repair baseline、Hunyuan feasibility/planned baseline、strict weak vine 与 candidate swap rationale。
