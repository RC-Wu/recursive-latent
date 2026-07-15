# Paper Figure Aesthetic Review - 2026-05-08

审阅范围：

- `paper_siga/figures/`
- `assets/paper_plot_style_recursive_growth.py`
- `assets/generate_polished_paper_figures_20260508.py`
- `docs/paper/paper_outline_method_figure_plan_zh_20260508.md`
- `docs/figures/method_system_grammar_draft_notes_20260508.md`
- `docs/visual_result_matrix_and_render_protocol_20260508.md`

约束：本文件只给审稿式审美诊断、排版建议和必要的小代码建议；不改 `main.tex`，不使用 matplotlib 生成新结果图。

## 0. 总体判断

现有图已经具备论文图雏形，但整体仍偏向“实验状态汇报”和“内部 contact sheet”，还没有形成 SIGGRAPH/ACM 风格的统一视觉系统。主要问题不是单张图不够精致，而是不同图之间的语言不一致：头图是大幅 Blender 渲染拼贴，方法图是扁平流程图位图，定量图是 matplotlib 风格，qualitative sheet 是带卡片边框的筛选表。放进两栏论文后，读者会感到这些图来自不同阶段，而不是同一篇成熟 paper。

最重要的改进目标：

1. 让头图先建立“可投稿的视觉冲击力”，而不是展示所有候选。
2. 让方法总图从“流程枚举”变成“递归状态算子”的视觉解释。
3. 让定量图统一字体、legend、子图标题和单位。
4. 让 qualitative mesh sheet 从筛选稿变成可对比的结果矩阵。
5. 让大圆环/portal 类结果成为可读的 transform-copy 证据，而不是孤立的装饰物。

## 1. 配色

### 当前问题

- 数据图配色基本采用 Okabe-Ito / Paul Tol 思路，方向正确，但语义映射还不够统一。`compete` 是蓝色、`fork_side` 是绿色、`portal` 是粉色、`scale_down` 是橙色；另一个 ablation 图里 `Per-depth` 也是蓝色、`Final-only` 也是橙色。这会让蓝色和橙色在不同图中同时代表“操作符”和“方法”，跨图阅读容易混淆。
- qualitative 图以灰底、浅绿材质为主，头图里又有深绿色 textured vine、棕色圆环、黑色 hard-surface、灰色 arch。颜色没有论文级的类别体系：有些颜色代表材质，有些代表类别，有些只是渲染默认值。
- 方法图使用多个浅色块，但目前更像 keynote/slide 草图。大面积淡蓝、淡绿、淡黄、淡紫没有明显的技术语义层级。

### 可执行建议

1. 把颜色分成三套，不要混用：
   - 方法/消融：`Direct` 灰、`Final-only` 橙、`Per-depth / Ours` 蓝。
   - 操作符曲线：使用蓝、绿、紫、红棕、金色，但不要在同一页同时让蓝色代表 Ours。
   - 渲染图：主图尽量使用统一 neutral clay / muted green-gray；只有 textured GLB 作为少数高亮。
2. 对于所有数据图，保留 colorblind-safe 色板，但用线型和 marker 作为冗余编码；不要只靠颜色区分。
3. 对 qualitative render，建议主矩阵统一为 neutral material；textured render 只出现在头图和一个 texture appendix/secondary figure 中。
4. 方法总图建议只保留三类颜色：
   - state / latent：浅蓝灰；
   - grammar / rule：浅紫或浅琥珀；
   - projection / feedback：高亮蓝或深青；
   - texture/export：低优先级灰绿，放在 loop 外。
5. 避免每个 box 都有不同 pastel 填色。SIGGRAPH/ACM 方法图更需要清晰信息架构，不需要像海报一样彩色。

### 小代码建议

`assets/paper_plot_style_recursive_growth.py` 可以增加语义分离，避免 `OPERATOR_COLORS` 和 `METHOD_COLORS` 共享核心蓝/橙语义：

```python
# Keep ablation colors reserved across all figures.
METHOD_COLORS = {
    "Direct": "#9AA0A6",
    "Final-only": "#D55E00",
    "Per-depth": "#0072B2",
}

# Use a distinct operator palette in operator-only plots.
OPERATOR_COLORS = {
    "compete": "#009E73",
    "compete_fork": "#CC79A7",
    "fork_side": "#E69F00",
    "portal": "#56B4E9",
    "scale_down": "#6B5B95",
}
```

