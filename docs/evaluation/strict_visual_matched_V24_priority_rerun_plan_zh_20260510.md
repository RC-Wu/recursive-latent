# V24 priority rerun strict matched 远端生成计划

日期：2026-05-10

范围：本计划只为 baseline 远端生成支线准备可执行输入与 launcher。当前回合不要启动远端，不修改 `paper_siga/main.tex`，不触碰 masked naturalization 文件，不删除旧结果。

## 1. 目标

V24 是 V23 三 seed/稳定池视觉 QA 后的 priority rerun，不再铺全 family 大网，而是集中解决审稿最容易追问的缺口：

1. root quality：L-system root fan 与 SC root network。
2. SC tree：主文 SC 候选的 cleaner crop / less clipping 备份。
3. DLA/IFS polish：少量 staghorn/frontier/lace 和 pyrite/radial 重跑，用于减轻端帽、机械桥接、局部穿插等视觉风险。

所有输入保持 OBJ pre-export，远端由 Trellis2 texturing/export 生成 PBR GLB。pre-export 门槛为 `LCR >= 0.999`；若 case 是 V23 near-stable 风险项，manifest 必须带 explicit `boundary tag`，并在 post-GLB 阶段重新做 fragment/visual QA。

## 2. 文件与生成器

新增文件：

- `assets/strict_visual_matched_cases_V24_priority_rerun_20260510.py`
- `assets/launch_strict_visual_matched_texture_V24_priority_rerun_20260510.sh`
- `tests/test_strict_visual_matched_cases_V24_priority_rerun_20260510.py`
- `docs/evaluation/strict_visual_matched_V24_priority_rerun_plan_zh_20260510.md`

本地 dry-run 输出默认目录：

- `results/strict_visual_matched_cases_V24_priority_rerun_20260510_dryrun`

远端输入目录：

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/inputs/strict_visual_matched_cases_V24_priority_rerun_20260510`

远端结果目录：

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/strict_visual_matched_texture_V24_priority_rerun_20260510`

cache/TMP 全部限定在远端项目目录：

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache/...`

## 3. Case 列表与 GPU 分配

总数：15 个远端 generation case。只用 GPU 4/5/6/7。

| priority | case | family | GPU | 目的 |
|---|---|---|---:|---|
| root quality | `V24_lsys_root_fan_d5_dense_rootlets_anchorA_seedA` | L-system | 4 | dense root fan，增强 rootlet attachment |
| root quality | `V24_lsys_root_fan_d5_dense_rootlets_anchorB_seedB` | L-system | 5 | dense root fan 第二 seed，降低 floating tips |
| root quality | `V24_lsys_root_fan_d5_smooth_rootlets_anchorA_seedA` | L-system | 6 | smooth root fan，作为更干净 root-quality 备选 |
| root quality | `V24_lsys_root_fan_d5_smooth_rootlets_anchorB_seedB` | L-system | 7 | smooth root fan 第二 seed，扩展 root fan silhouette |
| root quality | `V24_sc_root_network_260_anchorA_seedA` | SC | 4 | SC root network 主 rerun，降低 orphan fragments |
| root quality | `V24_sc_root_network_260_anchorB_seedB` | SC | 5 | SC root network 第二 seed，检查 path-to-root |
| SC tree | `V24_sc_tree_crown_260_attractor_clean_seedA` | SC | 6 | tree crown 主文候选 cleaner crop |
| SC tree | `V24_sc_tree_crown_260_attractor_clean_seedB` | SC | 7 | tree crown 第二 seed，减少截断/端帽 |
| SC tree backup | `V24_sc_tree_crown_260_sparse_kill_clean_seedA` | SC | 4 | sparse-kill backup，降低拥挤 |
| SC tree backup | `V24_sc_tree_crown_260_sparse_kill_clean_seedB` | SC | 5 | sparse-kill 第二 seed，筛 fragment visibility |
| DLA polish | `V24_dla_coral_cluster_900_staghorn_frontier_polish_seedA` | DLA/frontier | 6 | staghorn 主候选视觉 polish |
| DLA polish | `V24_dla_frontier_sheet_700_open_boundary_polish_seedA` | DLA/frontier | 7 | frontier sheet 端帽/branch thickness polish |
| DLA boundary | `V24_dla_coral_cluster_900_lace_porosity_boundary_seedA` | DLA/frontier | 4 | lace porosity boundary-tagged rerun |
| IFS polish | `V24_ifs_fractal_lattice_d4_pyrite_copy_bridges_polish_seedA` | IFS/transform | 5 | pyrite/lattice bridge contact polish |
| IFS polish | `V24_ifs_radial_ornament_o8_d4_orbit_spokes_polish_seedA` | IFS/transform | 6 | radial/orbit appendix fallback polish |

GPU 负载：GPU4 四个、GPU5 四个、GPU6 四个、GPU7 三个。

## 4. 本地验证命令

本地只生成 dry-run 输入和跑测试，不触发远端：

```bash
python3 -m pytest tests/test_strict_visual_matched_cases_V24_priority_rerun_20260510.py -q
python3 assets/strict_visual_matched_cases_V24_priority_rerun_20260510.py \
  --root /Users/fanta/code/agent/Code/recursive_3d_generative_growth \
  --out results/strict_visual_matched_cases_V24_priority_rerun_20260510_dryrun \
  --seed 20260510
