# Recursive 3D Generative Growth / Trellis2 项目交接文档

更新时间：2026-05-10 13:25 CST  
当前状态：按用户要求暂停新增工作，只写交接；远端已有 V22 批次仍在运行中，未手动停止。

## 0. 一句话交接

这个项目已经从“能否调用 Trellis2”推进到“严格一对一复现传统递归/生成模式，并用 Trellis2 输出 textured GLB/PBR mesh”的阶段。当前最重要的结论是：

- 传统 loose semantic 对比已经被用户否定；后续必须做严格同类别、同递归模式、同复杂度/深度的 one-to-one 对比。
- DLA / coral / crystal 的连通性问题基本可通过 connected implicit / scaffold 输入解决，多个批次已达到 surface voxel connectivity `components_r0/r1/r2=1, LCR=1.0`，但自然珊瑚/晶体语义和细节仍不稳定。
- 植物 / 根系 / 树冠是当前最弱主线：V17/V19 视觉不够，V22 正在远端跑 smooth botanical 新方案，需下一位 agent 首先接手检查。
- Masked local naturalization ablation 是目前最扎实的正结果之一：三类任务都支持 per-depth masked naturalization，兼具视觉和指标证据。
- V21 IFS / transform / radial / lattice 给出了一些可用的 transform/equivariance 证据和 pyrite/radial 候选，但 branch-tree 仍失败。

## 1. 当前用户要求

用户最新纠正的方向如下，下一位 agent 应优先遵守：

1. 生成视觉对比 case 不能只做本地筛选或本地后处理，必须在新 `a100-2` 上修改算法并生成新 case。
2. GPU 4/5/6/7 都可以用，尽量不要让显卡空闲。
3. 不满意就改生成方案继续跑，目标是视觉效果、连通性、PBR/textured mesh 和指标都达到论文级。
4. 所有最终可视化必须基于 mesh，最好是 Trellis2 textured GLB/PBR；matplotlib/点云图不能作为最终结果。
5. 传统 baseline 对比必须严格一对一：例如 L-system 生成树冠，我们也要按同类递归/生长模式生成类似树冠；DLA 生成晶体，我们也要生成类似晶体；IFS 的递归模式也要对应。
6. zoom-in 必须是真正相机 zoom-in 或高分辨率区域重渲染，正方形，摆正，白底，框选细节区域，不能只裁剪低分辨率图。
7. 当前任务已暂停用于交接；下一位 agent 继续前先读本交接文档和下方读文档顺序。

## 2. 环境与硬约束

本地项目目录：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`

AgentDoc 项目目录：

- `/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth`

远端机器：

- SSH alias：`a100-2`
- 项目根目录：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
- 只能使用 GPU 4/5/6/7，除非用户显式改变。
- 当前用户放宽后的远端总存储上限：100GB。
- 禁止使用远端 `/tmp` 或 `/dev/shm`；`TMPDIR/TORCH_HOME/HF_HOME/TRITON_CACHE_DIR` 等缓存必须在项目目录下。
- SSH shell 上限最近按用户要求在 3 或 4 之间浮动；交接时请保守按最多 3 个常驻 SSH shell。

远端最后一次状态检查（2026-05-10 13:23 CST）：

- 远端目录占用约 `78G`，低于 100GB。
- GPU 4/5/6/7 正在跑 V22，显存约 3.4-4.3GB，V22 已生成 `4/8` 个 `summary.json`。
- V21 seed `20293700` 已完成 `7/7`，但还没有拉回本地做指标/渲染。

## 3. 必读文档顺序

下一位 agent 不要从头扫全部文档，按下面顺序读即可。

### 3.1 当前主计划和进度日志

1. `/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_eval_naturalization_plan_20260510.md`
   - 当前最重要的 Ralph 计划和进度日志。
   - 包含 V1-V22 的运行进展、用户纠正、当前未完成项。

2. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/agentdoc_mirror/plans/recursive_3d_generative_growth_eval_naturalization_plan_20260510.md`
   - 本地 mirror，用于上下文压缩后快速恢复；内容应与 AgentDoc 计划同步。

### 3.2 严格一对一评估与 baseline

3. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_one_to_one_remote_generation_evaluation_protocol_zh_20260510.md`
   - 定义“严格 one-to-one”最终口径。
   - 明确 loose semantic 对比只作为 screening，不可作为主论文最终比较。

4. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_one_to_one_matching_gap_table_zh_20260510.md`
   - 记录目前每类传统方法与我们 case 的 gap。

5. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/baseline_one_to_one_metrics_status_zh_20260510.md`
   - 早期 one-to-one 指标结果。
   - 注意：这里有重要修正，传统 baseline 在 surface sampling 下多数并非天然破碎；论文不能声称传统方法本身一定碎。

6. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_matched_evaluation_protocol_for_paper_zh_20260510.md`
   - 论文评估协议草案。

### 3.3 方法论 / grammar / 理论框架

7. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/method/ps_rslg_formal_framework_deep_zh_20260509.md`
   - 目前最完整的 PS-RSLG 方法论框架。

8. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/method/formal_sparse_latent_grammar_v2_zh_20260509.md`
   - 形式化 grammar 支持 IFS / L-system / space colonization / DLA 等传统 family 的主要文档。

9. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/method/connectivity_invariant_ps_rslg_zh_20260509.md`
   - 连通性 invariant 的理论与实验动机。

10. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/method/ps_slg_connectivity_cache_extension_zh_20260509.md`
   - cache / connectivity 扩展方向。

### 3.4 自然化、连通性、DLA / coral / crystal

11. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/masked_naturalization_ablation_results_plan_zh_20260510.md`
   - 当前 masked local naturalization 的关键正结果。

12. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_visual_matched_v13_smooth_coral_crystal_plan_zh_20260510.md`
13. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_visual_matched_v14_branching_coral_plan_zh_20260510.md`
14. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_visual_matched_v16_natural_coral_plan_zh_20260510.md`
15. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_visual_matched_v18_connectivity_naturalization_plan_zh_20260510.md`
16. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_visual_matched_V20_paper_coral_crystal_zh_20260510.md`
   - DLA/frontier/coral/crystal 从 V13 到 V20 的主要实验线。
   - 重点结论：连通性可解决，语义/自然度仍需继续优化。

### 3.5 植物 / 根系 / 树冠

17. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_visual_matched_v17_root_source_plan_zh_20260510.md`
18. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_visual_matched_V19_meshroot_botanical_zh_20260510.md`
19. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_visual_matched_V22_botanical_smooth_zh_20260510.md`
   - 植物线当前最重要。
   - V17 和 V19 均未达到主文质量；V22 是最新远端正在跑的改进方向。

### 3.6 IFS / transform / pyrite / Escher

20. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_visual_matched_V21_ifs_transform_natural_zh_20260510.md`
   - V21 IFS / transform / radial / lattice 实验设计。

21. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/pyrite_depth_textured_showcase_zh_20260509.md`
22. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/bismuth_depth_textured_showcase_zh_20260509.md`
   - 旧版 pyrite/bismuth showcase；可用作视觉参考，但不等价于严格 one-to-one 评估。

### 3.7 论文与图

23. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/paper/current_paper_evidence_chain_audit_zh_20260509.md`
24. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/paper/experiment_section_and_revision_gap_review_zh_20260510_agent.md`
25. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/figures/method_diagram_design_plan_zh_20260510.md`
26. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/standard_pure_white_render_protocol_20260510.md`
27. `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/visuals/matched_camera_zoom_render_protocol_20260510.md`
   - 论文证据链、实验章节 gap、主流程图设计和白底 zoom 渲染规范。

## 4. 当前远端运行状态

### 4.1 V22 正在运行

V22 是最新 botanical smooth 远端生成批次，目标是解决植物/根系/树冠在 V17/V19 中出现的低多边形 token、blocky root stamping、语义不自然等问题。

相关文件：

- 本地生成器：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/strict_visual_matched_cases_V22_botanical_smooth_20260510.py`
- 本地 launcher：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets/launch_strict_visual_matched_texture_V22_botanical_smooth_20260510.sh`
- 本地测试：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/tests/test_strict_visual_matched_cases_V22_botanical_smooth_20260510.py`
- 本地文档：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/strict_visual_matched_V22_botanical_smooth_zh_20260510.md`

V22 worker 已完成并验证：

- `python3 -m pytest -q tests/test_strict_visual_matched_cases_V22_botanical_smooth_20260510.py`
- 结果：`3 passed`
- dry-run：8 cases，min LCR `1.0`，min vertices `6174`，min faces `12972`，min semantic details `166`。

远端启动命令已经执行：

