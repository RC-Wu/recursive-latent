# 论文故事与昨晚 prompt 逐项审计 - 2026-05-08

审计对象：

- 原始 proposal：`/Users/fanta/Downloads/recursive_3d_generative_growth_proposal.md`
- 昨晚 SIGA 夜间计划：`/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_siga_night_plan_20260508.md`
- texture/visuals 接续计划：`/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_texture_visuals_plan_20260508.md`
- 当前论文骨架：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex`

本文只做支线审计，不修改主 LaTeX 文件，也不修改已有实验脚本。

## 0. 总判断

当前项目已经从“试 Trellis2 能不能生成递归形状”推进到一个可防守的 SIGGRAPH Asia 方法雏形：**Projection-Stabilized Recursive Sparse-Latent Grammar (R-SLG)**。最强证据不是 texture，也不是 Droste/Escher，而是：

```text
root OBJ mesh
-> Trellis2 O-Voxel / shape SLAT encode
-> sparse grammar step
-> shape SLAT decode to OBJ mesh
-> per-depth Project
-> re-encode
-> repeat to depth 3/5
-> texture-latent / PBR voxel compatibility
```

当前最可防守的主线资产是 Trellis example `04` vine root，最可防守的算子是 `compete`。核心证据来自：

- vine depth-5 projected loop visual：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/contact_sheets/shaded_vine_d5_projected_loop_final_s5_20260508.png`
- vine depth-5 Blender/Cycles neutral render：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/blender_tiles/vine_d5_compete_iso.png`
- per-depth projection preview：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/contact_sheets/vine_d5_projected_loop_pruned_preview_20260508.png`
- projected-loop metrics in plan：`vine_d5_projected_compete` at depth 5, raw `669` components -> projected `2`, `190564` vertices / `455964` faces, texture/PBR route compatible with `1608` shape tokens and `526818` PBR voxel tokens.

