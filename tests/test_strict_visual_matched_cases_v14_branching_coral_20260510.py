import csv
import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "assets" / "strict_visual_matched_cases_v14_branching_coral_20260510.py"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_v14_branching_coral_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v14_materializes_finer_branching_single_component_coral_inputs(tmp_path):
    mod = load_module()

    summary = mod.materialize(Path(__file__).resolve().parents[1], tmp_path, seed=20260510)

    assert summary["num_cases"] == 8
    assert summary["remote_target"] == "a100-2"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["storage_limit_gb"] == 100
    assert summary["surface_generator"] == "implicit_metaball_marching_cubes_branching_coral_v14"
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
    assert all(row["case_id"].startswith("v14_dla_branching_") for row in rows)
    assert {"dla_coral_cluster_900", "dla_frontier_sheet_700", "dla_crystal_cluster_520"} <= {
        row["traditional_target"] for row in rows
    }
    assert sum(row["case_role"] == "priority_a100_2" for row in rows) >= 6

    required_operator_terms = {
        "stochastic_frontier_attachment",
        "occupancy_exclusion",
        "connected_projection",
        "implicit_metaball_union",
        "smooth_marching_cubes_surface",
        "fine_antler_tip_subbranching",
        "reduced_lobe_volume",
        "porous_ridge_microrelief",
        "no_detached_micro_islands",
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
        assert "fine_antler_tip_subbranching" in row["operator_composition"]
        assert "smooth_welded_staghorn_surface" not in row["operator_composition"]
        assert row["controls"]
        assert row["why_matches_traditional"]

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["case_id"] == row["case_id"]
        assert metadata["traditional_target"] == row["traditional_target"]
        assert metadata["strict_generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_posthoc_pick"
        assert metadata["remote_constraints"]["machine"] == "a100-2"
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["root_selection_log"]["root_source_type"] == "v14_implicit_fine_branching_coral_input_generator"
        assert metadata["traditional_alignment"]["operator_family"] == "traditional DLA/frontier accretive attachment"
        assert metadata["traditional_alignment"]["same_category"] is True
        assert "fresh on a100-2" in metadata["traditional_alignment"]["why_strict_one_to_one"]
        assert set(metadata["operators"]) >= required_operator_terms

        controls = metadata["controls"]
        assert controls["occupancy_exclusion_radius"] > 0.0
        assert controls["generated_nodes"] >= 150
        assert controls["direct_tube_mesh"] is False
        assert controls["implicit_grid_resolution"] >= 72
        assert controls["metaball_sample_count"] >= 1100
        assert controls["micro_branch_count"] >= 55
        assert controls["antler_tip_count"] >= 40
        assert controls["subtractive_pore_count"] >= 22
        assert controls["large_lobe_scale_max"] <= 0.78
        assert controls["thin_tip_radius_max"] <= 0.014
        assert "marching cubes" in controls["surface_strategy"]
        assert "thin branching" in controls["surface_strategy"]
        assert "claw" in controls["v14_failure_addressed"]
        assert "frontier attachment" in controls["frontier_attachment_mode"]

        contract = metadata["visual_readability_contract"]
        assert "single component" in contract["dryrun_visual_floor"]
        assert "large blob" in contract["v13_failure_addressed"]
        assert "fine antler" in contract["frontier_structure"]
        assert "detached" in contract["negative_constraint"]

        m = metric_by_case[row["case_id"]]
        assert m["vertices"] > 2600
        assert m["faces"] > 5000
        assert m["mesh_component_count"] == 1
        assert m["largest_mesh_component_vertex_ratio"] == 1.0
        assert m["surface_area"] > 0.0
        assert m["curved_branch_edges"] >= 140
        assert m["micro_branch_count"] >= 55
        assert m["antler_tip_count"] >= 40
        assert m["perforated_membrane_count"] >= 22

    with (tmp_path / "manifest.csv").open(encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == len(rows)
    assert {row["case_id"] for row in csv_rows} == {row["case_id"] for row in rows}