```bash
ssh a100-2 'cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 && RUN=strict_visual_matched_texture_V22_botanical_smooth_20260510 INPUT_NAME=strict_visual_matched_cases_V22_botanical_smooth_20260510 SEED=20260510 bash assets/launch_strict_visual_matched_texture_V22_botanical_smooth_20260510.sh'
```

最后状态：

- 远端结果目录：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/strict_visual_matched_texture_V22_botanical_smooth_20260510`
- 远端输入目录：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/inputs/strict_visual_matched_cases_V22_botanical_smooth_20260510`
- 远端日志目录：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/strict_visual_matched_texture_V22_botanical_smooth_20260510`
- 2026-05-10 13:23 CST：`4/8` summaries 已存在，GPU 4/5/6/7 仍在处理。

下一位 agent 第一件事应轮询：

```bash
ssh a100-2 'cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 && \
echo V22_summaries=$(find results/strict_visual_matched_texture_V22_botanical_smooth_20260510 -maxdepth 2 -name summary.json 2>/dev/null | wc -l) && \
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | sed -n "5,8p" && \
for f in logs/strict_visual_matched_texture_V22_botanical_smooth_20260510/gpu*.log; do echo ==== $(basename "$f"); tail -8 "$f"; done'
```

完成后拉取：

```bash
mkdir -p visuals/strict_visual_matched_texture_V22_botanical_smooth_20260510 \
  results/strict_visual_matched_texture_V22_botanical_smooth_20260510_remote/inputs
rsync -av a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/strict_visual_matched_texture_V22_botanical_smooth_20260510/ \
  visuals/strict_visual_matched_texture_V22_botanical_smooth_20260510/
rsync -av a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/inputs/strict_visual_matched_cases_V22_botanical_smooth_20260510/ \
  results/strict_visual_matched_texture_V22_botanical_smooth_20260510_remote/inputs/
