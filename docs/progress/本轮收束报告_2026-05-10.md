---
title: 本轮 Ralph Loop 收束报告 2026-05-10
date: 2026-05-10
tags:
  - recursive_3d_growth
  - trellis2
  - siga
  - ralph_loop
status: paused
---

# 本轮 Ralph Loop 收束报告 2026-05-10

本轮按用户要求已经收束并暂停 heartbeat。本文档汇总这一大轮和当前子任务完成情况、正负结果、方法论推进、实验缺口、论文状态、可视化状态和远端存储清理情况。

## 0. 当前状态

- heartbeat `recursive-trellis2-growth-research-loop` 已暂停。
- 远端 `a100-2` GPUs `4/5/6/7` 当前空闲。
- 远端项目目录仍为 `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`。
- 远端项目从 `98G` 清理到 `72G`。
- 本地论文 PDF 已可编译：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.pdf`，当前 27 页。
- 当前 `main.tex` 仍有实际 TODO：
  - `\EvidencePending`：约 14 个实际标记，grep 含宏定义为 15。
  - `\ExpFigTODO`：约 16 个实际标记，grep 含宏定义为 17。
- 本轮最后一个 GPU 子任务是 summary-only seed jitter profiling，没有写大 OBJ/PNG/GLB。

## 1. 本轮完成的任务

### 1.1 按 `agent_revision_and_experiment_requirements.md` 建立证据矩阵

已完成本地证据矩阵：

- 文档：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/evidence_matrix_for_revision_zh_20260510.md`
- CSV：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/evidence_matrix_20260510/evidence_matrix_for_revision_zh_20260510.csv`

矩阵共整理 19 项修订要求，逐项标注：

- `done` / `partial` / `missing`
- 可用文件
- 当前能支撑的论文表述
- 精确 caveat
- 下一步最小实验

最重要结论：当前证据能支撑的主线必须收窄为 **per-depth projection / admissible-state selection 抑制 conservative case 的 fragment propagation；selected projected/scaffold meshes 可进入 Trellis2 texture/PBR export path**。现在还不能支撑“整体 sparse-latent grammar 明确优于所有 mesh-space/traditional/generative baselines”。

### 1.2 论文文本按 revision 文档继续修订

已更新：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex`
- 状态文档：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/paper/text_structure_revision_status_20260510_002218.md`

主要变化：

- 进一步把标题、摘要、intro、related work、preliminaries、method 收束到 grammar/language-first。
- Projection 被写成执行语义和 admissible-state selection，不再作为唯一贡献。
- Texture/PBR 被降级为 export compatibility，不再作为核心方法贡献。
- 加入正文 / figures-only pages / appendix-supplement 的边界说明：
  - figures-only pages 不能引入新 claim、metric、algorithm 或论证；
  - appendix/supplement 主要放诊断、失败、扩展、长表；
  - 主文必须自洽，不能依赖附录图表才能成立。
- Classical-system coverage 在正文只保留简要主张，详细证明/推导仍应放 appendix/supplement。

编译状态：

- 本机 TinyTeX 路径可用：`/Users/fanta/Library/TinyTeX/bin/universal-darwin`
- `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` 成功。
- 仍有 ACM accessibility/metadata warnings、box warnings 和图片 alt-text warnings，但不是编译阻塞。

### 1.3 标准渲染协议切换为纯白、无平台、无地平线

已更新：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/blender_render_recursive_mesh.py`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/standard_pure_white_render_protocol_20260510.md`

变化：

- `--background` 默认从 `studio-gray` 改成 `white`。
- 默认渲染模式现在是纯白背景、无平台、无可见地面/地平线。
- 若需要正式图，优先输出透明 RGBA，再 flatten 到白底 RGB。
- 完成一个极小 smoke render：
  - alpha：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/smoke_pure_white_default_20260510/alpha/smoke_root_iso.png`
  - flat：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/smoke_pure_white_default_20260510/flat/smoke_root_iso.png`
- 像素检查：flat 输出四角均为 `(255,255,255)`。

### 1.4 给 `compete_grow` 增加真实 seed/jitter 支持

已更新：

- 本地：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/trellis2_recursive_slat_grammar_workflow.py`
- 已同步到远端：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/trellis2_recursive_slat_grammar_workflow.py`

原因：

- 之前的 `runtime_seed_stability_summary_only_ralph_20260510_0108` 实际是重复 profiling，不是真 seed robustness，因为 workflow 没有 `--seed` 参数，`compete_grow` 的 attractor 是确定性 `linspace/arange`。

新增参数：

- `--seed`
- `--compete-jitter`

默认 `--compete-jitter 0.0`，因此不影响旧 deterministic behavior。只有显式设置 jitter 才会给 `compete_grow` 的 attractor shell 加随机扰动。

### 1.5 完成一个低存储 seed jitter summary-only 诊断

远端：

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/runtime_seed_jitter_summary_only_ralph_20260510_0049`

