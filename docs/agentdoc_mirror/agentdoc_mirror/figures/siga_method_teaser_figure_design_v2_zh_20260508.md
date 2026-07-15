# SIGA 方法总图 / 大圆环 Teaser / 结果矩阵设计方案 v2

创建时间：2026-05-08  
写作范围：只给下一版 figure 的具体设计与制作规格；不修改 `main.tex`，不启动重型渲染，不使用 SSH。  
目标：把头图、大圆环、方法总图和 30+ 结果矩阵从“素材拼贴/流程草图”推进到可交给绘图、Blender、Slides/Figma 实现的制作 brief。

## 0. 总体视觉判断

下一版 figure set 应围绕一个主叙事组织：

> PS-RSLG 在 typed sparse latent state 上递归执行 grammar proposal、learned local naturalization、decode、projection、re-encode；per-depth projection 是稳定递归增长的核心，而不是最终清理。

因此所有图都要避免展示成“很多候选结果”。正文主图只展示最强证据：

1. 头图 / teaser：用 `vine/root` 和大圆环 `portal / transform-copy ornament` 建立第一视觉。
2. 方法总图：用单个粗反馈环解释 `S_d -> proposal -> decode -> projection -> re-encode -> S_{d+1}`。
3. 结果矩阵：用统一 Blender/Cycles 协议展示 30+ breadth，作为补充或 full-width 结果图。
4. 数据/消融图：只承担支撑论点，不和 qualitative 图抢视觉中心。

现有弱点必须在下一版解决：

- 头图不要再是超宽 contact strip。
- 方法图不要再把 coverage、equations、evidence、texture branch 全塞在同一层。
- 大圆环必须从“复杂棕色物体”变成清晰的 portal / transform-copy 证据。
- 结果矩阵必须像论文结果矩阵，而不是文件预览页。

## 1. 方法总图信息架构

### 1.1 目标读图路径

读者 5 秒内应看到：

```text
Root/source
  -> Sparse state S_d
  -> Typed grammar proposal
  -> Masked local naturalization
  -> Decode mesh
  -> Projection / admissible set
  -> Re-encode S_{d+1}
  -> feedback to the next depth
```

读者 20 秒内应理解：

- grammar rule 决定在哪里复制、分叉、竞争、portal/radial transform；
- frozen Trellis2 prior 负责 masked naturalization 和 decode/re-encode；
- projection 在每一层进入递归状态，抑制 fragments、断裂和不可渲染组件；
- texture/PBR 是最终 observable/export branch，不是递归稳定机制本体；
- classical procedural systems 是 degenerate instances，放到小角标或补充图，不占主图核心空间。

### 1.2 推荐 full-width block layout

画布建议：双栏宽 `7.0 in x 2.35-2.65 in`，vector PDF 优先；如果 Slides/Figma 输出 PNG，至少 `4200 x 1500 px`。

```text
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│ source/root  │ -> │ state S_d    │ -> │ grammar proposal │
│ image + mesh │    │ C_d,F_d,U_d  │    │ r: X -> {X_j,T_j}│
└──────────────┘    └──────┬───────┘    └────────┬─────────┘
                            │                     │
                            │                     v
                            │            ┌──────────────────┐
                            │            │ merge + masks +  │
                            │            │ occupancy compete│
                            │            └────────┬─────────┘
                            │                     v
┌─────────────────┐   ┌──────┴───────┐    ┌──────────────────┐
│ final observable│<- │ re-encode    │ <- │ projection P_lam │ <-┐
│ mesh / GLB      │   │ E_theta      │    │ admissible state │   │
└────────┬────────┘   └──────────────┘    └────────┬─────────┘   │
         │                                          v             │
         v                                 ┌──────────────────┐   │
┌─────────────────┐                        │ decode D_theta   │ --┘
│ optional texture│                        │ raw mesh proposal│
│ / PBR export    │                        └──────────────────┘
└─────────────────┘
```

更紧凑的视觉实现：

