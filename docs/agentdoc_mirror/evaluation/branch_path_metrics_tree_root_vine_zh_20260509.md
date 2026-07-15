# Tree / Root / Vine Branch-Path-Root Reachability 评测 20260509

本轮只补轻量评测框架与已有数据表格，不修改 `paper_siga/main.tex`，不修改 AgentDoc plan，不触碰远端。

## 1. 输出文件

- 脚本：`assets/branch_path_metrics_20260509.py`
- 完整表：`results/branch_path_metrics_20260509/branch_path_metrics.csv`
- JSON：`results/branch_path_metrics_20260509/branch_path_metrics.json`
- 精简表：`results/branch_path_metrics_20260509/branch_path_metrics_compact.csv`
- 运行配置：`results/branch_path_metrics_20260509/run_config.json`

默认运行命令：

```bash
python3 assets/branch_path_metrics_20260509.py \
  --out-dir results/branch_path_metrics_20260509 \
  --occupancy-resolution 64
```

## 2. 指标定义与证据等级

### 2.1 可作为论文候选的指标

以下指标可以进入论文表格，但必须配合同 root / same depth / same renderer / neutral render / zoom-in QA：

| 指标 | 含义 | 可写范围 |
|---|---|---|
| `root_component_ratio` | 从 root seed 可达的单位占比 | root reachability / attached-to-root proxy；skeleton 行更强 |
| `orphan_mass_ratio` | `1 - root_component_ratio` | orphan mass proxy；mesh 行依赖 voxelization |
| `geodesic_proxy_max_depth` | skeleton hop depth 或 voxel BFS hop depth | skeleton 行可写 path depth；mesh 行只能写 proxy |
| `bbox_normalized_path_span` | path length / bbox diagonal | 可用于同协议内部比较 |
| `tip_count_proxy` | skeleton degree-1 tips 或 voxel low-degree endpoints | skeleton 行可作为 branch metric；mesh 行不能当真实 tip count |
| `branching_proxy` | skeleton degree>=3 nodes 或 voxel high-degree points | skeleton 行可作为 branch node count；mesh 行只是 surface/occupancy proxy |
| `orphan_tip_proxy` | 不连到 root component 的 tip/end proxy | skeleton 行可写；mesh 行用于筛查 |

### 2.2 只能作为 proxy / appendix / screening 的指标

OBJ/GLB mesh 行没有可靠 skeletonization。本轮没有把 textured mesh surface 自动骨架化，因为 GLB face components 与材质/导出分片会严重污染拓扑判断，直接 skeletonize 容易制造虚假的 branch/tip 结论。

因此 mesh 行统一标记为：

```text
metric_level = mesh_voxel_proxy
skeletonization_status = not_skeletonized_voxel_proxy_only
paper_use_tier = proxy_screening_or_appendix_only_without_skeleton_or_manual_QA
```

mesh 行只适合回答：

- occupancy / edge-rasterized occupancy 是否大体连到 root；
- 是否有明显 orphan mass 或 orphan endpoints；
- path span proxy 是否随 depth 或 method 改变。

mesh 行不能单独回答：

- 真实 branch node 数；
- 真实 terminal tip 数；
- 真实 root 分叉拓扑；
- 递归 grammar 是否被 faithfully preserved。

## 3. 本轮数据覆盖

默认脚本在已有数据上跑了 19 行：

- vine depth textured GLB：4 行；
- space-colonization v2：3 个 case 的 `skeleton.json` 强指标 + tube OBJ proxy，共 6 行；
- connected scaffold v2 root/vine control：1 行；
- 传统 L-system / IFS tree OBJ：2 行；
- `siga_night_20260508` tree projected/pruned OBJ：3 行；
- public guide tree/root/vine textured GLB：3 行。

没有发现缺失输入，`missing_count=0`。

## 4. 核心结果

### 4.1 Vine depth textured GLB

四个 vine depth textured GLB 在 64 分辨率 vertex occupancy proxy 下：

| label | root ratio | path span | tip proxy | orphan tip proxy |
|---|---:|---:|---:|---:|
| stage 01 | 1.000 | 1.148 | 62 | 0 |
| stage 02 | 1.000 | 1.284 | 53 | 0 |
| stage 03 | 1.000 | 1.307 | 54 | 0 |
| stage 04 | 1.000 | 1.048 | 58 | 0 |

解释：这支持“vine depth showcase 在 occupancy root reachability proxy 下保持连通”。但 tip / branch / path 都还只是 mesh proxy，不能写成真实 skeleton branch metric。

### 4.2 Space-colonization traditional baseline

保存的 `skeleton.json` 是本轮最强 branch/path 证据：