## 2. 字体

### 当前问题

- 样式脚本中使用 `DejaVu Sans`，字号为 7 左右。两栏论文中还可以接受，但与 ACM/SIGGRAPH 常见正文气质不完全一致；如果 `main.tex` 使用 ACM 模板，图内 sans 字体会显得偏工具化。
- 方法总图标题巨大，正文 box 文字密集，缩到双栏宽度后可读性会明显下降。
- 头图和 contact sheet 的标签字体像默认 PIL/系统字体，大小和边距不统一。
- 数据图中的 `(a) ...` 标题放在图内且字号较大，像幻灯片标题；正式论文更适合把简短 panel label 留在图内，把解释放到 caption。

### 可执行建议

1. 数据图采用与论文更接近的 serif 或 ACM 兼容字体：
   - 首选：`Times New Roman`, `Times`, `Nimbus Roman`, `DejaVu Serif`。
   - 如果保留 sans，必须全论文所有图都统一，不能只有方法图和定量图不同。
2. 图内文本层级建议：
   - axis label：7.0-7.5 pt；
   - tick label：6.2-6.5 pt；
   - legend：6.2-6.7 pt；
   - panel label：7.0 pt bold；
   - 不要有大标题，标题交给 caption。
3. 方法总图如果放 full-width，图内最小文字不要低于 7 pt 等效打印字号；如果放 single-column，应删掉 bottom coverage 和 evidence strip。
4. qualitative sheet 的 tile label 只保留短标签，例如 `Vine, d=5, compete`；不要用文件名式 snake_case。
5. 所有公式必须 typeset，不要出现 `N_theta`, `P_lambda`, `S_d` 这类 ASCII 形式。

### 小代码建议

```python
mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "axes.titlesize": 7.2,
    "axes.labelsize": 7.2,
    "xtick.labelsize": 6.3,
    "ytick.labelsize": 6.3,
    "legend.fontsize": 6.4,
})
```

## 3. Legend

### 当前问题

- `space_competition_depth_curves_compact_20260508.png` 的 legend 横跨顶部，视觉上很清楚，但占用太多垂直空间；如果 full-width 放入论文，顶部 legend 和第一行子图距离偏大。
- `projection_ablation_lcr_components_20260508.png` 的 legend 位于图顶，间距尚可，但 panel title 太大，legend 和标题竞争注意力。
- 操作符名仍是代码名：`compete_fork`, `fork_side`, `scale_down`。这在审稿人眼中像实现细节，不像论文术语。
- 同一 figure 内 legend 用 marker+line，数据点可辨；但在灰度打印中 `portal` 的浅粉虚线和 `scale_down` 的橙色短划线区分度可能不足。

### 可执行建议

1. 把 legend 文案改成论文术语：
   - `compete` -> `Competition`
   - `compete_fork` -> `Competition+Fork`
   - `fork_side` -> `Side Fork`
   - `portal` -> `Portal Copy`
   - `scale_down` -> `Scale Copy`
2. 多 panel 曲线图使用一个全局 legend，但压缩到一行或放到右上角空白区域；不要让 legend 变成第一视觉中心。
3. 对 ablation 图，legend 文案保留 `Direct`, `Final-only`, `Per-depth`，但在 caption 中说明 `Per-depth` 是 PS-RSLG 的关键设置。
4. 给每条曲线设置更强的 marker 频率和线型差异；`portal` 可用 diamond dotted，`scale_down` 可用 plus dash-dot，但线宽需要略增。
5. 如果某个 subplot 缺少某些 operator，不要让 legend 暗示所有 case 都有完整曲线；caption 或 panel footnote 说明 missing operators due to unavailable/stalled cases。

### 小代码建议

```python
DISPLAY_LABELS = {
    "compete": "Competition",
    "compete_fork": "Competition+Fork",
    "fork_side": "Side Fork",
    "portal": "Portal Copy",
    "scale_down": "Scale Copy",
}

label=DISPLAY_LABELS.get(op, op)
```

## 4. Subplot 布局

### 当前问题

