---
id: PRJ-RECURSIVE-3D-GENERATIVE-GROWTH-COMMONS
title: Recursive 3D Generative Growth Project Commons
tags: [project, trellis2, a100, baseline, visualization]
domain: [research, experiments, ops]
summary: "High-frequency rules for recursive 3D generative growth experiments across Mac local baselines and new A100 Trellis2 runs."
updated_at: "2026-05-07"
owner: "codex"
---

# Operating Rules

- Use at most two concurrent SSH shells to `a100-2`; prefer non-interactive commands or one persistent session for long runs.
- Keep all new A100 artifacts under `/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`.
- Do not copy existing Trellis2 repositories or model weights into the project folder unless strictly needed. Use symlinks or environment variables to stay under the 50GB cap.
- Any long-running command must write stdout/stderr, command snapshot, and outputs under the project folder.
- Pull visual artifacts to `/Users/fanta/code/agent/Code/recursive_3d_generative_growth/visuals` and inspect before declaring a visual result.
- Separate empirical facts from hypotheses. Record failures as useful operator diagnostics.

# Key Existing Context

- Existing Trellis2 source on new A100: `/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/repos/TRELLIS.2`
- Existing MeshVAE/Trellis env hints: `/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/PATHS.new_a100.env`
- Existing project docs mirror for MeshVAE/Trellis context: `/mnt/beegfs/ruocheng/trellis2_michelangelo_bakeoff/docs/agentdoc_mirror`

# Current Question

Can a frozen Trellis2-style structured 3D flow generator preserve transformed procedural scaffolds while improving geometry/material naturalness enough to justify a new recursive sampling method?

