# Baseline case pool + metric 推荐（2026-05-10）

作者：并行 worker（Lane B，本地只读/文档更新）  
范围：补全 case pool 与机器可读推荐清单；未使用 SSH；未修改 `main.tex`。  
机器可读清单：`results/publication_baseline_metrics_20260510/baseline_case_pool_recommendations_20260510.csv`

## 0. 结论

本轮把可选择 case pool 整理为 7 个视觉/实验类别，每类至少 10 个候选，并额外加入 12 个主文受控比较 row 与 12 个 blocked/missing baseline slot。主文推荐不要追求“大而全”，而应使用一个 claim-safe 的小子集：

1. Gen3D baseline 主比较：`vine / pyrite / coral` 三个任务，比较 Trellis2 one-shot、Trellis2 trivial latent copy、mesh-space generated-root、PS-RSLG。
2. 非树优势主证据：`pyrite` 与 `coral`，因为 PS-RSLG strict rows 的 occupancy comps=1、LCR=1.000，而 ordinary/latent/mesh controls 明显破碎或 copy-paste。
3. botanical 正例：使用 `stronger vine stage5 reference`，不要把 weak strict `ours_vine` 行写成成功。
4. 同根 ablation：主文只放 `vine_compete_d3` 的 `direct / final-only / prune` miniset；`tree_compete_d3` 放 appendix 或备选。
5. Naturalization：`lsystem_branch/fork_side` 四列只能作为 visual/export ablation；source OBJ 未本地化，不能 claim topology/root/mask 指标。

## 1. 每类候选数量

| category | CSV rows | 可作为主文 | 用途 |
|---|---:|---|---|
| `ablation_depth` | 13 | `vine_compete_d3` direct/final-only/prune；必要时补 tree | projection/same-root 与 depth progression |
| `crystal_coral_dla` | 11 | bismuth/pyrite/coral 视觉；pyrite/coral 指标主证据 | 非树、晶体、珊瑚/DLA |
| `gen3d_baselines` | 12 | vine/pyrite/coral compact baseline table | ordinary generator / latent copy / mesh-space / ours |
| `hero_zoom` | 11 | hero combo overview + five zooms | 头图/teaser，不作为 baseline metric |
| `needs_repair_or_discard` | 10 | 不推荐主文正例 | 失败图库、repair 动机、风险审查 |
| `plant_root_tree` | 12 | stronger vine stage5；root/tree 视觉 appendix | 植物、根系、树冠 |
| `sci_fi_mechanical` | 10 | 暂放 appendix | domain breadth，尚无 matched baseline 主表 |
| `controlled_main` | 12 | 是 | 主文 claim-safe 子集 |
| `blocked_or_missing_baselines` | 12 | 只作 blocked slot | TRELLIS non-2 / Hunyuan claim gate |

## 2. 推荐主文 case

### Gen3D compact baseline table

推荐主文 row：

| case | method | status | 关键指标/边界 |
|---|---|---|---|
| vine | Trellis2 one-shot | complete | V=330677, F=662194, raw comps=202, occ comps=1, LCR=1.000；只能说明 ordinary baseline，不说明递归语义成功 |
| vine | Trellis2 trivial latent copy | complete | raw comps=283, occ comps=9, LCR=0.689；负控 |
| vine | mesh-space generated-root | complete | raw comps=101699, occ comps=5, LCR=0.813；copy-paste fragmentation |
| vine | PS-RSLG stronger stage5 | complete | V=647958, F=455964, occ comps=4, LCR=0.999；替代 weak strict vine row 作正例 |
| pyrite | Trellis2 one-shot | fragmented | raw comps=198, occ comps=17, LCR=0.127 |
| pyrite | Trellis2 trivial latent copy | fragmented | raw comps=985, occ comps=100, LCR=0.102 |
| pyrite | mesh-space generated-root | fragmented_copy_paste | raw comps=173575, occ comps=145, LCR=0.033 |
| pyrite | PS-RSLG strict | success | raw comps=50396, occ comps=1, LCR=1.000 |
| coral | Trellis2 one-shot | fragmented | raw comps=1050, occ comps=30, LCR=0.600 |
| coral | Trellis2 trivial latent copy | fragmented | raw comps=2208, occ comps=39, LCR=0.824 |
| coral | mesh-space generated-root | fragmented_copy_paste | V=754194, F=252000, raw comps=250404, occ comps=8, LCR=0.992；必须同时报告 copy repetition=1，不可只看 LCR |
| coral | PS-RSLG strict | success | raw comps=19659, occ comps=1, LCR=1.000 |

