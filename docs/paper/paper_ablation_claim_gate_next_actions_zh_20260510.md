# R-SLG Ablation Claim Gate 下一步动作

日期：2026-05-10  
角色：paper / ablation claim-gate worker  
范围：只读核对 reviewer 批评整理、P0/P1 claim gate 状态、论文修订完成度状态，以及 `paper_siga/main.tex` 的方法与实验章节。未 SSH，未修改 `paper_siga/main.tex`。

## 0. 总判断

当前 `main.tex` 已经明显向安全主线收敛：方法部分从“大状态 / 大 tuple / 长算子链”改成了核心 sparse-latent state、handle-local rule template、compact recursive transition、Algorithm 1、masked local naturalization、model-native projection、scope/export/complexity。实验部分也已经把 projection、baseline、naturalization、export、effective-resolution 和 boundaries 放进同一章，并且多处 caption 已显式降级 DLA/crystal/texture/export 的 claim。

但从 claim gate 角度，证据链仍不能支持完整强 claim。最安全的论文身份仍应是：

> PS-RSLG 是一个 finite-depth、projection-stabilized、native sparse-latent recursive execution framework；projection inside recursion 是当前最强结构证据；naturalization、export、effective-resolution、non-tree family 仍必须按 gate / diagnostic / boundary 写。

## 1. P0 Claim Gates

### 1.1 Same-root matrix

**已完成证据**

- `results/same_root_miniset_render_qa_20260510/` 已有 `vine_compete_d3` 和 `tree_compete_d3` 的 direct / final-only / prune 本地 OBJ、GLB、render QA。
- `paper_siga/main.tex` 中 Table `projection-ablation` 已把 direct、final-only、per-depth projection 放入同 root/operator/depth 的 projection ablation 叙事。
- 当前最安全可写结论是：在 conservative vine/tree depth-3 projection subset 中，direct recursion 碎片多，per-depth projection 明显改善；vine prune 行可写为 1 component / LCR=1.0 的局部正证据。

**缺口**

- strict same-root six-row matrix 未闭合：`traditional`、`bridge`、`proposed` 对 `vine_compete_d3` / `tree_compete_d3` 仍缺本地同 root、同 seed、同 depth、同 renderer、同 QA 的完整行。
- full family matrix 仍 blocked：coral、bismuth、pyrite 多数行仍是远端快照、selected row、或缺本地 final asset / GLB / render QA。
- 还缺 handle-level 中间态指标：active orphan handles、invalid fired handles、root-reachable frontier ratio、handle survival、deleted mass。

**不能写的强 claim**

- 不能写 same-root matrix 已闭合。
- 不能写 projection / bridge / traditional / proposed 已完成公平 six-row 定量比较。
- 不能写 native sparse-latent execution 已全面优于 mesh-space recursion 或 classical baselines。

**下一步闭合动作**

1. 优先补 `vine_compete_d3` 的 `traditional`、`bridge`、`proposed` 三列，并严格复用现有 direct / final-only / prune 的 root、depth、camera、renderer、GLB/render QA。
2. 若时间允许，再补 `tree_compete_d3` 同样三列，形成最小 two-root same-root matrix。
3. 为 same-root matrix 增补中间态 handle 指标，证明 final-only 的问题发生在递归过程中，而不是只发生在 terminal mesh。
4. 主文只引用已闭合 subset；未闭合 full matrix 放 appendix/status。

### 1.2 Naturalization matrix

**已完成证据**

- `main.tex` 方法部分已把 naturalization 写成 masked local flow / sparse feature blending，且明确 frozen generator 不是 global topology repair。
- `main.tex` 实验部分已有三任务三 seed 的 focused masked-local-naturalization ablation 叙事，支持 masked local naturalization 作为 projected state 下的 local surface/material realization operator。
- `results/naturalization_lsystem_miniset_qa_20260510/` 已有 L-system selected 四列 GLB/PBR/import QA，可支撑谨慎 visual/export ablation。

**缺口**

- selected L-system 四列的 source OBJ 仍是 remote-only，缺本地 OBJ connectivity、root reachability、mask leakage、anchor drift。
- with projection / without projection 控制未闭合，不能把 naturalization 贡献和 projection 贡献分离。
- non-tree controls（coral/pyrite）只到 weak-vs-masked selected visual/status，缺 rule-only、global-N、projection on/off、topology/root metrics。

**不能写的强 claim**

- 不能写 masked naturalization 修复 topology。
- 不能写 naturalization matrix 已闭合。
- 不能写 masked local-N 可以替代 per-depth projection。
- 不能写 coral/crystal naturalization 已稳定成功。

**下一步闭合动作**

