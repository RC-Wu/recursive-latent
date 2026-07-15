# Gen-3D Baseline 论文整合 QA（2026-05-10）

本文档只针对当前 gen-3D baseline 证据能否进入论文主文做 QA。依据文件包括 `paper_siga/main.tex`、两份 evaluation 状态文档、`gen3d_baseline_summary_table_20260510.csv`，以及两张最新 contact/zoom figure。未修改 `main.tex` 或任何图片。

## 1. 当前 gen-3D baseline 能支撑与不能支撑的 claim

### 可以支撑的 claim

1. **ordinary one-shot 3D generator 不等价于递归执行器。**
   - Trellis2 one-shot 在 vine 行的 occupancy LCR 为 `1.000`，说明它可以生成某些连通、可视上可接受的单体对象。
   - 但 pyrite one-shot 的 occupancy LCR 只有 `0.127`、coral one-shot 为 `0.600`，对应 occupancy components 分别为 `17` 和 `30`。这可以支撑“普通 one-shot 生成器不保证目标递归结构的附着性和局部重复结构”的 claim。
   - 严谨写法应强调“does not guarantee / is not designed to enforce”，不要写成 Trellis2 普遍失败或质量低。

2. **naive latent-copy 和 mesh-space copy-paste 是合理负例。**
   - latent-copy 三行都没有 typed handles、attachment feasibility、projection 或 re-encoding。vine `LCR=0.689`、pyrite `0.102`，coral 虽然 `0.824`，但 mesh face components 高达 `2208`，且只是 `copy_shift_upper_z` 控制。
   - mesh-space generated-root baseline 更强地暴露 copy-paste 碎片问题：vine raw face components `101699`、pyrite `173575`；pyrite occupancy LCR 仅 `0.033`。
   - 这组结果可以支撑“直接复用生成资产并做显式 S/R/T 递归，仍不能形成可继续作为 grammar state 使用的 attached support”。

3. **PS-RSLG 在当前选择的 pyrite/coral/vine 候选上提供了更强的 connected recursive asset evidence。**
   - pyrite strict visual matched textured GLB：occupancy components `1`，LCR `1.000`。
   - coral strict visual matched textured GLB：occupancy components `1`，LCR `1.000`。
   - vine 应使用 stronger vine stage5 reference：occupancy components `4`，LCR `0.999`。当前 strict `ours_vine` 行 LCR 只有 `0.072`，不能作为主文 vine 正向 claim 的依据。
   - 因此主文可写“selected PS-RSLG rows retain a dominant connected asset”，其中 vine 必须明确是 stronger stage-5 candidate，而不是 strict-matched weak row。

4. **Hunyuan3D 可以作为 audited planned baseline，而不能混入数值比较。**
   - 当前 a100-2 项目环境没有 Hunyuan repo、`hy3dgen` package 或 cached weights，texture pipeline 还需要额外 extension build。
   - 这可以支撑“we audited Hunyuan3D as a planned secondary baseline and report why it is not included numerically”，但不能支撑任何 Hunyuan 性能结论。

5. **figure 可以作为“诊断性视觉对比”支撑，而不是最终审美质量证据。**
   - contact sheet 清楚显示 one-shot、latent-copy、mesh-copy 与 PS-RSLG 的形态差异和失败模式。
   - zoom sheet 可支持“局部 recursive detail 的质性诊断方向”，但由于白色 mask/背景混叠和裁切问题，不能独立支撑强 effective-resolution claim。

### 不能支撑的 claim

1. **不能声称 ordinary 3D generators 普遍无法生成递归结构。**
   - vine one-shot `LCR=1.000`，且视觉上能生成复杂对象。证据只支持“不能可靠保证指定递归附着和可复用 grammar state”。

2. **不能声称 PS-RSLG 在所有 matched cases 上优于 baseline。**
   - strict `ours_vine` 行是负面或待替换状态，CSV 中 status 为 `needs_vine_candidate_swap_or_QA`。主文若使用 vine 正向结论，必须使用 stronger vine stage5 row，并解释其不是 strict row。

