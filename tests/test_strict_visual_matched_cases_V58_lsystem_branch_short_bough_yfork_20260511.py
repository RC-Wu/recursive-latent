import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "assets" / "strict_visual_matched_cases_V58_lsystem_branch_short_bough_yfork_20260511.py"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_visual_matched_cases_V58_lsystem_branch_short_bough_yfork_20260511", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_v58_lsystem_branch_materializes_short_bough_cases(tmp_path):
    mod = load_module()
    summary = mod.materialize(ROOT, tmp_path, seed=20260511)

    assert summary["num_cases"] == 4
    assert summary["surface_generator"] == "strict_visual_matched_cases_V58_lsystem_branch_short_bough_yfork_naturalization"
    assert summary["surface_strategy"] == "v58_lsystem_branch_short_bough_yfork_root_silhouette_naturalization"
    assert summary["allowed_gpus"] == [4, 5, 6, 7]
    assert summary["default_active_gpus"] == [4, 5]
    assert summary["max_simultaneous_remote_gpus"] == 2
    assert summary["lsystem_branch_gate"]["mask_scope"] == "object_space_compact_short_bough_side_yfork_bands_only"
    assert summary["lsystem_branch_gate"]["min_saddle_necks"] >= 3
    assert summary["lsystem_branch_gate"]["min_terminal_tapers"] > 0
    assert summary["do_not_launch_remote_before_local_visual_qa"] is True

    zoom_manifest = tmp_path / "V58_obj_zoom_manifest_junctiontarget_20260511.json"
    assert zoom_manifest.exists()
    assert not (tmp_path / "V53_obj_zoom_manifest_junctiontarget_20260511.json").exists()

    rows = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert {row["case_id"] for row in rows} == {
        "V58_lsys_branch_short_bough_yfork_A",
        "V58_lsys_branch_short_bough_lowfrag_B",
        "V58_lsys_branch_short_bough_dense_C",
        "V58_lsys_branch_short_bough_compact_D",
    }
    assert all(row["surface_strategy"] == "v58_lsystem_branch_short_bough_yfork_root_silhouette_naturalization" for row in rows)
    assert all(row["case_role"] == "v58_lsystem_branch_short_bough_yfork_naturalization" for row in rows)
    assert {int(row["gpu_group"]) for row in rows} == {4, 5}
    assert all(int(row["terminal_sleeve_count"]) == 0 for row in rows)
    assert all(int(row["terminal_taper_count"]) > 0 for row in rows)
    assert all(float(row["largest_component_projection_retained_ratio"]) >= 0.45 for row in rows)
    assert all(int(row["branch_junction_count"]) >= 3 for row in rows)

    for row in rows:
        metadata = json.loads(Path(row["metadata_path"]).read_text(encoding="utf-8"))
        assert metadata["root_selection_log"]["source_generator"] == "assets/strict_visual_matched_cases_V58_lsystem_branch_short_bough_yfork_20260511.py"
        assert "v58_lsystem_branch_naturalization_contract" in metadata
        assert "v53_lsystem_branch_naturalization_contract" not in metadata
        contract = metadata["v58_lsystem_branch_naturalization_contract"]
        assert contract["sdedit_seam_backprojection_available"] is False
        assert "compact short-bough" in contract["geometry_operator"]
        controls = metadata["controls"]
        assert controls["v58_lsystem_branch_short_bough_yfork_naturalization"] is True
        assert controls["v53_lsystem_branch_natural_bough_graph_yfork_naturalization"] is False
        assert controls["terminal_sleeve_count"] == 0
        assert controls["terminal_bud_count"] == 0
        assert controls["support_base_radius"] >= 0.035
        assert controls["sdedit_seam_backprojection_available"] is False
        assert "short_bough" in controls["root_silhouette_change"]
        assert "V54-V57" in controls["v54_v57_failure_addressed"]

    zdata = json.loads(zoom_manifest.read_text(encoding="utf-8"))
    assert len(zdata["cases"]) == 4
    assert all(item["detail_target_source"] == "v58_lsystem_explicit_short_bough_yfork_mask" for item in zdata["cases"])
    assert all(1.75 <= item["zoom_divisor"] <= 2.0 for item in zdata["cases"])
    assert all(len(item["fixed_detail_targets"]) == 2 for item in zdata["cases"])