1. 本地化 `lsystem_branch/fork_side` 四列 source OBJ，并补 OBJ connectivity、root reachability、mask leakage、anchor drift。
2. 对同一 selected root 补 with/without projection matched controls，拆开 projection 与 naturalization 的贡献。
3. 对 coral/pyrite 仅做 appendix 级补强：rule-only、global-N、projection on/off、topology/root metrics；不要优先抢主文 P0。
4. 主文措辞固定为：local realization under projected state；appendix 暴露完整 gap/status。

### 1.3 Effective-resolution / zoom retention

**已完成证据**

- `main.tex` 已在 scope/refinement 部分给出 token budget / local support accounting，并把 effective-resolution 明确写成待测 claim。
- `results/effective_resolution_metrics_20260510/` 与 `paper_siga/drafts/publication_ablation_effective_resolution_status_20260510.tex` 提供了 local_feature_scale、terminal_detail_count、zoom_retention proxy、face/GLB size、high-res blow-up estimate。
- `main.tex` 中 two-level zoom panel 和 effective-resolution status table 目前适合作为 qualitative/proxy diagnostic。

**缺口**

- 缺 same token / same face budget 的 one-shot vs recursive 定量。
- 缺 matched zoom render panels 的人工 QA 与 camera-level 对齐说明。
- 缺 handle-level detail survival after decode / project / re-encode。
- proxy 指标尚不能支撑摘要、contribution 或结论级分辨率优越性。

**不能写的强 claim**

- 不能写 PS-RSLG 定量证明 effective resolution 优于 one-shot generator。
- 不能写 universal zoom-retention 或 terminal-detail superiority。
- 不能把 effective-resolution 当作主贡献闭合。

**下一步闭合动作**

1. 固定 one-shot / trivial-copy / PS-RSLG 的 root、camera、token/face budget，补 same-budget zoom panel。
2. 定义并报告 terminal detail count、minimum visible feature scale、local token density、detail survival。
3. 将当前 proxy table 保持在 appendix/status；除非 matched experiment 闭合，否则主文只写 diagnostic。

### 1.4 DLA / coral / hard frontier fragmentation

**已完成证据**

- DLA bridge smoke 与 mesh QA 已证明 post-hoc bridge 是 negative/boundary diagnostic：face-level 指标可改善，但 occupancy/support 或视觉桥接仍不可靠。
- `main.tex` 已把 DLA/coral caption 降级为 grammar-native connected scaffold / stress case，而不是 physical DLA claim。
- coral mesh-space generated-root 负控已闭合，可证明 direct copy-paste mesh-space generated-root recursion 会产生极高 raw face islands。

**缺口**

- hard-DLA raw 仍碎；post-hoc bridge 不能成为正路线。
- grammar-native connected scaffold 只在 selected coral-style rerun 上较强，full coral same-root/naturalization matrix 未闭合。
- 缺 DLA/frontier family 的 root/seed robustness 与 attachment-aware proposal 统计。

**不能写的强 claim**

- 不能写 DLA/frontier growth 已解决。
- 不能写 bridge/cache 能稳定修复 fragmentation。
- 不能写 coral/DLA family 已整体闭合，或 physical DLA process 被恢复。

**下一步闭合动作**

1. 停止把 post-hoc bridge 扩展成 positive line；保留为 boundary diagnostic。
2. 优先推进 grammar-native volumetric / attachment-aware connected scaffold，记录 accepted attached proposals、connector masks、orphan support。
3. coral 只写 selected connected recursive asset / stress case，full family claim 等 same-root 与 naturalization 控制补齐后再升级。

### 1.5 Appendix / main split and 4.7 / 4.9 / 4.10

**已完成证据**

- `main.tex` 已有 `\clearpage` + `\appendix`，并包含 Supplementary Material Roadmap。
- 主文已有 `Naturalization, Export, and Effective Resolution` 与 `Boundaries and Supplement Placement`，多处文字已强调 gate / diagnostic / boundary。

**缺口**

- Appendix 目前仍含中文写作方案、revision log、TODO list 与内部状态语言，不能作为投稿版 appendix。
- 主文仍放了 effective-resolution status table、zoom diagnostic、selected scaffold、pyrite/coral、masked naturalization 等较多状态/诊断材料，最终仍需筛选。
- 4.7 仍承担 naturalization + export + effective-resolution 多重任务；4.9/4.10 仍应进一步合并压缩为收束小节。

**不能写的强 claim**

- 不能说 appendix/supplement split 已完成投稿级整理。
- 不能让 appendix status figure 成为主文核心论证依赖。
- 不能保留 visible TODO、draft、smoke、planned、current local log 等投稿危险痕迹。

**下一步闭合动作**

1. 将 4.7 改成更窄的 `Naturalization Claim Gate`：只服务 masked local realization，不承载 effective-resolution 强 claim。
2. 合并 4.9/4.10 为 `Export Compatibility, Effective-Resolution Diagnostics, and Boundaries`，只保留 3-5 段收束文字。
3. 建立 appendix/supplement index：每个 figure/table 标注 role、allowed claim、main / appendix / supplement / figures-only 去向。
4. 投稿版移除中文计划、revision log、TODO、内部状态语言；保留 compile-preserving material 只能作为正式 supplement。

