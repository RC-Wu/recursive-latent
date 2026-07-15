# Recursive 3D Growth 主实验收束 Ralph Loop 计划

更新时间：2026-05-11 CST  
状态：active / main-experiment convergence / 2026-05-11 latest user-update integrated  
本地项目根：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth`  
论文根：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga`  
远端：`a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
远端 GPU 限制：最多同时使用 2 张卡，只能从 `4/5/6/7` 里挑空闲卡。  
远端存储上限：`200GB`，当前约 `134GB`；清理只清明确失败/重复/低价值缓存，不动可复现证据。  
重要写作约束：不要覆盖 `paper_siga/main.tex` 中用户刻意保留的中文；任何正文修改前先读当前文件并局部 patch。  

## 0. 新任务总目标

把核心实验主线从“继续无边界追一个树冠 case”收束为一组可进入论文主实验的严格可比 case：

1. **Space colonization / tree crown**：汇总 V26--V33，保留用户认可的 V29 上色版本，同时纳入 V32 leafmass/canopy 视觉更强候选；最终按“主视觉读感、严格匹配、post-GLB metrics caveat”分层进入主视觉比较。
2. **L-system / branch-with-side-branches**：这是当前最弱主线。按照树冠接缝优化经验做新的 L-system 树枝 naturalization 迭代，目标是发表级：自然树枝、分支连接无硬接缝、无低模 token、无明显体素/管道感。
3. **IFS / pyrite crystal**：使用当前头图中质量较好的黄铁矿晶体 case；定位对应 GLB、metrics 和白底渲染源。
4. **DLA / coral**：从 figure17 或已有 DLA/coral 远端批次中找一个与头图不同、视觉不体素化的候选；若现有候选不够，换 root/grammar/guide 重新生成。
5. **主实验指标**：对 DLA + SC + L-system + IFS 做同协议量化，包括 connectivity、mesh quality、visual/render diagnostics、runtime/export、family-specific metrics；GPT/user study 留空待用户补。
6. **fig35/fig36 depth/density 控制图**：找到 B/C/D 三行对应 GLB，纯白背景重新渲染，每张子图都有 zoom-in，再以子图形式加入 TeX。
7. **正文核心实验节**：基于最终视觉和指标重写/完善主干对比实验讨论，清楚展示优势和 claim boundary。

## 0.1 2026-05-11 最新用户更新后的收束口径

- **树冠 case 已进入收束阶段**：用户认为 `V29` 上色 case 质量已经不错；本轮不再无止境追树冠新版本，而是汇总过去六七个版本，选视觉效果最好的进入主视觉比较。当前优先候选仍是 `V29_sc_tree_softleaf_entry_D` 与 `V32_sc_tree_leafmass_shell_B`，最终按视觉主候选/指标备份分层展示。
- **L-system branch-with-side-branches 是当前 P0**：根据 `docs/evaluation/strict_visual_matched_V24_three_seed_QA_recommendation_zh_20260510.md` 和用户反馈，传统 L-system 对比中“树枝上长分支”的自然度、视觉质量、非接缝感远未达标。必须复用树冠 naturalization 经验继续迭代，直到白底 overview + zoom 中不再像插接管、断面管或低模 token。
- **V34 仅作为失败诊断/起点**：V34 dry-run 全部 pre-export 连通，但 OBJ contact sheet 显示主枝末端仍有截断大管，zoom target 不稳定且部分 zoom 空白；因此 V34 不应直接作为远端主候选。下一轮应做 V35/V36：更强 terminal taper、主轴端部闭合 bud/cap、junction-target zoom 修正、降低圆管和切面读感。
- **IFS pyrite 使用头图认可 HQ case**：优先使用 `visuals/connected_scaffold_v2_textured_glb_hq_20260509/pyrite_lattice_pyrite_hq_steps8_tex2048_xformers/textured.glb`，同时保留 V24 pyrite lattice 作为 strict transform-copy 指标/条件主文证据。
- **DLA coral 使用与头图不同的候选**：优先从 V24 staghorn/frontier、V20/V11/V13/V14/V18 等已有批次中选最不体素化、白底 zoom 最稳定的非头图 case；如不够，再两卡小批量重跑。
- **fig35/fig36 重做为纯白 zoom 子图**：B/C/D 三行涉及的 GLB 都要用统一纯白背景重渲，每个子图带 zoom-in 和远景矩形框，TeX 中以子图形式组织，避免把旧混合背景图直接进主文。
- **指标与正文同步收束**：四类主实验 case（DLA + SC + L-system + IFS）必须同步生成 connectivity、mesh quality、visual/render diagnostics、family-specific metrics；GPT/user study 留空给用户后补。正文只在证据闭环后局部 patch，保留用户刻意留下的中文。

## 1. 不可漂移口径

- 本轮不继续把 V33 自动推远端；先完成 V26--V33 树冠证据汇总。当前 SC 位采用三层候选口径：`V32_sc_tree_leafmass_shell_B` 为视觉主候选，`V29_sc_tree_softleaf_entry_D` 为用户认可/上色候选，V26/V28 为指标稳定备份。
- L-system 树枝 case 不能继续使用 V24 中“不自然、接缝重、树枝管感明显”的候选作为主文正例；必须新迭代。
- 图像生成模型可以作为 whole-object low-contrast guide / reference source；当前没有闭合的 `2D seam SDEdit/inpaint -> UV/3D/GLB 回投` pipeline，不能写成已完成的局部 2D seam 修复。
- 所有主视觉渲染必须是 mesh/GLB/PBR 或 neutral mesh Blender render，纯白背景、正方形、多级 camera zoom；远景中必须用矩形框标注近景区域。
- 传统 baseline 不是 strawman；正文写 controlled family target/comparison，不写传统方法天然失败。
- Textured GLB/PBR 是 asset-readiness 和视觉证据，不替代 topology 证明。

## 2. 当前已知关键线索

### 2.1 树冠 V26--V33

- V29 用户认可“上完色质量已经还不错”，需要优先找远端 GLB、metrics 和白底 zoom。
- 2026-05-11 只读审计的新结论：`V32_sc_tree_leafmass_shell_B` 冠层 mass / veil 语义更强，最像当前主视觉正例；但 post-GLB r0 为 12 comps、LCR `0.993491`，只能写成视觉主候选/条件主文，不写成拓扑主稳。
- `V32_sc_tree_balanced_canopy_D` 是次选视觉候选，r0 9 comps、LCR `0.991607`。
- `V29_sc_tree_softleaf_entry_D` 仍是用户明确认可的上色候选，r0 5 comps、LCR `0.995661`，作为收束候选必须进入对照 sheet。
- V30 指标强于 V29，但视觉仍像稀疏枝架。
- V31 pre-GLB 指标更稳，但 OBJ 仍裸 tube skeleton，没有上远端。
- V32 remote 完成，post-GLB r0 LCR 约 `0.9839--0.9935`，视觉有 leaf-mass 遮挡但小岛/材质岛仍明显。
- V33 本地已修正为 fused-lobe 口径，pytest 通过、dry-run 通过、OBJ sheet 已生成；但是否超过 V29 要由视觉 QA 决定。

### 2.2 V24 QA 对 L-system 的警告

文档：`docs/evaluation/strict_visual_matched_V24_three_seed_QA_recommendation_zh_20260510.md`

- `V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA` 只适合 root visual 条件主文，并且有 connectivity caveat。
- 用户本轮明确指出“树枝上长分支”的 L-system 对比 case 自然程度、视觉效果、非接缝感远远不行；因此要针对 **branch with side branches**，而不是 root fan，重新迭代。

### 2.3 可疑/候选资产池

需要继续定位：

- 头图/teaser：
  - `paper_siga/figures/teaser_candidate_layout_v3_20260509.png`
  - `paper_siga/figures/teaser_candidate_4panel_mesh_pbr_20260509.png`
  - `paper_siga/figures/head_figure_draft_4cat_20260508.png`
  - `paper_siga/figures/head_figure_textured_non_tree_draft_20260508.png`
- Pyrite/IFS：
  - `visuals/pyrite_depth_hq_warm_showcase_20260509/stage*_textured.glb`
  - `visuals/pyrite_depth_textured_showcase_20260509*/pyrite_lattice_depth_stage_*_pyrite*_xformers/textured.glb`
  - V24 pyrite 条件主文路径见 V24 QA 文档。
- DLA/coral：
  - `visuals/strict_visual_matched_texture_v8_frontier_refine_seed*/.../textured.glb`
  - `visuals/strict_visual_matched_texture_v9_organic_frontier*/.../textured.glb`
  - `visuals/strict_visual_matched_texture_V20_paper_coral_crystal*/.../textured.glb`
  - `visuals/coral_depth_textured_showcase_20260509*/.../textured.glb`
  - `results/publication_hunyuan_text_root_meshspace_20260511/coral_branch_root/*_white_pbr.glb`
- Fig35/Fig36 depth/density：
  - `visuals/coral_depth_textured_showcase_20260509*/`
  - `visuals/bismuth_depth_textured_showcase_20260509*/`
  - `visuals/pyrite_depth_textured_showcase_20260509*/`
  - `visuals/coral_density_param_texture_20260509*/`
  - `visuals/coral_density_extreme_texture_20260509/`

## 3. 执行任务清单

### Task A：树冠主文候选收束

输出：

- `docs/evaluation/sc_tree_crown_V26_V33_selection_for_main_zh_20260511.md`
- 一个统一白底 contact sheet：`visuals/main_experiment_case_selection_20260511/sc_tree_crown_V26_V33_selection_contact.png`
- 推荐候选路径清单：GLB、metrics CSV、zoom 图、manifest。

步骤：

1. 收集 V26--V33 的 GLB、metrics、OBJ/GLB zoom、文档 verdict。
2. 当前候选必须至少包含：
   - `V32_sc_tree_leafmass_shell_B`：视觉主候选；记录 r0 12 comps / LCR `0.993491` caveat。
   - `V32_sc_tree_balanced_canopy_D`：视觉次选；记录 r0 9 comps / LCR `0.991607` caveat。
   - `V29_sc_tree_softleaf_entry_D`：用户认可上色候选；记录 r0 5 comps / LCR `0.995661` caveat。
   - `V26_sc_tree_crown_leafshield_B_lowcontrast` 或 `V26_sc_tree_crown_soft_canopy_D_lowcontrast`：r0 单连通/LCR 1.0 metric backup。
   - `V28_sc_tree_multiscale_canopy_C` 或 `V28_sc_tree_branch_flare_A`：r0 单连通/LCR 1.0，但视觉长杆/材质突变 boundary。
3. 对 V29/V32/V26/V28 做统一白底 overview + 2-level zoom；不要把已有白底图直接当最终排版图，最终需要按同相机和同背景重新生成。
4. 视觉 QA 排序：无长杆、无硬接缝、无小岛/材质岛、冠层读感、与 SC baseline strict match。
5. 指标兜底：`components_r0/r1/r2`、`LCR`、mesh import/render success、surface area、GLB size。
6. 选主文 SC 候选时必须同时给出 caption caveat：视觉主候选不等于拓扑最稳；Textured GLB 是 asset-readiness 证据。

### Task B：L-system branch naturalization 新迭代

输出：

- 新 generator：`assets/strict_visual_matched_cases_V34_lsystem_branch_naturalization_20260511.py`
- 新 launcher：`assets/launch_strict_visual_matched_texture_V34_lsystem_branch_naturalization_20260511.sh`
- 新测试：`tests/test_strict_visual_matched_cases_V34_lsystem_branch_naturalization_20260511.py`
- 本地 dry-run：`results/strict_visual_matched_cases_V34_lsystem_branch_naturalization_20260511_dryrun`
- 本地 OBJ 白底 zoom：`visuals/strict_visual_matched_cases_V34_lsystem_branch_obj_zoom_20260511/`
- 远端 GLB 批次：最多两张卡，例如 GPU 4/5。

设计方向：

- strict target：传统 L-system “branch with side branches”，不是 root fan；保留递归分支深度和侧枝分布。
- 当前任务 P0：用户明确指出 V24/strict QA 中“树枝上长分支”的 L-system 视觉、自然度和非接缝感远远不行；这一路必须用树冠迭代得到的 hidden hub、junction mask、fused collar、ridge、bud、low-contrast whole-object guide 方法重新做。
- 图像生成模型只能作为 whole-object guide 或参考图；没有 2D seam inpaint 回投闭环前，不得把它写成局部 seam 修复方法。
- 从树冠线迁移有效策略：
  - hidden/short hub：把低层笔直主杆拆成短段、多入口、轻微弯曲。
  - junction mask：每个侧枝连接处生成 object-space junction band。
  - fused lobe / bark collar：用少量厚的 transition lobes、bark collar、ridge 和 bud 覆盖硬接缝。
  - terminal cap naturalization：端部用 compact bud/leaf sheath，避免切面。
  - support visibility：外层细枝可以轻微降权，但不能失去 L-system 递归读感。
- 远端每轮最多 2 cases；先 4 个本地候选，选 2 个上远端；失败后迭代 V35/V36。
- 验收门槛：
  - pre-export `mesh_component_count=1`, `LCR>=0.999`。
  - post-GLB preferred `r0 LCR>=0.999`，至少 `r1 LCR=1.0`。
  - 白底 zoom 中侧枝 junction 无明显插接、无低模 token、无体素块、无孤立小叶岛。

### Task C：IFS pyrite 和 DLA coral 定稿

输出：

- `docs/evaluation/main_experiment_ifs_dla_case_selection_zh_20260511.md`
- `visuals/main_experiment_case_selection_20260511/ifs_dla_candidate_contact.png`
- 最终 GLB 路径和 metrics 路径。

步骤：

1. 定位头图中 pyrite crystal 对应 GLB，优先复用用户认可的 case。当前强线索为 `visuals/connected_scaffold_v2_textured_glb_hq_20260509/pyrite_lattice_pyrite_hq_steps8_tex2048_xformers/textured.glb`。
2. 从 V8/V9/V20/figure17/已有 depth showcase 中找非头图 DLA/coral 候选。
3. 对候选统一白底 overview + 2-level zoom，排除体素化/块状/管状/过度晶体化样例。
4. 若 DLA 候选不够，设计一个两卡远端 V34/V35 DLA small rerun：implicit smooth coral / frontier attachment / no voxel blocks / attached porous polyps。
5. 记录最终四类主实验 case：DLA、SC、L-system、IFS。

### Task D：fig35/fig36 depth/density 控制图重做

输出：

- `paper_siga/figures/depth_density_control_white_zoom_20260511/` 下的 PNG/PDF 子图。
- TeX 片段草稿：`paper_siga/drafts/depth_density_control_subfigures_20260511.tex`。
- 状态文档：`docs/figures/depth_density_control_white_zoom_plan_zh_20260511.md`。

步骤：

1. 在 `main.tex` 中定位 fig35/fig36 当前引用与 caption；不要覆盖中文。
2. 找到 B/C/D 三行对应 GLB 源。
3. 用统一白底、正方形、overview+zoom、callout 框重新渲染。
4. 每个 GLB/mesh 都生成 overview、zoom_01、zoom_02 和带矩形框 overview_callouts；近景区域必须能在远景中用矩形框对应。
5. 每行子图以 `subfigure` 或 `minipage` 形式排版；避免把长文件名放进图中。
6. 编译 paper_siga，检查 fatal error、undefined refs/cites、overfull hbox。

### Task E：主实验指标与正文

输出：

- 指标脚本/汇总表：`results/main_experiment_case_metrics_20260511/`
- 论文表格：`paper_siga/figures/main_experiment_case_metrics_20260511.tex`
- 实验讨论草稿文档：`docs/paper/main_experiment_section_revision_notes_zh_20260511.md`
- 最终局部修改 `paper_siga/main.tex`。

指标集合：

- Connectivity/topology：surface voxel components/LCR r0/r1/r2、root-attached ratio、orphan mass、path-to-root rate。
- Mesh quality：face/vertex count、raw/welded components、non-manifold edges、boundary edges、degenerate faces、normal consistency、triangle aspect ratio、Laplacian roughness、blockiness。
- Visual/render：GLB import success、render non-white pixel ratio、多视角 white render success、texture/PBR channel status、GLB size。
- Family-specific：
  - L-system：branch depth、junction count、branch angle distribution、terminal survival、junction collar coverage。
  - SC：attractor coverage、alive attractors、entry hub/branch seam diagnostics。
  - DLA：frontier survival、porosity、tip/neck count、blockiness。
  - IFS：orbit/symmetry IoU、copy-contact survival、lattice beam continuity。
- Semantic/visual learned metrics：CLIP/DINO optional secondary；GPT/user study 留空。

正文口径：

- 核心 claim：我们在严格 matched family targets 下，把程序递归结构、局部 naturalization、投影稳定性和 textured GLB export 组合成可发表资产证据。
- 不 claim：万能 grammar、物理 DLA/coral simulation、strict equivariance、2D seam inpaint 回投。

## 4. 远端执行规则

- 每次远端启动前检查：
  - `du -sh /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
  - `nvidia-smi` 的 GPU 4/5/6/7 状态。
