import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSET_SCRIPT = ROOT / "assets" / "masked_naturalization_ablation_assets_20260510.py"
SEAM_SCRIPT = ROOT / "assets" / "masked_naturalization_seam_band_qa_20260510.py"
BATCH_SCRIPT = ROOT / "assets" / "prepare_seam_aware_texturing_batch_20260510.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_prepare_seam_aware_texturing_batch_exports_remote_manifest(tmp_path):
    assets_mod = load_module(ASSET_SCRIPT, "masked_naturalization_ablation_assets_20260510")
    seam_mod = load_module(SEAM_SCRIPT, "masked_naturalization_seam_band_qa_20260510")
    batch_mod = load_module(BATCH_SCRIPT, "prepare_seam_aware_texturing_batch_20260510")

    asset_dir = tmp_path / "masked_assets"
    assets_mod.materialize(out_dir=asset_dir, resolution=34, depth_count=3, seed=20260510)
    seam_dir = tmp_path / "seam_results"
    seam_mod.build_seam_qa(asset_dir=asset_dir, out_dir=seam_dir, visual_dir=tmp_path / "seam_visuals", status_md=tmp_path / "status.md")

    out_dir = tmp_path / "seam_batch"
    summary = batch_mod.prepare_batch(seam_dir=seam_dir, out_dir=out_dir)
    assert summary["schema"] == "seam_aware_texturing_batch_20260510"
    assert summary["case_count"] == 3
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert Path(summary["manifest_csv"]).exists()
    assert Path(summary["manifest_json"]).exists()

    with Path(summary["manifest_csv"]).open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3
    assert {row["task_id"] for row in rows} == {"botanical_root", "coral_frontier", "ifs_crystal"}
    assert {int(row["gpu_group"]) for row in rows} <= {4, 5, 6, 7}
    for row in rows:
        assert row["mesh_path"].startswith("/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/inputs/seam_aware_texturing_batch_20260510/")
        assert row["guide_image"].endswith("_seam_aware_pbr_guide.png")
        assert "seam visual QA" in row["claim_scope"]
        local_mesh = out_dir / row["mesh_path"].split("/inputs/seam_aware_texturing_batch_20260510/", 1)[1]
        local_guide = out_dir / row["guide_image"].split("/inputs/seam_aware_texturing_batch_20260510/", 1)[1]
        local_meta = out_dir / row["metadata_path"].split("/inputs/seam_aware_texturing_batch_20260510/", 1)[1]
        assert local_mesh.exists()
        assert local_guide.exists()
        assert local_meta.exists()
        metadata = json.loads(local_meta.read_text(encoding="utf-8"))
        assert metadata["remote_texturing_role"] == "seam_aware_junction_collar_candidate"

    assert (out_dir / "gpu4567_cases.txt").exists()
    assert (out_dir / "gpu4_cases.txt").exists()
