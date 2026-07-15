#!/usr/bin/env python3
"""Prepare the Lane D pure-white hero zoom manifest.

This script does not render. It writes a manifest consumed by
scripts/figures/matched_camera_zoom_render_20260510.py so hero candidates can be
re-rendered with nested camera zooms on a pure-white background.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


CASES = [
    {
        "label": "hero_bismuth_hopper_hq",
        "mesh": "visuals/connected_scaffold_v2_textured_glb_hq_20260509/bismuth_hopper_bismuth_hq_steps8_tex2048_xformers/textured.glb",
        "material_mode": "preserve",
        "zoom_levels": 3,
        "category": "bismuth",
        "priority": "hero_candidate",
    },
    {
        "label": "hero_pyrite_lattice_hq",
        "mesh": "visuals/connected_scaffold_v2_textured_glb_hq_20260509/pyrite_lattice_pyrite_hq_steps8_tex2048_xformers/textured.glb",
        "material_mode": "preserve",
        "zoom_levels": 3,
        "category": "pyrite",
        "priority": "hero_candidate",
    },
    {
        "label": "hero_coral_octopus_hq",
        "mesh": "visuals/connected_scaffold_v2_textured_glb_hq_20260509/volumetric_dla_coral_octopus_hq_steps8_tex2048_xformers/textured.glb",
        "material_mode": "preserve",
        "zoom_levels": 3,
        "category": "coral",
        "priority": "hero_candidate",
    },
    {
        "label": "hero_fig24_pine_canopy_bark_leaf",
        "mesh": "visuals/strict_matched_root_stamped_20260510/lsys_pine_canopy_d5__rootstamped_tree_compete/root_stamped_candidate.glb",
        "material_mode": "preserve",
        "zoom_levels": 3,
        "category": "fig24_root_leaf",
        "priority": "fig24_candidate",
    },
    {
        "label": "hero_fig24_root_fan_bark",
        "mesh": "visuals/strict_matched_root_stamped_20260510/lsys_root_fan_d5__rootstamped_vine_roots/root_stamped_candidate.glb",
        "material_mode": "preserve",
        "zoom_levels": 3,
        "category": "fig24_root_leaf",
        "priority": "fig24_candidate",
    },
    {
        "label": "hero_fig24_climbing_vine_leaf",
        "mesh": "visuals/strict_matched_root_stamped_20260510/lsys_climbing_vine_d6__rootstamped_vine_stage5/root_stamped_candidate.glb",
        "material_mode": "preserve",
        "zoom_levels": 3,
        "category": "fig24_root_leaf",
        "priority": "alternate_fig24_candidate",
    },
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "case_gallery_for_user_20260510_gen3d_baseline_ablation" / "hero_zoom_manifest_20260510.json",
    )
    parser.add_argument("--absolute", action="store_true", help="Write absolute mesh paths.")
    args = parser.parse_args()

    cases = []
    missing = []
    for item in CASES:
        mesh = ROOT / item["mesh"]
        if not mesh.exists():
            missing.append(str(mesh))
        record = dict(item)
        record["mesh"] = str(mesh if args.absolute else Path(item["mesh"]))
        cases.append(record)

    payload = {
        "created_for": "Lane D pure-white nested hero zoom preparation",
        "renderer": "scripts/figures/matched_camera_zoom_render_20260510.py",
        "requirements": {
            "background": "pure white",
            "platform": "none",
            "in_image_text": "none",
            "labels": "subfigure labels below only during composition",
            "zoom_policy": "camera re-render, not 2D crop",
        },
        "cases": cases,
        "missing_meshes": missing,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(args.out)
    if missing:
        print("missing:")
        for path in missing:
            print(path)


if __name__ == "__main__":
    main()