- 同时最多使用 2 张 GPU。
- 所有 launcher 必须设置：
  - `TMPDIR="$ROOT/cache/local_tmp/$RUN"`
  - `TORCH_HOME="$ROOT/cache/torch"`
  - `XDG_CACHE_HOME="$ROOT/cache/xdg"`
  - `TRITON_CACHE_DIR="$ROOT/cache/triton/$RUN/gpu${gpu}"`
  - 不使用 `/tmp` 或 `/dev/shm`。
- 每轮远端结果必须拉回本地后再判断下一轮，不靠远端日志想象视觉质量。

## 5. 当前下一步

1. Heartbeat 已指向本计划；若任务口径再次变化，先更新本节。
2. 完成树冠收束文档：`docs/evaluation/sc_tree_crown_V26_V33_selection_for_main_zh_20260511.md`。
3. 完成 IFS/DLA 定稿文档：`docs/evaluation/main_experiment_ifs_dla_case_selection_zh_20260511.md`。
4. 基于现有 L-system generator patterns 实现 V34 branch naturalization，先本地 dry-run + OBJ zoom。
5. 选两个 V34 候选上 `a100-2` GPU 4/5 或 6/7，跑 textured GLB；同时最多两卡。
6. 生成最终四类 case 的统一白底 comparison sheet、metrics matrix 和论文表格。
7. 在真实证据闭环后，局部修改 `paper_siga/main.tex`，保留用户中文，编译并 push Overleaf。

## 6. 2026-05-11 交接状态快照

- 已确认 `paper_siga` 是单独 git/Overleaf 目录；项目根不是 git 仓库。正文修改前必须读当前 `paper_siga/main.tex` 并局部 patch。
- 已确认本机 AgentDoc 副本存在但大量既有脏改且落后远端；本轮只读 AgentDoc/项目镜像文档，不做 AgentDoc 同步或破坏性整理。
- 已确认旧上下文里多个子任务一致认为：没有闭合的 `2D seam SDEdit/inpaint -> UV/3D/GLB 回投`，因此 L-system/tree naturalization 继续走 3D object-space grammar-owned local geometry + low-contrast whole-object guide。
- 新开只读探索：
  - 树冠审计已完成，结论见 Task A。
  - IFS/DLA 候选定位和 fig35/fig36 源路径梳理正在进行。
- 本轮最重要的未完成项是 V34 L-system branch naturalization：必须尽快生成 4 个本地候选、白底 OBJ zoom、选 2 个上远端。

## 7. 2026-05-11 当前执行块：主实验收束与白底图闭环

本节是本轮最新用户更新后的执行事实入口，后续 heartbeat 或上下文压缩后应优先读取本节再继续。

### 7.1 已收束/已知事实

- 树冠 case 不再作为无限迭代目标。当前主视觉优先在 `V32_sc_tree_balanced_canopy_D`、`V32_sc_tree_leafmass_shell_B`、`V29_sc_tree_softleaf_entry_D` 中选，最终图里只保留视觉最强/最能和传统 SC tree crown 一对一比较的一到两个。
- L-system `branch-with-side-branches` 是当前 P0。V35 已经完成远端 textured GLB，并有 post-GLB metrics；当前主候选暂定 `V35_lsys_branch_fused_fork_C`，指标稳定备选 `V35_lsys_branch_bark_sleeve_B` 和 `V35_lsys_branch_lowfrag_taper_D`。需要用纯白背景 overview + junction zoom 判断是否已经达到发表级；若仍有插接管/硬接缝/低模 token，继续 V36。
- IFS 使用用户头图认可的 pyrite HQ 线，当前主推 `visuals/pyrite_depth_hq_warm_showcase_20260509/stage04_textured.glb`，同时保留 V24 strict pyrite lattice 作为 transform-copy/strict lattice 备份证据。
- DLA 使用与头图不同的 coral case，当前主推 `v14_dla_branching_table_coral_b`，要求主图视角避免体素化和低多边形切面。
- 本机已经确认存在 `/Applications/Blender.app/Contents/MacOS/Blender`，版本 `5.1.1`。上一轮“本地/远端没 Blender”的阻塞已过期。白底 overview/zoom/callout 优先走本机 Blender，不再等待远端。
- `paper_siga/main.tex` 当前有用户/前 agent 的脏改和刻意保留中文。证据闭环前不改正文；正文修改时只做局部 patch，绝不覆盖中文段落。
- heartbeat `r-slg-publication-ralph-loop-2` 已更新到当前线程，20 分钟一次，继续指向本计划。

### 7.2 本轮必须产出的最小闭环

