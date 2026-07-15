# V1-V60 case inventory 使用说明

本目录整理 V1 到 V60 已生成 case 的筛选图、几何文件位置、grammar/spec/manifest/脚本位置，以及一次受限 `a100-2` 远端文件列表。用户筛图优先看 HTML/PNG；后续 agent 复现优先读 JSON 和 `full_path_lists/`。

## 快速入口

- 多候选筛选 HTML: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/case_inventory_v1_v60_20260512/v1_v60_case_inventory_multi_image_gallery.html`
- 单代表图 contact sheet: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/case_inventory_v1_v60_20260512/v1_v60_representative_contact_sheet.png`
- 人类可读 Markdown: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/case_inventory_v1_v60_20260512/v1_v60_case_inventory_for_selection_zh.md`
- 机器可读完整 JSON: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/case_inventory_v1_v60_20260512/v1_v60_case_inventory.json`
- 每版本完整路径列表: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/case_inventory_v1_v60_20260512/full_path_lists`
- 代表图副本: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/case_inventory_v1_v60_20260512/representative_images`
- 多候选图副本: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs/evaluation/case_inventory_v1_v60_20260512/selection_images`

## 字段说明

- `selection_images`: 每个版本最多 16 张优先候选图，已复制到 `selection_images/Vxx/`，用于快速人工筛选。
- `all_image_paths`: 本地全部 raster 图片路径，按 contact sheet/zoom/white/textured 等启发式排序。
- `all_geometry_paths`: 本地全部 `.glb`/`.obj` 路径。
- `all_grammar_or_repro_paths`: 本地全部 `.json`/`.md`/`.py`/`.sh`/`.yaml` 路径，包含 manifest、summary、generator/test/postprocess 脚本等。
- `all_remote_paths`: 来自 `remote_a1002_v1_v60_files.txt` 的远端样本路径；远端状态可能之后变化。

## 当前覆盖验证

- V1-V60 共 60 个版本均有至少一张代表图。
- V1-V60 共 60 个版本均有至少一个本地几何路径。
- V1-V60 共 60 个版本均有至少一个 grammar/spec/repro 路径。
- 本 inventory 没有修改 `paper_siga/main.tex`。
