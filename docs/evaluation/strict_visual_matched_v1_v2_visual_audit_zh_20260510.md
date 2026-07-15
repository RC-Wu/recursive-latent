# strict visual matched V1/V2 视觉审计（2026-05-10）

范围：只根据本轮给定状态整理视觉审计结论；不重跑远端、不修改代码、不补看未给定图像之外的额外实验。

## 1. 输入产物

| 批次 | 状态 | contact sheet |
|---|---:|---|
| V1 | 远端 `16/16` Trellis2 textured GLB 成功 | `visuals/strict_visual_matched_texture_zoom_20260510/strict_visual_matched_texture_contact_sheet_20260510.png` |
| V2 | 远端 `8/8` 成功 | `visuals/strict_visual_matched_texture_v2_zoom_20260510/strict_visual_matched_texture_v2_contact_sheet_20260510.png` |

## 2. 总体结论

V1 证明 strict visual matched 远端纹理 GLB 管线已经能批量跑通，但多数 case 仍然是“结构/算子标签存在，视觉语义不足”。主要问题是 L-system 和 Space Colonization 结果球团化，DLA 结果 voxel/blocky，radial 结果稀疏；相对可保留的候选是 pyrite/bismuth 一类有晶体/矿物视觉价值的输出。

V2 的改动方向正确：针叶、纤维、平滑 capsule 和 radial ring 明显缓解了 DLA blockiness 与 radial 稀疏问题，root / SC root 更接近根系目标。但 V2 仍不能整体进入主文正例：pine/crown 仍偏刺球或灰白团块，DLA 仍像管线骨架而不是真正珊瑚。

主文策略应保持保守：只把“视觉任务已经可读、且不靠解释才能识别”的 case 放进正图；把跑通但语义不稳的 case 放入 appendix/failure 或下一轮筛选池。

## 3. 分 case verdict

| Case 类别 | V1 verdict | V2 verdict | 是否可进主文 | 主要理由 |
|---|---|---|---|---|
| L-system pine / canopy | Reject | Reject / appendix only | 否 | V1 明显球团化；V2 虽引入针叶方向，但整体仍偏刺球，缺少可读 trunk-to-branch hierarchy、层级分叉和 canopy silhouette。 |
| Space Colonization crown / bush | Reject | Borderline reject | 暂不进主文 | V1 球团化；V2 crown 仍灰白、团块或刺球感强，SC 的 attractor-driven branch readability 不足。若主文需要，只能作为“未达标的 matched-mode attempt”。 |
| Root / SC root network | Weak / hold | Keep as candidate | 可进候选池，需再筛 | V2 的纤维/root-like 改动有效，root / SC root 更像根系，视觉语义比 V1 明显增强。进入主文前仍需确认根须层级、主根/侧根关系和材质稳定性。 |
| DLA coral / frontier | Reject | Hold as stress case | 暂不进正例 | V1 voxel/blocky；V2 平滑 capsule 降低块状感，但仍像连接管线或骨架网络，不像真实珊瑚的分枝、孔洞、表面粗糙与局部生长纹理。可作为 DLA repair/naturalization 中间证据。 |
| Radial ornament / ring | Reject | Keep as candidate | 可进候选池，非最终 | V1 稀疏；V2 radial ring 改善了整体闭环与密度，可读性提高。但还需验证是否有足够的径向重复、环面厚度一致性和局部细节，不宜直接写成最终强正例。 |
| Pyrite | Keep as candidate | Keep as candidate | 可考虑主文，需精选 | V1 已有候选价值；矿物/晶体任务与 Trellis2 textured GLB 外观较匹配。若几何不过分块状、纹理清楚，可作为 hard-surface/mineral 正例之一。 |
| Bismuth | Keep as candidate | Keep as candidate | 可考虑主文，需精选 | V1 已有候选价值；阶梯晶体/金属矿物视觉语义较强。主文使用时应避免把它解释成 DLA，宜归入 ordered crystal / transform / lattice 类。 |

## 4. 主文准入建议

### 4.1 可优先考虑进主文

1. **pyrite / bismuth**：当前最接近 paper-facing textured asset 的矿物/晶体类候选。主文中应定位为 ordered crystal、mineral 或 transform/lattice 风格，不要混称为随机 DLA。
2. **V2 root / SC root**：作为 root-like recursive growth 候选有进步，但需要从 8 个结果里严格选最可读的一两个，并补 zoom 到主根、侧根、末端纤维。

### 4.2 暂不进入主文正例

1. **L-system pine / canopy**：V2 仍偏刺球，不能支撑 L-system pine 成功。
2. **SC crown / bush**：仍偏灰白团块或刺球，缺少 SC 结构可读性。
3. **DLA coral**：blockiness 虽改善，但当前像管线骨架；不能写成真正珊瑚。
4. **radial ring**：可以保留为候选，但需再提高环形结构厚度、重复性和材质辨识度后再决定。

## 5. V3 建议

### 5.1 L-system / pine / crown

- 保留显式主干、一级枝、二级枝和 terminal tips；自然化只允许发生在 tip 或叶簇局部，不能把整棵树抹成球团。
- pine 目标要从“刺球”改为“中心主轴 + 分层轮生枝 + 稀疏针叶束”，减少全向尖刺。
- crown 目标要固定颜色和材质：减少灰白石膏感，增加枝条/叶簇的颜色分层或 roughness 差异。

### 5.2 Root / SC root

- 沿 V2 的纤维/root-like 方向继续做，但加入粗细层级：主根更粗、侧根更细、末端纤维更密。
- 增加 root path 可读 zoom：根基、分叉节点、末端须根各一处，避免 contact sheet 中只看到毛团。
- 对 SC root 使用相同 attractor/root policy，避免“像根系”但不再对应 SC 规则。

### 5.3 DLA / coral

- 不再只用平滑 capsule 连接 hit set；需要加入 coral-specific 局部形态：分枝端头膨大、孔洞、粗糙表面和非均匀半径。
- 保留部分 DLA frontier 粒度，但避免 voxel cube 与直管骨架两种极端。
- 增加 fake-bridge / over-smoothing 负例对照，证明 V3 不是简单把稀疏点用管道连起来。

### 5.4 Radial / ring

- 继续 V2 radial ring 方向，强化径向重复单元、环形闭合和厚度一致性。
- 对每个 radial case 输出正视图、斜视图和局部重复单元 zoom；若只在一个角度可读，不应进主文。
- 若 pyrite/bismuth 更强，可把 radial ring 作为 appendix 候选，不与矿物类争主图位置。

### 5.5 Pyrite / bismuth

- 作为 V3 主文候选优先打磨：统一白底相机、增加局部晶面/阶梯 zoom、控制过度块状或贴图噪声。
- 论文命名必须收窄为 mineral/crystal/lattice，不要声称其解决 DLA coral。
- 与传统 baseline 对比时应强调“可控递归/变换结构 + 纹理资产质量”，而不是只看连通性。

## 6. 严格结论

V1 是成功跑通的纹理 GLB 批处理基线，但视觉上只有 pyrite/bismuth 明显有主文候选价值。V2 是有效的方向修正，尤其改善 root、SC root、radial 和 DLA 的第一层形态问题；不过 pine/crown 与 DLA coral 仍未达到 strict visual matched 的 paper-grade 标准。

下一轮 V3 应从“让每类都能生成”转向“每类只保留可识别的视觉语义”：矿物类优先冲主文，root 类进入候选池，pine/crown 与 DLA coral 继续作为重点失败项修复。