3. **不能把 occupancy LCR 写成 watertight topology、mesh manifold、真实物理连接或语义递归正确性。**
   - CSV 同时显示很多 raw mesh components 很高。occupancy LCR 是 surface/occupancy proxy，应写为 structural proxy 或 dominant connected support evidence。

4. **不能声称 Hunyuan3D baseline 已完成、失败、或被本文方法超过。**
   - 当前仅有环境可行性 audit，没有输出资产和 metrics。

5. **不能把 effective-resolution 写成已量化完成。**
   - `main.tex` 当前写法中“final quantitative language still requires terminal-detail counts, local feature scale, face/GLB growth, and estimated full-object high-resolution blow-up curve”是正确的 gate。
   - 两级 camera zoom 只能支持 qualitative direction。

6. **不能把 texture/PBR 质量作为结构性贡献证据。**
   - 当前 material quality 明显 category-dependent，且 zoom 图中有严重白色缺失/alpha 或背景 mask 混叠。texture export 只能写作 compatibility/export evidence。

## 2. 实验段落中如何严谨写 Hunyuan blocked planned baseline

建议主文保留 Hunyuan3D 段落，但必须满足以下约束：

1. **定位为 audited planned / secondary baseline。**
   - 不写入 quantitative table 的 method rows，除非表格有显式 `planned/blocked` status 列。
   - 不报告任何 Hunyuan LCR、component、视觉胜负或失败案例。

2. **blocked 原因写成环境和复现状态，而不是模型能力评价。**
   - 可写：当前 a100-2 项目环境未发现 Hunyuan3D/HY3D repo、`hy3dgen` package、cached weights 或结果目录；shape+texture pipeline 还需要安装依赖、下载权重、编译 texture 相关 extension。
   - 不写：Hunyuan3D 不可用、效果差、跑不动、不能做 text-to-3D。后两者需要实际复现或官方配置验证。

3. **text-to-3D 要单独标风险。**
   - 状态文档显示官方 API text branch 依赖额外 T2I worker，当前源码默认并非开箱即用 native text-to-3D。
   - 因此可写 `Hunyuan3D text-to-3D remains blocked-risk under the current audit; image-to-3D is the planned comparable setting after installation`。

4. **建议论文段落写法。**

```tex
Hunyuan3D 2.0 was audited as a secondary planned baseline rather than mixed into the quantitative comparison. In the current a100-2 project environment we found no reusable Hunyuan3D repository, hy3dgen package, cached weights, or prior outputs, and the textured pipeline requires additional dependency and extension installation. We therefore report the audit status and resource plan, while the numerical ordinary-generator comparison uses TRELLIS.2, whose checkpoint cache and prior outputs are already present. This status is an environment and reproducibility constraint, not a claim about Hunyuan3D quality.
```

当前 `main.tex` 的 Hunyuan 段落总体方向正确；建议补一句 “not a claim about model quality” 或等价表述，避免 reviewer 读成未跑模型的负面结论。

## 3. 当前 figure 的视觉问题和建议

### `gen3d_baseline_texture_fair_clean_20260510.png`

主要问题：

1. **layout 有明显空洞。**
   - 3 行 x 4 列布局中，mesh-space generated-root 的 coral 缺失，对应第三列第三行为空；视觉上容易被误读为排版错误。
   - 建议在图内或 caption/table 中显式标 `missing` / `not run`，或者将该列改成只覆盖 vine/pyrite 的 two-row inset。

2. **尺度和裁切不统一。**
   - vine one-shot 占据左上大面积平面，和其他对象尺度差异很大。
   - bottom row 的 PS-RSLG vine/pyrite/coral 被底部裁切，尤其 (i)(j)(l) 接近或超过图边界，影响主文可读性。

3. **部分 baseline 过淡或近乎不可见。**
   - (c)、(g) 几乎是点状残片，在白底上可见性很低。作为失败证据是有用的，但主文 figure 需要让失败模式可读。
   - 建议给碎片行使用统一的 faint gray bounding box 或局部放大 inset；如果不想加图内说明，则至少在 caption 中说明“near-empty panels indicate fragmented components at the fixed camera/scale”。