本地同步：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/runtime_seed_jitter_summary_only_ralph_20260510_0049`

输出：

- `summary.json` x 4
- `seed_jitter_summary.csv`
- `seed_jitter_summary.md`

设置：

- cases：vine、pyrite
- seeds：11、22
- grammar：`compete`
- depth：8
- `--summary-only`
- `--compete-jitter 0.035`

结果摘要：

| group | n | final tokens | final faces | max decode seconds | 解释 |
|---|---:|---:|---:|---:|---|
| pyrite | 2 | 2688-2697 | 1862322-1871928 | 0.135-0.142 | 有真实 seed/jitter 差异，但只是 summary-only |
| vine | 2 | 808-820 | 284406-287838 | 0.081-0.084 | 有真实 seed/jitter 差异，但只是 summary-only |

结论：

- 这补上了“workflow 可以真实接收 seed/jitter 并产生不同 token/mesh footprint”的最低证据。
- 不能作为 topology、visual、root/tip robustness 证明。
- 后续若要写 seed robustness，仍必须在正式 P0 matrix 中输出 per-depth metrics、mesh render、mean/std。

### 1.6 远端存储清理

清理前：

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`：`98G`

清理后：

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`：`72G`

清理策略：

- 只删旧的、重复的、明显 negative/diagnostic 或可再生成的大结果目录。
- 保留 `summary*.json`、`run_config.json`、`*metrics*.csv/json`、CSV 等小证据文件。
- 小证据文件已归档到：
  - 远端：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/docs/cleanup_archives/20260510_cleanup_before_pause`
  - 本地：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/remote_results/cleanup_archives/20260510_cleanup_before_pause`

主要删除目录：

- `results/trellis2_recursive_masked_repair`：5.8G
- `results/trellis2_recursive_masked_blend`：4.3G
- `results/siga_compete_masked`：3.0G
- `results/siga_dla_cluster_masked_blend`：1.8G
- `results/pyrite_connectivity_flow_grid_ralph_20260509_2340`：3.6G
- `results/connectivity_depth_flow_ralph_20260509_2310`：5.5G
- 若干重复 DLA bridge / public guide texture 目录：约 2G

没有删除：

- HF/Trellis2 权重与 cache。
- 当前 paper figures。
- 当前 case gallery。
- 当前 selected visual candidates。
- 当前 metrics/docs/summary aggregates。

## 2. 方法论推进情况

### 2.1 PS-RSLG / grammar-first 框架

已推进到可写入 paper draft 的状态。当前主框架是：

> Projection-Stabilized Recursive Sparse-Latent Grammar (PS-RSLG)

核心表述：

- 递归资产生成是 finite-depth recursive grammar execution。
- 语法拥有 topology、handles、frontiers、attachment certificates、rule traces、projection schedule。
- Trellis2/frozen sparse 3D generator 提供：
  - sparse native state；
  - mesh-to-sparse encoding；
  - sparse-to-mesh decoding；
  - masked/local realization；
  - selected texture/PBR export。
- Projection 是每层递归 transition 内部的 admissible-state selection，而不是最后 mesh cleanup。

当前可以保守写入论文的理论点：

- IFS、L-system、space-colonization、DLA/frontier、shape grammar 可作为 restricted rule families。
- Connected sparse support / root-attached active handle 是递归状态不变量。
- Per-depth projection 相比 final-only cleanup 的理论优势是：invalid fragments 在成为下一层 parent/frontier/cache/source 前被压制。
- Texture/PBR 不是结构证明，只是 selected projected mesh 的 export path。

仍不足：

- 还没有把所有 grammar components 用完整消融证明必要。
- 对 symmetry/equivariance、infinite recursion、cache/window 的理论 claim 仍偏 proposal / appendix。
- 对 DLA/physical crystal 不能写成已解决；只能写 crystal-inspired/lattice scaffold 和 stress case。

### 2.2 Projection / admissible-state selection

正面结果：

- conservative vine/tree `compete` 方向已有强数值证据：
  - direct recursion 出现大量碎块；
  - final-only cleanup 只能处理末端；
  - per-depth projection 在 conservative cases 中能显著抑制 fragment propagation。

负面/边界：

- aggressive fork、radial、DLA-like、某些 bridge/close 策略仍会碎块化。
- bridge 或 sparse close 有时改善 face diagnostic，却恶化 occupancy connectivity。
- 不能把 bridge 写成人工修网格；如果保留，只能作为 model/grammar-proposed connector mask 或 traditional repair baseline。

### 2.3 Sparse competition / space competition

已完成：

- 传统 space-colonization baseline 脚本和 strong baseline metrics。
- tree/root/vine fair sanity check 显示传统方法也能保持 occupancy-connected。
- 论文应该诚实写：传统方法结构控制很强，我们不是靠 connectivity 指标“击败传统方法”。

可支撑的 claim：

- Sparse competition 是 PS-RSLG 的一个 rule family。
- 它与 projection 结合后在 conservative branching/vine/root case 中比较稳定。

仍不足：

- 缺完整 same-root matrix，将 traditional/direct/final-only/prune/bridge/proposed 放在同一表里。
- 缺 root/junction/tip zoom QA。

### 2.4 Flow/SDE / masked naturalization

当前结论偏负面：

- global flow / sampler-only 更适合作为 negative/control。
- 它不能替代 grammar attachment/projection。
- 现在不能写“masked naturalization 已稳定提升表面质量且不漂移”。

仍需补：

- rule-only、no-N、weak blend、masked local-N、global-N、with/without projection 的统一 ablation。

### 2.5 Cache / LOD / infinite recursion

已有：

- runtime/token growth summary-only profiling 覆盖 depth 3/6/10/12/20、broad grammar 和 saturation。
- 结果证明 executor/decoder 可以做有限深度低存储 profiling。
- 典型 stress：
  - pyrite depth20 约 3.75M faces；
  - bismuth broad/saturation token 和 memory 最大；
  - reserved memory 约 5GB 量级。

不能支撑：

- effective resolution 超过 one-shot。
- infinite recursion 可视化成立。
- cache/LOD/window 真正改善视觉或拓扑。

下一步必须做 one-shot vs recursive refinement，补 local feature scale、terminal detail、zoom retention。

### 2.6 Crystal / symmetry / non-tree

当前最强非树方向：

- pyrite / bismuth connected scaffold + Trellis2 textured export。
- 它们可以作为 crystal-inspired/lattice scaffold 和 PBR compatibility。

不能写：

- 物理晶体生长已解决。
- 严格 equivariance 已实验验证。
- DLA/铋晶体碎块问题完全解决。

特别注意：

- pyrite/bismuth 可以作为非树正例，但 DLA bridge、radial、fragmented crystal 仍要归入 stress/negative/boundary。

## 3. 视觉与图库状态

当前用户可挑图位置：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/case_gallery_for_user_20260509`

