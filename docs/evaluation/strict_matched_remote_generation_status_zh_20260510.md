# 严格一对一远端新生成状态与用户纠偏（2026-05-10）

范围：本文只记录当前用户纠偏、远端新生成要求、严格匹配标准和后续检查项。本文不修改 AgentDoc 主计划，不修改代码，不代表主线程最终同步状态。

## 1. 最新用户纠偏

用户明确纠偏：当前 strict matched baseline / ours 比较不能停留在本地已有 case 的挑选、拼图、后处理或语义替换。

必须执行的新要求：

1. 必须在远端 `a100-2` 的 GPU `4/5/6/7` 上生成新的 ours case。
2. 不能只从本地已有资产中挑选候选，也不能只靠本地渲染、repair、camera zoom、contact sheet 或后处理来构成新证据。
3. 新 case 必须面向严格一对一比较的任务集合生成，而不是用高质量但任务不匹配的 root/GLB 顶替。
4. 本地已有候选可以继续作为参考、失败边界或 selection baseline，但不能替代远端新生成。

## 2. 严格一对一比较标准

严格 matched comparison 至少需要同时满足以下条件：

1. **同一任务语义**：baseline 与 ours 必须针对同一个 procedural task，而不是仅共享宽泛类别。例如 vine 不能随意顶替 pine canopy，ordered crystal 不能随意顶替 stochastic DLA。
2. **同一递归/生成模式**：L-system、space colonization、DLA/frontier、IFS/transform-copy 等 family 不能混用。若 ours 使用不同 root 或 naturalization，必须说明它如何继承或约束同一任务模式。
3. **同一输入约束**：尽量共享 seed、target skeleton、attractor set、hit set、transform schedule、depth budget、root policy、尺度归一化和相机协议。
4. **同一选择预算**：不能对 ours 做无限筛选而 baseline 只取一个默认样本。需要记录生成数量、筛选规则、失败数和最终选择依据。
5. **同一评估协议**：同一指标脚本、同一 occupancy/surface 分辨率、同一 camera-level zoom、同一纯白背景和同一 contact sheet 排列。
6. **结构与视觉都要过关**：连通性指标通过不等于 matched task 成功。必须同时检查递归结构保真、family-specific metric、视觉可读性和 asset quality。
7. **禁止宽松替换叙事**：如果 IFS branch 结果像 blob，或者 L-system 结果丢失 branch hierarchy，即使 root-connected，也只能标记为 failure/boundary，不能作为正例。

## 3. 远端批处理应覆盖的 case

远端新生成应覆盖以下 12 个 strict matched task。命名可由主线程统一，但语义范围应保持稳定。

| family | required cases | 关键匹配点 |
|---|---|---|
| L-system | `pine`, `root`, `vine` | turtle/rewriting 深度、分支层级、tip 分布、root/trunk 方向必须可读 |
| Space colonization | `crown`, `root`, `bush` | 共享 attractor set 或等价采样协议，检查 coverage、branch path 和 crown/root/bush 形态 |
| DLA/frontier | `coral`, `frontier` | 明确 seed/root policy、frontier attachment、porosity/cavity、fake bridge 风险 |
| IFS/transform | `branch`, `radial`, `lattice` | 保留 affine transform-copy orbit、scale decay、radial symmetry 或 lattice repetition |

建议远端批处理最小矩阵：

1. 每个 task 至少生成 ours 正例候选。
2. 每个 task 保留 raw / direct sparse grammar / projected / naturalized 或相近阶段输出，便于判断 projection 和 naturalization 是否破坏 task fidelity。
3. 每个 task 至少记录 4 个 seed 或明确说明当前只是 smoke run。
4. 输出 manifest 必须包含 case id、family、seed、depth/step budget、root source、guidance/source target、GPU id、命令摘要、生成时间和失败状态。

## 4. 远端执行约束

主线程同步时应确保：

1. 远端目标机器为 `a100-2`。
2. 使用 GPU `4,5,6,7` 做并行新生成。
3. 每个 GPU 的任务分配、日志路径、输出目录和退出码需要可追溯。
4. 不把本地已存在的 `vine_stage5`、`tree_compete_s3`、`pyrite_stage4`、`coral_density_0p25_octopus` 等直接冒充本次远端新生成结果。
5. 本地后处理只能在远端生成完成后作为统一评估/渲染步骤，不得替代新生成。

## 5. 后续检查项

### 5.1 生成产物检查

- [ ] 远端输出目录存在，且每个 required case 都有独立 case id。
- [ ] 每个 case 有 mesh/GLB 或中间结构文件、manifest、日志和失败记录。
- [ ] manifest 明确记录 GPU `4/5/6/7` 的分配和运行命令。
- [ ] 生成时间晚于本次纠偏记录，避免混入旧资产。
- [ ] 每个 family 至少有一个可渲染候选，同时保留失败样本用于筛选透明度。

### 5.2 严格匹配检查

- [ ] L-system pine/root/vine 是否保留 branch hierarchy、tip 分布、root/trunk 方向。
- [ ] Space-colonization crown/root/bush 是否共享或记录 attractor set，并报告 coverage/path 指标。
- [ ] DLA coral/frontier 是否保留 frontier/porosity，并记录 fake bridge 与 seed/root policy。
- [ ] IFS branch/radial/lattice 是否保留 transform-copy orbit、scale decay、对称性或 lattice repetition。
- [ ] 对不满足 task fidelity 的结果标记 failure/boundary，不进入正例表。

### 5.3 评估与图像检查

- [ ] 使用同一 surface/occupancy connectivity 协议跑 baseline 与 ours。
- [ ] 补充 family-specific metric，而不只报告 component/LCR/root ratio。
- [ ] 统一 pure-white fixed-camera overview。
- [ ] 每个 case 做 camera-level zoom：root/seed、junction/frontier、terminal tip/cavity/copy。
- [ ] contact sheet 不允许通过 crop 或尺度变化制造不公平视觉优势。

### 5.4 论文叙事检查

- [ ] 不写“传统方法天然不连通”这类过强结论。
- [ ] 不写“PS-RSLG 已经全面击败 L-system/SC/DLA/IFS”，除非 12 个 case 全部通过结构、视觉、多 seed 和 family-specific metric。
- [ ] 对 SC/DLA 可以先写 provisional matched-mode proxy，但必须附 caveat。
- [ ] 对 L-system/IFS 若仍 blob 化或 orbit 丢失，应写成 failure/boundary 和下一步，而不是成功案例。
- [ ] 主文、caption、supplement 中统一说明 selection budget 和失败率。

## 6. 当前状态判断

截至本文记录时，当前材料主要是本地候选、proxy audit、strict matched target 与弱项搜索结果；它们有助于定义任务和失败边界，但不足以回应用户最新纠偏。

下一步的核心不是继续本地挑图，而是在 `a100-2` 的 GPU `4/5/6/7` 上按上述 12 个 strict matched task 批量生成新 case，并用统一协议回收、评估和标记正例/失败/边界。
