# 严格论文故事审计：Recursive 3D Generative Growth / Trellis2 SIGGRAPH Asia - 2026-05-08

审计依据仅来自本地文件：

- `/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_texture_visuals_plan_20260508.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/paper_story_audit_zh_20260508.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visual_result_matrix_and_render_protocol_20260508.md`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex`

本文件只做论文故事审计，不修改 `main.tex`、`references.bib` 或任何实验脚本。

## 1. 当前故事，一段话版本

当前最稳的论文故事不是“我们让 Trellis2 学会无限递归”，也不是“我们已经生成高质量全材质 3D 资产矩阵”，而是：**训练冻结的 Trellis2 可以被重新用作 mesh-derived sparse 3D state 的表示和局部视觉先验；递归结构由显式 sparse-latent grammar 控制；每一层 decode 后的 connected-component projection / pruning 再 re-encode 被纳入递归映射本身，从而抑制深度递归中的碎片误差放大；最终得到有限深度的递归 3D asset growth，并且部分结果已经跑通 Trellis2 texture/GLB export。** 这条故事在 vine/root depth-5 `compete`、tree depth-3、DLA stress test、portal/transform-copy 附录上有初步证据；最硬的贡献是 projection-stabilized R-SLG，而不是 texture 质量、flow naturalization 曲线、Droste/Escher 应用或无限递归。

## 2. SIGGRAPH Asia 论文可成立的部分 vs 薄弱部分

### 2.1 现在已经可以作为 SIGA 主线的内容

1. **Projection-Stabilized Recursive Sparse-Latent Grammar**
   - 这是当前最强 claim。
   - 证据链清楚：root OBJ mesh -> O-Voxel/SLAT encode -> sparse grammar -> decode mesh -> per-depth Project -> re-encode -> repeat。
   - 已有强例子：vine depth 3 raw `819` components -> projected `1`；vine depth 5 raw `669` components -> projected `2`；tree depth 3 raw `752` components -> projected `2`；DLA depth 3 raw `110` components -> projected `1`。
   - 论文中应强调 Project 是 recursive map 的一部分，不是最后做一遍 cleanup。

2. **Mesh-first entry 替代 2D scaffold / prompt entry**
   - 当前故事有合理负面动机：直接用点线图、DLA/IFS/L-system 2D scaffold 去喂 image-conditioned Trellis2 会产生 sheet/fragments；mesh-first encode 更适合递归结构保存。
   - 这可以支撑 Introduction 中的“naive bridge fails”。

3. **Grammar owns support/topology, Trellis2 owns representation/local prior**
   - 这个分工比“frozen generator fully naturalizes recursion”更可信。
   - main.tex 已经接近这个表达：`S_d=(C_d,F_d,A_d,H_d)`，operators 在 sparse coordinates/features 上执行。
   - 建议把 Trellis2 称为 frozen native 3D representation / local prior / downstream texture route，而不是完整 recursive sampler。

4. **Occupancy-competition growth operator (`compete`)**
   - `compete` 目前是最稳定的 native sparse growth operator。
   - 可以作为一个具体 operator contribution，但不要把它写成传统 space-colonization baseline 的简单包装；应写成 R-SLG 内部的 occupancy-exclusion growth rule。

5. **Stability-expression tradeoff**
   - `compete` 稳定但保守；`compete_fork`、`fork_side` 更有形态增长但更碎；attachment-aware variants 能降组件但桥接几何粗糙；DLA/porous 数值稳定但视觉 blocky。
   - 这是一条像研究论文的结果线，比“我们展示很多漂亮图”更可防守。

6. **True textured GLB export 已经从“兼容性”推进到“技术跑通”**
   - 更新后的 texture/visuals plan 记录：`vine_d5_compete_s5_inference/textured.glb`、`tree_compete_s3/textured.glb`、`vine_d5_fork_side_s5/textured.glb`、`tree_portal_s3/textured.glb`、`dla_compete_s3/textured.glb`、`vine_projected_fork_side_s3/textured.glb` 等已成功。
   - 这允许论文说“texture/export smoke tests succeed for selected cases”。
   - 但只能作为 downstream appearance route / compatibility evidence，不能直接升级为“高质量材质生成已解决”。

### 2.2 当前不够强，不能放成主 claim 的内容

1. **高质量 textured 3D asset generation**
   - GLB export 成功不等于 paper-grade textured asset 成功。
   - 现有判断显示：vine/root 最强；tree 有可用纹理证据但 holes/thin sheets 更明显；DLA texture blocky/wood-like；portal/fork-side 仍受几何碎片限制。
   - main.tex abstract 里关于 textured GLB 的句子可以保留为 smoke-test 结果，但 teaser/caption 必须说明哪些 panel 是 textured GLB、哪些只是 neutral Blender render。

2. **Frozen Trellis2 as recursive naturalization operator**
   - 这是 proposal 的理想中心，但当前证据更偏 projection/grammar，而不是 clean local flow naturalization。
   - masked weak repair、alpha `0.25/0.5` 是经验性结果；没有 clean tau/noise curve。
   - 建议降级为“frozen Trellis2 representation and local prior are compatible with recursive sparse-state editing”。

3. **One-step generative rewrite 优于 copy-paste**
   - 目前没有同一 render protocol 下的 copy-paste / no-denoise / local-inpaint / full-flow / projected R-SLG 对照。
   - 不能把“generative rewrite beats copy-paste”作为主结论。

4. **Droste、Escher、Monument-Valley、真正 infinite recursion**
   - portal/transform-copy 有 appendix 价值；rotate/radial/radial4 稳定性弱。
   - 没有 camera-aware placement、view-dependent illusion evaluation，也没有无限深度结果。
   - 这些应放 Discussion future work，不应出现在 contributions。

5. **DLA/coral/porous 作为 hero**
   - DLA/porous 适合 stress-test，因为 projection 能控制组件数，但视觉仍 blocky。
   - 除非后续找到更好 root，否则不要把 DLA 放 teaser 主位。

6. **Attachment-aware / seam-aware grammar as final method**
   - 当前 `compete_fork_attach`、`fork_side_attach` 是可报告的探索，但桥接几何粗糙。
   - 放 appendix ablation 或 limitations 即可。

7. **30+ result matrix 已完成**
   - visual protocol 设计了 4 x 8 = 32 tiles；计划记录已有 32 neutral OBJ candidate render contact sheet。
   - 但严格说，论文级 30+ matrix 还需要统一元数据、相同 camera/material、最终筛选、caption 和 traceable render paths。

## 3. 必须补的实验和材料

### 3.1 主文必补，否则 SIGA story 会显得空

1. **Projection 定量表**
   - 行：root/operator/depth。
   - 列：raw components、kept components、largest component ratio、vertices/faces before/after、re-encode success、render success。
   - 至少覆盖：vine depth 3/5 compete，tree depth 3 compete，DLA depth 3 compete，portal/transform-copy 一例。

2. **Projection ablation**
   - 必须比较 no projection、final-only projection、per-depth projection。
   - 如果 no projection 太差，可以用 component explosion、renderability failure、visual crop 作为证据。

3. **统一 baseline visual protocol**
   - 至少四类：pure procedural/scaffold、one-shot or image-entry Trellis2 failure、direct sparse grammar without per-depth projection、projected R-SLG。
   - 所有 baseline 必须用同一 Blender/Cycles camera/material/lighting；不要把 matplotlib preview 和 Cycles render 混在主图里。

4. **Copy-paste / local naturalization 对照**
   - 如果论文仍想讲 “naturalization”，就必须补：copy transform only、full flow repair、masked weak blend、projection-stabilized masked blend。
   - 若来不及补，应把 naturalization 降级为 implementation detail。

5. **32-result matrix 的最终版**
   - 不是更多图越好，而是统一协议、四类 row、每 tile 有 root/operator/depth/projection/render path。
   - 可用 textured GLB stars 点缀，但矩阵主协议应以稳定 neutral OBJ/GLB Blender render 为准。

6. **Method figure**
   - 一张图必须明确：mesh root -> O-Voxel/SLAT encode -> sparse grammar -> shape decode -> Project -> re-encode loop -> final mesh -> optional texture/GLB -> render。
   - 这张图是论文说服力的核心，不应只靠文字描述。

7. **Texture QA table**
   - 现在可以说 GLB export succeeded，但必须给质量门槛。
   - 表中应有：case、operator/depth、GLB status、local Blender render path、visible holes/thin sheets/material mismatch、是否进入 teaser/matrix。

8. **非树状资产扩展**
   - 用户已经提醒不要过度聚焦 tree-like assets；plan 也记录了 crown radial ornament、scifi mechanical module、city arch cluster、snow architecture 等 non-tree root sweep。
   - SIGA 故事若只展示 vine/tree/DLA，会被看成植物递归小技巧；至少需要 transform/ornamental 或 architectural row 证明“recursive sparse-latent assets”更宽。

### 3.2 可补但不应阻塞主线

1. **Related-work 精修**
   - 要把工作和 Trellis editing / inpainting / 3D latent editing 区分开：本工作重点是 repeated recursive operator stability，不是 single edit。

2. **Video demo**
   - 适合 supplemental，不必作为论文主证据。
   - 若做，必须从 Blender turntable 或统一渲染输出剪，不用 contact sheet 屏录。

3. **Texture schedule observation**
   - steps/more texture resolution 不单调更好，这是有趣工程发现，但目前更适合作为 appendix note。

## 4. 如何逐点回答用户昨晚 prompt

| 昨晚 prompt 点 | 严格回答 | 论文处理 |
|---|---|---|
| 用 frozen Trellis2，不训练新模型 | 完成方向正确。Trellis2 作为 frozen mesh-derived representation、shape SLAT encode/decode、texture/GLB route 已跑通。 | 主文可写 training-free；不要暗示训练了新模型。 |
| 把递归程序放进 latent/sparse state，而不是外部 guidance | 部分完成且是主线。当前 R-SLG 在 sparse support/features 上操作，但 formal API 和图还不够。 | Contribution 1 + Method figure。 |
| 先诊断 Trellis2 operator，不急着做 Escher/fractal | 已完成初步诊断。2D scaffold/image condition 失败，mesh-first 成功；transform compatibility 有矩阵。 | Introduction motivation + Appendix diagnostics。 |
| translation/mirror/scale/rotate/portal 等 transform compatibility | 部分完成。translate/scale/portal 较稳，rotate/radial/radial4 弱。 | Compact table 主文或 appendix；不要 claim general equivariance。 |
| local re-noise / preservation-naturalization curve | 偏弱。只有 alpha 经验，没有 clean curve。 | 降级为 ablation/future work，除非补实验。 |
| one-step generative rewrite 优于 copy-paste | 未充分证明。缺同协议对照。 | 不能做主 claim；补 baseline 后再说。 |
| recursive depth scaling K=1..5 | 部分完成且很关键。vine depth 5 是最强；tree/DLA 多为 depth 3。 | Results 主表和主图。 |
| projection as recursive stabilizer | 完成，是最强贡献。per-depth Project + re-encode 已经形成方法核心。 | Contribution 2，Results 第一组。 |
| branching root/tree/coral/crystal demo | root/vine 强，tree 可用，DLA/coral/porous 目前只是 stress-test。 | teaser 以 vine/root 为主，DLA 不做 hero。 |
| space-colonization / occupancy competition | 初版完成，`compete` 最稳。 | 作为 native sparse occupancy competition operator。 |
| attachment/seam-aware grammar | 部分完成但视觉弱。 | Appendix / limitation。 |
| Droste / portal recursive embedding | 部分完成。portal 有视觉差异，但不是稳定主贡献。 | Appendix 或 fourth category backup。 |
| isometric / Monument-Valley-like illusion | 未完成。没有 camera-aware placement/eval。 | 不写主文贡献。 |
| material / texture coherence / GLB usability | 技术 export 已跑通多个 GLB；视觉质量仅 vine/tree 部分可用，其他不稳。 | 写 smoke-test success + quality caveat；不要写 solved material coherence。 |
| paper-quality rendering | 部分完成。已有 Blender/Cycles neutral renders、head draft、32 candidate contact sheet；最终 figure 还需统一筛选。 | 主文只放 Blender/Cycles renders，不放 raw previews。 |
| 30+ generated result matrix | 进行中。协议明确，已有候选，但最终论文矩阵仍需元数据和统一 QA。 | Fig. results matrix；caption 说明 texture status。 |
| traditional/generative baselines same visual protocol | 目前偏弱。已有 contact sheets，但还没主文级统一协议。 | 必补，否则 reviewer 会质疑 cherry-picking。 |
| SIGGRAPH/ACM paper skeleton | 已有 rough draft。main.tex story 方向基本对，但仍偏 preliminary。 | 继续填 Results tables/figures。 |
| related work scaffold | 有初稿，但定位风险仍在。 | 强调 repeated recursive operator stability。 |

## 5. 对当前 `main.tex` 的严格判断

1. **标题可用**
   - `Recursive Sparse-Latent Grammars for Training-Free 3D Generative Growth` 和当前最稳故事一致。

2. **Abstract 基本方向正确，但 texture 句子要谨慎**
   - “smoke tests export textured GLB assets” 可以成立。
   - 不要把这句话扩展成 “high-quality material generation”；最好在 Results/Limitations 明确 texture 质量不稳定。

3. **Introduction 的问题设定可用**
   - procedural recursion vs one-shot 3D generator 的张力清楚。
   - 建议进一步强调 naive bridge failure：2D scaffold condition 和 global flow repair 都不可靠。

4. **Contributions 需要更硬**
   - 现在 contributions 是合理方向，但还缺 projection quantitative evidence 的落点。
   - 建议把“empirical analysis of stability-expression tradeoff”落实为表和图。

5. **Teaser caption 诚实但仍需最终 QA**
   - caption 说 vine/root 是 true textured GLB，tree/porous/portal 是 neutral Blender render，这种诚实表述是对的。
   - 但最终版应避免“texture panel”和“neutral panel”在视觉风格上让人误读为同一质量等级。

6. **Results 太像状态报告**
   - 需要从 preliminary paragraph 变成：Projection table -> ablation figure -> visual matrix -> texture QA。

7. **Limitations 方向正确但需要具体**
   - 应具体列出 root-quality dependence、texture material mismatch、holes/thin sheets、operator compatibility empirical、non-tree breadth still under expansion。

## 6. 建议 figure/table plan

### 主文 figures

1. **Figure 1: Teaser / four-category assets**
   - Panel A: vine/root depth-5 `compete`，优先用 true textured GLB render。
   - Panel B: tree/bush depth-3 `compete`，如果 textured render holes 太明显，可用 neutral render，并在 caption 标明。
   - Panel C: transform/ornamental portal 或 non-tree architectural result，不要只放 tree-like。
   - Panel D: DLA/porous 只在视觉过关时进入；否则换成 non-tree ornamental，把 DLA 降到 stress-test figure。

2. **Figure 2: Method pipeline**
   - 必须画出 recursive loop，而不是普通 pipeline。
   - 关键视觉节点：sparse state、grammar operator、decode mesh、Project、re-encode、texture/GLB optional branch。

3. **Figure 3: Projection stabilizes recursion**
   - 同一 root/operator/depth 下对比 no projection、final-only projection、per-depth projection。
   - 同时给 visual crop 和 component count。

4. **Figure 4: 30+ result matrix**
   - 4 rows x 8 tiles。
   - Rows 推荐：organic vine/root；tree/bush；transform/ornamental/non-tree；porous/stress-test。
   - 所有 tiles 使用同一 Blender/Cycles protocol；texture stars 可以出现，但不要破坏协议。

5. **Figure 5: Stability-expression tradeoff / operator ablation**
   - Columns：`compete`、`compete_fork`、`fork_side`、`portal/radial`。
   - Rows：vine/tree/non-tree 或 depth 3/depth 5。
   - 目标是说明为什么保守 operator 稳、表达性 operator 碎。

### 主文 tables

1. **Table 1: Projection quantitative table**
   - root、operator、depth、raw components、projected components、vertices/faces、largest component ratio、renderability。

2. **Table 2: Overnight prompt / requirement status**
   - 可放 appendix，如果主文空间紧张。
   - 用 completed / partial / weak / missing。

3. **Table 3: Texture/GLB QA table**
   - case、GLB export status、render status、visual quality gate、paper usage。
   - 明确“export success”与“main-figure usable”不是同一概念。

4. **Table 4: Baseline comparison**
   - procedural scaffold、image-entry Trellis2、direct sparse grammar、full flow repair、masked weak blend、projected R-SLG。
   - 指标：connectedness、depth stability、renderability、visual failure notes。

### Appendix figures

1. Full transform compatibility matrix。
2. 2D scaffold / point-line condition failures。
3. Attachment-aware variants。
4. DLA/porous smoothing and failure/stress tests。
5. Texture schedule comparison：steps/resolution 不单调更好。

## 7. 最终严格结论

这篇论文现在有一个可写、可防守的 SIGGRAPH Asia 方法核心：**Projection-Stabilized R-SLG over mesh-derived Trellis2 sparse 3D states**。应该把论文火力集中在“递归结构控制 + frozen native 3D representation + per-depth projection 稳定性”上。当前可以诚实报告 true GLB export 已跑通多个样例，但 texture 还不是主贡献；copy-paste/local naturalization superiority、Droste/Escher/isometric、attachment-aware seam grammar、DLA/coral hero 和真正 infinite recursion 都应降级。下一步最重要的是补 projection quantitative table、统一 baseline/matrix、method figure、texture QA table 和 non-tree breadth，否则 story 会停留在“漂亮的实验状态报告”，而不是 SIGA 审稿人能快速判断贡献边界的论文。
