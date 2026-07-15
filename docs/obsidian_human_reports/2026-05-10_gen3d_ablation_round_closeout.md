# 2026-05-10 Gen3D Baseline / Ablation / 可视化收尾报告

时间：2026-05-10 08:20 CST  
状态：本轮子任务已暂停推进，等待用户挑 case 和下一轮决策。  
远端约束：`a100-2`，只用 GPU 4/5/6/7，最多 3 个 SSH shell；所有远端产物仍在 `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`。

## 1. 你最需要先看的文件

- Case 挑选目录：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/case_selection_by_type_20260510/`
  - 共 67 个有效 symlink，按类型分好：植物/根/树、晶体/珊瑚/DLA、科幻机械、gen3D baseline、depth ablation、hero zoom、需修复或丢弃。
- Case 中文索引：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/case_selection_by_type_zh_20260510.md`
- 当前 PDF：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.pdf`
  - 已重新编译成功，当前 39 页工作稿；仍有 ACM alt text / keyword / CCS warning 和 appendix 大浮动 warning。
- Gen3D 与 ablation 证据审查：
  - `docs/evaluation/gen3d_and_ablation_evidence_audit_zh_20260510_agent.md`
  - `docs/paper/experiment_section_and_revision_gap_review_zh_20260510_agent.md`

## 2. Gen3D baseline 与 latent/mesh-space 对比

已完成：

- Trellis2 one-shot image-conditioned baseline：vine / pyrite / coral 三类都有结果。
- Trellis2 trivial latent-copy baseline：vine / pyrite / coral 三类都有 `copy_shift_upper_z` 负控。
- Mesh-space generated-root baseline：vine / pyrite 两类完成；coral mesh-space generated-root 仍缺。
- Ours / PS-RSLG：pyrite、coral strict rows 连通性强；vine strict row 弱，因此论文表里同时保留 stronger vine stage5 candidate，避免过度解读。
- 论文表已修正：`paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex`
  - 修正了 mesh-space GLB 大小，之前 13.0/21.6 MB 不对，现在按 CSV/实际文件为 4.7/8.8 MB。

关键结论：

- Trellis2 one-shot 在 vine 上可生成可用单体，但 pyrite/coral 不能稳定表达递归附着结构。
- trivial latent-copy 和 mesh-space generated-root copy 都是强负控：它们能复制几何，但复制出来的局部不是下一层 grammar 可读取的 attached recursive state。
- Hunyuan3D 2.0 当前只能写 feasibility / planned baseline，不能写已比较。原因是远端没有 repo、`hy3dgen` 包或缓存权重；安装和权重预算较大，当前未进入数值比较。

新增/更新图：

- `paper_siga/figures/gen3d_baseline_texture_fair_clean_20260510.png`
- `paper_siga/figures/gen3d_baseline_geometry_control_clean_20260510.png`
- `paper_siga/figures/gen3d_baseline_texture_fair_zoom_clean_20260510.png`

注意：zoom 图仍有裁切/白洞问题，适合诊断或附录，不建议作为强主文图。

## 3. Ablation matrix 与 naturalization gap-fill

已完成：

- Same-root projection matrix 仍是 partial status，不是完整闭合实验：
  - traditional 30/8，direct 8/8，final-only 4/12，prune 5/11，bridge 1/15，proposed 15/10。
- Naturalization/projection matrix 已补第一轮 gap-fill：
  - rule-only：4 available / 22 missing
  - no-N：8 available / 18 missing
  - weak blend：8 available / 18 missing
  - masked local-N：22 available / 13 missing
  - global-N：12 available / 22 missing
  - with projection：35 available / 17 missing
  - without projection：4 available / 22 missing
- 聚合脚本已更新：`assets/naturalization_projection_ablation_aggregation_20260510.py`
- 表格已更新：`paper_siga/drafts/ablation_status_tables_20260510.tex`

新增 Trellis2 textured GLB 视觉证据：

- L-system same-root 四列：
  - rule-only
  - no-N / alpha 0
  - weak blend / alpha 0.25
  - masked local-N / alpha 1.0
- Non-tree 四列：
  - coral weak / coral local-N
  - pyrite weak / pyrite local-N

对应本地 GLB：

- `results/gapfill_texturing_selected_20260510/`
- `results/gapfill_non_tree_texturing_selected_20260510/`

对应纯白渲染：

- `paper_siga/figures/gapfill_naturalization_textured_overview_raw_clean_20260510.png`
- `paper_siga/figures/gapfill_naturalization_textured_zoom_01_clean_20260510.png`
- `paper_siga/figures/gapfill_non_tree_naturalization_textured_overview_raw_clean_20260510.png`
- `paper_siga/figures/gapfill_non_tree_naturalization_textured_zoom_01_clean_20260510.png`

严谨判断：

- 这些图证明“同根 ablation rows 可以进入 Trellis2 texture path”，但不能证明 naturalization 已经成功。
- L-system local-N 行出现明显 crown/support 形态偏移；non-tree 行仍有大量 frontier 小碎片。
- 因此我把它们放进 appendix/status，不作为主文正向结果。

未完成：

- 全目录 `recursive_growth_mesh_metrics.py` 对 `masked_naturalization_gapfill_20260510` 扫描 20 多分钟仍未产出 CSV，已停止。后续应改成 selected-final-only 指标脚本，只统计每个 row 的最终 mesh，不递归扫全目录。
- naturalization matrix 仍没有完整闭合；不能删除 TODO。

## 4. 论文修改状态

已完成：

- `main.tex` 已加入/更新：
  - Gen3D baseline compact table；
  - Hunyuan3D planned/blocked 的谨慎描述；
  - same-root / naturalization coverage appendix table；
  - L-system 和 non-tree naturalization textured status figures；
  - appendix 分区继续保留，正文 claim 更谨慎。
- `paper_siga/main.pdf` 重新编译成功，当前 39 页。
- `paper_siga/main.log` 当前没有 undefined reference/citation 级别阻塞；仍有 appendix 大图浮动和 ACM metadata warnings。

仍需改：

- 4.7 / 4.9 / 4.10 仍应继续压缩、合并，减少 texture/export 叙事负担。
- Appendix 还太长；正式投稿前应把大部分图移到 supplemental 或 figures-only pages。
- Effective-resolution 仍是 proxy，不能作为摘要或贡献中的强 claim。
- Hunyuan3D 如果要进入主表，需要单独安装和跑；否则保持 planned baseline。

## 5. 可视化与 case 选择

已完成：

- 建立了按类型整理的 case 文件夹：`visuals/case_selection_by_type_20260510/`
- 只纳入 mesh/textured-mesh 渲染，排除了 matplotlib 点云图。
- 子目录统计：
  - `plant_root_tree/`: 12
  - `crystal_coral_dla/`: 11
  - `sci_fi_mechanical/`: 7
  - `gen3d_baselines/`: 12
  - `ablation_depth/`: 13
  - `hero_zoom/`: 5
  - `needs_repair_or_discard/`: 7

我的建议：

- 主文优先考虑 pyrite / coral / vine stage5 / connected scaffold v3b 这类可解释且连通性较强的 case。
- DLA/晶体线必须继续做“连通性优先”的修复或更强 projection/cache 策略；当前 non-tree naturalization 图仍显示大量碎片，不能作为最终正例。
- L-system naturalization 图适合作为附录中的失败-aware ablation，可帮助说明为什么 local-N 不是无条件正向模块。

## 6. 方法论推进状态

正向：

- “ordinary 3D generation vs PS-RSLG” 的故事已经更完整：one-shot、latent-copy、mesh-space generated-root 三种 trivial 方案都能被定义为严谨负控。
- “grammar-owned topology + generator local realization + per-depth projection/re-encoding”的主线仍成立。
- PBR/texture 现在可用，但应作为 compatibility / asset-readiness，不应成为核心算法贡献。

负向/风险：

- system grammar 的理论框架仍需要继续强化，尤其是把 sampler、projection、typed handles、admissible state、classical systems as limits 串成一个统一形式。
- naturalization 还不是稳定贡献；目前更适合写成 claim gate 或 diagnostic。
- non-tree DLA/crystal 的碎片问题仍是最大实验风险，必须继续优先解决。

## 7. 存储与运行状态

- 远端所有 GPU 4/5/6/7 当前空闲。
- 远端项目大小从约 78G 清理到约 74G。
- 清理内容：只删除可重建的 `cache/triton/*` 和 `cache/tmp/*`。
- 未删除：实验结果、权重、GLB、OBJ、CSV、计划文档。
- 收尾检查时发现一个队列式 `strict_visual_matched_texture_v4_seed20260512_20260510` 纹理 launcher 仍在继续启动后续候选；为满足“本轮后暂停”，我停止了该 launcher 和子进程。它已经成功输出的 v4 GLB 保留在远端，未完成的 v4 候选下一轮再决定是否继续。

## 8. 下一轮最小优先级

1. 写 selected-final-only mesh metrics 脚本，替代全目录递归扫描，闭合 naturalization gap-fill 的连通性表。
2. 补 coral mesh-space generated-root baseline，完成 gen3D 三类 row 的矩阵。
3. 继续做 DLA/pyrite 连接性优先的 projection/cache/repair，而不是继续堆无连接的碎片 case。
4. 从 `case_selection_by_type_20260510/` 中人工挑主图候选，然后只对候选做高质量多层 zoom-in。
5. 继续压缩论文实验结构，把 status/gap/diagnostic 移到 supplemental，主文只留闭合 claim。
