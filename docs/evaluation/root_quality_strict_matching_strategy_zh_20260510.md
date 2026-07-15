# Root quality strict matching strategy（2026-05-10）

## 1. 更新后的 strict matching 规则

本轮 strict one-to-one 比较不再要求 PS-RSLG 使用与传统方法同样贫弱的 root primitive。允许使用更好的 Trellis2 root、生成图像 root、public guide image、已有项目高质量 root 或 public mesh/texture guide，但最终输出必须仍然严格匹配传统任务。

可接受的 strict match 必须同时满足：

1. **任务类别一致**：树冠对树冠、藤蔓对藤蔓、根系对根系、DLA/coral 对 frontier/coral、IFS lattice 对 transform/lattice。不能用“看起来都像植物/晶体”替代具体任务。
2. **粗轮廓和空间布局一致**：传统 target 是 climbing vine，就不能拿 flat root fan 顶替；传统 target 是 radial ornament，就不能拿普通 pyrite lattice 顶替。
3. **递归/生长模式一致**：L-system 对 branching/string rewriting；space colonization 对 attractor/competition；DLA/frontier 对 attachment/frontier/occupancy exclusion；IFS 对 transform-copy/orbit/lattice。
4. **深度与可见复杂度相当**：必须记录 depth、stage、branch/tip/copy budget、density 等控制量；最终图中要能看见与传统任务相当的多尺度结构。
5. **root 质量可独立优化，但要透明记录**：root/source/guide 可以更好，选择过程必须记录 provenance 和 selection budget，防止把人工挑选优势伪装成算法优势。
6. **证据必须是 mesh/PBR render**：主文比较使用纯白背景、upright centered、square overview、真实相机级 zoom 和 source callout。Matplotlib、点云或仅 2D crop 只能做内部诊断。

论文表述建议：

> Classical baselines use their native procedural primitives; PS-RSLG uses the same matched recursive operator family, but each grammar token may be instantiated with a higher-quality root or guide asset. We therefore log root provenance and the root-selection budget for every pair.

## 2. 已核对的证据入口

