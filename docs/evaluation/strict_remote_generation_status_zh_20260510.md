# 严格一对一远端生成 comparison 状态（2026-05-10）

本文只整理用户最新纠正后的 strict one-to-one remote generation 进展：最终 comparison 证据必须来自 `a100-2` 新生成的 PS-RSLG/Trellis2 textured GLB case，而不是本地已有资产筛选、root stamping、本地 mesh repair、2D crop、contact sheet 拼图或后处理。

## 1. 当前口径

最终主文可用证据必须同时满足：

1. 从传统 procedural task 出发定义 baseline：L-system pine/root/vine、space-colonization crown/root/bush、DLA/frontier coral/reef/crystal、IFS/transform branch/radial/lattice。
2. Ours 在 `a100-2` 上按同类、同递归/生长/变换模式新生成 textured GLB，并记录 seed、operator composition、root/source、controls、GPU 分配和 `summary.status=ok`。
3. 本地只做统一评估、白底 Blender overview、camera-level zoom、指标汇总和人工审计；本地处理不能替代远端生成。
4. 连通性通过不等于主文成功。每个候选还要过 category/mode readability、递归层级可读性、family-specific metric、mesh/PBR 质量和 selection budget 记录。

因此，早期从已有漂亮 GLB 挑 vine/tree/pyrite/coral 来配传统 baseline 的材料，只能作为 screening 或 protocol 参考，不能作为最终 paper evidence。

## 2. V1-V7 批次状态

| 批次 | 远端/本地状态 | 主要覆盖 | 当前判定 | 论文用途 |
|---|---|---|---|---|
| V1 `strict_visual_matched_texture_20260510` | `a100-2` 远端 16/16 textured GLB 成功，已拉回并渲染白底 zoom sheet | L-system、SC、DLA、IFS 全量初版 | 管线跑通，但 pine/SC 球团化，DLA 体素块状，radial 稀疏；pyrite/bismuth 相对可看 | 只作为远端管线 smoke run 和负面/边界筛选 |
| V2 `strict_visual_matched_texture_v2_20260510` | 远端 8/8 成功，已拉回并做视觉审计 | pine/root/SC root/DLA/radial 重点修正 | root/SC root、radial 有进步；pine/crown 仍刺球或团块，DLA 像管线骨架 | 中间结果；root/radial 入候选池，但非最终主文 |
| V3 `strict_visual_matched_texture_v3_20260510` | 远端 13/13 成功，已拉回并计算 surface metrics | 更丰富的 task-specific primitives | DLA/frontier 与 pyrite 指标较好；L-system pine/root、SC crown/root、radial r0 fragmentation 明显 | “视觉丰富但碎裂”的诊断，不建议进主文正例 |
| V3b `strict_visual_matched_texture_v3b_connected_20260510` | 远端 11/11 成功，occ64 r0 全部单连通、LCR 1.0 | connected occupancy/implicit scaffold | 连接性大幅修复，但多例变成 blocky/voxel-like scaffold | 连接性 ablation 强证据；主文候选需进一步视觉 QA |
| V4 `strict_visual_matched_texture_v4_*` | 多 seed 远端 12-case 批次完成；seed 20260510/20260511 均为 10/12 strict r0 single，其余近单连通，r1/r2 全单连通 | continuous implicit connected support | 连接性稳定，但 global implicit naturalization 把植物、根、DLA/coral 抹成 blob/blocky | 负面/中间 ablation：connected but over-naturalized；pyrite/radial/crystal 可保留候选 |
| V5 `strict_visual_matched_texture_v5_hybrid_20260510` | 远端 8/8 完成，已拉回并渲染三层 camera zoom；r1/r2 全单连通，r0 仅少量小组件且 LCR >= 0.9987 | hybrid explicit scaffold + connectors | 修复方向成立，但植物/根/SC crown 太杆状，DLA/coral 仍像块状石头 | 中间正证据，不够 main-paper 发表级；引出 V6 |
| V6 `strict_visual_matched_texture_v6_connectivity_*` | seed 20260510、20260700、20260800 均各有 11 个本地拉回 GLB；20260510 已有 surface metrics 和白底 zoom | pine/root/vine、SC crown/root/bush、DLA coral/frontier/crystal、IFS radial/lattice | 20260510 指标：r1/r2 全单连通；r0 近单连通，最弱 LCR 约 0.99797。pine/root/SC 可读性较 V5 改善，crystal/radial/lattice 更稳；DLA/coral 仍偏暗块状矿物 | 当前最重要的全族候选池；植物/SC/IFS 可进入主文候选筛选，DLA 需 V7 替换 |
| V7 `strict_visual_matched_texture_v7_organic_dla_*` | DLA/frontier/crystal focused run；202607xx、202610xx 两组各 8 个有 surface metrics，20261100 有 8 个 GLB 但尚缺 surface metrics | organic DLA coral/frontier + crystal boundary | 明显针对 V6 DLA 问题：smooth tube、porous/sheet frontier、brighter reef guide。多数 r0 单连通或近单连通，r1/r2 全单连通；仍需人工视觉 QA 和 baseline side-by-side | DLA/frontier 主文候选来源；crystal 只能在任务归属清楚时使用 |

