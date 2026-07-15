# 主消融视觉重做计划 2026-05-12

## 2026-05-12 纠偏：真实 OURS case 驱动

用户明确要求：本任务不能再用本地随机生成的示意图，也不能把 PPT 当成实验本身。PPTX 只允许作为最终排版容器；子图内容必须来自我们方案的真实生成 case 或围绕真实 OURS case 做出的完整消融。

本轮 target 更新为：

1. 优先从已有远端/我们方法生成结果中找视觉最佳、语义可识别的真实 OURS case。
2. 对这些真实 case 做 matched ablation：projection 侧补齐 no projection / final-only / prune-only / connector-aware / full PS-RSLE；naturalization 侧补齐 rule-only / no-N / weak / global / masked-no-proj / OURS。
3. 若已有 case 不足，则连接 `a100-2`，只用 GPU `4/5/6/7` 中最多两张卡继续生成和微调 OURS；远端存储上限按用户新要求放宽到 `200GB`，但仍清理明显失败、重复、低清缓存。
4. OURS 必须在最右列，必须是视觉最佳列；baseline 可以且应该暴露对应失败模式，但不能用假示意替代真实消融结果。
5. 每组实验至少两个不同 case：对象要能一眼看出是什么，并展示递归结构。Projection 和 masked naturalization 两边不能复用同一 case。

废弃路线：

- 本地 deterministic/random schematic panel；
- 纯 PPT 形状/示意图；
- 只用 caption 声称“OURS 最好”但子图不是同一真实 case 的 matched ablation；
- 未记录远端命令、manifest、mesh/render provenance 的图。

允许路线：

- 使用已有我们方法远端生成的 OBJ/GLB/texture/render 作为 OURS，然后重跑或构造同 case 的真实 ablation rows；
- 为保证视觉最佳，对 OURS 方法参数、grammar、projection/naturalization/postprocess 做合理微调，但必须记录为 full PS-RSLE/OURS 设置；
- baseline 采用相同 root/guide/seed/相机下禁用或弱化对应组件后的真实输出；
- 最终仍按用户要求先排入 PPTX，再由 PPTX 导出 PDF 引用到论文。

目标：重做 Experiment 2 projection ablation 与 Experiment 4 masked naturalization ablation 的主文视觉图。上一版图的对象不可读，无法让读者知道它是什么，也不能证明递归结构。新图必须满足两个硬条件：

1. 每个 case 必须是能一眼识别的具体 asset，并且必须展示递归结构，例如树苗/树枝、根叉、鹿角珊瑚、pyrite/cubic lattice。
2. `OURS` 必须固定在最右列，视觉效果必须是该行最完整、最清楚、最可发表的一列；其他方法必须和 `OURS` 拉开差距，明确暴露断裂、漂移、过剪、过平滑、孤立碎片或结构缺失。

## 验收标准

- 每个实验各两个 case，共四个 case，不重复。
- 每个 case 有 overview 与独立 zoom，overview 中用红框标出 zoom 区域。
- `OURS` 在每组图最右列。
- `OURS` 相对 root/rule-only 必须展示递归展开，而不是只有根。
- 其他列不能比 `OURS` 好，若视觉差距不明显就换 case 或调坏 baseline。
- 主文图仍必须 PPTX-first：先生成 PPTX，再导出 PDF，LaTeX 引用 PDF。
- 不覆盖用户当前 `paper_siga/main.tex` 与 `references.bib` 的既有修改，只在 ablation 图路径/caption 小范围合并。

## 本轮候选设计

### Experiment 2: Projection Ablation

展示 projection inside loop 对递归状态的作用。两行：

- `recursive pine sapling`：树干、二级分枝、叶簇/针簇。无 projection 有漂浮碎片；final-only 有终端团块但中间污染；prune-only 过剪；connector-aware 基本连接但不如 ours；`OURS` 是完整递归树苗。
- `pyrite cubic lattice`：金色 cubic/terraced lattice cluster。无 projection 有漂浮 cube；final-only 终端看似干净但重复块错位；prune-only 缺层；connector-aware 部分完整；`OURS` 是规则递归晶格。

