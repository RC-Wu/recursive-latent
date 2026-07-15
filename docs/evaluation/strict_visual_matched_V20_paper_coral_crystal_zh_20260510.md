# V20 Paper Coral/Crystal 严格匹配生成方案

本文档对应新增文件：

`assets/strict_visual_matched_cases_V20_paper_coral_crystal_20260510.py`

V20 的目标是取代 V18 作为下一轮论文图候选输入。V18 已经把 r0/r1/r2 连通性做到很稳，但人工视觉审查仍指出：若只看远程 textured/PBR 结果，部分 case 仍容易读成“带纹理的有机枝条/薄片”，而不是明确的 coral/crystal。V20 不改变严格一对一比较原则，而是在输入几何阶段提高语义可读性。

## 为什么取代 V18

- V18 优点：rooted attachment bridges、loop closure bridges、connected implicit support 已经能把 DLA/frontier/crystal 初始 mesh 保持为单一连通分量。
- V18 不足：coral 语义主要靠 pore/ridge/polyps 的泛化自然化，局部仍可能像枝条或片状有机结构；crystal 语义主要靠 facet/orbit/step，平面晶面和阶梯轮廓不够强。
- V20 改进：coral 增加重复 calyx/polyp 小杯、圆润多孔 reef surface、平滑锥形枝端，并显式禁止 flat rod cuts；crystal 增加 pyrite cubic facet plates、bismuth stepped terraces、 sharper planar facets，并显式禁止 smooth crystal blobs。

## 严格 DLA/frontier/crystal 映射

V20 每个 case 仍保留 `traditional_target`，用于和传统 baseline 做严格一对一对照：

| case | traditional_target | 语义目标 | GPU |
|---|---|---|---:|
| `V20_dla_staghorn_calyx_coral_a` | `dla_staghorn_coral_900` | staghorn coral | 4 |
| `V20_dla_staghorn_calyx_coral_b` | `dla_staghorn_coral_900` | staghorn coral robustness | 5 |
| `V20_dla_table_coral_reef_plate` | `dla_table_coral_plate_760` | table coral / reef plate | 6 |
| `V20_dla_branching_reef_loop_closure` | `dla_branching_reef_loop_650` | branching reef with loop closure | 7 |
| `V20_dla_frontier_lace_sheet_a` | `dla_frontier_sheet_700` | frontier lace sheet | 4 |
| `V20_dla_frontier_lace_sheet_b` | `dla_frontier_sheet_700` | frontier sheet backup | 5 |
| `V20_dla_pyrite_cubic_crystal` | `dla_pyrite_cubic_crystal_520` | pyrite cubic crystal | 6 |
| `V20_dla_bismuth_stepped_crystal` | `dla_bismuth_step_crystal_360` | bismuth stepped crystal | 7 |

这些 case 仍使用 stochastic active frontier、occupancy exclusion、attachment bridges 与 loop closure bridges。也就是说，V20 是在同一个 DLA/frontier/crystal 任务上增强视觉语义，而不是换成别的生成任务。

## mesh/PBR 与远程约束

- 本地 dry-run 只生成 OBJ 输入、guide PNG、manifest 与初始 mesh 指标。
- 最终 textured mesh/PBR 必须在 `a100-2` 上重新生成，GPU 限定为 `4/5/6/7`。
- launcher 使用 project-local cache：`$ROOT/cache/tmp`、`$ROOT/cache/torch`、`$ROOT/cache/triton/...`，不使用 `/tmp` 或 `/dev/shm`。
- metadata 固定 `generate_new_on_a100_2_no_local_selection_or_postprocessing`，禁止本地挑选、后处理修复、2D-only 结果替代。

## 论文图预期

V20 应优先用于论文图候选，因为它同时满足：

- 连通：初始 mesh enforce single connected component，记录 `largest_component_vertex_ratio >= 0.999`。
- 一对一：每个 recursive case 明确映射到一个 traditional baseline target。
- 语义：coral 有 staghorn/table/frontier reef 的 calyx、polyp、pore、rounded reef surface；crystal 有 pyrite cubic facets 和 bismuth stepped terraces。
- 输出：远程只接受 mesh/PBR textured GLB 路径，符合论文 figure 与补充材料资产要求。
