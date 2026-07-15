# 最新 textured connectivity 指标口径对齐说明（2026-05-10）

## 输入

- `results/connectivity_followup_metrics_20260509_2351/*_surface_voxel.csv`
- `results/connectivity_followup_metrics_20260509_2351/aggregate_surface_voxel_summary.json`
- `results/texture_latest_occpos_mesh_metrics_20260509/texture_latest_occpos_mesh_metrics.csv`
- `docs/remote_results/remote_experiment_followup_zh_20260510.md`
- `/Users/fanta/Downloads/agent_revision_and_experiment_requirements.md`

## 结论先行

最新 `texture_latest_*` textured GLB 结果不能用单一 raw face component 或单一 vertex-voxel 指标解释。建议论文中采用三层表述：

1. **主 textured 正例**：`pyrite_depth4_occpos_sparse_close`、`pyrite_depth4_warm_alt`、`bismuth_depth4_occpos_sparse_close`、`bismuth_depth4_warm_alt`。它们在 surface-voxel strict r0 和 seam-tolerant r1/r2 下均为 `1 comp, LCR=1.000`，且已有 vertex-voxel 主指标也为 `1 comp, LCR=1.000`。
2. **边界正例**：`coral_stage4_occpos_sparse_close`、`coral_stage4_edge_alt`。它们在 surface-voxel r0/r1/r2 下均为 `1 comp, LCR=1.000`，适合支持“textured surface renderability / non-tree surface occupancy connectedness”；但旧 mesh 指标里 coral 的 vertex-voxel 为 `3 comps, LCR=0.883`，welded face LCR 也只有 `0.893`，因此不应作为严格 vertex/face topology 主正例。
3. **仅 export compatibility / seam-tolerant 证据**：`scifi_repaired_gear_alt`。它可以导出和渲染，surface-voxel r1 后为 `1 comp, LCR=1.000`，但 strict r0 仍有 `72 comps`，只能说明 seam/alias-tolerant surface occupancy 近似连通，不能写成严格连通或 topology-clean。

纹理/PBR 仍按需求文档降级为 compatibility：这些结果证明 selected projected meshes 可以走 frozen Trellis2 texture/export path，不证明 texture 本身是本文核心贡献，也不证明 watertight raw mesh topology。

## 指标口径如何对齐

| 口径 | 本轮含义 | 适合支持 | 不适合支持 |
|---|---|---|---|
| surface-voxel r0/r1/r2 | 从 GLB 表面采样点后体素化，做 6-neighbor component；r1/r2 给 seam/alias 容忍 | textured GLB 的可渲染几何支持是否空间连通 | watertight topology、raw face graph 完整性 |
| vertex-voxel occupancy | 只用 mesh 顶点体素化后的 6-neighbor component | 跨 OBJ/GLB 的粗空间 proxy；对大块结构较稳 | 细连接、缺少顶点采样的面片、导出 seam 后的表面连续性 |
| raw face components | 原始三角面共享边/顶点的 graph component | 导出碎片、UV/material island、未 weld 面片的 caveat | textured asset 是否视觉连通的主判断 |
| welded face components | 量化顶点焊接后再做 face graph | 判断是否只是重复/近重合顶点造成的 face fragmentation | 单独作为跨类别主指标；容差会改变几何并引入尺度依赖 |

## 核心表

| case | source | surface-voxel strict r0 | surface-voxel r1 | vertex/raw/welded 对照 | 建议论文使用 |
|---|---|---:|---:|---|---|
| `bismuth_depth4_occpos_sparse_close` | occupancy positive | `1 / 1.000` | `1 / 1.000` | vertex `1 / 1.000`; raw face `9856 comps, LCR=0.028`; welded `3 comps, LCR=0.994` | 主 textured 正例；raw face 只作 export seam caveat |
| `bismuth_depth4_warm_alt` | variation | `1 / 1.000` | `1 / 1.000` | 几何规模与 occpos bismuth 相同；未在 mesh CSV 单独列出 | 主 textured 正例；作为材质/guide variation |
| `pyrite_depth4_occpos_sparse_close` | occupancy positive | `1 / 1.000` | `1 / 1.000` | vertex `1 / 1.000`; raw face `80156 comps, LCR=0.001`; welded `3 comps, LCR=0.990` | 主 textured 正例；最适合 crystal-like asset compatibility |
| `pyrite_depth4_warm_alt` | variation | `1 / 1.000` | `1 / 1.000` | 几何规模与 occpos pyrite 相同；未在 mesh CSV 单独列出 | 主 textured 正例；作为 warm material variation |
| `coral_stage4_occpos_sparse_close` | occupancy positive | `1 / 1.000` | `1 / 1.000` | vertex `3 / 0.883`; raw face `31154 comps, LCR=0.001`; welded `3 comps, LCR=0.893` | 边界正例；可写 surface-renderability connected，不写 strict topology clean |
| `coral_stage4_edge_alt` | variation | `1 / 1.000` | `1 / 1.000` | 几何规模与 occpos coral 相同；旧 vertex/welded caveat 仍适用 | 边界正例；可放 non-tree/coral-inspired surface case |
| `scifi_repaired_gear_alt` | variation | `72 / 0.9986` | `1 / 1.000` | 本轮无 mesh CSV 对照；surface r0 已显示大量小碎片 | 仅 export compatibility；最多写 seam-tolerant connected renderability |

## 对论文 claim 的建议写法

可以写：

> Selected pyrite and bismuth textured exports remain connected under both vertex-voxel and surface-sampled voxel diagnostics, while coral-like exports are connected under the more appropriate surface-sampled diagnostic but remain boundary cases under vertex-only and welded face metrics.

可以写：

> Textured GLB exports are evaluated as asset-readiness and renderability evidence; raw face fragmentation is reported as an export diagnostic rather than the primary structural metric.

不要写：

> All textured outputs are topology-clean.

不要写：

> Texture/PBR is a core contribution or repairs structural connectivity.

不要写：

> `scifi_repaired_gear_alt` is a strict connectivity-positive case.

## 最终分类

- **主正例**：pyrite occpos、pyrite warm、bismuth occpos、bismuth warm。
- **边界正例**：coral occpos、coral edge。
- **仅导出兼容性**：scifi repaired gear。