列顺序：

1. no projection
2. final-only
3. prune-only
4. connector-aware
5. OURS

### Experiment 4: Masked Naturalization

展示局部 masked realization 在 projection 已经保证状态有效后改善接缝/局部表面。两行：

- `wooden root fork`：木质 Y 型根叉，多级 rootlets。rule-only 是裸骨架/裂缝；no-N 有硬接缝；weak 稍改善；global 过平滑；masked/no-proj 有碎片；`OURS` 是连续根叉。
- `staghorn coral branch`：鹿角珊瑚递归分枝。rule-only 断裂骨架；no-N 分节明显；weak 仍有硬节点；global 过肿；masked/no-proj 有孤立枝；`OURS` 是连续珊瑚枝。

列顺序：

1. rule-only
2. no-N + proj
3. weak + proj
4. global + proj
5. masked / no-proj
6. OURS

## 执行路径

1. 先从已有真实 OURS 输出中筛选 case：优先 `V24` 的 staghorn/frontier/pyrite/SC-tree 和 `V63` 的 distributed recursive bough；如果这些不满足视觉门槛，再远端继续跑新 case。
2. 为选中的真实 OURS case 补同 root/seed/guide/camera 的 matched ablation mesh 或 GLB。Projection 侧必须包含 no projection / final-only / prune-only / connector-aware / full PS-RSLE；naturalization 侧必须包含 rule-only / no-N / weak / global / masked-no-proj / OURS。
3. 每个 variant 必须写 manifest，记录 mesh/GLB 来源、生成脚本、远端命令、seed、projection/naturalization 开关、渲染相机和是否经过后处理。
4. 用 Blender/真实 mesh 或 GLB 渲染白底 overview 与独立 zoom，overview 里用红框标出 zoom footprint。PPTX 只读取这些真实渲染 PNG 进行排版。
5. 新增/更新 PPTX composer，生成两张 PPTX-first figure，并用 Keynote 导出 PDF。
6. 视觉 QA：检查对象可读性、`OURS` 最右且最好、zoom 框对应、baseline 差距和是否真实 provenance 完整。
7. 若不达标，换真实 case、微调 OURS 生成参数、重跑远端，或重设 baseline ablation 开关；不得用本地示意图补位。
8. 更新 `paper_siga/main.tex` 的两处 ablation 图路径和 caption，保留中文与用户已有修改。
9. 编译 LaTeX，检查 undefined refs/cites。通过后再考虑 stage/commit/push Overleaf。

## 远端策略

本轮以远端真实方法输出为唯一证据来源。允许在本地做轻量 manifest、PPTX、LaTeX、视觉 QA 和已生成 mesh/GLB 的渲染，但不允许用本地随机/示意/代理几何作为主文消融子图。

最多两个 SSH shell：

- Lane A：projection ablation 真实 case 生成与渲染，优先 GPU `4`。
- Lane B：masked naturalization ablation 真实 case 生成与渲染，优先 GPU `5`。

GPU 只允许使用 `a100-2` 的 `4/5/6/7`。远端项目总量上限 `200GB`，当前已知约 `146GB`，只清理明显失败、重复、低分辨率缓存，不删可复现 manifest、精选 render、最终 mesh/GLB、metrics。

## 2026-05-12 当前接手后的立即行动

- [ ] 查清 `V24` 和 `V63` 已有远端 OURS 输出是否足以做四个真实 case。
- [ ] 如果已有 case 足够，直接生成 matched ablation variants；如果不够，启动两个远端 lane 继续生成。
- [ ] 替换 `paper_siga/figures/ablation_pptx_20260512/` 中任何本地示意图遗留内容，只保留真实 case 渲染。
- [ ] `paper_siga/main.tex` 暂不更新到 20260512 新图，直到真实 case 视觉 QA 通过。
