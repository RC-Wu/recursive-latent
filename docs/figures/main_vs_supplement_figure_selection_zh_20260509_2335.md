# 主文图与附录图取舍建议（2026-05-09 23:35）

范围：只读 `paper_siga/main.tex`、`case_gallery_for_user_20260509`、`docs/paper/reviewer_revision_compliance_matrix_20260509_2315.md` 和当前最新视觉文件。本文不修改 LaTeX，不跑远端。

最新视觉标准以 `pure_white_rendering_protocol_zh_20260509.md` 为准：论文图、筛选图和复渲染图统一纯白背景；不要平台、不要地面、不要可见接触阴影；主文正例只用 mesh 或 textured mesh，不用点云、Matplotlib scatter、PPT/内部 contact-sheet 风格图。

## 1. 总体取舍

当前 `main.tex` 仍是工作稿形态：正文中已有 teaser、方法图、规则表、算法框、claim map、metric 图，后面又串入大量 figures-only / supplement 候选。投稿版应从“把所有证据排进去”改成“主文只保留 claim-bearing figures/tables，figures-only 页只放强视觉证据，弱例和诊断进入 supplement”。

建议主文核心图线：

1. Teaser：只展示最强的 selected mesh/textured-mesh 正例，不放 radial / hard-DLA / 弱 breadth 结果。
2. Method：保留 PS-RSLG overview，但压缩文字密度，texture/export 降权。
3. Projection：保留纯白 no-ground projection ablation，这是当前最强方法证据。
4. Metrics/baseline：保留一个小的 claim-aligned metric 或 matched baseline 表，不把 Matplotlib/dashboard 图当视觉主角。
5. Qualitative：保留 vine depth、coral depth、pyrite/crystal 或 connected scaffold 中最强的 2-3 组。
6. Texture/export：保留 latest pure-white Trellis2 textured GLB contact 或 texture QA 表之一，强调 compatibility，不当 topology 证明。

## 2. 当前 `main.tex` 中每个 figure/table 的建议