- 传统 12 个任务靶子：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/strict_matched_task_targets_20260510/manifest.csv`
- 传统任务总览图：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_matched_traditional_targets_zoom_20260510/strict_matched_traditional_targets_contact_20260510.png`
- 高质量 root zoom 总览：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/matched_camera_zoom_existing_roots_20260510/matched_existing_roots_zoom_contact_20260510.png`
- 弱项候选 zoom 总览：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/matched_camera_zoom_weak_search_candidates_20260510/weak_search_candidates_zoom_contact_20260510.png`
- strict pair V2 manifest：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_matched_pair_candidates_v2_20260510/matched_pair_v2_manifest.csv`
- strict pair V2 总览图：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/strict_matched_pair_candidates_v2_20260510/strict_matched_pair_candidates_v2_contact_20260510.png`
- 高质量 root surface metrics：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/matched_high_quality_root_metrics_20260510/surface_metrics_occ64.csv`
- 弱项候选 surface metrics：`/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results/weak_search_candidate_metrics_20260510/surface_metrics_occ64.csv`

## 3. 候选 root / guide asset 清单

| candidate id | exact asset path | 适配的 classical task | 当前判断 |
|---|---|---|---|
| `tree_compete_s3` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/textured_glb_20260508/tree_compete_s3/textured.glb` | `sc_tree_crown_260`；可诊断 `lsys_pine_canopy_d5`、`sc_bush_shell_220` | 当前最好的 tree/crown root。surface r0: 2 comps, LCR 0.993；r2 单连通。主文可用于 SC crown，但 L-system pine 和 bush shell 仍需更贴合轮廓的 root。 |
| `vine_stage5` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/textured_glb_20260508/vine_d5_compete_s5_inference/textured.glb` | `lsys_climbing_vine_d6`、`sc_root_network_260`；可诊断 `lsys_root_fan_d5` | 当前最强 vine/root root。surface r0/r1/r2 全单连通。主文可用于 climbing vine 和 root network；flat root fan 需要另生 root。 |
| `tree_roots_hq` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/public_guide_textured_glb_20260509/tree_compete_d4_pruned_tree_roots_steps8_tex2048_xformers/textured.glb` | root/tree hybrid；可支持 `sc_root_network_260`、`lsys_root_fan_d5` 的替代搜索 | 视觉强但形状偏奇异，当前不优于 `vine_stage5`。适合进入 root pool，不宜直接主文。 |
| `coral_density_0p25_octopus` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/coral_density_extreme_texture_20260509/coral_density_param_density_0p25_octopus_steps8_tex2048_xformers/textured.glb` | `dla_coral_cluster_900` | 当前最好的 DLA/coral 替代候选。surface r0/r1/r2 全单连通；视觉仍有 voxel/bead 感，主文前需要 masked local naturalization 或更好 root。 |
| `coral_dla_octopus` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/connected_scaffold_v2_textured_glb_hq_20260509/volumetric_dla_coral_octopus_hq_steps8_tex2048_xformers/textured.glb` | `dla_coral_cluster_900` 旧候选；DLA/coral boundary | 连通性好，surface r0/r1/r2 全单连通，但更 chunk/bead。作为 diagnostic baseline 保留。 |
| `dla_side_octopus` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/public_guide_textured_glb_20260509e/dla_side_octopus_steps8_tex2048_xformers/textured.glb` | `dla_frontier_sheet_700` | 更接近 side/frontier mode，但 silhouette 还不是 sheet。surface r0: 26 comps, LCR 0.966；r2 单连通。诊断候选。 |
| `pyrite_stage4` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/pyrite_depth_hq_warm_showcase_20260509/stage04_textured.glb` | `ifs_fractal_lattice_d4` | 当前最强 transform/lattice root。surface r0/r1/r2 全单连通。主文可用，但应限定为 ordered lattice/transform family，不要写成 stochastic DLA。 |
| `bismuth_hopper_pyrite_hq` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/connected_scaffold_v2_textured_glb_hq_20260509/bismuth_hopper_pyrite_hq_steps8_tex2048_xformers/textured.glb` | `dla_aniso_crystal_800` 的 ordered-crystal boundary；也可支持 crystal/lattice task | 晶体视觉强，surface r0: 2 comps, LCR 0.9996；r1 单连通。不是随机 DLA，只能作为 ordered crystal boundary 或重新定义后的 crystal task。 |
| `cache_radial_transform_fusion` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/cache_selected_texture_20260509_rerun1516/cache_radial_transform_fusion_steps8_tex2048_xformers/textured.glb` | `ifs_radial_ornament_o8_d4` | 当前最连通的 radial/cache transform 候选，surface r0: 92 comps, LCR 0.998；r1 单连通。视觉像 blocky terrain/crystal，不是干净 ornament。诊断优先。 |
| `transform_radial4_gear` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/public_guide_textured_glb_20260509e/transform_radial4_gear_steps8_tex2048_xformers/textured.glb` | `ifs_radial_ornament_o8_d4`；hard-surface radial ornament | 语义更像 radial gear/ornament，但 metrics 弱：r0 845 comps, LCR 0.628；需 repair/naturalization 后再考虑。 |
| `scifi_gear_hq` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/scifi_module_guide_sweep_20260509/scifi_gear_hq_steps8_tex2048_xformers/textured.glb` | future scifi/mechanical recursive module；也可进入 IFS radial hard-surface root pool | 当前不直接对应 12 个传统任务中的 paper pair，但适合作为 radial/gear/architecture root pool。 |
| `scifi_arch_hq` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/scifi_module_guide_sweep_20260509/scifi_arch_hq_steps8_tex2048_xformers/textured.glb` | future portal/architecture transform task | 非当前主文 strict procedural pair；可作为 shape/scifi architecture coverage 的扩展证据。 |
| `scifi_module_projected_translate_stage03_gear` | `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals/public_guide_textured_glb_20260509/scifi_module_projected_translate_stage03_gear_steps8_tex2048_xformers/textured.glb` | translate/copy mechanical module；future IFS/tiling/architecture task | 可支持 mechanical transform-copy 诊断，但当前不是 12 个传统任务的主文候选。 |

## 4. Pair readiness 分级

| traditional task | current PS-RSLG candidate | 状态 | 处理建议 |
|---|---|---|---|
| `lsys_climbing_vine_d6` | `vine_stage5` | **paper-ready candidate** | 类别、climbing/vine silhouette、递归 tendril 复杂度和连通性都最强。补最终白底 nested zoom 与 root provenance 后可进主文。 |
| `sc_tree_crown_260` | `tree_compete_s3` | **paper-ready candidate** | 当前最强 tree/crown match。caption 需说明传统 baseline 是 tube skeleton，PS-RSLG 是同类 crown task 的高质量 root/PBR 实例。 |
| `sc_root_network_260` | `vine_stage5` | **paper-ready candidate** | root/vine competition 视觉和 connectivity 都强。需记录 attractor/competition 控制量，避免写成 L-system vine。 |
| `ifs_fractal_lattice_d4` | `pyrite_stage4` | **paper-ready candidate** | 适合 ordered transform/lattice claim。不要用于 `dla_aniso_crystal_800` 的 stochastic DLA claim。 |
| `lsys_pine_canopy_d5` | `tree_compete_s3` | diagnostic | 类别近似，但 pine/canopy morphology 与 L-system tube/needle tree 不够严格。需要 pine/conifer-like root 或重新渲染更像 canopy 的 tree root。 |
| `lsys_root_fan_d5` | `vine_stage5` | needs new root generation | root/vine 材质强，但 silhouette 是 hanging/climbing vine，不是 flat fan。应生成 fan-shaped root guide。 |
| `sc_bush_shell_220` | `tree_compete_s3` | needs new root generation | 植物类别相近，但 shell/bush silhouette 不够。应生成 spherical/bushy shell root。 |
| `dla_coral_cluster_900` | `coral_density_0p25_octopus` | diagnostic / near-candidate | 连接性达标，是当前最好 DLA/coral root；视觉 bead/voxel 感仍需 naturalization。主文前必须改善局部表面。 |
| `dla_aniso_crystal_800` | `bismuth_hopper_pyrite_hq` | diagnostic ordered-crystal boundary | 视觉强但模式偏 ordered crystal，不是 stochastic DLA。若主文使用，应改任务名为 ordered crystal/lattice，而不是 DLA。 |
| `dla_frontier_sheet_700` | `dla_side_octopus` | needs new root generation | side/frontier mode 比 coral 更接近，但 sheet silhouette 不成立。需要 sheet-like frontier root。 |
| `ifs_branch_tree_d6` | `ifs_transform_copy_proxy` | diagnostic mode-matched only | 语义最严格，但视觉 proxy-quality，不能主文。需要 transform-copy tree-like high-quality root。 |
| `ifs_radial_ornament_o8_d4` | `cache_radial_transform_fusion` / `transform_radial4_gear` | needs new root generation or repair | 一个连通但不像 ornament，一个像 ornament 但碎。需要 clean radial ornament hard-surface root。 |

## 5. Root provenance / selection budget 记录规范

每一个 strict pair 都应有一条 `root_selection_log` 记录。建议保存为 CSV/JSONL，并在 paper appendix 或 supplement 引用。最低字段如下：

| field | 含义 |
|---|---|
| `pair_id` | 例如 `sc_tree_crown_260__tree_compete_s3` |
| `traditional_task_id` | 传统任务名，与 `strict_matched_task_targets_20260510` manifest 对齐 |
| `traditional_family` | `lsystem` / `space_colonization` / `dla_frontier` / `ifs_transform` |
| `traditional_parameters` | depth、angle、attractor 数、kill radius、stickiness、transform set 等 |
| `psrslg_operator_family` | 对应 PS-RSLG rule family，必须与传统 family 对齐 |
| `root_asset_path` | 最终 root/guide/mesh 的 exact path |
| `root_source_type` | `existing_project_root` / `generated_image_root` / `public_guide_image` / `public_mesh_or_texture` / `proxy_generated_mesh` |
| `root_source_provenance` | 原始脚本、prompt、public source URL、run directory、checkpoint、seed、license/usage note |
| `root_pool_size` | 本任务实际进入筛选的 root 数 |
| `root_generation_budget` | 生成 root 的 GPU jobs、seeds、prompts、guide variants、steps、texture resolution |
| `root_screening_budget` | 被渲染/计量的候选数，使用的 metrics 和人工筛选标准 |
| `selection_rank` | 最终候选在该 pool 中的名次；若人工选择，写清楚 tie-breaker |
| `rejected_candidate_ids` | 主要落选候选及原因，例如 silhouette mismatch、fragmented、bead-like、not mode-matched |
| `projection_naturalization_schedule` | per-depth projection、masked local naturalization、final repair 是否启用 |
| `metric_paths` | surface metrics、mesh metrics、CLIP/DINO 或人工 label 文件路径 |
| `render_paths` | pure-white overview、camera zoom、contact sheet 路径 |
| `readiness_label` | `paper_ready_candidate` / `diagnostic` / `needs_new_root_generation` / `screening_only` |

选择预算的写法必须保守：

- 不写“我们随便挑了最好的”，而写“for this task we screened N roots / M guide variants under the same render and metric protocol”。
- 如果某个 root 是已有项目资产，要把它标成 `existing_project_root`，不要伪装成本轮为该 task 专门生成。
- 如果使用 public guide image，要记录 guide image path、来源、处理脚本和授权/引用状态。
- 如果最终 pair 只从 1 个 root 中选出，不能把它当作大规模 root search 的结果。
- 主文只报告 paper-ready candidate；diagnostic 和 failure 进入 appendix 或 method motivation。

## 6. 下一批实验

1. **锁定四个主文候选的 final evidence**：对 `lsys_climbing_vine_d6 -> vine_stage5`、`sc_tree_crown_260 -> tree_compete_s3`、`sc_root_network_260 -> vine_stage5`、`ifs_fractal_lattice_d4 -> pyrite_stage4` 重新生成最终纯白 square overview、两级 camera zoom、metrics 表和 root_selection_log。
2. **补 L-system pine / root fan / SC bush root pool**：生成或筛选 conifer canopy、flat fan root、spherical bush shell 三类 better roots。每类至少记录 root pool、guide variants、reject reasons，避免继续用 `tree_compete_s3` 或 `vine_stage5` 顶替 silhouette。
3. **DLA/coral naturalization sweep**：以 `coral_density_0p25_octopus` 为当前最佳，比较 `coral_dla_octopus`、不同 density、side/frontier root 和 masked local naturalization。目标是减少 bead/voxel 感，同时保持 surface r0/r1 连通和 attachment neck。
4. **IFS branch tree 专项生成**：不要再用普通 tree root 顶替 `ifs_branch_tree_d6`。应使用 transform-copy branch grammar 生成 tree-like high-quality root，至少比较 `ifs_transform_copy_proxy`、matched-guide textured GLB 和新生成 transform-copy root。
5. **Radial ornament hard-surface 修复**：以 `transform_radial4_gear` 和 `cache_radial_transform_fusion` 为两个端点，一个语义强但碎，一个连通强但不像 ornament。实验目标是 clean radial ornament：r0 component 大幅下降、r1 单连通、视觉不再像 voxel terrain。
6. **Scifi/mechanical 作为扩展而非当前主证据**：`scifi_gear_hq`、`scifi_arch_hq` 和 translate module roots 可用于 future architecture/gear coverage matrix；除非新增对应传统 task，否则不要混入当前 12 个 strict procedural pairs。
7. **论文写法同步**：主文 claim 应从“传统方法 topology 差”改为“在相似递归任务下，PS-RSLG 保持可控递归结构，同时通过高质量 root、per-depth projection、masked local naturalization 和 PBR guide 获得更强资产质量”。传统方法很多 surface proxy 是连通的，不能过度声称 fragmentation。

## 7. 当前结论

根质量放宽后，strict matching 的核心不是“复用同一个低质量 primitive”，而是“同任务、同模式、同布局、同深度复杂度下，透明地使用更强 root 实例化 PS-RSLG token”。现有材料中，vine/root、tree/crown 和 pyrite/lattice 已有主文候选；DLA/coral、IFS branch tree、radial ornament 还处在诊断或需新 root 生成阶段。
