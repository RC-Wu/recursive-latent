# 即时进展：Projection ablation mesh 图与 Coral extreme 参数图

时间：2026-05-09 11:15 CST

## 完成内容

1. 把 reviewer 修改意见文件纳入总任务。
2. 补齐 projection ablation 的真实 mesh/Blender 渲染图。
3. 生成更强的 coral density endpoint 参数控制实验，并完成 Trellis2 textured GLB 导出、Blender 渲染、指标统计和论文图。
4. 更新 `paper_siga/main.tex`，并成功重新编译 PDF。

## 新图

- Projection ablation mesh 图：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/projection_ablation_mesh_contact_20260509.png`
- Coral density extreme 图：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/coral_density_extreme_texture_20260509.png`
- 当前 PDF：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.pdf`

## 核心结果

Projection ablation conservative compete：

| case | direct raw comps | final-only raw comps | per-depth raw comps |
|---|---:|---:|---:|
| vine | 2059 | 2 | 1 |
| tree | 3201 | 4 | 2 |

Coral density endpoint：

| density | occ comps | occ LCR | faces |
|---:|---:|---:|---:|
| 0.25 | 1 | 1.000 | 71088 |
| 0.45 | 1 | 1.000 | 87256 |
| 1.35 | 1 | 1.000 | 190072 |
| 1.75 | 1 | 1.000 | 239736 |

## 判断

这两个补充都是真 mesh/textured mesh 证据，不是点云或 matplotlib preview。

Projection ablation 图适合进入主文，因为它直接支撑“projection inside recursion”的核心方法 claim。

Coral extreme 图比旧参数 sweep 更可用，可以作为 method-behavior/control figure，但仍不能写成严格消融或单调控制律。

## 仍需继续

- 清理 `main.tex` 中大量 revision trace；
- 把 Results 改成 claim-based structure；
- 把 classical limits 的长推导移到附录；
- 继续做 baseline/metric closure，尤其是传统方法、生成方法和 PS-RSLG 的公平协议；
- 继续推进 DLA/crystal 的真正连通和视觉质量，但当前不要把碎片修复负例写成成功结果。
