# Recursive 3D Generative Growth 项目交接文档

日期：2026-05-10  
用途：交接给下一位 agent 的唯一入口文档。已有文档不重复改写，只给出读取顺序、项目背景、远端约束、当前用户要求、已完成工作、未完成任务和关键风险。

## 0. 一句话总览

本项目目标是把 Trellis2 这类 sparse 3D generator 纳入一个可发表 SIGGRAPH Asia 级别的 recursive / grammar-based 3D asset generation 框架。当前论文主故事暂定为 **Projection-Stabilized Recursive Sparse-Latent Grammar / PS-RSLG**：grammar 负责拓扑和递归状态，Trellis2 sparse latent / texture path 负责局部生成、re-encoding、texture/PBR export。现在最重要的实验证据是：ordinary 3D generation、trivial latent-copy、mesh-space generated-root copy 都不能稳定替代 grammar-owned recursive state；但 naturalization、non-tree DLA/crystal connectedness、effective resolution、Hunyuan baseline 仍未闭合。

## 1. 工作区与远端约束

本地主要项目目录：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`

AgentDoc 项目目录：

- `/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth`

当前论文目录：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga`

远端机器：

- SSH alias：`a100-2`
- 远端项目根目录：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
- 只能使用新 A100 后四张卡：GPU `4/5/6/7`
- 当前用户最近要求曾限制最多 3 个 SSH shell；旧轮次放宽过 4 个，但下一任应按最新任务重新确认，默认保守用 3 个。
- 不要使用远端 `/tmp` 或 `/dev/shm`；所有 cache 放在远端项目目录下。
- 当前远端项目大小约 `74G`，上限最近曾放宽到 `100G`，但仍要谨慎。
- 当前已删除 20 分钟 heartbeat automation；下一任如果继续 Ralph loop，需要重新创建。

远端当前状态（本轮结束时）：

- GPU `4/5/6/7` 空闲。
- 没有本轮必须继续运行的 Trellis2 / metrics 任务。
- 一个队列式 `strict_visual_matched_texture_v4_seed20260512_20260510` launcher 在收尾时被停止，以满足用户“这一轮跑完后暂停”的要求；已完成的 v4 GLB 保留，未完成项下轮再决定。
- 已清理可重建缓存：`cache/triton/*`、`cache/tmp/*`，未删结果、权重、GLB、OBJ、CSV。

## 2. 用户当前总要求和交接时任务状态

用户最新明确要求是：本轮子任务完成后暂停，并按计划文档总结完成内容、未完成内容、正面/负面结果，尤其方法论推进点；同时清理历史不用存储。本轮已执行到暂停点。

在暂停前用户的长期目标仍是：

- 目标为 SIGGRAPH Asia 发表级别。
- 所有可视化必须基于 mesh，最好 textured mesh；matplotlib 点云图不能作为论文图。
- 白底渲染标准：纯白背景，无平台/地面，阴影很轻或无；组合图里不要放方法文字，只保留 Times New Roman 子图编号。
- 优先级：视觉效果、baseline、metric、可视化、方法论主体结构。
- 关键研究线：
  - 完整 grammar/system 框架，覆盖 IFS / L-system / DLA / space colonization / symmetry 等传统方法 domain；
  - ordinary 3D generator baseline；
  - latent-space vs mesh-space 正式对比；
  - same-root ablation matrix；
  - naturalization ablation；
  - connectivity-first non-tree DLA/crystal；
  - recursive zoom/effective resolution；
  - paper structure cleanup and appendix separation。

## 3. 下一位 agent 的推荐读取顺序

### 第 1 步：先读这份交接和最新收尾报告

1. 本文档：
   - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/agent_handoff_2026-05-10.md`
   - 作用：唯一入口，总览项目、约束、状态和下一步。

2. 最新中文收尾报告：
   - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/obsidian_human_reports/2026-05-10_gen3d_ablation_round_closeout.md`
   - 作用：本轮具体完成内容、负面结果、远端清理、下一轮优先级。

3. AgentDoc 最新 plan：
   - `/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_gen3d_baseline_ablation_plan_20260510.md`
   - 作用：本轮 Ralph loop 计划和逐时进度，是上下文压缩后恢复任务的主要文件。

