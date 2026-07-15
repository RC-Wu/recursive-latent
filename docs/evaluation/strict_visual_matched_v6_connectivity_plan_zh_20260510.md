# V6 strict visual matched connectivity plan

日期：2026-05-10

## 目标

V6 只负责生成新的 strict one-to-one comparison 输入，不复用、不挑选、不后处理 V3/V4/V5 远端结果。最终 strict visual comparison case 必须在 `a100-2` 新生成，远端只使用 GPU `4/5/6/7`，产物写入：

`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`

存储上限按 `100GB` 控制。

## V5 视觉反馈转化

V5 的 dry-run 和远端指标已基本可接受，但 contact sheet 显示视觉不够发表级：

- DLA coral/frontier 像黑色或棕色块状石头，不像连续生长的 organic frontier。
- L-system pine/vine/root 与 SC root/crown 已连通，但太像裸杆 scaffold，缺少叶片、针叶、细根层级和自然包络。
- radial ornament 结构可读，但材质/配色过花，且不是当前主文最关键 case。

V6 的修正策略：

- organic case：连续主枝/根 spine + 大量定向 leaf/needle/rootlet primitives + 局部 smooth envelope panels；不只依赖 cylinder/cone scaffold，也不做全局 blob。
- DLA/coral/frontier：connected branching tubes + bulbous/smooth tips + porous bridges；减少 faceted voxel chunks 和石头感。
- crystal：若作为 DLA/frontier 的非树类对照，走 bismuth/pyrite stepped lattice facets，但所有 facet 都必须由 shared skeleton/bridge 连到主结构。
- IFS/radial：保留结构可读性，作为次优/备选，不优先占主文位置。

## Dry-run 门槛

最低硬门槛：

- 每个 initial OBJ 必须是 `mesh_component_count == 1`。
- `largest_mesh_component_vertex_ratio == 1.0`。
- metadata 必须记录 root/source、operator family、operator composition、traditional target、controls、为何 strict match。

视觉门槛：

- single component 只是最低门槛，不等于可发表。
- neutral render/contact sheet 必须能直接读出 traditional target family。
- organic case 要能看见层级化叶/针/根须，而不是裸杆。
- DLA/coral 要能看见连续 accretive branching 和 organic porous frontier，而不是块状石头。
- crystal/lattice 要能看见 bismuth/pyrite stepped facets 或 affine lattice copy 关系，不能是漂浮碎片。

## V6 case 优先级

优先先上 `a100-2`：

1. `v6_dla_coral_cluster_900_connected_tube_sheet`
2. `v6_dla_frontier_sheet_700_connected_boundary_sheet`
3. `v6_dla_crystal_facet_cluster_connected_bridges`
4. `v6_lsys_pine_canopy_d5_same_rule_welded_needles`
5. `v6_lsys_root_fan_d5_same_rule_welded_hairs`
6. `v6_sc_tree_crown_260_same_attractor_welded_leaf_shell`
7. `v6_sc_root_network_260_same_attractor_welded_rootlets`
8. `v6_ifs_radial_ornament_o8_d4_connected_facets`

备选/补充：

- `v6_lsys_climbing_vine_d6_same_curl_attached_leaves`
- `v6_sc_bush_shell_220_same_attractor_welded_shell`
- `v6_ifs_fractal_lattice_d4_connected_copy_facets`

## 本地 dry-run

```bash
python3 assets/strict_visual_matched_cases_v6_connectivity_20260510.py
```

输出目录默认：

`results/strict_visual_matched_cases_v6_connectivity_20260510_dryrun`

关键文件：

- `manifest.csv`
- `manifest.json`
- `initial_metrics.csv`
- `initial_metrics.json`
- `a100-2_cases.txt`
- `gpu4567_cases.txt`
- per-case `*_metadata.json`

## 测试

```bash
python3 -m pytest -q tests/test_strict_visual_matched_cases_v6_connectivity_20260510.py
```

测试覆盖：

- dry-run 输出 manifest/metrics/case list。
- remote target 固定为 `a100-2`。
- GPU group 只允许 `4/5/6/7`。
- storage root 和 `100GB` 限制写入 summary/manifest/metadata。
- 每个 initial mesh 是 single component。
- metadata 包含 strict one-to-one policy、operator family、traditional alignment、visual readability contract。
