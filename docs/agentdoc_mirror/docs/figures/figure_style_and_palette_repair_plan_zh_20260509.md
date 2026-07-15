# SIGA 图像风格与配色修复计划（2026-05-09）

本文只针对 `paper_siga/figures/` 的现有图像资产和附近脚本/文档给出视觉修复规则，不改图、不改代码。重点回应“图丑、配色和绘图方案需要升级”的问题：下一轮不是继续堆图，而是建立统一的 SIGA 论文图像系统。

## 1. 总体视觉原则

当前图像的问题不是单张图完全不可用，而是视觉语言混杂：方法图像 slide，metric 图像 matplotlib，mesh 图像像内部 contact sheet，texture 图像像渲染 QA。SIGA 主文必须让读者感觉所有图来自同一套设计系统。

统一目标：

- 主文图少而强：每张图只服务一个 claim，不用一张图承担 gallery、QA、ablation 和素材状态汇报。
- 正文图优先使用 PDF/vector；mesh 和 texture 图用高分辨率 PNG，但必须保持相机、背景、光照、边距一致。
- 每张图内部去掉大标题，保留短 panel label；解释交给 caption。
- 避免 UI 卡片、圆角边框、彩色大块背景、文件名式标签和状态汇报式长标题。
- 将正文图和 supplement 图的视觉等级分开：正文图只放最干净证据，弱 case 和 stress test 放 supplement。

## 2. 配色规则

### 2.1 三套颜色不能混用

1. 方法/消融色：只用于 `Direct / Final-only / Per-depth`。
   - `Direct`: `#9AA0A6` 中性灰。
   - `Final-only`: `#D55E00` 橙红。
   - `Per-depth / Ours`: `#0072B2` 深蓝。
   - 这套颜色在所有 ablation、metric、caption legend 中保持固定。

2. 操作符色：只用于 operator-only 曲线或语法说明，不与方法消融同图混用。
   - `Competition`: `#009E73` 绿。
   - `Competition+Fork`: `#CC79A7` 紫粉。
   - `Side Fork`: `#E69F00` 金橙。
   - `Portal Copy`: `#56B4E9` 天蓝。
   - `Scale Copy`: `#6B5B95` 灰紫。
   - 必须同时使用 marker 和 line style，不能只靠颜色。

3. 渲染/材质色：正文 mesh 证据优先 neutral clay / muted gray-green。
   - neutral clay: `#B9B7AE`。
   - muted green-gray: `#9EAAA0`。
   - dark cavity/shadow: `#2F3432`。
   - textured GLB 只用于 teaser 和 texture/export 图，不与 neutral geometry evidence 随意混排。

### 2.2 背景规则

- mesh render 背景用接近白色的 warm gray：`#F6F5F1` 或 `#F4F4F0`。
- 禁用纯黑背景、强渐变背景、强景深模糊、装饰性 halo、厚投影。
- ground plane 可以保留，但必须轻：matte, roughness high, shadow soft, 不抢主体。
- 同一 figure 内所有 tile 使用同一背景、相机焦距、光照方向、主体 scale 和 crop margin。

## 3. 字体、线宽与排版

沿用 `assets/paper_plot_style_recursive_growth.py` 的方向，但进一步收紧：

- 字体：Times/Nimbus/DejaVu Serif，数学字体 STIX，PDF fonttype 42。
- axis label: 7.0-7.5 pt。
- tick label: 6.2-6.5 pt。
- legend: 6.2-6.7 pt。
- panel label: 7.0 pt bold，例如 `(a)`、`(b)`，不要写完整句子标题。
- 线宽：axis 0.65 pt，曲线 1.1-1.4 pt，grid 0.4-0.5 pt 且 alpha 低于 0.2。
- 图内最小文字打印后不能低于 6 pt；如果必须低于 6 pt，说明图应该拆分或转 supplement。
- 公式必须排版为 `$N_\theta$`, `$P_\lambda$`, `$S_d$`，不要出现 ASCII 变量名。

## 4. Caption 策略

caption 要承担解释，不要把解释塞进图内。

每个 caption 建议采用三句结构：