- 主环用 6 个节点即可：`S_d`、`Rule proposal`、`Merge/mask`、`N_\theta / D_\theta`、`P_\lambda`、`E_\theta(S_{d+1})`。
- `Root/source` 放在左侧输入，`Final mesh / GLB` 放在右下输出。
- `Texture/PBR export` 只从 final observable 分出一条细灰支线。
- `Classical systems covered` 不放大框；只在左下用 5 个很小 chips：`IFS`、`L-system`、`Space colonization`、`DLA`、`Symmetry`，caption 解释它们是 special cases。

### 1.3 真实 inset

方法图必须加 3 个真实图像 inset，不要全是抽象 box：

| Inset | 位置 | 内容 | 候选来源 |
|---|---|---|---|
| A | 左侧 root/source | root image + very small mesh/sparse state preview | `visuals/trellis_example_inputs_subset_20260507/04_130c2b18f1651a70f8aa15b2c99f8dba29bb943044d92871f9223bd3e989e8b1.webp` 或 public guide `tree_roots_arlington_square.png` |
| B | decode/projection 中间 | raw decoded mesh vs projected mesh 小对比 | `visuals/siga_night_20260508/contact_sheets/attached_projection_vine_d5_compare_20260508.png` 或重渲染 crop |
| C | final observable | clean final render | `visuals/paper_quality_renders_20260508/blender_tiles/vine_d5_compete_iso.png` |

Inset 规则：

- 三个 inset 不加圆角卡片；用 0.5 pt 浅灰边线即可。
- 每个 inset 下方最多 2-3 个词：`source`、`raw decode`、`projected`、`final render`。
- 不要使用文件名式标签。

### 1.4 数学和术语

图内只保留一个核心公式，放在主环下方细条：

\[
S_{d+1} =
\mathcal{E}_\theta
\circ
\mathcal{P}_{\lambda_d}
\circ
\mathcal{D}_\theta
\circ
\mathcal{N}_{\theta,\Omega_d}
\circ
\Theta_{\Pi_d}
\circ
\operatorname{Merge}
\circ
\operatorname{Prop}_{R_d^\star}(S_d).
\]

如果空间不足，压缩成：

\[
S_{d+1}=\mathcal{E}_\theta\mathcal{P}_{\lambda_d}\mathcal{D}_\theta\mathcal{N}_\theta\operatorname{Merge}\operatorname{Prop}(S_d).
\]

所有符号必须用 LaTeX 渲染，不要出现 `N_theta`、`P_lambda`、`S_d` 这类 ASCII 文本。

### 1.5 简化版 single-column block layout

如果方法图只能单栏放置，删掉 coverage chips 和大公式，采用竖向 loop：

```text
source/root
   |
S_d: typed sparse state
   |
Rule proposal + masks
   |
N_theta + D_theta
   |
P_lambda projection
   |
E_theta -> S_{d+1}
   |________ feedback ________

final mesh -> optional texture/PBR
```

单栏版只保留两个 inset：`raw decode` 和 `projected/final`。最小打印字号不得低于 7 pt。

## 2. 大圆环 teaser 的可执行构图

### 2.1 大圆环角色定位

大圆环应定义为：

> Portal / transform-copy ornament: a non-tree recursive result showing repeated transformed modules under projection-stabilized growth.

不要称作 crown、ring、arch wreckage 或 hard-surface failure。图内短标签建议：

- `Portal Ornament`
- 或 `Transform-Copy Ornament`

caption 中再写 `portal / transform-copy rule`。

### 2.2 头图首选布局：1+3 asymmetric teaser

画布建议：`7.0 in x 2.6 in` 或 `7.0 in x 2.8 in`。

```text
┌───────────────────────────────┬──────────────────────┐
│                               │  Portal Ornament     │
│                               │  large ring render   │
│   Recursive Vine / Root       ├──────────┬───────────┤
│   largest hero panel          │ Tree     │ Porous /  │
│   50-55% width                │ Growth   │ Transform │
│                               │          │ backup    │
└───────────────────────────────┴──────────┴───────────┘
```

面积分配：

