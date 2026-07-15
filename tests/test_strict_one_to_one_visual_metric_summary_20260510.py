import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_one_to_one_visual_metric_summary_20260510.py"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_one_to_one_visual_metric_summary_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_one_to_one_visual_metric_summary_exports_four_claim_bounded_rows(tmp_path):
    mod = load_module()
    rows = mod.build_rows()
    assert len(rows) == 4
    assert {row["family"] for row in rows} == {"DLA/frontier", "IFS/transform", "L-system", "Space colonization"}
    assert all(row["traditional_image_exists"] for row in rows)
    assert all(row["ours_image_exists"] for row in rows)
    assert all("post-GLB surface metrics" in row["metric_boundary"] for row in rows)

    by_family = {row["family"]: row for row in rows}
    assert by_family["DLA/frontier"]["display_priority"] == "main"
    assert by_family["L-system"]["display_priority"] == "main"
    assert by_family["IFS/transform"]["display_priority"] == "main-caveated-transform-admission"
    assert by_family["Space colonization"]["display_priority"] == "main-with-visual-caveat"
    assert float(by_family["IFS/transform"]["min_lcr_r0"]) >= 0.999

    out_dir = tmp_path / "one_to_one_metrics"
    mod.write_csv(out_dir / "rows.csv", rows)
    mod.write_markdown(out_dir / "summary.md", rows)
    with (out_dir / "rows.csv").open(encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == 4
    md = (out_dir / "summary.md").read_text(encoding="utf-8")
    assert "传统 target 是结构控制参照，不是弱 baseline" in md
    assert "watertight/manifold proof" in md
