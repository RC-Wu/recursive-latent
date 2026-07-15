# R-SLG 论文结构与实验部分最新完成度状态

日期：2026-05-10  
角色：本地 sidecar worker  
范围：基于 reviewer 批评整理、当前 publication structure / claim gate 文档、实验章节缺口审查，以及对 `paper_siga/main.tex` 中 4.7、4.9/4.10、appendix、TOC/roadmap、teaser 的只读检索。  
写入范围：仅本文档。未修改 `paper_siga/main.tex`。

## 0. 总体判断

当前状态可以概括为：

**已有结构化计划和 claim gate，但还没有完成最终投稿级重写。**

更具体地说，论文已经从“实验/图表状态堆叠”推进到一条更窄、更安全的主线：PS-RSLG 是一个 generation-model-native recursive sparse-latent execution framework；grammar 持有可继续执行的递归状态；frozen 3D generator 提供 masked local realization、codec 和 texture/PBR export；per-depth projection 防止 detached fragments 污染下一层 handles、frontiers 和 caches。

但 reviewer 批评中的核心问题仍未全部闭合：

- 方法部分虽然已经朝“核心状态 + 规则模板 + 执行算法 + projection/naturalization gate”移动，但还不能说已经是投稿级精炼版本。
- 实验章节已经有 claim-driven 的重排计划，也有 projection、gen3D baseline、masked naturalization、export/effective-resolution 的局部证据，但仍不是完整 matched ablation suite。
- 主文/appendix/supplement 的边界已有明确计划，`main.tex` 也已有 appendix roadmap；但主文仍混入若干 status/diagnostic 图表，尚需按 claim-bearing 标准最终筛选。
- 4.7、4.9/4.10、分辨率部分现在应被写成 gate / diagnostic / boundary，而不是完成的强结果。

因此，当前版本可以作为“下一轮投稿级重写的清晰施工图”，不能夸大为“实验和正文已经完成”。

## 1. 对用户大任务第 3 点的逐项状态回答

### 1.1 实验结构

**当前状态：部分成型，但仍需最终压缩和重排。**

已有文档建议把实验章节改成 claim-driven 顺序：

1. Tasks, Protocol, and Metrics
2. Per-Depth Projection Stabilizes Recursive State
3. Structural Baselines and Operator Admission
4. Ordinary Gen3D and Trivial Recursion Controls
5. Selected Connected Scaffolds and Export Compatibility
6. Naturalization Claim Gate
7. Effective-Resolution Diagnostics and Boundaries

`main.tex` 目前已经把实验统一在一个 `Experiments and Results` 章节下，且包含 task/protocol、operator screening、baseline/metrics、projection、structural/gen3D comparison、naturalization/export/effective resolution、boundaries 等内容。这比 reviewer 批评中的“第 4/5 章像状态报告”已有改进。

但仍未达到最终投稿级：

- 4.7 与 4.9/4.10 的内容仍偏状态汇总，需要进一步合并、降级和压缩。
- 主文仍保留了较多 selected showcase、texture/export、zoom/status 图表，可能让实验章节继续像“证据库存”而非“围绕少数 claim 的验证”。
- latent-vs-mesh、naturalization dropout、effective-resolution same-budget comparison、root/seed robustness 仍未闭合。

**安全表述：** 实验结构已有明确重排方案和初步实现，但最终稿应继续把主文收窄到 projection、gen3D/trivial controls、selected connected scaffolds、local naturalization gate、export compatibility 这几类可承载 claim 的结果。

### 1.2 Appendix 单开页 / 目录

**当前状态：方向正确，已有 appendix 单开和 roadmap，但还不是最终提交包拆分。**

只读检索 `main.tex` 显示：

- bibliography 后已有 `\clearpage` 和 `\appendix`。
- appendix 开头包含中文写作方案与重写审查记录。
- 后续有 `Supplementary Material Roadmap`，并列出 moved gallery、ablation status、classical limits、scope notes。
- roadmap 中明确写到正式 SIGGRAPH Asia submission 时，应把 distilled visual-only panels 放到 references 后允许的 figures-only pages，而 text-heavy diagnostics 留在 supplement。

这说明“appendix 单开页/路线图”已经有结构雏形。

但还需要注意：

- 当前 appendix 仍包含内部中文写作方案、TODO list 和状态性语言，投稿版不能照搬。
- 还没有一张最终 appendix/supplement index，逐项标明 figure/table 的 role、allowed claim、main/appendix/supplement/figures-only 去向。
- 主文不能依赖 appendix 图号完成核心论证；appendix 只能补充、诊断和暴露未闭合矩阵。

