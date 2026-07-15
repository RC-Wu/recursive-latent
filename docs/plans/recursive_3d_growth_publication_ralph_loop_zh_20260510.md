# Recursive 3D Generative Growth 发表级 Ralph Loop 计划

更新时间：2026-05-10 19:06 CST  
状态：active / publication-grade push  
本地项目根：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
论文根：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga`  
远端：`a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
远端 GPU：只用 `4,5,6,7`  
远端存储上限：用户已放宽到 `200GB`，但仍需清理明确不用的重复/失败/低分辨率 competing runs 和缓存残留。
SSH shell 上限：最多 3 个；默认 1 个非交互检查 + 1 个长任务 shell + 1 个备用  
Heartbeat：当前线程使用 `r-slg-publication-ralph-loop-2`，20 分钟唤醒继续推进；历史线程仍有 `r-slg-publication-ralph-loop` ACTIVE，不再新建重复 heartbeat。

## 0. 本轮总目标

把 PS-RSLG / Recursive Sparse-Latent Grammar 推到可投稿 SIGGRAPH Asia/TOG 风格的证据状态。最终完成不是“又跑了若干 case”，而是：

1. `masked local naturalization` 有闭合消融、可区分指标、白底相机 zoom 图、论文方法和实验文字。
2. `transform-copy / IFS / lattice` 在文章中成为 grammar operator admission/screening 的实证依据，而不是孤立 gallery。
3. 传统 baseline 做 strict one-to-one、同类别、同递归模式、同复杂度/深度、多 root/seed/grammar guide 的大规模生成、筛选、指标和最终白底多级 zoom 对比。
4. 所有主文 claim 都有对应指标和图；不成熟结果只放 appendix/status，不进入正向 claim。
5. 论文 `paper_siga/main.tex` 每次重要修改后本地强制编译，并 push 到 Overleaf remote `master`。

## 1. 不可漂移的口径

- 不做 loose semantic matching。每个比较从传统任务定义出发，ours 必须匹配 object category、coarse silhouette、visible recursive depth、growth/transform mode 和主要控制语义。
- 传统 baselines 不是 strawman。surface-sampled connectivity 已显示很多传统方法也连通；论文不能写“传统方法天然破碎”。
- Textured GLB/PBR 是 asset readiness 和视觉证据，不是拓扑证明。拓扑必须用 occupancy/surface voxel、root attachment、path-to-root、mesh diagnostics 等指标证明。
- Masked naturalization 是局部 surface/material realization operator；不能写成 global topology repair。
- Transform-copy 不是 Trellis2 strict equivariance。文章应写成 empirical operator admission：稳定 transform/orbit/lattice 进入 grammar，可失败 transform 作为边界和 negative controls。
- DLA/frontier 只能 claim frontier-attachment asset generation，不 claim physical DLA/coral/crystallization simulation。
- 最终视觉证据必须是 mesh/GLB/PBR 或 neutral mesh Blender render，纯白背景、正方形、多级相机 zoom、远景框选近景区域。点云/matplotlib 只作内部诊断。

## 2. 当前已确认状态

### 2.1 Masked naturalization

已有本地闭合小消融：

- `results/masked_naturalization_ablation_20260510/evaluation_current/metrics.csv`
- `results/masked_naturalization_ablation_20260510/evaluation_current/score_recommendations.csv`
- `visuals/masked_naturalization_ablation_zoom_20260510/masked_naturalization_ablation_contact_sheet_20260510.png`

当前三任务都推荐 `per_depth_masked_naturalization`：

| task | score | LCR | silhouette-vs-projection |
|---|---:|---:|---:|
| botanical_root | 0.904591 | 1.0 | 0.913689 |
| coral_frontier | 0.904822 | 1.0 | 0.904730 |
| ifs_crystal | 0.913500 | 1.0 | 0.925961 |

缺口：

- 全量 naturalization/projection matrix 仍是 `98 available / 132 missing`，还不是发表级闭合。
- 需要把五列/六列 protocol 明确成论文表格：rule scaffold / no-N / global-N / weak-N / final-only projection / per-depth projection / masked local-N。
- 需要指标更有区分度：locality preservation、mask-change mass、normal/roughness、blockiness、mesh quality、root attachment、branch/tip survival。

### 2.2 Transform / IFS / lattice

已有 V21 seed20293700：

- `results/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_20260510_remote/surface_metrics_occ64.csv`
- `visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_zoom_20260510/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_contact_sheet_20260510.png`

当前判断：

- `pyrite/lattice`、`radial`、`bismuth/Escher` 可作为 transform-copy/lattice 诊断。
- `IFS branch-tree` 仍失败，不能作为 IFS tree 正例。
- 文章主线应是“operator family 的 admission criterion”，不是“transform 结果好看”。

需要写进正文的逻辑：

1. Grammar library 不能任意收所有 transform；冻结生成器和 sparse codec 对 transform 不严格 commute。
2. 所以 operator admission 需要 empirical certificates：orbit consistency、contact survival、projection stability、semantic read、surface connectivity。
3. Pyrite/lattice/radial 是 positive certificate；branch-tree/axis mismatch 是 rejection/boundary。
4. 这支撑设计：PS-RSLG 用 group/lattice-complete transform-copy rules，并把 unstable transforms 降级为 appendix diagnostics。

### 2.3 Traditional baseline

当前 strict one-to-one 还没有最终闭合。已知主文候选：

- L-system：root fan 或 pine canopy，必须重新筛强 seed/root。
- Space colonization：root network 或 tree crown，必须带 attractor coverage。
- DLA/frontier：V8/V10/V11/V12 中选 coral cluster/frontier sheet，必须带 blockiness/frontier survival/porosity。
- IFS/transform：pyrite/lattice 或 radial ornament，不能用 pyrite 代替 IFS tree。

仍需大量生成：

- 多 root、多 seed、多 grammar guide、多参数。
- 远端 fresh Trellis2 textured GLB/PBR 输出，不靠本地后处理充正例。
- 每个 family 最少 2-3 exemplar，每个 exemplar 至少 4-8 candidates，最后按指标和视觉筛选。

## 3. 发表级验收门槛

### 3.1 主文 case 门槛

每个进入主文的 case 必须有：

- traditional target 定义和参数；
- ours root/source provenance 和 selection budget；
- operator composition；
- projection/naturalization schedule；
- texture/PBR guide；
- overview + 至少两级 camera zoom，白底，源区域框选；
- metrics CSV/JSON；
- 人工 QA verdict；
- 论文 caption 中明确 claim boundary。

### 3.2 主指标集合

Connectivity/topology：

- surface voxel component count `components_r0/r1/r2`
- largest component ratio `LCR_r0/r1/r2`
- root-attached ratio
- orphan mass ratio
- path-to-root rate
- attachment survival

Mesh quality：

- raw/welded face components
- non-manifold edge count
- boundary edge count / hole proxy
- degenerate face ratio
- normal consistency
- triangle aspect ratio
- Laplacian roughness
- blockiness score

Family metrics：

