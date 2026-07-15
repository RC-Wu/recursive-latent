---
id: PRJ-RECURSIVE-3D-GENERATIVE-GROWTH-ENTRY
title: Recursive 3D Generative Growth Docs Entry
tags: [project, trellis2, procedural_modeling, recursive_generation, research]
domain: [research, 3d_generation, experiments]
summary: "Project entry for empirical research on using Trellis2 as a recursive naturalization operator for procedural 3D growth grammars."
updated_at: "2026-05-07"
owner: "codex"
---

# Scope

This project investigates whether a frozen structured 3D generator, primarily Trellis2, can be used as a recursive naturalization operator for procedural grammars.

Primary target:

- run Trellis2 capability and operator diagnostics on new A100 `a100-2`
- run traditional procedural baselines locally on Mac
- implement the simplest Trellis2 generative baselines that actually run
- pull visual artifacts to Mac and inspect them directly before making research claims

# Active Roots

- Mac local project root: `/Users/fanta/code/agent/Code/recursive_3d_generative_growth`
- New A100 project root: `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
- Existing Trellis2/MeshVAE source context on new A100: `/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff`
- Input proposal: `/Users/fanta/Downloads/recursive_3d_generative_growth_proposal.md`

# Current Plan

- `plans/recursive_3d_generative_growth_ralph_plan_20260507.md`

# Current Research Notes

- `research/recursive_growth_literature_and_baseline_notes_20260507.md`
- `research/minimal_operator_design_and_metrics_20260507.md`
- `research/trellis2_zero_condition_diagnostics_20260507.md`
- `research/trellis2_handcrafted_proxy_diagnostics_20260507.md`
- `research/trellis2_latent_transform_probe_20260507.md`
- `research/trellis2_conditioning_problem_reframe_and_vae_coverage_20260507.md`

# Update Rules

- Treat `plans/recursive_3d_generative_growth_ralph_plan_20260507.md` as the living task ledger.
- Every phase transition, failed run, successful run, visual pull, or research conclusion must append a timestamped progress entry to the plan.
- Mirror updated AgentDoc project files into the local project root under `docs/agentdoc_mirror/`.
- Mirror the same docs to the new A100 project root under `docs/agentdoc_mirror/`.
- Keep the new A100 project folder below 50GB. Prefer references/symlinks to existing Trellis2 code and weights instead of copying large assets.
