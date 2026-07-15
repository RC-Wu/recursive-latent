import csv
import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "assets" / "strict_visual_matched_cases_v8_frontier_refine_20260510.py"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_v8_frontier_refine_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v8_frontier_refine_materializes_strict_connected_frontier_inputs(tmp_path):
    mod = load_module()

    summary = mod.materialize(Path(__file__).resolve().parents[1], tmp_path, seed=20260510)

    assert 8 <= summary["num_cases"] <= 12
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["storage_limit_gb"] == 100
    assert (tmp_path / "manifest.csv").exists()
    assert (tmp_path / "manifest.json").exists()
    assert (tmp_path / "initial_metrics.csv").exists()
    assert (tmp_path / "initial_metrics.json").exists()
    assert (tmp_path / "a100-2_cases.txt").exists()
    assert (tmp_path / "gpu4567_cases.txt").exists()
    for gpu in (4, 5, 6, 7):
        assert (tmp_path / f"gpu{gpu}_cases.txt").exists()
    assert (tmp_path / "README.md").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((tmp_path / "initial_metrics.json").read_text(encoding="utf-8"))
    metric_by_case = {row["case_id"]: row for row in metrics}

    assert len(rows) == summary["num_cases"]
    assert {row["remote_target"] for row in rows} == {"a100-2"}
    assert {int(row["gpu_group"]) for row in rows} == {4, 5, 6, 7}
    assert {row["family"] for row in rows} == {"DLA/frontier"}
    assert {"dla_coral_cluster_900", "dla_frontier_sheet_700", "dla_crystal_cluster_520"} <= {
        row["traditional_target"] for row in rows
    }
    assert any(row["case_role"] == "priority_a100_2" for row in rows)

    required_operator_terms = {
        "stochastic_frontier_attachment",
        "occupancy_exclusion",
        "continuous_center_skeleton",
        "smooth_tube_surface",
        "thin_plate_ridge_details",
        "small_scale_branching",
        "edge_attached_porous_membranes",
    }

    for row in rows:
        obj_path = Path(row["mesh_path"])
        metadata_path = Path(row["metadata_path"])
        guide_path = Path(row["guide_image"])
        assert obj_path.exists()
        assert obj_path.suffix == ".obj"
        assert metadata_path.exists()
        assert guide_path.exists()
        assert guide_path.suffix == ".png"
        assert row["strict_one_to_one"] == "true"
        assert row["generation_policy"] == "generate_new_on_a100_2_no_local_cherrypick"
        assert row["operator_composition"]
        assert row["controls"]
        assert row["why_matches_traditional"]

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["case_id"] == row["case_id"]
        assert metadata["traditional_target"] == row["traditional_target"]
        assert metadata["strict_generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_posthoc_pick"
        assert metadata["remote_constraints"]["machine"] == "a100-2"
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["root_selection_log"]["root_source_type"] == "v8_frontier_refine_input_generator"
        assert metadata["traditional_alignment"]["operator_family"] == "traditional DLA/frontier accretive attachment"
        assert metadata["traditional_alignment"]["same_category"] is True
        assert "fresh on a100-2" in metadata["traditional_alignment"]["why_strict_one_to_one"]
        assert set(metadata["operators"]) >= required_operator_terms
        assert metadata["controls"]["occupancy_exclusion_radius"] > 0.0
        assert metadata["controls"]["generated_nodes"] >= 180
        assert metadata["controls"]["surface_strategy"]
        contract = metadata["visual_readability_contract"]
        assert "single or near-single component" in contract["dryrun_visual_floor"]
        assert "reduce blocky" in contract["v7_failure_addressed"]
        assert "continuous center skeleton" in contract["frontier_structure"]
        assert "isolated block" in contract["negative_constraint"]

        m = metric_by_case[row["case_id"]]
        assert m["vertices"] > 1000
        assert m["faces"] > 2000
        assert m["mesh_component_count"] <= 2
        assert m["largest_mesh_component_vertex_ratio"] >= 0.985
        assert m["surface_area"] > 0.0

    with (tmp_path / "manifest.csv").open(encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == len(rows)
    assert {row["case_id"] for row in csv_rows} == {row["case_id"] for row in rows}