| 编号 | label / 文件 | 当前角色 | 建议 | 理由与修改方向 |
|---|---|---|---|---|
| Fig. teaser | `fig:teaser` / `teaser_candidate_layout_v3_20260509.png` | 头图 | **压缩并替换** | 旧版 breadth 太多，caption 已承认 radial/DLA 是边界。若保留头图，应换成最新纯白/mesh-textured 标准图组合：vine、coral、pyrite/lattice、connected scaffold。不要放 hard-DLA、radial、弱 cache。 |
| Fig. method overview | `fig:method-overview` / `method_system_ps_rslg_tog_draft_20260509.pdf` | 方法总图 | **保留但压缩** | 是主方法唯一总览，应该进主文；但当前仍像系统海报。建议只画 `rule proposal -> masked naturalization -> decode/project/re-encode -> next state`，texture/export 放 loop 外。 |
| Table rule families | `tab:rule-families` | 规则族表 | **保留但压缩** | 有助于说明语言对象；主文只保留 Grow/Branch/Attach/Copy 和 Split/Extrude。`Refine` 仍是 planned effective-resolution experiment，若没有数据应移附录或标为 future。 |
| Fig. algorithm box | `alg:ps-rslg-execution` | 算法框 | **压缩或移附录** | 对理解有帮助，但会占主文空间且文字密。7 页正文中建议改成短 Algorithm 或与方法图合并；详细 step list 放 supplement。 |
| Table claim map | `tab:claim-map-current` | claim 边界表 | **主文保留精简版** | 它能防止审稿人误读 topology/mesh/export。建议压缩成 4-5 行：language、projection、baseline、non-tree scaffold、texture/export。完整 claim map 放附录。 |
| Fig. claim metrics | `fig:claim-aligned-metrics` / `claim_aligned_metric_summary_20260509.png` | 指标总览 | **压缩或附录** | 是 Matplotlib/dashboard 风，违反“不要 PPT/内部状态图”的精神。主文可保留一张重绘后的小图；当前原图更适合 supplement。 |
| Fig. surface voxel | `fig:surface-voxel-connectivity` / `surface_voxel_connectivity_metric_20260509.pdf` | texture GLB 连通诊断 | **移附录** | 属于 export diagnostic，不是主视觉。主文可在 texture/export 表中引用，不需要单独占图。 |
| Fig. projection curves | `fig:projection-depth-curves` / `projection_depth_curves_20260508.pdf` | LCR 曲线 | **压缩到附录或合并** | 数据有用，但图龄较早、Matplotlib 风。主文已经有 projection ablation 图和表时，这张曲线可进 supplement。 |
| Fig. token curves | `fig:space-competition-depth-curves` | token growth 曲线 | **移附录** | 是复杂度/诊断，不是主 claim；7 页正文不应占双栏大图。 |
| Fig. SC baseline mesh | `fig:space-colonization-baseline` | 传统 mesh baseline | **移附录** | 传统 baseline 很重要，但这张 contact sheet 占版面，且是 baseline visual status。主文用 matched baseline 表更有效。 |
| Fig. traditional texture | `fig:traditional-texture-baseline` / `traditional_baseline_texture_rerun1554_20260509.pdf` | 公平 texture baseline | **主文小图或附录强图** | 价值高：证明传统方法也能走同一路 texture route，避免 strawman。若主文空间紧，放 figures-only 或 supplement，并在正文保留一句结论。 |
| Fig. result matrix | `fig:result-matrix` / `result_matrix_mesh_20260509.png` | 大结果矩阵 | **移附录，不进主文原图** | 信息量太大，颜色条和协议标签像内部 dashboard。当前不是纯白 no-ground 标准，也不是 single-claim figure。 |
| Fig. vine zoom | `fig:vine-zoom` | 多尺度 vine | **保留或 figures-only** | 能展示递归细节；但它是 programmatic PBR，不是 true Trellis2 textured GLB。主文可保留为 geometry zoom，caption 必须明确。 |
| Fig. vine depth textured | `fig:vine-depth-textured` | vine depth GLB | **主文保留** | 最强 organic / recursive depth 正例之一，mesh/textured mesh 合规。若版面紧，与 `fig:vine-stage5-guide-sweep` 二选一。 |
| Fig. vine stage5 guide sweep | `fig:vine-stage5-guide-sweep` | d=5 guide sweep | **figures-only 或附录** | 视觉强，但 guide sweep 不是 method ablation。主文若已放 vine depth，guide sweep 可放 figures-only。 |
| Fig. depth parameter main | `fig:depth-parameter-main-candidate` | same-condition behavior | **主文可保留压缩版** | 当前更像方法行为图而非 ablation。建议只保留 vine depth + coral depth 两行；density 行放 supplement。 |
| Fig. depth parameter zoom | `fig:depth-parameter-mesh-showcase-zoom` | zoom 版 behavior | **移附录** | 有价值但过密，占 0.82 页高。主文不应同时放 main candidate 和 zoom 版。 |
| Fig. connected scaffold | `fig:connected-best-expansion-textured` / `connected_scaffold_v2_hq_selected_contact_pure_white_rerun2115_20260509.png` | 最新纯白 connected scaffold | **figures-only 强候选** | 完全符合纯白 no-ground、mesh/textured-mesh 最新标准。适合两页 figures-only 里的精选视觉面板；主文正文中只引用最强行。 |
| Fig. latest textured compare | `fig:latest-textured-method-compare` / `ralph_positive_method_texture_contact_pure_white_20260509.png` | 最新 pure-white textured GLB | **figures-only 强候选，DLA 面板降权** | 最新、合规、能展示 bismuth/pyrite/coral textured GLB。但 hard-DLA 是 boundary case，不能作为正例混在主文核心。 |
| Fig. pyrite depth | `fig:pyrite-hq-depth-textured` | crystal/lattice depth | **主文小图或 figures-only** | 当前 preferred crystal/symmetry line。必须写 crystal-inspired lattice scaffold，不写物理 pyrite/clean topology。 |
| Fig. crystal guide sweep | `fig:crystal-stage4-guide-sweep` | bismuth/pyrite guide sweep | **附录或 figures-only，勿与 pyrite depth 同时大放** | guide/PBR sensitivity 证据，不是核心方法证据。若主文已有 pyrite depth，这张进 supplement。 |
| Fig. coral depth | `fig:coral-depth-textured` | coral/DLA-inspired depth | **主文保留** | 非树 connected scaffold 最强正例之一；符合 textured mesh 路线。必须避免物理 DLA 或 topology-clean 过claim。 |
| Fig. depth parameter full | `fig:depth-parameter-mesh-showcase` | 大 gallery | **移附录** | full gallery 过密，主文会像素材库。 |
| Fig. coral density | `fig:coral-density-extreme` | 参数端点 | **附录** | 可展示 fixed-stage parameter control，但视觉差异较弱且非严格单调，不做主 claim。 |
| Fig. DLA bridge smoke | `fig:dla-bridge-smoke-rerun` | hard-DLA / bridge 负例 | **附录负例** | 明确是 boundary/stress test。不能进主文正例，也不能放 teaser。 |
| Fig. projection ablation | `fig:projection-ablation-mesh` / `projection_ablation_pure_white_zoom_20260509.pdf` | projection 方法证据 | **主文保留，优先级最高** | 最新纯白、无地面、mesh render、带 zoom；直接支撑 per-depth projection inside transition。 |
| Table projection ablation | `tab:projection-ablation` | projection 数值表 | **主文保留精简版** | 与 projection 图互补。可只保留 conservative compete 两行；fork boundary 行放 supplement，避免削弱主结论。 |
| Table matched baseline | `tab:matched-structural-baseline-matrix` / `drafts/baseline_matrix_table_20260509.tex` | 公平 structural baseline | **主文短表或附录主表** | 重要结论是传统 baseline 很强，proposed 不是靠 connectivity 碾压。7 页正文可保留精简表；完整表附录。 |
| Table texture QA | `tab:texture-qa` | texture/export 诊断 | **附录或主文极简表** | 当前行数多，属于 GLB/PBR diagnostics。主文只保留 4 类 selected export + caveat；完整表放 supplement。 |