- L-system：branch depth, branch angle distribution, terminal/tip survival, needle/rootlet attachment
- Space colonization：attractor coverage, nearest-attractor distance, alive attractors, path-to-root
- DLA/frontier：frontier survival, tip/neck count, porosity, blockiness, bridge cost
- IFS/transform：orbit error, symmetry IoU, copy-contact survival, zoom consistency

Visual/semantic metrics：

- multi-view CLIP/DINO auxiliary scores only as secondary visual-semantic metric
- render success, GLB import success, texture/PBR channel status
- final human QA required for paper selection

## 4. 并行工作分配

### Worker A: Masked naturalization

Owner：Singer  
写入范围：`assets/`, `tests/`, `docs/evaluation/`, `results/`, `visuals/`  
禁止：直接改 `paper_siga/main.tex`

任务：

1. 补齐/整理五列或六列 masked naturalization 消融协议。
2. 增加 publishable metric aggregation：connectivity, locality, roughness, normal variation, silhouette, mesh quality, blockiness。
3. 生成论文可用 CSV/JSON/TEX 表格和中文文档。
4. 给主线程一份可插入论文的结果摘要和远端需求。

验收：

- 新脚本有测试。
- 现有 12 mesh 结果可复现 metrics。
- 输出至少一个 paper-ready compact table。

### Worker B: Transform paper story

Owner：Goodall  
写入范围：`paper_siga/main.tex`, `docs/paper/`, `docs/evaluation/`  
禁止：改 baseline/naturalization 脚本

任务：

1. 写中文修改大纲：transform 作为 grammar operator admission/screening。
2. 修改正文 Method operator 章节，引入 transform diagnostics 作为算子设计动机。
3. 修改 Experiments/Results，使 V21/pyrite/radial/lattice 成为论据。
4. 扮演 reviewer 批评，再基于批评二次修改；至少两轮小迭代。

验收：

- 文章故事闭合：operator definition -> admission certificate -> positive/boundary evidence -> claim boundary。
- 不声称 strict equivariance。
- 修改后可由主线程编译。

### Worker C: Baseline large generation

Owner：Ampere  
写入范围：`assets/`, `tests/`, `docs/evaluation/`, `results/`, `visuals/`  
禁止：改 `paper_siga/main.tex`

任务：

1. 设计 V23/V24 strict matched batch：L-system, SC, DLA/frontier, IFS/transform 全覆盖。
2. 多 root/seed/grammar guide/参数，优先视觉发表级。
3. 实现 local generator + launcher + tests + Chinese plan。
4. dry-run 输出 manifest/metrics，交给主线程远端启动。

验收：

- 每个 OBJ input pre-export LCR >= 0.999 或有明确 boundary tag。
- launcher 使用 GPU 4/5/6/7，cache 全在远端项目目录，禁用 `/tmp` 和 `/dev/shm`。
- 每个 case metadata 包含 traditional target, root provenance, operator composition, controls, selection budget。

### Worker D / main thread: Method figures

Owner：main thread，必要时再派视觉/图形 worker  
写入范围：`paper_siga/figures/method_diagram_drafts_20260510/`, `scripts/figures/`, `docs/figures/`, `docs/plans/`, `paper_siga/main.tex`

新增用户要求：

- 查找本地官方 OpenAI Codex 历史中最近完成的画图 agent 对话，作为额外上下文。
- 必读：
  - `paper_siga/figures/method_diagram_drafts_20260510/`
  - `docs/figures/method_diagram_design_plan_zh_20260510.md`
  - `/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_method_figures_plan_20260510.md`
- 现有方法图远未达到发表级。宁可不用弱图，也不要把 slide-like / dashboard-like 草稿放入主文。
- Trellis2 到主方法论这部分需要两级图：
  1. Preliminaries 第二节放一张 frozen Trellis2 substrate / sparse generator pipeline 图，展示主要模块：root/condition, O-Voxel support, Shape-SLAT features, masked/local sampler or naturalizer, mesh decoder, re-encoder, texture/PBR export。
  2. 主方法图中 copy/改造这张 frozen substrate，把 frozen 模块放进总框架，再突出 PS-RSLG grammar 如何和 frozen sparse latent 交互：handles/rules/proposals/masks -> frozen sampler/decoder -> projection -> re-encode -> next grammar state。
- 其他图要在读完整 `main.tex` 后重新思考：是否支撑某个必要 claim；如果不支撑，降级到 appendix/status 或删除。

图形发表级标准：

- 每张图只服务一个 claim，caption 自洽。
- 图内短标签，不用长文件名、snake_case、内部状态词。
- 禁用 UI dashboard/card-heavy 风格；使用白底或极浅灰底、细线、统一字号、色盲友好颜色。
- 真实 mesh/GLB render inset 必须清楚；不使用 point cloud / matplotlib scatter 作为方法图证据。
- 先出可编辑 SVG/PDF/PNG，再做 contact sheet 和审稿式自评。
- 最终主文图优先级：
  1. Trellis2 substrate preliminary figure；
  2. PS-RSLG main method overview；
  3. Projection/admissibility gate；
  4. Masked local naturalization mechanism；
  5. Operator admission / transform screening if正文需要；
  6. Classical coverage 图仅在能压缩清楚时进入主文，否则保留 appendix。

首轮任务：

1. 从官方 OpenAI 对话历史提取图形审美/结构建议。
2. 审阅现有 `method_diagram_drafts_contact_sheet.png` 和每张 SVG/PDF。
3. 写 `docs/figures/method_diagram_publication_revision_plan_zh_20260510.md`，明确每张图的去留和改法。
4. 重做至少 Figure B preliminary substrate 和 Figure A main method overview，确保它们不是草稿级。
5. 修改 `paper_siga/main.tex`：Preliminaries 加 Trellis2 substrate 图；Method overview 替换为新 PS-RSLG 图；旧图进入 appendix 或保留但不作为主图。

当前继续任务（2026-05-10 18:25 CST）：

1. 已完成 Figure B / Figure A publication 版并插入正文，`paper_siga` 编译通过，Overleaf 已持平。
2. 正在完成 Figure C：projection/admissibility gate。放置在 `Model-Native Projection` 中 projection argmin 之后、`Why final-only cleanup is insufficient` 之前。
3. Figure C 必须表达 conservative prune-only active-state policy：root-attached support 保持 active；detached/orphan support 被删除或降为 inactive descriptor；certified connector mask 只是 optional rule-proposed path，不是默认 mesh repair。
4. Figure C 输出目标：`paper_siga/figures/method_projection_admissibility_gate_20260510.{pdf,png,svg}`，并同步 draft contact sheet。
5. 插入正文后必须删除对应 `\ExpFigTODO`，保留或更新实验 TODO 为 projection variants/handle metrics，避免把机制图误写成闭合实验。

实验线下一步（只读 reviewer 建议，待 Figure C 完成后执行）：