## 3. 哪些是中间或负面结果

明确不应直接写成 main-paper 成功：

- V1 pine/SC/DLA/radial：远端成功但视觉语义不足；只能说明批量 textured GLB 管线跑通。
- V2 pine/crown/DLA：方向比 V1 好，但 pine/crown 仍不保留清晰层级，DLA 仍像管线或骨架。
- V3 L-system pine/root、SC root/crown/bush、radial：局部元素丰富，但 r0 fragmentation 明显；可作为 V3b 连接性修复的对照。
- V4 plant/root/crown/coral：连接性好，但 continuous implicit 把递归层级和 frontier 局部细节抹平，是“过度自然化”的负面 ablation。
- V5 plant/root/SC crown/DLA coral：r1/r2 单连通、r0 近单连通，但视觉仍过于 scaffold/杆状或块状；只能说 connectivity repair 有效，不能说最终视觉解决。
- 本地 naturalize/blocky mesh pilot：对 radial/transform fragmentation 有诊断价值，但会膨胀面积、吞掉 sheet/branch 细节；不能作为最终生成证据。

## 4. main-paper 候选池

当前较稳的候选方向：

1. **IFS / pyrite / lattice / radial**：V3b/V4/V6 的 lattice、radial、crystal 类在连通性和视觉任务适配上最稳，适合做非有机/transform 主文候选。注意 pyrite/bismuth 应归入 ordered transform/lattice/mineral，不要混称为 stochastic DLA coral。
2. **L-system root / pine / vine**：V6 比 V5 更自然，r1/r2 单连通，r0 近单连通；可进入候选池。最终是否进主文取决于白底 zoom 中 trunk/branch/root hair/tendril 层级是否无需解释即可读。
3. **Space-colonization root/crown/bush**：V6 的 SC root/crown 连接性和复杂度可用，优先检查 attractor-driven path-to-root、branch/leaf anchor 和 crown silhouette。若仍像厚壳或叶团，只能进补充。
4. **DLA/frontier coral/reef**：V7 是当前唯一应该继续主推的 DLA 证据来源。202607xx/202610xx 两组中，`v7_dla_coral_dense_porous_smooth_tips`、`v7_dla_coral_open_branching_*`、`v7_dla_frontier_*_reef_*` 都有远端 textured GLB 和 surface metrics；其中多例 r0 单连通，少数近单连通，r1/r2 全单连通。主文使用前必须人工确认 frontier attachment、porosity/cavity 和 coral/reef 语义。

建议主文只保留 4-6 个最稳行：一个 L-system plant/root，一个 SC root/crown，一个 DLA/frontier coral/reef，一个 IFS radial/lattice，再加 1-2 个强视觉补充。宁可少放，也不要把中间失败批次包装成成功。

