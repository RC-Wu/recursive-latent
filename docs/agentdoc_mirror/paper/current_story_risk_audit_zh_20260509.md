# Current Story Risk Audit, reviewer view

日期：2026-05-09

范围：基于当前 `paper_siga/main.tex`、三份 2026-05-09 评估/视觉文档，以及 `/Users/fanta/Downloads/论文修改意见与reviewer批评整理.md`。本文只判断当前论文故事和 claim 风险，不修改 `main.tex`。

## 1. 当前主故事是否成立

严格审稿视角下，当前主故事**窄范围成立**，但不能按 teaser/gallery 的视觉宽度来写。

成立的主故事应当是：

> 冻结 3D 生成模型的 sparse latent 可以作为递归程序状态，但直接 sparse edit、全局 repair、final-only cleanup 都会让碎片或拓扑漂移进入下一层递归；因此需要把 projection 放进每一层递归 transition，把 connected voxelized support 变成递归不变量。Trellis2 texture/PBR export 只是对 selected projected meshes 的资产导出兼容性验证，不是结构正确性的证明。

这个故事与当前稿件的改写方向一致：主稿已经从“procedural + generator 互补”转向“generation-model-native recursive language”，并且用 `z_d=(V_d,F_d,A_d)`、规则模板、masked flow naturalization、decode-project-encode transition 来替代原先的大 tuple 和长公式。这个叙事比 reviewer 批评里指出的旧版本更合理。

但是证据只支撑**connected support / finite-depth recursive asset**，不支撑更强的“高质量 3D 生成统一解决方案”。最稳数值来自 `claim_aligned_metric_summary_zh_20260509.md`：vine textured stages 1-4 的 `occ_comp_6n=1`、`occ_lcr_6n=1.0`，root reachability proxy 为 1.0；`bismuth_hopper_depth`、`pyrite_lattice_depth`、`volumetric_coral_depth` 的 source stages 1-4 也都是 `occ_comp_6n=1`、`occ_lcr_6n=1.0`。这些足够支持“per-depth projected voxelized support remains connected across displayed depths”。

最危险的反证也同样明确：vine textured GLB raw face components 约 `85k-107k`，face LCR 只有约 `0.001-0.002`；pyrite 虽然 occupancy 连通，但 mesh component count 从 `1` 增到 `139`；DLA bridge ablation 的 occupancy components 仍为 `4-9`，best LCR 也只是 `0.961`，且存在 fake bridge / over-closing。审稿人如果按 mesh topology 或物理 growth 来读，当前故事会被直接击穿。

## 2. 现在可以写的 claim

可以写，但必须限定指标、对象和语气：

1. **核心 claim：per-depth projection 稳定有限深度递归的 voxelized occupancy support。**  
   支撑数值：vine textured stages 1-4 `occ_comp_6n=1`, `occ_lcr_6n=1.0`；`vine_d5_projected_compete` 的 root ratio 为 `1.0`，path span `1.048-1.307`，orphan tip proxy `0`。bismuth、pyrite、volumetric coral source stages 1-4 也保持 `occ_comp_6n=1`, `occ_lcr_6n=1.0`。

2. **per-depth projection 优于 direct recursion / final-only cleanup，尤其在 conservative competition operator 上。**  
   主稿 Table 1 的 matched ablation 可用：`vine compete d3` direct comps `2059`, direct LCR `0.9049`; final kept `2`, final LCR `0.9934`; per-depth raw comps `819`, per-depth kept `1`, per-depth LCR `1.0000`。`tree compete d3` 也类似：direct comps `3201`, final kept `4`, per-depth kept `2`, per-depth LCR `0.9949`。

3. **存在 stability-expression tradeoff。**  
   可以写 conservative competition 最稳，fork/side/radial/echo 更表达但风险高。数值必须同时给负面：`vine compete-fork d3` direct comps `11490`, direct LCR `0.5178`; final LCR `0.6863`; per-depth LCR `0.5758`。`tree compete-fork d3` per-depth kept `53`, LCR `0.6141`，不能包装成成功。

4. **Trellis2 texture/PBR export 对 selected projected meshes 技术可行。**  
   主稿 texture table 可写 export compatibility：如 `vine/root compete` GLB `26.81 MB`, shape tokens `1608`, PBR tokens `526818`; `tree compete` `27.59 MB`, shape tokens `3126`, PBR tokens `778755`; `crown portal` `38.48 MB`, PBR tokens `1495359`。但这只证明 selected assets 可以进入 texture/export path。

5. **传统 procedural scaffold 即使用同一 Trellis2 texture path，也不会自动变成 connected asset-ready mesh。**  
   传统 texture baseline 很有力：space-colonization root `218` occ comps, LCR `0.524`; tree `278`, LCR `0.364`; L-system branch `315`, LCR `0.115`; voxel DLA `2511`, LCR `0.002`。这支持“texture alone is insufficient”，而不是“我们全面优于传统方法”。

## 3. 仍然危险或不能写的 claim

不能写：

- “方法解决了 tree/root/vine/crystal/DLA topology。”当前只证明 voxelized 6N support 的连通性，且 raw GLB face fragmentation 很严重。
- “导出的 textured GLB 拓扑干净。”vine raw face components `85k-107k`、face LCR `0.001-0.002` 是直接反证。
- “DLA/coral 已经解决。”`dla_bridge_ablation` occupancy comps `4-9`，visual QA 有 fake bridge / over-closing；coral 只能写 grammar-native connected scaffold stress positive。
- “bismuth/pyrite 是真实晶体生长。”bismuth 可以写 bismuth-like connected scaffold；pyrite 可以写 lattice scaffold connected voxel support。不能写 crystallization、facet physics 或 face-welded topology。
- “材质递归一致。”现在的 texture/PBR export 是 selected projected mesh 的后处理兼容性，material coherence/category quality 仍不稳定。
- “density parameter 控制强且单调。”coral density 四个 GLB 都 `occ_comp=1`, `LCR=1.0`，但 occupied voxels 为 `8551, 9191, 7377, 8478`，不单调；box-count proxy `2.16, 2.11, 2.09, 2.09`，视觉差异也偏弱。

