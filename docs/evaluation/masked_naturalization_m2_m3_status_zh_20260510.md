# Masked Local Naturalization M2/M3 状态 2026-05-10

## 已完成

- M2：已导出三任务 × 六协议同相机正交 contact sheet，并为每个 task 导出 protocol strip、mask overlay、before/after edit-region overlay。
- M3：已导出 sidecar 指标草案，包含 active handle survival、root attached、orphan、frontier reachability、deleted support、handle drift、mask overlap。
- M3+：新增 deterministic grammar trace graph sidecar，从 `primitive_trace` 重建几何接触图并直接计算 root-reachable active/frontier handles 与 unsupported active support mass。
- 所有 M3 状态语义指标均标注为 metadata+mesh proxy；当前没有真实运行时 handle graph，因此不能 claim 完整 grammar-readable state proof。

## 生成路径

- M2 contact sheet：`/private/var/folders/1z/_xfcm0nn4wb01hdvlmrqlppw0000gn/T/pytest-of-fanta/pytest-160/test_m2_m3_export_writes_same_0/masked_visuals/masked_naturalization_m2_contact_sheet_20260510.png`
- M2 manifest：`/private/var/folders/1z/_xfcm0nn4wb01hdvlmrqlppw0000gn/T/pytest-of-fanta/pytest-160/test_m2_m3_export_writes_same_0/masked_visuals/m2_visual_manifest_20260510.json`
- M3 CSV：`/private/var/folders/1z/_xfcm0nn4wb01hdvlmrqlppw0000gn/T/pytest-of-fanta/pytest-160/test_m2_m3_export_writes_same_0/masked_m2_m3/m3_state_sidecar_proxy_20260510.csv`
- M3 JSON：`/private/var/folders/1z/_xfcm0nn4wb01hdvlmrqlppw0000gn/T/pytest-of-fanta/pytest-160/test_m2_m3_export_writes_same_0/masked_m2_m3/m3_state_sidecar_proxy_20260510.json`
- M3+ trace graph CSV：`/private/var/folders/1z/_xfcm0nn4wb01hdvlmrqlppw0000gn/T/pytest-of-fanta/pytest-160/test_m2_m3_export_writes_same_0/masked_m2_m3/m3_trace_graph_sidecar_20260510.csv`
- M3+ trace graph JSON：`/private/var/folders/1z/_xfcm0nn4wb01hdvlmrqlppw0000gn/T/pytest-of-fanta/pytest-160/test_m2_m3_export_writes_same_0/masked_m2_m3/m3_trace_graph_sidecar_20260510.json`
- 状态文档：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/masked_naturalization_m2_m3_status_zh_20260510.md`

## 可进论文的表/图

- 主文 Figure：`masked_naturalization_m2_contact_sheet_20260510.png`，作为 3 rows × 6 columns visual ablation。
- 补充 Figure：每个 task 的 `same_camera_protocol_strip.png`、`mask_overlay.png`、`before_after_edit_overlay.png`。
- 补充 Table：`m3_state_sidecar_proxy_20260510.csv`。表头需保留 `_proxy` 后缀，并在 caption 中说明不是 watertight/topology/true handle graph proof。
- 更推荐的补充 Table：`m3_trace_graph_sidecar_20260510.csv`。它是 deterministic grammar trace graph 指标，强于启发式 proxy，但仍不是 Trellis runtime graph。

## M3 masked local-N 摘要

| task | active survival proxy | root attached proxy | reachable frontier proxy | orphan proxy | handle drift proxy |
|---|---:|---:|---:|---:|---:|
| `botanical_root` | 0.9800 | 0.8800 | 0.1140 | 1 | 0.0462 |
| `coral_frontier` | 0.9800 | 0.8800 | 0.1425 | 1 | 0.0451 |
| `ifs_crystal` | 0.9800 | 0.8800 | 0.1607 | 1 | 0.0461 |

## M3+ trace graph masked local-N 摘要

| task | active reachable | frontier reachable | unsupported active mass | root-attached mass | handle drift |
|---|---:|---:|---:|---:|---:|
| `botanical_root` | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.0021 |
| `coral_frontier` | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.0040 |
| `ifs_crystal` | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.0034 |

## 仍缺口

- M2 当前为 deterministic orthographic projection，不是 Blender/Cycles 或论文最终 renderer；可作为快速审稿前 QA 和 figure draft。
- M3 当前只能用 `primitive_trace`、`edit_mask_centers`、projection/naturalization flags 与 mesh LCR 做 proxy；仍缺真实 active handle IDs、parent-child graph、frontier graph reachability、root-attached mass tracing。
- M3+ 已经补入 grammar primitive trace graph，但它仍是生成脚本级 trace，不是 frozen Trellis2 sparse-latent runtime graph。
- 不能由本结果声明 global topology repair、watertight/manifold、self-intersection-free、物理生长真实性或类别级鲁棒性。
- 若要进一步加强主文口径，需要把 M3+ trace graph 扩展到真实 sparse-latent handle/frontier sidecar，并在多 seed 上复算。
