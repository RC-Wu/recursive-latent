# Experiment Section 重组审阅报告（2026-05-10）

范围：只审阅 `paper_siga/main.tex`、`paper_siga/figures/` 与 `paper_siga/drafts/` 中和最新 gen3D baseline、projection、naturalization、effective resolution 相关的材料。本文档不修改 `main.tex`，也不修改任何 figure/table/source 文件。

## 1. 总体判断

当前 `main.tex` 的实验部分已经从旧的 gallery/status-report 风格改成 claim-bearing 结构，但主文仍偏重，尤其是 `Structural Baselines and Gen-3D Comparisons` 与 `Naturalization, Export, and Effective Resolution` 两节把 baseline、公平性、texture export、effective resolution、selected showcase 和 claim gates 混在一起。SIGGRAPH Asia 主文应进一步收紧成一条因果链：

1. 先证明 per-depth projection 对 conservative recursive programs 是必要的。
2. 再证明 ordinary gen3D one-shot、trivial latent-copy、mesh-space generated-root recursion 不能替代 grammar-owned recursive state。
3. 再用少量 selected non-tree / coral-like connected scaffold 展示 breadth。
4. 最后把 texture/PBR 与 effective-resolution 放成兼容性和诊断性结果，而不是结构贡献。

推荐主文只承载“能支撑摘要和贡献”的 figure/table；候选筛选、guide sweep、density sweep、bridge smoke test、未闭环 naturalization/status table、弱 zoom 诊断均放 appendix 或 supplement。

## 2. 当前实验段落应如何重排

建议把第 4 节改成以下主线：

### 4.1 Tasks, Protocol, and Metrics

保留当前任务定义、occupancy-primary connectivity、raw mesh diagnostics、surface-voxel GLB diagnostics、texture/PBR export diagnostics 的协议分离。这里必须明确：occupancy LCR 不是 watertight topology，不是 manifold mesh，也不是物理生长正确性。

### 4.2 Per-Depth Projection Ablation

这是主结果一。保留 `projection_depth_curves_20260508.pdf`、`projection_ablation_pure_white_zoom_20260509.pdf` 和 `tab:projection-ablation`。但表述上要强调 conservative vine/tree competition 是 clean evidence，fork rows 是 stability-expression boundary，不能混成同等 positive result。

### 4.3 Structural Baselines Are Strong Controls

把 `baseline_matrix_table_20260509.tex` 放在这里，文字改成 fairness sanity check：classical L-system / space colonization 在 favorable tube/occupancy protocol 下本来就强，因此本文不是声称 out-connect classical procedural methods，而是证明 sparse-latent recursive execution 需要 projection-stabilized state semantics。

`space_colonization_blender_contact_sheet.png` 可保留为一个小的主文 figure 或移到 appendix；如果主文页数紧，表格已经足够，图可移 appendix。

### 4.4 Ordinary Gen3D and Trivial Recursion Controls

把当前 `Structural Baselines and Gen-3D Comparisons` 中 Trellis2 one-shot、latent-copy、mesh-space generated-root 的内容独立成小节。主文保留 `gen3d_baseline_texture_fair_clean_20260510.png` 和 `gen3d_baseline_summary_table_20260510.tex`，但文字要非常克制：

- Trellis2 one-shot can produce plausible individual objects, but does not enforce requested recursive attachment/state reuse.
- latent-copy and mesh-space copy expose failure of naive recursion without typed handles, admissibility, projection, and re-encoding.
- PS-RSLG rows are selected connected candidates, not universal wins.
- vine positive row uses the stronger stage-5 candidate; the weak strict-matched vine row must remain appendix/status.

Hunyuan3D 只写 audited planned baseline，不进入数值比较；加一句“this is an environment/reproducibility status, not a model-quality claim”。

### 4.5 Selected Connected Scaffolds and Export Compatibility

把 selected visual positives 放在一个短小节，承接 gen3D baseline 后的 breadth evidence。主文可保留 1 张 selected connected scaffold/showcase 图，最多再保留 1 张 depth showcase。推荐只留：

