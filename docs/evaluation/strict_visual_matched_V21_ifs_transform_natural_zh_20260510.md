# V21 IFS/transform natural 严格匹配生成说明

本文档记录 `strict_visual_matched_cases_V21_ifs_transform_natural_20260510.py` 的目标、操作符组合、远端约束和 dry-run 验证口径。V21 的定位是补齐 IFS / transform / radial / lattice 类 case：本地只生成远端输入，不生成最终结果，不筛选本地图像，不做后处理修复。

## 覆盖目标

V21 覆盖以下严格一对一目标：

- `ifs_branch_tree_d6`：fractal tree / branch IFS，保持 depth 6 的 affine branch copy grammar。
- `ifs_radial_ornament_o12_d5`：radial ornament，保持 order 12、depth 5 的旋转复制和 ring/spoke 结构。
- `ifs_pyrite_lattice_transform_d4`：lattice / pyrite-like transform，保持 signed-axis affine lattice recursion。
- `ifs_bismuth_stepped_transform_d5`：bismuth / stepped transform，保持 square-loop contraction 和 terrace translation。
- `ifs_escher_recursive_stair_loop_d4`：Escher-ish recursive stairs；OBJ 是物理连通网格，impossible-loop 只作为 view-dependent visual read。
- `transform_compat_positive_affine_stack_d4` 与 `transform_compat_negative_axis_mismatch_d4`：正/负 transform compatibility pair。正例使用共享轴的 commuting affine stack；负例使用 non-commuting anisotropic scale 和 axis mismatch，只作为 negative control，不计为正向 grammar match。

## OBJ-only mesh 输入和 mesh/PBR 约束

V21 的 mesh input policy 是 `obj_mesh_inputs_only`。manifest 中的 `mesh_path` 只指向 `.obj`，不使用 GLB / PLY / STL 作为输入。PNG guide 只用于远端 PBR texture guidance，不改变 mesh 输入格式。

远端输出必须走 mesh/PBR 路线：worker 调用 `trellis2_texturing_export_glb.py --mesh "$mesh" --image "$guide" --preprocess --texture-size "$tex"`，目标是 fresh textured GLB / PBR export。禁止输出包括 local selected render、2D-only image、posthoc repair mesh 和 non-OBJ mesh input。

## 操作符组合与 grammar mapping

每个 metadata 都记录 `grammar_mapping`，说明 operator composition 如何映射到传统 IFS/transform grammar：

1. `affine_transform_grammar`：每个 case 以传统 affine copy / rotation / scale / translation 为主语法。
2. `recursive_copy_depth_schedule`：depth、order、copy count 与对应 traditional target 锁定。
3. `strict_traditional_target_mapping`：一个 V21 OBJ 输入只对应一个 traditional target，比较单位是 one generated OBJ input to one traditional target。
4. `shared_vertex_connected_support`：所有 transform copy 通过 shared scaffold vertices 和 support faces 连接，避免 detached transform islands。
5. `attached_natural_mesh_detail`：branch bark/card、radial facets、pyrite cubes、bismuth slabs、stair treads 等细节都附着在 shared support 上。
6. `obj_mesh_input_only`：输入网格格式固定为 OBJ。
7. `pbr_material_prompt`：material prompt 与 guide image 只服务于远端 mesh/PBR 生成。
8. `largest_component_gate`：dry-run 必须通过 LCR >= 0.999。

## 连通性 gate

本地 dry-run 使用 `recursive_growth_mesh_metrics.component_stats` 对 OBJ face connectivity 计算 largest component ratio。V21 的硬 gate 是：

`LCR >= 0.999`

实现上，V21 不依赖后处理修复连通性，而是在生成时把每个 transform node 放入 shared vertex support，每条边的 ring face 都 fan 到 scaffold center。自然化细节也通过 anchor face 连接回主支撑，因此 dry-run 中应该是单一主 component。

## 远端生成约束

启动脚本为 `assets/launch_strict_visual_matched_texture_V21_ifs_transform_natural_20260510.sh`。默认远端根目录为：

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`

目标机器为 `a100-2`，GPU 固定为 `4/5/6/7`。所有 cache 都放在项目目录下，包括 `TMPDIR`、`TORCH_HOME`、`TRITON_CACHE_DIR`、`HF_HOME`、`XDG_CACHE_HOME` 和 `MPLCONFIGDIR`；脚本不使用 `/tmp` 或 `/dev/shm`。

main agent 可以调度远端 worker；本地执行本脚本只应 materialize dry-run inputs 和检查 manifest/metrics，不应启动 remote jobs。