- `space_competition_depth_curves_compact_20260508.png` 是 3x3 布局，信息完整，但打印后每个 panel 会比较小。y 轴科学计数法 `1e5`、`1e6` 分散在各 panel 左上角，视觉上略乱。
- 三行指标 `tokens / vertices / faces` 和三列类别 `Vine / Tree / Porous` 的布局符合矩阵逻辑，但每个 y 轴范围不同，读者比较趋势容易，比较绝对值不直观。
- `projection_ablation_lcr_components_20260508.png` 是 1x2 full-width 候选，叙事更强；但 x tick 旋转过大，bar 之间有一些空。
- 单指标版本 `space_competition_depth_curves_*` 可能比 3x3 更适合正文；3x3 适合 appendix 或 full-width analysis figure。

### 可执行建议

1. 正文推荐两张图而不是一张拥挤大矩阵：
   - Fig A：projection ablation，1x2，证明 per-depth projection。
   - Fig B：space competition depth curves，建议只展示 `tokens` 或 `faces` 的 1x3，剩余指标放 appendix。
2. 如果保留 3x3 full-width：
   - 只在最左列显示 y label；
   - 只在最底行显示 x label；
   - 去掉每个 panel 独立的 `1e5/1e6` offset，改成 y label 中写 `Vertices (x10^5)` / `Faces (x10^6)`；
   - 行标签可以放在图左侧外部，列标签放顶部。
3. `projection_ablation` 的两个 panel 不需要完整句子标题，改成：
   - `(a) Connected mass`
   - `(b) Fragment count`
   具体含义放 caption。
4. bar chart 建议加轻量数值标注，尤其 log count panel 可标注 `1`, `2`, `10`, `24`, `2.0k` 等关键数量级。
5. 统一 `fig.subplots_adjust` 或改用 `constrained_layout=False` + 手工布局；现在有些图顶部 legend 的边界依赖 `bbox_to_anchor=(0.5, 1.0)`，导出 PDF 后容易贴边。

## 5. Qualitative Mesh Sheet

### 当前问题

- `mesh_based_visual_status_contact_sheet_refined.png` 的 2x3 sheet 仍然像内部对比图：每个 tile 有圆角卡片、边框、标题，且有明显不同的 crop 和留白。
- top row 是 traditional baselines，bottom row 是 ours，但图中没有明确的视觉分隔或列对齐语义。审稿人可能会误读为 6 个同等结果，而不是 baseline vs method。
- `matrix_test_one_contact_sheet.png` 使用文件名标签，tile 很密，适合作为筛选表，不适合作为正文 qualitative matrix。
- `textured_glb_preview_contact_sheet.png` 的白底、label strip 和非统一视角使它更像素材预览；部分 textured 结果有碎片和透明感，直接进入正文会削弱方法可信度。

### 可执行建议

1. 正文 qualitative matrix 应重新定义为“结果矩阵”，不是 contact sheet：
   - 行：category，例如 Vine/Root, Tree/Bush, Porous, Transform/Portal。
   - 列：operator 或 depth，例如 Root, d=1, d=3, d=5 / Competition, Fork, Portal。
2. 去掉圆角卡片和边框。SIGGRAPH 风格通常用干净的图像网格、细分隔线和外部短标签，而不是 UI card。
3. 保持所有 tile：
   - 同一 camera；
   - 同一 resolution；
   - 同一 ground plane；
   - 同一 material；
   - 同一 crop margin。
4. 只保留 4-8 个最佳结果进入正文；30+ 矩阵可放 appendix 或 supplemental。正文图宁可少而强。
5. 对 baseline vs ours，建议使用列结构：
   - `Procedural baseline`
   - `Direct recursive`
   - `Final-only projection`
   - `Per-depth projection`
   这样 qualitative 图能直接支撑方法主张。
6. textured 结果不能和 neutral geometry 随意混排。若必须混排，caption 明确说明 textured 是 appearance path，neutral 是 geometry evidence。
7. 对孔洞、碎片、过暗结果不要在主图用大面积展示；可以作为 limitation 或 stress-test row。

### 建议正文候选

- 头图/teaser：使用 `head_figure_textured_non_tree_draft_20260508.png` 的思路，但需要重排和筛选。
- 方法/质量对比：使用 `mesh_based_visual_status_contact_sheet_refined.png` 中 bottom row 的 tree/vine textured 作为 inset，而不是原样作为正文图。
- 结果矩阵：基于 `matrix_test_one_contact_sheet.png` 重做 4x4 或 4x6，全部使用短论文标签。

## 6. 方法总图

### 当前问题

`method_system_grammar_draft_v2_20260508.png` 信息完整，但目前最大问题是“所有东西都在一张图里”。它同时承担：

