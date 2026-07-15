# V17 严格视觉匹配植物/根系生成计划

## 目标

V17 只覆盖植物、树冠、藤蔓和根系缺口，保持与传统基线的一对一任务模式：

- `lsys_pine_canopy_d5`：L-system 树/松冠，深度 5。
- `lsys_root_fan_d5`：L-system 根系扇形，深度 5，下向趋性。
- `lsys_climbing_vine_d6`：L-system 爬藤，6 次递归/卷曲调度。
- `sc_tree_crown_260`：space-colonization 树冠吸引子竞争。
- `sc_root_network_260`：space-colonization 根网/藤根吸引子竞争。
- `sc_bush_shell_220`：space-colonization 灌木外壳覆盖。

这不是语义替换，不是本地筛选，也不是从本地结果中挑选好看的样本；本地 dry-run 只生成新的 OBJ 网格输入和 PBR 引导图，最终结果必须在 `a100-2` 的 GPU 4/5/6/7 上重新生成。

## 根/源策略

V15/V6 的主要问题不是连通性，而是视觉上仍像几何杆、卡片或代理网格。V17 的根/源策略改为“参考种子 + 经典递归骨架”：

1. 先用原始经典模式生成骨架：L-system 或 space-colonization，不改变比较对象。
2. 再把高质量参考中的源点分布、主干粗细、根板展开、藤蔓卷曲和树冠末端密度转成程序化规则。
3. 所有细节都与骨架共享顶点连接：融合枝条 sleeve、叶片 lamina、根板、根毛和芽点都不是孤岛。
4. 输出只包含 mesh/PBR 引导，不做本地纹理结果筛选，不做 V6/V15 结果后处理。

参考来源记录如下：

- `visuals/textured_glb_20260508/tree_compete_s3/textured.glb`
- `visuals/textured_glb_20260508/vine_d5_compete_s5_inference/textured.glb`
- `visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb`
- `visuals/programmatic_pbr_renders_20260508/tree_auto_iso.png`
- `visuals/programmatic_pbr_renders_20260508/vine_auto_iso.png`

## 实现约束

- 生成脚本：`assets/strict_visual_matched_cases_v17_plants_roots_20260510.py`。
- 远程启动脚本：`assets/launch_strict_visual_matched_texture_v17_plants_roots_20260510.sh`。
- 远程机器：`a100-2`。
- 允许 GPU：4/5/6/7。
- 缓存、临时文件、Triton cache、Torch cache 都放在项目根目录下，不使用系统临时目录或共享内存目录。
- dry-run 连通性门槛：单一主连通分量，或 largest-component vertex ratio >= 0.999。

## 与传统基线的一对一关系

V17 不把根系换成别的类别，不把 space-colonization 换成手写语义模型，也不把 L-system 换成扩散结果选择。每个 case 的 metadata 都写入：

- `traditional_target`
- `operator_family`
- `same_category`
- `same_recursive_mode`
- `root_selection_log`
- `high_quality_source_references`
- `strict_generation_policy`

因此比较仍然是同一经典递归/生长任务，只是输入源策略从杆状代理升级为高质量、连通、可纹理的植物 mesh/PBR 输入。
