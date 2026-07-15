# Mesh-space trivial recursion negative-control baseline protocol (2026-05-10)

## 目的

本 baseline 是严格反例，不验证递归生成能力，只验证“把一个生成模型 root mesh 复制、缩放、旋转、平移并直接 merge”会得到什么。它用于和 PS-RSLG / 递归生成方法区分：如果方法只是 mesh-space copy paste，应在连通性、重复性和局部结构自然化上暴露明显负结果。

## 输入 root

默认输入使用本仓库已存在的本地 Trellis/connected mesh 作为 root placeholder：

- vine/tree: `inputs/connected_best_expansion_20260509/root_vine_connected_control.obj`
- pyrite/lattice: `inputs/connected_best_expansion_20260509/pyrite_crystal_lattice_cluster.obj`

如果远端最新 one-shot Trellis2 OBJ/GLB 拉回，可直接用命令行替换：

```bash
python3 assets/mesh_space_trivial_recursion_baseline_20260510.py \
  --vine-root visuals/gen3d_baseline_trellis2_one_shot_more_20260510/vine_one_shot_front_seed613_steps8_nopre/trellis2_dinov3_min.obj \
  --pyrite-root visuals/gen3d_baseline_trellis2_one_shot_more_20260510/pyrite_one_shot_front_seed613_steps8_nopre/trellis2_dinov3_min.obj
```

脚本默认把 root mesh 限制到 `--max-root-faces 12000`，只为本地实例化和预览可运行；该步骤不是生成或修复，只是确定性 face subset + 顶点 compact。正式相机图可把该值调大或设为 `0`。

## 方法定义

实现文件：

```bash
assets/mesh_space_trivial_recursion_baseline_20260510.py
```

两类 grammar：

- `vine_tree`: 传统树状递归，根节点向三个方向分叉，逐层使用 translate / rotate / scale。
- `pyrite_lattice`: 传统晶格递归，按 Manhattan shell 放置实例，逐层使用 translate / rotate / scale。

两个 ablation：

- `full_srt`: scale + rotate + translate。
- `no_scale`: 禁用 scale，只保留 rotate + translate，用于确认 scale taper 是否只是控制尺寸而非生成新结构。

负控制约束：

- 不调用 Trellis2 或任何 3D 生成模型。
- 不做 latent update。
- 不做 projection repair。
- 不做 mesh weld / boolean union / voxel close / hole fill。
- 输出 mesh 是 root 三角网格经变换后的直接 concat。

## 运行命令

```bash
python3 assets/mesh_space_trivial_recursion_baseline_20260510.py --self-test
python3 assets/mesh_space_trivial_recursion_baseline_20260510.py \
  --out results/mesh_space_trivial_baseline_20260510 \
  --max-depth 3 \
  --max-root-faces 12000 \
  --preview-max-faces 70000
```

## 输出

主目录：

```bash
results/mesh_space_trivial_baseline_20260510/
```

每个 case 输出：

- OBJ: `<grammar>/<variant>/depth_XX/*_depth_XX.obj`
- pure-white PBR GLB: `<grammar>/<variant>/depth_XX/*_white_pbr.glb`
- pure-white mesh preview PNG: `<grammar>/<variant>/depth_XX/*_white_preview.png`

汇总表：

- `mesh_space_trivial_metrics.csv`
- `mesh_space_trivial_metrics.json`
- `summary.json`

关键指标：

- `instance_count`: 传统实例数量。
- `component_count`: 直接 merge 后的 mesh 连通分量数。
- `largest_component_vertex_ratio`: 最大分量顶点占比。
- `fragmentation_score = 1 - largest_component_vertex_ratio`。
- `copy_repetition_score = 1.0`: 明确标记该 baseline 没有新几何生成。
- `latent_or_mesh_repair_used = 0`: 明确标记没有生成/修复步骤。

## 预期正/负结果

正结果：

- 能稳定生成可检查的 OBJ/GLB/PNG。
- depth sweep 和 `no_scale` ablation 可复现实例数、包围盒和碎片化随深度变化。
- GLB 使用白色 PBR 材质，PNG 是基于三角面 raster 的纯白 mesh 预览，不使用 matplotlib 点云作为最终证据。

负结果：

- mesh 分量数随实例数增长；没有跨实例自然连接。
- 最大连通分量占比随 depth 下降。
- 局部几何完全重复，只有 S/R/T 变换，不能产生新的局部结构、接缝自然化或递归形态融合。
- `no_scale` 和 `full_srt` 的差别主要是尺寸/包围盒，不改变 copy-paste 本质。