4. **PS-RSLG texture/material 视觉风格和 baseline 差异较大。**
   - (d) vine 是有机棕色材料，(h) pyrite 是块状金属/晶格，(l) coral 是粉色块状结构。它们视觉上更像 selected assets，而 baseline 多为黑色/灰色或碎片。
   - 这不一定不公平，但 caption 必须强调 metrics/table 是主比较，figure 是 render diagnostic；否则 reviewer 可能认为视觉风格差异来自 material guide 而不是结构。

建议：

- 若进入主文，保留当前图作为 diagnostic contact sheet，但不要让它承担唯一 positive evidence。
- 更理想的主文版本：每个 case 一行，列名在 caption/table 中对应；缺失 coral mesh-space panel 明确标 `not available`；统一对象在 cell 内的最大边界框尺寸；避免 bottom cropping。
- 如果图内不能加文字，至少在 caption 中说明 labels (a)-(l) 与 table rows 的映射方式。

### `gen3d_baseline_texture_fair_zoom_clean_20260510.png`

主要问题：

1. **白色缺失/alpha/mask artifact 非常明显。**
   - (d)、(h)、(j)、(l) 中大片白色区域切入模型表面，像 texture alpha 或 background mask 错误。这个问题会削弱“local detail quality”主张。

2. **zoom 区域的语义不够一致。**
   - 有些 panel 是细线/碎片的局部，有些是大块材质表面或体素块。它能诊断失败模式，但不适合作为严格 matched zoom 比较。

3. **部分 zoom panel 过空。**
   - (c)、(g) 主要是稀疏点云/碎片，在白底上难以阅读；(k) 完全空白或近乎空白。若不说明，这会被看成渲染失败。

4. **bottom row 大面积裁切。**
   - (i)、(j)、(l) 的 zoom 对象被图边截断，(l) 尤其明显。主文中会显得未完成。

建议：

- 当前 zoom 图更适合作为 appendix diagnostic，而不是主文 strong figure。
- 如果必须留在主文，caption 应降低 claim：`first qualitative zoom diagnostic`，并明确“white holes and missing panels are render/asset diagnostics rather than hidden successes”。
- 下一版建议重渲染：固定每个 cell 的 zoom box、用非白背景或浅灰背景区分 alpha/mask、统一 zoom ratio、避免对象贴边裁切、为空缺 panel 加 `missing` 状态。

## 4. 表格中哪些行适合主文，哪些适合附录

### 适合主文的行

主文表格应该保留能直接支撑核心 claim、且不会引发过度解释的行：

1. `vine / Trellis2 one-shot / image-conditioned one-shot`
   - 作为 ordinary generator 可生成 plausible connected object 的反例/平衡证据保留。
   - 写法：plausible one-shot but not evidence of grammar-state recursion。

2. `pyrite / Trellis2 one-shot / image-conditioned one-shot`
   - 支撑 one-shot 对非树状递归目标缺乏附着保证。

3. `coral / Trellis2 one-shot / image-conditioned one-shot`
   - 支撑 one-shot 对 frontier/accretion-like 目标的碎片风险。

4. `vine / Trellis2 trivial latent / copy_shift_upper_z`
   - 支撑 latent-copy 不能替代递归语义。

5. `pyrite / Trellis2 trivial latent / copy_shift_upper_z`
   - strongest latent-copy negative row，LCR `0.102`。

6. `coral / Trellis2 trivial latent / copy_shift_upper_z`
   - 可以保留，但 verdict 应写 `uncontrolled copy / fragmented mesh`，避免只看 `LCR=0.824` 误以为成功。

7. `vine / Mesh-space generated-root baseline / full_srt depth=2 direct merge`
   - 支撑 mesh-space direct merge 即便 occupancy proxy 不低也有极高 raw fragmentation。

8. `pyrite / Mesh-space generated-root baseline / full_srt depth=2 direct merge`
   - strongest mesh-space negative row，occupancy LCR `0.033` 且 face components `173575`。

9. `pyrite / Ours / PS-RSLG / strict_visual_matched_texture_20260510`
   - 主文正向非树状 connected recursive asset 证据。