- 方法 pipeline；
- 状态变量定义；
- grammar rule；
- projection loop；
- texture/PBR branch；
- classical systems coverage；
- core equations；
- evidence slots。

这对于草稿很好，但对于 SIGGRAPH/ACM 正文图太重。缩放后底部两块文字和 evidence strip 会不可读，顶部大标题也浪费版面。图内标题和 caption 重复，而且使用 ASCII formulas，降低论文质感。

### 可执行建议

1. 正文方法图只保留一个核心叙事：`S_d -> Rule/Merge -> Decode -> Projection -> Re-encode -> S_{d+1}`。
2. 把 texture/PBR export 画成 loop 之外的 final branch，不要让它看起来参与每一步递归。
3. 把 classical systems coverage 移到第二张小图、appendix figure 或 table；不要塞进主方法总图。
4. 把 core equations 移到正文公式或 caption，不要作为大框占图。
5. 加 2-3 个真实 visual inset：
   - root asset / sparse state；
   - raw decoded mesh with fragments；
   - projected mesh / final render。
   这会让方法图从抽象流程图变成 graphics paper figure。
6. 使用更少的 box 和更粗的主 loop。审稿人第一眼必须看懂：projection 是递归状态转移的一部分，不是最后清理。
7. 所有数学符号用 LaTeX 渲染：
   - `S_d`
   - `N_\theta`
   - `P_\lambda`
   - `E_\theta`
   - `D_\theta`
8. 输出必须是 vector PDF 或至少 2x/3x 分辨率 PNG；当前 bitmap 可以作为草图，不建议作为 final。

### 建议结构

```text
Root mesh/image
   -> Sparse state S_d
   -> Typed grammar rule r_d
   -> Sparse proposal + occupancy competition
   -> Masked local naturalization
   -> Decode mesh
   -> Projection / component pruning
   -> Re-encode S_{d+1}
   -> feedback loop

Stable final mesh
   -> optional Texture/PBR export
```

## 7. 头图与大圆环

### 当前问题

`head_figure_draft_4cat_20260508.png` 的横向 teaser 太扁，左侧 vine 很强，后三个 tile 面积小且留白大。它读起来像四个不等权的 thumbnails，而不是经过设计的 teaser。`Porous stress` 的块状结果和 `Transform/portal` 的重复树 tile 会拉低第一印象。

`head_figure_textured_non_tree_draft_20260508.png` 更有 SIGGRAPH teaser 潜力，因为它有 2x2 大图、textured vine、crown/ornament portal、hard-surface、architectural arch。但问题也明显：

- 每个 tile 左右有浅灰竖条，像裁剪残留，不像有意设计。
- 大圆环/crown portal 位于右上，造型有潜力，但中心结构有碎片，轮廓复杂，缺少局部放大和语义说明。
- hard-surface module 太黑，细节压在一起，读者难以判断这是失败、风格化还是结构复杂。
- architectural arch portal 的形体可读性不足，右侧褐色/灰色区域混杂，像破损扫描。
- 四个 tile 的材质、背景和光照差异较大，整体像不同来源素材拼贴。

### 头图改进清单

1. 推荐主 teaser 改成 2x2 或 1+3 布局，不建议继续使用 2240x676 超宽条。
2. 保留 vine/root 作为最大主视觉；它是当前最有冲击力的结果。
3. 大圆环/portal 应作为第二主视觉，但需要重渲染：
   - 使用 orthographic front/three-quarter view，让圆环闭合轮廓清楚；
   - 居中裁剪，确保外环不要贴边；
   - 背景改为统一 off-white 或 neutral gray；
   - 去掉浅灰竖条；
   - 加一个小 detail crop，展示 portal/repetition 单元，而不是只看混乱整体；
   - 若中心碎片不能解释为递归结构，应裁掉或作为 failure 不放主图。
4. hard-surface module 如果继续使用，必须提亮材质：
   - 不用纯黑/高 roughness 黑材质；
   - 改成 matte graphite + rim light；
   - 提高曝光，保留阴影但让孔洞和外轮廓可见。
5. architectural arch portal 目前不适合作为主 teaser 大格；除非有更干净的重渲染，否则放 appendix/stress-test。
6. teaser 内标签要更短：
   - `Textured Recursive Vine`
   - `Portal Ornament`
   - `Hard-Surface Growth`
   - `Architectural Portal`
   具体技术名放 caption，不放图内长标签。