## 3. 明确违反最新标准的图

按最新用户标准，以下图不应作为主文正例原样使用：

| 图/类型 | 违反点 | 处理 |
|---|---|---|
| `teaser_candidate_layout_v3_20260509.png` | 仍混入 radial/DLA boundary 和 programmatic PBR strip；不是最新纯白 no-ground 标准；teaser 语义过宽 | 替换为纯白 selected mesh/textured mesh 头图 |
| `result_matrix_mesh_20260509.png` | 大矩阵/协议色条/状态汇报感强，像 dashboard/contact sheet；不是 single-claim paper figure | supplement，总览用途 |
| `claim_aligned_metric_summary_20260509.png` | Matplotlib/dashboard 风；文字多；不是 mesh/textured mesh 视觉证据 | 重绘为简洁 metric 图或附录 |
| `projection_depth_curves_20260508.pdf`、`space_competition_depth_curves_tokens_20260508.pdf` | Matplotlib 曲线，只能做定量/诊断；不满足 mesh/textured mesh 视觉图标准 | 附录或小图合并 |
| `space_colonization_blender_contact_sheet.png` | contact sheet 风；传统 baseline 状态图，不是最终论文视觉 | 附录；主文用表 |
| `mesh_result_selection_contact_20260509.png` | 明确是筛选沟通图，含 DROP/负例行，不能作为 paper figure | 内部筛选或附录说明，不进主文 |
| `cache_*_texture_qa_20260509.*`、`connected_best_expansion_texture_qa_20260509.png` | QA/preview/diagnostic，通常有内部状态或弱 case | 只作 supplement diagnostic |
| `dla_bridge_smoke_stage1_rerun1455_20260509.*` | hard-DLA fragmented / bridge stress test；视觉和 claim 都是负例 | 附录负例，不进正例链 |
| `traditional_baseline_texture_matched_guide_20260509.png` | 较旧 matched-guide diagnostic，和最新 rerun 结论不完全一致 | supplement sensitivity，不作为主 baseline closure |
| 所有点云、scatter、preview、Matplotlib occupancy 图 | 不符合“不要点云/matplotlib/PPT风”作为主文视觉正例 | 只能做内部诊断或附录小图 |
| 所有带平台、地面、接触阴影、灰底、卡片边框、文件名标签过多的旧 contact sheet | 违反“纯白、无地面、无阴影边界、无 PPT 风” | 用 `pure_white_*` rerun 替换 |

当前合规的最新标准图包括：

- `projection_ablation_pure_white_zoom_20260509.pdf/.png`
- `projection_ablation_pure_white_flat_contact_rerun2105_20260509.png`
- `connected_scaffold_v2_hq_selected_contact_pure_white_rerun2115_20260509.png`
- `ralph_positive_method_texture_contact_pure_white_20260509.png`
- `standard_pure_white_selected_textured_contact_v2_20260509.png`