但按 SIGGRAPH Asia 标准，目前还不能声称“高质量 textured 3D asset generation”完成。当前 texture 证据主要是 Trellis2 texture SLAT / PBR voxel compatibility；第一个 true textured GLB export smoke 仍在修 export/postprocess 问题。对应记录在：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/rendering_setup_notes_20260508.md`
- remote log：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/textured_glb_vine_d5_compete_s5_inference_20260508_131955.log`
- remote output dir：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/siga_textured_glb_export/textured_glb_20260508/vine_d5_compete_s5_inference`

## 1. 昨晚要求逐项状态审计

| 要求 / prompt 目标 | 状态 | 证据 | 论文位置判断 |
|---|---|---|---|
| 使用 frozen Trellis2 作为 recursive naturalization operator，而不是训练新模型 | 部分完成 | Trellis2 mesh-first encode/decode、shape SLAT grammar、texture latent checks 已跑通；但 true local flow naturalization 的贡献证据弱于 projection/grammar 证据。 | 主故事可用，但措辞应是“repurpose frozen native 3D representation and local priors”，不要过度强调 flow naturalization 已解决。 |
| 不把程序语法当 external constraint guidance，而是 grammar-as-sampler / sparse latent rewrite | 部分完成 | 当前实现从 mesh -> O-Voxel/SLAT -> sparse coordinates/features 操作，相关脚本包括 `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/trellis2_recursive_slat_grammar_workflow.py`。 | 可做主贡献 1：sparse-latent grammar representation。需要补 formal operator API 和图。 |
| 先做 Trellis2 operator diagnostics，不直接跳复杂 fractal/Escher | 完成 | 直接 2D scaffold 条件失败、mesh-first 路线成功、transform compatibility matrix 已跑；可视结果如 `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/contact_sheets/transform_compat_tree_gpu6_0420_sheet.png`。 | 实验/负面结果。可用于 Introduction failure motivation 和 Appendix diagnostics。 |
| Latent transform compatibility：translation, mirror, scale, rotate, patch copy, portal 等 | 部分完成 | GPU6 transform run 完成；稳定：translate, scale, portal；弱：rotate_z；radial/radial4 artifact-prone。 | 主文可放一张 compact compatibility table；完整矩阵进附录。 |
| Local re-noise / preservation-naturalization curve | 部分完成偏弱 | masked weak repair、alpha `0.25/0.5` 有经验结论；但没有 proposal 要求的 clean tau curve。 | 不能作为主贡献单独宣称。可作为 ablation idea；未来 24 小时应补表或降级。 |
| One-step generative rewrite 优于 copy-paste | 未充分完成 | 有 masked/weak blend 和 direct grammar 结果，但还没有同一 render protocol 下 copy-paste/no-denoise/local-inpaint 的清晰对照。 | 当前不能作为主 claim。需要补 baseline figure，否则只放方法动机。 |
| Recursive depth scaling K=1..5 | 部分完成且很重要 | vine depth 3/5、tree depth 3、DLA depth 3 已完成。最强：`vine_d5_projected_compete` raw `669` -> projected `2` components。 | 主实验。建议成为 Results 第一张定量表。 |
| Projection as recursive stabilizer | 完成，且是当前最强贡献 | per-depth projection loop 已跑通：`root mesh -> encode -> grammar -> decode -> Project -> re-encode -> next step -> texture latent`。visual：`shaded_projected_loop_final_s3_20260508.png`、`shaded_vine_d5_projected_loop_final_s5_20260508.png`。 | 主贡献 2。应明确 Project 是 recursive map 的一部分，不是后处理清理。 |
| Branching coral / root / crystal recursive asset first demo | 部分完成 | root/vine demo 强；DLA/porous/coral-like 数值稳定但 blocky。DLA visual：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/contact_sheets/shaded_dla_projected_loop_final_s3_20260508.png`。 | root/vine 做主图；DLA/porous 做 stress test 或 negative result；coral/crystal 暂不做主贡献。 |
| Space colonization / occupancy competition operator | 完成初版 | `compete` 和 `compete_fork` 已实现并跑完，`compete` 最稳。visual：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/contact_sheets/shaded_pruned_compete_candidates_20260508.png`。 | 可做主贡献 3 的具体实例：native sparse occupancy competition growth。 |
| Attachment-aware / seam-aware grammar | 部分完成偏弱 | `compete_fork_attach`、`fork_side_attach` 已跑，组件数可降，但 bridge geometry 粗糙。visual：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/contact_sheets/attached_projection_vine_d5_compare_20260508.png`。 | 不适合主方法。放未来工作或附录 ablation；除非 24 小时内显著修好。 |
| Droste / portal embedding | 部分完成 | `portal` transform 稳定但资产逐步稀疏/侵蚀；visual：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/contact_sheets/transform_compat_tree_gpu6_0420_sheet.png` 和 tree/vine portal rows。 | Appendix / teaser backup。不要作为主贡献。 |
| Isometric / Monument-Valley-like recursive illusion | 未完成 | 当前没有 camera-aware placement 或 view-dependent evaluation。 | 不应出现在主文贡献；最多 Discussion future work。 |
| Material / texture coherence and GLB usability | 部分完成，风险高 | 多个 candidates texture-latent/PBR voxel compatible；true GLB export still in smoke/fix stage。notes：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/rendering_setup_notes_20260508.md`。 | 当前只能说 downstream texture latent compatibility。不能声称 final textured assets。 |
| Paper-quality mesh rendering | 部分完成 | matplotlib/mesh contact sheets 和本地 Blender/Cycles neutral renders 已有；Blender 输出在 `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/blender_tiles/`。 | 可支持内部选择和初稿 figure；还不够 final teaser。 |
| 30+ generated result matrix | 未完成 | 计划中明确缺口；当前有多张 contact sheet，但不是统一 protocol 的 30+ matrix。 | 未来 24 小时高优先级。 |
| Traditional/generative baselines same visual protocol | 部分完成偏弱 | 有 traditional baseline contact sheet `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/traditional_baselines_contact_sheet.png`，也有 one-shot/object-like/image-entry negative results；但未统一 Blender/render/camera/material。 | 主文必须补，否则 reviewer 会质疑提升来自选择性展示。 |
| SIGGRAPH/ACM paper skeleton | 部分完成 | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex` 已有 abstract/intro/method/experiments/results/discussion 骨架。 | 只是 rough draft。主线程应更新，不由本文修改。 |
| Related work scaffold | 部分完成 | main.tex 有相关 work 桶；night plan 记录已加 NANO3D/VoxHammer/3D-LATTE/InpaintSLat/TRELLISWorld 等 bib anchors。 | 需要严查近作定位，避免被看成 Trellis editing 的简单工程变体。 |

## 2. 哪些内容能放在哪里

### 2.1 可做主贡献

1. **Recursive Sparse-Latent Grammar over mesh-derived Trellis2 O-Voxel/SLAT state**
   - 证据：mesh-first path 已替代 2D scaffold path；当前 main.tex 已把 state 写为 `S_d=(C_d,F_d,A_d,H_d)`。
   - 必须强调：grammar owns topology/support，Trellis2 owns local visual prior，projection owns stability。

2. **Projection-Stabilized Recursion**
   - 证据：vine stage 3 raw `819` components -> projected `1`；vine depth 5 raw `669` -> projected `2`。
   - 推荐主文表：no projection vs final-only projection vs per-depth projection，depth 3/5，root = vine/tree/DLA，operator = compete/compete_fork/fork_side。

3. **Native sparse occupancy competition operator (`compete`)**
   - 证据：`compete` 是稳定 operator，depth 5 仍 bounded；`compete_fork`/`fork_side` 表达力更强但碎片更多。
   - 论文表述：它不是“space colonization baseline”，而是 R-SLG 内部的 occupancy-exclusion growth rule。

4. **Stability-expression tradeoff**
   - 证据：`compete` 稳定但视觉增长较保守；`compete_fork`/`fork_side` 更明显但组件数高；`radial`/DLA 更 stress-prone。
   - 这比“我们生成了很多漂亮资产”更可信，也更像研究贡献。

### 2.2 可做主实验 / ablation

- Projection ablation：none / final-only / per-depth。
- Operator ablation：`compete`, `compete_fork`, `fork_side`, `radial`, `portal`。
- Root quality ablation：Trellis example `04` vine, `09` tree, DLA/porous, `33` lattice-vine。
- Texture compatibility table：shape tokens、PBR voxel tokens、PBR mean、render/export status。
- Visual protocol comparison：scatter preview vs true shaded mesh，证明为什么 paper 必须看 true mesh。

### 2.3 可放附录

- Full transform compatibility matrix：translate, scale, mirror, rotate_z, radial4, portal。
- Trellis2 2D scaffold condition failures：handcrafted point/line/DLA/IFS/L-system image conditions。
- Lattice-vine / transform-copy demos。
- Attachment-aware variants当前版本。
- Full root sweep contact sheets。

### 2.4 可作为负面结果

- Direct procedural point/line image -> Trellis2：产生 sheets/fragments，支持“不能从 2D scaffold 直接进 generator”。
- Full flow repair as main route：过度 topology drift。
- DLA/porous main visual：projection 能数值稳定，但 true shaded mesh 仍 blocky。
- Naive Laplacian smoothing DLA：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/siga_night_20260508/contact_sheets/dla_compete_fork_smoothing_shaded_20260508.png`，会产生 streak/radial artifacts。
- Remote `bpy` path：环境不可用，改用 local Blender；这是工程限制，不是论文负面结果。

