# PS-RSLG 方法总图 v3 设计说明

创建时间：2026-05-09  
图文件：`paper_siga/figures/method_system_ps_rslg_v3_20260509.png`  
附加导出：`paper_siga/figures/method_system_ps_rslg_v3_20260509.pdf`

## 设计目标

v3 图把方法主线从旧图的多面板系统清单，压缩成一个更适合 Method 开头的核心叙事：

```text
root mesh / condition
-> sparse latent state
-> grammar handles / rules
-> masked sampler / naturalizer
-> decode
-> projection
-> re-encode
-> update handles and continue recursion
-> textured GLB export at selected finite depth
```

重点是让读者一眼看到：projection 位于每一步递归转移内部，而不是最终 mesh cleanup。图中 projection 使用橙棕色强调框、粗边框和环内反馈箭头标出；re-encode 之后回到 update memory，再反馈到 sparse latent state，形成清楚的递归闭环。

## 视觉取舍

- 配色采用克制的蓝、青绿、绿色、橙棕四色：蓝色对应 sparse latent codec/export，青绿对应 masked generator prior，绿色对应 grammar-owned structure，橙棕对应 projection-stabilized state。
- 删除旧图中过多的 classical limits/evidence 子面板，只在下方保留三块职责摘要：grammar controls、projection stabilizes、generator contributes。
- 图中只保留必要的公式和短语，避免把 Method 公式完整堆进图内。
- 使用简单几何图标表示 mesh、sparse support、mask grid、projection prune/bridge 和 GLB export，不使用动物或奇怪装饰。
- 结构上采用左输入、中间递归环、右导出的论文图布局，适合 figure* 宽图。

## 覆盖的必要元素

- `root mesh / condition`：左侧输入面板包含 root asset、image/text/category/material condition 和初始 encode。
- `sparse latent state`：中央第一个蓝色节点显示 `z_d = (V_d, F_d, A_d)`。
- `grammar handles / rules`：绿色节点显示 handles 到 proposals/masks/tests，并列出 grow/branch、attach/bridge、copy/split/refine。
- `masked sampler / naturalizer`：青绿色节点显示 hard-clamp anchors 和 edited mask sampling。
- `projection`：橙棕色节点位于 recursive loop 内部，展示 orphan support 被 prune/bridge 后变成 connected asset。
- `re-encode loop`：projection 向下进入 re-encode，再进入 update recursive memory，并由大弧线回到 sparse latent state。
- `textured GLB export`：右侧导出面板包含 projected mesh、texture/PBR path 和 textured GLB export。

## 与旧图相比

旧图 `method_system_grammar_polished_20260508.png` 信息更全，但视觉层级较散：classical limits、evidence slots、operator equation 和多个子面板同时争夺注意力；projection 虽在中间 panel 中出现，但不够像“递归不变量的核心操作”。

v3 更适合替换 Method 开头总览图，因为它更直接服务当前 Method 文字的主 claim：

> Projection is inside the recursive transition, not a final cleanup pass.

建议替换旧图作为主文 Method overview。旧图仍可作为内部草稿或补充材料参考，但如果主文只放一张方法总图，v3 的叙事更集中、审美更干净，也更不容易被 reviewer 读成普通工程流水线。

## 使用建议

- 若替换主文图，建议 `main.tex` 中仍使用 figure* 宽图，并将 caption 聚焦在 `grammar owns structure + frozen generator supplies masked local realization + projection inside recursion + finite-depth GLB export`。
- 如果最终排版希望压缩高度，可以裁掉下方三块职责摘要，只保留上半部分主循环；当前版本保留这些摘要是为了草图自解释。
- 当前图是设计草图，不宣称展示真实实验输出；右侧 GLB export 是方法路径图标，不应在 caption 中描述为具体结果截图。