4. 本地 mirror：
   - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/agentdoc_mirror/plans/recursive_3d_generative_growth_gen3d_baseline_ablation_plan_20260510.md`
   - 作用：AgentDoc plan 的本地镜像。若 AgentDoc 和 mirror 不一致，以 AgentDoc 为准，然后重新同步。

### 第 2 步：理解论文当前状态

5. 当前论文主文件：
   - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.tex`
   - 作用：当前论文草稿，已包含 gen3D baseline、ablation status、appendix、TODO 宏等。

6. 当前 PDF：
   - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.pdf`
   - 作用：当前可编译工作稿，39 页；不是投稿版，appendix 很长。

7. 论文结构审查：
   - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/paper/experiment_section_and_revision_gap_review_zh_20260510_agent.md`
   - 作用：逐项检查用户 2026-05-10 要求，包括 gen3D baseline、latent-vs-mesh、effective resolution、ablation、4.7/4.9/4.10、appendix、纯白图、hero。

8. Gen3D 与 ablation 证据审查：
   - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/gen3d_and_ablation_evidence_audit_zh_20260510_agent.md`
   - 作用：列出 Trellis2 one-shot / latent-copy / mesh-space / ours 的数值证据，明确 Hunyuan 只是 planned/blocked，列出 claim gate。

9. LaTeX 清理状态：
   - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/paper/latex_cleanup_status_zh_20260510.md`
   - 作用：了解当前 LaTeX 编译、warning 和待清理点。

### 第 3 步：看视觉结果和 case 选择

10. Case 选择目录：
    - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/case_selection_by_type_20260510/`
    - 作用：用户最可能先挑图的目录。共 67 个有效 symlink，已按类型分类。

11. Case 选择中文索引：
    - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/case_selection_by_type_zh_20260510.md`
    - 作用：说明每类图、质量判断、主文/附录/丢弃建议。

12. 纯白渲染规范：
    - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/standard_pure_white_render_protocol_20260510.md`
    - 作用：后续所有论文图和挑图应遵守的白底渲染协议。

13. Hero zoom 状态：
    - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/hero_multi_zoom_status_zh_20260510.md`
    - 作用：当前 hero multi-zoom 图的状态和缺陷。

### 第 4 步：理解 baseline 和 metric

14. Gen3D baseline protocol：
    - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/gen3d_baseline_protocol_zh_20260510.md`
    - 作用：ordinary 3D generation baseline 的设计。

15. Hunyuan3D feasibility：
    - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/hunyuan3d_baseline_feasibility_zh_20260510.md`
    - 作用：说明 Hunyuan 为什么当前不能写成已完成 baseline。

16. Mesh-space baseline protocol：
    - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/mesh_space_baseline_protocol_zh_20260510.md`
    - 作用：mesh-space generated-root / direct merge baseline 的设计。

17. Ablation metric protocol：
    - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/ablation_metric_protocol_zh_20260510.md`
    - 作用：connectivity、LCR、face components、surface voxel 等指标解释。

18. Evidence matrix：
    - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/evidence_matrix_for_revision_zh_20260510.md`
    - 作用：论文修订中每个 claim 对应什么证据。

### 第 5 步：理解方法论主线

19. 用户要求到 PS-RSLG 的方法映射：
    - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/method/revision_requirements_to_ps_rslg_plan_zh_20260510.md`
    - 作用：把用户对 grammar/system 的要求映射到论文方法框架。

20. 方法图设计计划：
    - `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/figures/method_diagram_design_plan_zh_20260510.md`
    - 作用：后续主方法图怎么画。

21. 原始 proposal：
    - `/Users/fanta/Downloads/recursive_3d_generative_growth_proposal.md`
    - 作用：最初任务设想和研究愿景。当前方向已收束，不要机械照搬，但需要理解背景。

22. 用户 reviewer / revision 要求：
    - `/Users/fanta/Downloads/agent_revision_and_experiment_requirements.md`
    - 作用：论文修改和实验补强清单。注意其中 projection 减少人工的要求与用户后来“必要处理可以合理保留”的指令有冲突，需基于实验谨慎操作。
    - `/Users/fanta/Downloads/论文修改意见与reviewer批评整理.md`
    - 作用：论文批评和修改意见，后续写 intro/related/method/experiments 时参考。

