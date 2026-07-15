# 论文结构与 LaTeX 整理状态 2026-05-10

## 本轮修改范围

- 只修改了 `paper_siga/main.tex` 和本状态文件。
- 未修改 assets、scripts、visuals、figures 目录中的任何文件。

## 已完成

1. `Experiments and Results` 已重新组织为 claim-bearing 主线：
   - 任务定义与协议；
   - baselines/metrics；
   - per-depth projection ablation；
   - structural baselines 与 Gen-3D baseline 待补；
   - naturalization/export/effective-resolution claim gate；
   - boundaries 与 supplement placement。

2. 大部分 gallery/diagnostic figure 已移动到 `\appendix` 后的 `Moved Gallery and Diagnostic Figures`：
   - strict candidate screens；
   - claim-aligned metric summary；
   - surface voxel diagnostic；
   - result matrix；
   - vine/depth/guide sweeps；
   - latest textured contact sheet；
   - crystal guide sweep；
   - coral density sweep；
   - DLA bridge smoke test。

3. 附录结构已强化：
   - `\clearpage` 后进入 `\appendix`；
   - 新增 `Appendix: Supplementary Material Roadmap`；
   - 用 contents-style list 明确 appendix gallery、classical limits、scope notes。

4. `Operator Scheduling and Sparse Competition` 已改写为更具体的算法式 prose/formula：
   - 定义 candidate set；
   - hard feasibility：reachability/budget/compatibility；
   - sparse competition score；
   - NMS/top-k selection；
   - 添加 evidence/TODO 标记。

5. `Recursive Refinement Scope`、`Material Handles and Trellis2 Texture Export`、`Scope, Complexity, and Export` 已合并为 `Scope, Refinement, Material Export, and Complexity`：
   - 明确 finite-depth claim；
   - 加入 token-budget/refinement accounting；
   - 将 material/PBR 降级为 export compatibility；
   - 保留 resolution/efficiency TODO。

## LaTeX 编译状态

- 本地未找到 `latexmk`、`pdflatex`、`bibtex`、`pdfinfo`。
- 已尝试运行：
  - `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`
  - 结果：`zsh:1: command not found: latexmk`
- 因此本轮未能生成新的 PDF。
- 现有旧 `paper_siga/main.pdf` 仍存在，使用 `pypdf` 读取为 27 页；该页数是修改前/未重编译 PDF 的页数，不代表本轮修改后的最终页数。

## 仍需 TODO

- 跑 Gen-3D baseline：TRELLIS one-shot、TRELLIS.2 one-shot、Hunyuan3D 或 blocked status、mesh-space grammar、trivial latent transform、ours。
- 补 same-root projection matrix：traditional/direct/final-only/prune/bridge/proposed。
- 补 naturalization ablation：rule-only、no-N、weak blend、masked local-N、global-N、with/without projection。
- 补 effective-resolution 实验：two-level zoom、local detail metrics、face count、GLB size、runtime/memory、one-shot 对比。
- 补 operator scheduling evidence：active handles、candidate/rejected/accepted tokens、next-depth handles。
- 补 per-depth runtime/GPU memory/encode-decode-projection cost/token growth。
- 安装或提供本地 LaTeX 工具后重新编译并更新 page count。