- Vine/root：50-55%，最大面板，负责视觉冲击。
- 大圆环：25-30%，第二主视觉，必须比 tree/porous 更大。
- Tree 和 porous/transform backup：各 10-12%，作为 breadth，不得拉低整体质量。

标签放置：

- 每个 panel 左上角放极短白/深灰标签，半透明底条最多 18 px 高，不使用大标题。
- 推荐标签：`Recursive Vine`、`Portal Ornament`、`Tree Growth`、`Porous Stress-Test`。

### 2.3 备选布局：2x2 balanced teaser

当四个资产都达到 paper-ready 时使用：

```text
┌────────────────────┬────────────────────┐
│ Recursive Vine     │ Portal Ornament    │
├────────────────────┼────────────────────┤
│ Tree Growth        │ Porous / Crystal   │
└────────────────────┴────────────────────┘
```

要求：

- 四张都必须统一背景、光照、相机和 crop。
- 大圆环不能小于其他 panel；否则失去 transform-copy 概念价值。
- 如果 hard-surface 仍然过黑或 arch 仍然破碎，不使用 2x2。

### 2.4 大圆环单独重渲染规格

必须产出三张素材：

| 素材 | 用途 | 相机 | 画面要求 |
|---|---|---|---|
| full ring | teaser 第二主视觉 | orthographic front 或 3/4 front | 外环完整闭合，四周留 8-12% margin，中心碎片不抢视线 |
| module crop | teaser 小 inset 或方法图补充 | crop 到重复单元 | 展示 portal/repetition module，不展示无意义噪声 |
| depth/projection strip | supplement 或 caption evidence | `raw -> projected -> final` | 只用 3 个小图，证明 projection 不是最终美化 |

材质建议：

- 首选 neutral clay / muted green-gray，确保 silhouette 优先。
- 如果使用棕色/金属 texture，降低纹理对比和 specular，避免内部噪声吞掉形体。
- 不用纯黑材质；hard-surface backup 用 matte graphite + rim light。

构图检查：

- 外环边缘不能贴图边。
- 中心碎片如果无法清理，改用 3/4 视角或 crop，让其不在视觉中心。
- 圆环厚度、重复单元和入口/portal 方向要能一眼读出。
- 不要在主图里混用浅灰竖条、白底截图、不同色温 render。

### 2.5 大圆环资产候选

优先级：

1. `tree_projected_portal`  
   - 当前 render：`visuals/paper_quality_renders_20260508/blender_tiles/tree_portal_iso.png`  
   - mesh 记录：`visuals/siga_night_20260508/siga_projected_recursive_loop_0715/tree_projected_portal/latest_mesh.txt`  
   - 用途：大圆环 / portal ornament 首选。
2. `transform_portal_d3`  
   - mesh：`visuals/siga_night_20260508/selected_meshes/transform_portal_d3.obj`  
   - 用途：如果 tree portal 过碎，作为更明确的 transform-copy backup。
3. `transform_radial4_d3`  
   - mesh：`visuals/siga_night_20260508/selected_meshes/transform_radial4_d3.obj`  
   - 用途：如果 radial symmetry 比 portal 更可读，替换为 `Radial Ornament`。
4. `vine_d5_projected_portal`  
   - mesh 记录：`visuals/siga_night_20260508/siga_projected_recursive_loop_0715/vine_d5_projected_portal/latest_mesh.txt`  
   - 用途：作为 vine family 内部 transform-copy 对照，不建议同时和 vine compete 主视觉并列。

## 3. 4 个 head assets 候选和替换策略

### 3.1 Head asset A: Organic Vine / Root

首选：

- 名称：`vine_d5_projected_compete`
- render：`visuals/paper_quality_renders_20260508/blender_tiles/vine_d5_compete_iso.png`
- mesh 记录：`visuals/siga_night_20260508/siga_projected_recursive_loop_0715/vine_d5_projected_compete/latest_mesh.txt`
- 角色：最大 hero panel，证明 depth-5 connected recursive growth。

替换顺序：

