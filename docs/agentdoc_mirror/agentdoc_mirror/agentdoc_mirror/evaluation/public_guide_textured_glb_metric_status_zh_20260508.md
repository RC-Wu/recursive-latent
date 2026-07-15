# 公开 Guide Textured GLB Mesh 指标状态 - 2026-05-08 23:59

本文记录 6 个公开图片 guide + Trellis2 textured GLB 的 mesh-level 指标。指标来自本地 `assets/recursive_growth_mesh_metrics.py`，主连通性口径为 `occupancy_6n_vertex_voxel`，因为 textured GLB 常按材质/三角片导出为大量不共享顶点的面片，raw face components 会极端虚高。

输出：

- `results/public_guide_textured_glb_metrics_20260508/metrics.json`
- `results/public_guide_textured_glb_metrics_20260508/metrics.csv`

## 1. 主指标表

| case | primary comps | primary LCR | occupied voxels | box-count proxy | visual QA |
|---|---:|---:|---:|---:|---|
| vine tendril | 1 | 1.000 | 6016 | 1.91 | 结构和卷须好；纹理破洞/白斑 |
| tree roots | 3 | 0.993 | 11414 | 1.93 | 树/根结构可读；材质脏且破碎 |
| portal arch | 1 | 1.000 | 12416 | 2.14 | 最稳定 non-tree candidate |
| porous/gloss smoke | 1 | 1.000 | 24296 | 2.33 | glossy/PBR 成立；几何语义像瓶子 |
| scifi gear | 2 | 0.99996 | 22814 | 2.25 | 机械读法成立；黄绿偏色和孔洞明显 |
| snow arch | 3 | 0.920 | 20369 | 2.16 | 建筑资产语义清楚；仍有局部断裂 |

## 2. 解释

正面：

- `vine`、`portal`、`porous/gloss` 在 occupancy 主口径下是单一空间连通体。
- `scifi gear` 虽有两个 occupancy components，但 largest ratio 接近 1，主结构没有碎裂成多个大块。
- `tree` 与 `snow arch` 有少量 occupancy components；`tree` 主体仍占 99.3%，`snow arch` 只有 92.0%，需要更谨慎。

风险：

- raw face connectivity components 达到数万到十万级，主要反映导出/材质/三角片不共享拓扑，不应作为主实验连通性指标。
- occupancy connectivity 是空间 proxy，不等价于 watertight mesh topology。论文写作必须使用 “voxel-occupancy proxy” 字样。
- 视觉 QA 仍然比单个连通性指标更严格：`porous/gloss` 指标好但语义不对，不能作为 crystal 成功。

## 3. 论文使用建议

- Texture/PBR QA 表应同时放 `GLB export status`、`primary occupancy LCR`、`visual QA label`。
- `portal arch` 和 `scifi gear` 可以支持非树类别 textured GLB 可行性。
- `vine tendril` 支持植物/卷须 category，但主图前需处理孔洞/白斑。
- `snow arch` 可用于 architecture candidate，但最好搭配 neutral stone render 或重新投影/清理。
- `porous/gloss` 只进 “PBR channel/gloss smoke test”，不进 crystal quality claim。
