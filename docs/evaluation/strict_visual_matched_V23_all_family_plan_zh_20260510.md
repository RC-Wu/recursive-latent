# V23 all-family strict matched 远端批量生成计划

日期：2026-05-10

范围：只设计并本地 dry-run 验证传统 baseline strict matched 输入，不直接 ssh 启动远端任务，不修改 `paper_siga/main.tex`。V23 目标是一次覆盖四类传统方法，优先得到可进入 paper-grade 筛选的 OBJ 输入、manifest、PBR guide 和远端启动命令。

## 1. 批次目标

V23 使用 `assets/strict_visual_matched_cases_V23_all_family_20260510.py` 生成 16 个严格一对一候选：

- L-system：tree/root/vine + dense rootlet 参数变体。
- space-colonization：crown/root/bush + sparse-kill crown 参数变体。
- DLA/frontier：coral/frontier sheet/crystal + lace porosity coral 参数变体。
- IFS：lattice/radial/branch tree/branch ornament。

本地 dry-run 只验证输入 mesh connectivity/manifest。最终证据必须在 `a100-2` 重新生成 mesh/PBR GLB 后，再做 post-GLB 指标、white overview、zoom 和人工 QA。

## 2. 预计 case 数和 GPU 分配

总数：16 个远端 generation case。GPU 4/5/6/7 每卡 4 个。

| GPU | V23 cases |
|---|---|
| 4 | `lsys_pine_canopy_d5`, `sc_tree_crown_260`, `dla_coral_cluster_900`, `ifs_fractal_lattice_d4` |
| 5 | `lsys_root_fan_d5`, `sc_root_network_260`, `dla_frontier_sheet_700`, `ifs_radial_ornament_o8_d4` |
| 6 | `lsys_climbing_vine_d6`, `sc_bush_shell_220`, `dla_crystal_cluster_520`, `ifs_fractal_tree_d5` |
| 7 | `lsys_root_fan_d5_dense_rootlets`, `sc_tree_crown_260_sparse_kill`, `dla_coral_cluster_900_lace_porosity`, `ifs_branch_ornament_d5` |

## 3. 本地验证命令

```bash
python3 -m pytest tests/test_strict_visual_matched_cases_V23_all_family_20260510.py -q
python3 assets/strict_visual_matched_cases_V23_all_family_20260510.py \
  --root /Users/fanta/code/agent/Code/recursive_3d_generative_growth \
  --out results/strict_visual_matched_cases_V23_all_family_20260510_dryrun \
  --seed 20260510
```

本地门槛：`LCR >= 0.999`，OBJ-only，`manifest.csv/json`、`initial_metrics.csv/json`、`gpu4/5/6/7_cases.txt` 完整。

## 4. 交给主线程的远端命令

不要直接 ssh 启动。主线程确认 `a100-2` GPU 4/5/6/7 空闲和存储余量后，可在远端项目根执行：

```bash
cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
bash assets/launch_strict_visual_matched_texture_V23_all_family_20260510.sh --generate-only
bash assets/launch_strict_visual_matched_texture_V23_all_family_20260510.sh
```

如果只想单卡分批：

```bash
bash assets/launch_strict_visual_matched_texture_V23_all_family_20260510.sh --worker 4
bash assets/launch_strict_visual_matched_texture_V23_all_family_20260510.sh --worker 5
bash assets/launch_strict_visual_matched_texture_V23_all_family_20260510.sh --worker 6
bash assets/launch_strict_visual_matched_texture_V23_all_family_20260510.sh --worker 7
```

默认使用 `STEPS=8`、`TEXTURE_SIZE=2048`、OBJ input + PBR guide，输出到 `results/strict_visual_matched_texture_V23_all_family_20260510`。

## 5. 存储风险

风险等级：中。16 个 Trellis2 mesh/PBR GLB 输出加 2048 贴图、日志、triton/cache 中间文件，保守上界约 64 GB；用户当前允许远端项目目录最高约 200 GB，但仍应清理明确不用的失败、低分辨率和重复 cache。若空间紧张，先降低 `TEXTURE_SIZE=1024` 或只启动 GPU 4/5 的 8 个主候选。

## 6. paper-grade 后处理门槛

每个远端结果需要补：

- post-GLB `LCR/RAR/PTR` 或 family metric。
- L-system：visible depth、branch/rootlet/leaf attachment QA。
- space-colonization：attractor coverage、nearest-attractor distance、path-to-root。
- DLA：frontier survival、bridge certificate、blockiness、porosity/tip/neck。
- IFS：orbit error、symmetry IoU、contact bridge survival。
- white overview + root/junction/frontier/contact/tip/facet zoom。

只有通过这些门槛的结果才能写成 paper-grade strict matched evidence。
