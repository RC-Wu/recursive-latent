# 2026-05-11 论文重写中文修改日志

项目：Recursive 3D Generative Growth / PS-RSLG  
论文目录：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga`  
主线：从“广义 Recursive Sparse-Latent Grammar”收束为“Projection-Stabilized Execution for Recursive Sparse 3D Latents”

## 0. 本轮改写目标

这次重写不是继续堆系统功能，而是把论文改成一个清晰的 SIGGRAPH 叙事：递归 3D 生成的关键问题不是最终 mesh 有瑕疵，而是中间状态会被后续规则继续读取；一旦游离碎片、无效 frontier 或错误 handle 进入下一层，它就会污染整个 derivation。因此，文章主贡献应当是把 admissibility projection 放进每一层 recursive transition，让每一层进入下一步之前都恢复成 root-attached、可寻址、可复用的 active state。

## 1. 当前事实边界

可以写成主文强论点的部分：

- projection ablation 已经是最强证据，能支撑 per-depth projection 维护 root reachability、去除 orphan active handles、保持 handle survival。
- final-only cleanup 的反例很重要：它可以让 terminal occupancy LCR 很高，但递归 active state 仍然污染，因此必须在递归环内做 projection。
- masked local naturalization 可以写成 projected state 下的局部 surface/asset-quality 改善，不能写成全局 topology repair。
- Trellis2 one-shot、trivial latent copy、mesh-space generated-root copy 可以作为 novelty gate，证明没有 typed handle、projection、re-encoding 的 trivial recursion 不能替代我们的执行语义。

必须谨慎或放附录的部分：

- effective resolution / zoom retention 还是 proxy 和 selected visual，不能写成普适定量证明。
- same-root full matrix 仍不是全部闭合，只能写 closed subset 或 appendix status。
- DLA/coral/crystal 只能写 inspired scaffold 和 selected connected result，不能写物理模拟或严格拓扑证明。
- Hunyuan 不能写成完整全面 baseline 已完成，除非后续补齐证据。

## 2. 待改动清单

- 标题：从 grammar-first 改成 projection-stabilized execution-first。
- 摘要：逐句围绕 state-validity problem、state contamination、per-depth projection 组织。
- Introduction：第一段就讲 one-shot generation 和 recursive execution 的本质区别；类别只作为例子，不作为覆盖面 claim。
- Related Work：新增 structured/programmatic shape generation，并补 GRASS、StructureNet、ShapeAssembly。
- Preliminaries：改成 Problem Setup and Generator Interface，统一 `u_d=(V_d,F_d)` 和 `s_d=(u_d,A_d)`。
- Method：重排为 program state、rule proposal、recursive transition、admissibility projection、masked local realization、scope；删除技术报告式杂项和过强术语。
- Discussion/Conclusion：正文不要以 limitations 收尾；limitations 放讨论或附录，结论正面收束贡献。

## 3. 已完成修改记录

- 2026-05-11：新增本重写计划和中文日志文档，作为后续上下文压缩恢复入口。
- 2026-05-11：重写标题和摘要。标题从 “Recursive Sparse-Latent Grammars...” 改为 “Projection-Stabilized Execution for Recursive Sparse 3D Latents”，把论文身份从 grammar 大覆盖面收束到 projection-stabilized execution。摘要逐句改为 state-validity problem -> generator 缺口 -> PS-RSLG state coupling -> masked local realization / codec -> per-depth projection -> controlled finite-depth evidence -> export compatibility，从一开始就让 reviewer 记住“中间状态污染”这个核心发现。
- 2026-05-11：重写 Introduction。第一段不再列大量类别来暗示广义覆盖，而是直接区分 one-shot object synthesis 和 recursive execution；第二段尊重 classical procedural systems 的 explicit state 优势；第三段说明 sparse structured generators 提供 codec/local prior 但没有 recursive validity semantics；第四段把 naive routes 的失败解释成 recursive state contamination；贡献项改为 program state、typed rule proposals、per-depth projection、frozen-generator implementation 四条。
- 2026-05-11：重写 Related Work 并补正式引用。新增 structured/programmatic shape generation 小节，加入 GRASS、StructureNet、ShapeAssembly；BibTeX 通过 Crossref DOI 核验后写入 `references.bib`。Related Work 现在按 procedural recursive modeling、structured/programmatic shape generation、3D asset generators、3D editing/control、positioning 五段组织，避免写成 citation list。
- 2026-05-11：重写 Preliminaries 为 `Problem Setup and Generator Interface`。删去重复 related work 的 classical-system 细节，只保留 finite-depth recursive programs 和 frozen sparse generator interface。符号统一为 generator-native `u=(V,F)`，为后续 `s_d=(u_d,A_d)` 做铺垫，解决旧稿里 `z` 同时代表 latent 和 program state 的混乱。
- 2026-05-11：重写 Method 为 `Projection-Stabilized Recursive Sparse-Latent Execution`。主结构变成 Program State、Rule Proposals、Recursive Transition、Admissibility Projection、Masked Local Realization、Scope and Implementation Notes。新增独立 Admissibility Projection 算法和 execution invariant；把 “model-native projection” 改成 codec-mediated active-state projection；删除/压缩 operator admission、scheduler 权重、material/export/effective-resolution 等技术报告式杂项，让 projection 成为方法核心。
- 2026-05-11：重写 Discussion 并新增 Conclusion。正文不再以 limitations 收尾，而是在 Discussion 中集中说明有限深度、authored roots/rules、masked realization 与 effective-resolution proxy 的边界；Conclusion 正面收束 state contamination、active handles、per-depth projection、frozen generator codec 四个核心点。
- 2026-05-11：删除 `main.tex` appendix 中旧的中文内部写作方案。该段仍引用旧摘要、旧 `z` 记号和 grammar-first 说法，保留会污染投稿稿；新的中文计划和日志改由本文件和 `paper_rewrite_projection_stabilized_plan_20260511.md` 承担。