## 2. P1 Claim Gates

### 2.1 Crystal / symmetry non-tree positive case

**已完成证据**

- Pyrite HQ depth textured showcase 是当前最强 non-tree selected positive。
- surface-sampled voxel connectivity 与 symmetry/orbit metrics 可支持 crystal/symmetry-inspired connected scaffold 与 export compatibility。

**缺口**

- 不是完整 same-root 或 naturalization matrix。
- symmetry/orbit metric 仍是 screening diagnostic，不是严格 equivariance。
- raw GLB face components 不能当 topology proof；bismuth 视觉/material 仍不够主结果级。

**不能写的强 claim**

- 不能写真实晶体生长、严格 symmetry/equivariance、watertight/manifold topology。
- 不能写 crystal family 全面闭合。

**下一步闭合动作**

1. 主文只保留 pyrite 作为 selected lattice/scaffold evidence。
2. 将 symmetry/orbit 指标命名为 screening diagnostic。
3. 若要升级，补 same-root transform-copy matrix、projection on/off、multi-seed visual/metric QA。

### 2.2 Coral non-tree connected scaffold

**已完成证据**

- selected coral-depth textured showcase 可作为 coral-inspired connected recursive asset / non-tree stress case。
- coral mesh-space generated-root baseline 已完成一个强 negative control。

**缺口**

- coral same-root direct/prune/bridge 多数仍是远端或局部证据。
- coral naturalization only partial；mesh-space full baseline 只闭合 generated-root 负控。

**不能写的强 claim**

- 不能写 coral family、DLA family、coral mesh-space baseline、same-root、naturalization 均完成。
- 不能写 coral result 证明 physical DLA/coral growth。

**下一步闭合动作**

1. 把 coral 放在 selected connected scaffold / stress case，而不是 main quantitative family claim。
2. 后续补 coral rule-only、global-N、masked-N、projection on/off、root metrics，再考虑进入 appendix matrix。

### 2.3 Full latent-vs-mesh baseline

**已完成证据**

- Coral mesh-space generated-root 负控已闭合。
- one-shot Trellis2、latent-copy、mesh-space generated-root、selected PS-RSLG 已形成当前 controlled comparison 的初步框架。

**缺口**

- TRELLIS non-2 / Hunyuan、strict ordinary gen3D rows、latent-copy vs mesh-space vs PS-RSLG full same-budget alignment 未完整闭合。
- 部分 rows 是 blocked/missing 或 selected 口径，不能混成公平定量胜负。

**不能写的强 claim**

- 不能写所有普通 3D generator 已公平评估并被击败。
- 不能写 full latent-vs-mesh baseline 已闭合。
- 不能写 sparse-latent grammar 全面优于 mesh-space procedure + texture export。

**下一步闭合动作**

1. 先把 current table 标成 controlled comparison / negative controls / selected rows，不写 universal superiority。
2. 补 mesh repair/re-encode variants、same-budget alignment、strict ordinary gen3D rows。
3. Hunyuan/TRELLIS non-2 只能在本地安装与缓存闭合后进入定量表；否则保留 planned secondary baseline。

## 3. 最小主文安全写法

主文可以安全写：

- PS-RSLG treats recursive 3D generation as stateful finite-depth execution over sparse generator-native latents.
- Per-depth projection prevents detached decoded support from becoming later active handles in conservative tested programs.
- Masked local naturalization is a local surface/material realization operator under already projected state.
- Selected connected scaffold families can enter the frozen Trellis2 GLB/PBR export path.
- DLA/coral/crystal examples are connected-scaffold or stress-test evidence, not physical-process recovery.
- Effective-resolution evidence is currently qualitative/proxy diagnostic.

主文必须避免：

- full same-root matrix closed。
- masked naturalization repairs topology。
- effective-resolution quantitatively superior to one-shot generation。
- all non-tree families solved。
- all ordinary 3D generators / mesh-space recursion fairly beaten。
- texture/PBR export proves structural validity。

## 4. 建议执行顺序

1. 补 `vine_compete_d3` same-root `traditional / bridge / proposed`，形成最小 full-row projection matrix。
2. 本地化 L-system naturalization source OBJ，并补 root / anchor / leakage / projection on-off 指标。
3. 做 matched zoom render QA 与 same-budget effective-resolution mini experiment。
4. 对 coral/pyrite 只补 appendix 级 naturalization/projection controls，不抢主文。
5. 建 appendix/supplement index，迁移 status inventory、guide sweeps、candidate screens、DLA bridge、effective-resolution proxy。
6. 最后清理投稿危险语言：TODO、draft、current、smoke、planned、blocked、本地日志口吻、中文内部计划。