```

### 4.2 V21 seed20293700 已完成但未拉取

V21 seed `20293700` 已在远端完成 `7/7`，未拉回本地。

远端结果：

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_20260510`
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/inputs/strict_visual_matched_cases_V21_ifs_transform_natural_seed20293700_20260510`

建议下一步拉取、跑 metrics 和 white-background zoom render。

## 5. 近期已完成工作摘要

### 5.1 Masked local naturalization ablation

文件：

- `assets/masked_naturalization_ablation_assets_20260510.py`
- `assets/evaluate_masked_naturalization_ablation_20260510.py`
- `tests/test_masked_naturalization_ablation_20260510.py`
- `docs/evaluation/masked_naturalization_ablation_results_plan_zh_20260510.md`

结果：

- 输出目录：`results/masked_naturalization_ablation_20260510`
- 评估：`results/masked_naturalization_ablation_20260510/evaluation_current/metrics.csv`
- contact sheet：`visuals/masked_naturalization_ablation_zoom_20260510/masked_naturalization_ablation_contact_sheet_20260510.png`
- 三个任务都推荐 `per_depth_masked_naturalization`。
- LCR 均为 `1.0`，silhouette IoU vs per-depth projection 大约 `0.904-0.926`。
- 这部分可进入正文或主消融，是当前最稳证据之一。

### 5.2 V19 mesh-root botanical

文件：

- `assets/strict_visual_matched_cases_V19_meshroot_botanical_20260510.py`
- `assets/launch_strict_visual_matched_texture_V19_meshroot_botanical_20260510.sh`
- `docs/evaluation/strict_visual_matched_V19_meshroot_botanical_zh_20260510.md`

结果：

- 远端生成完成并拉取：`visuals/strict_visual_matched_texture_V19_meshroot_botanical_20260510`
- metrics：`results/strict_visual_matched_texture_V19_meshroot_botanical_20260510_remote/surface_metrics_occ64.csv`
- contact sheet：`visuals/strict_visual_matched_texture_V19_meshroot_botanical_zoom_20260510/strict_visual_matched_texture_V19_meshroot_botanical_contact_sheet_20260510.png`

结论：

- 连通性较好：5/6 r0 single，root-fan tiny island LCR `0.9986`，all r1/r2 single。
- 视觉失败：mesh-root stamping 出现明显低多边形 token/block artifacts。
- 只能作为负面诊断：mesh-root stamping alone is not enough。

### 5.3 V20 paper coral/crystal

文件：

- `assets/strict_visual_matched_cases_V20_paper_coral_crystal_20260510.py`
- `assets/launch_strict_visual_matched_texture_V20_paper_coral_crystal_20260510.sh`
- `docs/evaluation/strict_visual_matched_V20_paper_coral_crystal_zh_20260510.md`

主要本地结果目录：

- `visuals/strict_visual_matched_texture_V20_paper_coral_crystal_20260510`
- `visuals/strict_visual_matched_texture_V20_paper_coral_crystal_seed20284900_20260510`
- `visuals/strict_visual_matched_texture_V20_paper_coral_crystal_seed20285700_20260510`
- `visuals/strict_visual_matched_texture_V20_paper_coral_crystal_seed20286500_20260510`
- `visuals/strict_visual_matched_texture_V20_paper_coral_crystal_steps16_seed20287300_20260510`
- `visuals/strict_visual_matched_texture_V20_paper_coral_crystal_steps4_seed20288100_20260510`
- `visuals/strict_visual_matched_texture_V20_paper_coral_crystal_tex4096_seed20288900_20260510`

关键 contact sheets：

- `visuals/strict_visual_matched_texture_V20_paper_coral_crystal_zoom_20260510/strict_visual_matched_texture_V20_paper_coral_crystal_contact_sheet_20260510.png`
- `visuals/strict_visual_matched_texture_V20_paper_coral_crystal_seed20284900_zoom_20260510/strict_visual_matched_texture_V20_paper_coral_crystal_seed20284900_contact_sheet_20260510.png`
- `visuals/strict_visual_matched_texture_V20_paper_coral_crystal_steps16_seed20287300_zoom_20260510/strict_visual_matched_texture_V20_paper_coral_crystal_steps16_seed20287300_contact_sheet_20260510.png`

结论：

- 多个 seed 的 connectivity 完美：max components_r0=1，min LCR=1.0。
- 视觉上连续 textured mesh 有进步，table/frontier 较强。
- 但 bismuth/pyrite 仍太 organic/branch-like；staghorn zoom 低多边形，未达到主图级。
- `STEPS=16` 不提升主观质量，反而更暗、更 organic，可作为负面 schedule ablation。

### 5.4 V21 IFS / transform / radial / lattice

文件：

- `assets/strict_visual_matched_cases_V21_ifs_transform_natural_20260510.py`
- `assets/launch_strict_visual_matched_texture_V21_ifs_transform_natural_20260510.sh`
- `docs/evaluation/strict_visual_matched_V21_ifs_transform_natural_zh_20260510.md`

已完成并审查：

- first seed：`visuals/strict_visual_matched_texture_V21_ifs_transform_natural_20260510`
- tex4096 seed：`visuals/strict_visual_matched_texture_V21_ifs_transform_natural_tex4096_seed20292500_20260510`
- seed20293300：`visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293300_20260510`

seed20293300 已拉取、测 metrics、渲染：

- metrics：`results/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293300_20260510_remote/surface_metrics_occ64.csv`
- contact sheet：`visuals/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293300_zoom_20260510/strict_visual_matched_texture_V21_ifs_transform_natural_seed20293300_contact_sheet_20260510.png`

seed20293300 人眼审查：

- branch-tree 仍失败：Trellis2/texturing 把它变成大枝干/叶团，不适合作树对比。
- pyrite/radial/Escher/positive-negative transform 更有用，但很多局部仍像 rods/scaffolds。
- positive/negative transform pair 可作为 transform compatibility 的实证图，不是最终视觉主图。

远端未拉取：

- seed20293700 已完成 7/7：`strict_visual_matched_texture_V21_ifs_transform_natural_seed20293700_20260510`

### 5.5 V13-V18 DLA/coral/crystal/plant 历史线

重要视觉路径：

- `visuals/strict_visual_matched_texture_v13_smooth_coral_crystal_zoom_20260510/strict_visual_matched_texture_v13_smooth_coral_crystal_contact_sheet_20260510.png`
- `visuals/strict_visual_matched_texture_v13_smooth_coral_crystal_seed20274100_zoom_20260510/strict_visual_matched_texture_v13_smooth_coral_crystal_seed20274100_contact_sheet_20260510.png`
- `visuals/strict_visual_matched_texture_v14_branching_coral_zoom_20260510/strict_visual_matched_texture_v14_branching_coral_contact_sheet_20260510.png`
- `visuals/strict_visual_matched_texture_v16_natural_coral_zoom_20260510/strict_visual_matched_texture_v16_natural_coral_contact_sheet_20260510.png`
- `visuals/strict_visual_matched_texture_v17_plants_roots_zoom_20260510/strict_visual_matched_texture_v17_plants_roots_contact_sheet_20260510.png`
- `visuals/strict_visual_matched_texture_v18_connectivity_naturalization_zoom_20260510/strict_visual_matched_texture_v18_connectivity_naturalization_contact_sheet_20260510.png`

简短结论：

- V13/V14/V16/V18 多次证明 DLA/coral/crystal 的 connectivity 可做到很好。
- 但 natural coral 的语义和细节始终不稳定：容易像 claw / rock-shell / organic sheet / rods。
- V17 植物/root 不够，仍 low-poly/blocky。

## 6. 论文状态

论文目录：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga`