1. `vine_projected_compete` depth 3：如果 depth 5 crop 不稳或局部碎片过多。
2. `vine_d5_projected_compete_fork`：如果 fork 形态明显更丰富且 projection 后仍干净。
3. `vine_projected_fork_side`：只作为 matrix 或小 panel，不作为最大主视觉。

重渲染要求：

- `iso`、`front`、`side` 三视图。
- teaser 使用 `iso` 或轻微 front-iso，保留枝条轮廓。
- 可用 textured preview 只有在不掩盖拓扑缺陷时才进入 teaser；否则用 neutral render。

### 3.2 Head asset B: Portal / Transform-Copy Ornament

首选：

- 名称：`tree_projected_portal`
- render：`visuals/paper_quality_renders_20260508/blender_tiles/tree_portal_iso.png`
- mesh 记录：`visuals/siga_night_20260508/siga_projected_recursive_loop_0715/tree_projected_portal/latest_mesh.txt`
- 角色：第二主视觉，负责非树、transform-copy、portal 叙事。

替换顺序：

1. `transform_portal_d3`：如果 tree portal 不够像大圆环。
2. `transform_radial4_d3`：如果 radial symmetry 比 portal 更可读。
3. `vine_d5_projected_portal`：如果需要和主 vine 统一材质和语言，但要避免两个 vine panel 太像。

降级条件：

- 圆环中心碎片明显且无法通过视角/crop 控制。
- 外轮廓不闭合或读成破损物。
- texture 让读者无法判断几何结构。

### 3.3 Head asset C: Tree / Bush Growth

首选：

- 名称：`tree_projected_compete`
- render：`visuals/paper_quality_renders_20260508/blender_tiles/tree_compete_iso.png`
- mesh 记录：`visuals/siga_night_20260508/siga_projected_recursive_loop_0715/tree_projected_compete/latest_mesh.txt`
- 角色：小 panel 或 2x2 panel，连接 procedural branching 叙事。

替换顺序：

1. `tree_projected_compete_fork`：如果分叉语义更强。
2. `tree_projected_fork_side`：如果 silhouette 更清晰。
3. `lsystem_fork_side_a0p25_pruned.obj`：作为 classical/procedural baseline 或 backup，不作为“ours”主视觉。

降级条件：

- 孔洞、底部破面或断裂是第一视觉。
- 需要靠非常特殊的视角才能看起来完整。

### 3.4 Head asset D: Porous / Crystal / Stress-Test

首选：

- 名称：`dla_projected_compete`
- render：`visuals/paper_quality_renders_20260508/blender_tiles/dla_compete_iso.png`
- mesh 记录：`visuals/siga_night_20260508/siga_projected_recursive_loop_0715/dla_projected_compete/latest_mesh.txt`
- 角色：小 panel，证明 stress-test breadth，不承担第一视觉。

替换顺序：

1. `dla_projected_compete_fork` 或 smoothed DLA：如果形体更像 porous/coral 而非 blocky cluster。
2. `dla_projected_radial`：如果 radial structure 可读。
3. `bismuth_crystal` / `pyrite_cubes` public guide 只作为 guide/source reference，不作为结果 tile。

降级条件：

- 块状感太强、像失败网格。
- fragment 或表面噪声让它拉低 teaser。
- 放入 appendix/stress-test matrix，不进入头图。

### 3.5 Texture / GLB 替换策略

如果 GLB/PBR 成功：

- 只给 2-3 个 star assets 使用 textured render：`vine`、`portal ornament`、可选 `tree`。
- matrix 仍以 neutral geometry 为主，避免材质差异破坏对比。
- caption 说明 textured panels are selected appearance exports。

如果 GLB/PBR 失败或质量不稳定：

- 头图全用 neutral geometry。
- texture latent / PBR compatibility 放 appendix table。
- 不要把 `textured_glb_preview_contact_sheet.png` 原样放正文。

## 4. 30+ result matrix 布局

### 4.1 目标布局

目标：4 行 x 8 列 = 32 个结果 tile，另附 4-6 个 ablation/failure tile 可放 supplemental second row 或单独 failure strip。

推荐 full-width 或 supplemental 宽图：

