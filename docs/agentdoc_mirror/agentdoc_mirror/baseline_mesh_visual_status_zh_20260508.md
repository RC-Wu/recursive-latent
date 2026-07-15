# Baseline Mesh Visual Status - 2026-05-08

本文档记录把传统 space-colonization baseline 从诊断预览图切换到 mesh-based Blender/Cycles 渲染的状态。结论是：传统 baseline 已经有可引用的 OBJ mesh 与 Blender render，matplotlib contact sheet 以后只作为诊断，不作为论文视觉。

## 1. 输入

传统 baseline 输出目录：

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/traditional_baselines_space_colonization_20260508_v2`

使用的 OBJ：

- `tree_canopy/space_colonization.obj`
- `root_vine/space_colonization.obj`
- `bush_shell/space_colonization.obj`

这些 OBJ 来自 `assets/space_colonization_baseline.py`，本身是 tapered/tube mesh，不是点云或 matplotlib 图。

## 2. 渲染命令

使用本机 Blender 5.1.1：

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background \
  --python /Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/blender_render_recursive_mesh.py \
  -- \
  --out-dir /Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/baselines_space_colonization_blender_20260508 \
  --views iso front side \
  --samples 64 \
  --resolution 1400 \
  --case sc_tree=/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/traditional_baselines_space_colonization_20260508_v2/tree_canopy/space_colonization.obj \
  --case sc_root=/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/traditional_baselines_space_colonization_20260508_v2/root_vine/space_colonization.obj \
  --case sc_bush=/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/traditional_baselines_space_colonization_20260508_v2/bush_shell/space_colonization.obj
```

## 3. 输出

渲染目录：

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/baselines_space_colonization_blender_20260508`

主要图：

- `space_colonization_blender_contact_sheet.png`：3 cases x 3 views，全部由 Blender/Cycles mesh render 生成。
- `mesh_based_visual_status_contact_sheet.png`：传统 SC mesh 与已有 Trellis2 mesh/textured render 的快速对照。
- `sc_tree_iso/front/side.png`
- `sc_root_iso/front/side.png`
- `sc_bush_iso/front/side.png`

## 4. 视觉判断

传统 space-colonization baseline 的结构很清楚，能作为 graph/branch/coverage 的结构 baseline。它的弱点也很明显：几何是 tube/skeleton 风格，端点和交界处视觉较程序化，没有现代生成资产的局部材质和自然边界。这正好适合论文中的对比逻辑：

- 传统方法：结构控制强，mesh 可复现，但 visual/material asset quality 弱。
- 我们的方法：在保留递归/空间竞争结构的同时，通过 sparse generative representation 和 Trellis2 texture/export 提供更接近资产的输出。

当前这组图可以进入草稿作为 baseline visual row，但不能作为最终 head figure。最终版本需要：

1. 统一相机、统一光照、统一裁切；
2. 与 proposed 方法同 case、同 root/operator/depth 放入同一 figure；
3. 增加 metric table 或 curve，避免只靠视觉判断。

## 5. 关键 caveat

- matplotlib/scatter 版本只保留为快速诊断。
- 论文图必须从 OBJ/GLB 经 Blender/Cycles 或等价 mesh renderer 生成。
- 当前传统 baseline 没有 PBR/texture；这是公平对比时需要明确的 baseline 性质，而不是渲染失败。

