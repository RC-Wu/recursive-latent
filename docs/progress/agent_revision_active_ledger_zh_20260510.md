# 论文修订与实验补强活动台账（2026-05-10 00:20）

## 当前执行原则

- 权威修订文档：`/Users/fanta/Downloads/agent_revision_and_experiment_requirements.md`。
- 论文主线必须收束为：**在稀疏 3D latent state 上执行的 generation-model-native recursive grammar / recursive language**。
- Projection 只能写成递归执行语义中的 **admissibility-constrained state selection**；不能表现为 case-by-case 手工 mesh repair。
- Texture/PBR 只作为 selected projected meshes 的 export compatibility；不能作为核心算法贡献。
- 正式视觉结果只接受 mesh/textured-mesh 的 Blender/论文级渲染；matplotlib/点云只能作为诊断或负例。
- 当前远端存储约 `96G/100G`，因此优先低存储实验、JSON/CSV 汇总、少量 OBJ/PNG；暂停大规模 GLB texture export。

## 已启动的并行工作

1. **远端 GPU 实验（主控）**
   - 运行：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results/projection_variant_connectivity_ralph_20260510_0018`
   - 日志：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/logs/projection_variant_connectivity_ralph_20260510_0018`
   - GPU 4：bismuth root，`raw / sparse_close / sparse_close_bridge / mesh_bridge_smooth`
   - GPU 5：pyrite root，同协议
   - GPU 6：volumetric coral root，同协议
   - GPU 7：hard-DLA stress root，同协议但更大 close/bridge radius
   - 目的：补齐修订文档要求的 projection variants / no-vs-close-vs-bridge / 非 tree 连通性证据。

2. **论文修订 subagent：Pascal**
   - 写范围：`paper_siga/main.tex` 与一份 `docs/paper/` 状态说明。
   - 目标：abstract/intro/preliminaries/method 符号与叙事按修订文档重写，保留 `EvidencePending` / `ExpFigTODO`。

3. **实验闭合 subagent：Franklin**
   - 写范围：`docs/evaluation/projection_variant_connectivity_followup_zh_20260510.md` 与小型结果汇总。
   - 目标：等待远端 run 完成后聚合 `summary.json`，解释哪些 claim 可支撑、哪些仍待证据。

4. **图库与渲染协议 subagent：Mill**
   - 写范围：`case_gallery_for_user_20260509/README.md`、`index.csv` 与一份 `docs/visuals/` note。
   - 目标：把候选 case 按 main positive / boundary / negative / appendix 分类，强调纯白、无平台、mesh-only 协议。

## 修订文档逐项状态

| 类别 | 当前状态 | 立即行动 |
|---|---|---|
| Abstract / Introduction | 部分完成，但仍需彻底 grammar-first；projection 仍偏强 | Pascal 正在改 `main.tex` |
| Related Work | 已有 procedural / 3D generator / editing 分组，但还需更系统引用和压缩 | 先保留 TODO，后续补 bib 与语言 |
| Preliminaries | 已存在，但定义仍需更文献化，Trellis-style pipeline 图仍缺 | Pascal 改正文；图保持 `ExpFigTODO` |
| Method 符号 | 已部分修复 `R_d` 等冲突；仍需 operator table 与 projection/naturalization 更严谨 | Pascal 改主文；后续根据实验清 TODO |
| Projection variants | 旧证据不足，最关键缺口之一 | 新四 GPU sweep 正在跑 |
| Naturalization ablation | Flow/SDE sampler-only 已是负面/控制证据；masked-local 正证据不足 | 暂不扩展大任务，先写成 partial/negative |
| Latent-vs-mesh novelty | 仍是最大 blocker，现有证据不够同根公平 | 后续需单独实验矩阵 |
| Effective resolution | 概念和指标已有，但无强实验证据 | 先保留主文 TODO，不强 claim |
| Metrics | LCR/occupancy 已不足；需要 mesh/skeleton/morphology/runtime/material | Franklin 汇总已有，后续扩 metric suite |
| Baselines | 传统 clean scaffold 在连通性上也很强，说明指标需重设 | 论文必须改成 asset-readiness / latent execution / effective detail 对比 |
| Visual rerender | 纯白无平台协议已接受；部分图库还需清理分类 | Mill 清理图库 |
| Texture/PBR | 当前质量用户已认可，但只能作为 compatibility | 论文贡献中降级 |
| Figures-only pages / appendix split | 结构意识已有，但主文还过长 | 编译后再做页面切分 |

## 当前风险判断

- **存储风险高**：远端根目录约 `96G/100G`，新实验如果继续增长，需要停止 hard-DLA 或不再写新 mesh。
- **论文核心风险仍是 novelty evidence**：必须证明不是 “procedural mesh + projection + Trellis texture”。当前最直接缺口是 latent-space vs mesh-space and ordinary texture-export baseline。
- **非 tree 视觉风险缓解但未解除**：pyrite/bismuth textured candidates 可作为 occupancy-primary positives；coral 边界；hard-DLA 仍主要是 stress/negative。
- **Flow/SDE 风险**：目前 sampler-only 不能替代 grammar/projection，应写成为什么需要 PS-RSLG 的负面证据，不应作为正贡献。

## 下一轮 Ralph Loop 顺序

1. 监控 projection sweep，若完成则拉取 `summary.json`/CSV 而非大 mesh。
2. 汇总 projection variants 到实验表，标出 strict positive / boundary / negative。
3. 整合 Pascal 的 paper revision，编译 `main.pdf`。
4. 将 Franklin/Mill 的文档同步到 Obsidian 与 AgentDoc mirror。
5. 如果远端存储仍安全，再考虑最小化 latent-vs-mesh 或 runtime/token-growth 任务；否则优先本地论文和指标整理。