```text
                 Competition  Comp.+Fork  Side Fork  Radial  Portal  Scale  Depth+  Backup
Organic Vine      tile         tile        tile       tile    tile    tile   tile    tile
Tree/Bush         tile         tile        tile       tile    tile    tile   tile    tile
Porous/DLA        tile         tile        tile       tile    tile    tile   tile    tile
Transform/Orn.    tile         tile        tile       tile    tile    tile   tile    tile
```

如果正文空间有限，正文只放 4x4 selected matrix：

```text
Rows: Vine, Tree, Porous, Transform
Cols: Competition, Fork, Portal/Radial, Depth/Projection star
```

30+ 全矩阵放 appendix/supplemental。

### 4.2 Tile 规格

- 每个 tile 使用同一 Blender/Cycles render protocol。
- 只混 `iso` view；`front/side` 不进入主矩阵，放 QA 或 appendix。
- tile crop 为正方形，主体最大边占画面 78-86%。
- 背景统一 off-white / warm gray，带非常轻的 contact shadow。
- 不使用圆角卡片，不使用粗边框。
- 行列分隔用 0.35-0.5 pt 浅灰线，或只用留白。
- 标签在矩阵外部：列标题在上，行标题在左；tile 内不放文件名。

### 4.3 32 tile 建议清单

#### Row 1: Organic Vine / Root

1. `vine_projected_compete` depth 3
2. `vine_projected_compete_fork` depth 3
3. `vine_projected_fork_side` depth 3
4. `vine_projected_radial` depth 3
5. `vine_d5_projected_portal` depth 5
6. `vine_prune_scale_down` 或 `lattice scale_down` backup
7. `vine_d5_projected_compete` depth 5 star
8. `vine_d5_projected_compete_fork` 或 `vine_d5_projected_fork_side`

#### Row 2: Tree / Bush

1. `tree_projected_compete`
2. `tree_projected_compete_fork`
3. `tree_projected_fork_side`
4. `tree_projected_portal`
5. `tree_compete_s1` progression
6. `tree_compete_s2` progression
7. `tree_compete_s3` final
8. `lsystem_fork_side_a0p25_pruned` baseline/backup

#### Row 3: Porous / DLA Stress-Test

1. `dla_projected_compete`
2. `dla_projected_compete_fork`
3. `dla_projected_radial`
4. `dla_projected_echo`
5. `dla_fork_side_s2_a0p25_d3`
6. `dla_side_s1_a0p25_d3`
7. smoothed DLA compete fork
8. raw/pruned DLA comparison winner

#### Row 4: Transform / Ornamental

1. `tree_projected_portal`
2. `transform_portal_d3`
3. `transform_radial4_d3`
4. `vine portal d3`
5. `vine radial4 d3`
6. `lattice portal d3`
7. `lattice scale_down d3`
8. `lattice translate_x d3`

现有 matrix tile 可参考：

- `visuals/paper_quality_renders_20260508/matrix_test_one/*.png`
- 当前 contact sheet：`paper_siga/figures/matrix_test_one_contact_sheet.png`

但最终图需要重新排版，不建议直接使用 contact sheet。

### 4.4 Metadata 和 provenance

每个 tile 在制作表中保留以下字段，但不全部写进图内：

| 字段 | 用途 |
|---|---|
| display label | 图内/列标题短标签 |
| category | row grouping |
| operator | Competition / Fork / Portal 等 |
| depth | `d=3`、`d=5` |
| status | direct / masked / projected / pruned / smoothed |
| mesh path | reproducibility |
| render path | figure assembly |
| component stats | caption 或 supplement |
| GLB status | success / pending / failed / not attempted |

图内 label 控制在 1 行，如：

- `d=5, Competition`
- `Portal, d=3`
- `Projected`
- `Smoothed`

不要写 `vine_d5_projected_compete_s5_iso.png`。

### 4.5 结果矩阵正文版 vs 补充版

正文版：

- 4x4 或 4x5，强调最强结果。
- 每行第一个 tile 放该 category 的 star。
- caption 重点解释 breadth 和 projection-stabilized growth。

补充版：