1. **L-system V35/V36 判断图**：对 V35 的 C/B/D 至少生成纯白 overview、overview_callouts、zoom_01、zoom_02、comparison sheet。目标区域优先选侧枝 junction 和端部 taper/cap。若 V35 C 在 zoom 里仍有明显接缝，立即实现/运行 V36。
2. **四类主实验一对一比较图**：传统 baseline vs ours，包含 SC、L-system、DLA、IFS 四行；所有图纯白背景；远景里用矩形框标出近景 zoom 区域；传统 baseline 不能故意选弱图。
3. **四类 metrics 表**：合并 surface-voxel connectivity、raw/welded mesh metrics、GLB import/render success、vertex/face/size、family-specific diagnostics。GPT/user study 留空占位，不写成已完成。
4. **fig35/fig36 depth/density 控制图**：B/C/D 行 GLB 用纯白背景重渲，每个子图带 zoom-in 和远景矩形框；先新增版本化 figure/draft，不覆盖旧文件。
5. **论文接入草稿**：在 `docs/paper/main_experiment_section_revision_notes_zh_20260511.md` 更新最终写作口径；待图和表通过 QA 后再局部写入 `paper_siga/main.tex`。

### 7.3 资源和安全边界

- 远端最多同时 2 张 GPU，只能从 `a100-2` 的 `4/5/6/7` 中选择。只有当 V35 纯白 zoom 证明不够或需要新 V36 textured GLB 时才上远端。
- 远端存储上限按最新用户口径为 `200GB`。只清理明确失败、重复、低价值缓存；不动可复现实验证据。
- 本机渲染/组合图和指标输出写入项目根下的 `visuals/`、`results/`、`docs/`、`paper_siga/figures/`、`paper_siga/drafts/`，不散落到项目外。

## 8. 2026-05-12 最新纠正后的执行块：深度/密度与语义对齐优先

本节是 2026-05-12 CST 用户纠正后的最新执行入口。后续 heartbeat、上下文压缩或 agent 交接时，应优先读取本节，再回看第 7 节历史状态。

### 8.1 最新口径变化

- **L-system branch-with-side-branches 的 P0 不再是继续修接缝本身**：当前形态基本达到要求，下一轮重点是接近传统 L-system baseline 的递归深度、侧枝密度、terminal 数量和多级分叉读感。我们的 case 必须在形态更自然的同时，结构上也能读成完整的递归 branch family。
- **传统 L-system baseline 本身是歪的**：进入对比前必须做 presentation/camera-level 直立重渲，保持几何/材质证据不被削弱，不把歪斜 baseline 当成 strawman。
- **V61 只作为干净但偏稀疏的中间基线**：已确认 V61 OBJ 白底图 clean，但侧枝数量和深度仍不足以和传统 L-system 的 dense recursive branch 直接对比。下一轮必须做 V62/V63：`main_steps=7--8`、`side_depth=3`、`side_every=2`、terminal count 目标 `12--16`，保留 V61/V59 的 anti-facet、shared-neck、graph-native taper 和 clean export policy。
- **IFS/transform 行不能继续放 pyrite 来对 branch-tree baseline**：当前 IFS 行如果比较的是 `ifs_branch_tree_matched`，ours 必须换成同语义的树干/树枝分叉结构。优先候选为 `V21_ifs_branch_tree_d6_natural_bark`；目标是模仿 IFS 树干分叉结构的深度、密度和多叉状态，同时更自然。Pyrite HQ 仍保留给 transform/pyrite lattice 证据或 teaser/另行 crystal row，不放错主实验 branch-tree 行。
- **DLA/frontier 行必须语义明确**：当前 ours 如果读不出语义则不能进入主实验。若 baseline 是 DLA/frontier/coral，则 ours 用复杂珊瑚 case；若 baseline 改成晶体，再用 ours crystal。当前主推复杂珊瑚候选 `v8_dla_coral_lace_reef_branching_a`，备选 `v8_dla_coral_antler_ridge_branching`、`v9_dla_coral_lace_branching_curve_a`、`V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA`。
- **正文 TeX 暂不推进**：在 L-system V62/V63、IFS branch-tree、DLA coral、SC tree crown 四行的白底 visual + zoom + metrics 闭环前，不 patch `paper_siga/main.tex`，并继续保留用户刻意留下的中文。

### 8.2 当前候选定位

- L-system 当前 fallback GLB：`results/strict_visual_matched_texture_V60_lsystem_branch_clean_export_fine_20260511/V60_lsys_branch_clean_short_bough_lowfrag_B/textured.glb`。优点是 r0/r1/r2 单连通、LCR 1.0；缺点是太稀疏，只能兜底。
- L-system 当前本地视觉基线：`visuals/strict_visual_matched_cases_V61_lsystem_branch_obj_zoom_dense_clean_bough_20260512/V61_lsystem_branch_dense_clean_bough_obj_contact_sheet_20260512.png`。优点是 clean；缺点是深度/密度不足。
- L-system baseline GLB：`visuals/traditional_baseline_texture_matched_guide_20260509/lsystem_branch_matched_steps6_tex1024_xformers/textured.glb`；baseline OBJ：`results/traditional_baselines/run_20260507_0300/lsystem_branch.obj`。必须直立/摆正后纯白重渲。
- IFS branch-tree ours 主候选：`visuals/strict_visual_matched_texture_V21_ifs_transform_natural_tex4096_seed20292500_20260510/V21_ifs_branch_tree_d6_natural_bark_steps8_tex4096_seed20294601_xformers/textured.glb`。metrics 已知：`9729 vertices / 19454 faces / 1 component / LCR 1.0 / depth 6 / affine transforms 3`；post-GLB occ64 r0 仅 12 tiny comps、LCR `0.9977`，r1/r2 单连通。
- DLA/frontier ours 主候选：`visuals/strict_visual_matched_texture_v8_frontier_refine_20260510/v8_dla_coral_lace_reef_branching_a_steps8_tex2048_seed20260811_xformers/textured.glb`。metrics 已知：`22503 vertices / 42491 faces / 1 component / LCR 1.0 / bbox diag 3.83 / surface area 17.88`。

### 8.3 立即执行顺序

1. 实现 `V62_lsystem_branch_recursive_dense_bough_yfork_20260512`：从 V61 派生，但增加递归深度和密度，至少四个本地候选；测试门槛提升到 `branch_junction_count >= 10`、`terminal_count >= 12`，优先 B/C 上远端。
2. 本地 materialize V62 dry-run，并用统一白底 OBJ zoom 做 contact sheet；只有视觉上比 V61 明显更接近 L-system 深度/密度且仍无硬接缝，才上 `a100-2` 两卡 textured GLB。
3. 直立/摆正传统 L-system baseline，并重渲纯白 overview + zoom/callout；记录 baseline 没有被弱化。
4. 版本化主实验 manifest：替换 IFS 行为 V21 branch-tree，替换 DLA/frontier 行为 V8 lace reef coral，L-system 行等待 V62/V63 或回退 V60，SC 行在 V29/V32 中收束。
5. 统一跑四行 metrics 和白底 comparison；证据闭环后再写 `docs/paper/main_experiment_section_revision_notes_zh_20260511.md` 和 `paper_siga/main.tex` 局部 patch。

### 8.4 2026-05-12 当前执行状态：V63 远端回收与主实验语义修正

- `V62` 已完成本地 dry-run 和 OBJ 白底 contact，但视觉结论是不作为最终：指标强、递归统计提高，但整体过于紧凑，terminal clusters 容易读成厚 blob。
- `V63_lsystem_branch_distributed_recursive_bough_20260512` 已完成本地 dry-run/OBJ 白底 contact，并且 `B/C` 已在 `a100-2` 的 GPU `4/5` 跑完 textured GLB。当前远端路径为 `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/strict_visual_matched_texture_V63_lsystem_branch_distributed_recursive_bough_BC_20260512_remote/`。
- `V63` 的判断标准不是“是否继续修接缝”，而是是否在自然形态基础上达到传统 L-system branch 的深度/密度/递归层级：候选至少应有清楚的主轴、沿轴分布的多级侧枝、足够 terminal 数量、zoom 中无 terminal blob 或切管读感。若 `V63 B/C` 白底 GLB zoom 仍不够，下一轮 `V64` 应保持 distributed graph，重点增加侧枝层级和细梢数量，同时缩小 terminal cap/降低末端团块，而不是回到 V62 的紧凑团簇。
- 传统 L-system baseline 必须摆正后重渲。若 GLB presentation rotation 在当前 renderer 中仍无效，则优先采用 OBJ neutral baseline 或生成 presentation-normalized mesh 副本，保证 baseline 是公平、直立、纯白背景的可读对照。
- IFS/transform 行按用户纠正改为同语义 branch-tree：当前主候选仍是 `V21_ifs_branch_tree_d6_natural_bark`，pyrite 仅用于 transform/pyrite lattice 或 teaser/crystal 证据，不放到 branch-tree 对比行。
- DLA/frontier 行按语义改为复杂 coral：当前主候选仍是 `v8_dla_coral_lace_reef_branching_a`；只有当该行 baseline 明确改为 crystal 时，才切换 ours crystal。
- `paper_siga/main.tex` 仍暂不修改。只有四行白底 visual + zoom + metrics 闭环后，才做局部 patch，并保留用户刻意留下的中文。

### 7.4 2026-05-11 当前执行更新：V36 之后继续 V37

本节记录本轮最新执行状态，避免上下文压缩后误把 V36 当作最终完成版本。

- `V35` 已有远端 textured GLB 和 post-GLB metrics，`B/C/D` 指标稳定，但白底 zoom QA 仍有“粗主枝 + 小侧枝贴上去”的读感，不建议直接进入主文正例。
- `V36` 已完成本地 generator、launcher、pytest、dry-run 和 OBJ 白底 zoom。它比 V35 更木质、更连通，但固定 junction zoom 后仍能看到粗主枝端部支配画面，部分候选的第二级 zoom 仍像切管/端帽，而不是自然分叉。因此当前决策是：**不要先上远端跑 V36 textured GLB，先做 V37 本地几何迭代**。
- `V37` 目标不是增加叶片遮挡，而是把 L-system branch-with-side-branches 做成更可信的连续木质分叉：
  - 缩短并缩细主轴 terminal，把端部从主要视角/zoom 中移开或转成自然闭合的细梢；
  - 让侧枝从主干中心线附近自然长出，而不是从粗管外壁插入；
  - 用更长的 tapered union sleeve、cambium saddle 和 bark ridge 沿主枝方向过渡；
  - 降低自由小叶/小芽数量，避免“绿片遮缝”的视觉借口；
  - zoom target 固定在中段侧枝 junction，而不是 terminal cap 或粗主枝端面。
- V37 本地验收门槛：
  - pre-export `mesh_component_count=1` 且 `largest_mesh_component_vertex_ratio>=0.999`；
  - OBJ 白底 overview 里侧枝层级明确，zoom_01/zoom_02 中不出现明显插接管、截断端面、大块低模 token 或空白 target；
  - 至少两个候选视觉过关后，才同步远端并用 `a100-2` 的 `4/5/6/7` 中最多两张卡跑 textured GLB。
- 若 V37 的 OBJ 白底仍不够，下一步不是盲跑纹理，而是继续 V38，优先改 graph/root/camera target 和 union geometry。远端 GPU 只用于视觉已基本过关的候选。