注意：

- 顶层项目目录不是 git repo；`paper_siga/` 是 nested git repo，已和远端 Overleaf 通过 git 连接。
- 之前已经把 algorithm 从 figure/minipage 里改为 ACM-style `algorithm` + `algpseudocode`，并插入 coverage/exemplar task 和严格评估表。
- 之前曾成功 push 到 Overleaf remote master，commit 包括 `5b13ca2`、`5c3de24` 等；下一位 agent 需要在 `paper_siga/` 下确认 git status。

建议下一步：

```bash
cd /Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga
git status --short
git log --oneline -5
```

论文当前最大风险：

- 方法论文字已有较多草稿，但最终实验图与严格 one-to-one case 还没完全闭合。
- 不能把 loose semantic visual comparison 当作主实验。
- 植物和 natural coral 的 final paper-grade visuals 还不足。
- 评估指标有初步框架，但最终表格仍应基于筛选后的严格任务重新跑。

## 7. Case gallery 与用户挑图位置

用户想亲自挑 case。主要 gallery：

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/case_gallery_for_user_20260509`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/case_gallery_for_user_20260510_remote_matched_candidates`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/case_gallery_for_user_20260510_matched_selection`

更建议先看：

1. `case_gallery_for_user_20260510_remote_matched_candidates/`
   - 新远端生成 strict matched candidates。
2. `case_gallery_for_user_20260509/06_baselines_metrics_ablation/`
   - 传统 baseline 和指标/消融相关图。
3. `visuals/strict_visual_matched_texture_V20_paper_coral_crystal_*_zoom_20260510/`
4. `visuals/strict_visual_matched_texture_V21_ifs_transform_natural*_zoom_20260510/`
5. V22 完成后新增：
   - `visuals/strict_visual_matched_texture_V22_botanical_smooth_zoom_20260510/`

## 8. 常用命令

### 8.1 拉取远端 run

```bash
RUN=strict_visual_matched_texture_V22_botanical_smooth_20260510
INPUT=strict_visual_matched_cases_V22_botanical_smooth_20260510
mkdir -p visuals/$RUN results/${RUN}_remote/inputs
rsync -av a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/$RUN/ visuals/$RUN/
rsync -av a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/inputs/$INPUT/ results/${RUN}_remote/inputs/
```

### 8.2 surface voxel connectivity metrics

```bash
RUN=strict_visual_matched_texture_V22_botanical_smooth_20260510
python3 assets/batch_surface_voxel_metrics_20260509.py \
  --root visuals/$RUN \
  --out-prefix results/${RUN}_remote/surface_metrics_occ64 \
  --resolution 64 \
  --sample-count 50000
```

### 8.3 生成 white-background multi-level camera zoom

```bash
RUN=strict_visual_matched_texture_V22_botanical_smooth_20260510
python3 - <<'PY'
import json, re, os
from pathlib import Path
run=os.environ['RUN']
root=Path('/Users/fanta/code/agent/Code/recursive_3d_generative_growth')
glbs=sorted((root/'visuals'/run).rglob('textured.glb'))
out=root/'results'/(run+'_remote')/'render_manifest.json'
out.parent.mkdir(parents=True, exist_ok=True)
cases=[]
for glb in glbs:
    label=re.sub(r'_steps\d+_tex\d+_seed\d+_xformers$', '', glb.parent.name)
    cases.append({'label': label, 'mesh': str(glb), 'material_mode':'preserve','zoom_levels':3})
out.write_text(json.dumps({'cases':cases},indent=2), encoding='utf-8')
print(out, len(cases))
PY

/Applications/Blender.app/Contents/MacOS/Blender -b \
  --python scripts/figures/matched_camera_zoom_render_20260510.py -- \
  --manifest results/${RUN}_remote/render_manifest.json \
  --out-dir visuals/${RUN}_zoom_20260510 \
  --resolution 900 \
  --samples 16 \
  --zoom-levels 3 \
  --camera iso \
  --engine eevee \
  --material-mode preserve