## 5. DLA、非树与连通性问题如何被 V6/V7 改进

早期问题分两类：

- **拓扑/代理连通性问题**：V3 的 plant/SC/radial 很多独立 primitive 导致 r0 组件数高；V3b/V4 用 connected occupancy/implicit support 基本解决，但副作用是 blocky/blob。
- **非树视觉可读性问题**：DLA/coral/frontier 和 SC/plant 的连接性改善后，视觉仍会变成黑色矿物块、连续团块或裸杆 scaffold，不能支撑 strict matched task。

V6 的改进：

- 不再只依赖 global implicit blob，而是用连续主枝/根 spine、定向 needle/rootlet/leaf primitives、局部 panels 和 connector/bridge 来保持 single/near-single support。
- 20260510 metrics 显示 11 个远端 GLB 的 r1/r2 全部单连通；r0 最弱 LCR 约 0.99797，说明小碎片已被压到很小，但最终文本应写“r0 near-single, r1/r2 single”，不要夸成全 strict r0。
- 对 tree/root/SC/IFS 的结构可读性比 V5 好；但 DLA/coral 仍像暗色块状矿物，因此不能作为 DLA 主文定稿。

V7 的改进：

- 专门把 DLA/coral/frontier 从 V6 的低多边形/块状矿物改成 stochastic frontier tree、smooth branching tubes、rounded tips、porous bridge panels 和 brighter reef/coral guides。
- 已有两组带 surface metrics 的远端结果：202607xx 8 个、202610xx 8 个；多数 case r0 单连通或 LCR > 0.9975，r1/r2 全单连通。
- V7 解决的是 DLA/frontier 的“非树类视觉自然化”缺口，但还需要和传统 DLA baseline 做 side-by-side 白底 overview、camera zoom、frontier/path/porosity 指标后，才能进入 main-paper 正图。

## 6. 还缺什么

1. **最终选择表**：从 V6/V7 多 seed 中选 4-6 个 main-paper rows，并列出 reject count、selection rule 和失败原因。
2. **baseline side-by-side**：每个最终 ours 必须配同一 traditional target 的白底 overview 和 camera-level zoom，不能只放 ours contact sheet。
3. **family-specific metrics**：L-system 要 branch order/depth/token survival；SC 要 attractor coverage/path-to-root；DLA 要 frontier attachment、porosity/cavity、fake-bridge；IFS 要 orbit/copy survival/symmetry IoU。
4. **同一 GLB 绑定证据链**：每个入选 case 的 render、zoom、connectivity、mesh quality、CLIP/DINO、人审标签必须指向同一个 `a100-2` 新生成 `textured.glb`。
5. **V7 视觉审计**：已有 V7 metrics 和 zoom 产物，但仍需人工标注哪些像 coral/reef/frontier，哪些只是 mineral/crystal boundary。
6. **V7 seed20261100 补指标**：本地已有 8 个 GLB 和输入 manifest，但当前目录只看到 inputs/summary 与 initial metrics，缺 surface metrics；不能和 202607xx/202610xx 同等引用。
7. **论文措辞收缩**：不能说传统方法天然不连通；更准确的 claim 是 PS-RSLG 在同一任务模式下，经 projection/local naturalization/Trellis2 生成 PBR textured mesh asset，并在最终选中 case 上保持 connected/near-connected surface support 与更强 asset quality。

## 7. 当前一句话结论

严格一对一远端 comparison 已经从“本地挑相似图”纠正为 `a100-2` 新生成证据链：V1/V2 跑通但视觉弱，V3/V3b/V4/V5 构成 fragmentation -> connected blocky -> over-naturalized -> hybrid readable 的中间证据，V6 是当前全族候选池，V7 是 DLA/frontier 的关键修复批次。最终主文证据还必须从 V6/V7 中绑定具体远端 GLB、传统 baseline、统一 zoom 和 family metrics 后再定稿。