| case | root ratio | max depth | tips | branch nodes | path span | orphan tips |
|---|---:|---:|---:|---:|---:|---:|
| tree_canopy | 1.000 | 26 | 434 | 371 | 0.789 | 0 |
| root_vine | 1.000 | 24 | 456 | 392 | 0.506 | 0 |
| bush_shell | 1.000 | 36 | 500 | 439 | 0.696 | 0 |

解释：space-colonization baseline 可以作为传统 skeleton baseline 的论文候选，但仍需要与 proposed 放进同 root、same depth、same renderer 的比较列。

对应 tube OBJ 使用 edge-rasterized occupancy 后 root ratio 分别为 0.990、0.994、0.9999。这说明 tube mesh occupancy proxy 基本连通，但仍不应替代 skeleton.json 的 branch/tip 统计。

### 4.3 Tree / root OBJ 和 GLB

| label | root ratio | path span | orphan tip proxy | 备注 |
|---|---:|---:|---:|---|
| root_vine_connected_control | 1.000 | 1.716 | 0 | connected scaffold v2 control |
| lsystem_branch | 0.980 | 0.924 | 116 | mesh proxy 有少量 orphan endpoint |
| ifs_branch_tree | 1.000 | 1.320 | 0 | mesh proxy 连通 |
| tree_compete_d4_pruned | 0.993 | 0.997 | 3 | projected/pruned tree proxy 较稳 |
| tree_compete_fork_d4_pruned | 0.967 | 1.238 | 10 | fork case 有 orphan proxy |
| masked_tree_compete_fork_s1_a025_d3_pruned | 0.879 | 0.997 | 37 | 明显低于其他 tree case，应作为 caveat |
| tree_compete_d4_pruned_tree_roots textured GLB | 0.993 | 0.997 | 3 | 与源 tree mesh proxy 一致 |

解释：`tree_compete_d4_pruned` 和 textured root/tree GLB 可以作为 root-reachability proxy 正例；`masked_tree_compete_fork...` 暴露较明显 orphan mass，不能作为主文正例。

## 5. 论文写法边界

可以写：

- 本轮补了 branch/path/root-reachability 表格框架；
- space-colonization skeleton baseline 在保存 graph 上 root ratio=1.0，tips/branch/max-depth 可作为传统 baseline metric；
- vine depth GLB 四阶段 occupancy root ratio=1.0、orphan tip proxy=0，支持 depth showcase 的 root-reachability proxy；
- tree/root projected case 中 `tree_compete_d4_pruned` 比 fork/masked fork 更稳。

不能写：

- “GLB 已经可靠 skeletonized”；
- “mesh proxy 的 tip_count 就是真实叶尖/根尖数”；
- “同 root / same depth 的 proposed 已经系统性击败 space-colonization”；
- “tree/root/vine 结构问题已完全解决”；
- “textured render 证明 branch topology 正确”。

## 6. 失败与缺口

1. **缺同 root / same depth 对照**  
   现有 vine GLB、space-colonization skeleton、tree/root OBJ 来自不同实验入口，不能直接写成公平横向比较。

2. **缺可靠 mesh skeletonization**  
   本轮没有做自动 skeleton extraction。mesh 行全部是 voxel/occupancy proxy，尤其 tip/branch 数会受 surface tessellation、voxel 分辨率和未 weld tube 影响。

3. **GLB face fragmentation 仍未解决**  
   既有协议已指出 textured GLB raw face component 很高。本轮 root reachability proxy 不能覆盖 face-level fragmentation caveat。

4. **root seed 是启发式**  
   mesh 行默认用 `min_z_voxel_closest_to_xy_centroid`。对横向生长 root、悬垂 vine 或非 z-up asset，必须改为显式 root anchor。

5. **缺 neutral render / zoom-in QA**  
   本任务只输出表格和文档，没有生成 Blender neutral render，也没有 junction/tip/root attachment zoom crop。论文主表必须补视觉 QA。

## 7. 下一步最小闭环

建议下一轮只跑一个小而严格的 tree/root/vine 矩阵：

| 条件 | 要求 |
|---|---|
| root | 同一个 root/scaffold anchor |
| depth | 同 D=0..5，至少 seeds 0/1/2 |
| methods | space-colonization / direct / final-only / prune-per-depth / bridge-per-depth |
| geometry evidence | 每层 OBJ/GLB + explicit root anchor |
| metrics | skeleton or centerline extraction、root_component_ratio、path-to-root rate、tips、branch nodes、orphan tips |
| render | neutral front/side/top/iso + junction/root/tip zoom |

只有这套跑完，branch/path/root-reachability 才能从“已有数据 proxy 表”升级为主文结构评测。