7. 不要让 textured 和 neutral 结果混得像随机材质。方案二选一：
   - geometry-first teaser：全部 neutral material，caption 说明 texture path；
   - selected-texture teaser：只有 2-3 个 textured stars，其他不放。
8. 头图要有一个视觉主次：
   - 50% 面积：best vine/root；
   - 25% 面积：大圆环/portal；
   - 25% 面积：tree/hard-surface/porous 中最清楚的两个小图。

### 大圆环专项建议

大圆环是目前最容易表达“transform-copy / portal / ornament”概念的非树结果，但需要从“复杂棕色环”变成“递归结构证据”：

1. 建议做三视图素材：
   - full ring front/iso；
   - close-up of repeated module；
   - raw/projection 或 depth progression 小 inset。
2. 外环轮廓要比内部纹理更重要。重渲染时优先保证 silhouette，必要时使用 clay material 而不是 textured brown。
3. 如果使用棕色材质，降低纹理对比和 specular，避免小洞和噪声把结构吞掉。
4. 圆环中心的碎片会严重伤害可信度。能清理则清理；不能清理就通过 crop 或选择视角让中心碎片不成为视觉焦点。
5. 在 caption 中明确它是 `portal/transform-copy ornament`，不要让读者猜它是 crown、ring、wreckage 还是失败件。

## 8. 数据图逐项建议

### `projection_ablation_lcr_components_20260508`

优点：

- 1x2 结构清楚；
- 结论直观，尤其 log fragment count panel；
- `Direct / Final-only / Per-depth` 叙事贴合 paper claim。

需改：

- panel title 改短；
- x tick 标签改成更正式的 case name；
- y label `Components (log)` 改成 `Connected components`，log scale 在 caption 或 axis annotation 说明；
- 加轻量数值标签，尤其 log panel；
- legend 保持顶部一行，但与 panel 间距压缩。

### `space_competition_depth_curves_compact_20260508`

优点：

- 3x3 矩阵很好地表达 category x metric；
- 线型和 marker 已经具备灰度可读性；
- 趋势明显，`Competition` 稳定性较强。

需改：

- 正文不建议直接用 3x3，信息太密；
- legend 文字改为论文术语；
- 科学计数法 offset 改成 axis label 单位；
- 对 Porous 只到 depth 2 的情况加 caption 说明；
- 若要强调方法主张，优先展示 `tokens` 或 `faces` 的 1x3。

### 单指标 `space_competition_depth_curves_*`

建议：

- 作为正文候选优于 3x3；
- 选择一张最能支持 claim 的指标，不要三张都放正文；
- 其余放 appendix/supplemental。

## 9. 优先级路线

### P0 - 投稿主图必须做

1. 重排 teaser：以 vine/root 和大圆环为核心，去掉弱 tile 或降级为 appendix。
2. 方法总图重画为 vector，删掉底部大段文字，只保留递归 projection loop。
3. 将 qualitative sheet 从 contact sheet 改为 uniform result matrix。
4. 数据图统一字体、legend 文案、panel label。

### P1 - 审稿观感明显提升

1. 给 projection ablation 增加数值标注和更短 panel title。
2. 将 3x3 depth curves 拆成正文 1x3 + appendix 3x3。
3. 给大圆环添加 detail crop 或 depth/projection inset。
4. 建立统一 tile label 字典，避免文件名进入论文图。

### P2 - 后续 polish

1. 为所有 Blender renders 增加统一 crop metadata。
2. 为每个 qualitative tile 保留 mesh/render provenance，但只写在 supplement metadata，不写在图内。
3. 做一次 grayscale/colorblind 检查。
4. 确认所有 final PDFs 使用 embedded fonts，避免位图文字。

## 10. 建议的最终 figure set

正文建议保留 5 类主图：

1. Teaser/head figure：精选 3-4 个强结果，vine/root + 大圆环为核心。
2. Method overview：PS-RSLG recursive projection loop，vector + real insets。
3. Projection ablation：1x2 bar chart。
4. Operator/depth analysis：1x3 line chart，展示 competition operator 稳定性。
5. Qualitative result matrix：4 category x 4 selected results，统一 Blender protocol。

Appendix/supplemental：

- 3x3 full metric curves；
- 30+ result matrix；
- textured GLB status sheet；
- failure/stress-test examples；
- full method coverage table for IFS/L-system/space-colonization/DLA/symmetry。