## 3. 当前主故事框架

推荐论文故事不要再围绕“recursive 3D flow sampler can do everything”。更稳的 SIGA story 是：

1. **Problem**：procedural recursion 有结构但没有 asset quality；one-shot 3D generators 有视觉先验但没有 recursive control。
2. **Naive failure**：2D scaffold conditions 和 global flow repair 都失败，因为 generator 如果拥有整个对象，会抹掉 recursive scaffold 或产生碎片。
3. **Key shift**：从 image/prompt entry 转向 mesh-derived native 3D state：O-Voxel/SLAT sparse support。
4. **Method**：R-SLG 在 sparse support/features 上执行 grammar；Project 作为 recursive operator 稳定每一层；Trellis2 作为 frozen representation/local prior 和 texture/material route。
5. **Main finding**：projection-stabilized recursion 能把错误放大控制住；`compete` 最稳定，expressive operators 需要 projection/attachment。
6. **Scope**：finite-depth realizations of potentially infinite recursive programs；不是真正无限几何，不是新训练模型，不是通用任意 transform equivariance。
7. **Evidence**：vine/tree 主线 + DLA stress test + transform appendix + texture-latent compatibility。

当前 main.tex 的 abstract/intro 已经接近这个方向，但仍有两点需要主线程后续改：

- 把 “masked local naturalizer” 的 claim 降到与证据匹配；目前最硬的是 projection-stabilized sparse grammar。
- 把 texture 相关措辞改成 “texture latent compatibility / downstream appearance route”，除非 true GLB export 在 24 小时内成功并渲染出可用图。

## 4. 最危险缺口

