# 严格同任务 baseline 扩展计划 2026-05-10

本文档只定义扩展后的 matched-task 任务池和通过口径。主表中不得再使用“传统 tree/coral/IFS”对比“我们的 vine/root/pyrite 正例”的松散替代；每个 case 必须在类别、粗轮廓、递归/生长模式和深度复杂度上逐项对齐。

## 统一执行规则

- 每个 case 先生成传统 baseline 目标 OBJ 和 `cases.txt`，再为 PS-RSLG 选择同类别 root 或同任务 root strategy。
- 传统 baseline 的控制量必须保留在 manifest 中：规则、depth/iteration、seed、attractor/stickiness/transform 参数。
- PS-RSLG 可以使用更好的 root/image/mesh，但最终任务必须仍然清楚属于同一目标类别和同一递归模式。
- 通过条件同时包含结构和语义：同类别、同粗轮廓、同递归模式、同复杂度、root/seed 可追踪、无主要漂浮碎片。
- 失败必须按 case 记录，不能用邻近类别替代。例如 L-system canopy 失败时不能换成 vine；DLA coral 失败时不能换成 generic coral asset。

## L-system / 分支重写

| case_id | 传统 baseline 目标 | PS-RSLG operator/root 策略 | 通过 | 失败 |
|---|---|---|---|---|
| `lsys_pine_canopy_d5` | L-system/turtle upright pine canopy；单 trunk、层级分枝、冠层近锥形或椭球形；depth 5 左右，tip 数量与传统目标同量级 | R0/R1：使用 tree trunk/canopy root；operator 为 typed branch rewrite + angle/length/taper schedule + per-depth projection + tip/junction naturalization | 最终 mesh 是 tree/pine canopy；主干向上，冠层 bbox 高宽比与 baseline 接近；branch depth、tip count、branch node count 不低于 baseline 的 60% 且不超过 180%；root_component_ratio >= 0.98 | 生成 vine/root/coral；冠层消失；只有贴图像树但结构不是 branching；tip 大量漂浮或过度剪枝 |
| `lsys_root_fan_d5` | L-system root fan；从单 root base 向下/侧向扩展，递归分叉，粗轮廓为扇形地下根系 | R0/R1：使用 root/vine root mesh 或 same-category root image；operator 为 root handle rewrite + gravity/tropism bias + collision mask + per-depth root projection | 最终类别明确是 root network；主轴向下或侧向铺展；每个 terminal 可回溯到 root；path length 和 junction count 与 baseline 同量级 | 被替换为 tree canopy；根系断裂；主要分支向上形成树；root anchor 不在基部 |
| `lsys_climbing_vine_d6` | L-system curling/climbing vine；主藤连续上升，侧枝/tendril 递归缠绕；depth 6 左右 | R0/R1：使用 vine root 或已有高质量 vine/root GLB 作为类别 root；operator 为 vine curl rewrite + helical local transform + support projection | 主藤连续、侧向卷须清楚；递归深度可见；bbox 呈细长攀援轮廓；无断裂主链 | 变成 bush/canopy；只有光滑绳索没有递归侧枝；卷须漂浮不连根 |

## Space colonization / 吸引子竞争

| case_id | 传统 baseline 目标 | PS-RSLG operator/root 策略 | 通过 | 失败 |
|---|---|---|---|---|
| `sc_tree_crown_260` | Space colonization tree crown；固定 attractor cloud、influence/kill radius、step size；树冠由吸引子竞争填充 | R0/R1：tree trunk root；operator 为 attractor competition + handle selection + occupancy exclusion + per-depth projection | tree crown 语义明确；attractor coverage、tip count、branch density 与 baseline 同量级；冠层轮廓覆盖同一椭球/伞形区域 | 用 vine/root 代替 crown；覆盖不足导致空冠；竞争生长不可追踪 |
| `sc_root_network_260` | Space colonization root network；attractor 分布在 root base 下方/侧方扁椭球体内；多级根须竞争填充土壤体积 | R0/R1：root base；operator 为 soil attractor field + root handle competition + collision/exclusion + projection | root network 类别正确；root_component_ratio >= 0.98；coverage 和 branching density 与 baseline 同量级；主要生长在下/侧向体积 | 变成树冠或 generic bush；大量孤立根须；根基位置漂移 |
| `sc_bush_shell_220` | Space colonization bush/shell；从低 seed 向半球壳层吸引子生长，形成灌木状外壳 | R1：bush/shrub root 或 neutral plant root；operator 为 shell attractor competition + radial exclusion + tip density control | silhouette 为半球/灌木壳；内外层分枝可见；tip 分布覆盖 shell；不出现单一树干主导 | 生成 tree canopy 或 coral cluster；壳层覆盖过稀；生长方向与 attractor shell 无关 |