图库已经按类别和用途标注：

- `main-positive`
- `appendix-candidate`
- `appendix-depth-sweep`
- `appendix-baseline-ablation`
- `appendix-method-support`
- `boundary-negative`
- `negative-diagnostic`

当前最建议优先查看：

- pyrite depth4 / HQ warm：晶体/非树正例。
- bismuth occpos / warm：非树/PBR 兼容候选。
- vine stage4/stage5：植物/根系/递归 depth 展示。
- coral connected / density：可作为边界或 supporting，不宜过度 claim。
- traditional baseline texture / space-colonization：用于对照传统方法结构强但表面/材质弱。

当前标准渲染模式：

- 纯白背景。
- 无平台、无地平线。
- 透明 RGBA + 白底 flatten。
- 不使用 matplotlib/point cloud 作为正式视觉证据。

## 4. 论文状态

论文当前路径：

- TeX：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex`
- PDF：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.pdf`

当前论文能支持的主故事：

> 本文提出一种 generation-model-native recursive grammar over sparse 3D latents。语法控制递归结构，冻结 Trellis2-style sparse 3D generator 提供 native sparse state、masked local realization、decode/re-encode 和 selected texture export。关键执行语义是 per-depth projection / admissible-state selection，使 recursive state 在每层保持 root-attached、可寻址、可继续生长。

当前不能支持或必须弱化的故事：

