import csv
import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "assets" / "strict_visual_matched_cases_v6_connectivity_20260510.py"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_v6_connectivity_20260510", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v6_dryrun_materializes_strict_one_to_one_connected_inputs(tmp_path):
    mod = load_module()

    summary = mod.materialize(Path(__file__).resolve().parents[1], tmp_path, seed=20260510)

    assert summary["num_cases"] >= 10
    assert summary["remote_target"] == "a100-2"
    assert summary["storage_root"] == "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
    assert summary["storage_limit_gb"] == 100
    assert (tmp_path / "manifest.csv").exists()
    assert (tmp_path / "manifest.json").exists()
    assert (tmp_path / "initial_metrics.csv").exists()
    assert (tmp_path / "initial_metrics.json").exists()
    assert (tmp_path / "a100-2_cases.txt").exists()
    assert (tmp_path / "gpu4567_cases.txt").exists()
    assert (tmp_path / "README.md").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((tmp_path / "initial_metrics.json").read_text(encoding="utf-8"))
    metric_by_case = {row["case_id"]: row for row in metrics}

    assert len(rows) == summary["num_cases"]
    assert {row["remote_target"] for row in rows} == {"a100-2"}
    assert {int(row["gpu_group"]) for row in rows} <= {4, 5, 6, 7}
    assert {"L-system", "Space colonization", "DLA/frontier", "IFS/transform"} <= {row["family"] for row in rows}
    assert any(row["case_role"] == "priority_a100_2" for row in rows)

    for row in rows:
        obj_path = Path(row["mesh_path"])
        metadata_path = Path(row["metadata_path"])
        assert obj_path.exists()
        assert obj_path.suffix == ".obj"
        assert metadata_path.exists()
        assert row["strict_one_to_one"] == "true"
        assert row["generation_policy"] == "generate_new_on_a100_2_no_local_cherrypick"
        assert row["storage_root"] == "/mnt/beegfs/ruocheng/recursive_3d_generative_growth_20260507"
        assert row["operator_composition"]
        assert row["traditional_target"]
        assert row["controls"]
        assert row["why_matches_traditional"]

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert metadata["case_id"] == row["case_id"]
        assert metadata["traditional_target"] == row["traditional_target"]
        assert metadata["operator_composition"] == row["operator_composition"]
        assert metadata["controls"]
        assert metadata["why_matches_traditional"]
        assert metadata["operator_family"]
        assert metadata["traditional_alignment"]["traditional_target"] == row["traditional_target"]
        assert metadata["traditional_alignment"]["operator_family"] == metadata["operator_family"]
        assert metadata["visual_readability_contract"]["dryrun_visual_floor"]
        assert metadata["visual_readability_contract"]["v5_failure_addressed"]
        assert metadata["root_selection_log"]["root_source_type"] == "v6_connected_case_input_generator"
        assert metadata["root_selection_log"]["source_generator"].endswith("strict_visual_matched_cases_v6_connectivity_20260510.py")
        assert metadata["remote_constraints"]["allowed_gpus"] == [4, 5, 6, 7]
        assert metadata["remote_constraints"]["storage_limit_gb"] == 100
        assert metadata["strict_generation_policy"] == "generate_new_on_a100_2_no_local_selection_or_posthoc_pick"
        if row["family"] in {"L-system", "Space colonization"}:
            contract = metadata["visual_readability_contract"]
            assert contract["organic_structure"] == "continuous spine plus many oriented leaf/needle/rootlet primitives plus local smooth envelope"
        if row["family"] == "DLA/frontier":
            contract = metadata["visual_readability_contract"]
            assert "bulbous/smooth tips" in contract["non_tree_structure"]
            assert "porous bridges" in contract["non_tree_structure"]

        m = metric_by_case[row["case_id"]]
        assert m["vertices"] > 0
        assert m["faces"] > 0
        assert m["mesh_component_count"] == 1
        assert m["largest_mesh_component_vertex_ratio"] == 1.0

    with (tmp_path / "manifest.csv").open(encoding="utf-8") as f:
        csv_rows = list(csv.DictReader(f))
    assert len(csv_rows) == len(rows)
    assert {row["case_id"] for row in csv_rows} == {row["case_id"] for row in rows}
