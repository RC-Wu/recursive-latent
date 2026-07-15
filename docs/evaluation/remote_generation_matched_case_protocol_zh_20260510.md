# 远端生成严格一对一匹配实验协议（2026-05-10）

## 核心结论

本轮 strict one-to-one baseline comparison 不能再使用“传统 baseline 生成一个形状，我们从已有漂亮结果里挑一个相似图”的口径。最终证据必须从传统任务出发：传统方法生成什么类别、递归深度、空间布局和生长/变换模式，PS-RSLG 就在远端 `a100-2` 重新生成同类、同模式、同尺度复杂度的 textured GLB，再用 mesh/PBR/Blender 白底渲染和 camera-level multi-depth zoom 做比较。

本地只允许做三类事情：任务定义、清单/指标整理、GLB 的白底渲染与可视化审计。不能把本地 mesh repair、root stamping、2D crop、matplotlib/point-cloud preview 伪装成最终生成结果。

## 严格 matched-task 定义

一个 case 只有同时满足下面条件，才算严格匹配：

| 维度 | 要求 | 记录方式 |
|---|---|---|
| 传统任务优先 | 先定义 classical target，再定义 ours；不能先看 ours 再找类似 baseline。 | `traditional_target`、baseline generator、seed、depth。 |
| 类别一致 | tree 对 tree，root 对 root，vine 对 vine，coral/frontier 对 coral/frontier，IFS/radial/lattice 对 transform/radial/lattice。 | `family`、`match_target`、人审标签。 |
| 递归/生长模式一致 | L-system 要保留 symbol rewrite/depth/branch angle；SC 要保留 attractor competition；DLA 要保留 accretive frontier attachment；IFS 要保留 transform-copy/orbit family。 | `operator_composition` 与 controls。 |
| 尺度和复杂度可比 | 深度、节点数、分叉/吸引点/粒子/transform order 不能相差到改变任务。 | depth、node/particle/attractor counts、box dimension。 |
| 生成路径合规 | ours 必须由远端 Trellis2/PS-RSLG textured GLB 产生；最终图必须来自 GLB/mesh/PBR render。 | remote result path、`summary.status=ok`、GLB path。 |
| 展示方式一致 | baseline 与 ours 都用白底 overview + 相同尺寸 camera zoom；zoom 不是 2D crop。 | render manifest、zoom level、callout metadata。 |

## 为什么必须远端重新生成

1. 公平性：传统 baseline 的输出是任务实例，PS-RSLG 也必须生成对应任务实例；本地后处理或挑选已有 GLB 不能证明方法能执行该任务。
2. 可复现性：远端 run 记录 input OBJ、guide、manifest、metadata、seed、GPU 分组和 `summary.json`，比本地临时改 mesh 更可追踪。
3. 评价闭环：连通性、surface quality、CLIP/DINO、mesh quality 和 zoom 审计都应绑定同一个远端 textured GLB，而不是分散在不同来源的图。
4. 避免误导：V3/V3b/V4 已显示局部漂亮、全局连通、递归可读性三者会互相冲突；只有重新生成才能验证算法改动，而不是通过后期修图掩盖缺陷。

## V3 / V3b / V4 / V5 / V6 的角色

| 版本 | 角色 | 主要结论 | 论文用途 |
|---|---|---|---|
| V3 | rich primitive visual test | 局部元素更丰富，但 plant/SC/IFS branch 有大量独立 primitive，严格 r0 connectivity 不稳。 | 作为“视觉丰富但碎裂”的诊断，不进主文最终比较。 |
| V3b | connected scaffold test | 11/11 远端 textured GLB 完成，occ64 r0 全部单连通；但很多 case 变成 blocky/voxel-like。 | 可作 connectivity 修复证据和 ablation。 |
| V4 | continuous implicit connected test | 12-case 多 seed 远端完成；r1/r2 全单连通，r0 多数单连通或近单连通；植物、根和 DLA/coral 被抹成 blob/blocky。 | 用于证明 global implicit naturalization 的边界；pyrite/radial/crystal 可保留为候选。 |
| V5 hybrid | remote generated readable scaffold test | 远端 8/8 completed，已拉回本地并渲染白底三层 camera zoom。surface occupancy r1/r2 全部单连通；r0 有少量孤立面片但 LCR >= 0.9987。视觉上连通性方向成立，但 DLA/coral 仍块状，植物/根/树冠太 scaffold/杆状。 | 中间证据：证明 connectivity repair 有效，但不够主文发表级；V6 需要提升自然形态。 |
| V6 | paper-grade selection run | 应在 V5 结果基础上只重跑失败 family：特别是 pine/crown/root/coral 的类别可读性、DLA frontier 的孔隙/分叉、SC crown 的 crown silhouette。 | 最终主文 run；要求每个入选 case 同时过 matched-task、人审、连通和 mesh/PBR zoom。 |

