import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V56_lsystem_branch_basal_continuation_yfork_20260511.py"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V56_lsystem_branch_basal_continuation_yfork_20260511", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v56_lsystem_branch_materializes_basal_continuation_cases(tmp_path):
    mod = load_module()
    summary = mod.materialize(ROOT, tmp_path, seed=20260511)

    assert summary["num_cases"] == 4
    assert summary["surface_generator"] == "strict_visual_matched_cases_V56_lsystem_branch_basal_continuation_yfork_naturalization"
    assert summary["surface_strategy"] == "v56_lsystem_branch_basal_continuation_yfork_naturalization"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["default_active_gpus"] == [4, 5]
    assert summary["max_simultaneous_remote_gpus"] == 2
    assert summary["lsystem_branch_gate"]["mask_scope"] == "object_space_basal_continuation_side_yfork_bands_only"
    assert summary["do_not_launch_remote_before_local_visual_qa"] is True

    zoom_manifest = tmp_path / "V56_obj_zoom_manifest_junctiontarget_20260511.json"
    assert zoom_manifest.exists()
    assert not (tmp_path / "V55_obj_zoom_manifest_junctiontarget_20260511.json").exists()
    assert not (tmp_path / "V54_obj_zoom_manifest_junctiontarget_20260511.json").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert {row["case_id"] for row in rows} == {
        "V56_lsys_branch_basal_continuation_yfork_A",
        "V56_lsys_branch_basal_continuation_yfork_lowfrag_B",
        "V56_lsys_branch_basal_continuation_yfork_dense_C",
        "V56_lsys_branch_basal_continuation_yfork_slim_D",
    }
    assert all(row["surface_strategy"] == "v56_lsystem_branch_basal_continuation_yfork_naturalization" for row in rows)
    assert all(int(row["terminal_sleeve_count"]) == 0 for row in rows)
    assert all(int(row["terminal_taper_count"]) > 0 for row in rows)
    assert all(float(row["largest_component_projection_retained_ratio"]) >= 0.90 for row in rows)

    for row in rows:
        metadata = json.loads(Path(row["metadata_path"]).read_text(encoding="utf-8"))
        assert metadata["root_selection_log"]["source_generator"] == "assets/strict_visual_matched_cases_V56_lsystem_branch_basal_continuation_yfork_20260511.py"
        assert "v56_lsystem_branch_naturalization_contract" in metadata
        controls = metadata["controls"]
        assert controls["v56_lsystem_branch_basal_continuation_yfork_naturalization"] is True
        assert controls["v55_lsystem_branch_elongated_saddle_yfork_naturalization"] is False
        assert controls["v54_lsystem_branch_centered_bough_yfork_naturalization"] is False
        assert controls["basal_continuation_node_count"] == 3
        assert controls["terminal_sleeve_count"] == 0
        assert controls["terminal_bud_count"] == 0
        assert controls["sdedit_seam_backprojection_available"] is False
        assert "branch root is no longer a visible club-like terminal" in controls["hard_tube_cap_mitigation"]

    zdata = json.loads(zoom_manifest.read_text(encoding="utf-8"))
    assert len(zdata["cases"]) == 4
    assert all(item["detail_target_source"] == "v56_lsystem_explicit_side_yfork_basal_continuation_excluded" for item in zdata["cases"])
    assert all(1.9 <= item["zoom_divisor"] <= 2.15 for item in zdata["cases"])
