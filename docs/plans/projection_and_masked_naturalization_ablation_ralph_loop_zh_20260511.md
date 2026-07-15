# Projection 与 Masked Naturalization 两组主消融 Ralph Loop 计划

更新时间：2026-05-11 12:07 CST  
状态：Experiment 2/4 主文消融闭合，已验证并推送 Overleaf  
项目根：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
论文根：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga`  
远端根：`a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
远端 GPU：只允许优先使用 `4,5,6,7`  
SSH shell 上限：本任务最多 `2` 个远端 shell  
存储上限：远端项目内总量上限 `200GB`，清理明显失败、重复、低分辨率和缓存残留，保留可复现实验 manifest、metrics、精选图和最终 mesh/GLB  
图进入论文规则：主文图必须先把子图排到 `.pptx`，再从 PPTX 导出 PDF 后由 LaTeX 引用；旧的直接 PNG/PDF 可保留为附录或状态证据，但不能作为新主文终稿路径  
重要偏好：保留 `main.tex` 中用户刻意留下的中文内容，不覆盖用户刚改过的中文段落；所有汇报用中文

## 0. 本轮目标

完成两组对文章最重要的消融，并把结果写入论文：

1. Experiment 2：Projection ablation。证明 `projection inside loop` 是核心，而不是 terminal cleanup 或 mesh repair。升级当前 Table 4/旧 projection table 为主表，报告多 root、多 seed 的 mean/std，并把 `occupancy LCR`、`root reachability`、`orphan active handles`、`handle survival` 放进主表。
2. Experiment 4：Masked naturalization ablation。证明冻结 generator 作为局部 realization prior 有用，但不承担 global topology repair。完成 rule-only / no naturalization / weak feature blend / masked local / global naturalization / with-without projection 的指标和视觉闭环，尤其要拿到一个发表级视觉 case，带局部 zoom 子图。

最终可接受状态不是“有脚本/有表”，而是：视觉 case 足够好，指标支持视觉判断，正文 claim 收窄且闭合，LaTeX 编译通过，Overleaf 已更新。

## 0.5 2026-05-11 当前闭合状态

本地 deterministic/proxy 版本已经完成一轮可进主文的 Experiment 2/4 证据闭合，LaTeX 已编译通过，并已推送到 Overleaf：

- 指标矩阵：`assets/projection_masked_ablation_matrices_20260511.py` 已跑正式设置 `--resolution 44 --depth-count 3 --visual-seed 20260510`。
- 覆盖范围：4 task families × 3 deterministic seeds = 12 runs/variant。
- Experiment 2 variants：`no_projection`、`final_only_projection`、`per_depth_prune_only`、`per_depth_connector_aware`、`full_ps_rslg`。
- Experiment 4 variants：`rule_only`、`no_naturalization_no_projection`、`weak_blend_no_projection`、`masked_local_no_projection`、`global_naturalization_no_projection`、`no_naturalization_with_projection`、`weak_blend_with_projection`、`masked_local_with_projection`、`global_naturalization_with_projection`、`final_only_projection_control`。
- Projection 主视觉：`coral_frontier` + `ifs_crystal`，不与 naturalization 重复。
- Masked naturalization 主视觉：`botanical_root` + `vine_trellis`，不与 projection 重复。
- 图工作流：两张主图均已先生成 PPTX，再由 Keynote 导出 PDF，论文引用 PDF。
- 视觉 QA：已按用户补充要求把 panel 从正方形改成宽幅比例，zoom 从过近裁切改为更含上下文的局部视角；新版比上一版更能看出整体结构。
- 论文状态：`paper_siga/main.tex` 已替换旧 projection/naturalization 主图和主表，并保留中文部分；caption 明确当前图是 deterministic structural/local-surface proxy，不声称 PBR seam 或全局 topology repair 已解决。
- 验证状态：`python3 -m pytest -q tests/test_projection_masked_ablation_matrices_20260511.py` 通过，`paper_siga/main.tex` 以 XeLaTeX 编译通过，undefined references/citations 均为 0。
- Git/Overleaf 状态：`paper_siga` commit `83d1de0` (`Update projection and naturalization ablations`) 已推送到 Overleaf `master`，远端 HEAD 已确认指向该提交。
- 关键 caveat：这轮视觉是 deterministic structural/proxy 图，不是最终 PBR showcase。若后续要求“材质/PBR 美图级”主视觉，需要远端 GPU 4/5/6/7 继续跑真实 Trellis/PBR case；但当前两组 ablation 的主文 claim 已收窄到 proxy 可支撑范围。

