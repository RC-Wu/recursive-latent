# 远端实验跟进状态 2026-05-10

采样时间：2026-05-09 23:50-23:55 CST  
远端主机：`a100-2`  
远端根目录：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`

## 1. 远端资源状态

- 项目目录占用：`94G`，低于 `100GB` 上限，但只剩约 `6GB` 余量。
- GPU 4/5/6/7 状态：全部空闲。
  - GPU 4: `0 / 81920 MiB`, util `0%`
  - GPU 5: `0 / 81920 MiB`, util `0%`
  - GPU 6: `0 / 81920 MiB`, util `0%`
  - GPU 7: `0 / 81920 MiB`, util `0%`
- 项目相关进程：未发现仍在运行的 `$ROOT` 相关进程。
- `screen -ls`：远端当前 shell 环境中 `screen` 不可用，不能依赖 screen session 监控。

## 2. 已发现的最新结果

### `texture_latest_variation`

远端目录：

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/texture_latest_variation_ralph_20260509_234319`

关键子结果：

- `pyrite_depth4_warm_alt/textured.glb`
- `bismuth_depth4_warm_alt/textured.glb`
- `coral_stage4_edge_alt/textured.glb`
- `scifi_repaired_gear_alt/textured.glb`
- `flow_vine_steps8_seedB/summary.json`
- `flow_coral_steps8_seedB/summary.json`

`flow_vine_steps8_seedB` 和 `flow_coral_steps8_seedB` 的 summary 当前只记录 `case` 和 `steps=8`，没有连通性指标。

### `flow_sde_runtime_stub`

远端目录：

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/flow_sde_runtime_stub_grid_ralph_20260509_233429`

关键 summary：

- `flow_vine_steps2_stub/summary.json`: `steps=2`
- `flow_coral_steps2_stub/summary.json`: `steps=2`
- `flow_bismuth_steps2_stub/summary.json`: `steps=2`
- `flow_pyrite_steps2_stub/summary.json`: `steps=2`

这些 summary 目前是 runtime stub 级别，只能证明 run 产生了按步数命名的输出；不能直接支撑 flow/SDE connectivity claim。

### `texture_latest_occupancy_positive`

远端目录：

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/texture_latest_occupancy_positive_ralph_20260509_233723`

关键子结果：

- `pyrite_depth4_occpos_sparse_close/textured.glb`
- `bismuth_depth4_occpos_sparse_close/textured.glb`
- `coral_stage4_occpos_sparse_close/textured.glb`
- `flow_pyrite_steps6_stub/summary.json`

`flow_pyrite_steps6_stub` 当前 summary 只记录 `case` 和 `steps=6`，没有 connectivity metrics。

## 3. 本轮新启动并完成的低存储实验

由于 GPU 4/5/6/7 空闲，但远端只剩约 `6GB` 余量，本轮没有启动新的大规模 GLB/mesh 生成。只启动了一个复用已有 GLB 的 surface-voxel connectivity metric extraction，输出规模为 `14K`。

结果目录：

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/connectivity_followup_metrics_20260509_2351`

日志目录：

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/connectivity_followup_metrics_20260509_2351`

输出文件：

- `aggregate_surface_voxel_summary.json`
- `texture_latest_variation_ralph_20260509_234319_surface_voxel.csv`
- `texture_latest_variation_ralph_20260509_234319_surface_voxel.json`
- `texture_latest_occupancy_positive_ralph_20260509_233723_surface_voxel.csv`
- `texture_latest_occupancy_positive_ralph_20260509_233723_surface_voxel.json`

缓存和临时目录均在项目根目录下：

- `$ROOT/.cache/connectivity_followup_metrics_20260509_2351/tmp`
- `$ROOT/.cache/connectivity_followup_metrics_20260509_2351/xdg`
- `$ROOT/.cache/connectivity_followup_metrics_20260509_2351/hf`
- `$ROOT/.cache/connectivity_followup_metrics_20260509_2351/torch`
- `$ROOT/.cache/connectivity_followup_metrics_20260509_2351/matplotlib`
- `$ROOT/.cache/connectivity_followup_metrics_20260509_2351/triton`

未使用远端 `/tmp` 或 `/dev/shm`。

## 4. 新 metric 结果摘要

本轮对 7 个已有 textured GLB 做了 surface-sampled voxel connectivity 诊断，主口径为 resolution 64、6-neighbor components、r0/r1/r2 dilation。结果显示：

| label | source | r0 comp | r0 LCR | r1 comp | r1 LCR | 判断 |
|---|---|---:|---:|---:|---:|---|
| `bismuth_depth4_occpos_sparse_close` | occupancy positive | 1 | 1.000 | 1 | 1.000 | 强正面 |
| `bismuth_depth4_warm_alt` | variation | 1 | 1.000 | 1 | 1.000 | 强正面 |
| `coral_stage4_edge_alt` | variation | 1 | 1.000 | 1 | 1.000 | 强正面 |
| `coral_stage4_occpos_sparse_close` | occupancy positive | 1 | 1.000 | 1 | 1.000 | 强正面 |
| `pyrite_depth4_occpos_sparse_close` | occupancy positive | 1 | 1.000 | 1 | 1.000 | 强正面 |
| `pyrite_depth4_warm_alt` | variation | 1 | 1.000 | 1 | 1.000 | 强正面 |
| `scifi_repaired_gear_alt` | variation | 72 | 0.9986 | 1 | 1.000 | r0 碎片多，但 r1 后连通；适合作为 seam/alias-tolerant renderability 证据，不适合作为严格 topology 正例 |

结论：当前 `texture_latest_*` 中 pyrite/bismuth/coral 的 textured GLB 在 surface-voxel 口径下已经可以作为 connectivity-positive paper evidence；`scifi_repaired_gear_alt` 需要谨慎，只能说 seam-tolerant surface occupancy 连通。

## 5. Blockers / 风险

1. 远端空间已到 `94G/100G`，不能再开 broad large GLB batch；后续优先只做 summary/CSV/小图诊断，或先清理确认无用的大结果。
2. `flow_sde_runtime_stub*` 当前 summary 太薄，只记录步数，没有 components/LCR/runtime 细表；不能直接写成 flow/SDE connectivity 实验证据。
3. `screen` 在当前远端 shell 不可用；后续长任务需要改用 `nohup`/后台 PID 文件或同步短任务。
4. 本轮没有拉取大型 mesh/GLB，本地只记录远端路径和小型 summary 结论；如要做论文图，需要再选择性拉取少数已确认正面的 GLB。

## 6. 下一步建议

- 立即可用：把 `connectivity_followup_metrics_20260509_2351/aggregate_surface_voxel_summary.json` 中的 6 个 r0 完全连通 textured GLB 写入实验表候选。
- 谨慎补强：对 flow/SDE stub 的 `mesh.obj` 运行同一 surface/occupancy metric，输出只保留 CSV/JSON，不生成新 GLB。
- 不建议：在当前 94G 占用下继续生成大批新 textured GLB。
