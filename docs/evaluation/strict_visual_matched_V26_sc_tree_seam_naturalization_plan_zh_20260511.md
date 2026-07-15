# V26 SC tree seam naturalization 计划

日期：2026-05-11  
状态：active / targeted seam repair  
本地生成器：`assets/strict_visual_matched_cases_V26_sc_tree_seam_naturalization_20260511.py`  
远端 launcher：`assets/launch_strict_visual_matched_texture_V26_sc_tree_seam_naturalization_20260511.sh`

## 目标

用户指出 V24 的树枝和树冠仍不自然、有接缝。这个判断成立：V24/V25 的 SC tree 虽然 post-GLB surface connectivity 很强，但白底 zoom 中仍有粗硬主枝、截断管段、树冠分枝和主干之间缺少连续过渡的问题。

V26 不扩大 baseline 矩阵，只针对 `sc_tree_crown_260` 做 4 个预声明候选：

- 在 grammar 输入 OBJ 阶段加入 branch/crown junction band；
- 只在接缝区域加入 `junction collar / cambium sleeve / leafshield` 过渡几何；
- 使用低对比连续 bark/leaf guide，避免 Trellis 原生 UV/PBR 生成强环带或 material island；
- metadata 中记录 seam mask center/radius、collar count、leafshield count；
- 远端只用 GPU 4/5/6/7，缓存仍在项目目录，预计低于 24GB 新增结果。

## 与 V24/V25 的区别

V24/V25 主要优化整体 tree crown 连通性和 tapered support；V26 明确把“树枝-树冠接缝”作为一等目标。它不是最终图像裁剪或渲染遮盖，而是把接缝区域写入 grammar-owned naturalization mask，再生成新的 OBJ 输入送 Trellis2。

## 预声明候选

| case | GPU | 主要改动 |
|---|---:|---|
| `V26_sc_tree_crown_junction_collar_A_lowcontrast` | 4 | cambium collar + low-contrast bark/leaf guide |
| `V26_sc_tree_crown_leafshield_B_lowcontrast` | 5 | leafshield 覆盖硬管截帽，同时保持 SC crown |
| `V26_sc_tree_crown_cambium_sleeve_C_lowcontrast` | 6 | 更强 junction sleeve，只加在 seam band |
| `V26_sc_tree_crown_soft_canopy_D_lowcontrast` | 7 | 软树冠过渡，降低 trunk/crown 材质反差 |

## 验收门槛

- pre-export OBJ `largest_mesh_component_vertex_ratio >= 0.999`，且无 boundary tag；
- 每个 case 必须有 `seam_mask_center_count > 0`、`junction_collar_count > 0`；
- 远端 Trellis2 结果要有 `summary.json` 和 `textured.glb`；
- post-GLB surface metrics 不低于 V25 SC floor，优先 `r0 components=1, LCR=1.0`；
- 白底多级相机 zoom 中接缝不能再像硬管插入树冠；
- 如果 Trellis UV/PBR 仍出现 material island，则使用 object-space procedural PBR 做视觉候选，但论文口径必须写成 grammar-owned material/rendering route，不能写成 Trellis texture 已普遍解决接缝。

## 论文口径

可以写：V24/V25 暴露出 branch/crown seam 失败，V26 用 masked local naturalization 的 junction-band version 专门优化该局部过渡，并用 seam-focused zoom QA 筛选。

不能写：图像生成模型或 SDEdit 已经自动解决所有树冠自然性问题；也不能把 object-space PBR 当作 Trellis UV/PBR 的成功证明。
