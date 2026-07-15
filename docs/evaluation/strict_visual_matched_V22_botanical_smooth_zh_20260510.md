# V22 botanical smooth 严格匹配生成说明

本文档记录 `strict_visual_matched_cases_V22_botanical_smooth_20260510.py` 的目标、语法操作符和远端约束。V22 的核心修复是：仍然做严格一对一的 L-system / space-colonization 植物与根系比较，但表面不再依赖 V17 的杆/卡片简化，也不再依赖 V19 的 mesh token stamping。所有输入都是 OBJ mesh，先在本地 dry-run 通过 LCR >= 0.999 连通性门槛，再交给远端 Trellis2 做 mesh/PBR 输出。

## 覆盖目标

V22 覆盖 8 个严格一对一目标：

- `lsys_pine_canopy_d5`：深度 5 L-system 松/树冠。
- `lsys_root_fan_d5`：深度 5 L-system 根扇。
- `lsys_climbing_vine_d6`：六轮递归爬藤与卷须。
- `sc_tree_crown_260`：space-colonization 树冠吸引子竞争。
- `sc_root_network_260`：space-colonization 根网吸引子竞争。
- `sc_bush_shell_220`：space-colonization 灌木外壳覆盖。
- `lsys_pine_canopy_depth_sweep_d6`：松树 L-system 深度参数 sweep。
- `sc_root_network_parameter_sweep_dense`：根网 space-colonization 参数 sweep。

这些 case 改变的是表面表达和细节密度，不改变传统 baseline 的类别、递归模式、粗轮廓或比较单位。

## 平滑几何策略

V22 使用平滑隐式半径场和扫掠支撑：

1. `smooth_implicit_radius_field`：每个语法节点按深度生成连续 taper 半径，而不是离散 low-poly block。
2. `swept_connected_support`：每条 L-system 边或 space-colonization 边生成带椭圆扰动的扫掠管，并通过共享节点顶点缝合成一个主连通分量。
3. `shared_vertex_semantic_detail_attachment`：叶片、针叶、根须、卷须都在导出 OBJ 前通过共享顶点面片接到支撑上。
4. `pre_export_leaf_needle_rootlet_details`：语义细节是实际 mesh 几何，不是渲染贴图里的假细节。

因此 V22 不是 low-poly block，也不是 token stamping。松树必须能读出针叶和树冠，根系必须能读出根须和根网，藤蔓必须能读出叶片和卷须，灌木必须能读出叶片外壳。

## 语法操作符说明

每个 metadata 都记录 `grammar_mapping`：

- L-system 中，`F` 对应前进并生成平滑扫掠段，`+/-` 对应 yaw 分支，`&/^` 对应 pitch 分支，`[]` 对应 push/pop 递归状态。
- 根系 L-system 额外记录 `root_tropism`，用于说明负 z 方向的根向下趋性。
- vine case 额外记录 `curl`、`tendril`、`leaf`，用于说明爬藤卷曲、卷须和叶片的连接方式。
- space-colonization 中，`attractor_field` 决定目标体积，`influence_radius` 决定哪些吸引子贡献方向，`kill_radius` 删除已覆盖吸引子，`step_size` 推进新支撑节点。

这些操作符只解释传统控制与 V22 mesh 几何的映射，不允许把本地结果作为最终筛选结果。

## 连通性和远端约束

dry-run 对每个 OBJ 运行 largest-component vertex ratio 检查，门槛为 `LCR >= 0.999`。失败时脚本直接报错，不写入可用 manifest。输出包括：

- `manifest.csv` / `manifest.json`
- `initial_metrics.csv` / `initial_metrics.json`
- `a100-2_cases.txt`
- `gpu4_cases.txt`、`gpu5_cases.txt`、`gpu6_cases.txt`、`gpu7_cases.txt`
- PBR guide PNG

启动脚本为 `assets/launch_strict_visual_matched_texture_V22_botanical_smooth_20260510.sh`。默认机器为 `a100-2`，GPU 固定为 `GPU 4/5/6/7`。所有 cache 都放在项目目录下，包括 `TMPDIR`、`TORCH_HOME`、`TRITON_CACHE_DIR`、`HF_HOME`、`XDG_CACHE_HOME` 和 `MPLCONFIGDIR`。

主流程只生成 OBJ 输入和调度远端 worker；本次本地验证只运行 pytest 和 dry-run，不启动远端任务。
