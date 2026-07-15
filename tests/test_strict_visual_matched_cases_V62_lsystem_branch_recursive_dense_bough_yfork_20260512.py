import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V62_lsystem_branch_recursive_dense_bough_yfork_20260512.py"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V62_lsystem_branch_recursive_dense_bough_yfork_20260512", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v62_lsystem_branch_materializes_recursive_dense_bough_cases(tmp_path):
    mod = load_module()
    summary = mod.materialize(ROOT, tmp_path, seed=20260511)

    assert summary["num_cases"] == 4
    assert summary["surface_generator"] == "strict_visual_matched_cases_V62_lsystem_branch_recursive_dense_bough_yfork_naturalization"
    assert summary["surface_strategy"] == "v62_lsystem_branch_recursive_dense_bough_yfork_depth_density_plus_antifacet"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["max_simultaneous_remote_gpus"] == 2
    assert summary["do_not_launch_remote_before_local_visual_qa"] is True
    assert "recursive_dense_compact_bough" in summary["lsystem_branch_gate"]["mask_scope"]
    assert summary["lsystem_branch_gate"]["min_target_terminals_for_visual_qa"] == 12
    assert summary["lsystem_branch_gate"]["target_branch_junctions_min"] == 10
    assert summary["v62_design"]["generator_change_required"] is True

    zoom_manifest = tmp_path / "V62_obj_zoom_manifest_junctiontarget_20260512.json"
    assert zoom_manifest.exists()
    assert not (tmp_path / "V53_obj_zoom_manifest_junctiontarget_20260511.json").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert {row["case_id"] for row in rows} == {
        "V62_lsys_branch_recursive_depth_A",
        "V62_lsys_branch_recursive_dense_B",
        "V62_lsys_branch_balanced_depth_C",
        "V62_lsys_branch_highdepth_lowfrag_D",
    }
    assert all(row["surface_strategy"] == "v62_lsystem_branch_recursive_dense_bough_yfork_depth_density_plus_antifacet" for row in rows)
    assert all(row["case_role"] == "v62_lsystem_branch_recursive_dense_bough_yfork_naturalization" for row in rows)
    assert {int(row["gpu_group"]) for row in rows} == {4, 5}
    assert all(int(row["terminal_sleeve_count"]) == 0 for row in rows)
    assert all(int(row["ridge_count"]) == 0 for row in rows)
    assert all(int(row["branch_junction_count"]) >= 10 for row in rows)
    assert all(int(row["terminal_count"]) >= 12 for row in rows)
    assert all(float(row["largest_component_projection_retained_ratio"]) >= 0.90 for row in rows)

    for row in rows:
        metadata = json.loads(Path(row["metadata_path"]).read_text(encoding="utf-8"))
        assert metadata["root_selection_log"]["source_generator"] == "assets/strict_visual_matched_cases_V62_lsystem_branch_recursive_dense_bough_yfork_20260512.py"
        assert "v62_lsystem_branch_naturalization_contract" in metadata
        controls = metadata["controls"]
        assert controls["v62_lsystem_branch_recursive_dense_bough_yfork_naturalization"] is True
        assert controls["v59_lsystem_branch_smooth_short_bough_yfork_naturalization"] is False
        assert controls["implicit_grid_resolution"] == mod.V62_GRID
        assert controls["gaussian_sigma"] == mod.V62_SIGMA
        assert controls["junction_radius_boost"] == mod.V62_JUNCTION_RADIUS_BOOST
        assert controls["terminal_sleeve_count"] == 0
        assert controls["ridge_count"] == 0
        assert controls["sdedit_seam_backprojection_available"] is False
        assert "V61 cleaned" in controls["v62_failure_addressed"]

    zdata = json.loads(zoom_manifest.read_text(encoding="utf-8"))
    assert len(zdata["cases"]) == 4
    assert all(item["detail_target_source"] == "v62_lsystem_explicit_recursive_dense_bough_yfork_mask" for item in zdata["cases"])
    assert all(1.65 <= item["zoom_divisor"] <= 1.8 for item in zdata["cases"])
    assert all(len(item["fixed_detail_targets"]) == 2 for item in zdata["cases"])
