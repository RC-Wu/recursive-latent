# V14 Branching Coral Strict Visual-Matched 方案

日期：2026-05-10

## 背景

V13 的人工审核指标已通过：8/8 case 在 r0/r1/r2 上都是 single component，LCR=1.0，并修复了 V12 的圆柱杆和截断端问题。但视觉上仍有不足：

- staghorn / table / frontier 有些读起来像爪状岩壳、动物壳或晶体片；
- 主体局部体块仍偏大，容易形成 blob 或板片；
- 分支层级不够细，缺少更自然的 staghorn / antler / coral-branch 结构。

V14 因此继续保留 V13 的隐式 metaball/SDF + marching-cubes 单组件策略，但把体量从大 lobe / plate 转移到更细的多级枝状结构。

## 生成设计

V14 保留严格匹配元数据：

- `stochastic_frontier_attachment`
- `occupancy_exclusion`
- `connected_projection`
- `traditional DLA/frontier accretive attachment`
- fresh on `a100-2`
- GPU 只使用 `4,5,6,7`
- 不做本地结果挑选，不复用 V1-V13 输出

视觉输入改为：

- 增加 active-tip skeleton 的节点预算和分支概率；
- 降低 `base_radius` / `tip_radius`，让主体更细；
- terminal lobe 从 V13 的较大三段圆头改为更小的两段圆头；
- 在 terminal 和高深度节点附近增加 connected antler-tip subbranch；
- 为 subbranch anchor 加入重叠密度，避免小孤岛；
- 增加小孔和 ridge microrelief，但所有 primitive 都必须贴附单一 frontier skeleton；
- frontier/table 保持扁平趋势，但减少大板片视觉；
- crystal backup 保持连通 ridge/branch 细节，避免块状碎片。

## Case 组成

共 8 个 case：

- 2 个 fine branching staghorn coral；
- 2 个 fine branching table coral；
- 2 个 fine branching frontier coral；
- 2 个 connected crystal ridge / branch backup。

每个 case 都输出：

- OBJ；
- guide PNG；
- metadata JSON；
- manifest row；
- initial mesh metrics；
- a100-2/gpu split 文本。

## 本地验证门槛

本地 dry-run 必须满足：

- `mesh_component_count == 1`；
- `largest_mesh_component_vertex_ratio == 1.0`；
- 元数据声明 `direct_tube_mesh == false`；
- `implicit_grid_resolution >= 72`；
- `generated_nodes >= 150`；
- `metaball_sample_count >= 1100`；
- `micro_branch_count >= 55`；
- `antler_tip_count >= 40`；
- `subtractive_pore_count >= 22`；
- `large_lobe_scale_max <= 0.78`；
- `thin_tip_radius_max <= 0.014`；
- operator 中包含 `fine_antler_tip_subbranching`、`reduced_lobe_volume`、`porous_ridge_microrelief`。

## 推荐远端命令

不要在本地启动远端任务。审核通过后，在 a100-2 项目环境执行：

```bash
cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
bash assets/launch_strict_visual_matched_texture_v14_branching_coral_20260510.sh
```

可选覆盖：

```bash
SEED=20260510 STEPS=8 TEXTURE_SIZE=2048 bash assets/launch_strict_visual_matched_texture_v14_branching_coral_20260510.sh
```

## 本地 dry-run 命令

仅生成本地输入，不启动远端：

```bash
python3 assets/strict_visual_matched_cases_v14_branching_coral_20260510.py \
  --root /Users/fanta/code/agent/Code/recursive_3d_generative_growth \
  --out /tmp/rgg_v14_branching_coral_dryrun \
  --seed 20260510
```

对应测试：

```bash
python3 -m pytest -q tests/test_strict_visual_matched_cases_v14_branching_coral_20260510.py
```
