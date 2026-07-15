# Method overview polished figure notes

创建时间：2026-05-08

输出文件：

- `paper_siga/figures/method_system_grammar_polished_20260508.png`
- `paper_siga/figures/method_system_grammar_polished_20260508.pdf`

生成脚本：

- `assets/generate_method_system_grammar_polished_20260508.py`

## 设计目标

这版图把 Method 总图从工程流水线改成 SIGGRAPH 风格的分栏方法图。主线是 **Projection-Stabilized Recursive Sparse-Latent Grammar (PS-RSLG)**：formal grammar 负责递归结构和 typed symbols，冻结 Trellis2 负责 sparse latent state、local prior、decode/re-encode、projection feedback 和 asset export。

图中显式覆盖五个审稿人应快速读到的模块：

1. **Typed sparse-latent state**：`S_d = (C, F, U, A, B, M, H, K)`，强调 sparse support、typed symbols、masks/history/caches。
2. **Grammar rule proposals**：规则从 typed frame/region/level/attributes 产生 transform-copy、attractor/frontier 和 masked sampling proposal。
3. **Competition / projection loop**：把 `Prop -> Merge -> Comp -> N_theta -> Decode -> Project -> Encode` 放在递归闭环内部，突出 projection 不是 final cleanup。
4. **Classical limits**：IFS、L-system、space colonization、DLA/frontier、CGA/shape grammar 都作为禁用或限制 learned sampler/projection/sparse-latent state 后的退化实例。
5. **Outputs / evidence**：连接 mesh/GLB/render 输出和当前论文证据槽，包括 projection ablation、depth curves、LCR/components/token curves 和 texture/PBR compatibility。

## 视觉口径

- 采用克制的浅色分栏：蓝灰表示 state，淡紫表示 grammar，浅绿表示 loop，暖灰表示 classical limits，青灰表示 evidence。
- 主要元素是矢量 patch、arrow、small multiples 和短标签，避免大面积高饱和色块。
- PNG 用于快速预览，PDF 保持矢量输出，适合 LaTeX `figure*` 替换当前 draft overview。

## 建议替换方式

当前 `paper_siga/main.tex` 中的 draft 图可替换为：

```latex
\includegraphics[width=\textwidth]{figures/method_system_grammar_polished_20260508.pdf}
```

caption 建议继续沿用 Method 节现在的 formal grammar 叙述，但把 “Draft overview” 改成 “Overview”。