- `connected_scaffold_v2_hq_selected_contact_pure_white_rerun2115_20260509.png`：作为 neutral connected-scaffold visual evidence。
- `pyrite_hq_depth_textured_showcase_20260509.pdf` 或 `coral_depth_textured_showcase_rerun1640_20260509.pdf` 二选一：作为 selected PBR/depth export compatibility。

如果主文需要非树状和 organic frontier 两类都出现，则 pyrite/coral 两张都可保留，但 caption 必须限制为 connected scaffold / PBR export compatibility，不要写 physical pyrite growth 或 faithful DLA。

### 4.6 Boundaries, Naturalization Gates, and Supplement Placement

把当前 `Naturalization, Export, and Effective Resolution` 与 `Boundaries and Supplement Placement` 合并压缩。Naturalization 现在不是闭环结果，因为 `ablation_and_resolution_status_tables_20260510.tex` 显示 rule-only、no-N、weak blend 仍缺失；因此这部分应写成 claim gate 或 limitation，而不是结果小节。

## 3. 哪些 figure/table 值得进主文

### 强烈建议主文保留

1. `figures/projection_ablation_pure_white_zoom_20260509.pdf`
   - 作用：主因果证据，direct / final-only / per-depth projection 对比。
   - 条件：caption 明确 raw mesh diagnostics 与 occupancy-primary metric 分离。

2. `tab:projection-ablation`
   - 作用：支持 per-depth projection 的核心数值。
   - 条件：fork rows 标为 boundary，不作为 success 平均值。

3. `drafts/baseline_matrix_table_20260509.tex`
   - 作用：显示 classical baselines 是 strong structural controls，防止 strawman 批评。
   - 条件：不要写成本文优于 classical procedural connectivity。

4. `figures/gen3d_baseline_texture_fair_clean_20260510.png`
   - 作用：ordinary gen3D / latent-copy / mesh-space / PS-RSLG 的 visual diagnostic。
   - 条件：caption 说明 missing/near-empty panels 是 fixed protocol 下的 diagnostic，不是排版错误；避免让 material style 差异承担 claim。

5. `drafts/gen3d_baseline_summary_table_20260510.tex`
   - 作用：当前最新 gen3D baseline 的主表。
   - 条件：主文 compact table 保留 one-shot 三行、latent-copy 三行、mesh-space vine/pyrite 两行、PS-RSLG pyrite/coral + stronger vine stage5；weak strict vine 与 missing coral mesh-space 放 appendix/status。

6. `figures/connected_scaffold_v2_hq_selected_contact_pure_white_rerun2115_20260509.png`
   - 作用：neutral mesh evidence，比 textured render 更适合支持 connected scaffold readability。
   - 条件：不要叫 textured result；当前 caption 已经接近正确。

### 可主文保留但建议二选一或压缩

1. `figures/pyrite_hq_depth_textured_showcase_20260509.pdf`
   - 强项：晶格/transform-copy 非树状视觉强，适合当前主线。
   - 风险：只能说 crystal-inspired connected scaffold，不能说 physical pyrite。

2. `figures/coral_depth_textured_showcase_rerun1640_20260509.pdf`
   - 强项：organic/frontier 类 breadth；caption 已强调不是 physical DLA。
   - 风险：若和 connected scaffold contact + gen3D baseline + texture QA 同时出现，主文图太多。

3. `figures/traditional_baseline_texture_rerun1554_20260509.pdf`
   - 强项：证明 classical supports 也可进 Trellis2 texture path，避免 texture strawman。
   - 风险：它支持 protocol separation，不是核心 claim；页数紧时移 appendix，并在正文一句话引用。

4. `tab:texture-qa`
   - 强项：透明记录 GLB export compatibility。
   - 风险：17 行太长，主文不宜放完整表。建议主文只留 compact export summary，完整表进 appendix。

### 建议移到 appendix / supplement

1. `figures/gen3d_baseline_texture_fair_zoom_clean_20260510.png`
   - 原因：白色 alpha/mask artifact、空 panel、裁切问题明显。可作为 effective-resolution diagnostic，但不适合承担主文 strong claim。

2. `drafts/ablation_and_resolution_status_tables_20260510.tex`
   - 原因：这是 status/coverage table，不是 completed ablation。可放 appendix 或内部 follow-up，不应主文当结果。

