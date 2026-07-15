# Latent-space vs mesh-space / texture-only 证据现状（2026-05-10 00:24）

## 目的

修订文档的核心质疑是：本文是否只是 “procedural mesh recursion + projection + Trellis2 texture export”。为了避免这个风险，需要证明递归操作确实发生在 generator-native sparse latent state 中，并且这种执行方式比 mesh-space 后处理或只做 Trellis2 texture export 更合适。

本 note 先整理现有数据中与这一问题直接相关的证据。结论必须谨慎：当前数据能支持“texture-only 不足以保证结构资产可用”的方向性证据，但还不能替代正式的同根、公平 latent-vs-mesh 实验。

## 汇总文件

- 行级表：`results/latent_vs_mesh_texture_evidence_20260510/latent_vs_mesh_texture_evidence_rows.csv`
- 协议汇总：`results/latent_vs_mesh_texture_evidence_20260510/latent_vs_mesh_texture_evidence_protocol_summary.csv`

## 当前数字

| protocol | n | occupancy positive | mean occ. comps | mean occ. LCR | 解释 |
|---|---:|---:|---:|---:|---|
| mesh_space_traditional_texture_only | 4 | 0 | 218.25 | 0.4807 | 传统程序 mesh 直接进入 Trellis2 texture/export 后，在 vertex-voxel occupancy 代理上通常碎裂 |
| connected_scaffold_trellis_texture_selected | 12 | 6 | 1.67 | 0.9986 | 选出的 connected scaffold + Trellis2 texture 有一半达到 occupancy-positive，但 raw face graph 仍很多 components |
| latest_projected_sparse_latent_texture_selected | 3 | 2 | 1.67 | 0.9610 | 最新 projected sparse-latent candidates 中 bismuth/pyrite occupancy-positive，coral 边界 |

## 可支撑的谨慎说法

1. **Trellis2 texture/PBR export 本身不能证明结构正确。**  
   传统 IFS/L-system/space-colonization root 直接 texture 后出现大量 occupancy components 和极低 raw face largest-component ratio。

2. **当前 selected projected candidates 在 occupancy-primary 结构代理上更稳定。**  
   bismuth/pyrite 以及多个 connected scaffold textured GLB 达到 `occ_comp=1` 或接近 1，说明“先让 recursive state 满足 admissibility，再 export texture”比直接 texture-only 更可靠。

3. **raw face graph 不能直接作为唯一失败判据。**  
   多个 Trellis2 GLB 的 raw face component count 很高，这可能受到 GLB/UV/material seam 切分影响。因此正文应同时报告 surface/vertex occupancy、welded face、raw face、Blender import/render success，并明确每个指标的语义。

## 不能支撑的强说法

1. 不能说 sparse-latent grammar 已经严格优于 mesh-space recursion。当前不是完全同根、同规则、同预算比较。
2. 不能说 GLB face topology-clean。大量 raw face components 仍存在。
3. 不能把 texture/PBR 作为主贡献。它只是 selected projected meshes 的 compatibility evidence。
4. 不能说 coral / hard-DLA 已完全解决。coral 是边界 positive；hard-DLA 目前仍偏 negative/stress。

## 下一步正式实验设计

需要一个同根公平矩阵：

| 维度 | 设置 |
|---|---|
| roots | vine/root, tree, pyrite/crystal, coral/porous, hard-DLA stress |
| protocols | mesh-space recursion + smoothing/remesh, mesh-space recursion + Trellis texture only, direct sparse edit, sparse-latent rule-only, sparse-latent + masked naturalization, sparse-latent + per-depth projection |
| metrics | occ components/LCR, surface-sampled components, welded/raw face components, root reachability, orphan handles, branch/tip survival, transform consistency, GLB import/render success, runtime/token/mesh growth |
| reporting | mean/std over seeds; main table + appendix full matrix |

论文中当前对应的 `\EvidencePending{Need explicit latent-space-vs-mesh-space implementation comparison...}` 必须保留，直到这个矩阵完成。
