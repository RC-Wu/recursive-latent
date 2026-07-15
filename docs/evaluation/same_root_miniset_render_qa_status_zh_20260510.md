# Same-root miniset GLB/render QA status（2026-05-10）

## 范围

- 主目标：`vine_compete_d3` 的 `direct` / `final-only` / `prune` 三列。
- 备选纳入：是，包含 tree_compete_d3 三列。
- 本轮仅验证已有本地 final OBJ，导出本地 GLB，并生成固定白底软件 render QA；未 SSH，未修改 `paper_siga/main.tex`。

## 行状态

| case | variant | status | OBJ | GLB | render QA | components | LCR | blocker |
|---|---|---|---|---|---|---:|---:|---|
| `vine_compete_d3` | `direct` | complete | yes | yes | yes | 2059 | 0.9049 |  |
| `vine_compete_d3` | `final-only` | complete | yes | yes | yes | 2 | 0.9934 |  |
| `vine_compete_d3` | `prune` | complete | yes | yes | yes | 1 | 1 |  |
| `tree_compete_d3` | `direct` | complete | yes | yes | yes | 3201 | 0.9169 |  |
| `tree_compete_d3` | `final-only` | complete | yes | yes | yes | 4 | 0.9842 |  |
| `tree_compete_d3` | `prune` | complete | yes | yes | yes | 2 | 0.9949 |  |

## 输出文件

- metrics: `results/same_root_miniset_render_qa_20260510/metrics/same_root_miniset_render_qa_metrics.csv`
- manifest: `results/same_root_miniset_render_qa_20260510/manifest/same_root_miniset_render_qa_manifest.json`
- GLB: `results/same_root_miniset_render_qa_20260510/glb/`
- renders: `results/same_root_miniset_render_qa_20260510/renders/` 与 `contact_sheets/`

## 可写进主文的保守结论

- 在 matched `vine_compete_d3` depth-3 projection 子集上，三列已有本地 final OBJ，且本轮 GLB import 与固定白底 render QA 均通过。指标支持保守写法：direct recursion 高碎片化（2059 components, LCR=0.9049），final-only 明显降低碎片（2 components, LCR=0.9934），per-depth prune/projection 达到单连通主结果（1 component, LCR=1.0）。
- `tree_compete_d3` 可作为备选或 appendix 支撑同向趋势：direct 为 3201 components/LCR=0.9169，final-only 为 4 components/LCR=0.9842，prune 为 2 components/LCR=0.9949；仍不是完整 six-row same-root matrix。
- 不能写 same-root matrix 已闭合；同一 case 的 `traditional` / `bridge` / `proposed` 仍缺。

## 验证摘要

- complete rows: 6
- blocked rows: 0
- 渲染方式：纯 Python/Pillow 三角面软件投影，白底、无文字标签；不是 Blender/PBR 最终图。
