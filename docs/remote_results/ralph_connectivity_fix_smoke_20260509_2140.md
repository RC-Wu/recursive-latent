# Ralph 远程连通性修复烟测状态 - 2026-05-09 21:40

## 目标

本轮只做一次聚焦 Ralph-iteration：验证上一轮 `connectivity_first_dla_crystal_20260509` 的远程导入失败是否已经修复，并在 GPU 4/5/6/7 约束下跑一个最小 DLA 连通性烟测。没有编辑 `paper_siga/main.tex`，没有编辑 gallery。

## 远程运行

- Host: `a100-2`
- 远程根目录: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
- 运行 ID: `run_20260509_213606_2501185`
- 远程输出: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/connectivity_first_dla_crystal_20260509_fix_import_smoke/run_20260509_213606_2501185`
- 远程日志: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/connectivity_first_dla_crystal_20260509_fix_import_smoke/run_20260509_213606_2501185/smoke.log`
- 启动时项目占用: `75G`，低于 100GB 上限
- 启动时 GPU 状态: GPU 4 `0/81920 MiB`，GPU 5 `0/81920 MiB`
- 实际使用 GPU: `4`
- 未使用 GPU: `0,1,2,3,5,6,7`
- 远程退出状态: `0`

缓存和临时目录全部放在项目内：

```bash
TMPDIR=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.cache/connectivity_first_dla_crystal_20260509_fix_import_smoke/run_20260509_213606_2501185/tmp
HF_HOME=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.cache/connectivity_first_dla_crystal_20260509_fix_import_smoke/run_20260509_213606_2501185/hf
XDG_CACHE_HOME=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.cache/connectivity_first_dla_crystal_20260509_fix_import_smoke/run_20260509_213606_2501185/xdg
TORCH_HOME=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.cache/connectivity_first_dla_crystal_20260509_fix_import_smoke/run_20260509_213606_2501185/torch
TRITON_CACHE_DIR=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.cache/connectivity_first_dla_crystal_20260509_fix_import_smoke/run_20260509_213606_2501185/triton/gpu4
MPLCONFIGDIR=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.cache/connectivity_first_dla_crystal_20260509_fix_import_smoke/run_20260509_213606_2501185/matplotlib
TORCH_EXTENSIONS_DIR=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.cache/connectivity_first_dla_crystal_20260509_fix_import_smoke/run_20260509_213606_2501185/torch_extensions
```

未使用远程 `/tmp` 或 `/dev/shm`。

## 精确命令

本轮只使用一个 SSH 会话；本地将两个必要脚本打包，远程解包后同步运行烟测，并把小型 JSON/PNG/MD artifacts 通过 stdout tarball 拉回本地。

远程实际实验命令为：

```bash
CUDA_VISIBLE_DEVICES=4 \
TRITON_CACHE_DIR=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.cache/connectivity_first_dla_crystal_20260509_fix_import_smoke/run_20260509_213606_2501185/triton/gpu4 \
/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/envs/trellis2_bakeoff/bin/python \
/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/connectivity_first_dla_crystal_20260509.py \
  --root /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 \
  --out /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/connectivity_first_dla_crystal_20260509_fix_import_smoke/run_20260509_213606_2501185 \
  --case dla_voxel_root=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/inputs/procedural_meshes/dla_cluster_voxels.obj \
  --grammars fork_side_attach \
  --methods sparse_close_bridge \
  --stages 1 \
  --max-tokens 14000 \
  --min-vertices 1800 \
  --mesh-bridge-components 10 \
  --texture-top-k 0
```

关键预检通过：

```text
import_ok=recursive_growth_mesh_metrics /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/assets/recursive_growth_mesh_metrics.py
```

## 拉回本地的小型 artifacts

本地目录：

`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/remote_results/connectivity_first_fix_smoke_20260509_pull/unpacked`

包含：

- `REMOTE_STATUS.md`
- `summary.json`
- `summary_partial.json`
- `run_config.json`
- `selected_candidates.json`
- `dla_voxel_root/fork_side_attach/sparse_close_bridge/summary.json`
- `dla_voxel_root/fork_side_attach/sparse_close_bridge/summary_partial.json`
- `stage_01/raw/proposal_before_connectivity.png`
- `stage_01/sparse_connectivity/proposal_after_sparse_connectivity.png`
- `stage_01/projected/mesh_projected.png`

未拉回大型 OBJ；远程 OBJ 仍在结果目录下。

## 指标

唯一候选：

- case: `dla_voxel_root`
- grammar: `fork_side_attach`
- method: `sparse_close_bridge`
- stage: `1`
- input tokens: `1162`
- proposal tokens: `1869`

Raw decode:

- vertices: `634580`
- faces: `1236902`
- face components: `3157`
- face largest-component ratio: `0.980987`
- occupancy components: `4`
- occupancy LCR: `0.995475`
- occupied voxels: `17016`

Sparse connectivity support:

- sparse before components: `1`
- sparse before LCR: `1.0`
- sparse tokens before: `1869`
- sparse after components: `1`
- sparse after LCR: `1.0`
- sparse tokens after: `2290`
- bridge voxels added: `0`

Decoded sparse result:

- vertices: `726702`
- faces: `1403372`
- face components: `4226`
- face largest-component ratio: `0.971899`
- occupancy components: `29`
- occupancy LCR: `0.994233`
- occupied voxels: `20113`

Mesh projection:

- input mesh components: `4084`
- kept components: `12`
- kept large components: `10`
- attached components: `10`
- bridge meshes added: `10`
- pruned components: `4072`
- final vertices: `301989`
- final faces: `549852`
- final face components: `1`
- final face largest-component ratio: `1.0`
- final occupancy components: `6`
- final occupancy LCR: `0.939027`
- final occupied voxels: `11054`
- selection score: `0.927027`

## 可用性判断

结果可用于“远程 harness 修复”和“bridge/projection 能把碎片 mesh 面连成单一 face component”的证据：上一轮缺失的 `recursive_growth_mesh_metrics` 导入问题已修复，raw/sparse/projected 三类 preview 都产生了，stage-1 pipeline 完整跑通。

结果暂时不能作为强 DLA/crystal 正例：虽然 face component 从 `3157` 降到 `1`，但 occupancy components 从 raw `4` 变成 projected `6`，occupancy LCR 从 `0.995475` 降到 `0.939027`。按之前验收标准“projected occupancy component count 低于 raw 且 LCR 不低于 raw”，本轮不通过。适合写成诊断：当前 mesh bridge 对表面连通有效，但会牺牲体素占据连通指标，需要下一步把 occupancy-aware selection 或 sparse/mesh 双指标约束放进 stage-1 小对比。

## 下一步建议

不要直接放大到 stage 3。先在同一 stage-1 设置下做非常小的对比：`sparse_close_bridge` vs `sparse_bridge_select` vs `mesh_bridge_smooth`，并把选择标准改为同时要求 face component 改善和 occupancy LCR 不下降。只有当 projected occupancy 指标不退化时，再考虑 DLA/porous/vine 三 case 小批量。
