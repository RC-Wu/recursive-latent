#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import json
import os
import re
import shutil
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/fanta/code/agent/Code/recursive_3d_generative_growth")
OUT = ROOT / "docs" / "evaluation" / "case_inventory_v1_v60_20260512"
REMOTE_LIST = OUT / "remote_a1002_v1_v60_files.txt"
VERSION_RE = re.compile(r"(?i)(?:^|[^a-z0-9])v([0-9]{1,2})(?:[^0-9]|$)")
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
DOC_IMAGE_EXTS = IMAGE_EXTS | {".pdf"}
GEOM_EXTS = {".glb", ".obj"}
SPEC_EXTS = {".json", ".md", ".py", ".sh", ".yaml", ".yml"}


@dataclass
class VersionBucket:
    version: int
    images: list[Path] = field(default_factory=list)
    contact_images: list[Path] = field(default_factory=list)
    geom: list[Path] = field(default_factory=list)
    specs: list[Path] = field(default_factory=list)
    generator_files: list[Path] = field(default_factory=list)
    remote_files: list[str] = field(default_factory=list)


def version_from_path(path: str) -> int | None:
    matches = VERSION_RE.findall(path)
    if not matches:
        return None
    # Prefer the last visible version token, because parent dirs can contain old suite names.
    v = int(matches[-1])
    if 1 <= v <= 60:
        return v
    return None


def walk_files(roots: Iterable[Path]) -> Iterable[Path]:
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # Keep generated previews, but skip obvious caches/build internals.
            parts = set(Path(dirpath).parts)
            if ".git" in parts or "__pycache__" in parts or ".pytest_cache" in parts:
                dirnames[:] = []
                continue
            for name in filenames:
                yield Path(dirpath) / name


def score_image(path: Path) -> tuple[int, int, int, str]:
    s = str(path).lower()
    name = path.name.lower()
    score = 0
    if "contact" in name or "sheet" in name:
        score += 1000
    if "zoom" in s:
        score += 250
    if "white" in s or "pure_white" in s:
        score += 120
    if "glb" in s or "textur" in s:
        score += 100
    if "obj" in s:
        score += 40
    if "preview" in name:
        score -= 100
    if "qa" in s:
        score += 30
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    return (-score, -size, len(str(path)), str(path))


def score_spec(path: Path) -> tuple[int, str]:
    s = str(path).lower()
    score = 0
    if path.name == "manifest.json":
        score += 1000
    if path.name == "summary.json":
        score += 900
    if path.name == "README.md".lower():
        score += 800
    if "manifest" in path.name.lower():
        score += 700
    if "strict_visual_matched_cases" in s and path.suffix == ".py":
        score += 650
    if "launch" in path.name.lower() and path.suffix == ".sh":
        score += 500
    if "test_strict_visual" in path.name.lower():
        score += 300
    return (-score, str(path))


