# V15 plant/root/IFS strict one-to-one remote generation plan

Date: 2026-05-10

## Goal

V15 targets the remaining strict visual-matched gaps after the V6/V8 family
audit and the V13/V14 DLA/coral/crystal branch.  Scope is limited to plant,
tree, root, and IFS/transform cases:

- L-system pine canopy, root fan, climbing vine.
- Space-colonization tree crown, root network, bush shell.
- IFS branch tree, radial ornament, lattice/crystal-like transform.

The final comparison cases must be generated fresh on `a100-2` using GPUs
`4/5/6/7`.  Local dry-run geometry is only the Trellis2 input, not a selected
final result.

## Design rationale

Prior connected plant/root/tree cases were acceptable by connectivity metrics
but often read as thin rods or bare scaffolds.  The V15 generator therefore
keeps the same category, silhouette, recursive depth, and growth/transform
mode, while changing the input support to:

- smooth connected tapered branch/root/transform support;
- attached needle, leaf, shell, and tendril cards for plant cases;
- connected fine root hairs/rootlets for root cases;
- bridged radial rings and small copy bridges for IFS transform cases;
- no grape-like sphere clusters, no voxel blocks, no pure rod scaffold.

IFS radial and lattice cases receive explicit ring/copy bridges so Trellis2 is
conditioned on a single coherent ornament/lattice instead of fragmented islands.

## Generated artifacts

Generator:

```bash
python3 assets/strict_visual_matched_cases_v15_plants_ifs_20260510.py \
  --root /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507 \
  --out /mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/inputs/strict_visual_matched_cases_v15_plants_ifs_20260510 \
  --seed 20260510
```

Expected files:

- `manifest.csv` and `manifest.json`
- `initial_metrics.csv` and `initial_metrics.json`
- `a100-2_cases.txt`
- `gpu4_cases.txt`, `gpu5_cases.txt`, `gpu6_cases.txt`, `gpu7_cases.txt`
- `gpu4567_cases.txt`
- per-case OBJ and metadata JSON
- guide PNG images under `_guides/`

## Remote launch protocol

Launcher:

```bash
bash assets/launch_strict_visual_matched_texture_v15_plants_ifs_20260510.sh
```

The launcher defaults to:

- `ROOT=/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507`
- `RUN=strict_visual_matched_texture_v15_plants_ifs_20260510`
- `INPUT_NAME=strict_visual_matched_cases_v15_plants_ifs_20260510`
- `SEED=20260510`
- `STEPS=8`
- `TEXTURE_SIZE=2048`

Cache and temp directories remain under `ROOT/cache` and `ROOT/hf_home`;
`/tmp/devshm` is intentionally unused.  Worker mode reads
`gpu${gpu}_cases.txt`, uses `CUDA_VISIBLE_DEVICES="$gpu"`, and skips a target
when `summary.json` already contains `"status": "ok"`.

## QA gates before remote texture generation

The local dry run must pass:

```bash
python3 -m pytest -q tests/test_strict_visual_matched_cases_v15_plants_ifs_20260510.py
```

Required gates:

- exactly 9 cases matching the listed traditional targets;
- only `L-system`, `Space colonization`, and `IFS/transform` families;
- all rows target `a100-2` and GPUs `4/5/6/7`;
- every OBJ has one main component or LCR >= `0.999` before Trellis2;
- per-case metadata records strict generation policy and root source;
- controls record smooth connected support, tapered branches, attached detail,
  no voxel blocks, no grape-ball primitives, and no rod-only scaffold.