V5 现有路径：

- GLB：`visuals/strict_visual_matched_texture_v5_hybrid_20260510`
- 指标：`results/strict_visual_matched_texture_v5_hybrid_20260510_remote/surface_metrics_occ64.csv`
- 输入 manifest：`results/strict_visual_matched_texture_v5_hybrid_20260510_remote/inputs/manifest.csv`
- zoom 渲染目录：`visuals/strict_visual_matched_texture_v5_hybrid_zoom_20260510`
- 白底三层 camera zoom contact sheet：`visuals/strict_visual_matched_texture_v5_hybrid_zoom_20260510/strict_visual_matched_texture_v5_hybrid_contact_sheet_20260510.png`

## 每类 traditional baseline 的一对一任务

| Baseline family | 传统任务 | PS-RSLG 必须执行的同类任务 | 当前候选状态 |
|---|---|---|---|
| L-system | pine canopy: depth-5/6 trunk, whorl branches, needles | symbolic rewrite -> whorled spine -> shared anchor tubes -> attached needle spurs | V5 有远端 GLB 和三层 zoom；r0 近单连通，但视觉偏 scaffold/杆状，不能定主文。 |
| L-system | root fan: downward fan, taper, root hairs | root rewrite -> fan spine -> shared anchor tubes -> attached root hairs | V5 有远端 GLB 和三层 zoom；r0 近单连通，但 root naturalness 不够，需要 V6。 |
| L-system | climbing vine: helical main chain, tendrils, leaves | curl rewrite -> main vine spine -> shared tendrils -> anchored leaf lobes | V5 r0 单连通，但仍需 baseline side-by-side zoom 和自然形态审计。 |
| Space colonization | tree crown: attractor-filled crown, terminal foliage | attractor competition -> node-parent branch graph -> terminal attachment scaffold | V5 有远端 GLB 和三层 zoom；r0 近单连通，但 crown 太 scaffold/杆状，不够发表级。 |
| Space colonization | root network: attractor-driven root/vine field | attractor competition -> root network spine -> root spurs -> terminal hairs | V5 有远端 GLB 和三层 zoom；结构复杂度高，但需要 V6 提升自然根系形态。 |
| Space colonization | bush/shell | attractor shell, competition, outward terminal tips | V4 覆盖但视觉块状；V6 需要 hybrid 重跑。 |
| DLA/frontier | coral cluster: stochastic nearest-parent attachment | random walk support -> nearest parent bridge -> welded coral tubes -> terminal tubelets | V5 有远端 GLB 和三层 zoom；r0 近单连通但有少量孤立面片，视觉仍块状，不够主文。 |
| DLA/frontier | frontier sheet / reef boundary | line seed frontier -> nearest parent bridge -> sheet spine -> boundary tubelets | V5 r0 单连通；但 DLA/coral/frontier 视觉仍偏块状，V6 需强化自然 coral/reef 形态。 |
| DLA/frontier | anisotropic crystal | stochastic/frontier or faceted mineral growth, not ordered IFS | V4 有候选，但语义边界风险高；V6 需要明确任务归属。 |
| IFS/transform | fractal branch tree | transform set -> repeated branch orbit -> projection schedule | V3b/V4 可候选；需保证不是随意 tree。 |
| IFS/transform | radial ornament order-8 depth-4 | radial orbit -> closed rings -> shared center spine -> inter-depth bridges -> teeth | V5 r0 单连通；当前是最清楚的 transform 候选之一。 |
| IFS/transform | pyrite/fractal lattice | transform-copy lattice/orbit with depth progression | V3/V4 强候选；适合作为非有机主文 case。 |
| IFS/transform | bismuth terrace/hopper | repeated stepped transform, faceted terracing | V4/V3 有候选；更适合 ordered-transform appendix 或 boundary。 |

## 指标表