**安全表述：** appendix 结构已经搭好，但最终投稿前还需要拆分为正式 supplement、figures-only pages 和内部工作记录三类；当前 appendix 不是最终形态。

### 1.3 图表主文 vs appendix

**当前状态：已有清单级决策，但 main.tex 里还需要执行最终迁移。**

当前 claim gate 计划已经明确：

- 主文只保留 claim-bearing figures/tables。
- appendix 放 status table、diagnostic、failure-aware material、metric explanation。
- supplement 放大 gallery、guide sweep、candidate screen、visual QA、blocked baseline audit。

建议主文保留的核心材料包括：

- projection ablation 白底图与 projection 表；
- compact structural/gen3D baseline 表和一张 diagnostic contact sheet；
- selected connected scaffold 白底图；
- pyrite/coral 中少量 selected connected scaffold/export showcase；
- masked naturalization focused gate，若页数允许可放主文短节，否则移 appendix。

建议移入 appendix/supplement 的材料包括：

- effective-resolution proxy/status table；
- gen3D zoom diagnostic；
- ablation coverage/status inventory；
- guide sweep、candidate screen、strict matched weak rows；
- Hunyuan3D/TRELLIS non-2 blocked audit；
- DLA bridge smoke、boundary/failure gallery。

`main.tex` 目前仍在主文中放了 masked naturalization 图表、gen3D zoom、effective resolution status table、selected scaffold、pyrite、coral 等较多内容。它们都带有谨慎 caption，但最终投稿时仍建议再筛一轮：每张主文图只服务一个 claim，不能让 status/diagnostic 图抢占主线。

**安全表述：** 图表归位原则已经清楚，但迁移还没有最终完成。

### 1.4 4.7

**当前状态：应重写为 Naturalization Claim Gate；目前 main.tex 仍是较宽的混合小节。**

reviewer 批评要求 naturalization 不要写成抽象算子堆叠，而要写成 masked flow / local sampling，并强调 frozen generator 只在 grammar 指定 mask 内做 local realization，不做 global topology repair。

当前结构计划建议把 4.7 改为：

**Naturalization Is a Local Realization Operator, Not a Topology Repair Mechanism**

或更短：

**Naturalization Claim Gate**

`main.tex` 当前的 `Naturalization, Export, and Effective Resolution` 已经写了重要限制：masked naturalization 只作为 projected recursive state 下的 local surface/material realization operator，不是 global topology repair；global naturalization 只是 control。但这一节仍同时承载 export、effective resolution、selected showcase，负担偏重。

当前安全结论：

- 可以说 masked local naturalization 在 selected rows 中提供局部 surface/material realization 证据。
- 不能说 naturalization 已经解决 topology。
- 不能说完整 naturalization matrix 已闭合。
- 不能让 naturalization 替代 projection 的贡献。

**建议状态标记：needs rewrite / claim gated。**

### 1.5 4.9 / 4.10

**当前状态：应合并压缩；当前 main.tex 仍分成 naturalization/export/effective resolution 与 boundaries 两段。**

现有计划建议把 4.9/4.10 合并为：

**Export Compatibility, Effective-Resolution Diagnostics, and Boundaries**

合并后的主文功能应是收束，而不是新增强 claim：

1. 先讲 selected projected meshes can enter Trellis2 texture/PBR export path。
2. 再讲 effective resolution 目前只是 qualitative/proxy diagnostic。
3. 最后讲 aggressive fork/radial/echo/hard-DLA/post-hoc bridge/guide-sensitive/dirty texture/uninspected GLB 等放 supplement。

`main.tex` 当前 `Boundaries and Supplement Placement` 已经有这个意识，但仍作为独立小节，且前一节塞入了较多图表和状态性数字。最终稿应进一步减少主文库存感，把 texture QA 长表、zoom 弱图、guide sweeps、candidate screens 下沉。

**建议状态标记：structure planned / needs merge and prose cleanup。**

### 1.6 分辨率部分

**当前状态：有理论动机和 proxy/status 表，但没有完成强 claim 所需实验。**

reviewer 明确指出“递归精细化 / effective resolution”应该成为重要论点：递归程序可以把固定 generator 的 sparse latent capacity 转化为局部更高结构分辨率，而不是简单一次性 one-shot grid。

