import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "assets" / "strict_visual_matched_cases_v4_20260510.py"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_v4_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v4_dryrun_materializes_remote_ready_strict_matched_inputs(tmp_path):
    mod = load_module()

    summary = mod.materialize(Path(__file__).resolve().parents[1], tmp_path, seed=20260510, case_limit=8)

    assert summary["num_cases"] == 8
    assert summary["remote_target"] == "a100-2"
    assert (tmp_path / "manifest.csv").exists()
    assert (tmp_path / "manifest.json").exists()
    assert (tmp_path / "initial_metrics.csv").exists()
    assert (tmp_path / "initial_metrics.json").exists()
    assert (tmp_path / "a100-2_cases.txt").exists()
    assert (tmp_path / "README.md").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((tmp_path / "initial_metrics.json").read_text(encoding="utf-8"))
    assert len(rows) == 8
    assert {row["remote_target"] for row in rows} == {"a100-2"}
    assert {"L-system", "DLA/frontier", "IFS/transform"} <= {row["family"] for row in rows}

    for row in rows:
        obj_path = Path(row["mesh_path"])
        metadata_path = Path(row["metadata_path"])
        assert obj_path.exists()
        assert obj_path.suffix == ".obj"
        assert metadata_path.exists()
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["match_target"] == row["match_target"]
        assert "strict_match_notes" in metadata

    for row in metrics:
        assert row["vertices"] > 0
        assert row["faces"] > 0
        assert row["largest_mesh_component_vertex_ratio"] >= 0.985
        assert row["mesh_component_count"] <= 3
