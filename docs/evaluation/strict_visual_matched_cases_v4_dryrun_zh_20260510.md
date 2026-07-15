# Strict visual-matched cases V4 dry-run notes（2026-05-10）

入口脚本：`assets/strict_visual_matched_cases_v4_20260510.py`

默认输出：`results/strict_visual_matched_cases_v4_20260510_dryrun`

本批次只生成本地 Trellis2 输入，不启动远端任务，不修改已有 launcher。严格对比的远端目标在 manifest 和 per-case metadata 中记录为 `a100-2`，后续正式生成必须在 `a100-2` 上重新跑 Trellis2，而不是只本地筛选或后处理。

V4 设计约束：

- L-system / space colonization / DLA-frontier / IFS-transform 均保持一对一传统 target、同类别、同递归模式和相近复杂度。
- plant/tree/root 使用 continuous trunk/branch/root occupancy，needle/leaf/root-hair 细节通过隐式桥接附着，避免 V3 的碎卡片和 V3b 的单纯 blocky blob。
- DLA/coral/frontier 使用 connected support + smooth implicit surface + deterministic bump/porosity proxy，避免 cube-per-hit 或独立珠状碎片。
- IFS/radial/lattice 使用 transform orbit、torus/ring/spine/bridge 或 connected lattice cache 保留递归/变换模式并降低组件数。
- `root_selection_log` 明确标记为 `proxy_generated_mesh` 和 local dry-run；正式论文证据仍需要 mesh/PBR render。

本地运行：

```bash
python3 assets/strict_visual_matched_cases_v4_20260510.py
```

快速小批：

```bash
python3 assets/strict_visual_matched_cases_v4_20260510.py --case-limit 8
```

输出文件：

- `manifest.csv` / `manifest.json`
- `initial_metrics.csv` / `initial_metrics.json`
- `a100-2_cases.txt`
- `gpu2_cases.txt`
- `_guides/*.png`
- 每个 case 目录下的 OBJ 和 `*_metadata.json`
