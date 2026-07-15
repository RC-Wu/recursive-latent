# Offline Mesh Metrics Pipeline 20260513

This pipeline is for local metrics discovery only. It does not call external scoring APIs and does not require an API key in dry-run mode.

## Workflow

```bash
python3 scripts/metrics_mesh_pipeline_20260513.py --dry-run --limit 12
python3 scripts/metrics_mesh_pipeline_20260513.py --write-manifest --limit 12
python3 scripts/metrics_mesh_pipeline_validate_20260513.py drafts/metrics_mesh_pipeline_dryrun_20260513.json
```

The generated manifest is `drafts/metrics_mesh_pipeline_dryrun_20260513.json`.

## What It Discovers

- Local metric tables under `../results` and `../visuals` whose filenames contain `metric` and end in `.csv` or `.json`.
- Local mesh assets under the same roots with `.glb`, `.gltf`, `.obj`, `.ply`, `.stl`, or `.off` extensions.
- For CSV tables, the script reports reusable mesh metric columns such as `vertices`, `faces`, component counts, occupancy LCR, boundary/nonmanifold columns, watertight flags, triangle quality, surface area, and bounding volume when present.
- For OBJ files, the script does a lightweight text scan for vertex and face counts.
- For GLB/other mesh files, dry-run records asset presence and file size only unless an existing metrics table already contains richer values.

## Boundary

The pipeline reports deterministic metrics already present in local CSV/JSON/mesh assets. Visual scoring is outside this offline discovery pass and is not part of the active experiment section.