10. `coral / Ours / PS-RSLG / strict_visual_matched_texture_20260510`
    - 主文正向 frontier/accretion-like connected recursive asset 证据。

11. `vine / Ours / PS-RSLG / stronger vine stage5 reference`
    - 主文 vine 正向结果应使用这一行，而不是 strict weak vine row。
    - 表格 caption 或 note 必须解释它是 stronger reference candidate，用于避免 over-reading weak strict row。

### 更适合附录或 status table 的行

1. `coral / Mesh-space generated-root baseline / missing`
   - 主文 compact table 可以省略，或只在 table note 中说明 mesh-space coral run missing。
   - 如果保留在主文，应有 `status` 列，否则空值会破坏表格可信度。

2. `vine / Ours / PS-RSLG / strict_visual_matched_texture_20260510`
   - 这行 status 是 `needs_vine_candidate_swap_or_QA`，LCR `0.072`，不能与 pyrite/coral strict rows 一起作为 positive row。
   - 适合 appendix 的 candidate-screen/status table，用来透明说明为什么主文 vine 换成 stage5 reference。

3. 所有只说明 asset path、source path 或 install feasibility 的 Hunyuan rows。
   - 若未来加入，应放在 appendix planned-baseline audit table，除非实际跑出 matched outputs。

4. 过多 diagnostic metrics columns。
   - 主文保留 vertices、faces、MB、occupancy components、occupancy LCR、verdict 已足够。
   - raw mesh components、source_path、asset_path、notes 更适合 appendix，除非正文讨论 occupancy 与 mesh-connectivity 的差异。

## 5. 对 `main.tex` 当前写法的整合建议

1. `Structural Baselines and Gen-3D Comparisons` 小节目前整体方向严谨：先定义 ordinary one-shot、latent-copy、mesh-space baseline，再说明不允许使用 PS-RSLG projection/local admissibility/masked naturalization。

2. 建议保留 “one-shot can produce plausible individual objects, but does not guarantee requested recursive attachment structure” 这种平衡写法。

3. 对 vine 的句子应持续保持透明：`the vine row uses the stronger stage-5 connected candidate rather than the weak strict-matched vine row`。这个句子很重要，不建议删。

4. Hunyuan 段落建议增加“this is an environment/reproducibility status, not a model-quality comparison”。

5. `Naturalization, Export, and Effective Resolution` 中关于 effective-resolution 的 gate 是正确的；不要在 abstract/conclusion 中提前把 zoom figure 写成完成量化 claim。

## 6. 本次读取的文件

- `paper_siga/main.tex`
- `docs/evaluation/ablation_and_gen3d_status_zh_20260510.md`
- `docs/evaluation/hunyuan3d_baseline_feasibility_zh_20260510.md`
- `results/gen3d_baseline_metrics_20260510/gen3d_baseline_summary_table_20260510.csv`
- `paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex`
- `paper_siga/figures/gen3d_baseline_texture_fair_clean_20260510.png`
- `paper_siga/figures/gen3d_baseline_texture_fair_zoom_clean_20260510.png`

## 7. 最终建议

1. 主文可以使用这组 gen-3D baseline，但 claim 必须聚焦在“ordinary / trivial recursion does not guarantee attached reusable recursive state；selected PS-RSLG candidates preserve dominant connected support”。

2. Hunyuan3D 保留为 planned audited baseline，不进入数值胜负比较。

3. 当前 contact sheet 可入主文但最好标明 missing/candidate 状态；zoom sheet 建议降级为 appendix diagnostic，除非重渲染解决白色 mask、空 panel 和裁切。

4. 主文表格使用 compact rows：Trellis2 one-shot 三行、latent-copy 三行、mesh-space vine/pyrite 两行、PS-RSLG pyrite/coral 和 stronger vine stage5 三行。strict weak `ours_vine` 和 missing coral mesh-space 放附录/status table。

5. 不要把 occupancy LCR 扩写为 watertight/manifold/physical correctness；它只能作为 occupancy-primary connectedness proxy。
