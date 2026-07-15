import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V57_lsystem_branch_tapered_midbough_yfork_20260511.py"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V57_lsystem_branch_tapered_midbough_yfork_20260511", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v57_lsystem_branch_materializes_tapered_midbough_cases(tmp_path):
    mod = load_module()
    summary = mod.materialize(ROOT, tmp_path, seed=20260511)

    assert summary["num_cases"] == 4
    assert summary["surface_generator"] == "strict_visual_matched_cases_V57_lsystem_branch_tapered_midbough_yfork_naturalization"
    assert summary["surface_strategy"] == "v57_lsystem_branch_tapered_midbough_yfork_naturalization"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["default_active_gpus"] == [4, 5]
    assert summary["max_simultaneous_remote_gpus"] == 2
    assert summary["lsystem_branch_gate"]["mask_scope"] == "object_space_tapered_midbough_side_yfork_bands_only"
    assert summary["do_not_launch_remote_before_local_visual_qa"] is True

    zoom_manifest = tmp_path / "V57_obj_zoom_manifest_junctiontarget_20260511.json"
    assert zoom_manifest.exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert {row["case_id"] for row in rows} == {
        "V57_lsys_branch_tapered_midbough_yfork_A",
        "V57_lsys_branch_tapered_midbough_yfork_lowfrag_B",
        "V57_lsys_branch_tapered_midbough_yfork_dense_C",
        "V57_lsys_branch_tapered_midbough_yfork_slim_D",
    }
    assert all(row["surface_strategy"] == "v57_lsystem_branch_tapered_midbough_yfork_naturalization" for row in rows)
    assert all(int(row["terminal_sleeve_count"]) == 0 for row in rows)
    assert all(int(row["terminal_taper_count"]) > 0 for row in rows)
    assert all(float(row["largest_component_projection_retained_ratio"]) >= 0.90 for row in rows)

    for row in rows:
        metadata = json.loads(Path(row["metadata_path"]).read_text(encoding="utf-8"))
        assert metadata["root_selection_log"]["source_generator"] == "assets/strict_visual_matched_cases_V57_lsystem_branch_tapered_midbough_yfork_20260511.py"
        assert "v57_lsystem_branch_naturalization_contract" in metadata
        controls = metadata["controls"]
        assert controls["v57_lsystem_branch_tapered_midbough_yfork_naturalization"] is True
        assert controls["v55_lsystem_branch_elongated_saddle_yfork_naturalization"] is False
        assert controls["v54_lsystem_branch_centered_bough_yfork_naturalization"] is False
        assert controls["terminal_sleeve_count"] == 0
        assert controls["terminal_bud_count"] == 0
        assert controls["support_base_radius"] <= 0.024
        assert controls["terminal_radius_shrink"] <= 0.075
        assert controls["tip_parent_radius_shrink"] <= 0.23
        assert controls["sdedit_seam_backprojection_available"] is False
        assert "two-ended tapered mid-bough" in controls["hard_tube_cap_mitigation"]

    zdata = json.loads(zoom_manifest.read_text(encoding="utf-8"))
    assert len(zdata["cases"]) == 4
    assert all(item["detail_target_source"] == "v57_lsystem_explicit_side_yfork_tapered_midbough" for item in zdata["cases"])
    assert all(1.8 <= item["zoom_divisor"] <= 2.0 for item in zdata["cases"])
