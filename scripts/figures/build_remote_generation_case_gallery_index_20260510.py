#!/usr/bin/env python3
"""Build a lightweight index for strict remote-generation gallery review.

The script scans local `visuals/` and `results/` folders for strict matched
remote-generation artifacts, then writes markdown and CSV indexes. It links to
existing files by default and only copies contact sheets when explicitly asked.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Iterable, NamedTuple


MD_NAME = "remote_generation_case_gallery_index_20260510.md"
CSV_NAME = "remote_generation_case_gallery_index_20260510.csv"
READINESS_ORDER = ("paper-candidate", "diagnostic-only", "reject/negative")
STRICT_MARKERS = (
    "strict_visual_matched_texture",
    "strict_matched_pair",
    "strict_matched_psrslg_proxy",
    "strict_matched_traditional_targets",
)


class GalleryEntry(NamedTuple):
    series: str
    family: str
    readiness: str
    kind: str
    name: str
    path: str
    source_dir: str
    notes: str


def repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def detect_series(text: str) -> str:
    match = re.search(r"(?i)(?:\bv(\d+[a-z]?)\b|_v(\d+[a-z]?)(?:_|$))", text)
    if match:
        value = match.group(1) or match.group(2)
        return f"V{value.upper()}"
    if "strict_matched_pair" in text:
        return "PAIR"
    if "traditional_targets" in text:
        return "TRADITIONAL"
    if "proxy" in text:
        return "PROXY"
    return "UNSERIED"


def detect_family(text: str, manifest_family: str = "") -> str:
    if manifest_family:
        normalized = manifest_family.strip()
        if normalized:
            if normalized.lower() in {"dla", "dla/frontier", "frontier"}:
                return "DLA/frontier"
            return normalized
    lower = text.lower()
    if "strict_visual_matched_texture" in lower:
        return "DLA/frontier"
    if any(token in lower for token in ("dla", "coral", "frontier", "staghorn", "crystal")):
        return "DLA/frontier"
    if any(token in lower for token in ("lsys", "l-system", "lsystem", "pine", "vine", "root")):
        return "L-system/tree/root"
    if any(token in lower for token in ("space_colonization", "sc_tree", "sc_root", "bush")):
        return "Space colonization"
    if any(token in lower for token in ("ifs", "transform", "radial", "lattice", "pyrite")):
        return "IFS/transform"
    return "mixed/unknown"


def detect_readiness(text: str, row: dict[str, str] | None = None) -> str:
    row = row or {}
    explicit = " ".join(
        row.get(key, "")
        for key in (
            "readiness",
            "recommended_use",
            "verdict",
            "qa_status",
            "status",
            "case_role",
            "generation_policy",
        )
    ).lower()
    lower = f"{text} {explicit}".lower()
    if any(token in lower for token in ("reject", "negative", "fail", "do_not_claim")):
        return "reject/negative"
    if any(token in lower for token in ("paper-candidate", "paper_safe", "main_candidate")):
        return "paper-candidate"
    return "diagnostic-only"


def is_relevant_path(path: Path) -> bool:
    joined = path.as_posix()
    return any(marker in joined for marker in STRICT_MARKERS)


def iter_contact_sheets(repo_root: Path) -> Iterable[Path]:
    visuals = repo_root / "visuals"
    if not visuals.exists():
        return []
    candidates = []
    for path in visuals.rglob("*"):
        if not path.is_file():
            continue
        name = path.name.lower()
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        if ("contact" in name or "sheet" in name) and is_relevant_path(path):
            candidates.append(path)
    return sorted(candidates)


def iter_manifests(repo_root: Path) -> Iterable[Path]:
    candidates = []
    for root_name in ("results", "visuals"):
        root = repo_root / root_name
        if not root.exists():
            continue
        for path in root.rglob("manifest.csv"):
            if is_relevant_path(path):
                candidates.append(path)
    return sorted(candidates)


def read_manifest_entries(path: Path, repo_root: Path) -> list[GalleryEntry]:
    entries = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            case_id = row.get("case_id") or row.get("name") or path.parent.name
            text = " ".join([path.as_posix(), case_id, row.get("traditional_target", "")])
            entries.append(
                GalleryEntry(
                    series=detect_series(text),
                    family=detect_family(text, row.get("family", "")),
                    readiness=detect_readiness(text, row),
                    kind="manifest-case",
                    name=case_id,
                    path=repo_relative(path, repo_root),
                    source_dir=repo_relative(path.parent, repo_root),
                    notes=manifest_notes(row),
                )
            )
    return entries


def manifest_notes(row: dict[str, str]) -> str:
    fields = []
    for key in ("traditional_target", "case_role", "generation_policy", "why_matches_traditional"):
        value = row.get(key, "").strip()
        if value:
            fields.append(f"{key}={value}")
    return "; ".join(fields)


def contact_sheet_entry(path: Path, repo_root: Path) -> GalleryEntry:
    text = path.as_posix()
    return GalleryEntry(
        series=detect_series(text),
        family=detect_family(text),
        readiness=detect_readiness(text),
        kind="contact-sheet",
        name=path.name,
        path=repo_relative(path, repo_root),
        source_dir=repo_relative(path.parent, repo_root),
        notes="link-only; source image not copied unless --copy-contact-sheets is set",
    )


def build_index(
    repo_root: str | Path,
    output_dir: str | Path,
    *,
    copy_contact_sheets: bool = False,
) -> list[GalleryEntry]:
    repo_root = Path(repo_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    for manifest in iter_manifests(repo_root):
        entries.extend(read_manifest_entries(manifest, repo_root))
    entries.extend(contact_sheet_entry(path, repo_root) for path in iter_contact_sheets(repo_root))
    entries = sorted(set(entries), key=lambda item: (item.family, item.readiness, item.series, item.kind, item.name))

    if copy_contact_sheets:
        copy_dir = output_dir / "contact_sheets"
        copy_dir.mkdir(parents=True, exist_ok=True)
        copied_entries = []
        for entry in entries:
            if entry.kind != "contact-sheet":
                copied_entries.append(entry)
                continue
            src = repo_root / entry.path
            safe_name = f"{entry.series}_{src.name}"
            dst = copy_dir / safe_name
            shutil.copy2(src, dst)
            copied_entries.append(entry._replace(notes=f"{entry.notes}; copied_to={dst.relative_to(output_dir).as_posix()}"))
        entries = copied_entries

    write_csv(entries, output_dir / CSV_NAME)
    write_markdown(entries, output_dir / MD_NAME)
    return entries


def write_csv(entries: list[GalleryEntry], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(GalleryEntry._fields))
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry._asdict())


def write_markdown(entries: list[GalleryEntry], path: Path) -> None:
    grouped: dict[str, dict[str, list[GalleryEntry]]] = defaultdict(lambda: defaultdict(list))
    for entry in entries:
        grouped[entry.family][entry.readiness].append(entry)

    lines = [
        "# Strict remote-generation case gallery index",
        "",
        "Generated from local `visuals/` and `results/` folders. This is an index of pulled artifacts; it does not launch remote jobs and does not copy large files by default.",
        "",
        "| readiness | meaning |",
        "|---|---|",
        "| paper-candidate | locally indexed as a candidate for user review; still needs final strict audit before paper use |",
        "| diagnostic-only | useful evidence, protocol calibration, or boundary material; not a final claim |",
        "| reject/negative | failure, negative, or do-not-claim material |",
        "",
    ]
    for family in sorted(grouped):
        lines.extend([f"## {family}", ""])
        readiness_keys = [key for key in READINESS_ORDER if key in grouped[family]]
        readiness_keys.extend(sorted(set(grouped[family]) - set(readiness_keys)))
        for readiness in readiness_keys:
            lines.extend([f"### {readiness}", "", "| series | kind | name | path | notes |", "|---|---|---|---|---|"])
            for entry in grouped[family][readiness]:
                lines.append(
                    f"| {entry.series} | {entry.kind} | {entry.name} | `{entry.path}` | {entry.notes or ''} |"
                )
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--copy-contact-sheets", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    entries = build_index(
        args.repo_root,
        args.output_dir,
        copy_contact_sheets=args.copy_contact_sheets,
    )
    print(f"wrote {len(entries)} entries to {args.output_dir / MD_NAME} and {args.output_dir / CSV_NAME}")


if __name__ == "__main__":
    main()
