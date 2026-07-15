import csv
import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "assets" / "baseline_matrix_20260509.py"


def load_module():
    spec = importlib.util.spec_from_file_location("baseline_matrix_20260509", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_quick_baseline_matrix_writes_meshes_metrics_and_contact_sheet(tmp_path):
    mod = load_module()

    summary = mod.generate_matrix(tmp_path, max_depth=2, seed=20260509, quick=True)

    metrics_path = tmp_path / "metrics.csv"
    contact_path = tmp_path / "contact_sheet_final_depth.png"
    assert metrics_path.exists()
    assert contact_path.exists()
    assert contact_path.stat().st_size > 1024

    rows = list(csv.DictReader(metrics_path.open(encoding="utf-8")))
    assert len(rows) == 3 * 3 * 2
    assert {row["case"] for row in rows} == {"tree", "root", "vine"}
    assert {row["method"] for row in rows} == {"lsystem", "space_colonization", "proposed_connected"}
    assert {row["same_seed"] for row in rows} == {"20260509"}
    assert {row["same_max_depth"] for row in rows} == {"2"}

    for row in rows:
        obj_path = Path(row["obj_path"])
        assert obj_path.exists()
        assert obj_path.suffix == ".obj"
        assert int(row["vertices"]) > 0
        assert int(row["faces"]) > 0
        assert int(row["segments"]) > 0
        assert float(row["path_to_root_rate"]) >= 0.0

    final = [row for row in rows if row["depth"] == "2"]
    assert len(summary["final_rows"]) == len(final)
    proposed = [row for row in final if row["method"] == "proposed_connected"]
    assert all(int(row["occupancy_component_count_6n"]) == 1 for row in proposed)
    assert all(float(row["root_component_ratio"]) == 1.0 for row in proposed)