## 4. 当前已完成的主要工作

### 4.1 Trellis2 基础与 texture/PBR

已确认 Trellis2 基本可用，并能走 textured GLB export。当前所有可用视觉证据已经尽量转向 mesh/textured mesh，避免点云图。纹理质量目前被用户认为“可以接受，大致可以用了”。

重要脚本：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/trellis2_texturing_export_glb.py`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/scripts/figures/matched_camera_zoom_render_20260510.py`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/flatten_png_to_white.py`

### 4.2 Gen3D baseline / latent-vs-mesh negative controls

已完成 Trellis2 one-shot、Trellis2 trivial latent-copy、mesh-space generated-root baseline 的核心证据：

- Trellis2 one-shot：vine / pyrite / coral。
- Trellis2 latent-copy：vine / pyrite / coral。
- mesh-space generated-root：vine / pyrite；coral 缺。
- ours / PS-RSLG：pyrite / coral strict rows强；vine strict row弱，表中用 stronger vine stage5 candidate 防止过度声明。

关键表和数据：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/gen3d_baseline_metrics_20260510/gen3d_baseline_summary_table_20260510.csv`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/gen3d_baseline_summary_table_20260510.tex`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/gen3d_baseline_texture_fair_clean_20260510.png`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/gen3d_baseline_geometry_control_clean_20260510.png`

严谨 claim：

- 可以写：普通 one-shot 和 naive latent/mesh recursion 不能稳定保持递归附着结构。
- 不能写：所有 3D generator 都失败；Hunyuan 已失败；TRELLIS 非 2 已比较。

### 4.3 Same-root / naturalization ablation

已完成第一轮 gap-fill，但不是完整闭合：

- Same-root projection matrix 仍 partial。
- Naturalization/projection matrix 已有 rule-only/no-N/weak-blend/masked local-N partial rows。
- 全目录 metrics 运行过慢，已停止，后续要写 selected-final-only metrics。

关键脚本和输出：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/naturalization_projection_ablation_aggregation_20260510.py`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/drafts/ablation_status_tables_20260510.tex`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/gapfill_texturing_selected_20260510/`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/gapfill_non_tree_texturing_selected_20260510/`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/gapfill_naturalization_textured_overview_raw_clean_20260510.png`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures/gapfill_non_tree_naturalization_textured_overview_raw_clean_20260510.png`

严谨 claim：

- 可以写：这些 same-root rows 都能进入 Trellis2 texture path。
- 不能写：masked naturalization 已经成功修复拓扑或提升所有 case。
- 当前观察：L-system local-N 会明显改变 crown/support，non-tree frontier 仍碎。

### 4.4 可视化整理

已创建：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/case_selection_by_type_20260510/`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/case_selection_by_type_zh_20260510.md`

此目录供用户人工挑 case。下一任 agent 不要随意覆盖，除非用户要求重新整理。

### 4.5 论文状态

当前 PDF：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/main.pdf`
- 可编译，39 页。

