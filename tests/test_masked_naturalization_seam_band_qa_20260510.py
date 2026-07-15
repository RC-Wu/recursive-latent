import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET_SCRIPT = ROOT / "assets" / "masked_naturalization_ablation_assets_20260510.py"
SEAM_SCRIPT = ROOT / "assets" / "masked_naturalization_seam_band_qa_20260510.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_seam_band_qa_exports_junction_collar_candidates(tmp_path):
    assets_mod = load_module(ASSET_SCRIPT, "masked_naturalization_ablation_assets_20260510")
    seam_mod = load_module(SEAM_SCRIPT, "masked_naturalization_seam_band_qa_20260510")

    asset_dir = tmp_path / "masked_assets"
    assets_mod.materialize(out_dir=asset_dir, resolution=34, depth_count=3, seed=20260510)

    out_dir = tmp_path / "seam_results"
    visual_dir = tmp_path / "seam_visuals"
    status_md = tmp_path / "seam_status.md"
    summary = seam_mod.build_seam_qa(
        asset_dir=asset_dir,
        out_dir=out_dir,
        visual_dir=visual_dir,
        status_md=status_md,
    )

    assert summary["schema"] == "masked_naturalization_seam_band_qa_20260510"
    assert summary["task_count"] == 3
    assert "not Trellis runtime topology proof" in summary["claim_scope"]
    assert Path(summary["metrics_csv"]).exists()
    assert Path(summary["metrics_json"]).exists()
    assert Path(summary["contact_sheet"]).exists()
    assert Path(summary["status_md"]).exists()

    with Path(summary["metrics_csv"]).open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3
    assert {row["task_id"] for row in rows} == {"botanical_root", "coral_frontier", "ifs_crystal"}
    for row in rows:
        assert row["source_variant"] == "per_depth_masked_naturalization"
        assert row["optimized_variant"] == "per_depth_masked_junction_collar"
        assert int(row["junction_collar_count"]) > 0
        assert Path(row["optimized_mesh"]).exists()
        assert Path(row["optimized_metadata"]).exists()
        assert float(row["optimized_lcr"]) >= 0.99
        metadata = json.loads(Path(row["optimized_metadata"]).read_text(encoding="utf-8"))
        assert metadata["variant"] == "per_depth_masked_junction_collar"
        assert metadata["junction_collar_count"] == int(row["junction_collar_count"])
        assert "seam-band" in metadata["claim_scope"]

    status = Path(summary["status_md"]).read_text(encoding="utf-8")
    assert "junction collar" in status
    assert "不能写" in status