3. `figures/strict_matched_pair_candidates_v2_20260510.png` 与 `strict_mode_matched_boundary_candidates_20260510.png`
   - 原因：candidate screening，不是 final evidence。

4. `figures/result_matrix_mesh_20260509.png`
   - 原因：太宽泛，容易把 weak cases 混成 success gallery。

5. guide sweeps / density sweeps / cross-guide variants：
   - `vine_stage5_guide_sweep_20260509.png`
   - `crystal_stage4_guide_sweep_20260509.png`
   - `bismuth_pyrite_crossguide_depth_rerun1755_20260509.*`
   - `coral_density_extreme_texture_rerun1900_20260509.png`
   - 原因：method behavior 或 texture sensitivity，非主因果链。

6. DLA bridge smoke / hard-DLA boundary：
   - `dla_bridge_smoke_stage1_rerun1455_20260509.pdf`
   - `dla_bridge_ablation_mesh_qa_20260509.png`
   - 原因：很适合说明 post-hoc repair 的边界，但不能作为 connected non-tree positive result。

7. `surface_voxel_connectivity_metric_20260509.pdf`
   - 原因：指标说明/diagnostic，可 appendix；主文用一句定义和表格 note 足够。

## 4. “4.7” 应该在哪里重写

如果当前编号按旧版小节对应，4.7 应重写成“Naturalization and Projection Are Not Interchangeable”或“Naturalization Claim Gate”，位置应放在 gen3D baseline 和 selected scaffold 之后、boundaries 之前。

建议重写重点：

1. 不再把 masked naturalization 写成已证明的主结果。
2. 明确 frozen sampler 是 local realization prior，不是 global topology repair。
3. 用 `drafts/ablation_and_resolution_status_tables_20260510.tex` 的事实作为内部依据：rule-only、no-N、weak blend 缺失，global-N 是 diagnostic flow/SDE row，post-hoc repair baseline 不能和 recursive projection 混为一谈。
4. 主文可写：“The current evidence supports projection-stabilized admissible state selection; naturalization remains an operator whose surface-quality benefit must be ablated separately.”
5. 删除或降级任何 “naturalization improves topology / repairs recursion / solves material quality” 的暗示。

换言之，4.7 不应该再是一个独立成功结果，而应是一个保守的 ablation-gated paragraph，服务于 claim hygiene。

## 5. “4.9 / 4.10” 如何合并与压缩

4.9 和 4.10 如果分别对应“texture/export/effective resolution”和“boundaries/supplement placement”，建议合并成一个短节：

### Suggested title

`Export Compatibility, Effective-Resolution Diagnostics, and Boundaries`

### 保留内容

- Trellis2 texture/PBR export is technically compatible with selected projected meshes。
- Export diagnostics are separate from topology metrics。
- Zoom/effective-resolution figure is preliminary qualitative diagnostic。
- Final quantitative effective-resolution claim 仍需 terminal-detail counts、local feature scale、face/GLB growth、runtime/memory、full-object high-resolution blow-up estimate。
- Aggressive fork/radial/echo/hard-DLA/bridge/cache-selected cases 是 boundary diagnostics，放 supplement。

### 删除或移出主文

- 大段列举所有 guide sweeps、candidate screens、demo prototypes。
- 完整 texture QA 长表。
- 当前 zoom 图作为主结果的强描述。
- “current paper use / candidate / smoke test / bug fixed / failed export” 等内部状态词。

合并后的节应该只有 3-5 段，主文结尾自然过渡到 Discussion and Limitations，而不是继续展开新结果。

## 6. gen3D / latent-vs-mesh 如何避免 overclaim

推荐使用以下 claim 边界：

1. 对 one-shot Trellis2：
   - 可以说：ordinary one-shot generation can synthesize plausible individual objects but does not guarantee the requested recursive attachment pattern or reusable grammar state。
   - 不要说：Trellis2 cannot generate recursive structures 或 one-shot always fails。vine one-shot 的 occupancy LCR 是 1.000，必须承认它可以生成 plausible connected object。

2. 对 latent-copy：
   - 可以说：direct sparse-latent copy is a negative control that lacks typed handles, attachment feasibility, projection, and re-encoding; it often creates fragments that are not valid future recursive state。
   - 不要说：sparse latents are bad。本文方法正是 sparse-latent grammar，失败的是 unconstrained copy/edit。