## DLA / frontier accretion

| case_id | 传统 baseline 目标 | PS-RSLG operator/root 策略 | 通过 | 失败 |
|---|---|---|---|---|
| `dla_coral_cluster_900` | DLA coral/porous cluster；random-walk attachment、中心或底部 seed、900 粒子左右；粗轮廓为多孔珊瑚团 | R0/R1：coral seed/root；operator 为 frontier attachment + stickiness analog + local masked naturalization + cavity-preserving projection | coral/frontier 类别清楚；保留多孔/枝状 frontier；root-connected frontier rate 高；不能用完全平滑实体替代 DLA 结构 | generic coral asset 无 frontier controls；过度平滑导致 DLA 形态消失；假桥把远端块硬连 |
| `dla_aniso_crystal_800` | Anisotropic DLA crystal；格点邻域带轴向/晶面偏置，形成晶簇/枝晶粗轮廓 | R0/R1：crystal seed/facet root；operator 为 anisotropic frontier selector + facet/contact handles + lattice/facet projection | 类别是 crystal/dendrite；存在方向性/facet-like 生长；frontier 与 seed 连通；anisotropy 指标与 baseline 同方向 | 替换成 pyrite lattice 但无 DLA/frontier；晶体变成树或珊瑚；碎片独立漂浮 |
| `dla_frontier_sheet_700` | DLA frontier sheet；从线状 seed/边界向前沿扩散附着，形成带状/片状枝晶前沿 | R0/R1：frontier strip seed；operator 为 boundary frontier handles + local attachment mask + bridge-aware projection | 粗轮廓是片状/边界前沿；增长方向可追踪；frontier tips 与 baseline 同量级；大部分前沿连到 seed strip | 退化成球状 cluster；前沿方向丢失；只剩光滑片而没有 accretion tips |

## IFS / transform-copy / fractal ornament

| case_id | 传统 baseline 目标 | PS-RSLG operator/root 策略 | 通过 | 失败 |
|---|---|---|---|---|
| `ifs_branch_tree_d6` | IFS recursive branch tree；固定 affine copy、scale decay、rotation schedule；树形自相似 | R0/R1：transform tree root motif；operator 为 transform-copy branch handles + scale/rotation schedule + projection | tree/branch 类别正确；transform copy 层级可识别；orbit/scale drift 在阈值内；branch topology 与 baseline 同量级 | 拿 lattice/crystal 替代 tree；transform 层级不可追踪；过度自然化破坏自相似 |
| `ifs_radial_ornament_o8_d4` | Radial IFS ornament；8 重旋转 copy + 缩放递归，粗轮廓为放射装饰/雪花 | R0/R1：radial motif root；operator 为 radial copy + axis lock + contact/admissibility projection | 8-fold 或预注册阶数清楚；copy survival 高；radial symmetry error 低；同一 motif 层级可见 | 生成 branch tree；旋转阶数不对；copy 大量丢失或互相穿插断裂 |
| `ifs_fractal_lattice_d4` | IFS/fractal lattice；基 motif 按 affine lattice basis 递归复制，形成多层格架/晶格装饰 | R0/R1：lattice motif root；operator 为 affine lattice transform + contact projection + masked naturalization | lattice/fractal ornament 类别明确；basis/contact 可追踪；component count 受控；自相似层级可见 | 用 DLA crystal 替代 affine lattice；contact graph 断裂；没有递归 transform 证据 |

## 最小主表选择

建议主文先选每族 1 个最强 strict case，补充材料放完整 10-12 个目标：

| Family | 主文优先 case | 原因 |
|---|---|---|
| L-system | `lsys_pine_canopy_d5` 或 `lsys_climbing_vine_d6` | 分支重写最容易被审稿人检查类别是否错配 |
| Space colonization | `sc_tree_crown_260` | 能直接检验同 attractor competition 下的 coverage 与资产质量 |
| DLA | `dla_coral_cluster_900` | 是压力线，必须诚实展示 frontier matching 而非 generic coral |
| IFS | `ifs_radial_ornament_o8_d4` | transform-copy 约束清楚，利于报告 orbit/symmetry error |

## 本地目标生成

配套脚本：`assets/strict_matched_task_targets_20260510.py`。

推荐命令：

```bash
python assets/strict_matched_task_targets_20260510.py --out results/strict_matched_task_targets_20260510
```

输出：

- `manifest.csv` / `manifest.json`：每个 traditional target 的 family、case、参数、OBJ 路径和基础几何统计。
- `cases.txt`：`case_id=OBJ path`，供后续渲染、指标和 PS-RSLG matched generation 读取。
- 每个 case 一个 OBJ；脚本只生成 CPU 本地传统 baseline mesh，不渲染、不调用 GPU、不写 `paper_siga`。