当前文档与 `main.tex` 已经做了两件事：

- 在方法的 scope/refinement 部分加入 token budget、terminal handles、local support 的解释。
- 在实验部分加入 two-level zoom diagnostic 和 effective-resolution proxy table。

但证据仍不足：

- 缺 same-token / same-face budget 的 one-shot vs recursive 定量比较。
- 缺严格定义的 minimum visible feature scale、terminal detail count、zoom retention score。
- 缺 handle-level detail survival after decode/project/re-encode。
- 当前 zoom 图和 proxy table 更适合 appendix/status，不足以支撑摘要或结论中的强分辨率 claim。

**当前可写：** selected recursive assets show qualitative/proxy diagnostics of local detail at attached regions。

**当前不可写：** PS-RSLG 已经定量证明 effective resolution 优于 one-shot generator，或 universal terminal-detail improvement。

**建议状态标记：important but weak/proxy-only gate。**

## 2. 当前完成度分级

| 模块 | 完成度 | 当前可用结论 | 主要风险 |
|---|---:|---|---|
| 论文主线 | 中等偏高 | 窄主线已明确：recursive state execution + per-depth projection | 仍需把 reviewer 批评中的故事线和方法抽象彻底投稿化 |
| 实验结构 | 中等 | claim-driven 结构已有计划，main.tex 已部分重排 | 主文仍偏证据库存，需压缩 |
| Projection | 较强 | conservative vine/tree subset 可作为主结果 | multi-seed、handle-level contamination、operator breadth 仍不足 |
| Gen3D / trivial recursion baseline | 中等 | Trellis2 one-shot、latent-copy、mesh-space partial 可作为 controls | Hunyuan3D/TRELLIS non-2、coral mesh-space、same-budget 不完整 |
| Masked naturalization | partial | selected rows 可支持 local realization gate | 完整 dropout matrix 未闭合，不能写 topology repair |
| Export / texture/PBR | 中等 | selected projected meshes 可进入 Trellis2 texture/PBR path | export 不证明 topology、material propagation 或 final asset quality |
| Effective resolution | 弱 / proxy | 可作为 qualitative diagnostic | 不能强 claim 定量优于 one-shot |
| Appendix/supplement | 中等 | 已有 clearpage、appendix、roadmap 和 moved diagnostics | 投稿版需移除内部计划/TODO 并建立最终 index |
| 图表投稿质量 | partial | 有若干白底、claim-bearing 候选图 | gallery/screen/status 图仍多，部分图有 PPT/裁切/artifact 风险 |

## 3. 下一步最小编辑顺序

如果只做最小文字和结构编辑，不新增实验，建议按以下顺序：

1. **先锁定主文实验骨架。** 把第 4 节压成 protocol、projection、structural/gen3D controls、selected connected scaffolds/export、naturalization gate、boundaries 六到七个 claim-driven 小节。
2. **重写 4.7。** 将 naturalization 独立写成 gate：masked local realization under projected state；明确不是 topology repair；完整 dropout matrix 未闭合。
3. **合并 4.9/4.10。** 写成 `Export Compatibility, Effective-Resolution Diagnostics, and Boundaries`，只留 3-5 段收束文字。
4. **迁移主文图表。** 主文只留 projection、compact gen3D baseline、selected connected scaffold、少量 export/naturalization gate；把 effective-resolution status table、zoom diagnostic、coverage/status inventory、guide sweeps、candidate screens 移到 appendix/supplement。
5. **给 appendix 建最终 index。** 每个 figure/table 标注 role、allowed claim、main/appendix/supplement/figures-only 去向，并检查主文是否依赖 appendix 图号完成核心论证。
6. **清理投稿危险措辞。** 删除或改写 draft、current、candidate、smoke、planned、blocked、User needs、local log 等内部工作语言；中文写作方案和蓝色 TODO 不应出现在投稿版正文。
7. **最后再决定是否补实验。** 若有时间，优先补 projection matched mini-matrix、latent-vs-mesh mini-matrix、naturalization dropout、effective-resolution same-budget comparison；否则所有相关结论必须保持 gate/diagnostic 语言。

## 4. 一句话结论

当前论文不是“已经完成最终投稿级实验重写”，而是已经具备一套清楚的 publication structure、claim gate 和图表分流方案；下一步最小工作是把 4.7、4.9/4.10 和分辨率部分全部降级为 gate/diagnostic/boundary 叙事，并把主文图表严格收缩到少数真正支撑核心 claim 的证据。
