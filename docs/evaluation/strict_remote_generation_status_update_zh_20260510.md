# 严格远端生成批次评估与选择更新（2026-05-10）

范围：本文是当前 strict remote-generation 批次的中间评估/选择更新，不是最终论文结论；不启动远端任务，不修改 `paper_siga`。目标是给后续用户挑图、V13/V14/V15 拉回后建 gallery index、以及下一轮一对一 baseline 比较提供清晰边界。

## 0. 用户纠偏必须执行

最终一对一 baseline comparison 必须来自 `a100-2` 上通过算法改动或新增 case 重新生成的结果。不能把本地已有图“挑好看的”、不能只做本地 postprocess/repair、也不能用 loose semantic match 替代 strict matched task。

允许本地做的事情只有：

- 汇总、索引、QA、指标读取、contact sheet 组织；
- 记录已有 V6-V13 的证据和失败模式；
- 准备 V13/V14/V15 拉回后的用户挑选 gallery。

不允许把这些本地整理动作写成“最终生成结果已解决”。

## 1. 已完成

| 项目 | 状态 | 证据用途 |
|---|---|---|
| V6 strict matched connectivity/root/SC/IFS 候选 | 已有本地 manifest/gallery，可作为 L-system、SC、IFS 下一轮复跑基线 | diagnostic-only；部分可作为下一批 `a100-2` 多 seed 输入 |
| V8 / V8-thin DLA frontier refine | 已有 lace、antler、frontier membrane、crystal blade 等候选 | diagnostic-only / frontier-rich comparator |
| V9 organic frontier | 多 seed 远端 summary `ok`，提供更有机的 frontier/tip/ridge 形态 | diagnostic-only；需要人工筛选，不能按 `status=ok` 晋级 |
| V10 readable coral/frontier | 改善 V9 过密问题，轮廓更可读 | diagnostic-only / fallback |
| V11 clean staghorn/table | 拓扑和可读性较稳 | diagnostic-only；rod/smooth 风险仍在 |
| V12 tapered staghorn/table | 修正 V11 terminal cut-end，适合作 DLA 主候选池 | partial candidate；仍需 blockiness/frontier 指标与人工 verdict |
| V13 smooth coral/crystal | 初始 mesh connectivity 已做到单 component / LCR 1.0 | topology pass；视觉审计仍未通过 final gate |

## 2. 部分完成

1. **DLA/coral/frontier 主线**：V11/V12/V13 已把“连通性”和“末端截断”推进很多，但 V13 视觉仍被审计为 coral/frontier shell/claw-like，不能作为最终正例。V8 的 frontier-rich 细节仍应保留作对照，因为 V12/V13 可能过 smooth。
2. **L-system / SC / IFS 严格匹配**：V6 有 case 名、控制参数和 gallery 证据，但还缺基于 `a100-2` 的最终多 seed 生成、post-GLB 指标、family-specific metrics 和人工 QA。
3. **用户挑选 gallery**：已有旧 gallery 和 contact sheets，但需要等新 V13/V14/V15 拉回后，用脚本重新扫描 `visuals/` 和 `results/`，按 family 与 readiness 输出 markdown/CSV 索引。

## 3. 尚未解决

| 缺口 | 当前判断 | 下一步门槛 |
|---|---|---|
| V13 final paper candidate | 未解决 | 需要证明不是 shell/claw/animal-shell/crystal-sheet，且通过 fixed camera zoom、frontier/tip/neck/porosity QA |
| V14/V15 最新结果选择 | 本地尚不能假设已完成 | 拉回后按 index + 人工 QA 分成 paper-candidate、diagnostic-only、reject/negative |
| IFS tree / branch transform-copy | 未解决 | 必须新生成真正 transform-copy branch/tree asset；pyrite/lattice 不能替代 IFS tree |
| SC attractor coverage | 未解决 | 必须报告 attractor coverage、nearest-attractor distance、terminal path-to-root |
| L-system visible hierarchy | 未解决 | 必须看见 trunk/branch/rootlet/needle/tendril 层级，不能是 blob 或纹理噪声 |
| DLA physical claim | 不应解决为强 claim | 只能写 frontier-attachment asset generation；不能写物理 DLA、真实珊瑚或真实晶体生长 |

## 4. 当前选择建议

| readiness | 放入内容 | 用途 |
|---|---|---|
| paper-candidate | 仅放拉回后同时满足 strict task、`a100-2` provenance、mesh/PBR render、metric pass、human QA 的 case | 用户最终挑主文候选 |
| diagnostic-only | V6-V13 中能说明进展、失败模式、frontier-rich 对照、topology pass 但视觉未过关的 case | 支撑状态更新、appendix、下一轮参数选择 |
| reject/negative | shell/claw、rod/cut-end、blob、wrong mode、over-smooth、fragmented surface 或 do-not-claim case | 失败分析和排除项 |

V13 目前应放 `diagnostic-only`，不是 `paper-candidate`。V11/V12 可作为 DLA/coral fallback 或横向对照，但不应直接写成 final solved。V8/V9/V10/V11/V12/V13 都有状态证据价值，尤其用于说明从 blocky/rod/cut-end 到 connectivity/topology pass 的演化，以及为什么仍需要 V14/V15 或后续算法改动。

## 5. Gallery index 准备

新增脚本目标：

```text
scripts/figures/build_remote_generation_case_gallery_index_20260510.py
```

使用方式：

```bash
python3 scripts/figures/build_remote_generation_case_gallery_index_20260510.py \
  --repo-root /Users/fanta/code/agent/Code/recursive_3d_generative_growth \
  --output-dir <gallery_output_dir>
```

默认行为：

- 扫描本地 `visuals/` 与 `results/`；
- 读取 strict matched texture / pair / proxy / target 的 contact sheet 与 `manifest.csv`；
- 生成 `remote_generation_case_gallery_index_20260510.md` 和 `.csv`；
- 按 series、family、readiness 组织；
- 只写链接，不复制大图。

可选复制 contact sheet：

```bash
python3 scripts/figures/build_remote_generation_case_gallery_index_20260510.py \
  --repo-root /Users/fanta/code/agent/Code/recursive_3d_generative_growth \
  --output-dir <gallery_output_dir> \
  --copy-contact-sheets
```

该复制只针对 contact sheet，不复制 GLB/OBJ/中间大文件。

## 6. 论文写法边界

现在可写：

- strict remote batches 已经提供 V6-V13 的候选池、诊断和失败模式；
- V13 达到 topology pass，但视觉未过 final gate；
- 下一步必须用 `a100-2` 新生成/算法改动结果完成 strict one-to-one baseline comparison；
- 本地 index/gallery 只是选择与审计工具。

现在不可写：

- V13 已解决 DLA/coral/frontier；
- V11/V12/V13 是最终 paper-grade 主图；
- 本地 postprocess/repair 等同于远端生成；
- pyrite/lattice 证明 IFS tree；
- DLA/coral/crystal 是物理仿真成功。
