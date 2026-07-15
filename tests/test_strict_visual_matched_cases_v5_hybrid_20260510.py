import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "assets" / "strict_visual_matched_cases_v5_hybrid_20260510.py"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_v5_hybrid_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v5_hybrid_dryrun_materializes_small_a1002_batch(tmp_path):
    mod = load_module()

    summary = mod.materialize(Path(__file__).resolve().parents[1], tmp_path, seed=20260510)

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
    assert {"L-system", "Space colonization", "DLA/frontier", "IFS/transform"} <= {row["family"] for row in rows}

    expected_targets = {
        "lsys_pine_canopy_d5",
        "lsys_root_fan_d5",
        "lsys_climbing_vine_d6",
        "sc_tree_crown_260",
        "sc_root_network_260",
        "dla_coral_cluster_900",
        "dla_frontier_sheet_700",
        "ifs_radial_ornament_o8_d4",
    }
    assert {row["match_target"] for row in rows} == expected_targets

    for row in rows:
        obj_path = Path(row["mesh_path"])
        metadata_path = Path(row["metadata_path"])
        assert obj_path.exists()
        assert obj_path.suffix == ".obj"
        assert metadata_path.exists()
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["traditional_target"] == row["match_target"]
        assert metadata["operator_composition"]
        assert metadata["why_matches_traditional"]
        assert metadata["root_selection_log"]["root_generation_budget"].startswith("local CPU dry-run")

    for row in metrics:
        assert row["vertices"] > 0
        assert row["faces"] > 0
        assert row["largest_mesh_component_vertex_ratio"] >= 0.985
        assert row["mesh_component_count"] <= 3