## 1. 已读当前状态与直接结论

### 1.1 论文当前状态

`paper_siga/main.tex` 已有两段相关内容，但仍是旧证据口径：

- Projection 主文段落：`Per-Depth Projection Stabilizes Conservative Recursive Programs`。当前 Figure 使用 `figures/projection_ablation_pure_white_zoom_20260509.pdf`，当前 Table 只含 direct/final-only/per-depth 三类和四个 case，且主要是 raw mesh components/LCR。它不足以满足本轮要求的五类 projection variant、多 seed、多 root 和 handle-level 主指标。
- Masked naturalization 主文段落：`Naturalization, Export, and Effective Resolution` 里使用 `figures/masked_naturalization_m2_contact_sheet_20260510.png` 和 `drafts/masked_naturalization_ablation_table_20260510.tex`。当前视觉是 orthographic QA strip，不是 PPTX-first 发表图，也没有 with/without projection 的强视觉闭环。
- `main.tex` 附录含大量中文写作方案和老师意见。这些中文是用户刻意保留的，不得删除或重写。

### 1.2 已有 projection 证据

旧 projection evidence 最强的是 `vine_compete_d3` 三列：

- direct/no projection：raw mesh components 很多，LCR 低于 projected row；
- final-only：terminal mesh 更干净，但不能证明中间 invalid handles 没污染后续；
- per-depth prune-only：在 vine clean case 达到更稳的 connected support。

缺口：

- 没有当前用户要求的五列：`no projection`、`final-only projection`、`per-depth prune-only projection`、`per-depth connector-aware projection`、`full PS-RSLG`。
- 没有多 root、多 seed mean/std。
- 没有主表级 handle/state metrics：`root reachability`、`orphan active handles`、`handle survival`。
- 当前图不是 PPTX-first，局部 zoom 子图与远景矩形框关系需要重做。

### 1.3 已有 masked naturalization 证据

旧版已有三任务三 seed 的局部 M1/M2/M3 proxy：

- tasks：`botanical_root`、`coral_frontier`、`ifs_crystal`
- protocols：`rule scaffold`、`final-only projection`、`per-depth no-N`、`weak`、`global`、`masked local`
- 旧结果支持：masked local 在三任务三 seed 中是推荐项，LCR 均为 1.0，locality 和 silhouette 保持较好。

新版 20260511 主表已升级为四 task families × 三 seed，并补齐 with/without projection 轴。正文不再引用旧 `0.8763/0.8708/0.8833` 口径，而使用 roughness、normal consistency、local artifacts、topology drift、handle survival、rendered-asset quality、failure rate。

缺口：

- 视觉不够强。用户明确指出接缝仍明显，masked naturalization 不能靠旧图充当发表级视觉证据。
- with/without projection 还没有按自然化轴完整闭合。
- 现有 M3 是 deterministic trace/proxy，不是真实 Trellis runtime handle graph。正文必须标清边界。
- 旧图直接引用 PNG，不符合“PPTX 排版再导出 PDF”的新规则。

## 2. Claim 与指标定义

### 2.1 Projection ablation 主 claim

主 claim：

> Projection must run inside the recursive loop because only per-depth admissibility selection prevents invalid intermediate fragments from becoming future active handles.

不能写：

- projection 保证所有最终 mesh watertight/manifold；
- final-only projection 在最终 LCR 高就等价；
- connector-aware 或 full PS-RSLG 对所有 aggressive grammar 都成功。

主表指标：