1. Masked naturalization：先本地闭合三 seed 聚合（`20260510/20260511/20260512`），形成 mean/std、win rate、failure flags；补 weak-N/global-N 同相机 zoom。当前单 seed 三任务可写窄结论：per-depth masked local-N 在投影下改善局部表面连续性，LCR=1.0，silhouette/locality 约 0.905--0.926。
2. V23 baseline 主文候选先锁四个：`V23_dla_coral_cluster_900_staghorn_frontier`、`V23_lsys_pine_canopy_d5_multi_root_smooth_needles`、`V23_ifs_fractal_lattice_d4_pyrite_copy_bridges`、`V23_sc_tree_crown_260_attractor_leaf_shell`。SC tree crown 最弱，优先补 2--3 个候选或用 bush shell 兜底并明确口径。
3. Transform/V21/V23：写成 operator admission/screening，不写 IFS 全胜。pyrite/lattice、radial、bismuth/stepped 是 screened/caveated positive；branch-tree 与 axis-mismatch 是 boundary/negative control。优先指标为 orbit/axis contract、copy-contact survival、surface connectivity、projection-readable handles。

## 5. 主线程责任

1. 维护本计划和 progress log。
2. 控制远端 SSH shell 数量和 GPU 4/5/6/7。

## 6. 2026-05-10 19:06 CST 方法图续推进 checkpoint

当前接手目标：继续完善 `[R-SLG]示意图` 相关方法图，达到可进入 SIGGRAPH/TOG 正文的严谨图形口径，而不是继续堆 dashboard 式草稿。

已确认额外上下文：

- 官方 OpenAI Codex 历史已定位：`/Users/fanta/.codex/sessions/2026/05/09/rollout-2026-05-09T22-18-20-019e0d1a-7c55-70a1-aa1a-64cf832fcaa4.jsonl`，标题 `[R-SLG]示意图`。
- 必读图形文档已读：`docs/figures/method_diagram_design_plan_zh_20260510.md`、`docs/figures/method_diagram_publication_revision_plan_zh_20260510.md`、AgentDoc method figures plan。
- 已复用 6 个既有只读 subagent 输出。共识：A/B/C 可进正文；masked local naturalization 只能以纯机制图进入 Method，不能把 evidence crop、`wins 3/3 seeds`、normal delta 等结果 claim 写在方法图里；D/G/F 暂不进主文，除非正文 claim 和真实素材闭合。

本 checkpoint 已确认：

1. 保留并继续使用三张正文主方法图：
   - `paper_siga/figures/method_trellis2_substrate_prelim_20260510.pdf`
   - `paper_siga/figures/method_ps_rslg_overview_publication_20260510.pdf`
   - `paper_siga/figures/method_projection_admissibility_gate_20260510.pdf`
2. 新增正文机制图：
   - `paper_siga/figures/method_masked_local_naturalization_mechanism_20260510.pdf`
   - 旧 `method_masked_local_naturalization_20260510.*` 保留为内部/补充候选，不进入正文。
3. 机制图只表达：rule scaffold fixes anchors/mask -> frozen local prior changes masked tokens -> projection selects active state -> re-encode；明确 masked naturalization 是 local realization，不是 topology repair 或 operator-admission shortcut。
4. `paper_siga/main.tex` 当前已包含：
   - 在 `Masked Local Naturalization` 小节插入 `fig:method-masked-naturalization`。
   - 将 algorithm 第 364 行长 comment 从四类 gate 缩短为 `admission gates`，避免 ACM 单栏 algorithm overfull。

当前继续执行项：

- 精修 `scripts/figures/compose_method_publication_diagrams_20260510.py`，重新生成 A/B/C/E 四张主方法图及 contact sheet。
- A 图右侧从 “selected exports” 改为 “finite-depth visual anchors”，避免像结果主图；中间 loop 保持最大，projection 在 loop 内最醒目。
- B 图标题和节点改成 Trellis2 preliminary / reusable sparse substrate，明确 projection 不属于 frozen Trellis2 pipeline。
- C 图统一符号到 `z_{d+1}=(\mathcal V,\mathbf F,\mathcal A)`，右侧 inset 避免文字重叠；connector 只写 optional/certified path。
- E 图继续保持 mechanism-only，不写 seed win、normal delta 或 metric number；正文量化段落只作为 closed ablation 摘要存在。

待本 checkpoint 完成前必须做：

- `paper_siga` 运行 `git diff --check`。
- 使用 TinyTeX/latexmk 编译 `main.tex`。
- 检查 undefined refs/cites/control sequence/fatal errors。
- 只 stage 正文实际引用的 PDF 和 `main.tex`，commit 并 push 到 Overleaf。

后续图形优先级：

1. 若继续改图，先重审 A/B/C/E 在编译后 PDF 中的实际浮动位置，尤其避免 Preliminaries/Method 开头连续 `figure*` 过度拥堵。
2. D operator scheduling 图和 G classical coverage 图只有在正文能承接 claim 时再进入；否则保留 supplement。
3. 对 masked naturalization 结果图，等完整 sampling schedule / mask rule / protocol 表闭合后，再考虑把 evidence 版图放入实验或补充。
4. 审核 worker 改动，避免文件冲突。
5. 启动远端大批次并拉回结果。
6. 跑统一 metrics、Blender white-background camera zoom、contact sheets。
7. 集成论文，强制编译，push Overleaf。
8. 每个阶段向用户汇报真实状态和剩余缺口。

## 6. 远端运行规则

每次远端启动前检查：

```bash
ssh a100-2 'cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 && \
printf "DU=" && du -sh . | cut -f1 && \
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | sed -n "5,8p"'
```

远端 batch 要求：

- 只用 GPU `4,5,6,7`。
- `TMPDIR`, `TORCH_HOME`, `HF_HOME`, `TRITON_CACHE_DIR`, `XDG_CACHE_HOME`, `MPLCONFIGDIR` 必须在项目目录。
- 结果目录统一：`results/<RUN>`，输入目录：`inputs/<INPUT_NAME>`，日志目录：`logs/<RUN>`。
- 存储超过 180G 时暂停新 batch，先整理/只拉取必要产物；低于 180G 仍应定期清理明确不用的重复/失败/低分辨率 competing runs 和缓存残留。
- 不启动重复低分辨率 competing run，除非显式命名为 diagnostic。

## 7. 论文修改规则