### 7.5 2026-05-11 V37 QA 结论与 V38 目标

- V37 已实现并通过本地验证：
  - generator：`assets/strict_visual_matched_cases_V37_lsystem_branch_woody_junction_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V37_lsystem_branch_woody_junction_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V37_lsystem_branch_woody_junction_naturalization_20260511.py`
  - dry-run：`results/strict_visual_matched_cases_V37_lsystem_branch_woody_junction_naturalization_20260511_dryrun/`
  - OBJ 白底 contact：`visuals/strict_visual_matched_cases_V37_lsystem_branch_obj_zoom_junctiontarget_20260511/V37_lsystem_branch_continuous_saddle_obj_contact_sheet_20260511.png`
- V37 指标：四个候选 pre-export 都是 `mesh_component_count=1`、`largest_mesh_component_vertex_ratio=1.0`；A/C 有 `50` 个 saddle neck，B/D 有 `10` 个 saddle neck；pytest `4 passed`。
- V37 视觉 QA：比 V36 更像连续分叉，但仍不满足发表级 L-system branch 正例。主要失败是白底 overview/zoom 里仍出现一个明显的大主轴端帽/截断管，zoom_02 会被读成“被切断的粗管 + 小枝”，而不是自然树枝。**因此 V37 不应上远端跑 textured GLB。**
- V38 目标：
  - 完全移除大主轴端帽读感：主轴末端必须变成细梢、自然弯出视野，或由多个细分叉终止，不能保留粗截断端；
  - zoom target 必须固定到无端帽的中段 saddle junction，不能落在 terminal cap；
  - 保留 V37 的 saddle-neck continuity 和 single-component/LCR 优势；
  - 若 V38 overview 和 zoom 都过关，才选择 2 个候选同步远端，用 `a100-2` 的 `4/5/6/7` 中最多两张卡跑 textured GLB。
- 对 Overleaf 的 push 只在正文局部 patch、LaTeX 编译通过、确认没有覆盖用户中文后执行。

### 7.6 2026-05-11 V38 QA 结论与 V39 目标

- V38 已完成本地 generator、launcher、pytest、dry-run、Blender 白底 OBJ zoom 和 contact sheet：
  - generator：`assets/strict_visual_matched_cases_V38_lsystem_branch_tipless_saddle_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V38_lsystem_branch_tipless_saddle_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V38_lsystem_branch_tipless_saddle_naturalization_20260511.py`
  - dry-run：`results/strict_visual_matched_cases_V38_lsystem_branch_tipless_saddle_naturalization_20260511_dryrun/`
  - OBJ 白底 contact：`visuals/strict_visual_matched_cases_V38_lsystem_branch_obj_zoom_junctiontarget_20260511/V38_lsystem_branch_tipless_saddle_obj_contact_sheet_20260511.png`
- V38 指标仍然稳定，四个候选都是 single component / LCR 1.0；但视觉 QA 失败，**不应上远端**：
  - contact sheet 中 `zoom_01` 的红框覆盖大量空白，说明固定 target 没有稳定落在可读 junction；
  - `zoom_02` 近景仍会读成孤立楔形/端部小片，而不是自然分叉；
  - 一些候选的主枝仍有“细枝旁挂一个切掉的 terminal sleeve”的读感，不能作为发表级 L-system branch 正例。
- V38 失败有两类原因：
  - geometry：terminal sleeve/lobe 虽然小，但在白底近景里仍形成楔形端帽；局部 collar center 作为 zoom target 也容易落到 lobe 尖端而不是 junction 根部。
  - camera/manifest：`zoom_02` 的 fixed target 与 `zoom_01` 几乎重合或落到同一 lobe 尖端，二级近景不是对 junction 的有效放大。
- V39 目标：
  - 移除 terminal sleeve 端帽策略，改成更细的 terminal twig continuation 和 wood-only taper；不再用可见 sleeve/lobe 作为端部遮挡；
  - zoom target 从 collar/lobe endpoint 改为 graph junction node + child-axis midpoint，优先中段侧枝根部；
  - 二级 zoom 必须围绕同一 junction 根部，不能漂到 terminal 或空白；
  - 本地 OBJ 白底 contact 中 overview、zoom_01、zoom_02 都必须有清楚的侧枝从主枝连续长出的读感，才允许同步远端并最多两卡跑 textured GLB；
  - 若 V39 仍失败，继续 V40，不用远端纹理掩盖结构问题。

### 7.7 2026-05-11 V39 QA 结论与 V40 目标

- V39 已实现并通过本地结构测试：
  - generator：`assets/strict_visual_matched_cases_V39_lsystem_branch_junction_root_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V39_lsystem_branch_junction_root_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V39_lsystem_branch_junction_root_naturalization_20260511.py`
  - pytest：`4 passed`
  - dry-run：`results/strict_visual_matched_cases_V39_lsystem_branch_junction_root_naturalization_20260511_dryrun/`
  - OBJ 白底 contact：`visuals/strict_visual_matched_cases_V39_lsystem_branch_obj_zoom_junctiontarget_20260511/V39_lsystem_branch_junction_root_obj_contact_sheet_20260511.png`
- V39 结构变化：terminal sleeve 被禁用，terminal 由 wood-only twig continuation 处理；zoom target 改为 junction root + child-axis midpoint pair，避免 V38 的同点/空白 target。
- V39 视觉 QA 仍失败，**不应上远端**：
  - `zoom_01` 仍被主枝楔形/细长主轴占据，像端部或管段而不是侧枝融合根；
  - `zoom_02` 仍大量空白，说明二级 target 不是一个稳定、可读、位于物体中心的 nested zoom；
  - overview 中侧枝层级存在，但目标区域没有展示“branch with side branches”的核心优势。
- V40 目标：
  - 直接重构 L-system branch graph，强制低中段出现 2--3 个可见 Y 型侧枝根，root anchor 在 overview 中远离 terminal；
  - zoom target 不再从 collar/lobe 或排序点自动选，而是从 generator 写入 `primary_junction_zoom_pairs`，固定第一组为最清楚的低中段侧枝根；
  - 视觉上宁可少一些 leaf/sheath，也要让主枝和侧枝的连续木质 fork 占满 zoom_01/zoom_02；
  - 若 V40 overview/zoom 仍失败，下一步考虑改用现有传统 L-system baseline 的 skeleton 做同拓扑 local naturalization，而不是继续随机 graph。

### 7.8 2026-05-11 V40 执行状态

- V40 已实现并通过结构测试：
  - generator：`assets/strict_visual_matched_cases_V40_lsystem_branch_primary_fork_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V40_lsystem_branch_primary_fork_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V40_lsystem_branch_primary_fork_naturalization_20260511.py`
  - renderer patch：`scripts/figures/matched_camera_zoom_render_20260510.py` 新增向后兼容 `zoom_divisor`，默认 `2.15` 不变。
  - pytest：`python3 -m pytest -q tests/test_strict_visual_matched_cases_V40_lsystem_branch_primary_fork_naturalization_20260511.py scripts/figures/test_matched_camera_zoom_render_20260510.py`，结果 `4 passed`。
- V40 local dry-run：
  - `results/strict_visual_matched_cases_V40_lsystem_branch_primary_fork_naturalization_20260511_dryrun/`
  - 四候选 single component / LCR 1.0；terminal sleeve 锁定为 0；第一 zoom pair 锁定显式 low/mid primary fork。
- V40 白底 OBJ QA：
  - 主 contact：`visuals/strict_visual_matched_cases_V40_lsystem_branch_obj_zoom_primaryfork_20260511/V40_lsystem_branch_primaryfork_obj_contact_sheet_20260511.png`
  - 备用同 anchor zoom contact：`visuals/strict_visual_matched_cases_V40_lsystem_branch_obj_zoom_primaryfork_sameanchor_zoom245_20260511/V40_lsystem_branch_primaryfork_sameanchor_zoom245_obj_contact_sheet_20260511.png`
  - 结论：比 V38/V39 明显前进，`overview` 与 `zoom_01` 已经能读到中段侧枝从主枝连续分叉。`zoom_02` 仍非完美主文近景，但已不再是空白或大端帽。为了避免本地无限打磨，V40 被批准进入远端 textured GLB 验证。
- 远端状态：
  - 远端：`a100-2`
  - 远端根目录：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
  - 预检：远端目录约 `139G`，低于 `200GB`；GPU 4/5/6/7 空闲。
  - 已同步 V40 generator/launcher 和 renderer patch。
  - 已启动：`V40_GPUS="4 5" STEPS=8 TEXTURE_SIZE=2048 bash assets/launch_strict_visual_matched_texture_V40_lsystem_branch_primary_fork_naturalization_20260511.sh`
  - 运行方式：GPU4 worker 先跑 `V40_lsys_branch_primary_fork_A`，后续 `dense_C`；GPU5 worker 先跑 `lowfrag_B`，后续 `slim_D`。同时最多两张卡。
- 下一步：
  - 监控远端日志和 `summary.json`；
  - 拉回 textured GLB；
  - 用白底 GLB zoom 和 post-GLB metrics 决定是否选 `lowfrag_B`/`slim_D` 或 `A`/`dense_C` 进入主实验 L-system 正例。

### 7.9 2026-05-11 V40 post-GLB 指标、主实验矩阵和 fig35/36 白底重渲

- V40 远端 textured GLB 已完成并拉回，四个候选均 `status: ok`：
  - `V40_lsys_branch_primary_fork_A_steps8_tex2048_seed20299512_xformers/textured.glb`
  - `V40_lsys_branch_primary_fork_lowfrag_B_steps8_tex2048_seed20299513_xformers/textured.glb`
  - `V40_lsys_branch_primary_fork_dense_C_steps8_tex2048_seed20299514_xformers/textured.glb`
  - `V40_lsys_branch_primary_fork_slim_D_steps8_tex2048_seed20299515_xformers/textured.glb`
- 新增 V40 post-GLB metrics：
  - surface metrics：`results/main_experiment_case_metrics_20260511/v40_lsystem_postglb_surface_metrics_occ64.csv`
  - recursive mesh metrics：`results/main_experiment_case_metrics_20260511/v40_lsystem_postglb_recursive_mesh_metrics.csv`
  - 关键判断：`slim_D` 指标最稳，`components_r0=1, LCR=1.0`；`lowfrag_B` 次稳，`components_r0=2, LCR=0.9977` 但材质红绿分裂；`A` 视觉分叉更自然但 r0 被拆成 4 个 components。
- L-system 当前结论：
  - `V40_lsys_branch_primary_fork_slim_D` 可作为“thin naturalized branch / topology-stable”候选；
  - 但它仍偏稀疏，和传统 dense branch-with-side-branches 的视觉强度不完全匹配，不能写成完全发表级的最终视觉胜利；
  - 若继续追主图质量，下一步应做 V41/V42：保留 D 的连通稳定性，增加中段 primary fork 密度，避免 B 的材质分裂，并修正主实验自动 zoom target。
