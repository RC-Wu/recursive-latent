# V19 meshroot botanical 严格匹配生成说明

本文档记录 `strict_visual_matched_cases_V19_meshroot_botanical_20260510.py` 的根/植物来源、操作符组合和远端生成约束。V19 的目标不是替换传统任务语义，而是在一对一比较中保留传统骨架或吸引子场，同时使用真实 GLB 网格 token 提升根、藤、树冠和灌木外观质量。

## 根/源策略

V19 生产路径使用真实 GLB 网格 token，不是本地筛选出的最终结果，也不是只用程序化杆件或卡片。当前 token 来源为：

- `visuals/textured_glb_20260508/tree_compete_s3/textured.glb`
- `visuals/textured_glb_20260508/vine_d5_compete_s5_inference/textured.glb`
- `visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb`
- `visuals/gen3d_baseline_texture_fairness_20260510/meshspace_genroot_vine_d2/textured.glb`

脚本会加载这些高质量项目 GLB，按包围盒归一化，从真实网格面片中抽取固定预算 token，然后把 token 作为可复用语法单元使用。只有在显式传入 `--use-tiny-fallback` 或源 GLB 不可读时，才会使用小型程序化 fallback；论文级生产路径必须使用真实 GLB token。

## 一对一比较约束

V19 覆盖六个严格匹配目标：

- `lsys_pine_canopy_d5`：仍由深度 5 L-system 树/针叶冠骨架控制。
- `lsys_root_fan_d5`：仍由深度 5 L-system 根向下趋性和扇形根系控制。
- `lsys_climbing_vine_d6`：仍由六轮爬藤/卷须递归控制。
- `sc_tree_crown_260`：仍由空间殖民树冠吸引子竞争控制。
- `sc_root_network_260`：仍由空间殖民根网吸引子场控制。
- `sc_bush_shell_220`：仍由空间殖民灌木外壳覆盖控制。

因此，V19 改变的是表面生成和 token 来源，不改变传统 baseline 的类别、递归模式或粗轮廓。pine/canopy 必须读作针叶树或树冠，root fan 必须读作根系，vine 必须读作藤蔓，SC crown/root/bush 必须读作吸引子驱动的冠层、根网或外壳。

## 操作符组合

每个 case 的 metadata 记录以下操作符组合：

1. `same_classical_recursive_mode`：传统 L-system 或 space-colonization 模式保持不变。
2. `real_glb_mesh_token_library`：从真实项目 GLB 构建可复用 token 库。
3. `grammar_skeleton_or_attractor_field`：用传统骨架或吸引子场决定锚点、方向和尺度。
4. `oriented_mesh_token_stamping`：把 token 的局部轴对齐到骨架边或吸引子分支方向。
5. `shared_vertex_support_bridge`：每个 token 面片通过共享支撑顶点桥接，避免独立漂浮碎片。
6. `connected_botanical_support_sweep`：基础支撑仍是连通的 taper sweep，用于保留生长结构。
7. `pbr_guide_output_for_trellis2`：输出 OBJ 和 PBR guide image，供 Trellis2 远端生成 textured GLB。
8. `no_local_selection`：本地 dry-run 只生成输入，不做最终图像/GLB挑选。

## 远端生成

启动脚本为 `assets/launch_strict_visual_matched_texture_V19_meshroot_botanical_20260510.sh`。默认远端根目录为 `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`，目标机器为 `a100-2`，GPU 固定为 `4/5/6/7`。所有 cache 都放在项目目录下，包括 `TMPDIR`、`TORCH_HOME`、`TRITON_CACHE_DIR`、`HF_HOME` 和 `XDG_CACHE_HOME`。

远端 worker 使用 `trellis2_texturing_export_glb.py --preprocess --texture-size "$tex"`，输出 textured GLB。main thread 只负责生成输入和调度 worker；不要在本地启动远端任务，也不要把本地 dry-run OBJ 当作最终结果。
