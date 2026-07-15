# PS-RSLG 方法图 TOG 风格草案建议

创建时间：2026-05-09  
草案脚本：`scripts/figures/compose_method_system_ps_rslg_tog_draft_20260509.py`  
输出图：`paper_siga/figures/method_system_ps_rslg_tog_draft_20260509.png`  
附加导出：`paper_siga/figures/method_system_ps_rslg_tog_draft_20260509.pdf`

## 对当前 v3 图的判断

`method_system_ps_rslg_v3_20260509.png` 的方法逻辑是对的：projection 位于每一步递归转移内部，re-encode/update memory 再回到 sparse state，能支撑主 claim。

主要审美风险是：

- 背景为暖白，和当前纯白渲染协议不一致。
- 外层大框、多个卡片、底部三块职责摘要让图更像 slide/PPT，而不像 SIGGRAPH/TOG 主文方法图。
- 文字密度偏高，读者容易在 responsibility summary、公式和节点说明之间分散注意力。
- 右侧 export 是抽象柱状图，缺少真实 mesh/GLB visual anchor。

## 建议的主文图方向

更像 TOG/SIGGRAPH 的版本应保留一个主视觉层级：

```text
root condition
-> sparse state
-> grammar
-> masked prior
-> decode
-> projection
-> re-encode
-> update memory
-> sparse state
```

图内只需要让 reviewer 读出三件事：

1. Grammar owns recursive topology.
2. Projection is inside every recursive step.
3. Frozen generator contributes masked local realization, codec, and export, not global topology.

底部解释性 bullets 建议移到 caption 或正文，不放在图里。

## 配色建议

采用 Okabe-Ito 风格色弱安全配色，并用位置/线型冗余编码：

- Grammar / handles：green `#009E73`
- Sparse codec / encode / re-encode：blue `#0072B2`
- Projection：vermillion/orange `#D55E00`
- Frozen prior / decode：neutral gray `#7B858F`

避免：

- 大面积渐变、阴影、彩色背景块。
- 同色系蓝绿过多导致模块不可分。
- 使用暖灰/off-white 作为画布背景。

## 版式建议

- 白底 `RGB(255,255,255)`，不要平台、投影、卡片阴影。
- 只保留一条强主循环；export 作为右侧窄列。
- 节点边框可以比填充更重要：白底空心框 + 顶部短色条，比整块浅色卡片更像论文图。
- 标题可比 v3 小，caption 承担解释工作；若放入 `figure*`，标题甚至可以从图内移除。
- 真实 mesh 小图只作为视觉锚点，不要把方法图变成结果图；最终可替换为 camera-matched, pure-white renders。

## 当前草案说明

新草案脚本使用已有纯白 mesh renders 作为接口占位：

- Root condition：projection ablation 的 vine per-depth render。
- Output assets：connected scaffold v2 HQ 的 bismuth、pyrite、volumetric coral/octopus pure-white renders。

这些路径集中在脚本顶部 `THUMBNAILS` 字典中，后续可直接替换为最终选定 case。脚本不运行重实验，不调用 Blender，只合成已有 PNG。

## 推荐下一步

- 若要进主文 Method overview：优先使用新草案作为版式方向，但建议在 LaTeX caption 中解释公式和模块职责，而不是把更多文字塞回图内。
- 若需要更保守版本：保留 v3 的逻辑结构，删除底部三块 summary，背景改纯白，右侧 export 换成真实 mesh 缩略图。
- 最终提交前需要统一所有图的字体、线宽和色条高度，避免方法图、metric 图、mesh showcase 图看起来像来自不同系统。