1. Claim 句：这张图证明什么，限定在一个主张内。
2. Reading 句：读者应该比较哪些行/列/panel。
3. Caveat 句：说明口径边界，例如 occupancy support、raw mesh face connectivity、textured GLB export 分别是什么。

禁止写法：

- “current draft”、“QA”、“status”、“candidate”、“best so far”等内部生产语言。
- “proves generality”、“solves all cases”等超出证据的说法。
- 在 caption 中列太多实现细节，导致核心 claim 被淹没。

推荐术语：

- `per-depth projection`：递归 transition 内的 projection。
- `final-only cleanup`：终端清理，不等价于递归不变量。
- `occupancy connected support`：主结构 claim 的 primary proxy。
- `raw mesh face components`：export diagnostic，不是主结构指标。
- `selected textured GLB`：只表示可进入 texture/PBR export 的选例。

## 5. 当前关键图像的处理建议

### 5.1 `method_system_ps_rslg_v3_20260509.pdf`

结论：可保留为方法总图，但需要一次“信息减法”重绘。

主要问题：

- 仍像一张综合系统海报，信息密度高。
- 多个模块同时抢注意力：grammar、Trellis2 state、projection、classical coverage、texture/export。
- 如果双栏放置，图内文字很容易低于有效阅读字号。

修复规则：

- 方法总图只讲一个循环：rule proposes support/anchors -> masked Trellis2 operation -> decode/project -> re-encode -> next recursive state。
- texture/export 放到 loop 外右下角，降权为 optional output。
- classical procedural systems 不进主图，转 supplement 或正文文字。
- 颜色只保留 state 蓝灰、rule 紫/琥珀、projection 深蓝、export 灰绿四类。
- panel 内不放大标题，caption 说明 projection inside transition 是关键。

### 5.2 `depth_parameter_mesh_showcase_zoom_20260509.pdf`

结论：适合作为 same-condition behavior 图，但不应承担核心 ablation。

主要问题：

- zoom 信息有价值，但如果缺少统一裁切和短标签，会像局部素材拼贴。
- depth/parameter 的视觉变化需要与 claim 对齐，不能暗示严格单调规律。

修复规则：

- 使用固定相机、固定材质、固定 crop；zoom inset 的框线统一为 0.6 pt 中性灰。
- 行列标签只写 `d=...`、`density=...`、`same guide` 等短术语。
- caption 使用 “same-condition behavior display”，不要写 “control proves”。
- 如果主文空间紧，优先保留更简洁的 `depth_parameter_main_candidate_20260509.pdf`，zoom 版进 supplement。

### 5.3 `coral_density_extreme_texture_20260509.png`

结论：不建议直接作为主文核心图；适合 supplement 或 teaser 的边界/texture inset。

主要问题：

- texture 图天然更吸引注意，但可能掩盖 geometry claim。
- “extreme density” 容易被读者理解为失败边界或艺术效果，而不是方法证据。

修复规则：

- 如果进入正文，必须明确它是 endpoint qualitative behavior 或 texture/export example。
- 不与 neutral mesh evidence 放在同一个无说明矩阵里。
- 需要同一背景、同一曝光、同一材质/texture pipeline 说明。
- caption 明确 raw GLB topology caveat，避免被当作 connectivity 证据。

### 5.4 `projection_ablation_mesh_contact_20260509.png`

结论：这是主文最重要的结果图之一，必须从 contact sheet 升级为 claim-aligned ablation figure。

主要问题：

- 文件名和当前形式仍有 contact sheet/QA 感。
- tile 数量和标签如果过多，会削弱 direct vs final-only vs per-depth 的阅读路径。

修复规则：

- 列固定为 `Direct recursion`、`Final-only cleanup`、`Per-depth projection`。
- 行只保留最干净的 conservative vine/tree case；fork/aggressive case 转 supplement 或作为 boundary row。
- 每个 tile 去掉圆角卡片和重边框；用细分隔线和外部短标签。
- 右侧可加一列极简 diagnostic：raw comps / LCR，用小号表格式文本，不要压在 render 上。
- caption 第一句直接对齐 claim：projection 的位置改变了后续递归状态，而不是只改变终端 mesh。

