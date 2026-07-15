# V25 root/SC refine 小批量计划

日期：2026-05-10  
状态：ready for remote launch after local contract tests  
本地 generator：`assets/strict_visual_matched_cases_V25_root_sc_refine_20260510.py`  
远端 launcher：`assets/launch_strict_visual_matched_texture_V25_root_sc_refine_20260510.sh`  
远端目标：`a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`  
GPU：只用 `GPU 4/5/6/7`  
存储上限：`200GB`；本批预估上限约 `40GB`，cache/TMP 必须在项目目录内。

## 1. 为什么要做 V25

V24 traditional-vs-ours one-to-one 图已经可以作为严格四族比较进入论文，但其中两行仍有弱点：

- `root fan`：V24 root fan 视觉强，但三 seed post-GLB surface r0 仍有 tiny islands，只能写成 visual family panel，不能写成 topology-stability proof。
- `SC tree crown`：V24 SC tree A 指标强，但 trunk/cap 局部视觉偏粗、偏 blocky。V25 只在视觉自然度上挑战 V24，不应牺牲 r0 单连通。

因此 V25 是小范围替换候选批，不是新的全家族主实验。完成远端 GLB、surface metrics、白底多级 zoom 和人工 QA 之前，不能直接替换当前 V24 主文图。

## 2. 输入合同

本批共 `8` 个 OBJ input，GPU 平均分配为每卡 `2` 个：

| case | family | target | goal |
|---|---|---|---|
| `V25_lsys_root_fan_dense_anchorC_stable` | L-system | `lsys_root_fan_d5` | thicker shared support for r0 stability |
| `V25_lsys_root_fan_dense_anchorD_stable` | L-system | `lsys_root_fan_d5` | more attached rootlets |
| `V25_lsys_root_fan_smooth_anchorC_stable` | L-system | `lsys_root_fan_d5` | cleaner silhouette and fewer islands |
| `V25_lsys_root_fan_smooth_anchorD_stable` | L-system | `lsys_root_fan_d5` | stronger rootlet attachment |
| `V25_sc_tree_crown_tapered_A` | Space colonization | `sc_tree_crown_260` | reduce blocky trunk/cap artifacts |
| `V25_sc_tree_crown_tapered_B` | Space colonization | `sc_tree_crown_260` | denser canopy with slimmer tubes |
| `V25_sc_tree_crown_leafshield_A` | Space colonization | `sc_tree_crown_260` | hide cut caps while preserving crown |
| `V25_sc_tree_crown_leafshield_B` | Space colonization | `sc_tree_crown_260` | cleaner local zoom and less massive trunk |

本地 dry-run 必须满足：

- `OBJ` input only；不使用本地 GLB 选择或后处理充当正例。
- pre-export `largest_mesh_component_vertex_ratio` gate：`LCR >= 0.999`。
- `boundary_tag` 为空；本批不允许 boundary row 进入远端正例。
- root extra rootlets 使用真实 L-system `nodes/parents` graph 作为 anchor，不再从 center vertices 伪造 parent list。

## 3. 远端运行命令

先只生成输入检查：

```bash
cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
bash assets/launch_strict_visual_matched_texture_V25_root_sc_refine_20260510.sh --generate-only
```

正式启动：

```bash
cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
bash assets/launch_strict_visual_matched_texture_V25_root_sc_refine_20260510.sh
```

launcher 约束：

- 只允许 `GPU 4/5/6/7`。
- `TMPDIR`、`TORCH_HOME`、`XDG_CACHE_HOME`、`TRITON_CACHE_DIR`、`MPLCONFIGDIR` 都在 `$ROOT/cache/...`。
- 不使用 `/tmp` 或 `/dev/shm`。
- 每个 worker 使用 `trellis2_texturing_export_glb.py --steps 8 --texture-size 2048 --preprocess`。

## 4. 替换门槛

### Root fan

V25 root 要替换 V24 `V24_lsys_root_fan_dense_A`，至少需要：

- 三 seed 或至少当前小批中最优候选达到 `max_components_r0 <= 1` 才能升级为 topology/main-stable；理想 `min_lcr_r0 >= 0.999999`。
- 若仍然只是 `components_r1=1` 且 `r0>1`，只能作为 visual family panel。
- 白底 zoom 中 detached fragments 不可见，并且 root fan/rootlet 语义仍清楚，不能变成粗管束或毛刺团。

### SC tree crown

V25 SC 要替换 V24 `V24_sc_tree_crown_attractor_A`，必须：

- 不低于 V24 的强指标基线：`components_r0=1`、`LCR_r0=1.0` 级别。
- 视觉上明显改善粗 trunk、blocky tube 或 cut cap。
- crown/attractor canopy 语义保持清楚。若指标退化到 `r0=3--4`，即使局部视觉稍好，也只能进入 appendix robustness。

## 5. 后处理与指标

远端完成后拉回：

- GLB/PBR 结果：`visuals/strict_visual_matched_texture_V25_root_sc_refine_20260510/`
- inputs：`results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/inputs/`
- surface metrics：`results/strict_visual_matched_texture_V25_root_sc_refine_20260510_remote/surface_metrics_occ64.csv/json`

复用脚本：

- surface metrics：`assets/batch_surface_voxel_metrics_20260509.py`
- matched-camera 白底 zoom：`scripts/figures/matched_camera_zoom_render_20260510.py`
- callout/contact sheet：`scripts/figures/postprocess_matched_camera_zoom_plan_20260510.py`
- 若替换论文图：`scripts/figures/compose_traditional_vs_v24_one_to_one_20260510.py` 需要改名或扩展为 V24/V25 mixed source，并更新 `paper_siga` 表格文案。

## 6. Claim boundary

- V25 是替换候选筛选批，不是新的全论文结论。
- traditional baselines 仍是强结构控制，不写成 strawman。
- surface metrics 是 post-GLB renderability/connectivity diagnostic，不是 watertight topology proof。
- root fan 若未达到 r0 单连通，只能写视觉家族对比，不写拓扑稳定证明。