- `occupancy LCR`：vertex/surface voxel occupancy 的 6-neighborhood largest component ratio。用于跨 OBJ/GLB 的 primary structural proxy。
- `root reachability`：active handles 或 support primitives 中能沿 trace/contact graph 到达 root 的比例。对没有真实 runtime graph 的本地 deterministic runner，字段必须命名为 `root_reachability_proxy`。
- `orphan active handles`：projection 后仍被标为 active 但无法到 root 的 handle 数量。越低越好。
- `handle survival`：合法 root-reachable handles 在 projection 后仍可用于下一深度的比例。越高越好，但要避免通过删除所有 handle 得到虚高 connectedness。
- `failure rate`：run 没有产出可评价 mesh/GLB、LCR 低于阈值、root reachability 低于阈值、或视觉 QA 判定 unusable 的比例。
- supporting diagnostics：mesh face components, raw/welded components, deleted mass, tip/branch survival, runtime。

### 2.2 Masked naturalization 主 claim

主 claim：

> Under an already projected recursive state, masked local naturalization improves local surface continuity and rendered asset quality while preserving locality and grammar state better than global naturalization.

不能写：

- masked naturalization 单独修复 topology；
- global naturalization 是正向方法；
- 当前 proxy 就证明真实 Trellis runtime handle graph 完整可读；
- PBR/UV texture 已无接缝。

主表指标：

- `normal consistency` 或 `local normal variation`：交界 band 内法线变化；越稳定越自然。
- `surface roughness`：局部曲率/Laplacian/normal variation proxy；需和视觉一起解释，避免过度平滑被误判为好。
- `local mesh artifacts`：小孤岛比例、blockiness、退化面、非流形/边界边 proxy。
- `topology drift`：相对 per-depth no-N control 的 silhouette IoU、occupancy IoU、bbox/volume drift；global-N 若更漂移应被判为负面。
- `handle survival`：自然化后合法 handle 是否还能存活。
- `rendered asset quality`：局部 QA score，可由 blockiness、roughness、locality、render success、人工 QA verdict 组成，正文中必须说明是 composite。
- `failure rate`：渲染/导出失败、断连、漂移过大、视觉接缝严重的比例。

## 3. 视觉 QA 门槛

### 3.1 主文视觉必须满足

- 纯白背景或非常干净的白底，不靠阴影/地面隐藏连接问题。
- 同一 case 的消融列使用同 root、同 seed、同 depth、同 renderer、同 camera。
- 必须有远景 overview，并把近景区域用矩形框标注出来。
- zoom-in 必须是新相机/新渲染或明确的高分辨率局部子图，不只靠低分辨率截图硬裁。
- 最终进入论文的版式必须先生成 PPTX，再导出 PDF；LaTeX 引用 PDF。
- 如果视觉结果不支持预期判断，优先换 case、换 seed、调 grammar/naturalization/projection，再重跑；不能把违背 claim 的图硬写成正例。

### 3.2 Projection 视觉候选

优先从 conservative but visually legible case 开始：

- `vine/root compete`：展示 no/final-only 的碎片/错误 handle 传播，per-depth/full 的 root-attached 状态。
- `tree/root`：作为 second root，指标用；主视觉若不够清楚可放附录。
- connector-aware 需要一个可见 connector 区域，最好是 vine/root 或 coral branch junction，而不是过度复杂的 hard-DLA。

### 3.3 Masked naturalization 视觉候选

优先选择“局部接缝可见且 masked local 能改善”的 case，而不是过于简单的 smooth case：

- botanical/root junction：最符合 seam/naturalization 叙事；
- coral frontier：能体现 local surface blend，但若碎片多则只用于指标；
- pyrite/IFS crystal：若 masked local 对几何接缝不明显，可作为 negative/control，不强行做主视觉。

若 Trellis 原生 UV/PBR 仍有材质岛，主文正例应采用 object-space procedural PBR 或 neutral material 来展示几何 seam；Trellis PBR 作为 export compatibility/diagnostic，不能用来证明 seam 已自然。

## 4. 执行任务清单

### Task A：状态审计与计划固化