1. **没有 final paper-quality textured OBJ/GLB render**
   - 当前最危险。SIGGRAPH Asia 视觉审稿不会只接受 PBR voxel token 数。
   - 已有路径：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/paper_quality_renders_20260508/blender_tiles/vine_d5_compete_iso.png`
   - 但该图是 neutral material，不是 true textured asset。

2. **Naturalization gain 证据不够干净**
   - Proposal 的 central hypothesis 是 generator naturalizes transformed patches。
   - 当前最强结果其实是 projection/stability；copy-paste/no-denoise/local denoise 对照还不够系统。

3. **Baselines 未统一 render protocol**
   - 传统 procedural、one-shot Trellis2、image-entry、direct coordinate、full flow、masked weak、projection-stabilized 都需要同一 camera/material/contact sheet。
   - 否则会被认为是 cherry-picking。

4. **主视觉过度依赖 Trellis example `04` vine root**
   - 这可以接受，但必须诚实表述 root-quality dependence。
   - tree `09` generalizes but semantics dominates；DLA blocky；lattice more like scene patch。

5. **Expressive growth 与 clean topology 尚未同时解决**
   - `compete` 稳但保守；`compete_fork`/`fork_side` 更有 growth 但碎片/bridge geometry 风险高。
   - attachment-aware 当前还粗糙，不能当最终方法。

6. **Related work positioning 仍危险**
   - 需要把贡献从 Trellis editing / inpainting 中区分出来：这里的关键是 repeated recursive operator stability，而不是 single edit。

## 5. 未来 24 小时优先级

1. **先锁定主 claim**
   - 主 claim：Projection-Stabilized R-SLG for finite-depth recursive 3D asset growth。
   - 暂停把 Droste/isometric/true infinite 放在主贡献中。

2. **完成或明确降级 true textured GLB**
   - 继续 remote smoke：
     - log：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/textured_glb_vine_d5_compete_s5_inference_20260508_131955.log`
     - output：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/siga_textured_glb_export/textured_glb_20260508/vine_d5_compete_s5_inference`
   - 若成功：立刻本地 Blender 渲染 textured GLB。
   - 若失败：论文内明确写 texture route is compatible but final PBR export is an engineering limitation / future work；主图用 neutral material。

3. **做一张可投稿方向的 teaser draft**
   - 候选：
     - `vine_d5_compete_iso.png`
     - `shaded_vine_d5_projected_loop_final_s5_20260508.png`
     - `strict_projection_vine_d5_20260508.png`
     - `attached_projection_vine_d5_compare_20260508.png`
   - 不要混用 scatter preview 和 shaded mesh；优先 Blender/Cycles neutral render。

4. **补统一 baseline/result matrix**
   - 至少 4 rows：
     - pure procedural / scaffold baseline；
     - one-shot or image-entry Trellis2 failure；
     - direct sparse grammar without per-depth projection；
     - projected R-SLG。
   - 至少 3 columns：
     - vine/root；
     - tree；
     - DLA/porous stress。

5. **补 projection 定量表到本地 docs**
   - remote 已有：
     - `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/docs/siga_projection_metrics_20260508/projection_metrics_table.csv`
     - `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/docs/siga_projection_metrics_20260508/projection_metrics_table.md`
   - 需要同步到 local docs，方便论文引用和防丢。

6. **补 method figure**
   - 一张图必须画清楚：
     - mesh root；
     - encode to sparse SLAT；
     - grammar operator；
     - decode；
     - Project；
     - re-encode loop；
     - texture/render path。

7. **对 DLA/porous 立即降级**
   - 除非找到更好的 coral/crystal root，否则 DLA 不进 teaser，不做主结果，只做 stress test。

8. **主线程改 paper_siga/main.tex 时的具体方向**
   - Contributions 改成 sparse grammar、projection-stabilized recursion、occupancy competition operator、stability-expression analysis。
   - Results 第一段写 projection table，而不是泛泛说 preliminary。
   - Limitations 明确 texture/rendering、root dependence、expressive seam blending。

## 6. 一句话结论

昨晚 prompt 的“递归生成增长”主问题已经收敛出一个可写论文的方法核心：**在 mesh-derived Trellis2 sparse 3D state 上做递归 grammar，并把 projection 放进递归映射中控制误差放大**。但“高质量带材质递归 3D asset”和“generator naturalization 明显优于 copy-paste”的证据还没达到 SIGGRAPH Asia 主结果标准。未来 24 小时应围绕 vine/projected/compete 把主图、projection 表、统一 baseline 和 texture/export fallback 做实。
