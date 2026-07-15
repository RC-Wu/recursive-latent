# V16 Natural Coral Strict Visual-Matched 方案

日期：2026-05-10

## 背景

V14 已经把 r0 连通性做到 perfect，但人工视觉审核仍指出：

- 分支仍有 faceted / low-poly / coarse branch 感；
- staghorn、table、frontier 的 coral/reef 语义不够强；
- 不能只做本地 mesh/textured output 后处理，必须在 a100-2 上重新生成新 case。

V16 因此作为 V14 之后的 remote-generation algorithmic branch。目标不是修补已有输出，而是生成更自然的 DLA/frontier/coral/crystal 输入根几何，让 Trellis2 texturing 接收到更像珊瑚礁的连通形体。

## 生成设计

V16 保留严格匹配条件：

- `stochastic_frontier_attachment`
- `occupancy_exclusion`
- `bridge_root_connectivity`
- `traditional DLA/frontier accretive attachment`
- fresh on `a100-2`
- GPU 只使用 `4,5,6,7`
- 不做本地结果挑选，不复用 V1-V15 textured output

几何侧改动：

- 使用高分辨率 implicit SDF / metaball union + marching cubes；
- 在输入生成阶段做 Gaussian field smoothing 与 Taubin/Laplacian shape smoothing；
- 每条 frontier edge 使用更高 section sampling，避免粗棱和低多边形分支；
- terminal 端点做 rounded/tapered tips，避免 flat cut；
- 添加 attached polyp buds、subtle pore depressions、surface ridge microrelief；
- 添加 continuous reef base，使所有 case 有 bridge/root 连续支撑；
- 对 crystal boundary 保留 faceted 语义，但必须是连通 ridge/boundary，而不是 detached block shards。

## Case 组成

共 8 个 case，按 gpu4..gpu7 均分：

- 2 个 natural staghorn；
- 1 个 branching elkhorn；
- 1 个 table coral；
- 1 个 porous reef plate；
- 1 个 frontier sheet；
- 2 个 faceted crystal boundary。

传统目标仍只覆盖：

- `dla_coral_cluster_900`
- `dla_frontier_sheet_700`
- `dla_crystal_cluster_520`

## 本地验证门槛

本地 dry-run 只验证输入根几何，不启动远端。门槛：

- `mesh_component_count == 1` 或 `largest_mesh_component_vertex_ratio >= 0.999`；
- `implicit_grid_resolution >= 84`；
- `section_samples_per_edge >= 14`；
- `taubin_smoothing_iterations >= 8`；
- `generated_nodes >= 180`；
- `metaball_sample_count >= 1400`；
- `rounded_terminal_tip_count >= 44`；
- `attached_polyp_count >= 70`；
- `subtle_pore_depression_count >= 36`；
- `surface_ridge_count >= 70`；
- metadata 明确禁止 voxel blocks、straight rods、flat terminal cuts、huge shell/blob。

## 远端约束

Launcher 使用：

- `ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
- 所有 cache 放在 `$ROOT/cache/...`
- DINO 权重放在 `$ROOT/weights/...`
- 不使用 `/tmp/devshm`
- 支持 `RUN`、`INPUT_NAME`、`SEED`、`STEPS`、`TEXTURE_SIZE`
- worker 模式读取 `gpu4_cases.txt` ... `gpu7_cases.txt`
- 若 `summary.json` 已存在且包含 `"status": "ok"`，跳过该 case

## 推荐远端命令

不要在本地启动远端任务。审核通过后，在 a100-2 项目环境执行：

```bash
cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
bash assets/launch_strict_visual_matched_texture_v16_natural_coral_20260510.sh
```

可选覆盖：

```bash
SEED=20260510 STEPS=8 TEXTURE_SIZE=2048 bash assets/launch_strict_visual_matched_texture_v16_natural_coral_20260510.sh
```

## 本地 dry-run 命令

```bash
python3 assets/strict_visual_matched_cases_v16_natural_coral_20260510.py \
  --root /Users/fanta/code/agent/Code/recursive_3d_generative_growth \
  --out /tmp/rgg_v16_natural_coral_dryrun \
  --seed 20260510
```

对应测试：

```bash
python3 -m pytest -q tests/test_strict_visual_matched_cases_v16_natural_coral_20260510.py
```
