# V9 Organic Frontier 严格匹配生成计划

日期：2026-05-10

## 目标

V9 只处理 DLA / frontier / crystal 严格匹配行，目标是修正 V8 / V8-thin 仍像平滑管子、杆件或几何枝条的问题。V9 不是本地筛选或后处理，而是新的远端输入生成算法：所有最终候选仍必须在 `a100-2` 上重新生成 textured GLB / PBR。

## 严格匹配约束

- 传统目标：`dla_coral_cluster_900`、`dla_frontier_sheet_700`、`dla_crystal_cluster_520`。
- 递归模式：随机 frontier attachment + occupancy exclusion + rooted accretive graph growth。
- 远端机器：`a100-2`。
- GPU：仅使用 `4,5,6,7`。
- 存储根目录：`/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`。
- 本地 dry-run 只生成 OBJ root 输入、guide 图、manifest 和初始指标，不启动远端实验。

## 相对 V8 的算法变化

V8 的主要问题不是连通性，而是近景仍像光滑粗管或杆件。V9 直接改变 frontier 几何发射方式：

- 将每条 frontier edge 从直管改成多环曲线边，加入曲率偏移和半径正弦扰动。
- 所有末端添加细针状 tip，避免 flat cut 或胶囊头。
- 在 scaffold 边上添加非对称 ridge fin，增强脊线和非平直表面。
- 在边上添加 annular perforated membrane，保留真实孔洞，但膜片通过 center 顶点挂接到 scaffold，避免漂浮薄片。
- coral / frontier / crystal 共用同一个 DLA/frontier attachment 协议，但 guide 和几何 profile 分开：coral lace、coral plate、frontier filigree、crystal needle。

## 输出文件

- `assets/strict_visual_matched_cases_v9_organic_frontier_20260510.py`
- `assets/launch_strict_visual_matched_texture_v9_organic_frontier_20260510.sh`
- `tests/test_strict_visual_matched_cases_v9_organic_frontier_20260510.py`
- `docs/evaluation/strict_visual_matched_v9_organic_frontier_plan_zh_20260510.md`

Dry-run 默认输出：

`results/strict_visual_matched_cases_v9_organic_frontier_20260510_dryrun/`

其中包含：

- `manifest.csv/json`
- `initial_metrics.csv/json`
- `a100-2_cases.txt`
- `gpu4_cases.txt` 到 `gpu7_cases.txt`
- 每个 case 的 OBJ 和 metadata JSON

## 建议远端分配

V9 总计 12 个 case，建议每张 GPU 3 个：

- GPU 4：coral lace A、frontier fan A、crystal needle A
- GPU 5：coral antler、frontier ripple、crystal frosted blade
- GPU 6：coral open reef、frontier open boundary、crystal ridge fan backup
- GPU 7：coral porous table、frontier plate backup、crystal branching prism backup

启动方式建议在确认 GPU 空闲和远端存储低于 100GB 后执行：

```bash
cd /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507
bash assets/launch_strict_visual_matched_texture_v9_organic_frontier_20260510.sh
```

可选 seed 池：

```bash
SEED=20263100 RUN=strict_visual_matched_texture_v9_organic_frontier_seed20263100_20260510 bash assets/launch_strict_visual_matched_texture_v9_organic_frontier_20260510.sh
SEED=20263300 RUN=strict_visual_matched_texture_v9_organic_frontier_seed20263300_20260510 bash assets/launch_strict_visual_matched_texture_v9_organic_frontier_20260510.sh
```

## 评价口径

V9 本地 dry-run 只能证明输入 root 的协议和初始连通性，不能替代远端 PBR 输出。若远端结果仍出现管状感，应优先检查：

- Trellis2 是否过度平滑了 perforated membrane 和 ridge fin；
- guide 图是否把 coral/crystal 材质推成胶质表面；
- 是否需要降低主 scaffold 半径并增加 ridge/membrane 比例；
- 是否需要对 coral case 增加更多局部扁平叶片，而不是继续增加 branchlet。