| 指标组 | 具体指标 | 目的 | 通过线/解释 |
|---|---|---|---|
| Connectivity | surface voxel components at r0/r1/r2, LCR, occupied voxels, root-attached mass | 判断是否是可渲染、可追踪的单一资产支撑。 | 主文优先 r0=1；若 r0 近单连通，需 LCR >= 0.995 且碎片视觉不可见；r1/r2 必须为 1。 |
| Surface quality | face components, non-manifold edges, degenerate faces, normal consistency, watertight/repair status, triangle aspect ratio | 避免 paper figure 只是连通但 mesh 破碎。 | GLB loader ok；无明显破面/法线翻转；zoom 下不能有严重洞、飞面、异常尖刺。 |
| Geometry complexity | vertices/faces, occupied voxels, box dimension 32-96, depth/node/particle counts | 证明 ours 保留递归复杂度，而不是简化成 blob。 | 与传统任务复杂度同阶；box dimension 不能因过度 smoothing 明显塌缩。 |
| Semantic visual | multi-view CLIP/DINO prompt score: category prompt + material/PBR prompt + negative prompt | 检查 tree/root/coral/radial 等语义是否比 baseline 或 ablation 更清楚。 | 只作为辅助，不替代人审；需要 multi-view 而非单图分数。 |
| Matched-task fidelity | operator family match, silhouette match, depth/scale match, control-parameter correspondence | 防止“看起来漂亮但不是同一任务”。 | 每行必须有 `why_matches_traditional` 与 controls。 |
| Multi-depth zoom | overview + zoom_01/02/03 camera render, callout source, local detail survival | 展示递归深度、junction、tip、facet、attachment neck。 | zoom 必须是重新设相机渲染；不能用 matplotlib 或 2D crop 当最终证据。 |
| Runtime/resource | GPU id, seed, Trellis2 steps, texture resolution, render time, failure rate | 保证远端实验可复现、可扩展。 | 每批次记录 case list、summary status、失败/重跑原因。 |

## 如何展示我们的优势

主文叙事不应说“传统方法都不连通”或“传统方法质量差”。更公平且更强的说法是：

1. 传统方法给出清楚的递归规则和增长控制，但原生输出通常缺少 textured GLB/PBR asset quality。
2. PS-RSLG 在同一任务族中保留递归控制，并通过 projection / local naturalization / Trellis2 texture 生成可渲染 mesh asset。
3. V3 -> V3b -> V4 -> V5 的证据链说明方法不是靠挑图，而是在远端逐步解决三类冲突：fragmentation、over-smoothing、semantic readability。
4. Multi-depth camera zoom 应该突出传统方法较弱而 ours 较强的具体部位：branch junction、root hair attachment、coral frontier neck、radial ring bridge、crystal facet，而不是只放全景。
5. 指标表和图应绑定同一个 GLB：同一 `textured.glb` 同时提供 overview、zoom、connectivity、mesh quality 和 CLIP/DINO。

推荐图表结构：

| Figure/Table | 内容 | 目的 |
|---|---|---|
| Main matched comparison | 4-6 个最强 family，每行 baseline/ours overview + zoom | 展示同任务下 ours 的 PBR asset quality 和局部递归细节。 |
| V3/V3b/V4/V5 ablation | rich fragmented -> connected blocky -> connected implicit -> hybrid connected but still scaffold/blocky | 解释为什么必须远端重生成，并说明 V5 是有效中间证据而非最终主文结果。 |
| Coverage matrix | L-system/SC/DLA/IFS 到 PS-RSLG operator family 的映射 | 证明比较覆盖传统方法类别。 |
| Metrics table | connectivity + surface quality + semantic + zoom QA | 给 reviewer 可复查的硬证据。 |

## 当前还不够发表级的 case

| Case | 问题 | 处理建议 |
|---|---|---|
| V4 plant/root/crown | connected 但 global implicit 导致 blob/blocky，递归读法被抹平。 | 只做 ablation，不做最终主文。 |
| V4 DLA coral/frontier | 连接性好，但像红色团块，不像 accretive coral/frontier。 | 被 V5/V6 tube-frontier 取代。 |
| V5 pine / plant / SC crown | connectivity 方向成立，但整体太 scaffold/杆状，植物、根、树冠自然形态不够。 | 作为中间证据；V6 需要更自然的局部 naturalization 和 foliage/root morphology。 |
| V5 DLA coral/frontier | r1/r2 单连通，r0 LCR 高，但视觉仍块状，不像发表级 coral/reef/frontier。 | 主文前必须 V6 重跑，保留 frontier attachment 同时增强孔隙、分叉和局部材质。 |
| V5 r0 孤立面片 | r0 有少量小组件，虽然 LCR >= 0.9987，但 strict claim 仍需谨慎表述。 | 指标表写作“near-single at r0, single after r1/r2 dilation”；不写成严格 r0 全单连通。 |
| Anisotropic crystal / bismuth | 容易从 DLA 任务滑到 ordered mineral/IFS 任务。 | 只能在任务定义清楚后进入 appendix 或 transform section。 |

## V6 执行清单

1. 从 V5 8 个远端 GLB 和 contact sheet 中先做人审：category read、mode read、zoom read、material read 四项；当前结论是中间证据，不够主文发表级。
2. 对失败 case 只改远端 input/guidance/connector 策略并重跑，不在本地 repair。
3. 每个入选 case 必须补齐 baseline counterpart 的同视角白底 overview 与 camera zoom。
4. 计算同一个 GLB 的 connectivity、surface mesh quality、CLIP/DINO、多视角 prompt score。
5. 最终只把同时满足 matched-task、remote generation、mesh/PBR render、multi-depth zoom、metric pass 的 case 放入主文；其余放 appendix/diagnostic。