## 4. 7 页正文 + 2 页 figures-only 排序草案

目标：正文 7 页只承载主论证；后 2 页只放强视觉/caption，不放长文本诊断。下面按 ACM/SIGA 双栏节奏估计。

### 7 页正文

| 页 | 内容 | 图表安排 |
|---|---|---|
| Page 1 | Title, abstract, intro opening, contributions | 顶部/跨栏：重做 teaser。只放 4 个强正例：vine、coral、pyrite/lattice、connected scaffold；不放 hard-DLA/radial。 |
| Page 2 | Related work + preliminaries | 无大视觉图；可保留一个很小 sparse generator state schematic，若方法图已覆盖则不放。 |
| Page 3 | Method overview + state/rules | 跨栏 `fig:method-overview` 压缩版；`tab:rule-families` 压成单栏或 4 行小表。 |
| Page 4 | Projection-stabilized execution + naturalization/projection semantics | 主文核心：`fig:projection-ablation-mesh` 跨栏；若空间紧，算法框移附录。 |
| Page 5 | Experiments: protocols, metrics, baselines | 精简 `tab:projection-ablation` 或 matched baseline short table；不要放大 dashboard metric 图。 |
| Page 6 | Qualitative selected results | `fig:vine-depth-textured` + `fig:coral-depth-textured` 组合成一个跨栏 2 行图；或用 `depth_parameter_main_candidate` 的 vine/coral 两行精简版。 |
| Page 7 | Texture/export compatibility, limitations, conclusion | 小表：texture/export QA 精简 4-6 行；正文 caveat：GLB renderability 不等于 topology proof。 |

### 2 页 figures-only

| 页 | 图排序 | 说明 |
|---|---|---|
| Figures-only Page 1 | 1. `connected_scaffold_v2_hq_selected_contact_pure_white_rerun2115_20260509.png`；2. `ralph_positive_method_texture_contact_pure_white_20260509.png` 去掉或降权 hard-DLA 面板；3. `pyrite_hq_depth_textured_showcase_20260509.pdf` | 这一页展示 selected connected scaffold 与 true textured GLB export。caption 必须写 selected、mesh/textured mesh、topology diagnostics separate。 |
| Figures-only Page 2 | 1. `vine_stage5_guide_sweep_20260509.png`；2. `traditional_baseline_texture_rerun1554_20260509.pdf`；3. `depth_parameter_main_candidate_20260509.pdf` 的压缩/局部版 | 这一页补充 guide sweep、fair texture route baseline、same-condition behavior。避免放 full result matrix。 |

## 5. 附录 / supplement 建议结构

1. Full claim map：完整 `tab:claim-map-current`。
2. Full projection ablation：保留 fork/aggressive boundary 行、曲线图和 token growth。
3. Full matched structural baseline matrix：完整 `baseline_matrix_table_20260509`、协议和 caveat。
4. Texture/PBR diagnostics：完整 `tab:texture-qa`、surface-voxel metric、GLB warnings、guide sensitivity。
5. Method behavior gallery：完整 depth/parameter gallery、zoom version、coral density sweep。
6. Negative/stress tests：hard-DLA bridge、radial/echo/fork fragmented、cache/repair QA、blocky/holed outputs。
7. Provenance/index：case gallery 路径、raw GLB/OBJ 路径、public guide source/attribution。

## 6. 下一轮执行优先级

P0：替换 teaser，不再用 `teaser_candidate_layout_v3_20260509.png` 原图。用最新纯白、无地面、mesh/textured-mesh 正例重排。

P0：主文保留 `projection_ablation_pure_white_zoom_20260509`，并把 projection 表压到 conservative compete 主线。

P0：删减主文大矩阵、QA 图、Matplotlib/dashboard 图；这些材料转 supplement。

P1：把 vine + coral depth 合成一个 clean 2-row qualitative figure；pyrite/lattice 作为小 panel 或 figures-only。

P1：把 `ralph_positive_method_texture_contact_pure_white_20260509` 中 hard-DLA 作为 boundary case 标注或移除，避免正例混淆。

P1：texture/export 只写 compatibility；所有 raw face components、surface-voxel caveat 留在表和 caption 中。

P2：完整附录整理，不要在正文依赖附录图号；正文只引用主文中真实存在的 claim-bearing figure/table。