- 四类主实验 comparison 已生成：
  - manifest：`results/main_experiment_case_metrics_20260511/main_experiment_traditional_vs_ours_manifest_20260511.json`
  - 单 case 白底 zoom：`visuals/main_experiment_traditional_vs_ours_white_zoom_20260511/`
  - QA contact：`visuals/main_experiment_traditional_vs_ours_white_zoom_20260511/main_experiment_traditional_vs_ours_contact_sheet_20260511.png`
  - 论文矩阵草稿：`paper_siga/figures/main_experiment_traditional_vs_ours_white_zoom_matrix_20260511.png`
  - 对应评估文档：`docs/evaluation/main_experiment_visual_metric_convergence_status_zh_20260511.md`
- 四类主实验统一指标已生成：
  - surface：`results/main_experiment_case_metrics_20260511/main_experiment_selected_surface_metrics_occ64.csv`
  - mesh：`results/main_experiment_case_metrics_20260511/main_experiment_selected_recursive_mesh_metrics.csv`
  - LaTeX table draft：`paper_siga/figures/main_experiment_selected_metrics_table_20260511.tex`
  - 指标摘要：SC ours r0 有 10 个 tiny components 但 r1 connected；L-system V40-D、DLA ours、IFS pyrite HQ 均 r0/r1 single component；IFS pyrite HQ faces `482,348`、box dim `2.195`。
- fig35/fig36 对应的 depth/density 控制图已按纯白背景重渲：
  - manifest：`results/main_experiment_case_metrics_20260511/depth_density_control_white_zoom_manifest_20260511.json`
  - raw/callout：`visuals/fig35_fig36_depth_density_rerender_20260511/`
  - depth progression：`paper_siga/figures/fig35_depth_parameter_mesh_showcase_white_zoom_20260511.png`
  - density sweep：`paper_siga/figures/fig36_coral_density_extreme_white_zoom_20260511.png`
  - 状态文档：`docs/figures/depth_density_control_white_zoom_status_zh_20260511.md`
  - QA：pyrite row 最强；bismuth/coral 行适合作 method-behavior/control evidence，不适合作自然视觉主 claim。
- `paper_siga/main.tex` 尚未 patch。原因：用户明确要求保留中文，且当前 L-system 主图仍未完全发表级；下一步只应在证据闭环后局部替换 figure include/input，不动中文块。

### 7.10 2026-05-11 V41/V42 post-GLB QA 与 V43 目标

- `V41` 已完成远端 textured GLB、post-GLB metrics 和白底 GLB zoom，但视觉 QA 失败：它比 V40 更密，却在近景中碎成细针/叶片，且 exact r0 connectivity 下降，不应作为主文 L-system 正例。
- `V42` 已完成本地 generator/launcher/test/dry-run、远端 textured GLB、post-GLB surface/mesh metrics 和白底 GLB zoom：
  - generator：`assets/strict_visual_matched_cases_V42_lsystem_branch_cluster_fork_naturalization_20260511.py`
  - remote：`results/strict_visual_matched_texture_V42_lsystem_branch_cluster_fork_naturalization_20260511_remote/`
  - surface metrics：`results/main_experiment_case_metrics_20260511/v42_lsystem_postglb_surface_metrics_occ64.csv`
  - mesh metrics：`results/main_experiment_case_metrics_20260511/v42_lsystem_postglb_recursive_mesh_metrics.csv`
  - GLB contact：`visuals/strict_visual_matched_texture_V42_lsystem_branch_cluster_fork_zoom_white_20260511/V42_lsystem_branch_cluster_fork_glb_contact_sheet_20260511.png`
- V42 指标上 `lowfrag_B` 与 `dense_C` 有明显进步，`components_r0=1, LCR=1.0`，比 V41 更稳；但视觉仍不够发表级：overview/zoom 仍像“细线骨架 + 扁叶/芽片/长针贴附”，侧枝根部的连续木质分叉不够厚实，局部存在长针和片状 token。因此 V42 可作为失败-进步证据和备选，不替换最终主实验 L-system 正例。
- 下一轮 `V43` 目标：
  - 减少 Trellis2 容易解释成叶片/针刺的自由细节：大幅降低 ridge/split 的细长管数量，不使用 leaf sheath、terminal sleeve、绿片遮缝；
  - 从图结构上做更粗、更连续的同类木质 Y-fork：主枝和侧枝在 low/mid zoom target 处有可读的共享 saddle-neck 和 union collar；
  - zoom target 固定在最粗、最清楚的 low/mid Y-junction 根部，而不是细枝末端、lobe endpoint 或空白区域；
  - 本地 OBJ 白底 contact 中至少两个候选要在 overview、zoom_01、zoom_02 都读成连续树枝分叉，才允许同步远端；
  - 远端仍只用 `a100-2` 的 `4/5/6/7` 中最多两张卡，默认 GPU 4/5；远端存储继续控制在 200GB 内。
- 证据闭环前继续不 patch `paper_siga/main.tex`，尤其保留用户刻意留下的中文 `ChinesePlan` 块。

### 7.11 2026-05-11 V43 本地 QA 与 V44 目标

- `V43` 已实现并完成本地结构测试、dry-run 与 OBJ 白底 overview/zoom：
  - generator：`assets/strict_visual_matched_cases_V43_lsystem_branch_wood_yfork_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V43_lsystem_branch_wood_yfork_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V43_lsystem_branch_wood_yfork_naturalization_20260511.py`
  - pytest：`2 passed`
  - dry-run：`results/strict_visual_matched_cases_V43_lsystem_branch_wood_yfork_naturalization_20260511_dryrun/`
  - OBJ contact：`visuals/strict_visual_matched_cases_V43_lsystem_branch_obj_zoom_woodyfork_20260511/V43_lsystem_branch_wood_yfork_obj_contact_sheet_20260511.png`
- V43 指标达标：四个候选 pre-export 均 `mesh_component_count=1`、`largest_mesh_component_vertex_ratio=1.0`，并且把 semantic detail 降到 `62--109`，避免 V42 那种 post-GLB 细针/叶片碎片风险。
- V43 视觉 QA 仍未达发表级，**不应上远端**：
  - 它成功去掉了 V42 的叶片/长针碎片，但 zoom 里读成“细管 + 圆鼓包 saddle/collar”，不是自然连续树枝；
  - junction 处的融合带太短、太圆，局部像机械节点或球形套管；
  - 侧枝仍有从鼓包上硬转出的管状感。
- `V44` 目标：
  - 把 V43 的圆鼓包改成沿主枝方向拉长、低起伏的椭圆 cambium saddle / sleeve；
  - side branch 从融合带中自然转出，局部半径从主枝到侧枝连续衰减，不要用球形 collar 遮缝；
  - zoom target 仍锁定 low/mid y-fork，但相机要展示 elongated saddle，而不是只拍到球形节点；
  - 继续保持 single-component/LCR 优势、无 leaf sheath、无 terminal sleeve、少自由细节；
  - V44 本地白底 overview/zoom 过关后，才同步远端并用最多两张 GPU 跑 textured GLB。

### 7.12 2026-05-11 V44 QA 结论与 V45 implicit-union 路线

- `V44` 已完成本地 generator、launcher、pytest、dry-run、Blender 白底 OBJ overview/zoom 和 contact sheet：
  - generator：`assets/strict_visual_matched_cases_V44_lsystem_branch_elongated_saddle_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V44_lsystem_branch_elongated_saddle_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V44_lsystem_branch_elongated_saddle_naturalization_20260511.py`
  - dry-run：`results/strict_visual_matched_cases_V44_lsystem_branch_elongated_saddle_naturalization_20260511_dryrun/`
  - OBJ contact：`visuals/strict_visual_matched_cases_V44_lsystem_branch_obj_zoom_elongatedsaddle_20260511/V44_lsystem_branch_elongated_saddle_obj_contact_sheet_20260511.png`
- V44 视觉 QA 失败，**不应上远端 textured GLB**：
  - overview 有 branch-with-side-branches 层级，但 zoom 仍像“细杆 + 低模楔形套管/机械节点”；
  - elongated saddle 仍是先生成细管 scaffold，再在节点外 append sleeve/ring geometry，近景会读成外贴结构，而不是连续木质分叉；
  - 继续调 sleeve 参数大概率只是在 V43 的“圆鼓包”和 V44 的“楔形套管”之间摆动。
- `V45` 已启动并通过本地 generator/test smoke：
  - generator：`assets/strict_visual_matched_cases_V45_lsystem_branch_implicit_wood_fork_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V45_lsystem_branch_implicit_wood_fork_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V45_lsystem_branch_implicit_wood_fork_naturalization_20260511.py`
  - pytest：`2 passed`
  - smoke dry-run：`results/strict_visual_matched_cases_V45_lsystem_branch_implicit_wood_fork_naturalization_20260511_smoke/`
- V45 的核心修正是把 fork root 从 `tube + appended sleeve` 改为 `implicit/metaball union before marching cubes`：
  - parent segment、saddle neck、child root、local saddle swell、bark ridge 都 stamp 到同一个 scalar field；
  - marching cubes 后只保留 largest component 并 Taubin smooth；
  - metadata/test 锁定 `implicit_union_support=True`、`mechanical_sleeve_disabled=True`、`direct_axis_sleeve_count=0`、`junction_implicit_union_count>=3`；
  - claim boundary 仍然是 generator-native object-space local naturalization，不声称 2D seam inpaint/backprojection。
- V45 当前注意事项：
  - smoke A 已可生成 OBJ 且 pre-export mesh 单连通，但 raw marching-cubes 小岛较多，`largest_component_projection_retained_ratio≈0.65`；若视觉过关，应下一步调高 field connectivity/level 或强化 branch/ridge stamp 以降低 raw islands；
  - V45 smoke Blender 白底 zoom 正在/待完成：`visuals/strict_visual_matched_cases_V45_lsystem_branch_obj_zoom_smoke_implicitwoodfork_20260511/`；
  - 若 smoke 仍像短 blob 或丢失侧枝层级，先调 V45 implicit field 参数，不上远端；
  - 若 smoke 读感明显优于 V44，再跑完整四候选 dry-run、OBJ contact，选至少两个候选上 `a100-2` GPU 4/5（最多两卡）。

### 7.13 2026-05-11 V45/V46 QA 结论与 V47 shared-neck Y-fork 路线

- `V45` 完成 whole-branch implicit/metaball union smoke 和 OBJ 白底 contact：
  - generator：`assets/strict_visual_matched_cases_V45_lsystem_branch_implicit_wood_fork_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V45_lsystem_branch_implicit_wood_fork_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V45_lsystem_branch_implicit_wood_fork_naturalization_20260511.py`
  - contact：`visuals/strict_visual_matched_cases_V45_lsystem_branch_obj_zoom_smoke_implicitwoodfork_20260511/V45_lsystem_branch_implicit_wood_fork_smoke_contact_sheet_20260511.png`
  - QA 结论：它去掉了 V44 的外贴套管，但整体变成粗短 blob/root-like，overview 失去 branch-with-side-branches 的长程轮廓，zoom 也不再有效。因此 **V45 不上远端**。