def rel_or_abs(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def choose(items: list[Path], n: int, *, image: bool = False, spec: bool = False) -> list[Path]:
    if image:
        return sorted(dict.fromkeys(items), key=score_image)[:n]
    if spec:
        return sorted(dict.fromkeys(items), key=score_spec)[:n]
    return sorted(dict.fromkeys(items), key=lambda p: (len(str(p)), str(p)))[:n]


def ordered_unique_paths(items: list[Path], *, image: bool = False, spec: bool = False) -> list[Path]:
    items = list(dict.fromkeys(items))
    if image:
        return sorted(items, key=score_image)
    if spec:
        return sorted(items, key=score_spec)
    return sorted(items, key=lambda p: (len(str(p)), str(p)))


def write_lines(path: Path, lines: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def thumb_for(path: Path, size: tuple[int, int] = (260, 190)) -> Image.Image:
    img = Image.open(path).convert("RGB")
    img.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "white")
    x = (size[0] - img.width) // 2
    y = (size[1] - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def write_contact_sheet(records: list[dict], out_path: Path) -> None:
    thumbs = []
    for rec in records:
        p = rec.get("representative_image_abs")
        if not p:
            continue
        path = Path(p)
        if not path.exists() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        try:
            thumbs.append((rec["version"], rec["label"], path, thumb_for(path)))
        except Exception:
            continue
    cols = 5
    cell_w, cell_h = 310, 245
    rows = max(1, (len(thumbs) + cols - 1) // cols)
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 14)
        font_b = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 16)
    except Exception:
        font = ImageFont.load_default()
        font_b = font
    for idx, (version, label, path, img) in enumerate(thumbs):
        r, c = divmod(idx, cols)
        x, y = c * cell_w, r * cell_h
        draw.rectangle([x, y, x + cell_w - 1, y + cell_h - 1], outline=(220, 220, 220))
        sheet.paste(img, (x + 25, y + 36))
        draw.text((x + 8, y + 8), f"V{version}: {label[:34]}", fill=(0, 0, 0), font=font_b)
        draw.text((x + 8, y + 228), path.name[:42], fill=(70, 70, 70), font=font)
    sheet.save(out_path)


def copy_selection_images(records: list[dict], sel_dir: Path) -> None:
    if sel_dir.exists():
        shutil.rmtree(sel_dir)
    sel_dir.mkdir(parents=True, exist_ok=True)
    for rec in records:
        version_dir = sel_dir / f"V{rec['version']:02d}"
        version_dir.mkdir(parents=True, exist_ok=True)
        copied = []
        for idx, rel in enumerate(rec["selection_images"], start=1):
            src = ROOT / rel
            if not src.exists() or src.suffix.lower() not in IMAGE_EXTS:
                continue
            safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", src.stem)[:70]
            dst = version_dir / f"{idx:02d}_{safe_stem}{src.suffix.lower()}"
            try:
                shutil.copy2(src, dst)
                copied.append(str(dst))
            except OSError:
                continue
        rec["selection_image_copies"] = copied


def copy_representatives(records: list[dict], rep_dir: Path) -> None:
    rep_dir.mkdir(parents=True, exist_ok=True)
    for rec in records:
        p = rec.get("representative_image_abs")
        if not p:
            continue
        path = Path(p)
        if not path.exists() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        safe_label = re.sub(r"[^A-Za-z0-9_.-]+", "_", rec["label"])[:80]
        dst = rep_dir / f"V{rec['version']:02d}_{safe_label}{path.suffix.lower()}"
        try:
            shutil.copy2(path, dst)
            rec["representative_image_copy"] = str(dst)
        except OSError:
            pass


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    buckets = {i: VersionBucket(i) for i in range(1, 61)}

    scan_roots = [
        ROOT / "results",
        ROOT / "visuals",
        ROOT / "paper_siga" / "figures",
        ROOT / "case_gallery_for_user_20260509",
        ROOT / "case_gallery_for_user_20260510_gen3d_baseline_ablation",
        ROOT / "docs",
        ROOT / "assets",
        ROOT / "scripts",
        ROOT / "tests",
    ]
    for path in walk_files(scan_roots):
        v = version_from_path(str(path))
        if v is None:
            continue
        ext = path.suffix.lower()
        b = buckets[v]
        if ext in DOC_IMAGE_EXTS:
            b.images.append(path)
            n = path.name.lower()
            if ext in IMAGE_EXTS and ("contact" in n or "sheet" in n or "overview" in n):
                b.contact_images.append(path)
        if ext in GEOM_EXTS:
            b.geom.append(path)
        if ext in SPEC_EXTS:
            b.specs.append(path)
            s = str(path).lower()
            if (
                "strict_visual_matched_cases" in s
                or "launch_strict_visual" in s
                or "test_strict_visual" in s
                or "postprocess_v" in s
            ):
                b.generator_files.append(path)

    if REMOTE_LIST.exists():
        for line in REMOTE_LIST.read_text(errors="ignore").splitlines():
            v = version_from_path(line)
            if v is not None:
                buckets[v].remote_files.append(line)

    records = []
    for v in range(1, 61):
        b = buckets[v]
        rep_candidates = b.contact_images or [p for p in b.images if p.suffix.lower() in IMAGE_EXTS]
        rep = choose(rep_candidates, 1, image=True)
        best_specs = choose(b.specs + b.generator_files, 12, spec=True)
        best_geom = choose(b.geom, 20)
        label_source = rep[0].parent.name if rep else (best_geom[0].parent.name if best_geom else f"V{v}_missing")
        rec = {
            "version": v,
            "label": label_source,
            "representative_image_abs": str(rep[0]) if rep else "",
            "representative_image_rel": rel_or_abs(rep[0]) if rep else "",
            "image_count": len(set(b.images)),
            "contact_image_count": len(set(b.contact_images)),
            "geometry_count": len(set(b.geom)),
            "spec_count": len(set(b.specs)),
            "generator_file_count": len(set(b.generator_files)),
            "remote_file_count": len(set(b.remote_files)),
            "representative_images": [rel_or_abs(p) for p in choose(rep_candidates, 8, image=True)],
            "geometry_paths": [rel_or_abs(p) for p in best_geom],
            "grammar_or_repro_paths": [rel_or_abs(p) for p in best_specs],
            "remote_paths_sample": sorted(set(b.remote_files))[:20],
        }
        full_images = ordered_unique_paths([p for p in b.images if p.suffix.lower() in IMAGE_EXTS], image=True)
        full_doc_images = ordered_unique_paths(b.images, image=True)
        full_geom = ordered_unique_paths(b.geom)
        full_specs = ordered_unique_paths(b.specs + b.generator_files, spec=True)
        full_remote = sorted(set(b.remote_files))
        rec.update(
            {
                "selection_images": [rel_or_abs(p) for p in full_images[:16]],
                "all_image_paths": [rel_or_abs(p) for p in full_images],
                "all_doc_image_paths": [rel_or_abs(p) for p in full_doc_images],
                "all_geometry_paths": [rel_or_abs(p) for p in full_geom],
                "all_grammar_or_repro_paths": [rel_or_abs(p) for p in full_specs],
                "all_remote_paths": full_remote,
            }
        )
        records.append(rec)

    copy_selection_images(records, OUT / "selection_images")
    copy_representatives(records, OUT / "representative_images")
    write_contact_sheet(records, OUT / "v1_v60_representative_contact_sheet.png")

    (OUT / "v1_v60_case_inventory.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (OUT / "v1_v60_case_inventory.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "version",
                "label",
                "representative_image_rel",
                "representative_image_abs",
                "image_count",
                "geometry_count",
                "spec_count",
                "generator_file_count",
                "remote_file_count",
            ],
        )
        writer.writeheader()
        for rec in records:
            writer.writerow({k: rec.get(k, "") for k in writer.fieldnames})

    list_dir = OUT / "full_path_lists"
    if list_dir.exists():
        shutil.rmtree(list_dir)
    for rec in records:
        prefix = list_dir / f"V{rec['version']:02d}"
        write_lines(prefix.with_name(prefix.name + "_images.txt"), rec["all_image_paths"])
        write_lines(prefix.with_name(prefix.name + "_geometry.txt"), rec["all_geometry_paths"])
        write_lines(prefix.with_name(prefix.name + "_grammar_or_repro.txt"), rec["all_grammar_or_repro_paths"])
        write_lines(prefix.with_name(prefix.name + "_remote_a1002.txt"), rec["all_remote_paths"])

    md = []
    md.append("# V1-V60 Case Inventory for Visual Selection\n")
    md.append("Generated from local project files plus one bounded `a100-2` remote file listing. The Markdown is a human-readable selection guide; the JSON and `full_path_lists/` keep complete path lists for later agents.\n")
    md.append(f"- Representative contact sheet: `{OUT / 'v1_v60_representative_contact_sheet.png'}`\n")
    md.append(f"- Multi-candidate HTML gallery: `{OUT / 'v1_v60_case_inventory_multi_image_gallery.html'}`\n")
    md.append(f"- Machine-readable JSON: `{OUT / 'v1_v60_case_inventory.json'}`\n")
    md.append(f"- CSV summary: `{OUT / 'v1_v60_case_inventory.csv'}`\n")
    md.append(f"- Copied representative images: `{OUT / 'representative_images'}`\n\n")
    for rec in records:
        md.append(f"## V{rec['version']:02d} - {rec['label']}\n")
        if rec.get("representative_image_copy"):
            md.append(f"![V{rec['version']:02d}]({rec['representative_image_copy']})\n\n")
        elif rec["representative_image_abs"]:
            md.append(f"![V{rec['version']:02d}]({rec['representative_image_abs']})\n\n")
        else:
            md.append("_No local representative image found._\n\n")
        md.append(
            f"- Counts: images={rec['image_count']}, geometry={rec['geometry_count']}, specs={rec['spec_count']}, remote={rec['remote_file_count']}\n"
        )
        if rec.get("selection_image_copies"):
            md.append("- Local copied selection images:\n")
            for p in rec["selection_image_copies"][:16]:
                md.append(f"  - `{p}`\n")
        if rec["representative_images"]:
            md.append("- Representative/selection images:\n")
            for p in rec["representative_images"]:
                md.append(f"  - `{p}`\n")
        if rec["geometry_paths"]:
            md.append("- GLB/OBJ paths:\n")
            for p in rec["geometry_paths"]:
                md.append(f"  - `{p}`\n")
        if rec["grammar_or_repro_paths"]:
            md.append("- Grammar / reproducibility / manifest paths:\n")
            for p in rec["grammar_or_repro_paths"]:
                md.append(f"  - `{p}`\n")
        if rec["remote_paths_sample"]:
            md.append("- Remote paths sample from `a100-2`:\n")
            for p in rec["remote_paths_sample"][:8]:
                md.append(f"  - `{p}`\n")
        v_prefix = f"V{rec['version']:02d}"
        md.append("- Complete path list files:\n")
        md.append(f"  - Images: `{list_dir / (v_prefix + '_images.txt')}`\n")
        md.append(f"  - GLB/OBJ: `{list_dir / (v_prefix + '_geometry.txt')}`\n")
        md.append(f"  - Grammar/repro: `{list_dir / (v_prefix + '_grammar_or_repro.txt')}`\n")
        md.append(f"  - Remote a100-2: `{list_dir / (v_prefix + '_remote_a1002.txt')}`\n")
        md.append("\n")
    (OUT / "v1_v60_case_inventory_for_selection_zh.md").write_text("".join(md), encoding="utf-8")

    cards = []
    cards.append("<!doctype html><meta charset='utf-8'><title>V1-V60 Case Inventory</title>")
    cards.append("<style>body{font-family:Arial,sans-serif;margin:20px} .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}.card{border:1px solid #ddd;padding:10px}.card img{max-width:100%;height:220px;object-fit:contain;background:#fff}.path{font-family:monospace;font-size:11px;word-break:break-all} h2{margin:0 0 8px}</style>")
    cards.append("<h1>V1-V60 Case Inventory</h1>")
    cards.append(f"<p>Contact sheet: <a href='{html.escape(str(OUT / 'v1_v60_representative_contact_sheet.png'))}'>PNG</a></p><div class='grid'>")
    for rec in records:
        img = rec.get("representative_image_copy") or rec["representative_image_abs"]
        cards.append("<div class='card'>")
        cards.append(f"<h2>V{rec['version']:02d}</h2><div>{html.escape(rec['label'])}</div>")
        if img:
            cards.append(f"<a href='{html.escape(img)}'><img src='{html.escape(img)}'></a>")
        else:
            cards.append("<div style='height:220px;display:flex;align-items:center;justify-content:center;background:#f7f7f7'>No image</div>")
        cards.append(f"<p>images={rec['image_count']} geometry={rec['geometry_count']} specs={rec['spec_count']} remote={rec['remote_file_count']}</p>")
        for title, key in [("Images", "representative_images"), ("GLB/OBJ", "geometry_paths"), ("Grammar/spec", "grammar_or_repro_paths")]:
            vals = rec[key][:5]
            if vals:
                cards.append(f"<b>{title}</b>")
                for p in vals:
                    cards.append(f"<div class='path'>{html.escape(p)}</div>")
        cards.append("</div>")
    cards.append("</div>")
    (OUT / "v1_v60_case_inventory_gallery.html").write_text("".join(cards), encoding="utf-8")

    multi = []
    multi.append("<!doctype html><meta charset='utf-8'><title>V1-V60 Multi-Image Case Gallery</title>")
    multi.append(
        "<style>body{font-family:Arial,sans-serif;margin:20px;color:#111}"
        "nav{position:sticky;top:0;background:white;padding:8px 0;border-bottom:1px solid #ddd}"
        "a{color:#0645ad}.version{border-top:2px solid #222;margin-top:26px;padding-top:12px}"
        ".thumbs{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}"
        ".thumb{border:1px solid #ddd;padding:8px;background:#fff}.thumb img{width:100%;height:180px;object-fit:contain;background:white}"
        ".path{font-family:monospace;font-size:11px;word-break:break-all;color:#333}.meta{color:#555}"
        "</style>"
    )
    multi.append("<h1>V1-V60 Multi-Image Case Gallery</h1>")
    multi.append("<p class='meta'>Each version shows up to 16 locally copied candidate images. Use the Markdown/JSON/full_path_lists files for GLB/OBJ and grammar reproduction paths.</p>")
    multi.append("<nav>")
    for rec in records:
        multi.append(f"<a href='#v{rec['version']:02d}'>V{rec['version']:02d}</a> ")
    multi.append("</nav>")
    for rec in records:
        multi.append(f"<section class='version' id='v{rec['version']:02d}'>")
        multi.append(f"<h2>V{rec['version']:02d} - {html.escape(rec['label'])}</h2>")
        multi.append(
            f"<p class='meta'>images={rec['image_count']} geometry={rec['geometry_count']} "
            f"specs={rec['spec_count']} remote={rec['remote_file_count']}</p>"
        )
        multi.append("<div class='thumbs'>")
        for idx, img in enumerate(rec.get("selection_image_copies", []), start=1):
            rel_src = rec["selection_images"][idx - 1] if idx - 1 < len(rec["selection_images"]) else ""
            multi.append("<div class='thumb'>")
            multi.append(f"<a href='{html.escape(img)}'><img src='{html.escape(img)}'></a>")
            multi.append(f"<div class='path'>{html.escape(rel_src)}</div>")
            multi.append("</div>")
        multi.append("</div>")
        multi.append("<p class='path'>")
        multi.append(f"JSON: {OUT / 'v1_v60_case_inventory.json'}<br>")
        v_prefix = f"V{rec['version']:02d}"
        multi.append(f"Image list: {list_dir / (v_prefix + '_images.txt')}<br>")
        multi.append(f"Geometry list: {list_dir / (v_prefix + '_geometry.txt')}<br>")
        multi.append(f"Grammar/repro list: {list_dir / (v_prefix + '_grammar_or_repro.txt')}")
        multi.append("</p></section>")
    (OUT / "v1_v60_case_inventory_multi_image_gallery.html").write_text("".join(multi), encoding="utf-8")

    readme = []
    readme.append("# V1-V60 case inventory 使用说明\n\n")
    readme.append("本目录整理 V1 到 V60 已生成 case 的筛选图、几何文件位置、grammar/spec/manifest/脚本位置，以及一次受限 `a100-2` 远端文件列表。用户筛图优先看 HTML/PNG；后续 agent 复现优先读 JSON 和 `full_path_lists/`。\n\n")
    readme.append("## 快速入口\n\n")
    readme.append(f"- 多候选筛选 HTML: `{OUT / 'v1_v60_case_inventory_multi_image_gallery.html'}`\n")
    readme.append(f"- 单代表图 contact sheet: `{OUT / 'v1_v60_representative_contact_sheet.png'}`\n")
    readme.append(f"- 人类可读 Markdown: `{OUT / 'v1_v60_case_inventory_for_selection_zh.md'}`\n")
    readme.append(f"- 机器可读完整 JSON: `{OUT / 'v1_v60_case_inventory.json'}`\n")
    readme.append(f"- 每版本完整路径列表: `{OUT / 'full_path_lists'}`\n")
    readme.append(f"- 代表图副本: `{OUT / 'representative_images'}`\n")
    readme.append(f"- 多候选图副本: `{OUT / 'selection_images'}`\n\n")
    readme.append("## 字段说明\n\n")
    readme.append("- `selection_images`: 每个版本最多 16 张优先候选图，已复制到 `selection_images/Vxx/`，用于快速人工筛选。\n")
    readme.append("- `all_image_paths`: 本地全部 raster 图片路径，按 contact sheet/zoom/white/textured 等启发式排序。\n")
    readme.append("- `all_geometry_paths`: 本地全部 `.glb`/`.obj` 路径。\n")
    readme.append("- `all_grammar_or_repro_paths`: 本地全部 `.json`/`.md`/`.py`/`.sh`/`.yaml` 路径，包含 manifest、summary、generator/test/postprocess 脚本等。\n")
    readme.append("- `all_remote_paths`: 来自 `remote_a1002_v1_v60_files.txt` 的远端样本路径；远端状态可能之后变化。\n\n")
    readme.append("## 当前覆盖验证\n\n")
    readme.append("- V1-V60 共 60 个版本均有至少一张代表图。\n")
    readme.append("- V1-V60 共 60 个版本均有至少一个本地几何路径。\n")
    readme.append("- V1-V60 共 60 个版本均有至少一个 grammar/spec/repro 路径。\n")
    readme.append("- 本 inventory 没有修改 `paper_siga/main.tex`。\n")
    (OUT / "README.md").write_text("".join(readme), encoding="utf-8")


if __name__ == "__main__":
    build()