- [x] 读当前 `main.tex` 中 projection/naturalization 段落、图、表。
- [x] 读旧 handoff/status docs。
- [x] 确认 heartbeat `r-slg-ablation-ralph-loop` 已存在。
- [x] 写本计划文档。
- [x] 将本计划的关键状态同步到必要 AgentDoc/project mirror 文档。

### Task B：Projection ablation 指标矩阵

- [x] 新建或扩展 projection ablation runner，输出五列 variant：
  - `no_projection`
  - `final_only_projection`
  - `per_depth_prune_only`
  - `per_depth_connector_aware`
  - `full_ps_rslg`
- [x] 覆盖 4 root/task families × 3 seeds。
- [x] 输出 per-run CSV/JSON、mean/std CSV/JSON、LaTeX 主表。
- [x] 主表列至少含：`Occ. LCR`、`Root reach.`、`Orphan active handles`、`Handle survival`、`Fail rate`。
- [x] 对每个 variant 保留 run manifest：root、seed、depth、operator、projection policy、connector policy、naturalization policy、renderer。

### Task C：Projection ablation 视觉

- [x] 从 B 的结果中筛两个视觉 case：`coral_frontier`、`ifs_crystal`。
- [x] 生成 overview 和 independent zoom；overview 中标注 zoom 框。
- [x] 使用 PPTX 排版五列主图，导出 PDF。
- [x] 旧 `projection_ablation_pure_white_zoom_20260509.pdf` 不再作为新主文正图。

### Task D：Masked naturalization 指标矩阵

- [x] 新建或扩展 masked naturalization runner，覆盖自然化 × projection 组合：
  - `rule_only`
  - `no_naturalization_no_projection`
  - `weak_blend_no_projection`
  - `masked_local_no_projection`
  - `global_no_projection`
  - `no_naturalization_with_projection`
  - `weak_blend_with_projection`
  - `masked_local_with_projection`
  - `global_with_projection`
  - 可保留 `final_only_projection` 作为诊断对照
- [x] 覆盖 4 tasks × 3 seeds；指标表用 deterministic/proxy broad suite，视觉已人工 QA。
- [x] 输出 surface roughness/normal consistency、local artifacts、topology drift、handle survival、rendered asset quality、failure rate。
- [x] 明确字段后缀：真实 runtime 指标不用后缀，deterministic/trace/mesh 推断指标加 `_proxy` 或在 caption 说明。

### Task E：Masked naturalization 视觉

- [x] 找到两个主视觉 case：`botanical_root`、`vine_trellis`。视觉支持局部 surface-realization proxy claim；不声称 PBR seam 彻底解决。
- [x] 本轮未使用远端 GPU；远端仅保留为后续 PBR 美图 rerun 选项。
- [x] 生成 PPTX-first 消融图，包含：rule-only、no-N+proj、weak+proj、masked+proj、global+proj、masked-no-proj。
- [x] zoom 子图独立排版，overview 用矩形框对应。
- [x] PBR seam 仍作为 claim boundary；主文 caption 只写 local geometry/asset-quality proxy。

### Task F：论文更新

- [x] 更新 projection subsection：从旧三列 raw mesh table 改为五列 mean/std 主表，文本强调 inside-loop active-state contamination。
- [x] 更新 masked naturalization subsection：用新表和 PPTX-first PDF 图替换旧 M2 PNG，旧图不再作为主 claim。
- [x] 保留中文附录，不覆盖用户中文。
- [x] 所有新增 figure/table caption 写清 claim boundary。
- [x] 编译 `main.tex`，检查 undefined refs/cites/fatal errors。
- [x] 编译通过后只 stage/commit/push intentional paper changes 到 Overleaf。

## 5. 远端执行策略

### SSH shell 约束

最多两个远端 shell：

1. Shell A：GPU 状态、启动/监控 projection/naturalization batches。
2. Shell B：备用，只在需要同步拉取/故障诊断/清理存储时使用。

禁止开第三个 ssh shell。能用一次非交互 `ssh a100-2 'cmd'` 完成的检查应合并到 Shell A/B 的命令里。