python3 scripts/figures/postprocess_matched_camera_zoom_plan_20260510.py \
  --plan visuals/${RUN}_zoom_20260510/matched_camera_zoom_plan.json \
  --contact visuals/${RUN}_zoom_20260510/${RUN}_contact_sheet_20260510.png
```

### 8.4 同步 AgentDoc plan mirror

```bash
cp /Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_eval_naturalization_plan_20260510.md \
  /Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/agentdoc_mirror/plans/recursive_3d_generative_growth_eval_naturalization_plan_20260510.md

rsync -av /Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth/plans/recursive_3d_generative_growth_eval_naturalization_plan_20260510.md \
  a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/docs/agentdoc_mirror/plans/recursive_3d_generative_growth_eval_naturalization_plan_20260510.md
```

## 9. 当前 open subagent 状态

已暂停并返回：

- `019e1054-6f98-7c72-aed3-4b84b67076a0` Hegel / V23：未改文件，未跑测试；只读了环境和 V20/V21/V22 文件。
- `019e1054-993a-7642-a8b7-c05cc44879b5` Fermat / status matrix：未改文件；只做只读 inventory。

已完成并产生文件：

- `019e1048-422f-7403-b6b4-c50f1a48f676` Boyle / V22：完成 V22 generator/launcher/test/doc，测试通过，未自己启动远端；主线程已启动远端 V22。

环境上下文里还有旧 subagent：

- `019e0fec-a324-7951-a014-35f159df1bba` Pasteur
- `019e0fec-cd2c-7c71-8707-99751739fd80` Zeno
- `019e0ffb-f81f-7e71-aae7-f10edc53607f` Heisenberg
- `019e1048-422f-7403-b6b4-c50f1a48f676` Boyle

下一位 agent 可以优先忽略旧 subagent，除非需要追溯它们的产物。

## 10. 下一步建议

接手后建议按顺序做：

1. 先检查 V22 是否完成；完成后拉回本地，跑 metrics，渲染 white-background zoom contact sheet，肉眼审查。
2. 拉回 V21 seed20293700，跑 metrics 和 render；比较 V21 多 seed 中 pyrite/radial/transform 哪些能进入论文证据。
3. 如果 V22 植物仍失败，继续远端新生成，而不是本地修图：优先 V23 botanical all-family 或单独 V23 plant/root。目标是 smooth connected support + visible recursive silhouette + no token/block artifacts。
4. DLA/coral/crystal 不要再只追连通性；连通性已经能做，下一步要让语义更像 coral/crystal。可尝试更高质量 guide、public root/guide、SDF coral primitives、局部 masked naturalization，而不是 tube/rod 或 block scaffold。
5. 更新 `recursive_3d_generative_growth_eval_naturalization_plan_20260510.md` 的 progress log 并 mirror。
6. 将最终看得上的 case 分类复制/索引进 `case_gallery_for_user_20260510_remote_matched_candidates`，便于用户挑选。
7. 论文方面只在严格 one-to-one case 稳定后再替换主图和主表；在此之前不要把 screening 图当最终证据。

## 11. 风险与不要做的事

- 不要把“我们生成了类似感觉的东西”当 one-to-one 对比；用户明确要求同类别/同递归模式。
- 不要声称传统方法天然破碎；surface sampling 后传统 baseline 通常也连通。
- 不要用 matplotlib、点云或低质量 proxy 图作为最终论文视觉。
- 不要只做本地后处理来掩盖失败；用户要远端算法生成新 case。
- 不要过度纠结头图；当前最优先是严格对比 case、连通性、视觉质量、指标。
- 不要让 GPU 4/5/6/7 长时间空闲，除非用户像本次一样要求暂停。

## 12. 本次暂停点

本次交接时我没有继续开新任务，只完成了：

- 记录 V22 远端运行状态。
- 中断两个刚开的支线 subagent，确认它们没有改文件。
- 写本交接文档。

未完成但正在等待接手：

- V22 remote batch 完成后的 pull / metrics / render / audit。
- V21 seed20293700 的 pull / metrics / render / audit。
- AgentDoc plan 的最新 V22 启动和暂停状态回写。
- 若 V22 视觉仍失败，继续设计并远端运行下一代 plant/root/tree generator。