推荐写法：ordinary one-shot、trivial latent copy、mesh-space generated-root direct copy 都不能稳定替代 grammar-owned recursive state；PS-RSLG 在 pyrite/coral 的 strict rows 上给出更强的 connected recursive asset evidence。不要写“所有 3D generator 都失败”。

### Same-root miniset

主文用 `vine_compete_d3` 三列：

| variant | status | components | LCR | 用途 |
|---|---|---:|---:|---|
| direct | complete | 2059 | 0.9049 | no-projection negative |
| final-only | complete | 2 | 0.9934 | final cleanup control |
| prune | complete | 1 | 1.0000 | per-depth prune/projection positive |

`tree_compete_d3` 可作为 appendix：direct=3201/LCR=0.9169，final-only=4/LCR=0.9842，prune=2/LCR=0.9949。不能写 same-root matrix 已完整闭合，因为 `traditional / bridge / proposed` 的 matched six-row matrix 仍不完整。

### Naturalization miniset

`lsystem_branch/fork_side` 四列可作为 visual/export ablation：

| variant | GLB import | faces | MB | occ proxy | claim gate |
|---|---|---:|---:|---:|---|
| rule-only | ok | 938204 | 51.717 | 0.0675 | source mesh remote-only |
| no-N | ok | 1098956 | 60.196 | 0.0675 | source mesh remote-only |
| weak blend | ok | 927980 | 50.846 | 0.0767 | source mesh remote-only |
| masked local-N | ok | 1571798 | 75.890 | 0.1122 | source mesh remote-only |

只可写四列均能进入同一 texture/export path 并通过本地 GLB import/material QA。不能 claim topology repair、root reachability、anchor preservation、mask leakage 或 naturalization/projection 的分离贡献。

## 3. Metric 推荐

主表必须保留这些列：

- geometry：vertices、faces、file size MB。
- connectivity：raw face components、welded components（若可得）、occupancy components 6N、occupancy LCR。
- task semantics：root reachability（仅在有 root/anchor 定义时报告）、orphan/fragment ratio、copy repetition score（mesh-space generated-root 必须报告）。
- pipeline QA：asset path、render/import success、visual QA status、failure label。
- claim gate：status、missing/blocked reason、notes。

解释规则：

- Raw components 高适合诊断 direct concat/copy-paste，但不能单独等价于视觉失败。
- Occupancy LCR 高也不能单独等价于成功，coral mesh-space generated-root 就是反例：LCR=0.992，但 raw comps=250404 且 copy_repetition_score=1。
- Hunyuan/TRELLIS non-2 行必须保留 blocked slot，等远端交付 repo/package/weights/outputs 后再补数值。
- 对 naturalization，当前只能报告 GLB import/material/occupancy proxy；source OBJ 未本地化前不要填 root/mask/topology 指标。

## 4. Blocked / 缺证据行

必须显式保留这些 blocked/missing 行：

| scope | rows | blocker |
|---|---:|---|
| TRELLIS non-2 image one-shot | 3 | Lane A 尚未交付 runnable TRELLIS 非 2 输出 |
| Hunyuan3D 2.0 image one-shot | 3 | 尚未交付 Hunyuan image-to-3D 输出 |
| Hunyuan3D 2.0 image+texture | 3 | 尚未交付 Hunyuan textured 输出 |
| Hunyuan3D mesh-space generated-root | 3 | 需要 Hunyuan root mesh 后才能本地复制生成负控 |
| strict `ours_vine` | 1 | weak strict row，主文正例应换 stronger vine stage5 |
| Naturalization source OBJ | 4 | source mesh 仍为 remote-only，阻塞 topology/root/mask metrics |
| full same-root matrix | 多行 | miniset 已可用，但 full `traditional/direct/final-only/prune/bridge/proposed` matched matrix 未闭合 |

## 5. CSV 使用说明

`baseline_case_pool_recommendations_20260510.csv` 每行包含：

- `category` / `case_id` / `case_label`
- `status` / `recommended` / `method_role`
- `asset_path` / `metric_source`
- `primary_metrics` / `metric_recommendation`
- `claim_safe_use` / `blocked_reason` / `notes`

其中 `controlled_main` 是建议主文子集；`blocked_or_missing_baselines` 是必须保留的 claim gate；其他类别是可选图池或 appendix pool。