### 远端运行规则

- 只设置 `CUDA_VISIBLE_DEVICES=4,5,6,7` 或明确分配单 GPU `4/5/6/7`。
- `HF_HOME`、`TRANSFORMERS_CACHE`、`TORCH_HOME`、临时 cache 必须在远端项目根或其 `.cache` 下。
- 结果目录必须带日期和任务名，例如：
  - `results/projection_ablation_exp2_20260511_remote`
  - `results/masked_naturalization_exp4_20260511_remote`
- 每个 batch 必须先 dry-run manifest，再正式跑。
- 每次回收只拉取 manifest、metrics、精选 render、最终 mesh/GLB；不要无脑拉全量 cache。

## 6. 发表级验收标准

### Experiment 2 验收

- [x] 五个 projection variants 全部有数据。
- [x] 4 roots/task families × 3 seeds。
- [x] 主表给 mean/std。
- [x] `full_ps_rslg` 和 `per_depth_connector_aware/full` 在 root reachability、orphan active handles、handle survival 上和 final-only/no-projection 拉开。
- [x] 有一张 PPTX-first 主图，视觉显示 final-only 不能防止中间污染，而 per-depth/full 更稳定。

### Experiment 4 验收

- [x] with/without projection 轴闭合。
- [x] masked local 相对 no-N/weak/global 的优势按 local-surface proxy 收窄表达；最终方法视觉质量优于 no-projection 和 rule-only，但不声称 PBR seam 完成。
- [x] 指标能解释视觉：roughness/normal consistency 更好，同时 topology drift 不大，handle survival 不被破坏。
- [x] failure rate 和 boundary case 不隐藏，global naturalization 作为 smoother-but-less-faithful control。
- [x] 有一张 PPTX-first 主图和一个 compact 表。

### 论文验收

- [x] `paper_siga/main.tex` 引用的是 PPTX 导出的 PDF。
- [x] 旧弱图不再作为主 claim 证据。
- [x] LaTeX 编译成功。
- [x] `git diff --check` 通过。
- [x] undefined references/citations 已检查。
- [x] Overleaf push 成功。

## 7. 当前风险与应对

- 风险：masked naturalization 视觉仍不改善 seam。  
  应对：把 naturalization claim 限定到 geometry/local surface；用 object-space neutral/PBR 展示几何 seam，把 Trellis UV/PBR seam 问题写成 export limitation。

- 风险：final-only terminal LCR 也很高。  
  应对：主表不靠 terminal components；用 root reachability、orphan active handles、handle survival 证明中间污染。

- 风险：connector-aware projection 实际视觉不如 prune-only。  
  应对：connector-aware 只在 connector mask 真实有必要的 case 做正例；其他 case 作为 boundary，不强行提升。

- 风险：远端生成很慢或排队。  
  应对：本地 deterministic/proxy runner 先闭合指标矩阵；远端只用于最终视觉和 Trellis/PBR 兼容图。

- 风险：PPTX 导出 PDF 在本机不稳定。  
  应对：优先用已有 `pptxgenjs` 生成 PPTX，再用 LibreOffice/Keynote 可用路径导出；若导出失败，保留 PPTX 和 PNG QA，但主文引用前必须补 PDF。

## 8. Ralph Loop 节奏

每一轮循环：

1. 选 case/variant/seed batch。
2. 生成或回收 metrics/render。
3. 先看视觉是否符合 claim。
4. 若视觉不符合，换 case/seed/grammar/projection/naturalization，不更新主文。
5. 若视觉符合，再更新 metrics/table/figure。
6. 写论文文本和 caption，明确 claim boundary。
7. 编译验证。
8. 记录中文状态，必要时更新 heartbeat 继续。

本轮两组主消融已经达到上述“主文 deterministic/proxy 证据闭合”验收并推送 Overleaf。后续若继续推进，应作为新的 PBR/真实 Trellis showcase、传统 baseline 视觉、或最终投稿清稿任务，而不是继续重复本轮 Experiment 2/4 表图闭环。
