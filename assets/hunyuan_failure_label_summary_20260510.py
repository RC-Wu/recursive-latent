#!/usr/bin/env python3
"""Summarize Hunyuan full-pool topology metrics into claim-safe labels."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "results/publication_hunyuan_recursive_guides_20260510/hunyuan_fullpool_topology_metrics_20260510.csv"
OUT_CSV = ROOT / "results/publication_hunyuan_recursive_guides_20260510/hunyuan_fullpool_failure_labels_20260510.csv"
OUT_JSON = ROOT / "results/publication_hunyuan_recursive_guides_20260510/hunyuan_fullpool_failure_labels_20260510.json"


VISUAL_NOTES = {
    "vine_lsystem_grammar": "curled filament cluster; poor grammar-readable vine scaffold despite importable mesh",
    "pyrite_lattice": "cage/block hybrid; high occupancy LCR but no explicit lattice grammar state",
    "coral_frontier": "block-like coral/frontier mass; high occupancy LCR but one-shot solid does not expose typed recursive branches",
    "branch_ornament": "fragmented ornament-like response; many raw/occupancy components",
    "branch_tree": "severely fragmented branch/tree response; low occupancy LCR",
    "radial_ornament": "severely fragmented radial response; very low occupancy LCR",
    "root_network": "partial root-network mass; many components and medium occupancy LCR",
    "tree_crown": "fragmented tree-crown response; low occupancy LCR",
}


def label_row(row: dict[str, str]) -> tuple[str, str]:
    raw = int(float(row["component_count"]))
    occ = int(float(row["occupancy_component_count_6n"]))
    lcr = float(row["primary_largest_component_ratio"])
    name = row["label"]
    if name in {"vine_lsystem_grammar", "branch_tree", "radial_ornament", "tree_crown"} or lcr < 0.2:
        return "fragmented_or_filamentary_one_shot", "Low occupancy LCR or visibly filamentary/fragmented one-shot response."
    if name in {"pyrite_lattice", "coral_frontier"}:
        return "one_shot_category_match_without_recursive_state", "Importable one-shot mesh; high occupancy LCR does not imply grammar-readable recursive state."
    if raw > 1000 or occ > 100:
        return "multi_component_generic_shape", "Many face/occupancy components; useful as broad generated-pool evidence, not a main positive."
    if lcr >= 0.99 and occ <= 1:
        return "generic_connected_one_shot_pending_semantics", "Connected proxy is high, but semantic/recursive-state correctness is unverified."
    return "one_shot_pending_visual_label", "Needs visual label before paper claim."


def main() -> None:
    rows = list(csv.DictReader(METRICS.open()))
    out_rows = []
    for row in rows:
        failure, reason = label_row(row)
        out_rows.append(
            {
                "case_id": row["label"],
                "vertices": row["vertices"],
                "faces": row["faces"],
                "raw_component_count": row["component_count"],
                "occupancy_component_count_6n": row["occupancy_component_count_6n"],
                "LCR": row["primary_largest_component_ratio"],
                "failure_label": failure,
                "label_reason": reason,
                "visual_note": VISUAL_NOTES.get(row["label"], "visual QA needed before strong claim"),
                "claim_safe_status": "generated_import_render_topology_QA_done_pending_semantic_review",
            }
        )
    fieldnames = list(out_rows[0].keys()) if out_rows else []
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)
    OUT_JSON.write_text(json.dumps(out_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"rows": len(out_rows), "csv": str(OUT_CSV), "json": str(OUT_JSON)}, indent=2))


if __name__ == "__main__":
    main()