### 5.5 `claim_aligned_metric_summary_20260509.png`

结论：应保留，但需要更像 paper figure，少像解释性 dashboard。

主要问题：

- 图宽很大，信息像 metric dashboard。
- 如果文字过多，会在双栏或 full-width 缩放后失去可读性。
- 需要严格区分 primary structural claim 和 export diagnostics。

修复规则：

- 拆成两层视觉：上层 primary occupancy connected support，下层 raw/welded mesh diagnostics。
- 使用灰/蓝/橙方法色，不引入新的语义颜色。
- 减少图内解释文本，把口径解释放 caption。
- 红叉/失败边界可以保留，但必须作为 boundary case，不要让它成为视觉中心。
- 如果无法在 7 pt 等效字号下读清，拆为 main summary + supplement detail。

## 6. 其他当前图像的优先级判断

优先保留并修：

- `teaser_candidate_layout_v3_20260509.png`：作为 teaser，但必须降低 breadth/generalization 语气。
- `projection_ablation_mesh_contact_20260509.png`：主结果证据，优先重排。
- `claim_aligned_metric_summary_20260509.png`：防止 reviewer 误解指标口径。
- `method_system_ps_rslg_v3_20260509.pdf`：唯一方法总图。
- `vine_stage5_guide_sweep_20260509.png`：selected texture/PBR export 证据。

建议转 supplement：

- `depth_parameter_mesh_showcase_zoom_20260509.pdf`：若主文已有简洁 depth figure。
- `coral_density_extreme_texture_20260509.png`：作为 extreme/endpoint qualitative case。
- `space_competition_depth_curves_*_20260508.pdf`：作为 token/vertices/faces growth diagnostics。
- `cache_*_texture_qa_20260509.*`：内部 QA 感强，不进主文。
- `matrix_test_one_contact_sheet.png`、`textured_glb_preview_contact_sheet.png`：素材筛选表，不进主文。

建议不作为正文图原样使用：

- 带 `contact_sheet`、`qa`、`candidate`、`draft` 的图，除非重命名并重排。
- 多类别混排但无统一相机/背景/标签体系的 gallery。
- 过暗、碎片显著、材质抢过结构的 texture 图。

## 7. 绘图与渲染实现规则

### Matplotlib 图

- 继续使用 `assets/paper_plot_style_recursive_growth.py` 作为唯一入口。
- 所有数据图同时导出 PDF 和 PNG；主文优先 include PDF。
- legend 使用论文术语，不使用 `compete_fork`、`scale_down` 等代码名。
- 多 panel 图只保留一个全局 legend。
- y 轴 offset 不要让每个 subplot 各写 `1e5/1e6`；改写入 axis label。
- bar chart 允许关键数值标注，但不要每个小柱都堆数字。

### Mesh/Texture Render

- 正文 geometry evidence 使用 neutral material；texture evidence 单独成图。
- 同一图内所有对象使用统一 light rig：large area key light + soft fill + ambient low。
- 相机固定为 3/4 view；如果需要 zoom，用 inset，不要换视角。
- 主体占 tile 高度 72-82%，上下留白一致。
- 不显示坐标轴、Blender UI、文件名、调试框。
- 阴影必须帮助读形，不制造脏背景。

## 8. 小型优先行动清单

P0：重排 `projection_ablation_mesh_contact_20260509.png`，把它从 QA/contact sheet 改成三列 ablation 主结果图。

P0：修 `claim_aligned_metric_summary_20260509.png`，把 primary occupancy claim 与 raw mesh diagnostics 分层，删除 dashboard 式解释文本。

P1：精简 `method_system_ps_rslg_v3_20260509.pdf`，只保留 PS-RSLG recursive transition loop，classical coverage 和 texture/export 降权。

P1：统一 render 背景、相机、材质规则；正文 mesh 图用 neutral material，texture 图单独说明。

P2：建立最终主文 figure whitelist，所有 `qa/contact_sheet/draft/candidate` 图若不重排就进入 supplement。

P2：更新 caption：每张图按 claim / reading / caveat 三句结构重写，避免内部生产语言和过度 claim。
