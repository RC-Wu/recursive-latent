# Reviewer 批评当前应用状态（2026-05-09）

来源文件：`/Users/fanta/Downloads/论文修改意见与reviewer批评整理.md`

## 已处理

- 方法名和主线已经基本收束到 **PS-RSLG / Projection-Stabilized Recursive Sparse-Latent Grammar**。
- 主文状态已经从工程式大元组降为 `z_d=(V,F,A)`，完整复杂状态转为附录/理论文档口径。
- `main.tex` 已加入 compact recursive transition、masked flow naturalization、projection inside transition、material handle/export 边界。
- 新增 mesh-rendered projection ablation 图，避免只用旧 preview 支撑核心 claim。
- 新增 coral extreme same-condition parameter figure，替换旧的弱参数图。
- texture table 的 `Paper use` 草稿列名已改为正式的 `Evaluation role`。

## 仍是 P0 风险

- `main.tex` 仍有大量注释保留旧文本，这是按用户要求“被替换内容先注释掉”保留的，但正式投稿前必须整体清理或移到 appendix/draft。
- Results 仍然偏状态报告，后续应改为 claim-based organization：
  - direct/final-only failure；
  - per-depth projection stabilization；
  - stability-expression boundary；
  - selected texture/PBR export；
  - diagnostic/failure boundary。
- Classical systems coverage 仍在主文展开较长，后续应压成一段和小表，详细 proof 移附录。
- Figure 数量远超 SIGA 主文容量，现在是研究草稿状态，后续必须筛选主图，把大矩阵/弱 case 转 supplement。
- 指标口径必须持续明确：occupancy-primary connected support、welded face diagnostics、raw GLB face components 是不同指标，不能混写。

## 本轮论文更新的安全 claim

可以写：

- Conservative competition + per-depth projection produces stronger finite-depth connected recursive support than direct recursion or final-only cleanup in matched vine/tree cases.
- Texture/PBR export works for selected projected meshes, including depth-5 vine and endpoint coral density cases.
- Same-condition control figures demonstrate qualitative depth/parameter behavior.

不能写：

- 所有 operator family 已解决；
- DLA/crystal physical growth 已解决；
- GLB raw topology clean；
- 我们在 connectivity 上全面优于传统 L-system/space-colonization baseline；
- material recursion consistency 已经被证明。
