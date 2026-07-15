# A100 SIGA Recursive Growth Project Inventory

Date: 2026-07-15
Scope: migration inventory for the SIGGRAPH Asia-oriented recursive 3D generative growth / PS-RSLG project.

## 0. Current Routing Correction

- Target machine for this project is `a100-2`, not `dev-intern-01` or `dev-intern-02`.
- Local SSH aliases exist for both `a100-2` and `a100-3`, but AgentDoc project docs and all confirmed project roots point to `a100-2`.
- Do not publish SSH credentials or AgentDoc `SECRETS` content. Use configured SSH aliases only.
- Current verified A100 status on 2026-07-15:
  - Host: `a100-2`
  - User: `ruocheng`
  - GPU: 8 x NVIDIA A100-SXM4-80GB
  - Current GPU memory: all 8 cards showed `0 MiB` used during this audit.
  - Storage: `/mnt/beegfs` about `28T` total, `18T` used, `11T` free.

## 1. Canonical Project Roots

### Local Mac

- Main local project root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`
- Local size: about `72G`
- Local root is not a Git repo.
- Important local subdirectory sizes:
  - `assets`: `6.2M`
  - `tests`: `712K`
  - `scripts`: `708K`
  - `docs`: `2.2G`
  - `paper_siga`: `495M`
  - `visuals`: `15G`
  - `results`: `26G`
  - `.hf_local_cache`: `27G`
  - `.worktrees`: `128M`

### AgentDoc

- Canonical AgentDoc project root: `/Users/fanta/code/AgentDoc/PROJECTS/recursive_3d_generative_growth`
- Important entry docs:
  - `PROJECT_DOCS.md`
  - `PROJECT_COMMONS.md`
  - `plans/recursive_3d_generative_growth_ralph_plan_20260507.md`
  - `plans/recursive_3d_generative_growth_siga_night_plan_20260508.md`
  - `plans/recursive_3d_generative_growth_system_grammar_plan_20260508.md`
  - `plans/recursive_3d_generative_growth_gen3d_baseline_ablation_plan_20260510.md`
  - `reports/agent_handoff_2026-05-10.md`
  - `reports/2026-05-10_gen3d_ablation_round_closeout.md`

### A100

- Main A100 project root: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
- Current A100 project size: about `152G`
- Upstream Trellis2/MeshVAE context: `/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff`
- Existing Trellis2 source context: `/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/repos/TRELLIS.2`
- A100 project path env in older context: `/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env`

## 2. What Belongs In GitHub

Target repo can be `RC-Wu/recursive-latent`. Do not push large outputs directly.

### Strong GitHub Candidates

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/assets`
  - Core scripts for PS-RSLG, grammar generation, metrics, rendering, texturing launchers, baseline generation, ablations.
  - Size is small enough for GitHub.
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/tests`
  - Includes local tests for strict visual matched cases and projection/naturalization logic.
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/scripts`
  - Small helper scripts.
- Selected docs from `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs`
  - Include method, evaluation protocols, migration notes, visual protocol, handoff docs, and AgentDoc mirrors.
  - Do not blindly push all `docs` if it contains generated galleries or large image inventories.
- Selected paper source from `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga`
  - `main.tex`, `.bib`, style/template files, and curated figure inputs.
  - Current `paper_siga` is an Overleaf git repo, branch `main`, remote `overleaf`, behind `overleaf/master` by 1.
  - It has many untracked figures/drafts; curate before pushing to GitHub.
- Remote-only small code that is not mirrored locally:
  - `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/trellis_classic_dense_smoke_20260529`
  - This is only about `180K` and should be copied into the repo, likely under `experiments/trellis_classic_dense_smoke_20260529/` or `assets/trellis_classic_dense_smoke_20260529/`.
- A compact environment manifest:
  - Python/Conda env names and key paths.
  - Package install commands.
  - A100 cache path policy.
  - Do not include secrets.

### GitHub With Git LFS Or Release Assets Only

- Small selected PNG contact sheets and final paper figures.
- Curated `case_selection_by_type_20260510` thumbnails only if compressed and intentionally selected.
- Do not push full GLB/OBJ/PLY result pools through normal Git.

## 3. Archive-Only Or External Artifact Transfer

These should be tarred or transferred separately, not committed to GitHub.

### A100 Large Directories

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/results`: about `81G`
  - Main experiment outputs, GLB/OBJ/PLY/PBR candidates, strict visual matched runs V2 through V67, gen3D baselines, Hunyuan probes, 5/29 TRELLIS classic runs.
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/inputs`: about `1.6G`
  - Generated OBJ inputs and manifests for strict visual matched and ablation runs.
  - Keep manifests and selected final inputs; full directory is archive-only.
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/weights`: about `16G`
  - Model weights. Archive only if future network access is uncertain.
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/hf_home`: about `23G`
  - Hugging Face cache. Usually re-downloadable, but useful to archive if reproducibility/offline transfer matters.
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/envs`: about `772M`
  - Environment snapshot; preferably replace with environment YAML plus wheel/cache notes.
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/repos`: about `272M`
  - Contains downloaded TRELLIS classic and Hunyuan3D-2 sources/archives. Archive if those exact snapshots matter.
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/runs`: about `51M`
  - 5/29 TRELLIS classic dense smoke run outputs.

### Local Large Directories

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/results`: about `26G`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals`: about `15G`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/.hf_local_cache`: about `27G`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/docs`: about `2.2G`
  - Many docs are valuable, but galleries and generated inventories may be too large for normal Git.
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/paper_siga/figures`: large and dirty. Curate final figure set separately.

## 4. Safe Discard / Rebuild Candidates