- `V46` 完成 high-sided continuous sweep + junction-local radius boost + short transition lobes：
  - generator：`assets/strict_visual_matched_cases_V46_lsystem_branch_continuous_sweep_fork_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V46_lsystem_branch_continuous_sweep_fork_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V46_lsystem_branch_continuous_sweep_fork_naturalization_20260511.py`
  - dry-run：`results/strict_visual_matched_cases_V46_lsystem_branch_continuous_sweep_fork_naturalization_20260511_dryrun/`
  - contact：`visuals/strict_visual_matched_cases_V46_lsystem_branch_obj_zoom_continuoussweepfork_20260511/V46_lsystem_branch_continuous_sweep_fork_obj_contact_sheet_20260511.png`
  - QA 结论：V46 恢复了长程 L-system branch 轮廓，也保持四候选 pre-export 单连通 / LCR 1.0；但近景仍像细管/硬折线 + 局部小鼓包，junction 连续木质感不足。因此 **V46 也不应直接上远端**，只作为 V44/V45 之后的局部进步证据。
- `V47` 当前目标：
  - 保留 V46 的长程轮廓、白底 manifest、安全 launcher 和 single-component gate；
  - 在 graph 层显式插入短 shared-neck intermediate nodes，让 main continuation 和 side branch 先共享一小段中心线，再分叉，避免“从管外壁插入”的读感；
  - 降低外贴 transition lobe 的视觉权重，把 naturalization 主要交给共享 graph 拓扑 + 局部 radius boost，而不是靠 sleeve/lobe patch；
  - 低中段 primary zoom target 固定到 shared neck 的根部和 side-branch interior，不能拍 terminal、端帽或空白；
  - 本地 pytest、dry-run、Blender 纯白 OBJ overview/zoom/contact 过关后，才同步远端并最多用 `a100-2` 的 GPU 4/5 跑 textured GLB。
- V47 验收门槛：
  - pre-export `mesh_component_count=1` 且 `largest_mesh_component_vertex_ratio>=0.999`；
  - overview 中可读出传统 L-system branch-with-side-branches 的递归侧枝层级；
  - `zoom_01/zoom_02` 中至少两个候选能读成自然木质 Y-fork，不出现插接管、楔形套管、圆鼓包主导、截断端帽或空白 target；
  - 未达到上述视觉门槛前，不 patch `paper_siga/main.tex`，不 push Overleaf，不上远端纹理生成。

### 7.14 2026-05-11 V47 QA 结论与 V48 implicit-capsule 路线

- `V47` 已完成本地 generator、launcher、pytest、dry-run、Blender 白底 OBJ overview/zoom 和 contact sheet：
  - generator：`assets/strict_visual_matched_cases_V47_lsystem_branch_shared_neck_yfork_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V47_lsystem_branch_shared_neck_yfork_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V47_lsystem_branch_shared_neck_yfork_naturalization_20260511.py`
  - pytest：`2 passed`
  - dry-run：`results/strict_visual_matched_cases_V47_lsystem_branch_shared_neck_yfork_naturalization_20260511_dryrun/`
  - contact：`visuals/strict_visual_matched_cases_V47_lsystem_branch_obj_zoom_sharedneckyfork_20260511/V47_lsystem_branch_shared_neck_yfork_obj_contact_sheet_20260511.png`
- V47 结构进步：
  - 四候选 pre-export 单连通 / LCR 1.0，`shared_neck_inserted_count>=3`；
  - overview 中 branch-with-side-branches 轮廓清楚，比 V45 的 blob 方向正确；
  - low/mid zoom target 稳定落在可读分叉区域，不是空白或 terminal。
- V47 视觉 QA 仍未达发表级，**不应上远端 textured GLB**：
  - zoom 中仍能读成低多边形硬管和三角折线，局部有机械折面；
  - shared-neck graph 解决了“从外壁插入”的一部分语义，但 ring/fan sweep 的面片仍让 junction 像折管；
  - 比 V46 少了小鼓包，但自然木质连续曲面仍不足。
- `V48` 路线：
  - 继承 V47 shared-neck graph 和 zoom target；
  - 把 support mesh 从 high-sided ring sweep 改为高分辨率 implicit capsule union / marching cubes，消除 hard ring fan facets；
  - 参数上比 V45 更保守：更高 resolution、更低 Gaussian blur、更低 junction swell、更强 taper 和 terminal clamp，避免 V45 的 coarse blob/root-like 坍缩；
  - output 仍是 OBJ 本地 QA，只有 V48 白底 overview + zoom 至少两个候选明显优于 V47，才同步远端跑 textured GLB。

### 7.15 2026-05-11 V48 QA 失败与 V49 high-res smooth Y-fork 进展

- `V48` 已完成本地 generator、launcher、pytest、dry-run、Blender 白底 OBJ overview/zoom 和 contact sheet：
  - generator：`assets/strict_visual_matched_cases_V48_lsystem_branch_implicit_capsule_yfork_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V48_lsystem_branch_implicit_capsule_yfork_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V48_lsystem_branch_implicit_capsule_yfork_naturalization_20260511.py`
  - dry-run：`results/strict_visual_matched_cases_V48_lsystem_branch_implicit_capsule_yfork_naturalization_20260511_dryrun/`
  - contact：`visuals/strict_visual_matched_cases_V48_lsystem_branch_obj_zoom_implicitcapsuleyfork_20260511/V48_lsystem_branch_implicit_capsule_yfork_obj_contact_sheet_20260511.png`
- V48 结构指标达标但视觉 QA 失败，**不应上远端 textured GLB**：
  - 四候选 pre-export 都是 single component / LCR 1.0，但顶点/面数只有约 `937--1373 / 1874--2754`，近景几何余量不足；
  - OBJ zoom 中仍显著读成低多边形硬折面、楔形节点和 coarse blob，不是自然木质连续 Y-fork；
  - raw marching-cubes component 为 `2--4`，largest-component retained ratio 低至约 `0.736`，说明 implicit field 仍有碎岛/低分辨率隐患。
- `V49` 已实现 high-resolution smooth Y-fork 路线并完成本地结构验证：
  - generator：`assets/strict_visual_matched_cases_V49_lsystem_branch_highres_smooth_yfork_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V49_lsystem_branch_highres_smooth_yfork_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V49_lsystem_branch_highres_smooth_yfork_naturalization_20260511.py`
  - pytest：`2 passed`
  - dry-run：`results/strict_visual_matched_cases_V49_lsystem_branch_highres_smooth_yfork_naturalization_20260511_dryrun/`
  - contact：`visuals/strict_visual_matched_cases_V49_lsystem_branch_obj_zoom_highressmoothyfork_20260511/V49_lsystem_branch_highres_smooth_yfork_obj_contact_sheet_20260511.png`
- V49 相对 V48 的关键修正：
  - implicit grid resolution 从 `112` 提高到 `176`，post-mesh 顶点/面数提高到约 `3584--4650 / 7164--9296`；
  - raw marching-cubes component 全部为 `1`，largest-component retained ratio 全部 `1.0`；
  - 降低 junction swell / ridge 强度，增加平滑，避免 V48 的楔形节点和 V45 的粗 blob；
  - 保持 no terminal sleeve / no 2D seam inpaint backprojection claim。
- V49 白底 QA 结论：`lowfrag_B` 和 `slim_D` 目前最稳，overview 和 zoom_01 已能读出较连续的中段 Y-fork，明显优于 V48；`zoom_02` 偏近，适合作 QA 但后续若入主图需要重新调 zoom divisor/target。
- 当前决策：V49 **允许进入远端 textured GLB 验证**，但仍只用 `a100-2` 的 GPU `4/5` 两张卡；远端结果拉回并做 GLB 白底 zoom/post-GLB metrics 后，才能决定是否替换主实验中 V40-D。
- 若 V49 post-GLB 出现材质分裂、树皮变叶片/针刺、或 zoom 再次变成 blob，则不 patch `paper_siga/main.tex`，继续 V50；不要用纹理掩盖局部几何问题。

### 7.16 2026-05-11 V49 post-GLB QA、smoothpost 诊断与 V50 本地收束

- V49 远端 textured GLB 已完成并拉回：
  - remote run：`strict_visual_matched_texture_V49_lsystem_branch_highres_smooth_yfork_naturalization_20260511`
  - 本地结果：`results/strict_visual_matched_texture_V49_lsystem_branch_highres_smooth_yfork_naturalization_20260511_remote/`
  - 白底 zoom：`visuals/strict_visual_matched_texture_V49_lsystem_branch_highres_smooth_yfork_zoom_white_20260511/V49_lsystem_branch_highres_smooth_yfork_glb_contact_sheet_20260511.png`
  - post-GLB metrics：`results/main_experiment_case_metrics_20260511/v49_lsystem_postglb_surface_metrics_occ64.csv` 与 `v49_lsystem_postglb_recursive_mesh_metrics.csv`
- V49 metrics 强：四个候选 post-GLB surface `components_r0=1, lcr_r0=1.0, components_r1=1, lcr_r1=1.0`，welded components 也为 `1`；`lowfrag_B` 和 `slim_D` 比 V40 明显更连贯。
- V49 视觉 QA 仍未完全发表级：
  - `lowfrag_B` 是当前最好的 V49 正例，但 white zoom 中 terminal/端部仍会读成圆头胶囊，近景仍有 faceted ridge；
  - `slim_D` 拓扑稳，但材质偏黑，主图可读性差；
  - 因此 V49 可以作为“比 V40 更好”的备选证据，但不应直接收束成最终主文 L-system ours。
- 已做本地 derivative smoothpost 诊断，证明问题不是单纯 normal/export faceting：
  - script：`assets/postprocess_v49_lsystem_branch_smooth_export_20260511.py`
  - output：`results/strict_visual_matched_texture_V49_lsystem_branch_highres_smooth_yfork_smoothpost_20260511/`
  - QA renders：`visuals/strict_visual_matched_texture_V49_lsystem_branch_highres_smooth_yfork_smoothpost_renderQA_zoom_white_20260511/`
  - 结论：subdivision/Laplacian smoothing 能降低表面折面，但会保留甚至强化 rounded terminal bulb 的语义；因此不能把 smoothpost 当最终主实验 case，只作为 V50 设计归因。
- V50 已实现并通过本地结构测试：
  - generator：`assets/strict_visual_matched_cases_V50_lsystem_branch_tapered_tip_highres_yfork_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V50_lsystem_branch_tapered_tip_highres_yfork_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V50_lsystem_branch_tapered_tip_highres_yfork_naturalization_20260511.py`
  - pytest：`2 passed`
  - dry-run：`results/strict_visual_matched_cases_V50_lsystem_branch_tapered_tip_highres_yfork_naturalization_20260511_dryrun/`
  - OBJ contact：`visuals/strict_visual_matched_cases_V50_lsystem_branch_obj_zoom_taperedtip_20260511/V50_lsystem_branch_taperedtip_obj_contact_sheet_20260511.png`
