#!/usr/bin/env python3
"""Create a matched-camera render manifest for real-case ablation GLBs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
DEFAULT_INPUT_MANIFEST = ROOT / "results" / "real_case_ablation_inputs_20260512" / "manifest.json"
DEFAULT_GLB_DIR = ROOT / "results" / "real_case_ablation_texture_20260512"
DEFAULT_OUT = ROOT / "results" / "real_case_ablation_texture_20260512" / "render_manifest_20260512.json"


def load_rows(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_glb(glb_dir: Path, row: dict, steps: int, texture_size: int) -> Path:
    name = f"{row['label']}_steps{steps}_tex{texture_size}_seed{row['seed']}_xformers"
    return glb_dir / name / "textured.glb"


def material_mode(row: dict) -> str:
    # Preserve Trellis2 material output in the final render.  The hint is kept
    # in the manifest only for visual QA and possible neutral-material reruns.
    return "preserve"


def rotation_for(row: dict) -> list[float] | None:
    case_id = str(row["case_id"])
    if "pyrite" in case_id:
        return [0.0, 0.0, 0.0]
    if "bough" in case_id:
        return [0.0, 0.0, 0.0]
    return None


def zoom_divisor(row: dict) -> float:
    if row["experiment"] == "projection":
        return 2.85
    return 3.00


def build(args: argparse.Namespace) -> dict:
    rows = load_rows(args.input_manifest)
    cases: list[dict] = []
    missing: list[str] = []
    for row in rows:
        glb = expected_glb(args.glb_dir, row, args.steps, args.texture_size)
        if not glb.exists():
            missing.append(str(glb))
            continue
        item = {
            "label": row["label"],
            "mesh": str(glb),
            "plan_mesh": row["mesh_path"],
            "material_mode": material_mode(row),
            "zoom_levels": 1,
            "zoom_divisor": zoom_divisor(row),
            "experiment": row["experiment"],
            "case_id": row["case_id"],
            "case_label": row["case_label"],
            "variant": row["variant"],
            "variant_label": row["variant_label"],
            "source_case": row["source_case"],
            "provenance": {
                "input_manifest": str(args.input_manifest),
                "source_mesh": row.get("source_mesh", ""),
                "derived_obj": row["mesh_path"],
                "remote_glb": str(glb),
                "seed": int(row["seed"]),
                "mutation_note": row["mutation_note"],
                "contract": "real source OBJ -> matched ablation OBJ -> Trellis2 textured GLB -> white-background camera render",
            },
        }
        rot = rotation_for(row)
        if rot is not None:
            item["rotation_deg"] = rot
        cases.append(item)
    payload = {
        "schema": "real_case_ablation_render_manifest_20260512",
        "cases": cases,
        "missing": missing,
        "expected_total": len(rows),
        "found_total": len(cases),
        "render_contract": "All cases point to real Trellis2 textured GLBs; PPTX consumes only rendered PNG panels derived from this manifest.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-manifest", type=Path, default=DEFAULT_INPUT_MANIFEST)
    parser.add_argument("--glb-dir", type=Path, default=DEFAULT_GLB_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--texture-size", type=int, default=2048)
    args = parser.parse_args()
    print(json.dumps(build(args), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