- 4x8，完整 32 tile。
- 可加 4-6 个 failure/stress-test 小 strip：`raw fragments`、`texture failed`、`unprojected`、`over-smoothed`。
- 允许更小字体，但最小不低于 6.2 pt。

## 5. 配色 / 字体 / 标签规范

### 5.1 配色体系

三套颜色分离，不混用：

#### 方法图

| 语义 | 颜色 |
|---|---|
| state / sparse latent | pale blue-gray `#DCE7EE` |
| grammar / rule | pale amber `#F3E3BE` |
| learned prior / sampler / decoder | pale violet `#E7DEF2` |
| projection / feedback | deep teal-blue `#1B6F8F` |
| texture/export | muted gray-green `#B9C8BE` |
| disabled/special cases | light gray `#E6E6E1` |

主反馈箭头只用 `#1B6F8F`，不要多色箭头。

#### 数据图

Method ablation 固定：

- `Direct`: gray `#9AA0A6`
- `Final-only`: orange `#D55E00`
- `Per-depth / Ours`: blue `#0072B2`

Operator plot 不复用 method 蓝/橙语义：

- `Competition`: green `#009E73`
- `Competition+Fork`: magenta `#CC79A7`
- `Side Fork`: gold `#E69F00`
- `Portal Copy`: sky `#56B4E9`
- `Scale Copy`: muted purple `#6B5B95`

#### Render / qualitative

- 主体材质：neutral clay / muted teal-gray。
- 背景：warm off-white / neutral gray。
- 只允许 selected GLB stars 使用 texture。
- 不同类别不要用不同鲜艳材质区分；类别由行标签和 caption 区分。

### 5.2 字体

推荐：

- 数据图：serif，`Times New Roman` / `Times` / `Nimbus Roman` / `DejaVu Serif`，math 用 STIX。
- 方法图和组图标签：如果用 sans，需全 figure set 统一，推荐 `Helvetica Neue` / `Arial` / `DejaVu Sans`；但公式必须 LaTeX。

字号：

| 元素 | 打印等效字号 |
|---|---|
| panel label `(a)` | 7.0-7.5 pt bold |
| axis label | 7.0-7.5 pt |
| tick label | 6.2-6.5 pt |
| legend | 6.2-6.7 pt |
| method block title | 7.2-8.0 pt |
| method block subtext | 6.5-7.0 pt |
| matrix row/column label | 6.5-7.2 pt |
| tile micro label | 5.8-6.2 pt，仅 supplement 使用 |

不要使用大标题占图内空间；标题交给 caption。

### 5.3 标签词典

Operator 显示名：

| code | display |
|---|---|
| `compete` | `Competition` |
| `compete_fork` | `Competition+Fork` |
| `fork_side` | `Side Fork` |
| `portal` | `Portal Copy` |
| `scale_down` | `Scale Copy` |
| `radial4` | `Radial Copy` |
| `echo` | `Echo Copy` |

Category 显示名：

| internal | display |
|---|---|
| vine/root | `Organic Vine` 或 `Recursive Vine` |
| tree/bush | `Tree Growth` |
| DLA/porous | `Porous Stress-Test` |
| transform/ornament | `Transform Ornament` |

Projection 显示名：

- `Direct`
- `Final-only`
- `Per-depth Projection`
- `Projected`
- `Pruned`
- `Smoothed`

## 6. 必须重渲染或降级的现有图

### 6.1 必须重渲染

1. `paper_siga/figures/head_figure_textured_non_tree_draft_20260508.png`
   - 原因：浅灰竖条、材质/光照不统一、panel 像拼贴。
   - 处理：只保留构图思路；重渲染 vine 和大圆环，重新排版。

2. `paper_siga/figures/head_figure_draft_4cat_20260508.png`
   - 原因：超宽比例太扁，后 3 个 tile 面积小且留白大。
   - 处理：降级为 draft reference；不要直接用于正文。

3. 大圆环 / portal tile
   - 当前候选：`visuals/paper_quality_renders_20260508/blender_tiles/tree_portal_iso.png`
   - 原因：需要 front/3/4 front、detail crop、silhouette-first render。
   - 处理：重渲染 full ring、module crop、projection/depth strip。