- V50 相对 V49 的关键改动：
  - implicit grid `176 -> 208`，field level `0.38 -> 0.40`，Gaussian sigma `0.52 -> 0.56`；
  - junction radius boost 稍降，避免分叉处鼓包主导；
  - 移除 V49 terminal cap ball，改为 short tapered implicit terminal continuations；新增 `terminal_taper_count` gate；
  - dry-run 四候选 raw MC components 全部 `1`、retained ratio `1.0`，pre-export LCR `1.0`，terminal taper 最少 `10`。
- V50 本地 OBJ QA 结论：
  - `A` / `dense_C` 仍能看到端部圆头，不上远端；
  - `lowfrag_B` 与 `slim_D` 的 junction zoom 明显比 V49 干净，端部圆头不再是主读感；允许远端 textured GLB 验证；
  - 下一步只跑 V50 `lowfrag_B` 和 `slim_D` 两个候选，最多用 `a100-2` GPU `4/5` 两张卡；远端结果拉回后再做 post-GLB metrics 与白底 zoom，若材质或 terminal 仍失败，再继续 V51，不 patch TeX。

### 7.17 2026-05-11 V50 post-GLB QA 失败归因与 V51 graph-taper 本地通过

- V50 B/D 远端 textured GLB 已完成、拉回并补齐 callouts/contact：
  - remote result：`results/strict_visual_matched_texture_V50_lsystem_branch_tapered_tip_highres_yfork_BD_20260511_remote/`
  - surface metrics：`results/main_experiment_case_metrics_20260511/v50_lsystem_bd_postglb_surface_metrics_occ64.csv`
  - mesh metrics：`results/main_experiment_case_metrics_20260511/v50_lsystem_bd_postglb_recursive_mesh_metrics.csv`
  - GLB white zoom/contact：`visuals/strict_visual_matched_texture_V50_lsystem_branch_tapered_tip_highres_yfork_BD_zoom_white_20260511/V50_lsystem_branch_taperedtip_BD_glb_contact_sheet_20260511.png`
- V50 指标强但视觉不收束：B/D post-GLB surface r0/r1/r2 全部 `components=1, LCR=1.0`，welded component 也为 `1`；但白底图中 zoom target 偏右且 textured GLB 出现深色 terminal/drop 和局部截断碎段读感，仍不能作为最终 L-system 主文视觉正例。因此 **V50 不切入主实验 manifest、不 patch TeX**。
- V51 已实现 graph-native terminal taper 路线：
  - generator：`assets/strict_visual_matched_cases_V51_lsystem_branch_graph_taper_yfork_naturalization_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V51_lsystem_branch_graph_taper_yfork_naturalization_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V51_lsystem_branch_graph_taper_yfork_naturalization_20260511.py`
  - pytest：`2 passed`
  - dry-run：`results/strict_visual_matched_cases_V51_lsystem_branch_graph_taper_yfork_naturalization_20260511_dryrun/`
  - OBJ contact：`visuals/strict_visual_matched_cases_V51_lsystem_branch_graph_taper_yfork_obj_zoom_20260511/V51_lsystem_branch_graph_taper_yfork_obj_contact_sheet_20260511.png`
- V51 关键修正：
  - 端部修复从 V50 的 terminal ellipsoid/field stamp 改为 grammar graph 内 two-step taper twig；metadata 中 `graph_terminal_taper_count>=10`、`field_terminal_taper_count=0`、`terminal_taper_source=graph_native_taper_segments_no_terminal_ellipsoid_stamps`；
  - implicit grid `216`、field level `0.405`、sigma `0.58`，junction boost 降到 `1.30/1.11`；
  - B/D guide 改用更轻的 cambium guide，减少 V50 post-GLB 过黑 terminal/drop 风险；
  - 四候选 raw marching-cubes component 全部 `1`，largest-component retained ratio 全部 `1.0`，pre-export LCR gate 通过。
- V51 本地 OBJ QA：相比 V50，B/D 的 junction 连续性和 terminal 语义更稳，端部不再由额外 ellipsoid stamp 主导；仍保留 branch-with-side-branches 长程轮廓。允许上远端 textured GLB 验证，但只跑 `lowfrag_B` 与 `slim_D`，最多用 `a100-2` 的 GPU `4/5`。
- 下一步执行门槛：
  - 同步 V51 generator/launcher 及必要依赖到远端；
  - 生成远端 inputs 后裁剪 `gpu4_cases.txt/gpu5_cases.txt` 只包含 B/D；
  - 跑 textured GLB，拉回后做 post-GLB metrics 和白底 GLB zoom；
  - 只有 V51 GLB 同时满足视觉过关（无暗 terminal drop、无孤立碎段、junction zoom 读成连续木质 Y-fork）与 surface/mesh 连通稳定时，才替换主实验 L-system ours、重跑 comparison/matrix/table 并局部 patch `paper_siga/main.tex`。

### 7.18 2026-05-11 V54--V57 失败收敛结论与 V58 root/silhouette 切换

- V54--V57 已完成本地 generator/test/dry-run/OBJ 白底 zoom，但结论一致：**指标过关、视觉未达发表级，不应上远端 textured GLB**。
  - V54 centered-bough：pre-export single component / LCR 1.0；白底 zoom 仍像管子分叉，近景有平切/截断边和 saddle 鼓包。
  - V55 elongated-saddle：pre-export single component / LCR 1.0；圆鼓包有所减弱，但端部变成“大头棒”，overview 更像细管骨架。
  - V56 basal-continuation：pre-export single component / LCR 1.0；basal continuation 没解决根部 club-like 读感，A/B/C 出现新的大头根部。
  - V57 tapered-midbough：pre-export single component / LCR 1.0；zoom 仍被裁切边/管状表面主导，A--D 均不应上远端。
- 关键经验：继续在同一长细 branch graph 上微调 local saddle / terminal taper 会把 metrics 做漂亮，但视觉仍被根 silhouette 限制；下一轮必须换 root/silhouette，而不是继续给 V57 打补丁。
- V58 已实现为 **short-bough root/silhouette rewrite**：
  - generator：`assets/strict_visual_matched_cases_V58_lsystem_branch_short_bough_yfork_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V58_lsystem_branch_short_bough_yfork_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V58_lsystem_branch_short_bough_yfork_20260511.py`
  - pytest：`1 passed`
  - dry-run：`results/strict_visual_matched_cases_V58_lsystem_branch_short_bough_yfork_20260511_dryrun/`
  - OBJ 白底 zoom/contact：`visuals/strict_visual_matched_cases_V58_lsystem_branch_obj_zoom_short_bough_20260511/V58_lsystem_branch_short_bough_obj_contact_sheet_20260511.png`
- V58 dry-run 结构指标：
  - 四个候选均 `mesh_component_count=1`、`largest_mesh_component_vertex_ratio=1.0`、`raw_marching_cubes_component_count=1`、`largest_component_projection_retained_ratio=1.0`。
  - 顶点/面数约 `5900--8056 / 11796--16108`，比 V54--V57 有足够几何余量。
  - 四候选 branch junction 最少 `4`，terminal taper 最少 `15`，仍符合 branch-with-side-branches 的 strict target。
- V58 白底 QA：
  - 整体明显脱离 V54--V57 的“长细管骨架”局部最小值；junction 不再主要读成圆鼓包 saddle。
  - 当前最可上远端候选是 `V58_lsys_branch_short_bough_lowfrag_B` 与 `V58_lsys_branch_short_bough_compact_D`，二者 overview 最干净、端部和分叉读感相对稳。
  - caveat：V58 仍只是 OBJ 视觉门槛通过，不是最终胜利；若 post-GLB 出现暗 terminal drop、塑料质感、纹理分裂或 Y-fork 变回插接管，必须继续 V59。
- 下一步：仅同步 V58 generator/launcher 到 `a100-2`，远端 generate-only 后裁剪 case 文件，只跑 B/D 两个候选，最多 GPU 4/5 两卡；拉回后做 post-GLB metrics 和白底 GLB zoom，过关才替换主实验 L-system ours。

### 7.19 2026-05-11 V58 post-GLB 指标闭合但视觉未最终发表级

- V58 B/D 已在 `a100-2` 完成 textured GLB，实际只保留两个本地 QA 最稳候选：
  - remote run：`strict_visual_matched_texture_V58_lsystem_branch_short_bough_yfork_BD_20260511`
  - 本地 GLB：`results/strict_visual_matched_texture_V58_lsystem_branch_short_bough_yfork_BD_20260511_remote/`
  - GLB 白底 zoom/contact：`visuals/strict_visual_matched_texture_V58_lsystem_branch_short_bough_yfork_BD_zoom_white_20260511/V58_lsystem_branch_short_bough_BD_glb_contact_sheet_20260511.png`
  - post-GLB metrics：`results/main_experiment_case_metrics_20260511/v58_lsystem_bd_postglb_surface_metrics_occ64.csv` 与 `results/main_experiment_case_metrics_20260511/v58_lsystem_bd_postglb_metrics/`
- 指标结果非常干净：
  - `V58_lsys_branch_short_bough_lowfrag_B`：post-GLB surface r0/r1/r2 全部 `components=1, LCR=1.0`。
  - `V58_lsys_branch_short_bough_compact_D`：post-GLB surface r0/r1/r2 全部 `components=1, LCR=1.0`。
  - faces 约 `11.8k`，GLB size 约 `646--702KB`。
- 视觉 QA：
  - V58 相比 V54--V57 是明确进步：overview 不再是长细管骨架，短枝段和侧枝结构读感更接近可比较的 branch-with-side-branches。
  - 但 post-GLB zoom 仍未最终发表级：表面出现明显锯齿/faceted strip，木纹偏塑料，`compact_D` 还有局部过暗端部；这些会在论文主图 zoom 中被放大。
  - 因此 V58 可以作为“root/silhouette 切换有效”的进步证据和 fallback，但暂不替换主实验 L-system 最终图，不 patch `paper_siga/main.tex`。
- 下一步 V59：不要回到长细 graph；保留 V58 short-bough silhouette，但提高隐式场分辨率/平滑、降低 post-GLB 易放大的脊线纹理强度，优先目标是 white GLB zoom 中无锯齿 strip、无暗端点、无塑料木纹主读感。若 V59 失败，再考虑把 V58 lowfrag_B 作为指标最强 fallback，并在主文 caption 中明确视觉 caveat。

### 7.20 2026-05-11 V59 本地 anti-facet short-bough 通过，B/D 上远端验证

- V59 已实现，目标不是改任务语义，而是专门解决 V58 post-GLB 的 faceted strip / 塑料木纹 / 暗端点问题：
  - generator：`assets/strict_visual_matched_cases_V59_lsystem_branch_smooth_short_bough_yfork_20260511.py`
  - launcher：`assets/launch_strict_visual_matched_texture_V59_lsystem_branch_smooth_short_bough_yfork_20260511.sh`
  - test：`tests/test_strict_visual_matched_cases_V59_lsystem_branch_smooth_short_bough_yfork_20260511.py`
  - pytest：`1 passed`
  - dry-run：`results/strict_visual_matched_cases_V59_lsystem_branch_smooth_short_bough_yfork_20260511_dryrun/`
  - OBJ 白底 zoom/contact：`visuals/strict_visual_matched_cases_V59_lsystem_branch_obj_zoom_smooth_short_bough_20260511/V59_lsystem_branch_smooth_short_bough_obj_contact_sheet_20260511.png`