3. 对 mesh-space generated-root：
   - 可以说：mesh-space S/R/T recursion over decoded generated roots exposes copy-paste fragmentation and does not maintain grammar-readable sparse state。
   - 不要说：mesh-space procedural modeling is generally inferior。classical procedural baselines 在结构连通性上很强。

4. 对 PS-RSLG：
   - 可以说：selected PS-RSLG cases preserve a dominant connected occupancy support for pyrite/coral and a strong stage-5 vine candidate。
   - 不要说：PS-RSLG universally outperforms all baselines。当前 strict matched vine row 仍弱，seed/root variation 未闭环。

5. 对 Hunyuan3D：
   - 可以说：audited as a planned secondary baseline but not included numerically because local environment lacked repo/package/weights/results。
   - 不要说：Hunyuan3D failed 或本文优于 Hunyuan3D。

## 7. Effective-resolution 比较如何写

当前可支持的只是“visual diagnostic direction”和“proxy status”，不能写成已完成的 resolution theorem。

建议主文写法：

> The zoom panels provide a qualitative diagnostic of recursive detail under the same camera protocol. They suggest that selected PS-RSLG assets preserve local motifs inside an attached finite-depth state, whereas one-shot and trivial-copy controls either lose the requested motif or preserve it as disconnected fragments. We treat this as an effective-resolution diagnostic rather than a completed quantitative claim.

如果使用 `drafts/effective_resolution_status_table_20260510.tex` 或 `ablation_and_resolution_status_tables_20260510.tex`，只能作为 appendix status table。尤其 tree/vine 行 detail ratio 是 0.54，不能写成 universal detail superiority；可写成 smaller local feature scale / zoom efficiency proxy。

当前 `gen3d_baseline_texture_fair_zoom_clean_20260510.png` 不建议主文强用，因为白色缺失、空 panel 和裁切会削弱可信度。若必须主文使用，应降级 caption，并明确它不是 quantitative resolution evidence。

## 8. 推荐的主文 figure/table 最小集合

如果要把第 4 节压到最干净，建议主文只保留：

1. Projection ablation figure + projection ablation table。
2. Matched structural baseline matrix table。
3. Gen3D baseline contact sheet + compact gen3D baseline table。
4. One selected connected scaffold/depth/export figure。
5. Optional compact texture/export summary table，完整 QA 进 appendix。

这样主文只讲四件事：projection 必要性、公平 structural baselines、ordinary gen3D/trivial recursion 不等价、selected projected meshes 可 export/inspect。

## 9. 需要立刻避免的文字风险

1. 不要把 texture/PBR render 写成 topology evidence。
2. 不要把 occupancy/surface-voxel LCR 写成 watertight/manifold。
3. 不要把 coral/DLA-inspired 写成 physical DLA。
4. 不要把 crystal/pyrite-inspired 写成真实晶体生长模拟。
5. 不要把 Hunyuan blocked audit 写成模型失败。
6. 不要把 status table 当 completed ablation。
7. 不要把 weak strict vine row 隐藏在 positive table 里；主文若使用 vine，应说明用了 stronger stage-5 candidate。

## 10. 本次审阅依据

- `paper_siga/main.tex`
- `paper_siga/drafts/baseline_matrix_table_20260509.tex`
- `paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex`
- `paper_siga/drafts/ablation_and_resolution_status_tables_20260510.tex`
- `paper_siga/drafts/experiment_claim_metric_insert_20260509.md`
- `paper_siga/drafts/reviewer_method_results_patch_20260509.tex`
- `paper_siga/figures/gen3d_baseline_texture_fair_clean_20260510.png`
- `paper_siga/figures/gen3d_baseline_texture_fair_zoom_clean_20260510.png`
- `paper_siga/figures/connected_scaffold_v2_hq_selected_contact_pure_white_rerun2115_20260509.png`
- `paper_siga/figures/hero_multi_zoom_white_20260510.png`
- `docs/paper/gen3d_baseline_paper_integration_qa_zh_20260510.md`
- `docs/paper/paper_restructure_status_zh_20260510.md`
- `docs/paper/main_tex_todo_triage_zh_20260510.md`