4. `paper_siga/figures/method_system_grammar_draft_v2_20260508.png`
   - 原因：bitmap draft，信息过载，ASCII formula，无真实 inset。
   - 处理：按本文件第 1 节重画 vector 版。

5. `paper_siga/figures/matrix_test_one_contact_sheet.png`
   - 原因：仍是 contact sheet，不是论文矩阵。
   - 处理：用现有 tile 作为素材池，重新排版；最好重新统一 batch render。

6. `paper_siga/figures/mesh_based_visual_status_contact_sheet_refined.png`
   - 原因：圆角卡片、内部状态汇报感强。
   - 处理：只作为选图依据，不直接放正文。

7. `paper_siga/figures/textured_glb_preview_contact_sheet.png`
   - 原因：GLB 预览不等于 paper-ready textured render，白底和标签 strip 不统一。
   - 处理：降级为 texture status / appendix reference。

### 6.2 可保留但需要图形 polish

1. `paper_siga/figures/projection_ablation_lcr_components_20260508.pdf`
   - 保留 1x2 结构。
   - panel title 改短：`(a) Connected mass`、`(b) Fragment count`。
   - y label 改为正式单位，log scale 在 caption 说明。
   - 加关键数值标注。

2. `paper_siga/figures/space_competition_depth_curves_tokens_20260508.pdf`
   - 正文优先使用 tokens 1x3。
   - legend 改为论文术语。
   - caption 说明 missing/stalled operators。

3. `paper_siga/figures/space_competition_depth_curves_compact_20260508.pdf`
   - 适合 appendix/full-width analysis。
   - 若放正文，必须去掉各 panel 科学计数法 offset，改用 axis label 单位。

### 6.3 必须降级到 appendix 或素材池

1. 过暗 hard-surface module
   - 除非 matte graphite + rim light 重渲染后可读，否则不进 teaser。

2. architectural arch portal
   - 当前形体可读性不足；除非有更干净重渲染，否则只进 appendix/stress-test。

3. porous/DLA blocky variants
   - 作为 stress-test matrix 可以保留；不作为最大头图。

4. mixed-material contact sheets
   - 不直接进入正文；只能做 selection board。

## 7. 制作顺序

P0：

1. 重渲染 4 个 head asset 的统一 neutral `iso/front/side`。
2. 专门重渲染大圆环：full ring、module crop、projection/depth strip。
3. 重画方法总图 vector 版，只保留核心 loop 和 3 个真实 inset。
4. 用现有 `matrix_test_one` 素材先排一版 4x8 matrix，检查行列标签和 crop。

P1：

1. 如果 GLB 质量通过，只替换 2-3 个 teaser star panels。
2. 数据图统一字体、legend 和 panel title。
3. 做 4x4 正文结果矩阵和 4x8 supplement 矩阵两个版本。

P2：

1. 灰度/色盲检查。
2. 确认 vector PDF 字体嵌入。
3. 为每个 final tile 保存 mesh/render provenance 表。

## 8. 最终交付建议

下一版可交付文件建议为：

1. `head_teaser_v2.pdf/png`：1+3 布局，vine 最大，大圆环第二大。
2. `method_overview_ps_rslg_v2.pdf`：vector recursive projection loop。
3. `result_matrix_4x4_main_v2.pdf/png`：正文 qualitative breadth。
4. `result_matrix_4x8_supp_v2.pdf/png`：30+ result matrix。
5. `portal_ornament_detail_strip_v2.pdf/png`：大圆环 full/detail/projection 证据，可嵌入 teaser 或 supplement。

最重要的设计取舍：

- 宁可减少头图 asset 数量，也不要让弱结果降低第一印象。
- 宁可方法图少几个 block，也要让 projection-in-loop 一眼可见。
- 宁可 30+ 矩阵放 supplement，也不要在正文塞不可读小 tile。
- 宁可全 neutral geometry，也不要使用质量不稳定的 texture 混排。