```

验证点：

- 15 个 case，全为 `V24_` 前缀。
- `manifest.csv/json`、`initial_metrics.csv/json`、`gpu4/5/6/7_cases.txt` 齐全。
- 每行 OBJ-only + PBR guide。
- `largest_mesh_component_vertex_ratio >= 0.999`，或 explicit `boundary tag`。
- 不使用 GPU 0/1/2/3。

## 5. 交给主线程的远端命令

不要在当前回合启动远端。主线程确认 GPU 4/5/6/7 和存储后，可在远端项目根执行：

```bash
cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
bash assets/launch_strict_visual_matched_texture_V24_priority_rerun_20260510.sh --generate-only
bash assets/launch_strict_visual_matched_texture_V24_priority_rerun_20260510.sh
```

如果只想分卡执行：

```bash
bash assets/launch_strict_visual_matched_texture_V24_priority_rerun_20260510.sh --worker 4
bash assets/launch_strict_visual_matched_texture_V24_priority_rerun_20260510.sh --worker 5
bash assets/launch_strict_visual_matched_texture_V24_priority_rerun_20260510.sh --worker 6
bash assets/launch_strict_visual_matched_texture_V24_priority_rerun_20260510.sh --worker 7
```

默认参数：

- `STEPS=8`
- `TEXTURE_SIZE=2048`
- `CUDA_VISIBLE_DEVICES` 只允许 4/5/6/7
- `TMPDIR/TORCH_HOME/XDG_CACHE_HOME/TRITON_CACHE_DIR` 均在远端项目目录

## 6. Post-GLB QA 门槛

V24 不是直接进论文的最终证据。远端完成后必须补：

1. surface metrics：`components_r0`, `lcr_r0`, `occupied`, `vertices`, `faces`。
2. root quality：root attachment close-up、path-to-root、orphan fragment ratio。
3. SC tree：主文裁图下的小碎片、截断端、端帽是否显眼。
4. DLA：staghorn/frontier 的 branch thickness、tip caps、lace porosity 是否引入可见碎片。
5. IFS：pyrite copy bridges 是否读作有效 contact，而不是机械穿插；radial/orbit 是否保留 transform symmetry。

主文升级条件：

- L-system root fan：rootlets 附着清楚，不能有大量 floating hair-like tips。
- SC root network：post-GLB components 和 orphan fragments 显著优于 V23。
- SC tree crown：主文 crop 比 V23 更少截断/拥挤。
- DLA/IFS polish：不能牺牲 V23 的高 LCR，只能作为视觉改良。

## 7. Boundary tag

当前唯一 boundary-tagged case：

- `V24_dla_coral_cluster_900_lace_porosity_boundary_seedA`

原因：V23 lace porosity 属于 near-stable，components_r0 曾到 7。它可以作为 DLA porosity appendix 备选，但不能在未通过 post-GLB fragment QA 前进入主文。
