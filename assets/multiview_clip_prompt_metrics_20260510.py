#!/usr/bin/env python3
"""Compute lightweight CLIP prompt-image scores for rendered case views.

The script is intentionally render-based: it scores the same images that enter
paper contact sheets rather than point clouds or internal meshes.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


DEFAULT_PROMPTS = {
    "lsystem_branch_baseline": "a recursive branching plant structure on a white background",
    "ours_vine_stage5": "a textured recursive vine root plant asset on a white background",
    "sc_tree_canopy_baseline": "a space colonization tree canopy with branching structure on a white background",
    "ours_vine_root": "a textured recursive root and vine asset on a white background",
    "dla_cluster_baseline": "a diffusion limited aggregation coral cluster on a white background",
    "ours_coral_octopus": "a textured organic coral branching asset on a white background",
    "ifs_branch_tree_baseline": "an iterated transform recursive branching tree on a white background",
    "ours_pyrite_lattice": "a textured pyrite crystal lattice recursive asset on a white background",
}


def parse_case_file(path: Path) -> list[str]:
    labels: list[str] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        labels.append(line.split("=", 1)[0])
    return labels


def image_paths(render_dir: Path, label: str, views: list[str]) -> list[Path]:
    paths = []
    for view in views:
        candidate = render_dir / f"{label}_{view}.png"
        if candidate.exists():
            paths.append(candidate)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-file", type=Path, required=True)
    parser.add_argument("--render-dir", type=Path, required=True)
    parser.add_argument("--out-prefix", type=Path, required=True)
    parser.add_argument("--model", default="openai/clip-vit-base-patch32")
    parser.add_argument("--views", nargs="+", default=["iso", "front"])
    args = parser.parse_args()

    args.out_prefix.parent.mkdir(parents=True, exist_ok=True)
    labels = parse_case_file(args.case_file)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = CLIPProcessor.from_pretrained(args.model)
    model = CLIPModel.from_pretrained(args.model).to(device).eval()

    rows = []
    with torch.no_grad():
        for label in labels:
            prompt = DEFAULT_PROMPTS.get(label, label.replace("_", " "))
            paths = image_paths(args.render_dir, label, args.views)
            if not paths:
                rows.append(
                    {
                        "label": label,
                        "prompt": prompt,
                        "view_count": 0,
                        "mean_clip_cosine": "",
                        "min_clip_cosine": "",
                        "max_clip_cosine": "",
                    }
                )
                continue

            images = [Image.open(p).convert("RGB") for p in paths]
            inputs = processor(text=[prompt], images=images, return_tensors="pt", padding=True)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            image_features = model.get_image_features(pixel_values=inputs["pixel_values"])
            text_features = model.get_text_features(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            scores = (image_features @ text_features.T).squeeze(1).detach().cpu()
            rows.append(
                {
                    "label": label,
                    "prompt": prompt,
                    "view_count": len(paths),
                    "mean_clip_cosine": float(scores.mean().item()),
                    "min_clip_cosine": float(scores.min().item()),
                    "max_clip_cosine": float(scores.max().item()),
                }
            )

    csv_path = args.out_prefix.with_suffix(".csv")
    json_path = args.out_prefix.with_suffix(".json")
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    print(f"[done] {csv_path}")
    print(f"[done] {json_path}")


if __name__ == "__main__":
    main()