## 4. 传统 baseline texture 诊断如何放进论文

应放成**诊断性 baseline**，不是主 baseline matrix 的替代品。

推荐论文位置：Results 中 texture/export 小节之后，或 ablation/diagnostic subsection。它回答的问题是：如果传统 L-system / space-colonization / DLA 也拿到同一个 Trellis2 texture/export path，是否就足够？答案是否定的。四个传统 baseline 都能导出 colored GLB，但 occupancy 连接性很差：root `218 / 0.524`，tree `278 / 0.364`，L-system `315 / 0.115`，DLA `2511 / 0.002`。这正好服务核心论点：问题不是缺纹理，而是递归状态每一步必须 connected / projectable / reusable。

写法要克制：

> To isolate the role of texture export, we pass representative procedural scaffolds through the same Trellis2 texture path. Although GLB export succeeds, the occupancy-component counts remain high and LCR remains low, indicating that material transfer alone does not produce connected recursive assets.

必须加 caveat：这不是 matched same-root、same-depth、same-seed 的最终公平 baseline matrix；输入类别、root 和 guide 没有完全统一；指标是 GLB vertex-occupancy proxy，raw face components 会受 UV/material islands 影响。

## 5. 哪些图应主文，哪些放补充

主文建议只保留能直接服务 claim 的图：

1. **方法图**：保留但要压缩成 recursive sparse-latent program execution，不要像系统海报。它服务“grammar owns topology, generator supplies local priors, projection inside transition”。
2. **claim-aligned metric summary**：适合主文，因为它明确把 occupancy connectedness、mesh/face caveat、DLA negative 标出来。caption 需要正式化，避免 “current draft”。
3. **projection ablation table / curve**：必须主文。Table 1 是目前最像论文证据的结果，尤其 `vine compete d3` 和 `tree compete d3`。
4. **vine depth textured strip**：可以主文，作为 selected textureable recursive asset；caption 必须强调 fixed guide、true Trellis2 textured GLB、非 ablation。
5. **traditional baseline texture diagnostic**：可以主文或紧邻主文的 appendix。若主文篇幅有限，主文给 2x2 小图 + 数值表，完整图放补充。

更适合补充：

- `result_matrix_mesh_20260509.png`：像状态总览/gallery，协议混合，容易被 reviewer 读成 claim 过宽。
- `depth_parameter_mesh_showcase_20260509.png`：控制 gallery，但强 claim 不够集中。
- `coral_density_param_showcase_20260509.png`：全部连通是优点，但视觉差异和数值单调性弱，适合 supplement 的 parameter-control evidence。
- bismuth/pyrite/coral textured showcase：如果主文需要展示非树类广度，只选一张最强的 bismuth 或 coral；其余放补充。pyrite 因 mesh components 到 `139`，主文必须谨慎。
- DLA/radial/echo 边界案例：放 supplement 或 failure/diagnostic appendix，不要放主结果核心。

## 6. 下一轮最关键实验

最关键不是再做更多漂亮图，而是补一个**同 root、同 depth、同 seed、同 renderer 的 tree/root/vine 公平 baseline matrix**。

最低可接受矩阵：

- Methods：L-system、space-colonization、direct sparse grammar、final-only cleanup、prune-per-depth、bridge-per-depth、proposed。
- Fixed controls：同 root/seed/depth/camera/renderer，必要时同 texture/export path 分开报告。
- Metrics：`occ_comp_6n`、`occ_lcr_6n`、root component ratio、path-to-root rate、orphan mass、orphan tips、tip count、branch nodes、path span。
- Visual QA：neutral front/side/top/iso，以及 root attachment、junction、tip zoom。

原因：当前最强 claim 是 branching/vine/root 的 per-depth projection 稳定性，但传统 baseline texture 诊断不是 matched matrix；branch/path proxy 也还没有系统覆盖所有 baseline。这个实验补上后，论文就能从“有说服力的研究状态报告”变成“围绕核心 claim 的可审稿证据链”。

第二优先级才是 bismuth/pyrite 的 facet/contact/symmetry/cavity 指标，以及 DLA/coral 的 frontier attachment、porosity/cavity、bridge survival、fake bridge / over-closing label。

## 7. 最重要的 5 条结论

1. 当前主故事可以成立，但只能写成“per-depth projection 在 finite-depth recursive sparse-latent programs 中维护 voxelized 6N connected support”，不能写成通用拓扑或材质成功。
2. 最强正证据是 vine/root/tree conservative competition：`vine compete d3` per-depth kept `1`, LCR `1.0000`；vine textured stages 1-4 `occ_comp_6n=1`, `occ_lcr_6n=1.0`, root ratio `1.0`。
3. 最大风险是指标错位：occupancy 连通不等于 raw mesh/GLB topology clean。vine textured GLB raw face components `85k-107k`、face LCR `0.001-0.002` 必须公开为 caveat。
4. 传统 baseline texture 诊断应作为“texture alone is insufficient”的辅助证据：四个传统 textured GLB 的 occ comps 分别为 `218, 278, 315, 2511`，LCR 分别为 `0.524, 0.364, 0.115, 0.002`。
5. 下一轮最关键实验是 matched same-root tree/root/vine baseline matrix；没有它，论文仍容易被 reviewer 认为 baseline 不公平、claim 过宽、实验像状态报告。

## 8. 产出文件

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/paper/current_story_risk_audit_zh_20260509.md`