- 不能说“完整解决 DLA/crystal/frontier growth”。
- 不能说“texture/PBR 是核心贡献”。
- 不能说“所有 baseline 全面击败”。
- 不能说“infinite recursion/effective resolution 已验证”。
- 不能说“masked flow/SDE naturalization 已正面成立”。

当前最大论文缺口：

1. latent-space vs mesh-space recursion 正式对比缺失。
2. 完整 same-root projection-stability matrix 缺失。
3. masked naturalization ablation 缺失。
4. effective resolution / recursive refinement 缺失。
5. fixed-camera root/junction/tip/failure zoom QA 缺失。

## 5. 正面结果

- Trellis2 mesh-first encode/decode、textured GLB export、PBR render 路线已经可用。
- 用户已认可当前纹理/PBR 质量大体可接受。
- pyrite/bismuth/vine 等 selected case 可作为主视觉候选。
- Conservative `compete` + per-depth projection 是目前最稳的主方法证据。
- 传统 baseline 已经实现，且指标说明它们很强，这有助于避免 strawman baseline。
- runtime/token growth summary-only profiling 可作为 complexity/scaling supporting evidence。
- 纯白无平台渲染协议已落地，后续可统一重渲染。
- 远端存储已清到 72G，后续继续实验空间充足。

## 6. 负面结果 / 风险

- DLA、radial、aggressive fork、某些 crystal/porous 生成仍碎片化，不能作为主正例。
- Bridge/sparse close/post repair 有时会造成假连接或 surface soup。
- Raw GLB face components 常常极多，必须使用 surface-voxel / vertex-voxel / welded-face diagnostics 分层解释，不能把 textured GLB 说成拓扑 clean mesh。
- Flow/SDE sampler-only 目前偏负面，不能写成主贡献。
- Baseline/metric 仍远未完全闭合；当前论文里的 TODO 不能清除。
- 当前 PDF 27 页是工作稿，不是投稿页数。

## 7. 剩余任务建议顺序

下一轮若恢复，建议按以下顺序做，不要再先铺新方向：

1. 完整 P0 same-root projection-stability matrix：
   - tree/root/vine；
   - traditional L-system；
   - traditional space-colonization；
   - direct sparse；
   - final-only；
   - prune-per-depth；
   - model-bridge；
   - traditional repair；
   - proposed。
2. 为 P0 matrix 做 pure-white fixed-camera overview + root/junction/tip/failure zoom。
3. latent-space vs mesh-space recursion 对比：
   - mesh procedural + texture；
   - mesh procedural + repair；
   - sparse rule-only；
   - sparse masked-N；
   - one-shot Trellis2；
   - image scaffold；
   - final-only。
4. masked naturalization ablation：
   - rule-only / no-N / weak blend / masked local-N / global-N / with/without projection。
5. effective-resolution / recursive-refinement：
   - one-shot vs recursive；
   - local feature scale；
   - terminal detail count；
   - zoom retention。
6. 晶体/非树只保留 pyrite/bismuth/lattice scaffold 正例，DLA bridge 继续作为 stress/negative，除非出现明确连通且语义清楚的新结果。
7. 论文压缩：
   - 主文 7 页目标；
   - references 后最多 2 页 figures-only；
   - appendix/supplement 单独处理。

## 8. 本轮主要新增/更新文件

- `paper_siga/main.tex`
- `paper_siga/main.pdf`
- `assets/trellis2_recursive_slat_grammar_workflow.py`
- `assets/blender_render_recursive_mesh.py`
- `docs/evaluation/evidence_matrix_for_revision_zh_20260510.md`
- `results/evidence_matrix_20260510/evidence_matrix_for_revision_zh_20260510.csv`
- `docs/visuals/standard_pure_white_render_protocol_20260510.md`
- `results/runtime_seed_jitter_summary_only_ralph_20260510_0049/seed_jitter_summary.csv`
- `results/runtime_seed_jitter_summary_only_ralph_20260510_0049/seed_jitter_summary.md`
- `docs/remote_results/cleanup_archives/20260510_cleanup_before_pause/cleanup_manifest.txt`

## 9. 暂停状态

本轮已按要求暂停：

- 没有继续开新实验。
- 没有继续让 heartbeat 自动推进。
- 远端 GPUs 4/5/6/7 空闲。
- 远端存储清理完成。
- 当前报告、证据矩阵、渲染协议和论文状态可作为下一轮恢复入口。
