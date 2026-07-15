import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "assets" / "connected_scaffold_cases_20260509.py"


def load_module():
    spec = importlib.util.spec_from_file_location("connected_scaffold_cases", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_smoke_generation_writes_connected_mesh_assets(tmp_path):
    mod = load_module()

    summary = mod.generate_all(tmp_path, quick=True)

    labels = {row["label"] for row in summary["rows"]}
    assert {"connected_dla_coral", "bismuth_stepped_crystal", "crystal_lattice_cluster", "root_vine_control"} <= labels
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "metrics.csv").exists()
    assert (tmp_path / "contact_sheet.png").exists()
    for row in summary["rows"]:
        obj_path = Path(row["obj_path"])
        assert obj_path.exists()
        assert obj_path.suffix == ".obj"
        assert row["faces"] > 0
        assert row["vertices"] > 0
        assert row["occupancy_component_count_6n"] <= 2
        assert row["largest_occupancy_component_ratio_6n"] >= 0.98
