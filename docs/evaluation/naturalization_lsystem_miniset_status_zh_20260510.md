# Naturalization L-system Miniset 状态（2026-05-10）

## 结论

- miniset：`N-lsystem-localN-4col`
- case：`lsystem_branch/fork_side`
- 四列：`rule-only` / `no-N` / `weak blend` / `masked local-N`
- 主文状态：可作为谨慎的 visual/export ablation 候选。
- 不可 claim：不能 claim topology repair、root reachability、anchor preservation、mask leakage，也不能分离 naturalization 与 projection 贡献。

## 本地 QA 表

| variant | GLB import | GLB faces | GLB MB | PBR/material | occ proxy | source mesh | claim gate |
|---|---:|---:|---:|---|---:|---|---|
| rule-only | ok | 938204 | 51.716915 | 1/1; tex=2 1024x1024 | 0.067481995 | remote-only | visual_export_ablation_only_source_mesh_blocked |
| no-N | ok | 1098956 | 60.196037 | 1/1; tex=2 1024x1024 | 0.067470551 | remote-only | visual_export_ablation_only_source_mesh_blocked |
| weak blend | ok | 927980 | 50.845573 | 1/1; tex=2 1024x1024 | 0.076702118 | remote-only | visual_export_ablation_only_source_mesh_blocked |
| masked local-N | ok | 1571798 | 75.890301 | 1/1; tex=2 1024x1024 | 0.112243652 | remote-only | visual_export_ablation_only_source_mesh_blocked |

## 已完成的本地证据

- `trimesh` 成功 import 四个 selected textured GLB，并记录 geometry/material/texture/bbox/file size。
- 四个 GLB 均包含 PBR material；检测到 base-color 与 metallic-roughness texture，texture resolution 为 `1024x1024`。
- occupancy proxy 使用 `64^3` bbox vertex grid 的 unique occupied cell ratio，只能作为轻量空间占用/密度 proxy，不是连通性或 root 指标。
- GLB face count 与 selected summary 的 `mesh_faces` 一致，说明 selected export summary 与本地 GLB geometry 对齐。

## Blocker：source mesh 仍未本地化

以下 exact source mesh 路径来自 selected summary，但本地未找到对应 OBJ：

- `rule-only`: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/masked_naturalization_gapfill_20260510/lsystem_branch_rule_only_direct/fork_side/depth_03/mesh.obj`
- `no-N`: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/masked_naturalization_gapfill_20260510/lsystem_branch_masked_alpha_grid/fork_side/steps_2/alpha_0p0/depth_03/masked/mesh.obj`
- `weak blend`: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/masked_naturalization_gapfill_20260510/lsystem_branch_masked_alpha_grid/fork_side/steps_2/alpha_0p25/depth_03/masked/mesh.obj`
- `masked local-N`: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/masked_naturalization_gapfill_20260510/lsystem_branch_masked_alpha_grid/fork_side/steps_2/alpha_1p0/depth_03/masked/mesh.obj`

由于 source OBJ 不在本地，本轮没有计算：

- OBJ face connectivity / largest component ratio
- root reachability
- mask leakage
- anchor drift / preserved-token geometry drift
- with projection vs without projection 控制
- global-N matched negative/control

## Claim-safe 使用边界

可以写：在 selected L-system row 上，`rule-only/no-N/weak blend/masked local-N` 四列均能进入同一 Trellis2 texture/export path，本地 GLB import 与材质导入 QA 通过，可用于谨慎的视觉/导出状态 ablation。

不能写：masked local-N 修复拓扑、保持 root/anchor、没有 mask leakage，或自然化本身优于 projection。当前证据也不能支持完整 naturalization matrix，只支持最小四列 selected visual/export subset。

## 输出文件

- CSV：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/naturalization_lsystem_miniset_qa_20260510/naturalization_lsystem_miniset_qa.csv`
- JSON：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/naturalization_lsystem_miniset_qa_20260510/naturalization_lsystem_miniset_qa_manifest.json`
