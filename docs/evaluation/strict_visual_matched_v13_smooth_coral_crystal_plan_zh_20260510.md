# V13 Smooth Coral/Crystal Strict Matched 方案

日期：2026-05-10

## 背景

V12 的 dry-run 指标通过：单组件、连通比例、manifest 和远端约束都正常。但主线程视觉审核认为它仍然失败，主要问题是：

- 枝干像圆柱杆；
- terminal 有截断端；
- 表面复杂度偏低；
- crystal/frontier 边界仍不够自然。

V13 因此不再直接输出 welded skeleton tube/cylinder mesh。它只把 active-frontier skeleton 当作隐式场采样骨架，再通过 metaball/SDF-like density union 和 marching cubes 导出连续表面。

## 生成设计

V13 保留严格匹配元数据：

- `stochastic_frontier_attachment`
- `occupancy_exclusion`
- `connected_projection`
- `traditional DLA/frontier accretive attachment`
- fresh on `a100-2`
- GPU 只使用 `4,5,6,7`
- 不做本地结果挑选，不复用 V1-V12 输出

视觉输入改为：

- active frontier skeleton 生成节点和边；
- 在边上密采样 metaball，形成连续有机主体；
- terminal 加多级 rounded lobes，避免平切口；
- tips 附加短 micro-branches；
- 沿边界添加 ridge-line density；
- 用浅 subtractive pores/dimples 增加珊瑚表面复杂度；
- crystal case 使用更低噪声和扁平 ridge ellipsoid，避免块状碎片。

## Case 组成

共 8 个 case：

- 2 个 smooth staghorn coral；
- 2 个 smooth table coral；
- 2 个 smooth frontier sheet；
- 2 个 smooth crystal ridge。

每个 case 都输出：

- OBJ；
- guide PNG；
- metadata JSON；
- manifest row；
- initial mesh metrics；
- a100-2/gpu split 文本。

## 本地验证门槛

本地 dry-run 必须满足：

- `mesh_component_count == 1`；
- `largest_mesh_component_vertex_ratio == 1.0`；
- 元数据声明 `direct_tube_mesh == false`；
- `implicit_grid_resolution >= 68`；
- `rounded_terminal_lobe_count >= 18`；
- `ridge_line_count >= 28`；
- `subtractive_pore_count >= 16`；
- operator 中包含 `implicit_metaball_union` 和 `smooth_marching_cubes_surface`。

## 推荐远端命令

不要在本地启动远端任务。审核通过后，在 a100-2 项目环境执行：

```bash
cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
bash assets/launch_strict_visual_matched_texture_v13_smooth_coral_crystal_20260510.sh
```

可选覆盖：

```bash
SEED=20260510 STEPS=8 TEXTURE_SIZE=2048 bash assets/launch_strict_visual_matched_texture_v13_smooth_coral_crystal_20260510.sh
```
