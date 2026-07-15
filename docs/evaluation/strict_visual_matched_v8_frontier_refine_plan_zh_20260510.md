# V8 frontier refine strict visual matched plan

日期：2026-05-10

## 背景

最新 strict one-to-one 比较要求必须在 `a100-2` 重新生成新 case，不能只做本地后处理或从旧结果里挑选。V6 解决了植物和部分非树结构的连通性，但 DLA/coral/frontier 仍容易读成块状石头。V7 把 DLA/reef 改成连通、较亮的有机管状输入，但端头仍偏胶囊或菌状。

V8 只生成新的本地输入根文件，不启动远端、不使用 SSH、不修改 V1-V7 文件。最终结果仍由 main thread 在 `a100-2` 上用 GPU `4/5/6/7` 重新生成。

## 算法目标

V8 保持传统递归模式：

- stochastic frontier attachment；
- occupancy exclusion；
- DLA/coral/frontier/crystal 同一类 accretive attachment comparison；
- 每个 OBJ 初始结构必须是单组件或近单组件。

V8 改变的是输入几何实例化：

- 用 rooted continuous center skeleton 作为所有 case 的起点；
- 用 smooth tapered tubes 替代 voxel/cube/chunk；
- 用 small-scale branchlets 增加珊瑚枝杈密度；
- 用 thin plates/ridges 和少量 edge-attached porous membranes 形成礁、边界膜和晶体脊；
- 避免 detached shards、floating sheets、global blob、large capsule tips。

## 输出

脚本：

```bash
python3 assets/strict_visual_matched_cases_v8_frontier_refine_20260510.py
```

默认 dry-run 输出目录：

`results/strict_visual_matched_cases_v8_frontier_refine_20260510_dryrun`

关键文件：

- `manifest.csv` / `manifest.json`
- `initial_metrics.csv` / `initial_metrics.json`
- `a100-2_cases.txt`
- `gpu4_cases.txt` / `gpu5_cases.txt` / `gpu6_cases.txt` / `gpu7_cases.txt`
- `gpu4567_cases.txt`
- `_guides/*.png`
- per-case `*_metadata.json`
- `README.md`

## Case 设计

V8 生成 10 个 DLA/frontier case，覆盖：

- `dla_coral_cluster_900`
- `dla_frontier_sheet_700`
- `dla_crystal_cluster_520`

优先远端先跑：

1. `v8_dla_coral_lace_reef_branching_a`
2. `v8_dla_coral_antler_ridge_branching`
3. `v8_dla_coral_porous_table_reef`
4. `v8_dla_frontier_fan_lace_membrane_a`
5. `v8_dla_frontier_terraced_ridge_sheet`
6. `v8_dla_crystal_accretive_blade_cluster`
7. `v8_dla_crystal_pyrite_ridge_cluster`

备选/鲁棒性 seed：

- `v8_dla_frontier_open_boundary_seed_b`
- `v8_dla_coral_lace_reef_branching_b`
- `v8_dla_crystal_frontier_prism_seed_b`

## 验收门槛

硬门槛：

- `remote_target == a100-2`
- `allowed_gpus == [4, 5, 6, 7]`
- case 数量在 8-12 之间
- 每个 OBJ `mesh_component_count <= 2`
- 每个 OBJ `largest_mesh_component_vertex_ratio >= 0.985`
- manifest、metrics、guide PNG、metadata、per-GPU case list 齐全

视觉门槛：

- neutral render 应能直接读出珊瑚/礁/晶体，不应读成孤立块；
- coral/frontier 应显示连续生长边界、分叉和孔洞膜；
- crystal 应显示连接的 blade/ridge/facet，而不是漂浮碎片；
- dry-run 指标只是输入质量 gate，不能替代 `a100-2` 新生成结果的人工视觉 QA。

## 测试

```bash
python3 -m py_compile assets/strict_visual_matched_cases_v8_frontier_refine_20260510.py
python3 -m pytest -q tests/test_strict_visual_matched_cases_v8_frontier_refine_20260510.py
python3 assets/strict_visual_matched_cases_v8_frontier_refine_20260510.py
```
