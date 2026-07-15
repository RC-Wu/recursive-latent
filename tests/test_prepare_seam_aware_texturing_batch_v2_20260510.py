import csv
import importlib.util
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
V1_SCRIPT = ROOT / "assets" / "prepare_seam_aware_texturing_batch_v2_20260510.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_prepare_seam_aware_texturing_batch_v2_uses_fixed_geometry_and_many_guides(tmp_path):
    mod = load_module(V1_SCRIPT, "prepare_seam_aware_texturing_batch_v2_20260510")
    v1_dir = tmp_path / "v1"
    for source_case in {
        "S01_botanical_root_junction_collar_continuous_bark",
        "S02_coral_frontier_junction_collar_continuous_pores",
        "S03_ifs_crystal_junction_collar_continuous_facets",
    }:
        case_dir = v1_dir / source_case
        case_dir.mkdir(parents=True)
        (case_dir / f"{source_case}.obj").write_text("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n", encoding="utf-8")
        (case_dir / f"{source_case}_metadata.json").write_text(
            json.dumps({"source_case": source_case, "remote_texturing_role": "v1"}),
            encoding="utf-8",
        )

    out_dir = tmp_path / "v2"
    summary = mod.prepare_batch(v1_dir=v1_dir, out_dir=out_dir)
    assert summary["schema"] == "seam_aware_texturing_batch_v2_20260510"
    assert summary["case_count"] == 8
    assert summary["allowed_gpus"] == [4, 5, 6, 7]

    rows = list(csv.DictReader((out_dir / "manifest.csv").open(encoding="utf-8")))
    assert len(rows) == 8
    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert {row["task_id"] for row in rows} == {"botanical_root", "coral_frontier", "ifs_crystal"}
    assert any("low-contrast" in row["claim_scope"] for row in rows)

    for row in rows:
        assert row["mesh_path"].startswith(
            "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507/inputs/seam_aware_texturing_batch_v2_20260510/"
        )
        assert row["guide_image"].endswith("_pbr_guide_v2.png")
        local_mesh = out_dir / row["mesh_path"].split("/inputs/seam_aware_texturing_batch_v2_20260510/", 1)[1]
        local_guide = out_dir / row["guide_image"].split("/inputs/seam_aware_texturing_batch_v2_20260510/", 1)[1]
        local_meta = out_dir / row["metadata_path"].split("/inputs/seam_aware_texturing_batch_v2_20260510/", 1)[1]
        assert local_mesh.exists()
        assert local_guide.exists()
        assert Image.open(local_guide).size == (768, 768)
        metadata = json.loads(local_meta.read_text(encoding="utf-8"))
        assert metadata["remote_texturing_role"] == "seam_aware_v2_low_contrast_texture_candidate"
        assert metadata["paper_claim_scope"].startswith("visual seam/PBR QA")

    for gpu in [4, 5, 6, 7]:
        assert (out_dir / f"gpu{gpu}_cases.txt").read_text(encoding="utf-8").strip()