- V59 关键改动：
  - 保留 V58 compact short-bough root/silhouette；
  - implicit grid `224 -> 288`，Gaussian sigma `0.60 -> 0.78`，field level `0.410 -> 0.424`；
  - junction boost 从 `1.30/1.11` 降到 `1.18/1.055`；
  - free ridge scaffold 降为 `0`，guide 改为 desaturated low-contrast bark/sapwood；
  - claim boundary 仍是 object-space grammar-owned naturalization，无 2D seam inpaint/backprojection。
- V59 本地指标：
  - 四候选均 `mesh_component_count=1`、`LCR=1.0`、`raw_marching_cubes_component_count=1`、retained ratio `1.0`；
  - faces 约 `17.7k--25.9k`，明显高于 V58，几何余量更充足；
  - free ridge `0`。
- V59 本地视觉 QA：
  - 比 V58 更平滑，OBJ zoom 中原先容易变成 post-GLB 锯齿 strip 的脊线源头明显减少；
  - `V59_lsys_branch_smooth_short_bough_lowfrag_B` 与 `V59_lsys_branch_smooth_short_bough_compact_D` 最稳，仍保持 short-bough 读感且不明显 blob；
  - `dense_C` 更密，但枝条堆叠风险更高，不优先上远端。
- 下一步：只跑 V59 B/D textured GLB。远端仍只用 `a100-2` GPU 4/5，最多两卡；GLB 拉回后做 post-GLB metrics 和白底 zoom。若 V59 GLB 解决 V58 的锯齿/塑料木纹，即可考虑替换主实验 L-system ours；否则以 V58/V59 作为失败边界，下一轮需考虑材质/渲染或 guide 侧方案，而不是继续盲目几何平滑。

### 7.21 2026-05-12 corrected V67B 主实验收束状态

- 根据用户最新判断，L-system 的“多尖刺/密度深度”版本已可接受，本轮停止盲目扩张 V61/V62 远端搜索，转为主实验收束。
- 当前四类主实验 manifest 固定为：
  - SC：`SC_baseline_tree_canopy` vs `SC_ours_V32_balanced_canopy_D`
  - L-system：`LSystem_baseline_OBJ_neutral_upright` vs `LSystem_ours_V67_tapered_dense_B`
  - DLA/frontier：`DLA_baseline_cluster` vs `DLA_ours_V8_lace_reef_coral_A`
  - IFS/transform：`IFS_baseline_matched_branch_tree` vs `IFS_ours_V21_branch_tree_natural_bark`
- 关键修正：
  - IFS 行不再使用 pyrite，pyrite 只服务 transform/lattice/crystal story；
  - DLA/frontier 行使用复杂 coral case，不再使用语义不明对象；
  - 传统 L-system baseline 使用 upright/neutral OBJ render，避免歪斜呈现。
- 主要输出：
  - manifest：`results/main_experiment_case_metrics_20260511/main_experiment_traditional_vs_ours_manifest_corrected_V67B_20260512.json`
  - 白底 render：`visuals/main_experiment_traditional_vs_ours_white_zoom_corrected_V67B_20260512/`
  - 论文矩阵图：`paper_siga/figures/main_experiment_traditional_vs_ours_white_zoom_matrix_corrected_V67B_20260512.png`
  - 论文指标表：`paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`
  - 状态文档：`docs/evaluation/main_experiment_convergence_corrected_V67B_status_zh_20260512.md`
- Metrics 结论：
  - DLA ours V8：surface r0/r1 均单连通，视觉也最干净；
  - SC/IFS ours：r0 有少量 texture-export/薄片小岛，r1 单连通，welded component 为 1；
  - L-system V67：视觉达到当前收束要求，faces 75,528，但 exact r0 被细尖刺和小岛严厉惩罚（`components_r0=107, LCR_r0=0.979`），r1 单连通；正文必须明确这个 caveat，不能声称 watertight 或 strict r0 topology solved。
- 下一步：
  - 局部 patch `paper_siga/main.tex`，用 corrected V67B 图表替换旧 V24/V25 one-to-one 段落；
  - 保留用户刻意留下的中文注释，不做全局重写；
  - 编译 paper_siga，成功后推送 Overleaf。

### 7.22 2026-05-12 IFS/transform 行递归性修正：V21 -> V63C，主图改为 4x4 单层 zoom

- 用户指出 IFS 行 ours 图递归性不明显，且叶片/块状结构遮挡层级。已做同版式 QA：
  - V23 true-IFS：`IFS_ours_V23_fractal_tree_branch_copy` 机制最匹配，但 4x4 主图中仍主要读成块状重复端部，递归分叉视觉不够稳定；
  - V59 lowfrag / dense：V59 lowfrag 太稀，V59 dense OBJ 有竹状递归读感但未 textured GLB，且 zoom 仍容易落到单枝条；
  - V63 B/C textured GLB：`V63_lsys_branch_balanced_fan_C` 视觉最好，overview 和 zoom 均能读出多层分叉，且无叶片遮挡。
- 当前主图候选固定为：
  - SC：`SC_baseline_tree_canopy` vs `SC_ours_V32_balanced_canopy_D`
  - L-system：`LSystem_baseline_OBJ_neutral_upright` vs `LSystem_ours_V67_tapered_dense_B`
  - DLA/frontier：`DLA_baseline_cluster` vs `DLA_ours_V8_lace_reef_coral_A`
  - IFS/transform branch target：`IFS_baseline_matched_branch_tree` vs `RecursiveBranch_ours_V63_balanced_fan_C`
- 重要 claim 边界：
  - V63C 是 L-system branch grammar 的 distributed recursive bough textured GLB，不是 formal IFS operator；
  - 因此正文已改为“IFS/transform branch-tree target 的 visual recursive branch stress test”，operator admission 仍只绑定 V21/V23 的 lattice/radial/pyrite/transform-copy evidence；
  - 不允许在 caption 或正文中写成 “V63C 证明 IFS branch operator admitted”。
- 已完成代码/文档改动：
  - `scripts/figures/render_main_experiment_upright_4x4_zoom_20260512.py` 增加 `--ifs-ours` 候选开关，加入 `v63_distributed_dense_B` 和 `v63_balanced_fan_C`；
  - `scripts/figures/compose_main_experiment_upright_4x4_zoom_from_manifest_20260512.py` 左侧 label 区加宽，避免 `Space colonization` 被裁；
  - `paper_siga/main.tex` 局部替换主实验图为 `figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.png`，图注改为 4x4、单层 zoom、灰框、无列文字，并保守说明 IFS/transform row 的 claim 边界；
  - `paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex` 将 IFS/transform ours 更新为 V63C 指标。
- V63C 指标：
  - surface occ64：`C_r0=1, LCR_r0=1.000, C_r1=1, C_r2=1`；
  - faces `37,274`，vertices `25,291`，welded component `1`，box dim `2.071`；
  - mesh face-component count 高但 welded/surface diagnostics 单连通，正文只用 surface/welded 指标，不声称 watertight。
- 当前运行状态：
  - 高分辨率最终图正在本地 Blender 渲染：
    `paper_siga/figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.png`
    `paper_siga/figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.json`
  - 渲染完成后必须运行独立 compose 脚本（Blender 内 PIL 可能不生成最终 PNG）：
    `python3 scripts/figures/compose_main_experiment_upright_4x4_zoom_from_manifest_20260512.py --manifest paper_siga/figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.json --out paper_siga/figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.png --panel-size 560`
  - 然后打开最终 PNG 做肉眼 QA：4 行 x 4 panels、只有左侧行名、无列标题、灰色 callout 框、所有树/分支朝上、zoom 聚焦递归区。
- 完成门槛：
  - `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` 通过；
  - grep log 无 fatal/missing figure/undefined citation-reference；
  - 只 stage 相关文件：主图 PNG/JSON、指标表、`main.tex`、两个 figure scripts、本文档；
  - commit 后 `git push overleaf HEAD:master`。

### 7.23 2026-05-12 V63C/4x4 主实验已推送 Overleaf，远端新增 figure 占位已最小修复

- Overleaf 在本轮提交前从 `5e00ee2` 前进到 `b2f6148`，新增：
  - `figures/natural_recursive_structures_fourpanel.png`
  - `figures/personal/sparse_latent.pdf`
  - `main.tex` 若干修改。
- 为避免覆盖用户/Overleaf 侧改动，本轮没有强推旧分支；新建临时 worktree：
  - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/.worktrees/paper_siga_upright_v63c_20260512`
  - 分支：`codex/main-experiment-upright-v63c-20260512`
  - 基底：最新 `overleaf/master` (`b2f6148`)。
- 已在该最新基底上重放 V63C/4x4 主实验补丁并提交：
  - commit：`280d6e1b895de224ec2e2c4849b83f09800e9044`
  - message：`Update main comparison figure layout`
  - push：`git push overleaf HEAD:master` 已成功，Overleaf `master` 从 `b2f6148` 快进到 `280d6e1`。
- 推送内容：
  - `paper_siga/main.tex`：
    - 主实验比较图改为 `figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.png`；
    - caption/text 改为 4x4、single-level zoom、gray rectangles、无列文字；
    - IFS/transform 行明确为 branch-tree target 的 visual stress test，不把 V63C 写成 admitted IFS operator；
    - 最小修复 Overleaf 新增的嵌套 `figure` 占位块，删除 `Enter Caption` / `fig:placeholder`，保留 `figures/natural_recursive_structures_fourpanel.png` 和原 photo-credit caption 口径，只修复 `Recursive  in` 语病和 label 位置。
  - `paper_siga/figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.png`
  - `paper_siga/figures/main_experiment_traditional_vs_ours_upright_4x4_zoom_20260512.json`
  - `paper_siga/figures/main_experiment_selected_metrics_table_corrected_V67B_20260512.tex`
- 验证：
  - 在临时 worktree 跑 `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`，退出码 `0`；
  - `main.pdf` 生成，大小约 `44MB`，最终日志写出 `main.pdf (50 pages, 45984570 bytes)`；
  - grep `main.log` 未发现 `undefined`、`Citation.*undefined`、`Reference.*undefined`、`LaTeX Error`、`Fatal error`、`File .* not found`、`Emergency stop`、`Not in outer par mode`、`Enter Caption`、`fig:placeholder`；
  - 日志中只剩已有 BibTeX metadata warning、underfull/overfull、float-only page 等非 fatal 排版警告。
- 本地 `paper_siga` 原工作区仍有大量未提交/未跟踪文件和用户/其他 agent 改动，已执行 `git reset` 清空 index，未清理或回滚这些内容。后续若继续从原 `paper_siga` 工作区改正文，应先 fetch 最新 Overleaf，并手动处理 `overleaf/master` 与本地脏改的差异，避免覆盖用户中文或 Overleaf 侧新增图。