Do not delete automatically without a final confirmation, but these are the strongest cleanup candidates.

### A100

- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/cache`: about `30G`
  - Main reclaim target. Mostly generated caches.
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/hf_home`: about `23G`
  - Re-downloadable model cache if weights are archived elsewhere.
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/triton_cache`: about `18M`
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.cache`: about `7.6M`
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/.tmp`, `.torch`, `.triton`, `.xdg_cache`, `tmp`
- Python bytecode and pytest caches under all project paths.
- `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/repos/Hunyuan3D-2.zip.bad`
- Download archives such as `TRELLIS.zip` and `Hunyuan3D-2.zip` after exact extracted source snapshots are archived or re-download instructions are recorded.

### Local

- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/.hf_local_cache`: about `27G`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/.cache`: about `117M`
- `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/.pytest_cache`
- `.DS_Store`, `__pycache__`, `*.pyc`, transient logs.
- Large local `results`/`visuals` duplicates after selected final figures and manifests are archived.

## 5. Conversation / Provenance Records

### Found

- AgentDoc contains the best structured provenance for the SIGA project:
  - `PROJECTS/recursive_3d_generative_growth/plans/*`
  - `PROJECTS/recursive_3d_generative_growth/research/*`
  - `PROJECTS/recursive_3d_generative_growth/reports/*`
  - mirrored copies under local project `docs/agentdoc_mirror/`
- Current-account local Codex sessions under `/Users/fanta/.codex/sessions` contain many hits for:
  - `recursive_3d_generative_growth`
  - `SIGA`
  - `PS-RSLG`
  - `strict_visual_matched`
  - `a100-2`
  - `Hunyuan3D`
- The densest hit window is 2026-05-07 through 2026-05-10, with many parallel subagent and heartbeat sessions.

### Not Found / Limits

- No readable A100-side `.codex/sessions` history was found in the audited project or home paths.
- A100 project `.codex_env_work` contains only environment/smoke artifacts such as nvdiffrast zip and GLB smoke output, not conversation history.
- If relevant conversations were under another Codex account, they are not visible from the current local account unless that account's session files are mounted or exported.

### Recommended Provenance Archive

- Archive filtered local sessions for dates 2026-05-07 through 2026-05-13 that match project keywords.
- Keep AgentDoc project docs and this migration inventory in Git.
- Do not put raw full `.codex/sessions` into the public GitHub repo if they contain private prompts, credentials, or unrelated task context.

## 6. Project Content Map

### Core Method / Implementation

- `assets/procedural_baselines.py`
- `assets/trellis2_texturing_export_glb.py`
- `assets/run_projected_recursive_loop.sh`
- `assets/strict_visual_matched_cases_*.py`
- `assets/launch_strict_visual_matched_texture_*.sh`
- `assets/projection_masked_ablation_matrices_20260511.py`
- `assets/evaluate_masked_naturalization_ablation_20260510.py`
- `assets/recursive_growth_mesh_metrics.py`
- `assets/mesh_quality_metrics.py`
- `assets/compute_main_experiment_selected_metrics_20260511.py`
- `assets/experiment3_*_20260511.py`
- `assets/render_mesh_contact_sheet.py`
- `assets/blender_*`

### Paper / Figures

- `paper_siga/main.tex`
- `paper_siga/references.bib`
- `paper_siga/drafts/*`
- Curated `paper_siga/figures/*`
- Current state: compile was previously successful in project docs, but `paper_siga` git state is dirty and behind Overleaf by 1.

### Important Evaluation Docs

- `docs/agent_handoff_2026-05-10.md`
- `docs/evaluation/gen3d_and_ablation_evidence_audit_zh_20260510_agent.md`
- `docs/evaluation/evidence_matrix_for_revision_zh_20260510.md`
- `docs/evaluation/case_inventory_v1_v60_20260512/`
- `docs/evaluation/main_experiment_convergence_corrected_V67B_status_zh_20260512.md`
- `docs/evaluation/projection_masked_ablation_matrices_zh_20260511.md`
- `docs/visuals/standard_pure_white_render_protocol_20260510.md`
- `docs/visuals/case_selection_by_type_zh_20260510.md`

## 7. Migration Plan

1. Create or reuse `RC-Wu/recursive-latent`.
2. Commit first only small, source-controlled material:
   - `assets`
   - `tests`
   - `scripts`
   - selected `docs`
   - selected `paper_siga` source
   - environment manifests
   - `.gitignore`
   - `README.md`
3. Copy remote-only small code into the local project before commit:
   - `a100-2:/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/trellis_classic_dense_smoke_20260529`
4. Create a separate artifact manifest for large assets:
   - A100 `results`
   - A100 `inputs`
   - A100 `weights` or re-download instructions
   - local `visuals`
   - local `results`
5. Use Git LFS only for a small curated final figure/thumbnail set if needed.
6. Keep raw GLB/OBJ/PLY pools outside GitHub, as tarballs or object storage.
7. After archive verification, delete rebuildable caches first:
   - A100 `cache`
   - A100 `hf_home` only if weights can be redownloaded or archived
   - local `.hf_local_cache`
   - Python/Triton/temp caches

## 8. Open Questions Before Deletion

- Should `hf_home` be archived for offline reproducibility, or treated as redownloadable?
- Which final figure/case set should be preserved as public GitHub examples?
- Should `paper_siga` remain primarily Overleaf-backed, or be mirrored into `RC-Wu/recursive-latent`?
- Should raw current-account `.codex/sessions` be archived privately, or only AgentDoc summaries kept?
- Is `a100-3` expected to hold additional mirrors for this exact project? AgentDoc does not currently indicate that; current confirmed project root is `a100-2`.