编译命令：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga
export PATH=/Users/fanta/Library/TinyTeX/bin/universal-darwin:$PATH
latexmk -pdf -g -interaction=nonstopmode -halt-on-error main.tex > compile_gen3d_ablation_20260510.log 2>&1
```

已知 warning：

- ACM alt text warnings；
- ACM keywords / CCS / reference format warnings；
- appendix 大图 float warnings。

没有 undefined reference/citation 阻塞。

## 5. 当前未完成和最重要风险

### P0：DLA / crystal / non-tree 碎片问题

用户明确说 DLA、履带车、铋晶体、树叶/根系碎块完全不能接受。当前虽有 connected scaffold 和 texture/PBR，但许多 non-tree frontier 仍碎。下一轮如果继续实验，应优先做 connectivity-first，不要堆更多碎片 case。

可尝试方向：

- selected-final-only metrics 找出真正连通的 candidate；
- projection/cache/LOD/transform cache；
- mesh repair 只在改善视觉和拓扑时使用；
- 更连续的 root mesh / implicit scaffold；
- 先选几类能做通的正例，不要无限扩展意义不明 case。

### P0：Naturalization matrix 未闭合

现在只是 partial gap-fill。需要：

- selected-final-only metric script；
- fixed same-root rows；
- before/after components、LCR、root reachability；
- 统一白底图。

### P0：Coral mesh-space generated-root baseline 缺失

Gen3D baseline 的 mesh-space generated-root 当前只有 vine / pyrite，coral 缺。若用户继续要求完整矩阵，这是最小应补项。

### P1：Hunyuan3D baseline

当前只能 planned/blocked。若要跑：

- 需要安装 Hunyuan3D 2.0 repo/package/weights；
- 预计 shape-only 8-12GB，shape+texture 15-25GB，完整 repo/cache 更大；
- 需要确认环境、CUDA extension、许可证和访问权限；
- 不要把未跑模型写成比较结果。

### P1：Effective-resolution / zoom retention

当前只有 proxy 和诊断图。需要：

- one-shot vs recursive refinement；
- 两级以上 zoom；
- local feature scale；
- terminal detail count；
- zoom retention；
- face/GLB size；
- 假设全局高分辨率膨胀的估算。

### P1：论文结构

用户多次要求：

- 4.7 重写；
- 4.9 / 4.10 合并；
- 大部分 status/gap/diagnostic 放 appendix 或 supplemental；
- 正文只留闭合 claim；
- abstract / intro / contributions / related work 与当前方法框架一致。

当前还没有完成最终论文级压缩。

## 6. 下一轮建议行动顺序

如果下一任 agent 要继续推进，而不是只回答问题，建议顺序如下：

1. 先向用户确认是否已经从 `case_selection_by_type_20260510` 挑图；如果没有，可先等用户挑图或主动给 top-10 建议。
2. 写 selected-final-only metrics 脚本，替代全目录递归扫描。
3. 补 coral mesh-space generated-root baseline，完成 gen3D 三类 mesh-space 矩阵。
4. 对 DLA/crystal 做 connectivity-first repair/cache/projection 小矩阵，不要大规模无目标生成。
5. 根据已闭合证据压缩 `main.tex`，把 status/gap 移到 appendix。
6. 如果用户明确要求，恢复 heartbeat / Ralph loop；否则不要自动开新的过夜任务。

## 7. 重要命令备忘

检查远端 GPU：

```bash
ssh a100-2 'nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | sed -n "5,8p"'
```

检查远端项目大小：

```bash
ssh a100-2 'du -sh /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507'
```

检查是否有遗留任务：

```bash
ssh a100-2 'pgrep -af "trellis2_texturing_export_glb|recursive_growth_mesh_metrics|launch_strict_visual_matched_texture_v4" || true'
```

同步 AgentDoc plan 到远端 mirror：

```bash
rsync -av /Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_gen3d_baseline_ablation_plan_20260510.md \
  a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/docs/agentdoc_mirror/plans/
```

编译论文：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga
export PATH=/Users/fanta/Library/TinyTeX/bin/universal-darwin:$PATH
latexmk -pdf -g -interaction=nonstopmode -halt-on-error main.tex > compile_gen3d_ablation_20260510.log 2>&1
```

## 8. 不要误写的结论

下一任 agent 尤其要避免以下 overclaim：

- 不要写 Hunyuan3D 已完成或被我们 outperform。
- 不要写 naturalization 已经成功闭合 ablation。
- 不要写 DLA/crystal 线已经解决碎片问题。
- 不要把 texture/PBR 写成核心算法贡献；它主要是 Trellis2 export compatibility。
- 不要把 occupancy LCR 写成 watertight/manifold/physical correctness。
- 不要把 strict weak vine row 写成正例；需要用 stronger vine stage5 candidate 或重新跑。
- 不要把 appendix/status table 当 completed ablation result。

## 9. 当前交接结论

本轮实际交付是一个“可暂停、可恢复”的状态：

- 论文可编译；
- case 已分类；
- gen3D baseline 初步成形；
- ablation coverage 有 partial gap-fill；
- 远端 GPU 空闲；
- 远端存储低于 100GB；
- 主要风险和下一步已经写清。

下一任 agent 应优先补闭合性，而不是继续堆更多视觉上不可用的碎片 case。