每次改 `paper_siga/main.tex` 后必须：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga
git diff --check
/Users/fanta/Library/TinyTeX/bin/universal-darwin/latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex
grep -c "LaTeX Warning.*undefined" main.log
grep -c "Citation.*undefined" main.log
```

只有编译通过、undefined refs/cites 为 0，才允许 commit/push：

```bash
git push overleaf main:master
```

## 8. Progress log

- 2026-05-10 18:00 CST：创建本 publication-grade Ralph loop 计划；创建 heartbeat `r-slg-publication-ralph-loop`；并行派发 Singer(masked naturalization)、Goodall(transform story)、Ampere(baseline generation) 三个 worker。当前远端上一轮检查 V21=7/7、V22=8/8、项目目录约 78G、GPU 4/5/6/7 空闲。
- 2026-05-10 18:15 CST：用户追加 method figure 发表级任务。已将图形任务并入本计划，并把 Trellis2 substrate preliminary figure + PS-RSLG main method overview 设为主文图优先级。已确认官方 OpenAI Codex 历史候选 `[R-SLG]示意图` session id `019e0d1a-7c55-70a1-aa1a-64cf832fcaa4`，路径 `/Users/fanta/.codex/sessions/2026/05/09/rollout-2026-05-09T22-18-20-019e0d1a-7c55-70a1-aa1a-64cf832fcaa4.jsonl`；还在筛最近非中转站画图记录。
- 2026-05-10 18:05 CST：用户将远端存储上限放宽到 `200GB`，但要求仍注意清理不用的东西。本计划已同步：新 batch 可使用更大 selection budget，但清理策略保留。

- 2026-05-10 15:58 CST：三条 worker 已完成并由主线程复核。Singer 将 masked local naturalization 扩为三任务六列同根协议，masked local-N mean score `0.8771`，高于 no-N `0.7854`、weak `0.8462`、global-N `0.8180`，三任务 locality delta vs global-N 均为正。Goodall 已把 transform 写成 grammar operator screening/admission 故事，`main.tex` 编译通过、undefined refs/cites 为 0，并已 commit/push Overleaf：`2ac6eba Add transform operator screening story`。Ampere 完成 V23 all-family strict matched batch，本地 dry-run 16 cases、min OBJ LCR `1.0`、tests/py_compile/bash -n 通过；主线程已在 `a100-2` GPU 4/5/6/7 启动并完成远端 Trellis2 GLB/PBR 生成，16/16 summaries ok。V23 surface metrics：r1/r2 全部单连通，r0 min LCR `0.99923`，r0 单连通强候选包括 DLA coral/crystal/frontier sheet、IFS radial、L-system dense root fan、SC tree crown。V5c 结果已拉回并完成 surface metrics；正在做纯白底多级相机 zoom 和后处理 callout。远端目录仍约 `79G`，低于 `200GB` 上限。

- 2026-05-10 16:02 CST：补充校准：上一条记录中的 15:58 CST 为本地实际检查时间；本轮关键状态不变。V23 selected-8 zoom manifest 已生成：`results/strict_visual_matched_texture_V23_all_family_20260510_remote/V23_zoom_manifest_selected8_glb_localplan.json`，候选包括 pine、dense root fan、SC crown、DLA coral/frontier/crystal、pyrite lattice、radial。V5c corrected local-plan Blender render 继续执行中，后处理将由 `scripts/figures/postprocess_matched_camera_zoom_plan_20260510.py` 在系统 Python 下补 callout/contact sheet。

- 2026-05-10 16:04 CST：为满足多 seed/root selection pool，主线程启动第二批 `V23_all_family_seed20260511_20260510`，仍只用 GPU 4/5/6/7，目标是再生成 16 个同协议 strict matched Trellis2 GLB/PBR 候选供最终人工挑图；该批不替代第一批指标结论。第一批 V23 初筛表已写入 `results/strict_visual_matched_texture_V23_all_family_20260510_remote/V23_surface_metric_screening_summary_zh_20260510.md`。

- 2026-05-10 16:07 CST：第二批 V23 seed sweep `strict_visual_matched_texture_V23_all_family_seed20260511_20260510` 已远端完成 16/16 并拉回本地；远端总目录仍约 `79G`，四张卡空闲。V5c corrected local-plan 白底相机 zoom 渲染完成 8/8，并已用系统 Python 后处理生成 overview/zoom callout、每 case comparison sheet 和总 contact sheet：`visuals/strict_visual_matched_texture_v5c_detail_seed20265110_zoom_20260510/strict_visual_matched_texture_v5c_detail_seed20265110_contact_sheet_20260510.png`。

- 2026-05-10 16:42 CST：接手后完成当前轮收尾校准。已复用三个本地 subagent：Hooke 负责论文接入、Laplace 负责 V23 第二 seed 指标摘要、Gauss 负责候选选择汇总。第二 seed `surface_metrics_occ64.csv` 确认为完整 16 rows，新增/更新 `results/strict_visual_matched_texture_V23_all_family_seed20260511_20260510_remote/V23_surface_metric_screening_summary_zh_20260510.md` 和 `results/strict_visual_matched_texture_V23_all_family_seed_comparison_20260510.csv`。跨 seed 推荐主文候选为：L-system `pine_canopy`/`root_fan`，Space colonization `tree_crown`/`root_network`，DLA/frontier `staghorn_frontier`/`frontier_sheet`，IFS/transform `radial_ornament`/`pyrite_lattice`；详见 `docs/evaluation/baseline_candidate_selection_zh_20260510.md`。Masked local naturalization 已接入 `paper_siga/main.tex` 和 `drafts/masked_naturalization_ablation_table_20260510.tex`，六列协议 mean score 为 masked local-N `0.8771`、weak `0.8462`、global-N `0.8180`、no-N `0.7854`、final-only `0.7519`、rule-only `0.4414`。主文中的内部中文写作计划和可见 TODO 已默认隐藏，`latexmk -g -pdf` 通过，undefined refs/cites 均为 `0`，PDF 为 43 页。发现 V23 selected-8 渲染脚本实际渲染路径未使用 `plan_mesh` 选 zoom target，已修 `scripts/figures/matched_camera_zoom_render_20260510.py` 并用 `--plan-only` 验证 target_source 全部为 `plan_mesh`；当前正在输出 `visuals/strict_visual_matched_texture_V23_all_family_selected8_zoom_localplan_fixed_20260510` 的快速白底 zoom QA 渲染，完成后需系统 Python 后处理 callout/contact sheet 并决定是否以 Cycles 高质量重渲染。Heartbeat `r-slg-publication-ralph-loop` 已重新绑定当前线程。

- 2026-05-10 17:02 CST：本轮继续推进并修正 V23 zoom target。确认 `plan_mesh` 与 GLB 坐标存在错位，弃用 `selected8_zoom_localplan_fixed`；改用 `--target-source render` 以实际 GLB vertices 选择 zoom target，完成 8/8 render-target 白底相机 zoom、系统 Python 后处理 callout/contact sheet 和像素 QA。可用图：`visuals/strict_visual_matched_texture_V23_all_family_selected8_zoom_render_target_20260510/strict_visual_matched_texture_V23_all_family_selected8_render_target_contact_sheet_20260510.png`，已复制进 `paper_siga/figures/strict_visual_matched_texture_V23_all_family_selected8_render_target_contact_sheet_20260510.png` 并作为 appendix/status 图接入 `main.tex`。论文 `latexmk -g -pdf` 通过，undefined refs/cites/undefined control sequence 均为 `0`，PDF 为 44 页；commit `bc4ee1c Add V23 all-family zoom status figure` 已推送 Overleaf `main:master` 成功。

- 2026-05-10 17:04 CST：第三个 V23 seed `strict_visual_matched_texture_V23_all_family_seed20260512_20260510` 已在 `a100-2` GPU 4/5/6/7 完成 16/16 summaries ok，远端目录仍约 `79G`，四卡空闲；结果和 inputs 已拉回本地。第三 seed surface metrics 已写入 `results/strict_visual_matched_texture_V23_all_family_seed20260512_20260510_remote/surface_metrics_occ64.{csv,json}`。三 seed 汇总表已生成：`results/strict_visual_matched_texture_V23_all_family_seed3_comparison_20260510.csv` 与 `results/strict_visual_matched_texture_V23_all_family_seed3_rows_20260510.csv`。三 seed结构稳定结论：DLA `staghorn_frontier`/`frontier_sheet`/`crystal` 为 `main-stable`；L-system `pine_canopy` 为 `main-stable`，root/vine rows 为 appendix-stable；IFS `radial_ornament` 和 `branch_ornament` 为 `main-stable`，`pyrite_lattice`/branch-tree 为 near-stable；SC `bush_shell` 为 `main-stable`，`tree_crown`/sparse-kill 为 near-stable，root-network 为 appendix-stable。下一步应做 family-specific metric + visual QA 后再决定主文四/八格组合。

- 2026-05-10 17:05 CST：三个本地 subagent 输出已合并为状态文档：Gauss `docs/evaluation/baseline_publication_gap_update_zh_20260510_gauss.md` 指出旧 selected-8 目录缺图、传统 baseline 指定目录为空，并给出 V23 主候选/指标缺口；Hooke `docs/evaluation/masked_naturalization_publication_status_update_zh_20260510_hooke.md` 判定 masked local-N 可作为“局部 surface-continuity under projection”窄主文表+图，但仍缺 seed/root 统计、weak/global-N 同相机图和 handle-level 指标；Laplace `docs/paper/transform_algorithm_story_reviewer_update_zh_20260510_laplace.md` 复核 arXiv:2604.09132 SATO 源码，确认 ACM/acmart 下应使用独立 `algorithm` + `algpseudocode` 浮动体，并建议 transform 写成 grammar operator admission/screening 而非 equivariance claim。

- 2026-05-10 18:45 CST：接手上一轮 handoff 后完成当前轮推进。确认 heartbeat `r-slg-publication-ralph-loop` ACTIVE，20 分钟；AgentDoc 共享克隆存在其它项目脏改动，因此未在共享 AgentDoc 中 pull/rebase，仅更新项目内计划/mirror。远端 seed sweep `strict_visual_matched_texture_V23_all_family_seed20260513_20260510` 已在 `a100-2` GPU 4/5/6/7 完成 16/16 summaries；远端目录约 `80G`，四卡空闲，低于 `200GB` 上限。结果与 inputs 已拉回本地：`visuals/strict_visual_matched_texture_V23_all_family_seed20260513_20260510/` 与 `results/strict_visual_matched_texture_V23_all_family_seed20260513_20260510_remote/inputs/`；surface metrics 已写入 `results/strict_visual_matched_texture_V23_all_family_seed20260513_20260510_remote/surface_metrics_occ64.{csv,json}`。
- 2026-05-10 18:50 CST：修复 `assets/v23_family_specific_metrics_20260510.py` 的内存风险：默认 `--mesh-quality off` 不再加载/拆分 GLB，必要时才用 `--mesh-quality full` 做重 mesh diagnostics；同时纳入 seed20260513。四 seed enhanced family metrics 已生成：`results/strict_visual_matched_texture_V23_all_family_family_metrics_enhanced_20260510/family_specific_enhanced_rows.csv` 为 64 rows、summary 16 cases。四 seed comparison 已生成：`results/strict_visual_matched_texture_V23_all_family_seed4_comparison_20260510.csv`、`results/strict_visual_matched_texture_V23_all_family_seed4_rows_20260510.csv`、`docs/evaluation/strict_visual_matched_V23_all_family_four_seed_summary_zh_20260510.md`。四 seed结构结论：DLA staghorn/frontier/crystal 为 main-stable；IFS radial 为 main-stable，pyrite lattice near-stable 但仍是 strict lattice/pyrite 主文候选；L-system pine canopy near-stable 且主文视觉候选不变；SC tree crown near-stable，SC bush shell main-stable 但一对一语义弱些。
- 2026-05-10 18:55 CST：三条 subagent 二轮输出已合并。Gauss2 写入 `docs/evaluation/baseline_visual_qa_main_appendix_recommendation_zh_20260510_gauss2.md`，推荐主文四 family 最小组合：`V23_lsys_pine_canopy_d5_multi_root_smooth_needles`、`V23_sc_tree_crown_260_attractor_leaf_shell`、`V23_dla_coral_cluster_900_staghorn_frontier`、`V23_ifs_fractal_lattice_d4_pyrite_copy_bridges`，并明确 traditional baselines 不是弱连通 strawman。Hooke2 写入 `docs/evaluation/masked_naturalization_next_experiment_spec_zh_20260510_hooke2.md` 和 `results/masked_naturalization_ablation_20260510/next_experiment_spec_hooke2_20260510/`，给出 M1 三 seed 54 rows、M2 六 protocol zoom 18 rows、M3 handle-state schema 与 exact commands。Laplace2 写入 `docs/paper/transform_algorithm_reviewer_iteration2_zh_20260510_laplace.md`，复核 Algorithm 1 为 ACM-style `algorithm+algpseudocode`，并指出中文内部计划须隐藏。
- 2026-05-10 19:00 CST：论文 `paper_siga/main.tex` 已更新并 push Overleaf。正文新增 Trellis2 substrate preliminary figure 和新版 PS-RSLG main overview figure；transform-copy operator story 保持为 empirical admission/screening，不声称 strict equivariance；branch-tree row 为 boundary/rejected-as-positive，axis-mismatch 为 negative compatibility control；中文内部写作计划重新包入 `\iffalse...\fi`，默认不进入 PDF。已执行 `git diff --check`、`latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex`，编译通过，PDF 46 页，undefined refs/cites/control sequence 均为 0。已 commit/push Overleaf：`122ac46 Refine method and transform screening story`，只提交 `main.tex` 和两张新引用方法图 PDF，未 stage 其它历史 untracked 素材。

- 2026-05-10 18:18 CST：当前线程接手“方法示意图发表级重画”任务。已按 `agentdoc-startup` 读取 AgentDoc 入口与项目 commons；AgentDoc 共享克隆有其它项目脏改，故不在共享 AgentDoc 中 pull/rebase，只在项目文档和论文仓内行动。确认官方 Codex 图形历史路径为 `/Users/fanta/.codex/sessions/2026/05/09/rollout-2026-05-09T22-18-20-019e0d1a-7c55-70a1-aa1a-64cf832fcaa4.jsonl`，标题 `[R-SLG]示意图`；确认 heartbeat `r-slg-publication-ralph-loop-2` ACTIVE，每 20 分钟唤醒。两名只读 subagent 已完成：一个抽取官方画图历史/图计划，一个审阅 `main.tex` 图位。共识是 A/B/C 职责成立但仍偏 dashboard/slide；D/E 可作为机制图候选，但只有在重绘到足够克制后才进主文，G 暂留 supplement。当前改图策略：先精修 `scripts/figures/compose_method_publication_diagrams_20260510.py` 中 A/B/C，降低圆角卡片和 claim 条，统一 `z_d=(V_d,F_d,A_d)`，把 projection 明确画成 conservative prune-only active-state selection；重生成 PDF/PNG/SVG 和 contact sheet 后再决定是否插入 D/E 或仅更新 A/B/C。Overleaf fetch 后 `HEAD...overleaf/master` 为 `0 0`。

- 2026-05-10 18:31 CST：完成 A/B/C 方法图发表级二轮精修并编译验证。脚本 `scripts/figures/compose_method_publication_diagrams_20260510.py` 已把 A/B/C 从 dashboard/slide 风格收敛为更克制的论文机制图：B 图显式保留 condition、O-Voxel、Shape-SLAT、local prior、Dec/Enc、export，并声明 grammar-visible interface；A 图突出 frozen substrate -> recursive transition -> admissibility projection -> next state 的闭环，删去多余 rule-tag/button；C 图标题改为 active-state selection，只保留 root reachability、orphan handle prune/deactivate、budget/renderability 三项 gate，并标出 inactive/deleted 与 optional connector mask 的边界。旧 D/E/F/G contact sheet 已目视复核：D 过抽象、E 缺同根真实 naturalization ablation 素材，暂不进入主文；待真实素材和指标闭合后再重画。`paper_siga` 编译通过：`latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex` 输出 48 页，undefined refs/cites/control sequence/fatal errors 均为 0；剩余为既有 CJK/appendix 大图/ACM image-description 警告。注意：当前 PDF 仍包含中文写作计划 appendix，这是投稿前必须清理或隐藏的高风险项，但非本轮图改动引入。

- 2026-05-10 18:55 CST：继续原任务并确认用户放宽远端存储上限到 `200GB`。远端 V24 第三 seed `strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510` 已在 `a100-2` GPU 4/5/6/7 完成 `15/15` summaries 和 `15/15` GLB，四卡空闲；远端项目约 `90G`。结果已拉回：`visuals/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510/`，inputs 已拉回：`results/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510_remote/inputs/`；第三 seed surface metrics 已写入 `results/strict_visual_matched_texture_V24_priority_rerun_seed20260512_20260510_remote/surface_metrics_occ64.{csv,json}`。新增三 seed 汇总脚本 `assets/scripts/v24_three_seed_stability_summary_20260510.py`，输出 `results/strict_visual_matched_texture_V24_priority_rerun_seed3_rows_20260510.csv`、`results/strict_visual_matched_texture_V24_priority_rerun_seed3_comparison_20260510.csv/json` 和 `docs/evaluation/strict_visual_matched_V24_three_seed_QA_recommendation_zh_20260510.md`。三 seed 结论：SC tree A、DLA staghorn、DLA frontier sheet、IFS radial 为 r0 三次单连通；pyrite lattice 为 transform-copy/lattice 条件主文，r1 三次单连通且 LCR > 0.9997；root fan A 只能作为视觉条件主文，仍需白底 zoom 确认小碎片不可见。当前已启动本地 Blender 渲染 `visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510/`，候选为 SC tree A、DLA staghorn/frontier sheet、IFS radial/pyrite、root fan A/B。

- 2026-05-10 18:56 CST：两个只读 subagent 完成审阅并已收口。Masked 审阅确认 `paper_siga/main.tex` 仍引用旧 masked contact sheet，建议用最新 M2 三任务六协议同相机图替换；M1 三 seed表可进主文，M2 可作视觉 QA 主图，M3 只能作为 metadata+mesh proxy appendix。V24 QA 审阅确认两 seed recommendation 基本正确，但 root fan 应降级为第三 seed + zoom QA 条件主文，pyrite lattice 需 bridge-contact zoom 后再作主文 claim；传统 baseline 不可写成弱 baseline。已修正 `docs/evaluation/masked_naturalization_m2_m3_status_zh_20260510.md` 中 pytest 临时路径为项目稳定路径，并准备将 `visuals/masked_naturalization_m2_m3_20260510/masked_naturalization_m2_contact_sheet_20260510.png` 复制入 `paper_siga/figures/`。

- 2026-05-10 18:59 CST：完成本轮论文和 V24 可视化收口。`paper_siga/main.tex` 已将 masked naturalization 主文图替换为 M2 六协议同相机 contact sheet `figures/masked_naturalization_m2_contact_sheet_20260510.png`，正文补充 M3 仅为 proxy sidecar，不是 runtime handle-graph proof。`latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex` 通过，PDF 48 页，undefined refs/cites/control/fatal 均为 0；commit/push Overleaf 成功：`3cd0051 Update masked naturalization visual ablation`。V24 seed3 本地 Blender/Cycles 白底 zoom 已完成 7 个候选，后处理输出总图 `visuals/strict_visual_matched_texture_V24_priority_rerun_seed3_zoom_white_20260510/strict_visual_matched_texture_V24_priority_rerun_seed3_contact_sheet.png` 和每 case `strict_matched_zoom_comparison.png`。像素 QA 非空；目视 QA 已补入 `docs/evaluation/strict_visual_matched_V24_three_seed_QA_recommendation_zh_20260510.md`：pyrite lattice 和 root fan 视觉强但需 caveat，DLA/frontier 指标强但不写物理仿真，SC tree A 指标强但视觉上需谨慎。

- 2026-05-10 19:16 CST：完成方法图语义和视觉口径收敛并推送 Overleaf。已基于官方 `[R-SLG]示意图` 历史、三份图形计划和 6 个只读 subagent 审稿意见，更新 `scripts/figures/compose_method_publication_diagrams_20260510.py` 并重生成 A/B/C/E 四张方法图 PDF/PNG/SVG。主文提交只包含 4 个已引用 PDF 与 `main.tex` 两处 caption：B 图改为 “Frozen Trellis2-style sparse substrate”；A 图把右侧结果称为 finite-depth visual anchors，明确不是 category-wide claims；C 图强调 active-state selection / prune-deactivate；E 图保持 mechanism-only，不含 seed win/normal delta 等结果化数字。执行 `git diff --check`、`latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex`，PDF 48 页，undefined refs/cites/control/fatal/errors 均为 0；Overleaf push 成功，commit `9dc10b9 Tighten method figure semantics`，`overleaf/master...HEAD = 0 0`。剩余风险：本地 `paper_siga/main.tex` 仍有未提交 V24 traditional-vs-ours figure/table 插入及未跟踪 `figures/traditional_vs_v24_one_to_one_zoom_20260510.png`、`drafts/traditional_vs_v24_one_to_one_summary_20260510.tex`，本次未混入方法图提交；后续需单独审查、编译、提交。既有 CJK/中文写作计划 appendix、appendix 大图 float-too-large、ACM image-description 警告仍是投稿前高风险清理项。

- 2026-05-10 19:13 CST：heartbeat 接手后继续传统 baseline/V24 one-to-one 收口。按 AgentDoc 启动要求读取入口和当前项目计划；共享 AgentDoc 克隆存在大量其它项目脏改且此前曾落后，因此未原地 pull/rebase，仅在项目内 `docs/` 和 `paper_siga/` 行动。已用两个只读 subagent 并行完成：一是定位本机 Codex 历史 `[R-SLG]示意图`，确认方法图口径仍为 Trellis2 frozen substrate、projection 在递归内部、masked naturalization 非全局修复；二是盘点 traditional target 与 V24 seed3 white zoom assets。远端 `a100-2` 检查显示项目约 `90G`，GPU 4/5/6/7 全空闲，低于 `200GB`。新增合成脚本 `scripts/figures/compose_traditional_vs_v24_one_to_one_20260510.py`，生成严格四族 one-to-one 图 `visuals/traditional_vs_v24_one_to_one_zoom_20260510/traditional_vs_v24_one_to_one_zoom_20260510.{png,pdf}` 并复制到 `paper_siga/figures/traditional_vs_v24_one_to_one_zoom_20260510.png`。图像 QA：`2522x1888`，非白像素比例 `0.1255`，输入均为已有 matched-camera zoom comparison。新增论文表 `paper_siga/drafts/traditional_vs_v24_one_to_one_summary_20260510.tex`，正文已接入 Figure/Table。新增状态文档 `docs/evaluation/traditional_vs_v24_one_to_one_figure_status_zh_20260510.md`。下一步：编译 `paper_siga`，若通过则 commit/push Overleaf；若图过大影响版面则降级到 appendix 或缩小为三行主图。

- 2026-05-10 19:45 CST：本轮 heartbeat 继续传统 baseline 发表级推进。V25 root/SC refine 小批量已完成本地工程化：`assets/strict_visual_matched_cases_V25_root_sc_refine_20260510.py` 修正 rootlet scatter，不再从 center vertices 伪造 parent list，而是复用真实 L-system `nodes/parents` graph；新增 launcher `assets/launch_strict_visual_matched_texture_V25_root_sc_refine_20260510.sh`、pytest `tests/test_strict_visual_matched_cases_V25_root_sc_refine_20260510.py`、计划文档 `docs/evaluation/strict_visual_matched_V25_root_sc_refine_plan_zh_20260510.md`。本地 dry-run 8/8，GPU 4/5/6/7 每卡 2 case，pre-export OBJ LCR gate 全通过；`python3 -m py_compile`、`bash -n`、pytest `3 passed`。只读审阅结论：V25 不能直接替换 V24；root 必须把 r0 tiny islands 压到 `components_r0<=1` 才能升级 topology/main-stable，SC 必须保持 V24 SC A 的 r0 单连通并且视觉改善 trunk/cap 才能替换。论文只读审阅结论：masked/transform/coverage/algorithm 主线基本闭合，但投稿硬风险是 `main.tex` appendix 可见中文内部计划和大量源码 TODO；下一轮必须清理。

- 2026-05-10 19:55 CST：V25 root/SC refine 远端完成并本地评估。`a100-2` GPU 4/5/6/7 启动后 8/8 `summary.status=ok`、8/8 `textured.glb`，远端目录仍约 `90G`，四卡空闲。结果拉回 `visuals/strict_visual_matched_texture_V25_root_sc_refine_20260510/`，inputs 拉回 `results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/inputs/`。surface metrics 写入 `results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/surface_metrics_occ64.{csv,json}`，汇总写入 `results/strict_visual_matched_texture_V25_root_sc_refine_comparison_20260510.csv` 与 `docs/evaluation/strict_visual_matched_V25_root_sc_refine_QA_recommendation_zh_20260510.md`。关键结果：`V25_lsys_root_fan_smooth_anchorD_stable` r0=1/LCR=1.0，替换 V24 root caveat；`V25_sc_tree_crown_tapered_B` r0=1/LCR=1.0，保留 SC connectivity floor 但仍只是 tapered visual candidate。已完成两者白底 two-level zoom：`visuals/strict_visual_matched_texture_V25_root_sc_refine_zoom_white_20260510/V25_root_sc_refine_contact_sheet_20260510.png`。已更新 one-to-one 图脚本和 paper_siga 图/表：DLA/IFS 保持 V24，root/SC 使用 V25 selected candidates；同时把 `main.tex` 中可见中文内部计划包入 `\iffalse`，降低投稿硬风险。下一步：编译 `paper_siga`，只 stage 本轮相关图表和 main.tex，push Overleaf。

- 2026-05-10 19:32 CST：继续方法图发表级收敛。两个只读 reviewer 结论已合并：projection gate 最强，Trellis2 prelim 基本可用，masked local naturalization mechanism 小修可用，PS-RSLG overview 信息密度过高需降噪。已更新 `scripts/figures/compose_method_publication_diagrams_20260510.py` 并重生成 A/B/C/E 四张图。关键改动：overview 从“所有模块塞一张图”改成 `(a) frozen Trellis2 substrate / (b) grammar-owned recursive transition / (c) selected asset view` 三块；右侧 visual anchors 从三条 contact/inset 压成单一 selected asset view；删除旋转 `codec round trip` 标签，改为水平 `codec path`；统一符号为 `$V_d$`, `$F_d$`, `$\mathcal{A}_d$`, `$\mathcal{R}_d$`, `$\mathcal{N}_\theta$`, `$\Pi_{\theta,\lambda_d}$`, `$z_{d+1}$`；masked local naturalization 图缩短标题为 `Masked Local Naturalization`，补充 `$m_d$ is the sparse editable mask`，去掉 sampler 内部重复标签，避免缩小后文字打架。最新 QA contact sheet：`paper_siga/figures/method_diagram_drafts_20260510/method_publication_abc_contact_sheet_20260510.png`。下一步只 stage 四张正文引用 PDF，编译 `main.tex` 并 push Overleaf；SVG/PNG/draft contact sheet 保留为本地可编辑/QA 资产，不混入 Overleaf commit。

- 2026-05-10 20:26 CST：heartbeat 接手后先按用户纠正确认：`paper_siga/main.tex` 中中文写作方案/ChinesePlan appendix 是用户刻意保留内容，不再清理、不再覆盖；当前 `paper_siga` tracked diff 为 0，`overleaf/master...HEAD = 0 0`。本轮无远端 GPU 使用。Masked naturalization 完成 M3+ 本地补强：在 `assets/export_masked_naturalization_m2_m3_20260510.py` 中新增 deterministic grammar trace graph sidecar，从 `primitive_trace` 重建几何接触图，输出 `results/masked_naturalization_m2_m3_20260510/m3_trace_graph_sidecar_20260510.{csv,json}`；三任务 masked local-N 的 trace active/frontier reachability 均为 `1.0000`，unsupported active support mass 均为 `0.0000`，handle drift 为 `0.0021/0.0040/0.0034`。状态文档 `docs/evaluation/masked_naturalization_m2_m3_status_zh_20260510.md` 已更新：M3+ 强于旧 proxy，但仍不是 Trellis sparse-latent runtime handle graph，不可写成 watertight/topology/physical proof。新增 strict one-to-one 图像+结构指标同表脚本 `assets/strict_one_to_one_visual_metric_summary_20260510.py`、测试 `tests/test_strict_one_to_one_visual_metric_summary_20260510.py`，输出 `results/traditional_vs_ps_rslg_one_to_one_metrics_20260510/traditional_vs_ps_rslg_one_to_one_metric_rows_20260510.{csv,json}` 和中文摘要。四行展示建议：DLA/staghorn 和 V25 root 为 `main`，V24 pyrite lattice 为 `main-caveated-transform-admission`，V25 SC tapered-B 为 `main-with-visual-caveat`；传统 target 明确是结构控制参照，不是弱 baseline。验证：`python3 -m py_compile assets/export_masked_naturalization_m2_m3_20260510.py`、`python3 -m py_compile assets/strict_one_to_one_visual_metric_summary_20260510.py`、`python3 -m pytest -q tests/test_strict_one_to_one_visual_metric_summary_20260510.py tests/test_masked_naturalization_m2_m3_20260510.py`，结果 `2 passed`。

- 2026-05-10 23:52 CST：继续用户最新要求，明确“中文保留”，未修改/覆盖 `paper_siga/main.tex`。本轮重点转向传统 baseline vs ours 视觉对比与 masked naturalization 接缝问题。两个只读 explorer 结论合并：现有 masked local-N 的 projection/trace 指标成立，但白底 zoom 接缝仍明显，主要来自 junction band 未显式优化、Trellis2 texture/PBR 的 UV/material island、以及 callout/alpha flatten/camera 展示链路放大；因此不能写“最终 PBR GLB 已无接缝”。新增 `assets/masked_naturalization_seam_band_qa_20260510.py` 与测试 `tests/test_masked_naturalization_seam_band_qa_20260510.py`，输出 `results/masked_naturalization_seam_optimization_20260510/masked_naturalization_seam_band_metrics_20260510.{csv,json}`、`visuals/masked_naturalization_seam_optimization_20260510/masked_naturalization_seam_optimization_contact_sheet_20260510.png` 和状态文档 `docs/evaluation/masked_naturalization_seam_optimization_status_zh_20260510.md`。新增 junction-collar 候选保持三任务 LCR `1.0`；coral seam band normal delta `0.516°`、IFS boundary jump delta `0.625°`，root 几何改进接近 0，说明 root 更可能需要材质连续 guide。新增 `assets/prepare_seam_aware_texturing_batch_20260510.py` 与测试 `tests/test_prepare_seam_aware_texturing_batch_20260510.py`，生成 `results/seam_aware_texturing_batch_20260510/`：3 个 junction-collar OBJ + 3 张 seam-aware PBR guide，远端 manifest 分配 GPU 4/5/6，GPU 7 暂留。远端检查：`a100-2` 项目目录约 `94G`，低于 `200GB`，GPU 4/5/6/7 空闲；已同步输入并用 `assets/launch_seam_aware_texturing_20260510.sh` 启动 `seam_aware_texturing_batch_20260510_remote`，GPU4=root、GPU5=coral、GPU6=IFS/crystal，日志位于远端 `logs/seam_aware_texturing_batch_20260510_remote/`。传统 one-to-one 图按用户要求改为 PPTX-first：新增 `scripts/figures/compose_traditional_vs_psrslg_one_to_one_pptx_20260510.{js,py}` 和 Keynote exporter helper，生成 `paper_siga/figures/traditional_vs_psrslg_one_to_one_pptx_20260510/traditional_vs_psrslg_one_to_one_20260510.pptx`、一页主图版 `traditional_vs_psrslg_one_to_one_main_20260510.pptx` 与 PNG preview；Keynote AppleEvent PDF export 在本机超时，已记录为导出器问题，不是 PPTX 排版失败。验证：`python3 -m pytest -q tests/test_prepare_seam_aware_texturing_batch_20260510.py tests/test_masked_naturalization_seam_band_qa_20260510.py` 结果 `2 passed`。

- 2026-05-11 00:52 CST：继续传统 baseline 视觉/PBR 与 masked naturalization seam 优化，仍未修改/覆盖 `paper_siga/main.tex`，保留用户中文内容。回收远端 `seam_aware_texturing_batch_20260510_remote` 三个 GLB，本地 metrics 写入 `results/seam_aware_texturing_batch_20260510_remote/surface_metrics_occ64.{csv,json}`；3/3 在 occ64 下 `r0/r1/r2 components=1`、`LCR=1.0`。白底 zoom 输出 `visuals/seam_aware_texturing_batch_20260510_zoom_white/seam_aware_texturing_contact_sheet_20260510.png`；目视结论：v1 结构干净但 root 有深色环带、coral 有红黄材质岛、IFS 有高对比条纹，不能作为“接缝自然”主文正例。新增 v2 低对比多 guide 批次：`assets/prepare_seam_aware_texturing_batch_v2_20260510.py`、`assets/launch_seam_aware_texturing_v2_20260510.sh`、`tests/test_prepare_seam_aware_texturing_batch_v2_20260510.py`，本地生成 `results/seam_aware_texturing_batch_v2_20260510/`，远端 8/8 在 GPU4/5/6/7 完成并拉回 `results/seam_aware_texturing_batch_v2_20260510_remote/`；8/8 metrics 均为 occ64 `r0/r1/r2 components=1`、`LCR=1.0`，fast zoom 为 `visuals/seam_aware_texturing_batch_v2_20260510_zoom_white_fast/seam_aware_texturing_v2_contact_sheet_20260510.png`，并新增 true-white flatten 脚本 `scripts/figures/flatten_zoom_raw_to_white_20260510.py`，输出 `*_white.png` 避免透明黑底污染 QA。v2 视觉筛选：root `S01a` 比 v1 好，coral 仍有大块材质岛，IFS `S03a` 干净但过于平滑/陶土感。新增 object-space procedural PBR 路线 `scripts/figures/seam_aware_procedural_pbr_render_20260511.py`，固定已通过 LCR 的 geometry，在物体坐标中生成连续 PBR，避免 UV 分岛；输出 `visuals/seam_aware_procedural_pbr_20260511_zoom_white/seam_aware_procedural_pbr_contact_sheet_20260511.png`。当前最佳视觉：`S02c_coral_procedural_ivory_pbr` 接缝最自然，`S03a_pyrite_procedural_facets_pbr` 最适合 transform/lattice PBR 展示，`S01a_root_procedural_bark_pbr` seam 自然但植物 bark 感不足。新增 PPTX-first seam QA deck：`paper_siga/figures/seam_aware_pbr_qa_pptx_20260511/seam_aware_pbr_qa_20260511.pptx`，尚未导出 PDF，尚未接入论文。Keynote 自动导出脚本 `scripts/figures/export_pptx_with_keynote_20260510.py` 已加 `with timeout of 1800 seconds` 和 summary 输出，但本机 Keynote AppleEvent 仍长时间卡住，已终止后台 osascript；当前进入论文的 PPTX 图仍需要手动 Keynote 导出 PDF 或在装有 LibreOffice 的机器上转换。远端项目约 `95G`，GPU 4/5/6/7 空闲，低于 `200GB`。
